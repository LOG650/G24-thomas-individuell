"""
Steg 3: Cut-off-optimering basert på tilstandsscore
====================================================
Finner den heuristikken som maksimerer forventet samlet verdi når
beslutningen skal baseres alene på tilstandsscore c in {1,...,5}.

Siden c har kun fem verdier, kan vi enumerere alle mulige regler
(4^5 = 1024 kombinasjoner) og velge den med høyest forventet totalverdi.
Resultatet er en tabell som viser valgt handling per tilstandsscore.
"""

import itertools
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_verdimodell import ACTIONS

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def best_policy_by_condition(df: pd.DataFrame) -> dict:
    """For hver tilstandsscore, velg handling med høyest gjennomsnittlig EV."""
    policy = {}
    for c in range(1, 6):
        subset = df[df['condition'] == c]
        if len(subset) == 0:
            policy[c] = 'dispose'
            continue
        means = {a: subset[f'ev_{a}'].mean() for a in ACTIONS}
        policy[c] = max(means, key=means.get)
    return policy


def evaluate_policy(df: pd.DataFrame, policy: dict) -> float:
    """Sum av forventet verdi når policy (condition -> action) anvendes (vektorisert)."""
    # Vektorisert: for hver enhet, velg EV-kolonnen som matcher policy[condition]
    total = 0.0
    for c in range(1, 6):
        mask = df['condition'] == c
        a = policy[c]
        total += float(df.loc[mask, f'ev_{a}'].sum())
    return total


def enumerate_all_policies(df: pd.DataFrame) -> pd.DataFrame:
    """Evaluer alle 4^5 = 1024 mulige politikker og returner resultatene."""
    # Preaggreger: sum av ev_{a} over alle enheter med hver tilstand c
    agg = {
        c: {a: float(df.loc[df['condition'] == c, f'ev_{a}'].sum()) for a in ACTIONS}
        for c in range(1, 6)
    }
    rows = []
    for combo in itertools.product(ACTIONS, repeat=5):
        policy = {c: combo[c - 1] for c in range(1, 6)}
        total = sum(agg[c][policy[c]] for c in range(1, 6))
        rows.append({
            **{f'c{c}': policy[c] for c in range(1, 6)},
            'total_ev': total,
        })
    return pd.DataFrame(rows).sort_values('total_ev', ascending=False).reset_index(drop=True)


def plot_cutoff_chart(policy: dict, df: pd.DataFrame, output_path: Path) -> None:
    """Visualiser policy som et fargekart per tilstandsscore."""
    fig, ax = plt.subplots(figsize=(9, 4.5))

    palette = {
        'repair':    '#8CC8E5',
        'refurbish': '#97D4B7',
        'recycle':   '#F6BA7C',
        'dispose':   '#ED9F9E',
    }
    edge = {
        'repair':    '#1F6587',
        'refurbish': '#307453',
        'recycle':   '#9C540B',
        'dispose':   '#961D1C',
    }

    x = np.arange(1, 6)
    counts = [int((df['condition'] == c).sum()) for c in x]
    for c, cnt in zip(x, counts):
        a = policy[c]
        ax.bar(
            c, cnt, width=0.7,
            color=palette[a], edgecolor=edge[a], linewidth=1.4,
        )
        ax.text(
            c, cnt + max(counts) * 0.02, a,
            ha='center', va='bottom', fontsize=11, fontweight='bold',
            color=edge[a],
        )

    ax.set_xlabel('Tilstandsscore $c$', fontsize=14)
    ax.set_ylabel('Antall enheter', fontsize=14)
    ax.set_xticks(x)
    ax.set_ylim(0, max(counts) * 1.18)
    ax.set_title('Optimal cut-off-politikk: handling per tilstandsscore',
                 fontsize=12, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 3: CUT-OFF-OPTIMERING")
    print(f"{'='*60}")

    df = pd.read_csv(OUTPUT_DIR / 'units_with_values.csv')

    # Beregn beste handling per tilstand via gjennomsnitt
    policy = best_policy_by_condition(df)
    print("\n--- Optimal policy ---")
    for c in range(1, 6):
        print(f"  c = {c}: {policy[c]}")

    total = evaluate_policy(df, policy)
    print(f"\nTotal forventet verdi: {total:,.0f} NOK")

    # Enumerer alle og vis topp-10
    all_policies = enumerate_all_policies(df)
    print("\nTopp-10 politikker etter total EV:")
    print(all_policies.head(10).to_string(index=False))

    # Lagre
    summary = {
        'policy': {str(c): a for c, a in policy.items()},
        'total_ev': round(total, 2),
        'antall_politikker_evaluert': int(len(all_policies)),
        'verste_policy_ev': round(float(all_policies['total_ev'].min()), 2),
        'beste_policy_ev': round(float(all_policies['total_ev'].max()), 2),
    }
    with open(OUTPUT_DIR / 'step03_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Lagre policy i egen JSON så senere steg kan bruke den
    with open(OUTPUT_DIR / 'cutoff_policy.json', 'w', encoding='utf-8') as f:
        json.dump({str(c): a for c, a in policy.items()}, f, indent=2, ensure_ascii=False)

    plot_cutoff_chart(policy, df, OUTPUT_DIR / 'disp_cutoff_chart.png')


if __name__ == '__main__':
    main()
