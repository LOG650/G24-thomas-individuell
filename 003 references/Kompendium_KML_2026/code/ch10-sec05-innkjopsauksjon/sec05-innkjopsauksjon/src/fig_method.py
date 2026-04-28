"""
Prosessfigur for WDP-eksempelet
===============================
Seks-stegs arbeidsflyt fra datainnsamling til sensitivitet.
"""

from pathlib import Path

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

C_TEXT = '#1F2933'
C_BOX_FILL = '#8CC8E5'
C_BOX_EDGE = '#1F6587'
C_BOX_FILL2 = '#97D4B7'
C_BOX_EDGE2 = '#307453'
C_ARROW = '#556270'
C_ACCENT = '#5A2C77'

STEPS = [
    ('Steg 1', 'Datainnsamling', 'Bud fra leverandorer:\nenkeltbud + bundle-bud'),
    ('Steg 2', 'Naiv tildeling', 'Laveste enhetspris per\nkategori; sammenligningsgrunnlag'),
    ('Steg 3', 'MIP-formulering', r'WDP: $\min \sum p_b x_b$ s.t.' + '\ndekning + bundle-XOR'),
    ('Steg 4', 'MIP-loesning', 'PuLP + CBC;\nbesparelse vs. naiv'),
    ('Steg 5', 'Diversifisering', r'Skranke: maks $\alpha$ av ' + '\nkontraktverdi per leverandoer'),
    ('Steg 6', 'Sensitivitet', 'Scenarier: leverandoer\ntrekker seg / nytt bud'),
]


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    fig, ax = plt.subplots(figsize=(14.0, 3.2))

    n = len(STEPS)
    box_w = 1.95
    box_h = 1.7
    gap = 0.55

    for i, (tag, title, body) in enumerate(STEPS):
        x = i * (box_w + gap)
        edge = C_BOX_EDGE if i < 3 else C_BOX_EDGE2
        fill = C_BOX_FILL if i < 3 else C_BOX_FILL2
        box = mpatches.FancyBboxPatch(
            (x, 0), box_w, box_h,
            boxstyle='round,pad=0.05,rounding_size=0.1',
            linewidth=1.5, edgecolor=edge, facecolor=fill)
        ax.add_patch(box)

        ax.text(x + box_w / 2, box_h - 0.22, tag,
                ha='center', va='top', fontsize=11, fontweight='bold',
                color=edge)
        ax.text(x + box_w / 2, box_h - 0.58, title,
                ha='center', va='top', fontsize=11, fontweight='bold',
                color=C_TEXT)
        ax.text(x + box_w / 2, box_h - 0.95, body,
                ha='center', va='top', fontsize=9, color=C_TEXT)

        if i < n - 1:
            x_end = x + box_w
            x_next = x_end + gap
            ax.annotate('', xy=(x_next, box_h / 2), xytext=(x_end, box_h / 2),
                        arrowprops=dict(arrowstyle='->', color=C_ARROW,
                                        lw=1.6))

    ax.set_xlim(-0.2, n * (box_w + gap))
    ax.set_ylim(-0.2, box_h + 0.25)
    ax.set_aspect('equal')
    ax.axis('off')
    plt.tight_layout()
    out = OUTPUT_DIR / 'wdp_method.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {out}")


if __name__ == '__main__':
    main()
