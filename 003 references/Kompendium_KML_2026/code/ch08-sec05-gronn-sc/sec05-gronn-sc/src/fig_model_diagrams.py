"""
Pedagogiske figurer for Modell-subseksjonen
============================================
Genererer:
- gronnsc_method.png      : 6-stegs prosessdiagram
- gronnsc_schematic.png   : to-trinns stokastisk struktur (stage-1 -> scenarioer -> stage-2)
- gronnsc_epsilon_pareto.png : illustrasjon av epsilon-constraint metoden
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def draw_method_diagram(output_path: Path) -> None:
    """6-stegs prosess, sekvensielle bokser."""
    fig, ax = plt.subplots(figsize=(12, 3.2))

    steps = [
        ("1. Data", "6 DC,\n50 kunder,\n3 moduser", "#8CC8E5", "#1F6587"),
        ("2. Basislinje", "Enkeltmal\nMIP\n(cost / emis)", "#97D4B7", "#307453"),
        ("3. Epsilon", "Pareto-front\n(cost vs emis)", "#F6BA7C", "#9C540B"),
        ("4. Scenario-red.", "Kantorovich\nfast-forward", "#BD94D7", "#5A2C77"),
        ("5. Karbonpris", "Modal shift\ntipping-punkt", "#ED9F9E", "#961D1C"),
        ("6. Anbefaling", "3D-visualisering\n+ knee-point", "#8CC8E5", "#1F6587"),
    ]

    box_w, box_h = 1.65, 1.45
    gap = 0.25
    x0 = 0.1
    y = 0.5

    for i, (title, subtitle, fill, edge) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        box = FancyBboxPatch(
            (x, y),
            box_w,
            box_h,
            boxstyle="round,pad=0.06",
            linewidth=1.6,
            edgecolor=edge,
            facecolor=fill,
        )
        ax.add_patch(box)
        ax.text(
            x + box_w / 2,
            y + box_h - 0.25,
            title,
            ha="center",
            va="top",
            fontsize=10,
            fontweight="bold",
            color=edge,
        )
        ax.text(
            x + box_w / 2,
            y + box_h / 2 - 0.2,
            subtitle,
            ha="center",
            va="center",
            fontsize=8.5,
            color="#1F2933",
        )
        # Pil til neste
        if i < len(steps) - 1:
            arr = FancyArrowPatch(
                (x + box_w + 0.02, y + box_h / 2),
                (x + box_w + gap - 0.02, y + box_h / 2),
                arrowstyle="-|>",
                mutation_scale=14,
                color="#556270",
                linewidth=1.4,
            )
            ax.add_patch(arr)

    ax.set_xlim(0, x0 + len(steps) * (box_w + gap) - gap + 0.1)
    ax.set_ylim(0, 2.3)
    ax.axis("off")
    ax.set_title(
        "Prosessen i seks steg",
        fontsize=12,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def draw_two_stage_schematic(output_path: Path) -> None:
    """To-trinns stokastisk struktur: stage-1 -> scenariotre -> stage-2."""
    fig, ax = plt.subplots(figsize=(12, 5.2))

    # Stage 1 boks
    s1 = FancyBboxPatch(
        (0.3, 2.0),
        1.9,
        1.2,
        boxstyle="round,pad=0.1",
        linewidth=1.8,
        edgecolor="#1F6587",
        facecolor="#8CC8E5",
    )
    ax.add_patch(s1)
    ax.text(
        1.25,
        2.95,
        "STAGE 1",
        ha="center",
        va="center",
        fontsize=12,
        fontweight="bold",
        color="#1F6587",
    )
    ax.text(
        1.25,
        2.55,
        "$y_i \\in \\{0,1\\}$\nåpne DC\n(her-og-nå)",
        ha="center",
        va="center",
        fontsize=10,
        color="#1F2933",
    )

    # Scenariomarkør i midten
    ax.text(
        3.6,
        4.5,
        "Scenarier $s$\nmed sannsynligheter $p^s$",
        ha="center",
        va="center",
        fontsize=10,
        color="#556270",
        style="italic",
    )

    # Tre scenariogrener
    scen_y = [4.0, 2.6, 1.2]
    scen_lbl = [r"$\xi^1$ (lav)", r"$\xi^2$ (snitt)", r"$\xi^S$ (høy)"]
    fills = ["#F6BA7C", "#F6BA7C", "#F6BA7C"]
    for i, (yy, lbl, fc) in enumerate(zip(scen_y, scen_lbl, fills)):
        # Pil fra stage-1 til scenario-punkt
        arr = FancyArrowPatch(
            (2.2, 2.6),
            (3.3, yy),
            arrowstyle="-|>",
            mutation_scale=14,
            color="#556270",
            linewidth=1.3,
        )
        ax.add_patch(arr)
        # Scenariobokser (små runde)
        circ = mpatches.FancyBboxPatch(
            (3.4, yy - 0.25),
            0.95,
            0.5,
            boxstyle="round,pad=0.04",
            linewidth=1.4,
            edgecolor="#9C540B",
            facecolor=fc,
        )
        ax.add_patch(circ)
        ax.text(3.87, yy, lbl, ha="center", va="center", fontsize=10, color="#1F2933")

        # Stage-2 bokser til høyre for hvert scenario
        s2 = FancyBboxPatch(
            (5.0, yy - 0.42),
            2.6,
            0.84,
            boxstyle="round,pad=0.08",
            linewidth=1.5,
            edgecolor="#307453",
            facecolor="#97D4B7",
        )
        ax.add_patch(s2)
        ax.text(
            6.3,
            yy + 0.16,
            "STAGE 2",
            ha="center",
            va="center",
            fontsize=10,
            fontweight="bold",
            color="#307453",
        )
        ax.text(
            6.3,
            yy - 0.18,
            "$x^s_{ijm} \\in [0,1]$  allokering",
            ha="center",
            va="center",
            fontsize=9,
            color="#1F2933",
        )
        arr2 = FancyArrowPatch(
            (4.37, yy),
            (4.95, yy),
            arrowstyle="-|>",
            mutation_scale=13,
            color="#556270",
            linewidth=1.2,
        )
        ax.add_patch(arr2)

    # Målfunksjon som boks helt til høyre
    obj = FancyBboxPatch(
        (8.0, 2.0),
        2.3,
        1.2,
        boxstyle="round,pad=0.1",
        linewidth=1.8,
        edgecolor="#5A2C77",
        facecolor="#BD94D7",
    )
    ax.add_patch(obj)
    ax.text(
        9.15,
        2.95,
        "TRE MAL",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color="#5A2C77",
    )
    ax.text(
        9.15,
        2.45,
        "Kost\nUtslipp\nService",
        ha="center",
        va="center",
        fontsize=9.5,
        color="#1F2933",
    )
    # Pil fra stage-2 bokser til mal
    for yy in scen_y:
        arr3 = FancyArrowPatch(
            (7.65, yy),
            (8.0, 2.6),
            arrowstyle="-|>",
            mutation_scale=12,
            color="#556270",
            linewidth=1.0,
            alpha=0.7,
        )
        ax.add_patch(arr3)

    ax.set_xlim(0, 11)
    ax.set_ylim(0.5, 5.5)
    ax.axis("off")
    ax.set_title(
        "To-trinns stokastisk flermal struktur: stage-1 beslutning, "
        "scenariorealisering, stage-2 recourse, tre mal",
        fontsize=11.5,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def draw_epsilon_constraint_illustration(output_path: Path) -> None:
    """Skjematisk illustrasjon av epsilon-constraint metoden."""
    fig, ax = plt.subplots(figsize=(7.5, 5.3))

    # Tegn en skjematisk Pareto-front i 2D (cost vs emission)
    emis = np.linspace(1, 9, 100)
    cost = 8 + 12 / emis  # skjematisk konveks front

    ax.plot(emis, cost, "-", color="#1F6587", linewidth=2.5, alpha=0.85, label="Pareto-front")

    # Marker epsilon-steg
    eps_pts = [2.0, 3.5, 5.0, 7.0]
    for i, e in enumerate(eps_pts):
        c_pt = 8 + 12 / e
        ax.axvline(e, color="#9C540B", linestyle="--", linewidth=1.0, alpha=0.55)
        ax.scatter([e], [c_pt], s=100, color="#F6BA7C", edgecolors="#9C540B", linewidths=1.5, zorder=3)
        ax.annotate(
            rf"$\epsilon_{{{i+1}}}$",
            (e, 0.2),
            ha="center",
            fontsize=11,
            color="#9C540B",
        )

    # Akser og etiketter
    ax.set_xlabel(r"Utslipp $E$  (målvariabel begrenset av $\epsilon$)", fontsize=11)
    ax.set_ylabel(r"Kostnad $C$  (målvariabel som minimeres)", fontsize=11)
    ax.set_title(
        "Epsilon-constraint: minimer $C$ underlagt $E \\leq \\epsilon_k$",
        fontsize=12,
        fontweight="bold",
    )
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 25)
    ax.grid(True, alpha=0.3)

    # Beskrivende annotering
    ax.annotate(
        "Hver $\\epsilon_k$ gir\nett Pareto-punkt",
        xy=(5.0, 8 + 12 / 5.0),
        xytext=(6.8, 15),
        fontsize=10,
        ha="center",
        arrowprops=dict(arrowstyle="->", color="#556270", lw=1.1),
        color="#1F2933",
    )

    ax.legend(loc="upper right", fontsize=10, frameon=True)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    draw_method_diagram(OUTPUT_DIR / "gronnsc_method.png")
    draw_two_stage_schematic(OUTPUT_DIR / "gronnsc_schematic.png")
    draw_epsilon_constraint_illustration(OUTPUT_DIR / "gronnsc_epsilon_illustration.png")


if __name__ == "__main__":
    main()
