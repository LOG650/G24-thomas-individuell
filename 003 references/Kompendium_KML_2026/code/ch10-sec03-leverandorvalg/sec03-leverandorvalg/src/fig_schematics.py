"""
Schematiske figurer for AHP + TOPSIS-eksempelet
===============================================
Produserer:

- ahp_hierarki.png     : AHP-hierarki (mål -> kriterier -> alternativer)
- ahp_method.png       : prosessdiagram for multikriterieanalysen

Bruker plain matplotlib uten eksternt data.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Farger fra bokens standard-skjema
COLOR_PRIMARY   = '#1F6587'
COLOR_SECONDARY = '#307453'
COLOR_ACCENT    = '#5A2C77'
COLOR_S1FILL    = '#8CC8E5'
COLOR_S2FILL    = '#97D4B7'
COLOR_S3FILL    = '#F6BA7C'
COLOR_S4FILL    = '#BD94D7'
COLOR_S5FILL    = '#ED9F9E'
COLOR_INK       = '#1F2933'


def box(ax, x, y, w, h, text, facecolor, edgecolor=COLOR_INK,
        fontsize=10, fontweight='bold', textcolor=COLOR_INK):
    patch = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.05",
        linewidth=1.2, edgecolor=edgecolor, facecolor=facecolor,
    )
    ax.add_patch(patch)
    ax.text(x, y, text, ha='center', va='center',
            fontsize=fontsize, fontweight=fontweight, color=textcolor)


def connect(ax, x1, y1, x2, y2, color=COLOR_INK, lw=1.0):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, zorder=0)


def plot_hierarki(output_path: Path) -> None:
    """AHP-hierarki med mål -> kriterier -> alternativer."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis('off')

    # Nivå 1: Mål
    box(ax, 5.0, 5.2, 3.2, 0.7,
        'Mål: Velg beste leverandør', COLOR_S4FILL, fontsize=12)

    # Nivå 2: Kriterier
    crit = ['Pris', 'Kvalitet', 'Leveringstid',
            'Fleksibilitet', 'Bærekraft']
    cfills = [COLOR_S1FILL, COLOR_S2FILL, COLOR_S3FILL,
              COLOR_S4FILL, COLOR_S5FILL]
    xs_c = np.linspace(1.0, 9.0, 5)
    for x, c, fc in zip(xs_c, crit, cfills):
        box(ax, x, 3.3, 1.5, 0.55, c, fc, fontsize=10)
        connect(ax, 5.0, 4.85, x, 3.57)

    # Nivå 3: Alternativer
    alts = ['Alfa', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta']
    xs_a = np.linspace(0.8, 9.2, 6)
    for x, a in zip(xs_a, alts):
        box(ax, x, 1.2, 1.15, 0.5, a, '#F4F7FB',
            edgecolor=COLOR_PRIMARY, fontsize=10)
        # Kobling til hvert kriterium (tynn, grå)
        for xc in xs_c:
            connect(ax, xc, 3.03, x, 1.45, color='#CBD5E1', lw=0.5)

    # Nivåbeskrivelser
    ax.text(0.1, 5.2, 'Nivå 1', fontsize=10, fontweight='bold',
            color=COLOR_PRIMARY, va='center')
    ax.text(0.1, 3.3, 'Nivå 2', fontsize=10, fontweight='bold',
            color=COLOR_PRIMARY, va='center')
    ax.text(0.1, 1.2, 'Nivå 3', fontsize=10, fontweight='bold',
            color=COLOR_PRIMARY, va='center')

    ax.set_title('AHP-hierarki: mål, kriterier og leverandøralternativer',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_method(output_path: Path) -> None:
    """Prosessdiagram for AHP + TOPSIS (6 steg)."""
    steps = [
        ('Steg 1', 'Datainnsamling'),
        ('Steg 2', 'AHP-vekter\n(CI/CR)'),
        ('Steg 3', 'TOPSIS:\nA+, A-, d+, d-'),
        ('Steg 4', 'Rangering\n$C_i$'),
        ('Steg 5', 'Sensitivitet'),
        ('Steg 6', 'Anbefaling'),
    ]
    fills = [COLOR_S1FILL, COLOR_S2FILL, COLOR_S3FILL,
             COLOR_S4FILL, COLOR_S5FILL, COLOR_S2FILL]

    fig, ax = plt.subplots(figsize=(12, 3.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.axis('off')

    xs = np.linspace(1.0, 11.0, len(steps))
    for i, (x, (label, txt), fc) in enumerate(zip(xs, steps, fills)):
        box(ax, x, 1.5, 1.65, 1.3,
            f"{label}\n\n{txt}", fc, fontsize=10)
        if i < len(steps) - 1:
            ax.annotate(
                '', xy=(xs[i + 1] - 0.80, 1.5), xytext=(x + 0.83, 1.5),
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLOR_INK),
            )

    ax.set_title('Prosess: AHP + TOPSIS for leverandørvalg',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("SCHEMATISKE FIGURER (hierarki + metode)")
    print(f"{'='*60}")

    plot_hierarki(OUTPUT_DIR / 'ahp_hierarki.png')
    plot_method(OUTPUT_DIR / 'ahp_method.png')


if __name__ == '__main__':
    main()
