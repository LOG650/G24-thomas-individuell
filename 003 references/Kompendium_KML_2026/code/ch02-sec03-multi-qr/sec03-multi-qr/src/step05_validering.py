"""
Steg 5: Monte Carlo-validering av servicenivaa
=============================================
Simulerer den optimaliserte (Q,R)-politikken fra steg 4 over 2000 uker
med tilfeldig etterspørsel og leveringstid. Vi maaler:

- Realisert type-1 servicenivaa (fraksjon av sykluser uten mangel)
- Realisert type-2 fill rate (andel etterspørsel dekket direkte fra lager)
- Gjennomsnittlig lagerbeholdning og volumbruk
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from step01_datainnsamling import (
    DATA_DIR, OUTPUT_DIR, S_FILLS, S_DARKS, PRIMARY, INKMUTED,
)
from step02_uavhengig_qr import WEEKS_PER_YEAR, SERVICE_LEVEL_TYPE1


SIM_SEED = 4242
SIM_WEEKS = 2000


def simulate_product(mu_D: float, sigma_D: float, mu_L: float, sigma_L: float,
                     Q: float, R: float, weeks: int = SIM_WEEKS,
                     seed: int = SIM_SEED) -> dict:
    """Diskret uke-simulering av en (Q,R)-politikk for ett produkt.

    Vi skiller mellom \"replenishment cycle\" (fra en ordreankomst til neste)
    og maaler type-1 servicenivaa som fraksjon av slike sykluser uten manko.
    Fill rate (type-2) er 1 - (total manko / total etterspørsel).
    """
    rng = np.random.default_rng(seed)
    on_hand = Q + R  # start med en full base
    on_order = 0.0
    orders_in_transit: list[tuple[int, float]] = []
    total_demand = 0.0
    total_shortage = 0.0

    # Cycle-regnskap: hver gang et parti ankommer, lukker vi en syklus.
    cycles_with_stockout = 0
    cycles = 0
    current_cycle_has_stockout = False

    for week in range(weeks):
        # 1) Motta ankomne ordrer (og lukk syklus)
        new_in_transit = []
        for arr_week, qty in orders_in_transit:
            if arr_week <= week:
                on_hand += qty
                on_order -= qty
                # Forrige syklus slutter i det leveransen ankommer.
                cycles += 1
                if current_cycle_has_stockout:
                    cycles_with_stockout += 1
                current_cycle_has_stockout = False
            else:
                new_in_transit.append((arr_week, qty))
        orders_in_transit = new_in_transit

        # 2) Etterspørsel (trunkert paa 0)
        d = max(0.0, rng.normal(mu_D, sigma_D))
        total_demand += d
        if d <= on_hand:
            on_hand -= d
        else:
            shortage = d - on_hand
            total_shortage += shortage
            on_hand = 0.0
            current_cycle_has_stockout = True

        # 3) Lagerposisjon
        inventory_position = on_hand + on_order
        if inventory_position <= R:
            lead = max(1, int(round(rng.normal(mu_L, sigma_L))))
            orders_in_transit.append((week + lead, Q))
            on_order += Q

    fill_rate = 1.0 - total_shortage / max(1e-9, total_demand)
    type1 = 1.0 - cycles_with_stockout / max(1, cycles)
    return {
        "cycles": cycles,
        "cycles_with_stockout": cycles_with_stockout,
        "fill_rate": float(fill_rate),
        "type1_service": float(type1),
        "total_demand": float(total_demand),
        "total_shortage": float(total_shortage),
    }


def run_validation(df: pd.DataFrame, shared: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for idx, row in df.iterrows():
        q = float(shared.iloc[idx]["Q_star"])
        r = float(shared.iloc[idx]["R_star"])
        res = simulate_product(
            mu_D=row["mu_D"], sigma_D=row["sigma_D"],
            mu_L=row["mu_L"], sigma_L=row["sigma_L"],
            Q=q, R=r, seed=SIM_SEED + idx * 17,
        )
        rows.append(
            {
                "produkt_id": row["produkt_id"],
                "Q": round(q, 1),
                "R": round(r, 1),
                "sykluser": res["cycles"],
                "type1_realisert": round(res["type1_service"], 4),
                "fill_rate_realisert": round(res["fill_rate"], 4),
                "sum_etterspørsel": round(res["total_demand"], 0),
                "sum_manko": round(res["total_shortage"], 1),
            }
        )
    return pd.DataFrame(rows)


def plot_service(val: pd.DataFrame, target: float, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(val))
    width = 0.38
    ax.bar(x - width / 2, val["type1_realisert"], width,
           color=S_FILLS[0], edgecolor=S_DARKS[0], label="Type-1 (realisert)")
    ax.bar(x + width / 2, val["fill_rate_realisert"], width,
           color=S_FILLS[1], edgecolor=S_DARKS[1], label="Fill rate (realisert)")
    ax.axhline(target, ls="--", color=S_DARKS[4],
               label=f"Maal type-1 = {target:.2f}")
    ax.set_ylim(0.8, 1.02)
    ax.set_xticks(x)
    ax.set_xticklabels(val["produkt_id"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Servicenivaa", fontsize=11)
    ax.set_title(
        "Realisert servicenivaa (Monte Carlo-simulering, 2000 uker)",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="lower right", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: MONTE CARLO-VALIDERING")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "produkter.csv")
    shared = pd.read_csv(OUTPUT_DIR / "step04_shared_qr.csv")

    val = run_validation(df, shared)
    print("\nRealisert servicenivaa per produkt:")
    print(val.to_string(index=False))

    summary = {
        "maal_type1": SERVICE_LEVEL_TYPE1,
        "type1_gjennomsnitt": round(float(val["type1_realisert"].mean()), 4),
        "type1_min": round(float(val["type1_realisert"].min()), 4),
        "fill_rate_gjennomsnitt": round(float(val["fill_rate_realisert"].mean()), 4),
        "fill_rate_min": round(float(val["fill_rate_realisert"].min()), 4),
        "sim_weeks": SIM_WEEKS,
        "seed": SIM_SEED,
    }
    print("\nSammendrag:")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    val.to_csv(OUTPUT_DIR / "step05_validering.csv", index=False)
    with open(OUTPUT_DIR / "step05_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_service(val, SERVICE_LEVEL_TYPE1, OUTPUT_DIR / "multiqr_mc_service.png")


if __name__ == "__main__":
    main()
