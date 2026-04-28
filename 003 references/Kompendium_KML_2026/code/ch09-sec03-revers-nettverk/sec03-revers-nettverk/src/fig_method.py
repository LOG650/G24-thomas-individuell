"""
Metodefigur: 6-stegs arbeidsflyt for reverse nettverksdesign
============================================================
Genererer en enkel flytdiagramfigur som viser de seks stegene i
eksempelet, i samme stil som uflp_method.png.

Lagres rett i latex-figures-katalogen.
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT_FIG = (Path(__file__).parent.parent.parent.parent.parent
           / 'latex' / '200-bodymatter' / 'part02-omrader'
           / 'ch09-returlogistikk' / 'figures' / 'revnet_method.png')


STEPS = [
    {
        'title': 'Steg 1:\nDatainnsamling',
        'icon': 'pin',
        'sub': 'Kunder, IS\nog GV',
        'fill': '#8CC8E5', 'stroke': '#1F6587',
    },
    {
        'title': 'Steg 2:\nAvstandsmatrise',
        'icon': 'grid',
        'sub': 'Haversine\n$c_{ij}, c_{ik}$',
        'fill': '#97D4B7', 'stroke': '#307453',
    },
    {
        'title': 'Steg 3: MIP-\nformulering',
        'icon': 'sigma',
        'sub': 'Flertrinns-\nmodell',
        'fill': '#F6BA7C', 'stroke': '#9C540B',
    },
    {
        'title': 'Steg 4:\nMIP-losning',
        'icon': 'check',
        'sub': 'PuLP og CBC',
        'fill': '#BD94D7', 'stroke': '#5A2C77',
    },
    {
        'title': 'Steg 5:\nSensitivitet',
        'icon': 'bars',
        'sub': r'$\rho, \kappa, \beta$',
        'fill': '#ED9F9E', 'stroke': '#961D1C',
    },
    {
        'title': 'Steg 6:\nAnbefaling',
        'icon': 'doc',
        'sub': 'Hvilke IS\nog GV aapnes?',
        'fill': '#8CC8E5', 'stroke': '#1F6587',
    },
]


def draw_icon(ax, kind, cx, cy, color):
    r = 0.30
    if kind == 'pin':
        ax.plot([cx], [cy + 0.05], 'o', color=color, markersize=13,
                markerfacecolor=color, markeredgecolor=color)
        ax.plot([cx, cx], [cy - 0.25, cy + 0.05], color=color, linewidth=2.0)
    elif kind == 'grid':
        for i in range(3):
            for j in range(3):
                ax.add_patch(mpatches.Rectangle(
                    (cx - 0.3 + j * 0.2, cy - 0.3 + i * 0.2),
                    0.18, 0.18, fill=False, edgecolor=color, linewidth=1.2))
    elif kind == 'sigma':
        ax.text(cx, cy, r'$\Sigma$', ha='center', va='center',
                fontsize=30, color=color, fontweight='bold')
    elif kind == 'check':
        ax.plot([cx - 0.25, cx - 0.05, cx + 0.30],
                [cy - 0.05, cy - 0.28, cy + 0.22],
                color=color, linewidth=4.0, solid_capstyle='round')
    elif kind == 'bars':
        for i, h in enumerate([0.25, 0.40, 0.18, 0.55]):
            ax.add_patch(mpatches.Rectangle(
                (cx - 0.35 + i * 0.17, cy - 0.30),
                0.13, h, facecolor=color, edgecolor=color))
    elif kind == 'doc':
        ax.add_patch(mpatches.Rectangle(
            (cx - 0.22, cy - 0.33), 0.44, 0.66,
            fill=False, edgecolor=color, linewidth=2.0))
        for yo in [0.17, 0.03, -0.11]:
            ax.plot([cx - 0.14, cx + 0.12], [cy + yo, cy + yo],
                    color=color, linewidth=1.4)


def main() -> None:
    OUT_FIG.parent.mkdir(parents=True, exist_ok=True)

    n = len(STEPS)
    box_w = 1.9
    box_h = 2.3
    gap = 0.45
    total_w = n * box_w + (n - 1) * gap
    x0 = 0.3

    fig_w = 0.6 + total_w * 0.9
    fig, ax = plt.subplots(figsize=(fig_w, 3.4))
    ax.set_xlim(0, total_w + 0.6)
    ax.set_ylim(0, box_h + 0.6)
    ax.set_aspect('equal')
    ax.axis('off')

    for i, step in enumerate(STEPS):
        bx = x0 + i * (box_w + gap)
        by = 0.3
        # Rounded box
        box = FancyBboxPatch(
            (bx, by), box_w, box_h,
            boxstyle="round,pad=0.02,rounding_size=0.18",
            facecolor=step['fill'], edgecolor=step['stroke'], linewidth=1.6)
        ax.add_patch(box)

        # Title
        ax.text(bx + box_w / 2, by + box_h - 0.32, step['title'],
                ha='center', va='top', fontsize=10, fontweight='bold',
                color=step['stroke'])

        # Icon
        draw_icon(ax, step['icon'], bx + box_w / 2, by + box_h / 2 - 0.05,
                  step['stroke'])

        # Subtitle
        ax.text(bx + box_w / 2, by + 0.22, step['sub'],
                ha='center', va='bottom', fontsize=9, color='#1F2933')

        # Arrow
        if i < n - 1:
            arr = FancyArrowPatch(
                (bx + box_w + 0.02, by + box_h / 2),
                (bx + box_w + gap - 0.02, by + box_h / 2),
                arrowstyle='->', mutation_scale=18,
                color='#556270', linewidth=1.6)
            ax.add_patch(arr)

    plt.tight_layout()
    plt.savefig(OUT_FIG, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Metodefigur lagret: {OUT_FIG}")


if __name__ == '__main__':
    main()
