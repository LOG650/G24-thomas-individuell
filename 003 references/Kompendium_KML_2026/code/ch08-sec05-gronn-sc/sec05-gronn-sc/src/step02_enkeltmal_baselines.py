"""
Steg 2: Enkeltmål-basislinjer
=============================
Vi kjører MIP-en med hver enkelt målfunksjon isolert:
- Min kostnad (ingen utslippsbegrensning, ingen karbonpris)
- Min utslipp (ingen kostnadsbegrensning)
- Min service (vektet avstand)

Dette etablerer ekstrempunktene til Pareto-fronten og viser hvor
dramatisk losningen endrer seg med ulik målfunksjon.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from solver import build_and_solve, load_instance

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def plot_baseline_comparison(results: dict, output_path: Path) -> None:
    labels = ["Min kost", "Min utslipp", "Min service"]
    costs = [results[k]["total_cost"] / 1e6 for k in ("cost", "emission", "service")]
    emis = [results[k]["emission_kg"] / 1000 for k in ("cost", "emission", "service")]
    serv = [results[k]["service"] / 1e6 for k in ("cost", "emission", "service")]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))

    colors = ["#8CC8E5", "#97D4B7", "#F6BA7C"]
    edges = ["#1F6587", "#307453", "#9C540B"]

    axes[0].bar(labels, costs, color=colors, edgecolor=edges, linewidth=1.5)
    axes[0].set_ylabel("Total kostnad (MEUR/ar)", fontsize=11)
    axes[0].set_title("Kostnad", fontsize=11, fontweight="bold")
    axes[0].grid(axis="y", alpha=0.3)

    axes[1].bar(labels, emis, color=colors, edgecolor=edges, linewidth=1.5)
    axes[1].set_ylabel("CO2 (tonn/ar)", fontsize=11)
    axes[1].set_title("Utslipp", fontsize=11, fontweight="bold")
    axes[1].grid(axis="y", alpha=0.3)

    axes[2].bar(labels, serv, color=colors, edgecolor=edges, linewidth=1.5)
    axes[2].set_ylabel("Service (millioner enhets-km)", fontsize=11)
    axes[2].set_title("Service", fontsize=11, fontweight="bold")
    axes[2].grid(axis="y", alpha=0.3)

    fig.suptitle(
        "Enkeltmal-basislinjer: KPI-er for hver isolert malfunksjon",
        fontsize=12,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 2: Enkeltmal-basislinjer")
    print("=" * 60)

    inst = load_instance(DATA_DIR)

    results = {}
    for obj in ("cost", "emission", "service"):
        print(f"\n>> Loser MIP med mal: {obj} ...")
        r = build_and_solve(inst, objective=obj, carbon_price=0.0, time_limit=120)
        results[obj] = r
        print(f"  Status: {r['status']}, tid: {r['solve_time_s']:.1f}s")
        print(f"  Apnede DC: {r['opened']}")
        print(f"  Totalkost: {r['total_cost']:,.0f} EUR")
        print(f"  Utslipp:   {r['emission_kg']/1000:,.1f} tonn CO2")
        print(f"  Service:   {r['service']/1e6:,.3f} M enhets-km")
        print(f"  Modal: {dict((k, round(v,0)) for k,v in r['modal_volume'].items())}")

    # Lagre
    clean = {
        k: {
            "opened": v["opened"],
            "total_cost": v["total_cost"],
            "fixed_cost": v["fixed_cost"],
            "transport_cost": v["transport_cost"],
            "carbon_cost": v["carbon_cost"],
            "emission_kg": v["emission_kg"],
            "service": v["service"],
            "modal_volume": v["modal_volume"],
            "solve_time_s": v["solve_time_s"],
        }
        for k, v in results.items()
    }
    with open(OUTPUT_DIR / "step02_baselines.json", "w", encoding="utf-8") as f:
        json.dump(clean, f, indent=2, ensure_ascii=False)

    plot_baseline_comparison(results, OUTPUT_DIR / "gronnsc_baselines.png")


if __name__ == "__main__":
    main()
