"""
Steg 2: Analytiske M/M/1-formler
================================
Beregner rho, L, Lq, W, Wq for baseline-parametrene og for et spekter
av utnyttelsesverdier rho i (0, 1).
"""

import json
from pathlib import Path

import numpy as np

from step01_datainnsamling import LAMBDA_TRUE, MU_TRUE

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def mm1_formler(lmbda: float, mu: float) -> dict:
    """Lukkede M/M/1-formler."""
    if mu <= lmbda:
        raise ValueError("Krav: my > lambda (rho < 1).")
    rho = lmbda / mu
    L = rho / (1.0 - rho)
    Lq = rho ** 2 / (1.0 - rho)
    W = 1.0 / (mu - lmbda)
    Wq = rho / (mu - lmbda)
    P0 = 1.0 - rho
    return {
        'lambda': lmbda,
        'mu': mu,
        'rho': rho,
        'L': L,
        'Lq': Lq,
        'W': W,
        'Wq': Wq,
        'P0': P0,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 2: ANALYTISKE M/M/1-FORMLER")
    print("=" * 60)

    # Baseline
    baseline = mm1_formler(LAMBDA_TRUE, MU_TRUE)
    print(f"\nBaseline (lambda={LAMBDA_TRUE}, my={MU_TRUE}):")
    for k, v in baseline.items():
        print(f"  {k} = {v:.4f}")

    # W og Wq i minutter (lettere tolkning)
    baseline_min = {
        'W_min': baseline['W'] * 60.0,
        'Wq_min': baseline['Wq'] * 60.0,
    }
    print(f"  W  = {baseline_min['W_min']:.2f} min")
    print(f"  Wq = {baseline_min['Wq_min']:.2f} min")

    # Kurve rho in (0.05, 0.99)
    rho_grid = np.concatenate([
        np.linspace(0.05, 0.90, 18),
        np.linspace(0.91, 0.99, 9),
    ])
    kurve = []
    for rho in rho_grid:
        lam = rho * MU_TRUE
        f = mm1_formler(lam, MU_TRUE)
        kurve.append({
            'rho': round(rho, 4),
            'L': round(f['L'], 4),
            'Lq': round(f['Lq'], 4),
            'W_min': round(f['W'] * 60.0, 3),
            'Wq_min': round(f['Wq'] * 60.0, 3),
        })

    results = {
        'baseline': {k: round(v, 5) for k, v in baseline.items()},
        'baseline_W_min': round(baseline_min['W_min'], 3),
        'baseline_Wq_min': round(baseline_min['Wq_min'], 3),
        'kurve': kurve,
    }
    results_path = OUTPUT_DIR / 'step02_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")


if __name__ == '__main__':
    main()
