"""
Steg 3: TOPSIS -- avstand til ideal- og anti-idealløsning
==========================================================
- Vektornormalisering av ytelsesmatrise X -> R.
- Vekting med AHP-vekter -> V.
- Bestem positive (A+) og negative (A-) idealløsninger basert på
  cost/benefit-kriterier.
- Beregn euklidsk avstand d+_i og d-_i for hver leverandør.
- Nærhetsskår C_i = d-_i / (d+_i + d-_i).

Referanse: Hwang & Yoon (1981).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    CRITERIA,
    CRITERION_TYPES,
    SUPPLIERS,
    get_performance_dataframe,
)
from step02_ahp_vekter import ahp_eigenvector_weights
from step01_datainnsamling import get_pairwise_dataframe

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def vector_normalize(X: np.ndarray) -> np.ndarray:
    """Vektornormalisering: r_ij = x_ij / sqrt(sum_k x_kj^2)."""
    denom = np.sqrt((X ** 2).sum(axis=0))
    return X / denom


def topsis_scores(
    X: np.ndarray,
    weights: np.ndarray,
    criterion_types: list[str],
) -> dict:
    """Kjør hele TOPSIS-prosedyren og returner alle mellomtrinn."""
    m, n = X.shape
    assert len(weights) == n
    assert len(criterion_types) == n

    # 1) Vektornormalisering
    R = vector_normalize(X)

    # 2) Vektet normalisert matrise
    V = R * weights

    # 3) Ideal (A+) og anti-ideal (A-) per kolonne
    A_plus = np.zeros(n)
    A_minus = np.zeros(n)
    for j, ctype in enumerate(criterion_types):
        col = V[:, j]
        if ctype == 'benefit':
            A_plus[j] = col.max()
            A_minus[j] = col.min()
        elif ctype == 'cost':
            A_plus[j] = col.min()
            A_minus[j] = col.max()
        else:
            raise ValueError(f"Ukjent kriterietype: {ctype}")

    # 4) Euklidske avstander
    d_plus = np.sqrt(((V - A_plus) ** 2).sum(axis=1))
    d_minus = np.sqrt(((V - A_minus) ** 2).sum(axis=1))

    # 5) Nærhetsskår
    C = d_minus / (d_plus + d_minus)

    return {
        'R': R,
        'V': V,
        'A_plus': A_plus,
        'A_minus': A_minus,
        'd_plus': d_plus,
        'd_minus': d_minus,
        'C': C,
    }


def plot_distances(suppliers: list[str], d_plus: np.ndarray,
                   d_minus: np.ndarray, output_path: Path) -> None:
    """Dobbelt-søylediagram som viser d+_i og d-_i per leverandør."""
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(suppliers))
    width = 0.38

    ax.bar(x - width / 2, d_plus, width, label='$d_i^{+}$ (avstand til ideal)',
           color='#ED9F9E', edgecolor='#961D1C', linewidth=0.6)
    ax.bar(x + width / 2, d_minus, width,
           label='$d_i^{-}$ (avstand til anti-ideal)',
           color='#97D4B7', edgecolor='#307453', linewidth=0.6)

    ax.set_xticks(x)
    ax.set_xticklabels(suppliers, fontsize=11)
    ax.set_ylabel('Euklidsk avstand', fontsize=11)
    ax.set_title('TOPSIS-avstander per leverandør',
                 fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.tick_params(axis='both', labelsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 3: TOPSIS -- AVSTAND OG NÆRHETSSKÅR")
    print(f"{'='*60}")

    perf = get_performance_dataframe()
    X = perf.values.astype(float)
    ctypes = [CRITERION_TYPES[c] for c in CRITERIA]

    # Hent AHP-vekter på nytt
    A_pair = get_pairwise_dataframe().values
    weights, _ = ahp_eigenvector_weights(A_pair)

    topsis = topsis_scores(X, weights, ctypes)

    print("\n--- Normalisert matrise R ---")
    for i, s in enumerate(SUPPLIERS):
        row = '  '.join(f'{v:.4f}' for v in topsis['R'][i])
        print(f"  {s:<8s} {row}")

    print("\n--- Vektet normalisert V ---")
    for i, s in enumerate(SUPPLIERS):
        row = '  '.join(f'{v:.4f}' for v in topsis['V'][i])
        print(f"  {s:<8s} {row}")

    print("\n--- Idealløsninger ---")
    for j, c in enumerate(CRITERIA):
        print(f"  {c:<14s} A+={topsis['A_plus'][j]:.4f}   "
              f"A-={topsis['A_minus'][j]:.4f}   ({ctypes[j]})")

    print("\n--- Avstander og nærhetsskår ---")
    print(f"  {'Leverandør':<10s}  {'d+':>8s}  {'d-':>8s}  {'C':>8s}")
    for i, s in enumerate(SUPPLIERS):
        print(f"  {s:<10s}  "
              f"{topsis['d_plus'][i]:>8.4f}  "
              f"{topsis['d_minus'][i]:>8.4f}  "
              f"{topsis['C'][i]:>8.4f}")

    # Lagre
    results = {
        'suppliers': SUPPLIERS,
        'criteria': CRITERIA,
        'weights': [float(round(w, 6)) for w in weights.tolist()],
        'R': [[float(round(v, 6)) for v in row] for row in topsis['R'].tolist()],
        'V': [[float(round(v, 6)) for v in row] for row in topsis['V'].tolist()],
        'A_plus': [float(round(v, 6)) for v in topsis['A_plus'].tolist()],
        'A_minus': [float(round(v, 6)) for v in topsis['A_minus'].tolist()],
        'd_plus': [float(round(v, 6)) for v in topsis['d_plus'].tolist()],
        'd_minus': [float(round(v, 6)) for v in topsis['d_minus'].tolist()],
        'C': [float(round(v, 6)) for v in topsis['C'].tolist()],
    }
    with open(OUTPUT_DIR / 'step03_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step03_results.json'}")

    # Figur
    plot_distances(SUPPLIERS, topsis['d_plus'], topsis['d_minus'],
                   OUTPUT_DIR / 'ahp_topsis_distanser.png')


if __name__ == '__main__':
    main()
