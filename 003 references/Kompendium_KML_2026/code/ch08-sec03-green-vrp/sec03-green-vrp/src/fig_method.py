"""
Illustrer seks-stegs prosessen for Green VRP som et flytdiagram.

Saves directly to the LaTeX figures folder via OUTPUT_DIR.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from matplotlib.patches import FancyArrowPatch

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def draw_box(ax, x, y, w, h, title, body, color_fill, color_edge):
    rect = FancyBboxPatch((x, y), w, h,
                          boxstyle='round,pad=0.02,rounding_size=0.08',
                          linewidth=1.2,
                          edgecolor=color_edge,
                          facecolor=color_fill,
                          zorder=2)
    ax.add_patch(rect)
    ax.text(x + w / 2, y + h - 0.22, title,
            ha='center', va='top', fontsize=10.5, fontweight='bold',
            color='#1F2933')
    ax.text(x + w / 2, y + h / 2 - 0.10, body,
            ha='center', va='center', fontsize=9, color='#1F2933')


def draw_arrow(ax, x1, y1, x2, y2, color='#556270'):
    arrow = FancyArrowPatch((x1, y1), (x2, y2),
                             arrowstyle='-|>', mutation_scale=15,
                             linewidth=1.3, color=color, zorder=1)
    ax.add_patch(arrow)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 4.8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.6)
    ax.axis('off')

    steps = [
        (1, 'Steg 1', 'Datainnsamling\n(depot + 25 kunder, utslippsfaktorer)',
         '#8CC8E5', '#1F6587'),
        (2, 'Steg 2', 'Distanse-baseline\n(klassisk Clarke-Wright)',
         '#97D4B7', '#307453'),
        (3, 'Steg 3', 'Utslippsmodell\n$e(w) = \\alpha + \\beta w$',
         '#BD94D7', '#5A2C77'),
        (4, 'Steg 4', 'Green Clarke-Wright\n(savings paa CO$_2$)',
         '#F6BA7C', '#9C540B'),
        (5, 'Steg 5', '2-opt paa utslipp\n(lokal forbedring per rute)',
         '#ED9F9E', '#961D1C'),
        (6, 'Steg 6', 'Pareto-front\n(kostnad vs CO$_2$)',
         '#8CC8E5', '#1F6587'),
    ]

    box_w = 1.75
    box_h = 1.55
    gap = 0.25

    positions_row1 = [(0.2 + i * (box_w + gap), 2.6) for i in range(3)]
    positions_row2 = [(0.2 + i * (box_w + gap), 0.5) for i in range(3)]
    positions_row2 = list(reversed(positions_row2))

    for i, (num, title, body, fill, edge) in enumerate(steps):
        if i < 3:
            x, y = positions_row1[i]
        else:
            x, y = positions_row2[i - 3]
        draw_box(ax, x, y, box_w, box_h, f'{title}', body, fill, edge)

    # Piler: 1 -> 2 -> 3 (row1), 3 -> 6 (ned), 6 -> 5 -> 4 (row2 reversert)
    def center(pos):
        return pos[0] + box_w / 2, pos[1] + box_h / 2

    right_mid = lambda p: (p[0] + box_w, p[1] + box_h / 2)
    left_mid = lambda p: (p[0], p[1] + box_h / 2)
    bot_mid = lambda p: (p[0] + box_w / 2, p[1])
    top_mid = lambda p: (p[0] + box_w / 2, p[1] + box_h)

    # 1 -> 2
    draw_arrow(ax, *right_mid(positions_row1[0]), *left_mid(positions_row1[1]))
    # 2 -> 3
    draw_arrow(ax, *right_mid(positions_row1[1]), *left_mid(positions_row1[2]))
    # 3 -> 4 (ned, positions_row2 reversert: [0]=steg4 rightmost, [1]=steg5, [2]=steg6)
    draw_arrow(ax, *bot_mid(positions_row1[2]), *top_mid(positions_row2[0]))
    # 4 -> 5
    draw_arrow(ax, *left_mid(positions_row2[0]), *right_mid(positions_row2[1]))
    # 5 -> 6
    draw_arrow(ax, *left_mid(positions_row2[1]), *right_mid(positions_row2[2]))

    out = OUTPUT_DIR / 'gvrp_method.png'
    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {out}')


if __name__ == '__main__':
    main()
