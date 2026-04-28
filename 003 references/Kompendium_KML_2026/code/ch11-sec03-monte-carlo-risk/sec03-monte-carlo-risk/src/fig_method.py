"""
Genererer prosessdiagram for seksjon 'Monte Carlo risikokvantifisering'.
Skjematisk figur med 6 trinn, lagres direkte til LaTeX-mappen.
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from step01_datainnsamling import (
    COLOR_INK,
    COLOR_S1,
    COLOR_S1_DARK,
    COLOR_S2,
    COLOR_S2_DARK,
    COLOR_S3,
    COLOR_S3_DARK,
    COLOR_S4,
    COLOR_S4_DARK,
    COLOR_S5,
    COLOR_S5_DARK,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

STEPS = [
    ('Steg 1', 'Datainnsamling', 'Parametre og\nfordelinger',
     COLOR_S1, COLOR_S1_DARK),
    ('Steg 2', 'Basissimulering', 'En enkelt\n(\u00e5rs\\)-run',
     COLOR_S2, COLOR_S2_DARK),
    ('Steg 3', 'Monte Carlo', '10\u202f000 runs,\nVaR og CVaR',
     COLOR_S3, COLOR_S3_DARK),
    ('Steg 4', 'Tornado', 'Sensitivitet\nper driver',
     COLOR_S4, COLOR_S4_DARK),
    ('Steg 5', 'Mitigasjon', 'Tiltak og\nrisikoreduksjon',
     COLOR_S5, COLOR_S5_DARK),
    ('Steg 6', 'Anbefaling', 'Kost/nytte-\ntrade-off',
     COLOR_S1, COLOR_S1_DARK),
]


def draw_method(output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(12, 3.6))
    ax.set_xlim(0, len(STEPS) * 2 + 0.5)
    ax.set_ylim(0, 3.5)
    ax.axis('off')

    box_w = 1.7
    box_h = 2.3
    gap = 0.3
    y0 = 0.7

    for i, (num, title, subtitle, color, dark) in enumerate(STEPS):
        x0 = 0.25 + i * (box_w + gap)
        box = mpatches.FancyBboxPatch(
            (x0, y0), box_w, box_h,
            boxstyle='round,pad=0.02,rounding_size=0.12',
            facecolor=color, edgecolor=dark, linewidth=1.7, alpha=0.95,
        )
        ax.add_patch(box)
        ax.text(x0 + box_w / 2, y0 + box_h - 0.35, num,
                ha='center', va='center',
                fontsize=11, fontweight='bold', color=dark)
        ax.text(x0 + box_w / 2, y0 + box_h - 0.95, title,
                ha='center', va='center',
                fontsize=12, fontweight='bold', color=COLOR_INK)
        ax.text(x0 + box_w / 2, y0 + 0.7, subtitle,
                ha='center', va='center',
                fontsize=9.5, color=COLOR_INK)

        # Pil til neste boks
        if i < len(STEPS) - 1:
            x_arrow_start = x0 + box_w + 0.04
            x_arrow_end = x0 + box_w + gap - 0.04
            ax.annotate('', xy=(x_arrow_end, y0 + box_h / 2),
                        xytext=(x_arrow_start, y0 + box_h / 2),
                        arrowprops=dict(arrowstyle='->',
                                        color=COLOR_INK, lw=1.6))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    # Lagre til output-mappen (figurer kopieres senere)
    draw_method(OUTPUT_DIR / 'mcr_method.png')


if __name__ == '__main__':
    main()
