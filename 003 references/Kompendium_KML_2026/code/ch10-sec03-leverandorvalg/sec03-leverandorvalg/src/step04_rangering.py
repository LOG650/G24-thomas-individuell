"""
Steg 4: Rangering av leverandører
=================================
Sammenstill TOPSIS-skår C_i og rangér leverandørene.
Genererer oversiktsfigur med C-skår per leverandør og en
sammenligning av faktiske ytelsesverdier for topp 3.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    CRITERIA,
    CRITERION_TYPES,
    SUPPLIERS,
    get_pairwise_dataframe,
    get_performance_dataframe,
)
from step02_ahp_vekter import ahp_eigenvector_weights
from step03_topsis import topsis_scores

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def rank_suppliers(suppliers: list[str], C: np.ndarray) -> list[dict]:
    """Sorter leverandører etter fallende C_i."""
    order = np.argsort(-C)
    ranked = []
    for rank, idx in enumerate(order, start=1):
        ranked.append({
            'rank': int(rank),
            'supplier': suppliers[idx],
            'C': float(round(C[idx], 6)),
        })
    return ranked


def plot_ranking(ranked: list[dict], output_path: Path) -> None:
    """Horisontalt søylediagram med C_i sortert."""
    fig, ax = plt.subplots(figsize=(9, 5))
    names = [r['supplier'] for r in ranked][::-1]  # topp nederst -> øverst
    scores = [r['C'] for r in ranked][::-1]

    # Gradient: best (topp) = mørkeste blå
    cmap = plt.get_cmap('Blues')
    colors = [cmap(0.35 + 0.55 * i / max(1, len(ranked) - 1))
              for i in range(len(ranked))]

    bars = ax.barh(names, scores, color=colors, edgecolor='black', linewidth=0.6)
    for bar, s in zip(bars, scores):
        ax.text(s + 0.005, bar.get_y() + bar.get_height() / 2,
                f'{s:.3f}', va='center', fontsize=10)

    ax.set_xlim(0, max(scores) * 1.18)
    ax.set_xlabel('Nærhetsskår $C_i$', fontsize=12)
    ax.set_title('TOPSIS-rangering av leverandører',
                 fontsize=12, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    ax.tick_params(axis='both', labelsize=11)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 4: RANGERING")
    print(f"{'='*60}")

    perf = get_performance_dataframe()
    X = perf.values.astype(float)
    ctypes = [CRITERION_TYPES[c] for c in CRITERIA]
    A_pair = get_pairwise_dataframe().values
    weights, _ = ahp_eigenvector_weights(A_pair)

    topsis = topsis_scores(X, weights, ctypes)
    C = topsis['C']
    d_plus = topsis['d_plus']
    d_minus = topsis['d_minus']

    ranked = rank_suppliers(SUPPLIERS, C)
    print("\n--- Rangering ---")
    for r in ranked:
        print(f"  #{r['rank']}  {r['supplier']:<8s}  C = {r['C']:.4f}")

    # Rangeringstabell med alle mellomresultater
    table_rows = []
    for r in ranked:
        idx = SUPPLIERS.index(r['supplier'])
        table_rows.append({
            'rank': r['rank'],
            'supplier': r['supplier'],
            'd_plus': float(round(d_plus[idx], 6)),
            'd_minus': float(round(d_minus[idx], 6)),
            'C': float(round(C[idx], 6)),
        })

    results = {
        'ranking': table_rows,
        'weights': [float(round(w, 6)) for w in weights.tolist()],
        'criteria': CRITERIA,
    }
    with open(OUTPUT_DIR / 'step04_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step04_results.json'}")

    # Figur
    plot_ranking(ranked, OUTPUT_DIR / 'ahp_rangering.png')


if __name__ == '__main__':
    main()
