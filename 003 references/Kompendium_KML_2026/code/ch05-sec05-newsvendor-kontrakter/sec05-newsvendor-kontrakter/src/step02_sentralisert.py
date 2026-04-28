"""
Steg 2: Sentralisert newsvendor (integrert kjede)
=================================================
Beregner optimal bestilling naar kjeden opererer som en enhet:
  Q_kjede* = F^{-1}((p - c) / (p - s))

Plotter forventet kjedeprofitt som funksjon av Q, og markerer det optimale
punktet og sammenligner med gjennomsnittlig etterspoersel.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from step01_datainnsamling import (
    MU_DEMAND,
    SIGMA_DEMAND,
    PRICE_RETAIL,
    COST_SUPPLIER,
    SALVAGE_VALUE,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def expected_chain_profit(Q: float, p: float, c: float, s: float,
                          mu: float, sigma: float) -> float:
    """Forventet kjedeprofitt for bestilling Q under normalfordelt etterspoersel.

    Bruker lukket formel for normalfordeling:
      E[min(D, Q)] = mu - sigma * L(z), der z = (Q - mu)/sigma
      L(z) = phi(z) - z * (1 - Phi(z))  (standard loss function)
    """
    z = (Q - mu) / sigma
    loss = stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z))
    expected_sales = mu - sigma * loss           # E[min(D, Q)]
    expected_leftover = Q - expected_sales        # E[(Q - D)^+]
    revenue = p * expected_sales + s * expected_leftover
    cost = c * Q
    return revenue - cost


def optimal_q(p: float, c: float, s: float, mu: float, sigma: float) -> float:
    """Klassisk newsvendor-loesning."""
    cr = (p - c) / (p - s)
    return stats.norm.ppf(cr, loc=mu, scale=sigma)


def plot_profit_curve(output_path: Path) -> None:
    """Plot forventet kjedeprofitt som funksjon av Q."""
    q_star = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                       MU_DEMAND, SIGMA_DEMAND)
    Q_range = np.linspace(MU_DEMAND - 3 * SIGMA_DEMAND,
                          MU_DEMAND + 3 * SIGMA_DEMAND, 400)
    profit = np.array([expected_chain_profit(q, PRICE_RETAIL, COST_SUPPLIER,
                                             SALVAGE_VALUE, MU_DEMAND,
                                             SIGMA_DEMAND) for q in Q_range])

    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.plot(Q_range, profit / 1000, color='#1F6587', linewidth=2,
            label=r'$E[\Pi_{kjede}(Q)]$')

    pi_star = expected_chain_profit(q_star, PRICE_RETAIL, COST_SUPPLIER,
                                    SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    ax.axvline(q_star, color='#961D1C', linestyle='--', linewidth=1.7,
               label=f'$Q^*_{{kjede}} = {q_star:.0f}$')
    ax.axhline(pi_star / 1000, color='#961D1C', linestyle=':', linewidth=1.2,
               alpha=0.6)
    ax.plot([q_star], [pi_star / 1000], 'o', color='#961D1C', markersize=10,
            zorder=5)

    ax.axvline(MU_DEMAND, color='#307453', linestyle=':', linewidth=1.3,
               label=fr'$\mu = {MU_DEMAND}$')

    # Markere omtrent hvor naiv (produsere mu) ligger
    pi_mu = expected_chain_profit(MU_DEMAND, PRICE_RETAIL, COST_SUPPLIER,
                                  SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    ax.plot([MU_DEMAND], [pi_mu / 1000], 's', color='#307453', markersize=9,
            zorder=5)

    ax.set_xlabel(r'$Q$ (bestilt kvantum)', fontsize=12)
    ax.set_ylabel(r'$E[\Pi_{kjede}(Q)]$  (tusen NOK)', fontsize=12)
    ax.set_title('Forventet kjedeprofitt som funksjon av bestilling',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='lower center', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 2: SENTRALISERT NEWSVENDOR')
    print('=' * 60)

    cr = (PRICE_RETAIL - COST_SUPPLIER) / (PRICE_RETAIL - SALVAGE_VALUE)
    q_star = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                       MU_DEMAND, SIGMA_DEMAND)
    pi_star = expected_chain_profit(q_star, PRICE_RETAIL, COST_SUPPLIER,
                                    SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)

    # Sammenlign med naiv strategi Q = mu
    pi_mu = expected_chain_profit(MU_DEMAND, PRICE_RETAIL, COST_SUPPLIER,
                                  SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)

    print(f'\nKritisk forhold (p-c)/(p-s) : {cr:.4f}')
    print(f'Q*_kjede (optimal bestilling)  : {q_star:.1f}')
    print(f'Sikkerhetslager over mu        : {q_star - MU_DEMAND:.1f}')
    print(f'\nForventet kjedeprofitt ved Q* : {pi_star:,.0f} NOK')
    print(f'Forventet kjedeprofitt ved mu : {pi_mu:,.0f} NOK')
    print(f'Gevinst ved Q* vs mu          : {pi_star - pi_mu:,.0f} NOK')

    results = {
        'kritisk_forhold': round(cr, 4),
        'q_star_kjede': round(float(q_star), 1),
        'profitt_q_star': round(float(pi_star), 0),
        'profitt_mu': round(float(pi_mu), 0),
        'gevinst_vs_mu': round(float(pi_star - pi_mu), 0),
    }

    with open(OUTPUT_DIR / 'step02_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step02_results.json'}")

    plot_profit_curve(OUTPUT_DIR / 'nv_profit_curve.png')


if __name__ == '__main__':
    main()
