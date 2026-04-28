"""
Steg 5: Sensitivitetsanalyse
============================
Hvor mye paavirkes Wq naar vi endrer lambda eller my med +/-20 %?
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import LAMBDA_TRUE, MU_TRUE
from step02_analytisk import mm1_formler

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def sensitivitet() -> dict:
    """Beregn Wq-respons paa endringer i lambda og my."""
    baseline = mm1_formler(LAMBDA_TRUE, MU_TRUE)
    Wq_base = baseline['Wq'] * 60.0

    endringer = np.linspace(-0.20, 0.20, 21)  # +/- 20 %
    lambda_serie = []
    mu_serie = []

    for e in endringer:
        lam_ny = LAMBDA_TRUE * (1.0 + e)
        mu_ny = MU_TRUE * (1.0 + e)
        # Lambda-endring med fast my
        if mu_ny > 0 and MU_TRUE > lam_ny:
            f = mm1_formler(lam_ny, MU_TRUE)
            lambda_serie.append({
                'endring': round(e, 3),
                'lambda': round(lam_ny, 3),
                'rho': round(f['rho'], 4),
                'Wq_min': round(f['Wq'] * 60.0, 3),
                'dWq_min': round(f['Wq'] * 60.0 - Wq_base, 3),
            })
        # My-endring med fast lambda
        if mu_ny > LAMBDA_TRUE:
            f = mm1_formler(LAMBDA_TRUE, mu_ny)
            mu_serie.append({
                'endring': round(e, 3),
                'mu': round(mu_ny, 3),
                'rho': round(f['rho'], 4),
                'Wq_min': round(f['Wq'] * 60.0, 3),
                'dWq_min': round(f['Wq'] * 60.0 - Wq_base, 3),
            })

    return {
        'baseline_Wq_min': round(Wq_base, 3),
        'lambda_sensitivitet': lambda_serie,
        'mu_sensitivitet': mu_serie,
    }


def plot_sensitivitet(resultater: dict, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))

    lam = resultater['lambda_sensitivitet']
    mu = resultater['mu_sensitivitet']
    x_lam = [100 * r['endring'] for r in lam]
    y_lam = [r['Wq_min'] for r in lam]
    x_mu = [100 * r['endring'] for r in mu]
    y_mu = [r['Wq_min'] for r in mu]

    ax.plot(x_lam, y_lam, marker='o', color='#9C540B', linewidth=2,
            markersize=5, label=r'Endring i $\lambda$ (fast $\mu$)')
    ax.plot(x_mu, y_mu, marker='s', color='#307453', linewidth=2,
            markersize=5, label=r'Endring i $\mu$ (fast $\lambda$)')
    ax.axhline(y=resultater['baseline_Wq_min'], color='#1F2933',
               linestyle='--', alpha=0.6, linewidth=1,
               label=r'Baseline $W_q$')

    ax.set_xlabel('Prosentvis endring i parameter (%)', fontsize=11)
    ax.set_ylabel(r'Ventetid $W_q$ (min)', fontsize=11)
    ax.set_title(r'Sensitivitet av $W_q$ for $\lambda$ og $\mu$',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: SENSITIVITETSANALYSE")
    print("=" * 60)

    res = sensitivitet()
    print(f"Baseline Wq = {res['baseline_Wq_min']} min")
    ekstrem_lam = res['lambda_sensitivitet'][-1]
    ekstrem_mu = res['mu_sensitivitet'][0]
    print(f"  +20 % lambda -> Wq = {ekstrem_lam['Wq_min']} min "
          f"(rho = {ekstrem_lam['rho']})")
    print(f"  -20 % my     -> Wq = {ekstrem_mu['Wq_min']} min "
          f"(rho = {ekstrem_mu['rho']})")

    path = OUTPUT_DIR / 'step05_results.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(res, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {path}")

    plot_sensitivitet(res, OUTPUT_DIR / 'mm1_sensitivity.png')


if __name__ == '__main__':
    main()
