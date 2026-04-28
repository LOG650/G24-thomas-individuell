"""
Steg 6: Sammenligning og tidsbesparelse
========================================
Sammenligner tre politikker:

1. Tilfeldig tildeling (baseline)
2. Frekvensbasert tildeling med 70/20/10-grenser (industri-default)
3. Frekvensbasert tildeling med grid-optimerte grenser

For hver politikk rapporteres forventet reisedistanse og utledede
produktivitetstall -- antall plukklinjer per time og aarlig besparelse
i gangeksekundertid. Vi antar at plukkeren gaar med ~4 km/t (1,1 m/s)
og har 15 sekunder per lokasjon for selve plukkhandlingen (denne siste
er uavhengig av layout og paavirker ikke sammenligningen).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import (
    DATA_DIR,
    OUTPUT_DIR,
    PRIMARY,
    INKMUTED,
    S_DARKS,
    S_FILLS,
)

WALK_SPEED = 1.1       # m/s
PICK_TIME = 15.0       # sekunder per lokasjon (uendret mellom politikkene)
WORK_HOURS_PER_YEAR = 1800  # antatt effektive plukktimer per aarsverk


def load_summary(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_kpis(
    e_distance_m: float, plukklinjer_per_dag: float, n_dager: int,
) -> dict:
    """Regn ut utledede nokkeltall for en politikk."""
    gang_tid_s = e_distance_m / WALK_SPEED
    syklus_s = gang_tid_s + PICK_TIME
    linjer_per_time = 3600.0 / syklus_s
    arlig_linjer = plukklinjer_per_dag * 365
    arlig_gangtid_timer = arlig_linjer * gang_tid_s / 3600.0
    return {
        "e_distance_m": round(e_distance_m, 2),
        "gang_tid_s_per_linje": round(gang_tid_s, 2),
        "linjer_per_time": round(linjer_per_time, 1),
        "arlig_gangtid_timer": round(arlig_gangtid_timer, 0),
    }


def plot_comparison(summary_df: pd.DataFrame, output_path: Path) -> None:
    """Soyled diagram over forventet distanse og besparelse."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    colors = [S_FILLS[0], S_FILLS[1], S_FILLS[4]]
    edges = [S_DARKS[0], S_DARKS[1], S_DARKS[4]]
    x = np.arange(len(summary_df))
    bars = ax1.bar(
        x, summary_df["e_distance_m"], color=colors, edgecolor=edges, lw=1.4,
    )
    for bar, v in zip(bars, summary_df["e_distance_m"]):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.5, f"{v:.1f} m",
                 ha="center", fontsize=10, fontweight="bold", color=INKMUTED)
    ax1.set_xticks(x)
    ax1.set_xticklabels(summary_df["metode_label"], fontsize=10)
    ax1.set_ylabel("Forventet distanse per plukk (m)", fontsize=11)
    ax1.set_title("Forventet reisedistanse per politikk",
                  fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")

    # Besparelse mot random
    baseline = summary_df["e_distance_m"].iloc[0]
    reduction = (baseline - summary_df["e_distance_m"]) / baseline * 100
    bars = ax2.bar(
        x, reduction, color=colors, edgecolor=edges, lw=1.4,
    )
    for bar, v in zip(bars, reduction):
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.3, f"{v:.1f} %",
                 ha="center", fontsize=10, fontweight="bold", color=INKMUTED)
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary_df["metode_label"], fontsize=10)
    ax2.set_ylabel("Reduksjon mot tilfeldig (%)", fontsize=11)
    ax2.set_title("Distansebesparelse mot tilfeldig tildeling",
                  fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.set_ylim(0, max(reduction.max() * 1.25, 5))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_mc_comparison(
    random_mc: np.ndarray, classbased_mc: np.ndarray,
    optimert_mc: np.ndarray, output_path: Path,
) -> None:
    """Overlagrede MC-distansehistogrammer."""
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    bins = np.linspace(
        min(random_mc.min(), classbased_mc.min(), optimert_mc.min()),
        max(random_mc.max(), classbased_mc.max(), optimert_mc.max()),
        45,
    )
    ax.hist(random_mc, bins=bins, color=S_FILLS[0], alpha=0.55,
            edgecolor=S_DARKS[0], lw=0.5,
            label=f"Tilfeldig (gj.snitt {random_mc.mean():.1f} m)")
    ax.hist(classbased_mc, bins=bins, color=S_FILLS[1], alpha=0.55,
            edgecolor=S_DARKS[1], lw=0.5,
            label=f"Klassebasert (gj.snitt {classbased_mc.mean():.1f} m)")
    ax.hist(optimert_mc, bins=bins, color=S_FILLS[4], alpha=0.55,
            edgecolor=S_DARKS[4], lw=0.5,
            label=f"Optimert (gj.snitt {optimert_mc.mean():.1f} m)")
    ax.set_xlabel("Distanse per plukk (m)", fontsize=11)
    ax.set_ylabel("Antall simulerte plukk", fontsize=11)
    ax.set_title("Sammenligning av distansefordelinger (Monte Carlo)",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 6: SAMMENLIGNING")
    print("=" * 60)

    random_summary = load_summary(OUTPUT_DIR / "step03_random_summary.json")
    cls_summary = load_summary(OUTPUT_DIR / "step04_classbased_summary.json")
    opt_summary = load_summary(OUTPUT_DIR / "step05_optimert_summary.json")

    step01 = load_summary(OUTPUT_DIR / "step01_summary.json")
    plukk_per_dag = step01["gjennomsnitt_plukk_per_dag"]
    n_dager = step01["antall_dager"]

    methods = [
        ("Tilfeldig", random_summary),
        ("Klassebasert (70/20/10)", cls_summary),
        (f"Sonebasert (K={opt_summary.get('n_zones', 3)})", opt_summary),
    ]
    rows = []
    for label, s in methods:
        kpis = compute_kpis(s["mc_gjennomsnitt_m"], plukk_per_dag, n_dager)
        row = {
            "metode_label": label,
            "e_distance_m": s["mc_gjennomsnitt_m"],
            "mc_median_m": s["mc_median_m"],
            "mc_p95_m": s["mc_p95_m"],
            **kpis,
        }
        rows.append(row)

    compare = pd.DataFrame(rows)

    baseline_d = compare["e_distance_m"].iloc[0]
    compare["reduksjon_pct"] = (
        (baseline_d - compare["e_distance_m"]) / baseline_d * 100
    ).round(1)
    baseline_time = compare["arlig_gangtid_timer"].iloc[0]
    compare["spart_gangtid_timer"] = (
        baseline_time - compare["arlig_gangtid_timer"]
    ).round(0)
    compare["spart_arsverk"] = (
        compare["spart_gangtid_timer"] / WORK_HOURS_PER_YEAR
    ).round(2)

    print("\nSammenligning:")
    print(compare.to_string(index=False))
    compare.to_csv(OUTPUT_DIR / "step06_comparison.csv", index=False)

    with open(OUTPUT_DIR / "step06_comparison_summary.json", "w",
              encoding="utf-8") as f:
        json.dump(
            compare.to_dict(orient="records"), f, indent=2,
            ensure_ascii=False,
        )

    random_mc = np.load(OUTPUT_DIR / "mc_distances_random.npy")
    class_mc = np.load(OUTPUT_DIR / "mc_distances_classbased.npy")
    opt_mc = np.load(OUTPUT_DIR / "mc_distances_optimert.npy")

    plot_comparison(compare, OUTPUT_DIR / "slot_savings.png")
    plot_mc_comparison(
        random_mc, class_mc, opt_mc,
        OUTPUT_DIR / "slot_distance_dist.png",
    )

    # Oppsummerende tekst
    print("\nBesparelse i gangtid per aar (antatt 1 plukker):")
    for _, r in compare.iterrows():
        print(f"  {r['metode_label']}: "
              f"{r['e_distance_m']:.1f} m/plukk, "
              f"{r['arlig_gangtid_timer']:.0f} t/aar "
              f"(spart {r['spart_gangtid_timer']:.0f} t "
              f"= {r['spart_arsverk']:.2f} aarsverk)")

    print("\nFerdig med steg 6.\n")


if __name__ == "__main__":
    main()
