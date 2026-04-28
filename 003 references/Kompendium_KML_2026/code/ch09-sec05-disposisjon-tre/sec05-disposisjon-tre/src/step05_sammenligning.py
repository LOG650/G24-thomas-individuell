"""
Steg 5: Sammenligning av politikker
=====================================
Vi sammenligner tre politikker på datasettet:
  1. Naiv: alltid resirkulere
  2. Heuristikk: cut-off per tilstandsscore (steg 3)
  3. Lært: beslutningstre med flere features (steg 4)

Vi rapporterer samlet forventet verdi, andel repair/refurbish/recycle/dispose
og marginal gevinst i forhold til naiv baseline.
"""

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_verdimodell import ACTIONS

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def eval_naiv(df: pd.DataFrame, fixed_action: str = 'recycle') -> dict:
    """Alltid én handling."""
    total = float(df[f'ev_{fixed_action}'].sum())
    shares = {a: (1.0 if a == fixed_action else 0.0) for a in ACTIONS}
    return {'name': f'naiv-{fixed_action}', 'total_ev': total, 'shares': shares}


def eval_cutoff(df: pd.DataFrame, policy: dict) -> dict:
    """Cut-off-politikk condition -> handling (vektorisert)."""
    total = 0.0
    action_counts = {a: 0 for a in ACTIONS}
    for c in range(1, 6):
        mask = df['condition'] == c
        a = policy[c]
        total += float(df.loc[mask, f'ev_{a}'].sum())
        action_counts[a] += int(mask.sum())
    n = len(df)
    shares = {a: action_counts[a] / n for a in ACTIONS}
    return {'name': 'cut-off', 'total_ev': total, 'shares': shares}


def eval_tree(df: pd.DataFrame, clf, feature_names: list) -> dict:
    """Beslutningstre med full feature-vektor (vektorisert)."""
    from step04_beslutningstre import build_features
    X = build_features(df)[feature_names]
    preds = clf.predict(X)

    total = 0.0
    action_counts = {a: 0 for a in ACTIONS}
    ev_cols = {a: df[f'ev_{a}'].to_numpy() for a in ACTIONS}
    for a in ACTIONS:
        mask = preds == a
        total += float(ev_cols[a][mask].sum())
        action_counts[a] = int(mask.sum())
    n = len(df)
    shares = {a: action_counts[a] / n for a in ACTIONS}
    return {'name': 'tre', 'total_ev': total, 'shares': shares}


def eval_oracle(df: pd.DataFrame) -> dict:
    """Oracle: alltid velg handling med maksimal EV per enhet."""
    total = float(df['optimal_value'].sum())
    action_counts = df['optimal_action'].value_counts()
    n = len(df)
    shares = {a: int(action_counts.get(a, 0)) / n for a in ACTIONS}
    return {'name': 'oracle', 'total_ev': total, 'shares': shares}


def plot_profit_compare(results: list, output_path: Path) -> None:
    """Stolpediagram som sammenligner total EV per politikk."""
    fig, ax = plt.subplots(figsize=(9, 5))

    names = [r['name'] for r in results]
    totals = [r['total_ev'] / 1000.0 for r in results]  # kNOK

    colors = ['#ED9F9E', '#F6BA7C', '#97D4B7', '#8CC8E5']
    edge = ['#961D1C', '#9C540B', '#307453', '#1F6587']

    bars = ax.bar(names, totals, color=colors, edgecolor=edge, linewidth=1.4)
    for bar, val in zip(bars, totals):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(totals) * 0.02,
            f'{val:,.1f}'.replace(',', ' ').replace('.', ','),
            ha='center', va='bottom', fontsize=11, fontweight='bold',
        )

    ax.set_ylabel('Total forventet verdi (kNOK)', fontsize=13)
    ax.set_title('Sammenligning: naiv vs. cut-off vs. tre vs. oracle',
                 fontsize=12, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='both', labelsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 5: SAMMENLIGNING AV POLITIKKER")
    print(f"{'='*60}")

    df = pd.read_csv(OUTPUT_DIR / 'units_with_values.csv')

    # Last inn cut-off-politikk
    with open(OUTPUT_DIR / 'cutoff_policy.json', 'r', encoding='utf-8') as f:
        cutoff_policy_raw = json.load(f)
    cutoff_policy = {int(c): a for c, a in cutoff_policy_raw.items()}

    # Last inn tre
    with open(OUTPUT_DIR / 'decision_tree.pkl', 'rb') as f:
        tree_data = pickle.load(f)
    clf = tree_data['clf']
    feature_names = tree_data['feature_names']

    # Evaluer alle
    results = [
        eval_naiv(df, 'recycle'),
        eval_cutoff(df, cutoff_policy),
        eval_tree(df, clf, feature_names),
        eval_oracle(df),
    ]

    # Rapportering
    baseline = results[0]['total_ev']
    print(f"\n{'Policy':<15s} {'Total EV (NOK)':>16s} {'Delta vs naiv':>16s} {'% av oracle':>14s}")
    print('-' * 62)
    oracle_total = results[-1]['total_ev']
    for r in results:
        delta = r['total_ev'] - baseline
        pct = r['total_ev'] / oracle_total * 100
        print(f"  {r['name']:<13s} {r['total_ev']:>16,.0f} {delta:>14,.0f} {pct:>13.1f}%")

    print("\n--- Handlings-fordelinger ---")
    for r in results:
        share_str = ', '.join(
            f"{a}={r['shares'][a]:.2f}" for a in ACTIONS
        )
        print(f"  {r['name']:<13s}: {share_str}")

    # Lagre resultater
    summary = {
        'results': [
            {
                'name': r['name'],
                'total_ev': round(r['total_ev'], 2),
                'shares': {a: round(r['shares'][a], 4) for a in ACTIONS},
                'delta_vs_naiv': round(r['total_ev'] - baseline, 2),
                'pct_of_oracle': round(r['total_ev'] / oracle_total * 100, 2),
            }
            for r in results
        ],
    }
    with open(OUTPUT_DIR / 'step05_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_profit_compare(results, OUTPUT_DIR / 'disp_profit_compare.png')


if __name__ == '__main__':
    main()
