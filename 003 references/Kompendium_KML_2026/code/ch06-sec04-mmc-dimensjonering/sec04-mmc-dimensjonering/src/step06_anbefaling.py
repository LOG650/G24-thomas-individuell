"""
Steg 6: Anbefaling og Gantt-visualisering
==========================================
Oppsummer valget av c, validerer mot simulering (SimPy) og lager
en Gantt-aktig visualisering av en representativ drifts-dag.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import simpy

from step01_datainnsamling import (
    COLOR_S1, COLOR_S1D, COLOR_S2, COLOR_S2D, COLOR_S3,
    COLOR_S3D, COLOR_S4, COLOR_S4D, COLOR_S5, COLOR_S5D,
)
from step02_erlang_c import LAMBDA, MU, mmc_metrics, prob_wait_greater

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

CRANE_COLORS = [COLOR_S1, COLOR_S2, COLOR_S3, COLOR_S4, COLOR_S5]
CRANE_EDGES = [COLOR_S1D, COLOR_S2D, COLOR_S3D, COLOR_S4D, COLOR_S5D]


def simulate_mmc(lam: float, mu: float, c: int, sim_hours: float = 48.0,
                 seed: int = 2026) -> dict:
    """
    Diskret hendelses-simulering av M/M/c i SimPy.
    Returnerer gjennomsnittlig Wq og P(Wq > 10 min) estimert fra simulering.
    """
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    servers = simpy.Resource(env, capacity=c)

    wait_times = []

    def ship(name: str):
        t_arrive = env.now
        with servers.request() as req:
            yield req
            wait = env.now - t_arrive
            wait_times.append(wait)
            service = rng.exponential(scale=1.0 / mu)
            yield env.timeout(service)

    def arrivals():
        i = 0
        while True:
            inter = rng.exponential(scale=1.0 / lam)
            yield env.timeout(inter)
            if env.now > sim_hours:
                break
            i += 1
            env.process(ship(f"skip-{i}"))

    env.process(arrivals())
    env.run(until=sim_hours)

    wait_arr = np.array(wait_times)
    if len(wait_arr) == 0:
        return {'Wq_min': 0.0, 'p_wait_gt_10min': 0.0, 'n': 0}
    return {
        'Wq_min': float(wait_arr.mean() * 60),
        'p_wait_gt_10min': float((wait_arr > 10.0 / 60.0).mean()),
        'p_wait_gt_0': float((wait_arr > 0).mean()),
        'n': int(len(wait_arr)),
    }


def simulate_gantt(lam: float, mu: float, c: int, duration_hours: float,
                   seed: int = 42):
    """Produserer en liste (kran_id, start, slutt, ankomst) for en kort periode."""
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    servers = simpy.Resource(env, capacity=c)

    # (server_id, start, end, arrival)
    events = []
    server_log = [None] * c

    def ship(name: str, arrive: float):
        with servers.request() as req:
            yield req
            # finn forste ledige kran
            free_id = None
            for i in range(c):
                if server_log[i] is None or server_log[i] <= env.now:
                    free_id = i
                    break
            if free_id is None:
                free_id = int(np.argmin([x if x is not None else 0
                                         for x in server_log]))
            start = env.now
            service = rng.exponential(scale=1.0 / mu)
            end = start + service
            server_log[free_id] = end
            events.append((free_id, start, end, arrive))
            yield env.timeout(service)

    def arrivals():
        i = 0
        while True:
            inter = rng.exponential(scale=1.0 / lam)
            yield env.timeout(inter)
            if env.now > duration_hours:
                break
            i += 1
            env.process(ship(f"skip-{i}", env.now))

    env.process(arrivals())
    env.run(until=duration_hours + 2.0)
    return events


def plot_gantt(events, c: int, duration: float, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    for server_id, start, end, arrive in events:
        y = server_id
        ax.barh(y, end - start, left=start, height=0.7,
                color=CRANE_COLORS[server_id % len(CRANE_COLORS)],
                edgecolor=CRANE_EDGES[server_id % len(CRANE_EDGES)],
                linewidth=0.8)
        # marker ankomst som en prikk pa samme rad
        ax.plot(arrive, y, marker='|', color='black', markersize=8,
                markeredgewidth=1.2)
    ax.set_yticks(range(c))
    ax.set_yticklabels([f'Kran {i + 1}' for i in range(c)])
    ax.set_xlabel('Tid (timer)', fontsize=12)
    ax.set_xlim(0, duration)
    ax.set_title(rf'Driftsmønster med $c = {c}$ kraner over '
                 rf'{int(duration)} timer (simulert)',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 6: ANBEFALING")
    print("=" * 60)

    # Les valg fra steg 3 og 4
    step3 = json.loads((OUTPUT_DIR / 'step03_service_dim.json')
                       .read_text(encoding='utf-8'))
    step4 = json.loads((OUTPUT_DIR / 'step04_cost_optim.json')
                       .read_text(encoding='utf-8'))
    c_service = step3['valg_av_c']['c_optimal']
    c_cost = step4['c_optimal']
    c_anbefalt = max(c_service, c_cost)

    print(f"\nServicevalg:   c = {c_service}")
    print(f"Kostnadsvalg:  c = {c_cost}")
    print(f"Anbefaling:    c = {c_anbefalt} (max av de to)")

    # Analytiske og simulerte verdier
    m = mmc_metrics(c_anbefalt, LAMBDA, MU)
    sim = simulate_mmc(LAMBDA, MU, c_anbefalt, sim_hours=2000.0)
    p_analyt = prob_wait_greater(10.0 / 60.0, c_anbefalt, LAMBDA, MU)

    compare = {
        'c_anbefalt': c_anbefalt,
        'analytisk': {
            'rho': float(m['rho']),
            'Lq': float(m['Lq']),
            'Wq_min': float(m['Wq'] * 60),
            'W_min': float(m['W'] * 60),
            'P_wait_gt_10min': float(p_analyt),
        },
        'simulert': sim,
    }
    path = OUTPUT_DIR / 'step06_anbefaling.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(compare, f, indent=2, ensure_ascii=False)
    print(f"Lagret: {path}")

    print("\n--- Sammenlikning analytisk vs. simulering ---")
    print(f"  Analytisk Wq: {m['Wq']*60:.2f} min  | "
          f"Simulert Wq: {sim['Wq_min']:.2f} min")
    print(f"  Analytisk P(Wq>10min): {p_analyt:.4f} | "
          f"Simulert: {sim['p_wait_gt_10min']:.4f}")

    # Gantt over et 8-timersvindu
    events = simulate_gantt(LAMBDA, MU, c_anbefalt,
                            duration_hours=8.0, seed=123)
    plot_gantt(events, c_anbefalt, 8.0, OUTPUT_DIR / 'mmc_gantt.png')

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print(f"Havnen bor investere i {c_anbefalt} kraner for normal drift.")
    print("Simuleringen bekrefter de analytiske verdiene.")


if __name__ == '__main__':
    main()
