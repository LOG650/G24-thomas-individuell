"""
Steg 2: Modellformulering
=========================
Spesifiserer LP-modellen eksplisitt (beslutningsvariabler,
objekt, skranker). Skriver en tekstlig oppsummering til output/ og
lager en enkel metodefigur for Prosess-seksjonen.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

from step01_datainnsamling import parameters

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


MODEL_TEXT = r"""
Aggregert produksjonsplanlegging (LP)
-------------------------------------
Beslutningsvariabler (for t = 1, ..., T):
  P_t  = ordinaer produksjon i maaned t         [baater]
  O_t  = overtidsproduksjon i maaned t          [baater]
  I_t  = lagerbeholdning ved slutten av mnd t   [baater]
  H_t  = antall ansatte som rekrutteres i mnd t [ansatte]
  F_t  = antall ansatte som sies opp i mnd t    [ansatte]
  W_t  = arbeidsstyrke ved slutten av mnd t     [ansatte]

Objekt:
  min  sum_t ( c_P * P_t + c_O * O_t + c_I * I_t
             + c_H * H_t + c_F * F_t )

Skranker:
  (1) Lagerbalanse:     I_t = I_{t-1} + P_t + O_t - D_t        (t = 1..T)
  (2) Arbeidsbalanse:   W_t = W_{t-1} + H_t - F_t              (t = 1..T)
  (3) Produktivitet:    P_t <= alpha * W_t                     (t = 1..T)
  (4) Overtidskapasit:  O_t <= O_max                           (t = 1..T)
  (5) Ikke-negativ:     P_t, O_t, I_t, H_t, F_t, W_t >= 0      (t = 1..T)

Startbetingelser: I_0, W_0 er gitt fra data.
"""


def plot_method(output_path: Path) -> None:
    """Enkel horisontal metodefigur med de seks stegene."""
    fig, ax = plt.subplots(figsize=(11, 3.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis('off')

    steps = [
        ('Steg 1', 'Datainnsamling'),
        ('Steg 2', 'Modell-\nformulering'),
        ('Steg 3', 'LP-loesning\n(PuLP / linprog)'),
        ('Steg 4', 'Sensitivitet\n(skyggepriser)'),
        ('Steg 5', 'Validering\n(stresstest)'),
        ('Steg 6', 'Anbefaling'),
    ]

    fill_colors = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E', '#8CC8E5']
    stroke_colors = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C', '#1F6587']

    box_w = 1.6
    box_h = 1.6
    gap = 0.35
    x0 = 0.25
    for i, (head, body) in enumerate(steps):
        x = x0 + i * (box_w + gap)
        box = FancyBboxPatch((x, 1.1), box_w, box_h,
                             boxstyle='round,pad=0.02,rounding_size=0.12',
                             linewidth=1.4,
                             edgecolor=stroke_colors[i],
                             facecolor=fill_colors[i])
        ax.add_patch(box)
        ax.text(x + box_w / 2, 1.1 + box_h - 0.45, head,
                ha='center', va='center',
                fontsize=11, fontweight='bold', color=stroke_colors[i])
        ax.text(x + box_w / 2, 1.1 + box_h / 2 - 0.25, body,
                ha='center', va='center',
                fontsize=9, color='#1F2933')
        # Pil til neste boks
        if i < len(steps) - 1:
            arrow = FancyArrowPatch(
                (x + box_w, 1.1 + box_h / 2),
                (x + box_w + gap, 1.1 + box_h / 2),
                arrowstyle='-|>', mutation_scale=14,
                linewidth=1.3, color='#556270')
            ax.add_patch(arrow)

    ax.text(6.0, 3.6, 'Aggregert produksjonsplanlegging -- LP-prosess',
            ha='center', va='center', fontsize=12, fontweight='bold',
            color='#1F2933')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: MODELLFORMULERING")
    print("=" * 60)

    params = parameters()

    print(MODEL_TEXT)
    print(f"Antall beslutningsvariabler: 6 * T = {6 * params['T']}")
    print(f"Antall likhetsskranker:      2 * T = {2 * params['T']}"
          " (lager- og arbeidsbalanse)")
    print(f"Antall uliketsskranker:      2 * T = {2 * params['T']}"
          " (produktivitet + overtidsmaks)")

    model_path = OUTPUT_DIR / 'step02_model.txt'
    with open(model_path, 'w', encoding='utf-8') as f:
        f.write(MODEL_TEXT)
    print(f"\nModelltekst lagret: {model_path}")

    stats = {
        'n_variabler': 6 * params['T'],
        'n_likhetsskranker': 2 * params['T'],
        'n_uliketsskranker': 2 * params['T'],
        'horisont': params['T'],
    }
    with open(OUTPUT_DIR / 'step02_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)
    print(f"Statistikk lagret: {OUTPUT_DIR / 'step02_stats.json'}")

    plot_method(OUTPUT_DIR / 'agglp_method.png')


if __name__ == '__main__':
    main()
