"""
Steg 6: Anbefaling og 3D Pareto-visualisering
=============================================
Genererer en 3D-fremstilling av Pareto-fronten (kost, utslipp, service)
og oppsummerer anbefalinger til beslutningstaker. Dersom step03/04/05
har produsert JSON-output, bygger vi visualiseringen fra disse; ellers
regenereres enkeltpunkter her.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

from solver import Instance, build_and_solve, load_instance

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def subset_instance(inst: Instance, k: int) -> Instance:
    """Mindre instance for 3D-punktsky: hastighet viktigere enn presisjon."""
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
    print("STEG 6: Anbefaling og 3D Pareto")
    print("=" * 60)

    # Les pareto fra step03 (2D)
    pareto_path = OUTPUT_DIR / "step03_pareto.json"
    if not pareto_path.exists():
        print("step03_pareto.json mangler -- kjor steg 3 forst")
        return
    pareto = json.loads(pareto_path.read_text(encoding="utf-8"))

    # For 3D-plot genererer vi ogsa noen ekstra punkter der vi i tillegg
    # begrenser service. Dette gir en punktsky som visualiserer 3D-
    # Pareto-avveiningen. For hastighet bruker vi subset av scenariosett.
    full_inst = load_instance(DATA_DIR)
    inst = subset_instance(full_inst, k=8)
    print(f"Bruker {len(inst.scenario_list)} scenarier for 3D-punktsky")

    # Mal service-bounds (2x2 rutenett = 4 ekstra punkter)
    s_vals = [p["service"] for p in pareto]
    s_min = min(s_vals)
    s_max = max(s_vals)
    s_targets = np.linspace(s_min * 1.02, s_max * 0.98, 2)

    extra = []
    for st in s_targets:
        for emis_frac in (0.4, 0.75):
            emis_min = min(p["emission_kg"] for p in pareto)
            emis_max = max(p["emission_kg"] for p in pareto)
            eps_e = emis_min + emis_frac * (emis_max - emis_min)
            print(f"\n>> service <= {st/1e6:.2f} Mkm, emission <= {eps_e/1000:.1f} tonn ...")
            r = build_and_solve(
                inst,
                objective="cost",
                eps_emission=float(eps_e),
                eps_service=float(st),
                time_limit=30,
            )
            if not np.isfinite(r["total_cost"]):
                continue
            extra.append(
                {
                    "total_cost": r["total_cost"],
                    "emission_kg": r["emission_kg"],
                    "service": r["service"],
                    "opened": r["opened"],
                }
            )

    all_points = pareto + extra

    # 3D-plot
    fig = plt.figure(figsize=(10, 7))
    ax = fig.add_subplot(111, projection="3d")

    co = np.array([p["total_cost"] / 1e6 for p in all_points])
    em = np.array([p["emission_kg"] / 1000 for p in all_points])
    sv = np.array([p["service"] / 1e6 for p in all_points])

    # Fargelegg etter kost-rank
    sc = ax.scatter(
        em,
        sv,
        co,
        c=co,
        cmap="viridis",
        s=110,
        edgecolors="#1F2933",
        linewidths=0.7,
        alpha=0.9,
    )

    # Marker Pareto-2D (fra step03) spesielt
    pco = np.array([p["total_cost"] / 1e6 for p in pareto])
    pem = np.array([p["emission_kg"] / 1000 for p in pareto])
    psv = np.array([p["service"] / 1e6 for p in pareto])
    ax.plot(pem, psv, pco, "-", color="#961D1C", linewidth=2.2, alpha=0.8, label="Cost-vs-emis front")
    ax.scatter(pem, psv, pco, s=180, color="#ED9F9E", edgecolors="#961D1C", linewidths=1.6, label="2D Pareto")

    ax.set_xlabel("Utslipp (tonn CO2)", fontsize=10)
    ax.set_ylabel("Service (Mkm)", fontsize=10)
    ax.set_zlabel("Kost (MEUR)", fontsize=10)
    ax.set_title("3D Pareto-front: kost vs utslipp vs service", fontsize=12, fontweight="bold")
    fig.colorbar(sc, ax=ax, shrink=0.6, label="Kost (MEUR)", pad=0.1)
    ax.legend(loc="upper left", fontsize=9)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "gronnsc_pareto_3d.png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {OUTPUT_DIR / 'gronnsc_pareto_3d.png'}")

    # Anbefaling: "knee point" - punktet med minst euklidisk avstand til
    # utopi-punktet (min av alle tre mal)
    utopia = np.array([em.min(), sv.min(), co.min()])
    pts = np.column_stack([em, sv, co])
    # Normaliser
    ranges = pts.max(axis=0) - pts.min(axis=0)
    ranges[ranges == 0] = 1
    pts_norm = (pts - pts.min(axis=0)) / ranges
    ut_norm = np.zeros(3)
    dists = np.linalg.norm(pts_norm - ut_norm, axis=1)
    best_idx = int(np.argmin(dists))
    best = all_points[best_idx]

    recommendation = {
        "recommended_point": {
            "total_cost": best["total_cost"],
            "emission_kg": best["emission_kg"],
            "service": best["service"],
            "opened": best["opened"],
        },
        "utopia_distance_normalized": float(dists[best_idx]),
        "n_pareto_points_2d": len(pareto),
        "n_total_explored": len(all_points),
    }
    with open(OUTPUT_DIR / "step06_recommendation.json", "w", encoding="utf-8") as f:
        json.dump(recommendation, f, indent=2, ensure_ascii=False)

    print("\nANBEFALING (knee-point, minste normalisert avstand til utopi):")
    print(f"  Kost:     {best['total_cost']:,.0f} EUR/ar ({best['total_cost']/1e6:.2f} MEUR)")
    print(f"  Utslipp:  {best['emission_kg']/1000:.1f} tonn CO2/ar")
    print(f"  Service:  {best['service']/1e6:.2f} Mkm")
    print(f"  Apne DC:  {best['opened']}")


if __name__ == "__main__":
    main()
