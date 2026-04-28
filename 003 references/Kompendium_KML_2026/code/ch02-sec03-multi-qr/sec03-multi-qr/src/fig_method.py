"""
Genererer prosessdiagram-figur multiqr_method.png
================================================
Seks-stegs flyt for eksempelet, tegnet med matplotlib.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from step01_datainnsamling import OUTPUT_DIR, S_FILLS, S_DARKS, PRIMARY, INKMUTED


STEPS = [
    ("Steg 1", "Datainnsamling\n(10 produkter)"),
    ("Steg 2", "Uavhengig (Q,R)\n(baseline)"),
    ("Steg 3", "Formulering\n(Lagrange)"),
    ("Steg 4", "Optimering\n($\\lambda_V, \\lambda_B$)"),
    ("Steg 5", "Validering\n(Monte Carlo)"),
    ("Steg 6", "Sensitivitet\n(Pareto)"),
]


def draw(path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis("off")

    box_w, box_h = 1.65, 1.2
    gap = 0.25
    x0 = 0.2
    y = 0.9

    fills = [S_FILLS[0], S_FILLS[1], S_FILLS[3], S_FILLS[2], S_FILLS[1], S_FILLS[4]]
    strokes = [S_DARKS[0], S_DARKS[1], S_DARKS[3], S_DARKS[2], S_DARKS[1], S_DARKS[4]]

    xs = []
    for i, (header, body) in enumerate(STEPS):
        x = x0 + i * (box_w + gap)
        xs.append(x)
        box = FancyBboxPatch(
            (x, y), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            linewidth=1.8, edgecolor=strokes[i], facecolor=fills[i],
        )
        ax.add_patch(box)
        ax.text(
            x + box_w / 2, y + box_h - 0.3, header,
            ha="center", va="center", fontsize=10, fontweight="bold",
            color=strokes[i],
        )
        ax.text(
            x + box_w / 2, y + box_h / 2 - 0.1, body,
            ha="center", va="center", fontsize=9, color="#1F2933",
        )

    # Piler mellom boksene
    for i in range(len(STEPS) - 1):
        start = (xs[i] + box_w, y + box_h / 2)
        end = (xs[i + 1], y + box_h / 2)
        arrow = FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=14,
            linewidth=1.5, color=INKMUTED,
        )
        ax.add_patch(arrow)

    ax.text(
        6, 2.55, "Flerprodukts (Q,R) med delte skranker -- arbeidsflyt",
        ha="center", va="center", fontsize=12, fontweight="bold",
        color=PRIMARY,
    )

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    draw(OUTPUT_DIR / "multiqr_method.png")


if __name__ == "__main__":
    main()
