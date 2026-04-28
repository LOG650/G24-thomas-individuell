"""
Steg 5: Sensitivitet
====================
Variasjon i bestillingsmengde og effektivitet som funksjon av
  (a) etterspoerselsvariasjon sigma,
  (b) kostnadsstruktur w/c-marg,
  (c) kontraktsparameter phi i revenue-sharing.

Viser at koordineringsgapet oeker med variansen, samt hvordan phi
fordeler gevinsten mellom detaljist og leverandoer.
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
from step04_revenue_sharing import (
    rs_retailer_profit, rs_supplier_profit, coordinated_wholesale
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def plot_sensitivity(output_path: Path) -> dict:
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    # ---- (a) effektivitet vs sigma ----
    sigmas = np.linspace(50, 500, 60)
    eff = np.zeros_like(sigmas)
    q_gap = np.zeros_like(sigmas)
    for i, sig in enumerate(sigmas):
        q_c = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                        MU_DEMAND, sig)
        q_r = optimal_q_retailer(PRICE_RETAIL, WHOLESALE_PRICE, SALVAGE_VALUE,
                                 MU_DEMAND, sig)
        pi_c = expected_chain_profit(q_c, PRICE_RETAIL, COST_SUPPLIER,
                                     SALVAGE_VALUE, MU_DEMAND, sig)
        pi_r_dec = retailer_profit(q_r, PRICE_RETAIL, WHOLESALE_PRICE,
                                   SALVAGE_VALUE, MU_DEMAND, sig)
        pi_s_dec = supplier_profit(q_r, WHOLESALE_PRICE, COST_SUPPLIER)
        eff[i] = (pi_r_dec + pi_s_dec) / pi_c
        q_gap[i] = q_c - q_r

    ax = axes[0]
    ax.plot(sigmas, eff * 100, color='#1F6587', linewidth=2,
            label=r'Effektivitet $\Pi_{dec}/\Pi_{kjede}$')
    ax.axvline(SIGMA_DEMAND, color='#961D1C', linestyle='--', linewidth=1.2,
               label=rf'$\sigma = {SIGMA_DEMAND}$')
    ax.set_xlabel(r'$\sigma$ (etterspoerselsstandardavvik)', fontsize=11)
    ax.set_ylabel('Kjedeeffektivitet (\\%)', fontsize=11)
    ax.set_title('(a) Effektivitet vs variasjon',
                 fontsize=11, fontweight='bold')
    ax.legend(loc='lower left', fontsize=9)
    ax.grid(True, alpha=0.3)

    # ---- (b) Q-gap som funksjon av w ----
    w_range = np.linspace(COST_SUPPLIER + 50, PRICE_RETAIL - 50, 60)
    q_r_w = np.array([optimal_q_retailer(PRICE_RETAIL, w, SALVAGE_VALUE,
                                         MU_DEMAND, SIGMA_DEMAND) for w in w_range])
    q_c_const = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                          MU_DEMAND, SIGMA_DEMAND)

    ax = axes[1]
    ax.plot(w_range, q_r_w, color='#9C540B', linewidth=2,
            label=r'$Q^*_R(w)$')
    ax.axhline(q_c_const, color='#1F6587', linestyle='--', linewidth=1.5,
               label=f'$Q^*_{{kjede}} = {q_c_const:.0f}$')
    ax.axvline(WHOLESALE_PRICE, color='#961D1C', linestyle=':', linewidth=1.2,
               label=rf'$w_0 = {WHOLESALE_PRICE}$')
    ax.set_xlabel('$w$ (engrospris, NOK)', fontsize=11)
    ax.set_ylabel(r'$Q^*_R$', fontsize=11)
    ax.set_title('(b) Detaljistens bestilling vs $w$',
                 fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)

    # ---- (c) profittfordeling under revenue-sharing som funksjon av phi ----
    q_c = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                    MU_DEMAND, SIGMA_DEMAND)
    phis = np.linspace(0.05, 0.95, 91)
    ret_pi = np.zeros_like(phis)
    sup_pi = np.zeros_like(phis)
    for i, phi in enumerate(phis):
        w_p = coordinated_wholesale(phi, COST_SUPPLIER)
        ret_pi[i] = rs_retailer_profit(q_c, phi, PRICE_RETAIL, w_p,
                                       SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
        sup_pi[i] = rs_supplier_profit(q_c, phi, PRICE_RETAIL, w_p,
                                       COST_SUPPLIER, SALVAGE_VALUE,
                                       MU_DEMAND, SIGMA_DEMAND)

    q_r_dec = optimal_q_retailer(PRICE_RETAIL, WHOLESALE_PRICE, SALVAGE_VALUE,
                                 MU_DEMAND, SIGMA_DEMAND)
    pi_ret_dec = retailer_profit(q_r_dec, PRICE_RETAIL, WHOLESALE_PRICE,
                                 SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    pi_sup_dec = supplier_profit(q_r_dec, WHOLESALE_PRICE, COST_SUPPLIER)

    ax = axes[2]
    ax.plot(phis, ret_pi / 1000, color='#9C540B', linewidth=2,
            label=r'Detaljist $\Pi_R(\varphi)$')
    ax.plot(phis, sup_pi / 1000, color='#1F6587', linewidth=2,
            label=r'Leverandoer $\Pi_S(\varphi)$')
    ax.axhline(pi_ret_dec / 1000, color='#9C540B', linestyle=':',
               linewidth=1.2, alpha=0.7,
               label=f'detalj. baseline {pi_ret_dec/1000:.0f}')
    ax.axhline(pi_sup_dec / 1000, color='#1F6587', linestyle=':',
               linewidth=1.2, alpha=0.7,
               label=f'lever. baseline {pi_sup_dec/1000:.0f}')

    pareto_mask = (ret_pi >= pi_ret_dec) & (sup_pi >= pi_sup_dec)
    if pareto_mask.any():
        phi_lo = phis[pareto_mask].min()
        phi_hi = phis[pareto_mask].max()
        ax.axvspan(phi_lo, phi_hi, color='#97D4B7', alpha=0.3,
                   label=rf'pareto-omr. $\varphi \in [{phi_lo:.2f}, {phi_hi:.2f}]$')

    ax.set_xlabel(r'$\varphi$ (detaljistens inntektsandel)', fontsize=11)
    ax.set_ylabel('Forventet profitt (tusen NOK)', fontsize=11)
    ax.set_title(r'(c) Profittfordeling over $\varphi$',
                 fontsize=11, fontweight='bold')
    ax.legend(loc='center right', fontsize=8)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')

    return {
        'pareto_phi_min': round(float(phi_lo), 4) if pareto_mask.any() else None,
        'pareto_phi_max': round(float(phi_hi), 4) if pareto_mask.any() else None,
        'eff_ved_sigma_100': round(float(np.interp(100, sigmas, eff)), 4),
        'eff_ved_sigma_250': round(float(np.interp(250, sigmas, eff)), 4),
        'eff_ved_sigma_500': round(float(np.interp(500, sigmas, eff)), 4),
        'q_gap_ved_sigma_100': round(float(np.interp(100, sigmas, q_gap)), 1),
        'q_gap_ved_sigma_250': round(float(np.interp(250, sigmas, q_gap)), 1),
        'q_gap_ved_sigma_500': round(float(np.interp(500, sigmas, q_gap)), 1),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 5: SENSITIVITET')
    print('=' * 60)

    results = plot_sensitivity(OUTPUT_DIR / 'nv_sensitivity.png')

    print('\nEffektivitet desentralisert vs integrert:')
    print(f"  sigma = 100: {results['eff_ved_sigma_100']*100:.1f}%")
    print(f"  sigma = 250: {results['eff_ved_sigma_250']*100:.1f}%")
    print(f"  sigma = 500: {results['eff_ved_sigma_500']*100:.1f}%")
    print('\nQ-gap (Q_kjede - Q_R):')
    print(f"  sigma = 100: {results['q_gap_ved_sigma_100']:.1f}")
    print(f"  sigma = 250: {results['q_gap_ved_sigma_250']:.1f}")
    print(f"  sigma = 500: {results['q_gap_ved_sigma_500']:.1f}")
    print(f"\nPareto-omraade for phi: "
          f"[{results['pareto_phi_min']}, {results['pareto_phi_max']}]")

    with open(OUTPUT_DIR / 'step05_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step05_results.json'}")


if __name__ == '__main__':
    main()
