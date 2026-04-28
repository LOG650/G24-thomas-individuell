"""
Felles MIP-solver for den to-trinns stokastiske flermål modellen.

Modellen:
- Stage 1: beslutte åpning y_i (binært) og modus-valg z_{ij,m} (binært)
  per (DC, kunde, modus). Notat: vi forenkler ved å la modus velges
  per (DC, kunde) -- det er da en "modal choice" fremfor ren fri
  allokering. Dette holder modellen håndterbar samtidig som
  karbonpris-tipping-effekten kommer fram.
- Stage 2: for hvert scenario s velges allokeringsandel x^s_{ij,m}
  (fraksjon av kunde j sin etterspørsel betjent via (i, j, m)).

Tre målfunksjoner:
- Kostnad: fast kost + forventet transportkost + karbonpris-kost
- Utslipp: forventet CO2 (kg)
- Service: forventet vektet avstand-til-kunde (service-proxy)

Det som returneres fra ``solve_scenario_mip`` er verdier for alle tre
målene for det valgte Pareto-punktet. Dette er "deterministisk
ekvivalent" av to-trinns programmet med et gitt scenariosett.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pulp


@dataclass
class Instance:
    dcs: pd.DataFrame
    customers: pd.DataFrame
    modes: pd.DataFrame
    edges: pd.DataFrame
    scenarios: pd.DataFrame  # kolonner: scenario, customer, demand
    scenario_probs: dict[int, float] | None = None  # kan være None -> uniform

    @property
    def dc_list(self) -> list[str]:
        return list(self.dcs["dc"])

    @property
    def cust_list(self) -> list[str]:
        return list(self.customers["customer"])

    @property
    def mode_list(self) -> list[str]:
        return list(self.modes["mode"])

    @property
    def scenario_list(self) -> list[int]:
        return sorted(self.scenarios["scenario"].unique().tolist())

    def prob(self, s: int) -> float:
        if self.scenario_probs is not None:
            return self.scenario_probs[s]
        return 1.0 / len(self.scenario_list)


def load_instance(data_dir: Path) -> Instance:
    return Instance(
        dcs=pd.read_csv(data_dir / "dc_candidates.csv"),
        customers=pd.read_csv(data_dir / "customers.csv"),
        modes=pd.read_csv(data_dir / "modes.csv"),
        edges=pd.read_csv(data_dir / "edges.csv"),
        scenarios=pd.read_csv(data_dir / "scenarios.csv"),
    )


def build_and_solve(
    inst: Instance,
    objective: str,            # 'cost' | 'emission' | 'service'
    carbon_price: float = 0.0, # EUR/tonn CO2 (kun brukt som del av cost)
    eps_cost: float | None = None,     # skranke for cost (cost <= eps)
    eps_emission: float | None = None, # skranke for CO2 (emission <= eps, kg)
    eps_service: float | None = None,  # skranke for service (service <= eps)
    time_limit: int = 60,
    msg: bool = False,
) -> dict:
    """Bygger og løser LP-relaksert to-trinns modell for gitt målfunksjon og
    skranker. Forenkling: vi lar andeler x være kontinuerlige i [0,1],
    mens DC-åpning y og modus-valg z er binære. Dette gir et MIP med
    moderat størrelse.

    Scenariosett: scenariene i ``inst`` brukes direkte som
    SAA-approksimasjon.
    """
    I = inst.dc_list
    J = inst.cust_list
    M = inst.mode_list
    S = inst.scenario_list

    # Lookup-dict for edges
    edge = {
        (r["dc"], r["customer"], r["mode"]): r
        for _, r in inst.edges.iterrows()
    }
    demand = {
        (r["scenario"], r["customer"]): r["demand"]
        for _, r in inst.scenarios.iterrows()
    }
    fixed_cost = dict(zip(inst.dcs["dc"], inst.dcs["fixed_cost"]))
    capacity = dict(zip(inst.dcs["dc"], inst.dcs["capacity"]))

    prob_name = f"gronnsc_{objective}_cp{int(carbon_price)}"
    prob = pulp.LpProblem(prob_name, pulp.LpMinimize)

    # Stage 1 variabler
    y = {i: pulp.LpVariable(f"y_{i}", cat="Binary") for i in I}
    # Forenkling: modus-valg z gjelder ingen direkte tilordning -- vi lar
    # allokeringsandelen velge mellom DC-kunde-modus per scenario. Dette
    # tilsvarer at enhver DC kan serve enhver kunde via enhver modus. For
    # mer realistisk modal-valg-mekanikk kunne man lagt z som binær, men
    # her holder vi modellen enklere ved å ta fraksjonell allokering.

    # Stage 2 variabler: x[s, i, j, m] andel av kunde j etterspørsel i sc s
    x = {}
    for s in S:
        for i in I:
            for j in J:
                for m in M:
                    x[(s, i, j, m)] = pulp.LpVariable(
                        f"x_{s}_{i}_{j}_{m}", lowBound=0, upBound=1
                    )

    # Koeffisienter
    def c_cost(i, j, m):
        return edge[(i, j, m)]["cost_per_unit"]

    def c_emis(i, j, m):
        return edge[(i, j, m)]["emis_per_unit"]  # kg/enhet

    def c_serv(i, j, m):
        return edge[(i, j, m)]["service_cost"]

    # Forventet transportkost (EUR)
    exp_trans_cost = pulp.lpSum(
        inst.prob(s) * demand[(s, j)] * c_cost(i, j, m) * x[(s, i, j, m)]
        for s in S for i in I for j in J for m in M
    )
    # Forventet utslipp (kg CO2)
    exp_emission = pulp.lpSum(
        inst.prob(s) * demand[(s, j)] * c_emis(i, j, m) * x[(s, i, j, m)]
        for s in S for i in I for j in J for m in M
    )
    # Forventet service (vektet avstand x service_factor)
    exp_service = pulp.lpSum(
        inst.prob(s) * demand[(s, j)] * c_serv(i, j, m) * x[(s, i, j, m)]
        for s in S for i in I for j in J for m in M
    )

    # Karbonpris-bidrag: carbon_price er EUR/tonn, exp_emission er kg ->
    # konverter: cost_carbon = carbon_price * exp_emission / 1000
    exp_carbon_cost = (carbon_price / 1000.0) * exp_emission

    # Fast DC-kost
    fixed_dc_cost = pulp.lpSum(fixed_cost[i] * y[i] for i in I)

    total_cost_expr = fixed_dc_cost + exp_trans_cost + exp_carbon_cost

    # Velg målfunksjon
    if objective == "cost":
        prob += total_cost_expr
    elif objective == "emission":
        prob += exp_emission
    elif objective == "service":
        prob += exp_service
    else:
        raise ValueError(f"Ukjent objective: {objective}")

    # Skranker
    # 1) Etterspørselsdekking pr scenario og kunde
    for s in S:
        for j in J:
            prob += (
                pulp.lpSum(x[(s, i, j, m)] for i in I for m in M) == 1.0,
                f"demand_{s}_{j}",
            )

    # 2) Kapasitet pr DC pr scenario
    for s in S:
        for i in I:
            prob += (
                pulp.lpSum(
                    demand[(s, j)] * x[(s, i, j, m)] for j in J for m in M
                )
                <= capacity[i] * y[i],
                f"cap_{s}_{i}",
            )

    # 3) Minst én DC åpnes
    prob += pulp.lpSum(y[i] for i in I) >= 1

    # 4) Epsilon-skranker
    if eps_cost is not None:
        prob += total_cost_expr <= eps_cost, "eps_cost"
    if eps_emission is not None:
        prob += exp_emission <= eps_emission, "eps_emission"
    if eps_service is not None:
        prob += exp_service <= eps_service, "eps_service"

    # Løs
    t0 = time.time()
    solver = pulp.PULP_CBC_CMD(msg=msg, timeLimit=time_limit)
    prob.solve(solver)
    t1 = time.time()
    status = pulp.LpStatus[prob.status]

    if status not in ("Optimal", "Not Solved") or prob.status == -1:
        return {
            "status": status,
            "solve_time_s": t1 - t0,
            "opened": [],
            "objective": float("inf"),
            "total_cost": float("inf"),
            "emission_kg": float("inf"),
            "service": float("inf"),
        }

    opened = [i for i in I if pulp.value(y[i]) is not None and pulp.value(y[i]) > 0.5]

    total_cost_val = pulp.value(total_cost_expr)
    emis_val = pulp.value(exp_emission)
    serv_val = pulp.value(exp_service)

    # Dekomponer kost
    fixed_val = sum(fixed_cost[i] for i in opened)
    trans_val = pulp.value(exp_trans_cost)
    carbon_val = pulp.value(exp_carbon_cost)

    # Modal split: sum av transportert volum pr modus over alle scenario
    modal_volume = {m: 0.0 for m in M}
    for s in S:
        for i in I:
            for j in J:
                for m in M:
                    v = pulp.value(x[(s, i, j, m)])
                    if v is None:
                        continue
                    modal_volume[m] += inst.prob(s) * demand[(s, j)] * v

    return {
        "status": status,
        "solve_time_s": t1 - t0,
        "opened": opened,
        "objective_name": objective,
        "objective": pulp.value(prob.objective),
        "total_cost": total_cost_val,
        "fixed_cost": fixed_val,
        "transport_cost": trans_val,
        "carbon_cost": carbon_val,
        "emission_kg": emis_val,
        "service": serv_val,
        "modal_volume": modal_volume,
    }
