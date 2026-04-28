"""
Steg 3: Modellformulering med delte skranker
============================================
Skriver den matematiske Lagrangeanen til skjerm/JSON slik at den kan
refereres fra LaTeX, og sjekker om den uavhengige losningen fra steg 2
er \"feasible\" mot delte skranker (kapasitet V_max, budsjett B_max).
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step01_datainnsamling import DATA_DIR, OUTPUT_DIR


# Delte skranker for porteføljen (satt av logistikksjef)
#   V_max : maks gjennomsnittlig lagervolum (m^3)
#   B_max : maks gjennomsnittlig kapitalbinding (NOK)
V_MAX_M3 = 160.0
B_MAX_NOK = 5_000_000.0


def feasibility_check(indep: pd.DataFrame, df: pd.DataFrame) -> dict:
    """Er uavhengig losning \"feasible\" mot delte skranker?"""
    # Gjennomsnittlig lager = Q/2 + SS (med sikkerhetslager)
    avg_volume = float((df["v"] * (indep["Q_star"] / 2 + indep["SS"])).sum())
    avg_value = float((df["c"] * (indep["Q_star"] / 2 + indep["SS"])).sum())
    return {
        "V_max_m3": V_MAX_M3,
        "B_max_NOK": B_MAX_NOK,
        "avg_volume_uavhengig_m3": round(avg_volume, 2),
        "avg_value_uavhengig_NOK": round(avg_value, 0),
        "volume_overskridelse_m3": round(avg_volume - V_MAX_M3, 2),
        "budget_overskridelse_NOK": round(avg_value - B_MAX_NOK, 0),
        "volume_feasible": avg_volume <= V_MAX_M3,
        "budget_feasible": avg_value <= B_MAX_NOK,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: MODELLFORMULERING (Lagrange)")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "produkter.csv")
    indep = pd.read_csv(OUTPUT_DIR / "step02_independent_qr.csv")

    feas = feasibility_check(indep, df)
    print("\nFeasibility-sjekk mot delte skranker:")
    for key, value in feas.items():
        print(f"  {key}: {value}")

    # Skriv Lagrangeanen som formelstreng (kun informativ)
    lagrangian = {
        "maalfunksjon": (
            "min sum_i [ K_i D_i / Q_i + h_i c_i (Q_i/2 + k_i sigma_{DL,i}) "
            "+ pi_i D_i sigma_{DL,i} L(k_i) / Q_i ]"
        ),
        "skranker": {
            "volum": "sum_i v_i (Q_i/2 + k_i sigma_{DL,i}) <= V_max",
            "budsjett": "sum_i c_i (Q_i/2 + k_i sigma_{DL,i}) <= B_max",
            "service": "Phi(k_i) >= alpha_i for alle i (type 1)",
        },
        "lagrange": (
            "L = TC(Q,k) + lambda_V (sum v_i (Q_i/2 + k_i sigma_{DL,i}) - V_max) "
            "+ lambda_B (sum c_i (Q_i/2 + k_i sigma_{DL,i}) - B_max)"
        ),
        "KKT": {
            "dL_dQi=0": (
                "- K_i D_i / Q_i^2 + h_i c_i / 2 + lambda_V v_i/2 + lambda_B c_i/2 "
                "- pi_i D_i sigma_{DL,i} L(k_i) / Q_i^2 = 0"
            ),
            "dL_dki=0": (
                "h_i c_i sigma_{DL,i} - pi_i D_i sigma_{DL,i} (1 - Phi(k_i)) / Q_i "
                "+ (lambda_V v_i + lambda_B c_i) sigma_{DL,i} = 0"
            ),
            "komplementaritet": "lambda_V, lambda_B >= 0, skranker binder naar lambda > 0",
        },
    }

    out = {
        "skranker": {"V_max_m3": V_MAX_M3, "B_max_NOK": B_MAX_NOK},
        "feasibility_uavhengig": feas,
        "modell": lagrangian,
    }
    path = OUTPUT_DIR / "step03_model.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nModellformulering lagret: {path}")

    if not (feas["volume_feasible"] and feas["budget_feasible"]):
        print(
            "\nDen uavhengige losningen bryter minst en skranke "
            "-- koordinert optimering er nødvendig i steg 4."
        )


if __name__ == "__main__":
    main()
