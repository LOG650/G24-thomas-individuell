"""
Steg 5: Rullerende horisont-simulering
======================================
Kjører både uavhengig (R,S,s) og den koordinerte to-trinns
stokastiske losningen som rullerende horisont over ``N_PERIODS`` 7-
dagers perioder.

For den koordinerte losningen:
    1. Ved starten av hver periode, generer reduserte scenariø basert
       på det lokale tilstands- og inventarbildet.
    2. Løs to-trinns LP for å finne stage-1-bestillinger og en
       "anticipative" forventet transshipment-plan.
    3. Realisér etterspørsel i perioden (7 dager syntetisk fra
       dataset-grunnlaget). Oppdater inventar og backorder-tilstander
       ved å løse LP-ens stage-2 på nytt, betinget av faktisk
       realisering -- det vil si vi løser en "recourse LP" for én
       scenarieø (faktisk realisering).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

from step01_datainnsamling import (
    CORRELATION,
    COST_PARAMS,
    LOCATION_PARAMS,
    LOCATIONS,
    SEED,
)
from step02_uavhengig_rss import REVIEW_PERIOD, independent_rss, simulate_independent
from step03_scenariogenerering import fast_forward_reduction, generate_scenarios
from step04_to_trinns_LP import solve_two_stage_lp

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

N_PERIODS = 12
N_SCEN_PER_PERIOD = 1500   # færre pr periode for fart
N_REDUCED_PER_PERIOD = 40


def solve_stage2_given_realization(
    orders: dict,
    initial_inventory: dict,
    realization: np.ndarray,
    costs: dict = COST_PARAMS,
) -> dict:
    """Løs stage-2 LP for én faktisk realisasjon, med gitte stage-1-bestillinger."""
    locs = LOCATIONS
    prob = pulp.LpProblem("recourse", pulp.LpMinimize)

    y = {(l, m): pulp.LpVariable(f"y_{l}_{m}", lowBound=0)
         for l in locs for m in locs if l != m}
    w = {l: pulp.LpVariable(f"w_{l}", lowBound=0) for l in locs}
    h = {l: pulp.LpVariable(f"h_{l}", lowBound=0) for l in locs}

    prob += (
        pulp.lpSum(costs["holding"] * h[l] + costs["backorder"] * w[l] for l in locs)
        + pulp.lpSum(costs["transship"] * y[(l, m)]
                     for l in locs for m in locs if l != m)
    )
    for l_idx, l in enumerate(locs):
        inflow = initial_inventory[l] + orders[l] + pulp.lpSum(y[(m, l)] for m in locs if m != l)
        outflow = pulp.lpSum(y[(l, m)] for m in locs if m != l)
        prob += h[l] - w[l] == inflow - outflow - realization[l_idx], f"bal_{l}"

    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))

    return {
        "status": pulp.LpStatus[prob.status],
        "h": {l: float(round(pulp.value(h[l]), 3)) for l in locs},
        "w": {l: float(round(pulp.value(w[l]), 3)) for l in locs},
        "y": {(l, m): float(round(pulp.value(y[(l, m)]), 3))
              for l in locs for m in locs if l != m},
    }


def realize_period_demand(rng: np.random.Generator, period_days: int) -> np.ndarray:
    """Generer faktisk realisert daglig etterspørsel for én periode."""
    mus = np.array([LOCATION_PARAMS[l]["mu"] for l in LOCATIONS])
    sigmas = np.array([LOCATION_PARAMS[l]["sigma"] for l in LOCATIONS])
    cov = CORRELATION * np.outer(sigmas, sigmas)
    draws = rng.multivariate_normal(mus, cov, size=period_days)
    return np.clip(np.round(draws), 0, None)


def rolling_horizon_coordinated(n_periods: int = N_PERIODS,
                                period_days: int = REVIEW_PERIOD,
                                seed: int = SEED + 100) -> dict:
    rng = np.random.default_rng(seed)

    inventory = {loc: 0.0 for loc in LOCATIONS}
    history = []
    total_costs = {"order": 0.0, "holding": 0.0, "backorder": 0.0, "transship": 0.0}
    total_backorder_units = 0.0
    total_demand_units = 0.0
    total_stockout_days = 0
    total_days = 0

    for t in range(n_periods):
        # Generer scenariø for denne perioden
        scen_seed = seed + 13 * (t + 1)
        scenarios = generate_scenarios(
            n_scenarios=N_SCEN_PER_PERIOD,
            period_days=period_days,
            seed=scen_seed,
        )
        reduced, weights = fast_forward_reduction(scenarios, N_REDUCED_PER_PERIOD)

        # Løs to-trinns LP for å finne stage-1 bestillinger
        res = solve_two_stage_lp(reduced, weights, initial_inventory=inventory)
        orders = res["orders"]

        # Realiser daglig etterspørsel over perioden
        daily = realize_period_demand(rng, period_days)
        realization = daily.sum(axis=0)

        # Løs stage-2 LP gitt faktisk realisasjon
        recourse = solve_stage2_given_realization(orders, inventory, realization)

        # Oppdater kostnader
        period_order_cost = sum(COST_PARAMS["order"] * orders[l] for l in LOCATIONS)
        period_holding_cost = sum(COST_PARAMS["holding"] * recourse["h"][l] for l in LOCATIONS)
        period_backorder_cost = sum(COST_PARAMS["backorder"] * recourse["w"][l] for l in LOCATIONS)
        period_transship_cost = sum(
            COST_PARAMS["transship"] * recourse["y"][(l, m)]
            for l in LOCATIONS for m in LOCATIONS if l != m
        )

        total_costs["order"] += period_order_cost
        total_costs["holding"] += period_holding_cost
        total_costs["backorder"] += period_backorder_cost
        total_costs["transship"] += period_transship_cost

        period_backorder_units = sum(recourse["w"][l] for l in LOCATIONS)
        total_backorder_units += period_backorder_units
        total_demand_units += realization.sum()

        # Stockout-dager (daglig telt): dag er stockout hvis daglig etterspørsel
        # > daglig tilgjengelig. Forenklet heuristikk: bruk forholdet w/total
        # og approksimer som at alle stockout-enheter skjer spredt over perioden.
        if period_backorder_units > 0:
            total_stockout_days += int(np.ceil(period_backorder_units / max(1.0, realization.sum() / period_days)))
        total_days += period_days

        # Oppdater inventar = h fra recourse (restordre antas backordred -> eller lost)
        # Forenklet: restordre tapes (lost sales), inv = h
        inventory = {l: recourse["h"][l] for l in LOCATIONS}

        history.append({
            "period": t + 1,
            "orders": orders,
            "realization": {l: float(realization[i]) for i, l in enumerate(LOCATIONS)},
            "backorder_units": float(round(period_backorder_units, 2)),
            "transship_units": float(round(
                sum(recourse["y"][(l, m)] for l in LOCATIONS for m in LOCATIONS if l != m),
                2,
            )),
            "period_cost": float(round(
                period_order_cost + period_holding_cost + period_backorder_cost + period_transship_cost, 2,
            )),
            "ending_inventory": inventory.copy(),
        })

    total = sum(total_costs.values())
    return {
        "total_costs": {k: float(round(v, 2)) for k, v in total_costs.items()},
        "total_cost": float(round(total, 2)),
        "total_backorder_units": float(round(total_backorder_units, 2)),
        "total_demand_units": float(round(total_demand_units, 2)),
        "service_level_fillrate": float(round(
            1 - total_backorder_units / max(1.0, total_demand_units), 4,
        )),
        "total_days": total_days,
        "stockout_days_approx": int(total_stockout_days),
        "history": history,
    }


def rolling_horizon_independent(n_periods: int = N_PERIODS,
                                period_days: int = REVIEW_PERIOD,
                                seed: int = SEED + 100) -> dict:
    """Kjør uavhengig (R,S,s) med *samme* realiseringsgenerator som den
    koordinerte kjoringen, slik at sammenligningen er rettferdig.
    """
    rng = np.random.default_rng(seed)

    policies = {loc: independent_rss(loc) for loc in LOCATIONS}

    inventory = {loc: policies[loc]["S"] for loc in LOCATIONS}  # full start
    pipeline = {loc: [] for loc in LOCATIONS}   # (arrival_day_idx, qty)

    total_costs = {"order": 0.0, "holding": 0.0, "backorder": 0.0, "transship": 0.0}
    total_backorder = 0.0
    total_demand = 0.0
    total_stockout_days = 0
    total_days = 0

    history = []

    day_global = 0
    for t in range(n_periods):
        daily = realize_period_demand(rng, period_days)
        period_backorder_units = 0.0
        period_units_ordered = 0.0

        # Bestill ved periodestart
        period_order_cost = 0.0
        for loc in LOCATIONS:
            # Pipeline = sum of in-transit
            in_transit = sum(q for (d, q) in pipeline[loc])
            inv_pos = inventory[loc] + in_transit
            if inv_pos <= policies[loc]["s"]:
                order_qty = max(0.0, policies[loc]["S"] - inv_pos)
                pipeline[loc].append((day_global + policies[loc]["L"], order_qty))
                period_order_cost += COST_PARAMS["order"] * order_qty
                period_units_ordered += order_qty

        # Simuler dag-for-dag
        period_holding_cost = 0.0
        period_backorder_cost = 0.0
        period_stockout_days = 0
        for d in range(period_days):
            # Motta leveranser per lokasjon
            for loc in LOCATIONS:
                arr_qty = sum(q for (arr_d, q) in pipeline[loc] if arr_d == day_global)
                inventory[loc] += arr_qty
                pipeline[loc] = [(arr_d, q) for (arr_d, q) in pipeline[loc] if arr_d > day_global]

            # Møt etterspørsel
            for i, loc in enumerate(LOCATIONS):
                d_t = daily[d, i]
                total_demand += d_t
                served = min(inventory[loc], d_t)
                short = d_t - served
                inventory[loc] -= served
                period_backorder_units += short
                total_backorder += short
                period_backorder_cost += short * COST_PARAMS["backorder"]
                if short > 0:
                    period_stockout_days += 1
                period_holding_cost += inventory[loc] * COST_PARAMS["holding"]
            day_global += 1
            total_days += 1

        total_stockout_days += period_stockout_days

        total_costs["order"] += period_order_cost
        total_costs["holding"] += period_holding_cost
        total_costs["backorder"] += period_backorder_cost

        history.append({
            "period": t + 1,
            "units_ordered": float(round(period_units_ordered, 2)),
            "backorder_units": float(round(period_backorder_units, 2)),
            "period_cost": float(round(period_order_cost + period_holding_cost + period_backorder_cost, 2)),
        })

    return {
        "policies": policies,
        "total_costs": {k: float(round(v, 2)) for k, v in total_costs.items()},
        "total_cost": float(round(sum(total_costs.values()), 2)),
        "total_backorder_units": float(round(total_backorder, 2)),
        "total_demand_units": float(round(total_demand, 2)),
        "service_level_fillrate": float(round(1 - total_backorder / max(1.0, total_demand), 4)),
        "total_days": total_days,
        "stockout_days_approx": int(total_stockout_days),
        "history": history,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 5: Rullerende horisont - koordinert (to-trinns stokastisk)")
    print("=" * 60)
    coord = rolling_horizon_coordinated()
    print(f"Totalkostnad koordinert: {coord['total_cost']:,.2f}")
    print(f"Fill-rate: {coord['service_level_fillrate']:.4f}")

    print("\n" + "=" * 60)
    print("STEG 5: Rullerende horisont - uavhengig (R,S,s)")
    print("=" * 60)
    indep = rolling_horizon_independent()
    print(f"Totalkostnad uavhengig: {indep['total_cost']:,.2f}")
    print(f"Fill-rate: {indep['service_level_fillrate']:.4f}")

    out = {"coordinated": coord, "independent": indep}
    with open(OUTPUT_DIR / "step05_rolling_horizon.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step05_rolling_horizon.json'}")


if __name__ == "__main__":
    main()
