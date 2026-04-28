"""
Steg 3: Epsilon-constraint -> Pareto-front
==========================================
Bygger Pareto-fronten ved å minimere kostnad mens utslipp begrenses til
varierende tak (epsilon). Dette gir en 2D-front (cost vs emission).
Service-komponenten gir oss et tredje mål som visualiseres separat.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from solver import build_and_solve, load_instance

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("STEG 3: Epsilon-constraint Pareto-front")
    print("=" * 60)

    inst = load_instance(DATA_DIR)

    # Ekstrempunkter: finn min emission og min cost for å sette epsilon-område
    r_min_cost = build_and_solve(inst, objective="cost", time_limit=60)
    r_min_emis = build_and_solve(inst, objective="emission", time_limit=60)

    emis_max = r_min_cost["emission_kg"]
    emis_min = r_min_emis["emission_kg"]
    cost_min = r_min_cost["total_cost"]
    cost_max = r_min_emis["total_cost"]

    print(f"\nEkstrempunkter:")
    print(f"  min-cost  => cost={cost_min:,.0f} EUR, emis={emis_max/1000:,.1f} tonn")
    print(f"  min-emis  => cost={cost_max:,.0f} EUR, emis={emis_min/1000:,.1f} tonn")

    # Epsilon-steg mellom emis_min og emis_max
    n_points = 9
    eps_values = np.linspace(emis_min * 1.001, emis_max * 0.999, n_points)

    pareto = [
        {
            "eps_emission_kg": float(emis_max),
            "total_cost": float(cost_min),
            "emission_kg": float(r_min_cost["emission_kg"]),
            "service": float(r_min_cost["service"]),
            "opened": r_min_cost["opened"],
            "modal_volume": r_min_cost["modal_volume"],
        }
    ]

    for eps in eps_values:
        print(f"\n>> Epsilon emis = {eps/1000:.1f} tonn ...")
        r = build_and_solve(
            inst, objective="cost", eps_emission=float(eps), time_limit=60
        )
        if not np.isfinite(r["total_cost"]):
            print(f"   INFEASIBLE -- hopper over")
            continue
        pareto.append(
            {
                "eps_emission_kg": float(eps),
                "total_cost": float(r["total_cost"]),
                "emission_kg": float(r["emission_kg"]),
                "service": float(r["service"]),
                "opened": r["opened"],
                "modal_volume": r["modal_volume"],
            }
        )
        print(
            f"   cost={r['total_cost']:,.0f} EUR, "
            f"emis={r['emission_kg']/1000:.1f} tonn, "
            f"service={r['service']/1e6:.2f} Mkm"
        )

    pareto.append(
        {
            "eps_emission_kg": float(emis_min),
            "total_cost": float(cost_max),
            "emission_kg": float(emis_min),
            "service": float(r_min_emis["service"]),
            "opened": r_min_emis["opened"],
            "modal_volume": r_min_emis["modal_volume"],
        }
    )

    # Sorter pareto-fronten etter emission
    pareto_sorted = sorted(pareto, key=lambda p: p["emission_kg"])

    with open(OUTPUT_DIR / "step03_pareto.json", "w", encoding="utf-8") as f:
        json.dump(pareto_sorted, f, indent=2, ensure_ascii=False)

    # Plot 2D: cost vs emission
    em_arr = np.array([p["emission_kg"] / 1000 for p in pareto_sorted])
    co_arr = np.array([p["total_cost"] / 1e6 for p in pareto_sorted])
    sv_arr = np.array([p["service"] / 1e6 for p in pareto_sorted])

    fig, ax = plt.subplots(figsize=(8, 5.5))
    ax.plot(em_arr, co_arr, "-", color="#1F6587", linewidth=2, alpha=0.7, zorder=1)
    sc = ax.scatter(
        em_arr,
        co_arr,
        c=sv_arr,
        s=130,
        cmap="viridis",
        edgecolors="#1F2933",
        linewidths=1.2,
        zorder=2,
    )
    cbar = fig.colorbar(sc, ax=ax, shrink=0.85)
    cbar.set_label("Service (Mkm)", fontsize=10)

    # Merk ekstrempunkter
    ax.annotate(
        "min utslipp",
        (em_arr[0], co_arr[0]),
        xytext=(10, 10),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        color="#307453",
    )
    ax.annotate(
        "min kost",
        (em_arr[-1], co_arr[-1]),
        xytext=(-30, 12),
        textcoords="offset points",
        fontsize=10,
        fontweight="bold",
        color="#1F6587",
    )

    ax.set_xlabel("Utslipp (tonn CO2/ar)", fontsize=11)
    ax.set_ylabel("Total kostnad (MEUR/ar)", fontsize=11)
    ax.set_title(
        "Pareto-front: kostnad vs utslipp (farge = service-niva)",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "gronnsc_pareto_2d.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {OUTPUT_DIR / 'gronnsc_pareto_2d.png'}")


if __name__ == "__main__":
    main()
