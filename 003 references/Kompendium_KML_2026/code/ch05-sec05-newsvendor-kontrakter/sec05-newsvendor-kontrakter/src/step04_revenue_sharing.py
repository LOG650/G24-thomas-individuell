"""
Steg 4: Revenue-sharing-kontrakt
================================
Leverandoeren tilbyr en ny engrospris w' og beholder en andel 1 - phi av
detaljistens omsetning. Detaljisten faar dermed en andel phi av inntektene.
Ved valg av w' = phi * c og phi in (0, 1) koordineres kjeden:
  Detaljistens kritiske forhold blir (phi*p - phi*c) / (phi*p - phi*s) = CR_kjede,
  saa Q*_R(phi) = Q*_kjede.

phi fordeler kjedens profittkake mellom de to partene. Vi velger phi slik at
begge parter tjener mer enn under den desentraliserte loesningen (pareto-forbedring).
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
from step03_desentralisert import retailer_profit, supplier_profit, optimal_q_retailer

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def rs_retailer_profit(Q: float, phi: float, p: float, w_prime: float,
                       s: float, mu: float, sigma: float) -> float:
    """Detaljistens profitt under revenue-sharing.

    Detaljist beholder phi-andelen av omsetningen.
    E[profitt_R] = phi * (p * E[min(D,Q)] + s * E[(Q-D)^+]) - w' * Q
    """
    z = (Q - mu) / sigma
    loss = stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z))
    expected_sales = mu - sigma * loss
    expected_leftover = Q - expected_sales
    return phi * (p * expected_sales + s * expected_leftover) - w_prime * Q


def rs_supplier_profit(Q: float, phi: float, p: float, w_prime: float,
                       c: float, s: float, mu: float, sigma: float) -> float:
    """Leverandoerens profitt under revenue-sharing.

    Selger Q til redusert pris w' og faar (1 - phi) av omsetningen.
    """
    z = (Q - mu) / sigma
    loss = stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z))
    expected_sales = mu - sigma * loss
    expected_leftover = Q - expected_sales
    return (w_prime - c) * Q + (1 - phi) * (p * expected_sales + s * expected_leftover)


def coordinated_wholesale(phi: float, c: float) -> float:
    """Koordinerende engrospris: w' = phi * c."""
    return phi * c


def plot_pareto_frontier(output_path: Path) -> None:
    """Plot Pareto-frontieren: profitt for detaljist vs leverandoer over phi."""
    q_chain = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                        MU_DEMAND, SIGMA_DEMAND)
    pi_chain = expected_chain_profit(q_chain, PRICE_RETAIL, COST_SUPPLIER,
                                     SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)

    # Desentraliserte baseline-profitter
    q_ret_dec = optimal_q_retailer(PRICE_RETAIL, WHOLESALE_PRICE, SALVAGE_VALUE,
                                   MU_DEMAND, SIGMA_DEMAND)
    pi_ret_dec = retailer_profit(q_ret_dec, PRICE_RETAIL, WHOLESALE_PRICE,
                                 SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    pi_sup_dec = supplier_profit(q_ret_dec, WHOLESALE_PRICE, COST_SUPPLIER)

    # Pareto-frontier under revenue-sharing
    phis = np.linspace(0.05, 0.95, 91)
    ret_profits = np.zeros_like(phis)
    sup_profits = np.zeros_like(phis)
    for i, phi in enumerate(phis):
        w_prime = coordinated_wholesale(phi, COST_SUPPLIER)
        ret_profits[i] = rs_retailer_profit(q_chain, phi, PRICE_RETAIL,
                                            w_prime, SALVAGE_VALUE,
                                            MU_DEMAND, SIGMA_DEMAND)
        sup_profits[i] = rs_supplier_profit(q_chain, phi, PRICE_RETAIL,
                                            w_prime, COST_SUPPLIER,
                                            SALVAGE_VALUE, MU_DEMAND,
                                            SIGMA_DEMAND)

    # Finn pareto-forbedringsomraadet: begge >= desentralisert
    pareto_mask = (ret_profits >= pi_ret_dec) & (sup_profits >= pi_sup_dec)
    phi_min = phis[pareto_mask].min() if pareto_mask.any() else None
    phi_max = phis[pareto_mask].max() if pareto_mask.any() else None

    fig, ax = plt.subplots(figsize=(10, 5.5))

    ax.plot(ret_profits / 1000, sup_profits / 1000, color='#1F6587',
            linewidth=2, label=r'Revenue-sharing (varierer $\varphi$)')
    if pareto_mask.any():
        ax.plot(ret_profits[pareto_mask] / 1000, sup_profits[pareto_mask] / 1000,
                color='#307453', linewidth=4, alpha=0.7,
                label='Pareto-forbedrings-region')

    ax.plot([pi_ret_dec / 1000], [pi_sup_dec / 1000], 's',
            color='#961D1C', markersize=12, zorder=5,
            label=f'Desentralisert ({pi_ret_dec/1000:.0f}, {pi_sup_dec/1000:.0f})')

    # Valgt phi = 0.5 for illustrasjon
    phi_mid = 0.5
    w_mid = coordinated_wholesale(phi_mid, COST_SUPPLIER)
    ret_mid = rs_retailer_profit(q_chain, phi_mid, PRICE_RETAIL, w_mid,
                                 SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    sup_mid = rs_supplier_profit(q_chain, phi_mid, PRICE_RETAIL, w_mid,
                                 COST_SUPPLIER, SALVAGE_VALUE,
                                 MU_DEMAND, SIGMA_DEMAND)
    ax.plot([ret_mid / 1000], [sup_mid / 1000], 'o', color='#5A2C77',
            markersize=12, zorder=5,
            label=rf'$\varphi = {phi_mid}$ ({ret_mid/1000:.0f}, {sup_mid/1000:.0f})')

    ax.axhline(pi_sup_dec / 1000, color='#961D1C', linestyle=':',
               linewidth=1.0, alpha=0.5)
    ax.axvline(pi_ret_dec / 1000, color='#961D1C', linestyle=':',
               linewidth=1.0, alpha=0.5)

    ax.set_xlabel(r'Forventet detaljistprofitt (tusen NOK)', fontsize=12)
    ax.set_ylabel(r'Forventet leverandoerprofitt (tusen NOK)', fontsize=12)
    ax.set_title('Pareto-frontier under revenue-sharing-kontrakt',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')

    return (pi_ret_dec, pi_sup_dec, pi_chain, phi_min, phi_max,
            phi_mid, ret_mid, sup_mid)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 4: REVENUE-SHARING-KONTRAKT')
    print('=' * 60)

    (pi_ret_dec, pi_sup_dec, pi_chain_star,
     phi_min, phi_max,
     phi_mid, ret_mid, sup_mid) = plot_pareto_frontier(
        OUTPUT_DIR / 'nv_revenue_sharing_pareto.png')

    q_chain = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                        MU_DEMAND, SIGMA_DEMAND)

    print(f'\nKoordinert bestilling      : Q = Q*_kjede = {q_chain:.1f}')
    print(f'Kjedeprofitt (integrert)   : {pi_chain_star:,.0f} NOK')
    print(f'\nDesentralisert baseline:')
    print(f'  Detaljist                : {pi_ret_dec:,.0f} NOK')
    print(f'  Leverandoer              : {pi_sup_dec:,.0f} NOK')
    print(f'\nPareto-forbedrings-region for phi:')
    if phi_min is not None:
        print(f'  phi in [{phi_min:.2f}, {phi_max:.2f}]')
    else:
        print('  ingen pareto-forbedring funnet')

    # Verifiser for valgt phi = 0.5
    w_mid = coordinated_wholesale(phi_mid, COST_SUPPLIER)
    print(f'\nIllustrativt valg phi = {phi_mid}:')
    print(f"  Koordinerende engrospris w' = phi*c = {w_mid:.0f} NOK")
    print(f'  Detaljistprofitt          : {ret_mid:,.0f} NOK'
          f'  (+{(ret_mid-pi_ret_dec)/pi_ret_dec*100:.1f}% vs desentr.)')
    print(f'  Leverandoerprofitt        : {sup_mid:,.0f} NOK'
          f'  (+{(sup_mid-pi_sup_dec)/pi_sup_dec*100:.1f}% vs desentr.)')
    print(f'  Sum kjede                 : {ret_mid + sup_mid:,.0f} NOK')

    results = {
        'q_koordinert': round(float(q_chain), 1),
        'profitt_kjede_integrert': round(float(pi_chain_star), 0),
        'desentralisert_retailer': round(float(pi_ret_dec), 0),
        'desentralisert_supplier': round(float(pi_sup_dec), 0),
        'pareto_phi_min': round(float(phi_min), 4) if phi_min is not None else None,
        'pareto_phi_max': round(float(phi_max), 4) if phi_max is not None else None,
        'valgt_phi': phi_mid,
        'valgt_w_prime': round(float(w_mid), 0),
        'valgt_retailer_profitt': round(float(ret_mid), 0),
        'valgt_supplier_profitt': round(float(sup_mid), 0),
        'kjede_profitt_kontrollsjekk': round(float(ret_mid + sup_mid), 0),
    }

    with open(OUTPUT_DIR / 'step04_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step04_results.json'}")


if __name__ == '__main__':
    main()
