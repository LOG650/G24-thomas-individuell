"""
Steg 4: To-trinns stokastisk LP
===============================
Formulerer og løser den to-trinns stokastiske modellen for én
gjennomgangsperiode med 60 reduserte scenariø (fra steg 3).

Stage 1 (her-og-nå):
    x_l >= 0  for alle lokasjoner l  -- bestilling per lokasjon

Stage 2 (gitt realisert etterspørsel ksi^s):
    y^s_{lm} >= 0  -- transshipment fra l til m
    w^s_l    >= 0  -- restordre på l
    h^s_l    >= 0  -- gjenvaærende lager på l

Modell (lineær relaksering -- heltall på bestillinger kan legges på ved behov):

    min   sum_l c^o * x_l
        + sum_s p^s [ sum_l (c^h * h^s_l + c^b * w^s_l)
                      + sum_{l != m} c^t * y^s_{lm} ]

    s.t.  h^s_l + w^s_l = (I0_l + x_l) + sum_m y^s_{ml} - sum_m y^s_{lm} - ksi^s_l
          x_l, y^s_{lm}, h^s_l, w^s_l >= 0

I0_l er initiallager per lokasjon (satt til 0 for rent stage-1-perspektiv).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pulp

from step01_datainnsamling import COST_PARAMS, LOCATIONS

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

INITIAL_INVENTORY = {loc: 0.0 for loc in LOCATIONS}


def solve_two_stage_lp(
    scenarios: np.ndarray,
    weights: np.ndarray,
    initial_inventory: dict | None = None,
    costs: dict | None = None,
) -> dict:
    """Løs den to-trinns stokastiske LP-en.

    Parametre
    ---------
    scenarios : shape (S, L)
        Periodiske etterspørselsrealiseringer.
    weights : shape (S,)
        Sannsynligheter p^s som summerer til 1.
    initial_inventory : {loc: float}
        Start-lager per lokasjon ved starten av perioden.
    costs : dict med noekler order/holding/backorder/transship.
    """
    if initial_inventory is None:
        initial_inventory = INITIAL_INVENTORY
    if costs is None:
        costs = COST_PARAMS

    n_scen, n_loc = scenarios.shape
    locs = LOCATIONS

    prob = pulp.LpProblem("two_stage_flerlok", pulp.LpMinimize)

    # Stage 1: bestillinger
    x = {l: pulp.LpVariable(f"x_{l}", lowBound=0) for l in locs}

    # Stage 2: transshipment y^s_{lm}, restordre w^s_l, lager h^s_l
    y = {
        (s, l, m): pulp.LpVariable(f"y_{s}_{l}_{m}", lowBound=0)
        for s in range(n_scen)
        for l in locs
        for m in locs
        if l != m
    }
    w = {
        (s, l): pulp.LpVariable(f"w_{s}_{l}", lowBound=0)
        for s in range(n_scen)
        for l in locs
    }
    h = {
        (s, l): pulp.LpVariable(f"h_{s}_{l}", lowBound=0)
        for s in range(n_scen)
        for l in locs
    }

    # Maælfunksjon: stage 1 innkjopskost + forventet stage 2
    stage1 = pulp.lpSum(costs["order"] * x[l] for l in locs)
    stage2 = pulp.lpSum(
        weights[s] * (
            pulp.lpSum(costs["holding"] * h[(s, l)] + costs["backorder"] * w[(s, l)] for l in locs)
            + pulp.lpSum(
                costs["transship"] * y[(s, l, m)]
                for l in locs
                for m in locs
                if l != m
            )
        )
        for s in range(n_scen)
    )
    prob += stage1 + stage2

    # Balansebetingelser per scenario og lokasjon
    for s in range(n_scen):
        for l_idx, l in enumerate(locs):
            inflow = initial_inventory[l] + x[l] + pulp.lpSum(y[(s, m, l)] for m in locs if m != l)
            outflow = pulp.lpSum(y[(s, l, m)] for m in locs if m != l)
            prob += (
                h[(s, l)] - w[(s, l)] == inflow - outflow - scenarios[s, l_idx],
                f"bal_{s}_{l}",
            )

    # Løs
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=120)
    prob.solve(solver)
    status = pulp.LpStatus[prob.status]

    orders = {l: float(round(pulp.value(x[l]), 2)) for l in locs}
    obj = float(round(pulp.value(prob.objective), 2))

    # Kostnadsdekomponering
    c_order = sum(costs["order"] * orders[l] for l in locs)
    c_hold = 0.0
    c_back = 0.0
    c_trans = 0.0
    for s in range(n_scen):
        for l in locs:
            c_hold += weights[s] * costs["holding"] * pulp.value(h[(s, l)])
            c_back += weights[s] * costs["backorder"] * pulp.value(w[(s, l)])
            for m in locs:
                if m != l:
                    c_trans += weights[s] * costs["transship"] * pulp.value(y[(s, l, m)])

    avg_backorder = sum(
        weights[s] * sum(pulp.value(w[(s, l)]) for l in locs) for s in range(n_scen)
    )
    avg_holding = sum(
        weights[s] * sum(pulp.value(h[(s, l)]) for l in locs) for s in range(n_scen)
    )
    avg_transship = sum(
        weights[s]
        * sum(pulp.value(y[(s, l, m)]) for l in locs for m in locs if l != m)
        for s in range(n_scen)
    )

    return {
        "status": status,
        "objective": obj,
        "orders": orders,
        "cost_order": float(round(c_order, 2)),
        "cost_holding": float(round(c_hold, 2)),
        "cost_backorder": float(round(c_back, 2)),
        "cost_transship": float(round(c_trans, 2)),
        "avg_backorder_units": float(round(avg_backorder, 3)),
        "avg_holding_units": float(round(avg_holding, 3)),
        "avg_transship_units": float(round(avg_transship, 3)),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 4: To-trinns stokastisk LP")
    print("=" * 60)

    data = np.load(OUTPUT_DIR / "step03_scenarios.npz")
    reduced = data["reduced"]
    weights = data["weights"]
    print(f"Løser med {reduced.shape[0]} scenariø x {reduced.shape[1]} lokasjoner")

    result = solve_two_stage_lp(reduced, weights)
    print(f"\nStatus: {result['status']}")
    print(f"Objektiv (1 periode): {result['objective']:,.2f} kr")
    print("\nOptimale stage-1 bestillinger:")
    for loc, q in result["orders"].items():
        print(f"  {loc}: {q:6.2f} enheter")

    print("\nKostnadsdekomponering:")
    print(f"  Bestilling:       {result['cost_order']:10,.2f} kr")
    print(f"  Lagerhold (fvt):  {result['cost_holding']:10,.2f} kr")
    print(f"  Restordre  (fvt): {result['cost_backorder']:10,.2f} kr")
    print(f"  Transshipment:    {result['cost_transship']:10,.2f} kr")

    with open(OUTPUT_DIR / "step04_two_stage_result.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step04_two_stage_result.json'}")


if __name__ == "__main__":
    main()
