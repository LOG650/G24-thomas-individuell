"""
Steg 6: Anbefalt disposisjonspolitikk + metodefigur
=====================================================
Oppsummerer anbefalt politikk som en enkel tabell med regler avledet fra
beslutningstreet og lager en illustrasjon av prosessen (method-figuren).
"""

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from step02_verdimodell import ACTIONS

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def plot_method_diagram(output_path: Path) -> None:
    """Metodefigur: seks stegs i disposisjonsanalyse."""
    fig, ax = plt.subplots(figsize=(12, 4.8))

    steps = [
        ('1. Datainnsamling',       '#8CC8E5', '#1F6587'),
        ('2. Forventet verdi',      '#97D4B7', '#307453'),
        ('3. Cut-off-\noptimering', '#F6BA7C', '#9C540B'),
        ('4. Beslutningstre',       '#BD94D7', '#5A2C77'),
        ('5. Sammenligning',        '#ED9F9E', '#961D1C'),
        ('6. Anbefaling',           '#8CC8E5', '#1F6587'),
    ]

    n = len(steps)
    box_w = 1.5
    box_h = 1.1
    gap = 0.4

    for i, (label, fill, edge) in enumerate(steps):
        x = i * (box_w + gap)
        rect = mpatches.FancyBboxPatch(
            (x, 0.5), box_w, box_h,
            boxstyle='round,pad=0.05',
            facecolor=fill, edgecolor=edge, linewidth=2,
        )
        ax.add_patch(rect)
        ax.text(
            x + box_w / 2, 0.5 + box_h / 2, label,
            ha='center', va='center', fontsize=10, fontweight='bold',
            color='#1F2933',
        )

        # Pil til neste
        if i < n - 1:
            arrow_x1 = x + box_w + 0.03
            arrow_x2 = x + box_w + gap - 0.03
            ax.annotate(
                '',
                xy=(arrow_x2, 0.5 + box_h / 2),
                xytext=(arrow_x1, 0.5 + box_h / 2),
                arrowprops=dict(arrowstyle='->', color='#556270', lw=1.6),
            )

    total_w = n * box_w + (n - 1) * gap
    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(0.2, 2.0)
    ax.axis('off')
    ax.set_title(
        'Disposisjonsanalyse: fra returdata til handlingsregler',
        fontsize=13, fontweight='bold', pad=6,
    )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def build_rules_table(df: pd.DataFrame, clf, feature_names: list) -> pd.DataFrame:
    """Lag en enkel regel-tabell: gjennomsnittlig prediksjon per tilstand."""
    from step04_beslutningstre import build_features
    X = build_features(df)[feature_names]
    preds = clf.predict(X)
    df2 = df.copy()
    df2['pred_action'] = preds

    rows = []
    for c in range(1, 6):
        subset = df2[df2['condition'] == c]
        n = len(subset)
        if n == 0:
            continue
        action_counts = subset['pred_action'].value_counts()
        dominant = action_counts.idxmax()
        share = action_counts.max() / n
        rows.append({
            'condition': c,
            'n': n,
            'dominant_action': dominant,
            'dominant_share': round(float(share), 3),
            'counts': {a: int(action_counts.get(a, 0)) for a in ACTIONS},
        })
    return pd.DataFrame(rows)


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 6: ANBEFALING")
    print(f"{'='*60}")

    df = pd.read_csv(OUTPUT_DIR / 'units_with_values.csv')

    with open(OUTPUT_DIR / 'decision_tree.pkl', 'rb') as f:
        tree_data = pickle.load(f)
    clf = tree_data['clf']
    feature_names = tree_data['feature_names']

    rules = build_rules_table(df, clf, feature_names)
    print("\n--- Regel-tabell (dominant handling per tilstand) ---")
    print(rules.to_string(index=False))

    # Last inn resultater fra step05 for oppsummering
    with open(OUTPUT_DIR / 'step05_summary.json', 'r', encoding='utf-8') as f:
        step05 = json.load(f)

    best_tree = next(r for r in step05['results'] if r['name'] == 'tre')
    oracle = next(r for r in step05['results'] if r['name'] == 'oracle')
    naiv = next(r for r in step05['results'] if r['name'] == 'naiv-recycle')

    print("\n--- Nøkkeltall ---")
    print(f"  Naiv (alltid resirkulere): {naiv['total_ev']:,.0f} NOK")
    print(f"  Lært tre:                  {best_tree['total_ev']:,.0f} NOK")
    print(f"  Oracle:                    {oracle['total_ev']:,.0f} NOK")
    print(f"  Tre andel av oracle:       {best_tree['pct_of_oracle']:.1f} %")

    summary = {
        'rules': rules.to_dict(orient='records'),
        'headline': {
            'naiv_ev': naiv['total_ev'],
            'tre_ev': best_tree['total_ev'],
            'oracle_ev': oracle['total_ev'],
            'uplift_tre_vs_naiv': round(best_tree['total_ev'] - naiv['total_ev'], 2),
            'pct_of_oracle': best_tree['pct_of_oracle'],
        },
    }
    with open(OUTPUT_DIR / 'step06_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Lag metodefigur
    plot_method_diagram(OUTPUT_DIR / 'disp_method.png')


if __name__ == '__main__':
    main()
