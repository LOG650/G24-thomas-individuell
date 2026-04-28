"""
Steg 6: Sammenligning av strategier
===================================
Leser step05-resultatene og genererer:
  - en side-ved-side sokyleplott med KPIene
  - en numerisk tabell (JSON) for LaTeX
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from common import PALETTE_FILL, PALETTE_STROKE

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 6: SAMMENLIGNING")
    print("=" * 60)

    with open(OUTPUT_DIR / "step05_simpy.json", "r", encoding="utf-8") as f:
        runs = json.load(f)

    # Tildel korte etiketter
    labels = ["A: Integrert", "B: MIP+FIFO-batch", "C: FIFO+k-medoids", "D: Baseline"]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # 1) On-time-share
    on_time = np.array([r["on_time_share"] * 100 for r in runs])
    axes[0].bar(labels, on_time, color=PALETTE_FILL, edgecolor=PALETTE_STROKE)
    axes[0].set_title("Deadline-overholdelse (%)", fontsize=11, fontweight="bold")
    axes[0].set_ylim(0, 105)
    axes[0].grid(True, alpha=0.3, axis="y")
    for i, v in enumerate(on_time):
        axes[0].text(i, v + 1.2, f"{v:.1f}", ha="center", fontsize=9, fontweight="bold")
    axes[0].tick_params(axis="x", labelsize=8)

    # 2) Gjsnitt fullforingstid
    mean_t = np.array([r["mean_completion_min"] / 60.0 for r in runs])
    axes[1].bar(labels, mean_t, color=PALETTE_FILL, edgecolor=PALETTE_STROKE)
    axes[1].set_title("Gjsnitt fullforing (timer)", fontsize=11, fontweight="bold")
    axes[1].grid(True, alpha=0.3, axis="y")
    for i, v in enumerate(mean_t):
        axes[1].text(i, v + max(mean_t) * 0.02, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
    axes[1].tick_params(axis="x", labelsize=8)

    # 3) Pakkeko (gjsnitt)
    qavg = np.array([r["mean_pack_queue"] for r in runs])
    axes[2].bar(labels, qavg, color=PALETTE_FILL, edgecolor=PALETTE_STROKE)
    axes[2].set_title("Gjsnitt pakkeko (batcher)", fontsize=11, fontweight="bold")
    axes[2].grid(True, alpha=0.3, axis="y")
    for i, v in enumerate(qavg):
        axes[2].text(i, v + max(qavg) * 0.03 + 0.05, f"{v:.2f}", ha="center", fontsize=9, fontweight="bold")
    axes[2].tick_params(axis="x", labelsize=8)

    plt.tight_layout()
    out_fig = OUTPUT_DIR / "intlag_simpy_kpi.png"
    plt.savefig(out_fig, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {out_fig}")

    # Tabell-data for LaTeX
    summary = []
    for r, short in zip(runs, labels):
        summary.append(
            {
                "strategy": short,
                "name": r["name"],
                "completed": r["completed"],
                "on_time_share": round(r["on_time_share"], 4),
                "mean_completion_min": round(r["mean_completion_min"], 2),
                "mean_pack_queue": round(r["mean_pack_queue"], 3),
                "max_pack_queue": round(r["max_pack_queue"], 3),
            }
        )
    with open(OUTPUT_DIR / "step06_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Sammendrag lagret: {OUTPUT_DIR / 'step06_summary.json'}")

    # Tekst-sammendrag
    print("\nRelativt (vs baseline D):")
    base = runs[-1]
    for r, short in zip(runs, labels):
        ot_delta = (r["on_time_share"] - base["on_time_share"]) * 100
        pct_improvement = 0.0
        if base["mean_completion_min"] > 0:
            pct_improvement = (base["mean_completion_min"] - r["mean_completion_min"]) / base["mean_completion_min"] * 100
        print(
            f"  {short:25s}  deadline +{ot_delta:+6.2f} pp,  "
            f"fullforing {pct_improvement:+6.1f}%"
        )


if __name__ == "__main__":
    main()
