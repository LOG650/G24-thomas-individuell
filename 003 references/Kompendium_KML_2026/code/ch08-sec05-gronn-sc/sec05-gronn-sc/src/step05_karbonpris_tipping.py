"""
Steg 5: Karbonpris-tipping-punkter
==================================
Parametriserer karbonprisen fra 0 til 250 EUR/tonn og identifiserer
punktene der optimal losning *bytter* modus (typisk lastebil -> tog
-> skip). Dette er en konkret indikator for hvor mye karbonpris som
skal til for å drive modal shift.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from solver import Instance, build_and_solve, load_instance

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def subset_instance(inst: Instance, k: int) -> Instance:
    """Bygg en mindre instance med de k forste scenariene av de opprinnelige.

    Karbonpris-eksperimentet skal bare vise tipping-punktet; det trenger
    ikke hele scenariosettet. Ved a ta et subset akselererer vi kjoringen
    dramatisk uten at resultatene endrer kvalitativt.
    """
    sub_scen = inst.scenarios[inst.scenarios["scenario"] < k].copy()
    return Instance(
        dcs=inst.dcs,
        customers=inst.customers,
        modes=inst.modes,
        edges=inst.edges,
        scenarios=sub_scen,
    )


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("STEG 5: Karbonpris-tipping-punkter")
    print("=" * 60)

    full_inst = load_instance(DATA_DIR)
    # Bruk bare 8 scenarier for karbonpris-sveipet; vi kjorer mange
    # MIP-er og trenger hastighet. Tipping-punktet er robust mot
    # scenario-antallet.
    inst = subset_instance(full_inst, k=8)
    print(f"Bruker {len(inst.scenario_list)} scenarier for karbonpris-sveipet")

    # Karbonpriser å evaluere (EUR/tonn CO2)
    prices = [0, 25, 50, 75, 100, 125, 150, 200, 250]

    results = []
    for p in prices:
        print(f"\n>> Karbonpris = {p} EUR/tonn ...")
        r = build_and_solve(inst, objective="cost", carbon_price=p, time_limit=30)
        mv = r["modal_volume"]
        total = sum(mv.values())
        share_truck = mv.get("truck", 0) / total if total > 0 else 0
        share_rail = mv.get("rail", 0) / total if total > 0 else 0
        share_ship = mv.get("ship", 0) / total if total > 0 else 0

        results.append(
            {
                "carbon_price": p,
                "total_cost": r["total_cost"],
                "emission_kg": r["emission_kg"],
                "service": r["service"],
                "opened": r["opened"],
                "share_truck": share_truck,
                "share_rail": share_rail,
                "share_ship": share_ship,
                "modal_volume": mv,
            }
        )
        print(
            f"   cost={r['total_cost']:,.0f} EUR, emis={r['emission_kg']/1000:.1f} t, "
            f"moduser: truck={share_truck:.1%}, rail={share_rail:.1%}, ship={share_ship:.1%}"
        )

    with open(OUTPUT_DIR / "step05_carbon_tipping.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Plot modal share vs karbonpris
    pr = np.array([r["carbon_price"] for r in results])
    truck = np.array([r["share_truck"] for r in results])
    rail = np.array([r["share_rail"] for r in results])
    ship = np.array([r["share_ship"] for r in results])
    emis = np.array([r["emission_kg"] / 1000 for r in results])
    cost = np.array([r["total_cost"] / 1e6 for r in results])

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    axes[0].stackplot(
        pr,
        truck,
        rail,
        ship,
        labels=["Lastebil", "Jernbane", "Skip"],
        colors=["#ED9F9E", "#8CC8E5", "#97D4B7"],
        edgecolor="white",
        linewidth=0.8,
    )
    axes[0].set_xlabel("Karbonpris (EUR/tonn CO2)", fontsize=11)
    axes[0].set_ylabel("Modal andel", fontsize=11)
    axes[0].set_title("Modal shift med karbonpris", fontsize=12, fontweight="bold")
    axes[0].legend(loc="upper right", fontsize=10)
    axes[0].set_ylim(0, 1)
    axes[0].grid(True, alpha=0.3)

    ax2 = axes[1]
    ln1 = ax2.plot(pr, cost, "o-", color="#1F6587", linewidth=2, markersize=7, label="Kost (MEUR)")
    ax2.set_xlabel("Karbonpris (EUR/tonn CO2)", fontsize=11)
    ax2.set_ylabel("Total kostnad (MEUR/ar)", fontsize=11, color="#1F6587")
    ax2.tick_params(axis="y", labelcolor="#1F6587")
    ax2.grid(True, alpha=0.3)

    ax2b = ax2.twinx()
    ln2 = ax2b.plot(pr, emis, "s-", color="#307453", linewidth=2, markersize=7, label="Utslipp (tonn)")
    ax2b.set_ylabel("Utslipp (tonn CO2/ar)", fontsize=11, color="#307453")
    ax2b.tick_params(axis="y", labelcolor="#307453")

    ax2.set_title("Kost og utslipp vs karbonpris", fontsize=12, fontweight="bold")
    lns = ln1 + ln2
    ax2.legend(lns, [l.get_label() for l in lns], loc="center right", fontsize=10)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "gronnsc_modal_shift.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {OUTPUT_DIR / 'gronnsc_modal_shift.png'}")

    # Identifiser tipping points: der modal-andel endrer seg med > 5pp
    tipping = []
    for i in range(1, len(results)):
        dt = truck[i] - truck[i - 1]
        dr = rail[i] - rail[i - 1]
        ds = ship[i] - ship[i - 1]
        if max(abs(dt), abs(dr), abs(ds)) > 0.05:
            tipping.append(
                {
                    "price_from": int(pr[i - 1]),
                    "price_to": int(pr[i]),
                    "delta_truck": float(dt),
                    "delta_rail": float(dr),
                    "delta_ship": float(ds),
                }
            )

    print("\nTipping-punkter (modal-endring > 5pp):")
    for t in tipping:
        print(
            f"  {t['price_from']} -> {t['price_to']} EUR/t: "
            f"d_truck={t['delta_truck']:+.1%}, d_rail={t['delta_rail']:+.1%}, d_ship={t['delta_ship']:+.1%}"
        )

    with open(OUTPUT_DIR / "step05_tipping.json", "w", encoding="utf-8") as f:
        json.dump(tipping, f, indent=2, ensure_ascii=False)

    # Ekstra: enkel kost/utslipp vs karbonpris figur
    fig2, ax = plt.subplots(figsize=(8, 5))
    ax.plot(pr, emis, "o-", color="#307453", linewidth=2.2, markersize=8)
    # Marker tipping-punkter
    for t in tipping:
        ax.axvspan(t["price_from"], t["price_to"], alpha=0.12, color="#BD94D7")
    ax.set_xlabel("Karbonpris (EUR/tonn CO2)", fontsize=11)
    ax.set_ylabel("Utslipp (tonn CO2/ar)", fontsize=11)
    ax.set_title(
        "Tipping-punkter: karbonpris hvor optimal losning bytter modus",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "gronnsc_carbon_tipping.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {OUTPUT_DIR / 'gronnsc_carbon_tipping.png'}")


if __name__ == "__main__":
    main()
