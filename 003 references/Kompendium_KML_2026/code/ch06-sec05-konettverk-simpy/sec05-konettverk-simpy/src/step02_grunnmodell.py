"""
Steg 2: Grunnmodell i SimPy
===========================
Bygger opp SimPy-simulatoren for konettverket:
  - Station: SimPy Resource-wrapper som logger ventetid, servicetid, ko-lengde.
  - OrderNetwork: rutingen av ordrer gjennom stasjoner i serie.
  - run_simulation(): driver ankomster og samler inn KPI-er.

Denne modulen brukes av steg 3-5.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np
import simpy

from step01_datainnsamling import network_parameters


# ============================================================
# Hjelpefunksjoner: servicetidsprovetaking
# ============================================================

def make_service_sampler(dist: str, params: dict, rng: np.random.Generator) -> Callable[[], float]:
    """Returner funksjon som sampler en servicetid fra angitt fordeling."""
    if dist == 'exponential':
        mean = params['mean']
        return lambda: rng.exponential(mean)
    if dist == 'lognormal':
        mu, sigma = params['mu'], params['sigma']
        return lambda: rng.lognormal(mean=mu, sigma=sigma)
    if dist == 'uniform':
        low, high = params['low'], params['high']
        return lambda: rng.uniform(low, high)
    raise ValueError(f"Ukjent fordeling: {dist}")


# ============================================================
# Stasjons- og nettverksklasser
# ============================================================

@dataclass
class StationMetrics:
    """Logger metrikker per stasjon."""
    name: str
    wait_times: list = field(default_factory=list)        # tid i kø før service
    service_times: list = field(default_factory=list)     # faktisk betjeningstid
    sojourn_times: list = field(default_factory=list)     # wait + service per stasjon
    # Tidsveid stasjonsutnyttelse
    busy_time: float = 0.0


class Station:
    """En kostasjon: en SimPy Resource (med c servere) og innsamling av metrikker."""

    def __init__(self, env: simpy.Environment, name: str, servers: int,
                 sampler: Callable[[], float]):
        self.env = env
        self.name = name
        self.servers = servers
        self.resource = simpy.Resource(env, capacity=servers)
        self.sampler = sampler
        self.metrics = StationMetrics(name=name)

    def process(self, order):
        """SimPy-prosess: ordre ankommer stasjonen, venter, betjenes."""
        t_arrive = self.env.now
        with self.resource.request() as req:
            yield req
            t_start = self.env.now
            wait = t_start - t_arrive
            service = self.sampler()
            yield self.env.timeout(service)
            t_end = self.env.now

        # Logg
        self.metrics.wait_times.append(wait)
        self.metrics.service_times.append(service)
        self.metrics.sojourn_times.append(t_end - t_arrive)
        # Busy-tid pa c servere: service-tiden (tidsvekt per server)
        self.metrics.busy_time += service


class OrderNetwork:
    """Ett ordrer-konettverk som rutes seriellt gjennom stasjonslisten."""

    def __init__(self, env: simpy.Environment, stations: list[Station]):
        self.env = env
        self.stations = stations
        self.order_sojourn: list[float] = []  # total gjennomlopstid
        self.order_arrival: list[float] = []
        self.order_departure: list[float] = []

    def handle_order(self, order_id: int):
        """En ordres ferd gjennom alle stasjoner i serie."""
        t_arrive = self.env.now
        self.order_arrival.append(t_arrive)
        for st in self.stations:
            yield self.env.process(st.process(order_id))
        t_depart = self.env.now
        self.order_departure.append(t_depart)
        self.order_sojourn.append(t_depart - t_arrive)


def arrival_generator(env: simpy.Environment, network: OrderNetwork,
                      arrival_rate_per_min: float, n_orders: int,
                      rng: np.random.Generator):
    """Poisson-ankomster av ordrer til nettverket."""
    for i in range(n_orders):
        iat = rng.exponential(1.0 / arrival_rate_per_min)
        yield env.timeout(iat)
        env.process(network.handle_order(i))


# ============================================================
# Hovedsimulering
# ============================================================

def build_network(env: simpy.Environment, params: dict,
                  rng: np.random.Generator,
                  station_overrides: dict | None = None) -> OrderNetwork:
    """Bygg stasjonskjede ut fra parameterdict. station_overrides kan endre servers etc."""
    station_overrides = station_overrides or {}
    ordered = sorted(params['stations'].items(), key=lambda kv: kv[1]['order'])
    stations: list[Station] = []
    for name, s in ordered:
        override = station_overrides.get(name, {})
        servers = override.get('servers', s['servers'])
        dist = override.get('service_dist', s['service_dist'])
        sp = override.get('service_params', s['service_params'])
        sampler = make_service_sampler(dist, sp, rng)
        stations.append(Station(env, name, servers, sampler))
    return OrderNetwork(env, stations)


def run_simulation(n_orders: int = 5000, seed: int = 2025,
                   arrival_rate_per_hour: float | None = None,
                   station_overrides: dict | None = None) -> dict:
    """Kjor en simulering og returner resultater som dict."""
    params = network_parameters()
    if arrival_rate_per_hour is not None:
        params['arrival_rate'] = arrival_rate_per_hour
    arrival_rate_per_min = params['arrival_rate'] / 60.0

    rng = np.random.default_rng(seed=seed)
    env = simpy.Environment()
    network = build_network(env, params, rng, station_overrides)
    env.process(arrival_generator(env, network, arrival_rate_per_min, n_orders, rng))
    env.run()

    # Aggreger metrikker
    sim_end = env.now  # tiden da siste ordre forlater systemet
    station_stats = {}
    for st in network.stations:
        n = len(st.metrics.wait_times)
        station_stats[st.name] = {
            'n': n,
            'mean_wait': float(np.mean(st.metrics.wait_times)) if n else 0.0,
            'p95_wait': float(np.percentile(st.metrics.wait_times, 95)) if n else 0.0,
            'mean_service': float(np.mean(st.metrics.service_times)) if n else 0.0,
            'mean_sojourn': float(np.mean(st.metrics.sojourn_times)) if n else 0.0,
            'utilization': float(st.metrics.busy_time / (sim_end * st.servers)) if sim_end > 0 else 0.0,
            'wait_times': list(st.metrics.wait_times),
            'sojourn_times': list(st.metrics.sojourn_times),
        }

    results = {
        'sim_end_min': sim_end,
        'n_orders_completed': len(network.order_sojourn),
        'throughput_per_hour': len(network.order_sojourn) / (sim_end / 60.0) if sim_end > 0 else 0.0,
        'order_sojourn': list(network.order_sojourn),
        'mean_sojourn': float(np.mean(network.order_sojourn)),
        'p95_sojourn': float(np.percentile(network.order_sojourn, 95)),
        'stations': station_stats,
    }
    return results


if __name__ == '__main__':
    # Enkel roktest
    res = run_simulation(n_orders=500, seed=1)
    print(f"Sim-tid: {res['sim_end_min']:.1f} min")
    print(f"Gjennomsnittlig gjennomlopstid: {res['mean_sojourn']:.2f} min")
    print(f"Gjennomstromning: {res['throughput_per_hour']:.2f} ordrer/time")
    for n, s in res['stations'].items():
        print(f"  {n:20s} rho={s['utilization']:.3f}  E[W]={s['mean_wait']:.2f} min")
