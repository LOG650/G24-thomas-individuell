"""
Steg 2: Uavhengig (R,S,s) per lokasjon (basislinje)
===================================================
Beregner klassisk periodisk gjennomgang (R,S,s) for hver lokasjon
uavhengig, basert på normaltilnaærming av etterspørsel i
gjennomgangsperioden + ledetid. Denne losningen brukes senere som
sammenligningsgrunnlag for den koordinerte stokastiske losningen.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

from step01_datainnsamling import (
    COST_PARAMS,
    LOCATION_PARAMS,
    LOCATIONS,
)

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

REVIEW_PERIOD = 7   # R = 7 dager (ukentlig gjennomgang)
SERVICE_LEVEL = 0.95  # Type-1 servicenivå


def independent_rss(
    loc: str,
    review_period: int = REVIEW_PERIOD,
    service_level: float = SERVICE_LEVEL,
) -> dict:
    """Beregn (R, S, s) parametre for én lokasjon med uavhengig politikk.

    Forventning og varians i gjennomgangsperioden + ledetid:
        mu_RL = (R + L) * mu
        var_RL = (R + L) * sigma^2

    Order-up-to-nivå:
        S = mu_RL + z * sqrt(var_RL)
    Bestillingspunkt:
        s = L * mu + z * sigma * sqrt(L)
    """
    mu = LOCATION_PARAMS[loc]["mu"]
    sigma = LOCATION_PARAMS[loc]["sigma"]
    L = LOCATION_PARAMS[loc]["leadtime_days"]

    z = norm.ppf(service_level)
    mu_RL = (review_period + L) * mu
    var_RL = (review_period + L) * sigma**2
    S = mu_RL + z * np.sqrt(var_RL)
    s_reorder = L * mu + z * sigma * np.sqrt(L)

    return {
        "location": loc,
        "R": review_period,
        "L": L,
        "mu": mu,
        "sigma": sigma,
        "z": float(round(z, 3)),
        "mu_RL": float(round(mu_RL, 2)),
        "sigma_RL": float(round(np.sqrt(var_RL), 2)),
        "S": float(round(S, 2)),
        "s": float(round(s_reorder, 2)),
    }


def simulate_independent(
    demand: pd.DataFrame,
    policies: dict,
    review_period: int = REVIEW_PERIOD,
) -> dict:
    """Simuler uavhengig (R,S,s)-politikk per lokasjon over hele horisonten."""
    n_days = len(demand)
    results = {loc: {"inventory": [], "orders": [], "backorders": []} for loc in LOCATIONS}

    for loc in LOCATIONS:
        S = policies[loc]["S"]
        s = policies[loc]["s"]
        L = policies[loc]["L"]

        # Startlager = S
        inv_pos = S  # "inventory position" inkl. utestaænde bestillinger
        on_hand = S
        pipeline: list[tuple[int, float]] = []  # (leveringsdag, mengde)

        total_holding = 0.0
        total_backorder = 0.0
        total_ordering = 0.0
        total_units_ordered = 0.0
        total_demand = 0.0
        stockout_days = 0

        for t in range(n_days):
            # Motta leveringer som ankommer i dag
            arrivals = [q for (d, q) in pipeline if d == t]
            on_hand += sum(arrivals)
            pipeline = [(d, q) for (d, q) in pipeline if d > t]

            d_t = int(demand[loc].iloc[t])
            total_demand += d_t

            # Dekk etterspørsel
            served = min(on_hand, d_t)
            short = d_t - served
            on_hand -= served
            total_backorder += short
            if short > 0:
                stockout_days += 1

            # Oppdater lagerposisjon
            pipeline_qty = sum(q for (_, q) in pipeline)
            inv_pos = on_hand + pipeline_qty

            # Bestill hver R-te dag hvis inv_pos <= s
            if t % review_period == 0:
                if inv_pos <= s:
                    order_qty = S - inv_pos
                    pipeline.append((t + L, order_qty))
                    total_ordering += COST_PARAMS["fixed_order"]
                    total_units_ordered += order_qty

            total_holding += on_hand * COST_PARAMS["holding"]
            results[loc]["inventory"].append(on_hand)

        results[loc]["stats"] = {
            "total_demand": float(total_demand),
            "total_units_ordered": float(round(total_units_ordered, 1)),
            "total_backorder_units": float(round(total_backorder, 1)),
            "stockout_days": int(stockout_days),
            "service_level": float(round(1 - stockout_days / n_days, 4)),
            "cost_holding": float(round(total_holding, 1)),
            "cost_ordering": float(round(total_ordering, 1)),
            "cost_backorder": float(round(total_backorder * COST_PARAMS["backorder"], 1)),
            "cost_purchase": float(round(total_units_ordered * COST_PARAMS["order"], 1)),
        }
        results[loc]["stats"]["cost_total"] = float(
            round(
                results[loc]["stats"]["cost_holding"]
                + results[loc]["stats"]["cost_ordering"]
                + results[loc]["stats"]["cost_backorder"]
                + results[loc]["stats"]["cost_purchase"],
                1,
            )
        )
    return results


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 2: Uavhengig (R,S,s) per lokasjon")
    print("=" * 60)

    demand = pd.read_csv(DATA_DIR / "demand.csv", index_col="date", parse_dates=["date"])

    policies = {loc: independent_rss(loc) for loc in LOCATIONS}
    for loc, pol in policies.items():
        print(f"  {loc}: R={pol['R']} L={pol['L']} s={pol['s']:.1f} S={pol['S']:.1f}")

    sim = simulate_independent(demand, policies)

    total_cost = sum(sim[loc]["stats"]["cost_total"] for loc in LOCATIONS)
    total_backorder = sum(sim[loc]["stats"]["cost_backorder"] for loc in LOCATIONS)
    print(f"\nTotalkostnad uavhengig politikk: {total_cost:,.0f} kr")
    print(f"Herav restordrekost: {total_backorder:,.0f} kr")

    # Oppsummering per lokasjon
    summary = {
        loc: {
            "policy": policies[loc],
            "stats": sim[loc]["stats"],
        }
        for loc in LOCATIONS
    }
    summary["total_cost"] = float(round(total_cost, 1))

    with open(OUTPUT_DIR / "step02_uavhengig_results.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step02_uavhengig_results.json'}")


if __name__ == "__main__":
    main()
