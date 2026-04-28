"""
Steg 3: Desentralisert newsvendor (double marginalization)
==========================================================
Naar detaljisten optimerer for seg selv med engrospris w > c, blir:
  Q_R* = F^{-1}((p - w) / (p - s)) < Q_kjede*

Leverandoer og detaljist deler profitt etter sine egne regnestykker.
Sammenligner kjedeprofitten mot den sentraliserte loesningen (verdi-gap).
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
    WHOLESALE_PRICE,
)
from step02_sentralisert import expected_chain_profit, optimal_q

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def retailer_profit(Q: float, p: float, w: float, s: float,
                    mu: float, sigma: float) -> float:
    """Detaljistens forventede profitt.

    Detaljist kjoeper for w og selger for p (eller s ved restsalg).
    E[profitt_R] = p * E[min(D, Q)] + s * E[(Q - D)^+] - w * Q
    """
    z = (Q - mu) / sigma
    loss = stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z))
    expected_sales = mu - sigma * loss
    expected_leftover = Q - expected_sales
    return p * expected_sales + s * expected_leftover - w * Q


def supplier_profit(Q: float, w: float, c: float) -> float:
    """Leverandoerens profitt: selger Q enheter til engrospris w, koster c."""
    return (w - c) * Q


def optimal_q_retailer(p: float, w: float, s: float,
                       mu: float, sigma: float) -> float:
    """Detaljistens beste respons gitt engrospris w."""
    cr = (p - w) / (p - s)
    return stats.norm.ppf(cr, loc=mu, scale=sigma)


def plot_centralized_vs_decentralized(output_path: Path) -> None:
    """Sammenlign de to ordrekvantumene og profittkurvene."""
    q_chain = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                        MU_DEMAND, SIGMA_DEMAND)
    q_ret = optimal_q_retailer(PRICE_RETAIL, WHOLESALE_PRICE, SALVAGE_VALUE,
                               MU_DEMAND, SIGMA_DEMAND)

    Q_range = np.linspace(MU_DEMAND - 3 * SIGMA_DEMAND,
                          MU_DEMAND + 3 * SIGMA_DEMAND, 400)

    pi_chain = np.array([expected_chain_profit(q, PRICE_RETAIL, COST_SUPPLIER,
                                               SALVAGE_VALUE, MU_DEMAND,
                                               SIGMA_DEMAND) for q in Q_range])
    pi_ret = np.array([retailer_profit(q, PRICE_RETAIL, WHOLESALE_PRICE,
                                       SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
                       for q in Q_range])

    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.plot(Q_range, pi_chain / 1000, color='#1F6587', linewidth=2,
            label=r'$E[\Pi_{kjede}(Q)]$ (integrert)')
    ax.plot(Q_range, pi_ret / 1000, color='#9C540B', linewidth=2,
            label=r'$E[\Pi_R(Q \mid w)]$ (detaljist)')

    ax.axvline(q_chain, color='#1F6587', linestyle='--', linewidth=1.5,
               label=f'$Q^*_{{kjede}} = {q_chain:.0f}$')
    ax.axvline(q_ret, color='#9C540B', linestyle='--', linewidth=1.5,
               label=f'$Q^*_R = {q_ret:.0f}$')

    pi_chain_star = expected_chain_profit(q_chain, PRICE_RETAIL, COST_SUPPLIER,
                                          SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    pi_chain_at_qr = expected_chain_profit(q_ret, PRICE_RETAIL, COST_SUPPLIER,
                                           SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)

    # Marker gap
    ax.annotate('', xy=(q_chain, pi_chain_star / 1000),
                xytext=(q_ret, pi_chain_at_qr / 1000),
                arrowprops=dict(arrowstyle='->', color='#961D1C', linewidth=1.5))
    gap_midx = 0.5 * (q_chain + q_ret)
    gap_midy = 0.5 * (pi_chain_star + pi_chain_at_qr) / 1000
    ax.text(gap_midx, gap_midy + 15, 'verdi-gap',
            color='#961D1C', fontsize=10, ha='center')

    ax.set_xlabel(r'$Q$ (bestilt kvantum)', fontsize=12)
    ax.set_ylabel(r'Forventet profitt  (tusen NOK)', fontsize=12)
    ax.set_title('Sentralisert vs desentralisert optimering',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='lower center', fontsize=10, ncol=2)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 3: DESENTRALISERT NEWSVENDOR')
    print('=' * 60)

    q_chain = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                        MU_DEMAND, SIGMA_DEMAND)
    q_ret = optimal_q_retailer(PRICE_RETAIL, WHOLESALE_PRICE, SALVAGE_VALUE,
                               MU_DEMAND, SIGMA_DEMAND)

    cr_chain = (PRICE_RETAIL - COST_SUPPLIER) / (PRICE_RETAIL - SALVAGE_VALUE)
    cr_ret = (PRICE_RETAIL - WHOLESALE_PRICE) / (PRICE_RETAIL - SALVAGE_VALUE)

    pi_chain_at_q_chain = expected_chain_profit(q_chain, PRICE_RETAIL,
                                                COST_SUPPLIER, SALVAGE_VALUE,
                                                MU_DEMAND, SIGMA_DEMAND)
    pi_chain_at_q_ret = expected_chain_profit(q_ret, PRICE_RETAIL,
                                              COST_SUPPLIER, SALVAGE_VALUE,
                                              MU_DEMAND, SIGMA_DEMAND)
    pi_retailer = retailer_profit(q_ret, PRICE_RETAIL, WHOLESALE_PRICE,
                                  SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    pi_supplier = supplier_profit(q_ret, WHOLESALE_PRICE, COST_SUPPLIER)

    print(f'\nKritisk forhold kjeden   : {cr_chain:.4f}  --> Q*_kjede = {q_chain:.1f}')
    print(f'Kritisk forhold detaljist: {cr_ret:.4f}  --> Q*_R     = {q_ret:.1f}')
    print(f'\nDouble marginalization-gap:')
    print(f'  Q*_kjede - Q*_R         : {q_chain - q_ret:.1f} enheter')
    print(f'\nProfitter ved desentralisert loesning Q*_R:')
    print(f'  Detaljist               : {pi_retailer:,.0f} NOK')
    print(f'  Leverandoer             : {pi_supplier:,.0f} NOK')
    print(f'  Kjede (sum)             : {pi_retailer + pi_supplier:,.0f} NOK')
    print(f'\nIntegrert (referanse) Q*_kjede: {pi_chain_at_q_chain:,.0f} NOK')
    print(f'Tap ved double margin.  : {pi_chain_at_q_chain - (pi_retailer + pi_supplier):,.0f} NOK')

    efficiency = (pi_retailer + pi_supplier) / pi_chain_at_q_chain

    results = {
        'q_chain': round(float(q_chain), 1),
        'q_retailer': round(float(q_ret), 1),
        'kritisk_forhold_kjede': round(float(cr_chain), 4),
        'kritisk_forhold_retailer': round(float(cr_ret), 4),
        'profitt_retailer_desentralisert': round(float(pi_retailer), 0),
        'profitt_supplier_desentralisert': round(float(pi_supplier), 0),
        'profitt_kjede_desentralisert': round(float(pi_retailer + pi_supplier), 0),
        'profitt_kjede_integrert': round(float(pi_chain_at_q_chain), 0),
        'tap_dobbelmarg': round(float(pi_chain_at_q_chain -
                                      (pi_retailer + pi_supplier)), 0),
        'effektivitet': round(float(efficiency), 4),
    }

    with open(OUTPUT_DIR / 'step03_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step03_results.json'}")

    plot_centralized_vs_decentralized(OUTPUT_DIR / 'nv_centralized_vs_decentralized.png')


if __name__ == '__main__':
    main()
