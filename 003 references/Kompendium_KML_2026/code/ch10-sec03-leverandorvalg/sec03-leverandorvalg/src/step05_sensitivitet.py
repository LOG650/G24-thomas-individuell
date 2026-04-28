"""
Steg 5: Sensitivitetsanalyse
============================
Hvor robust er rangeringen mot små endringer i kriterievekter?

Strategi:
- For hvert kriterium j, endre w_j med faktor 1 +/- delta (delta = 0.20).
- Renormaliser de andre vektene slik at Sum w_j = 1.
- Kjør TOPSIS og registrer C-skår + rangering.
- Plott spider/radar-figur der hver akse er et kriterium og
  hver linje viser C_i for topp-leverandører under pertubasjonen.
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


def perturb_weights(w: np.ndarray, j: int, delta: float) -> np.ndarray:
    """Juster w_j med faktor (1 + delta) og renormaliser."""
    new_w = w.copy()
    new_w[j] = w[j] * (1 + delta)
    # Renormaliser (forble positive; delta > -1)
    new_w = new_w / new_w.sum()
    return new_w


def sensitivity_matrix(
    X: np.ndarray,
    w_base: np.ndarray,
    criterion_types: list[str],
    deltas: list[float],
) -> dict:
    """
    For hvert kriterium j og hver delta, beregn C for alle leverandører.

    Returnerer dict med to matriser av form (m_suppliers, n_criteria),
    én for hver delta.
    """
    results = {}
    for d in deltas:
        C_matrix = np.zeros((X.shape[0], X.shape[1]))
        rank_matrix = np.zeros((X.shape[0], X.shape[1]), dtype=int)
        for j in range(X.shape[1]):
            w_new = perturb_weights(w_base, j, d)
            out = topsis_scores(X, w_new, criterion_types)
            C_matrix[:, j] = out['C']
            rank_matrix[:, j] = np.argsort(-out['C']).argsort() + 1
        results[f'delta_{d:+.2f}'] = {
            'C': C_matrix,
            'rank': rank_matrix,
            'delta': float(d),
        }
    return results


def plot_sensitivity_spider(
    suppliers: list[str],
    criteria: list[str],
    baseline_C: np.ndarray,
    sens: dict,
    output_path: Path,
) -> None:
    """
    Radar/spider-plott. For hver leverandør vises baseline C_i som en sirkel,
    og to pertubasjonskurver (delta = +0.20 og -0.20).
    Vi viser kun topp-tre leverandører for lesbarhet.
    """
    # Topp-tre leverandører ut fra baseline
    top_idx = np.argsort(-baseline_C)[:3]
    n = len(criteria)
    angles = np.linspace(0, 2 * np.pi, n, endpoint=False).tolist()
    angles += angles[:1]  # lukk sløyfen

    fig, ax = plt.subplots(figsize=(8, 7), subplot_kw=dict(polar=True))

    colors = ['#1F6587', '#307453', '#5A2C77']
    for plot_i, sup_idx in enumerate(top_idx):
        base_val = baseline_C[sup_idx]
        c_plus = sens['delta_+0.20']['C'][sup_idx].tolist() + [sens['delta_+0.20']['C'][sup_idx][0]]
        c_minus = sens['delta_-0.20']['C'][sup_idx].tolist() + [sens['delta_-0.20']['C'][sup_idx][0]]
        c_base = [base_val] * (n + 1)

        color = colors[plot_i % len(colors)]
        # Baseline som stiplet sirkel
        ax.plot(angles, c_base, color=color, linestyle='--', linewidth=1.2,
                alpha=0.6)
        # Pertubasjoner
        ax.plot(angles, c_plus, color=color, linewidth=2.0,
                label=f'{suppliers[sup_idx]}')
        ax.plot(angles, c_minus, color=color, linewidth=2.0, alpha=0.55)
        ax.fill(angles, c_minus, color=color, alpha=0.08)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(criteria, fontsize=11)
    # Y-grense: litt margin
    all_vals = []
    for d in ['delta_+0.20', 'delta_-0.20']:
        all_vals.append(sens[d]['C'][top_idx].flatten())
    all_vals = np.concatenate(all_vals)
    low = float(max(0.0, all_vals.min() * 0.90))
    high = float(min(1.0, all_vals.max() * 1.05))
    ax.set_ylim(low, high)
    ax.tick_params(axis='y', labelsize=8)
    ax.set_title('Sensitivitet av $C_i$ ved $\\pm 20\\%$ endring per vekt\n'
                 '(stiplet = uperturbert; heltrukket = +/-20 %)',
                 fontsize=11, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.25, 1.05), fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 5: SENSITIVITETSANALYSE")
    print(f"{'='*60}")

    perf = get_performance_dataframe()
    X = perf.values.astype(float)
    ctypes = [CRITERION_TYPES[c] for c in CRITERIA]

    A_pair = get_pairwise_dataframe().values
    w_base, _ = ahp_eigenvector_weights(A_pair)

    # Baseline
    base_out = topsis_scores(X, w_base, ctypes)
    C_base = base_out['C']
    base_ranks = np.argsort(-C_base).argsort() + 1  # 1-indeksert

    # Pertubasjoner
    deltas = [-0.20, 0.20]
    sens = sensitivity_matrix(X, w_base, ctypes, deltas)

    print("\nBaseline C_i:")
    for s, c, r in zip(SUPPLIERS, C_base, base_ranks):
        print(f"  {s:<8s} C = {c:.4f}   rank = {r}")

    # Skriv ut rangeringsstabilitet
    print("\nRang under +20% pertubasjon per kriterium:")
    print(f"  {'':8s}" + ''.join(f'{c:>14s}' for c in CRITERIA))
    for i, s in enumerate(SUPPLIERS):
        row_ranks = sens['delta_+0.20']['rank'][i]
        print(f"  {s:<8s}" + ''.join(f'{r:>14d}' for r in row_ranks))

    print("\nRang under -20% pertubasjon per kriterium:")
    print(f"  {'':8s}" + ''.join(f'{c:>14s}' for c in CRITERIA))
    for i, s in enumerate(SUPPLIERS):
        row_ranks = sens['delta_-0.20']['rank'][i]
        print(f"  {s:<8s}" + ''.join(f'{r:>14d}' for r in row_ranks))

    # Serialiser
    serial = {
        'baseline_C': [float(round(x, 6)) for x in C_base.tolist()],
        'baseline_rank': [int(r) for r in base_ranks.tolist()],
        'deltas': [float(d) for d in deltas],
        'perturbations': {},
    }
    for d in deltas:
        key = f'delta_{d:+.2f}'
        serial['perturbations'][key] = {
            'C': [[float(round(x, 6)) for x in row]
                  for row in sens[key]['C'].tolist()],
            'rank': [[int(x) for x in row]
                     for row in sens[key]['rank'].tolist()],
        }

    with open(OUTPUT_DIR / 'step05_results.json', 'w', encoding='utf-8') as f:
        json.dump(serial, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step05_results.json'}")

    # Spider-figur
    plot_sensitivity_spider(SUPPLIERS, CRITERIA, C_base, sens,
                            OUTPUT_DIR / 'ahp_sensitivitet_spider.png')


if __name__ == '__main__':
    main()
