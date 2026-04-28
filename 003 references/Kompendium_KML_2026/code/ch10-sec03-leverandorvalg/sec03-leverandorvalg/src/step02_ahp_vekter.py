"""
Steg 2: AHP -- egenvektor-vekter + CI/CR-konsistenssjekk
========================================================
Beregner kriterievekter fra parvis sammenligningsmatrise ved hjelp
av den dominerende egenvektoren (principal eigenvector), og sjekker
konsistens med Consistency Index (CI) og Consistency Ratio (CR).

Referanse: Saaty (1980) The Analytic Hierarchy Process.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    CRITERIA,
    get_pairwise_dataframe,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


# Saatys Random Index (RI) for tilfeldig parvis matrise (Saaty 1980)
RANDOM_INDEX = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90,
                5: 1.12, 6: 1.24, 7: 1.32, 8: 1.41,
                9: 1.45, 10: 1.49}


def ahp_eigenvector_weights(A: np.ndarray) -> tuple[np.ndarray, float]:
    """
    Beregn vekter som normalisert dominerende egenvektor til A.

    Returnerer
    ----------
    weights : np.ndarray, shape (n,)
        Normaliserte vekter (summerer til 1)
    lambda_max : float
        Største egenverdi (brukes til CI-beregning)
    """
    eigvals, eigvecs = np.linalg.eig(A)
    # Velg indeks med størst (reell del av) egenverdi
    idx = np.argmax(eigvals.real)
    lambda_max = float(eigvals[idx].real)
    w = eigvecs[:, idx].real
    w = w / w.sum()
    return w, lambda_max


def geometric_mean_weights(A: np.ndarray) -> np.ndarray:
    """Alternativ: geometrisk snitt per rad (raskt og nærliggende)."""
    g = np.exp(np.log(A).mean(axis=1))
    return g / g.sum()


def consistency_check(A: np.ndarray, lambda_max: float) -> dict:
    """Beregn CI og CR for en n x n sammenligningsmatrise."""
    n = A.shape[0]
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0.0
    ri = RANDOM_INDEX.get(n, 1.49)
    cr = ci / ri if ri > 0 else 0.0
    return {
        'n': int(n),
        'lambda_max': float(round(lambda_max, 6)),
        'CI': float(round(ci, 6)),
        'RI': float(round(ri, 3)),
        'CR': float(round(cr, 6)),
        'acceptable': bool(cr < 0.10),
    }


def plot_weights_bar(criteria: list[str], weights: np.ndarray,
                     output_path: Path) -> None:
    """Søylediagram for AHP-vekter."""
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']
    bars = ax.bar(criteria, weights, color=colors[:len(criteria)],
                  edgecolor='black', linewidth=0.6)
    for bar, w in zip(bars, weights):
        ax.text(bar.get_x() + bar.get_width() / 2, w + 0.005,
                f'{w:.3f}', ha='center', va='bottom', fontsize=10)
    ax.set_ylabel('Vekt $w_j$', fontsize=12)
    ax.set_ylim(0, max(weights) * 1.25)
    ax.set_title('AHP-vekter $w_j$ (dominerende egenvektor)',
                 fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.tick_params(axis='x', labelsize=11, rotation=15)
    ax.tick_params(axis='y', labelsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 2: AHP-VEKTER OG KONSISTENSSJEKK")
    print(f"{'='*60}")

    pairwise_df = get_pairwise_dataframe()
    A = pairwise_df.values

    # Hovedmetode: dominerende egenvektor
    w_eig, lam_max = ahp_eigenvector_weights(A)
    # Tilleggsmetode: geometrisk snitt (bør være nær)
    w_geom = geometric_mean_weights(A)

    print("\n--- Egenvektor-vekter ---")
    for c, w in zip(CRITERIA, w_eig):
        print(f"  {c:<14s} w = {w:.4f}")
    print(f"  lambda_max = {lam_max:.4f}")

    print("\n--- Geometriske vekter (kontroll) ---")
    for c, w in zip(CRITERIA, w_geom):
        print(f"  {c:<14s} w = {w:.4f}")

    # Konsistens
    check = consistency_check(A, lam_max)
    print("\n--- Konsistenssjekk ---")
    print(f"  n          = {check['n']}")
    print(f"  lambda_max = {check['lambda_max']}")
    print(f"  CI         = {check['CI']}")
    print(f"  RI         = {check['RI']}")
    print(f"  CR         = {check['CR']}  "
          f"({'OK (< 0.10)' if check['acceptable'] else 'FOR HØYT (>= 0.10)'})")

    # Lagre
    results = {
        'criteria': CRITERIA,
        'weights_eigenvector': [float(round(x, 6)) for x in w_eig.tolist()],
        'weights_geometric':   [float(round(x, 6)) for x in w_geom.tolist()],
        'lambda_max': float(round(lam_max, 6)),
        'consistency': check,
    }
    with open(OUTPUT_DIR / 'step02_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step02_results.json'}")

    # Figur
    plot_weights_bar(CRITERIA, w_eig, OUTPUT_DIR / 'ahp_vekter.png')


if __name__ == '__main__':
    main()
