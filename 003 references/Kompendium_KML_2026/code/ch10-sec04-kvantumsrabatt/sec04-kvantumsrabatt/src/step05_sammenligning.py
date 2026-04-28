"""
Steg 5: Sammenligning av all-units og incremental
==================================================
Sammenlign TC-kurver og optimalt Q* for begge discount-modellene. Viser ogsa
breakeven-analyse: ved hvilken rabattgrense lonner det seg aa bestille i neste
intervall?

Output:
 - output/qd_compare.png        : side-om-side TC-kurver
 - output/qd_breakeven.png      : breakeven for all-units ved hoyeste prisbrudd
 - output/qd_compare.json
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_products, build_price_breaks, PALETTE
from step02_basic_eoq import total_cost
from step03_all_units import allunits_optimal
from step04_incremental import (
    cumulative_purchase_cost,
    incremental_optimal,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def tc_allunits_curve(Q_grid: np.ndarray, D: float, K: float, i_rate: float,
                      breaks_sku: pd.DataFrame) -> np.ndarray:
    """Total-kostnadskurven for all-units (valg av c etter Q)."""
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    TC = np.zeros_like(Q_grid)
    for k, q in enumerate(Q_grid):
        # finn intervallet q faller i
        c = sub['pris'].iloc[0]
        for _, row in sub.iterrows():
            if q >= row['q_min']:
                c = row['pris']
        h = i_rate * c
        TC[k] = total_cost(q, D, K, h, c)
    return TC


def tc_incremental_curve(Q_grid: np.ndarray, D: float, K: float, i_rate: float,
                         breaks_sku: pd.DataFrame) -> np.ndarray:
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    TC = np.zeros_like(Q_grid)
    for k, q in enumerate(Q_grid):
        A = cumulative_purchase_cost(q, sub)
        c_avg = A / q
        h = i_rate * c_avg
        TC[k] = A * D / q + D * K / q + 0.5 * q * h
    return TC


def plot_compare(sku: str, D: float, K: float, i_rate: float,
                 breaks_sku: pd.DataFrame, path: Path) -> None:
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    q_max_break = sub['q_min'].iloc[-1]
    Q_grid = np.linspace(1, max(3.0 * q_max_break, 800), 2000)

    TC_all = tc_allunits_curve(Q_grid, D, K, i_rate, sub)
    TC_inc = tc_incremental_curve(Q_grid, D, K, i_rate, sub)

    fig, ax = plt.subplots(figsize=(9.5, 5.2))

    ax.plot(Q_grid, TC_all, color=PALETTE['s1d'], linewidth=2.3,
            label='All-units $TC_{\\mathrm{au}}(Q)$')
    ax.plot(Q_grid, TC_inc, color=PALETTE['s4d'], linewidth=2.3,
            label='Incremental $TC_{\\mathrm{inc}}(Q)$')

    # Marker prisbrudd
    for j in range(1, len(sub)):
        q_br = sub['q_min'].iloc[j]
        ax.axvline(q_br, color='gray', linestyle=':', alpha=0.5)

    # Marker optimum for hver modell
    res_au = allunits_optimal(D, K, i_rate, sub)
    res_in = incremental_optimal(D, K, i_rate, sub)
    ax.plot(res_au['Q_star'], res_au['TC_star'], '*',
            color=PALETTE['s1d'], markersize=20, markeredgecolor='black',
            zorder=6, label=f"All-units $Q^*={res_au['Q_star']:,.0f}$")
    ax.plot(res_in['Q_star'], res_in['TC_star'], '*',
            color=PALETTE['s4d'], markersize=20, markeredgecolor='black',
            zorder=6, label=f"Incremental $Q^*={res_in['Q_star']:,.0f}$")

    ax.set_xlabel('Bestillingsmengde $Q$', fontsize=11)
    ax.set_ylabel('Total arlig kostnad (NOK)', fontsize=11)
    ax.set_title(f'Sammenligning all-units vs incremental ({sku})',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    ax.tick_params(axis='both', labelsize=9)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {path}")


def plot_breakeven(sku: str, D: float, K: float, i_rate: float,
                   breaks_sku: pd.DataFrame, path: Path) -> None:
    """Breakeven-analyse for all-units:

    Gitt at EOQ i et lavt prisintervall er < q_prisbrudd, lonner det seg aa
    'hoppe opp' til q_prisbrudd? Plott TC(Q) over en fintmasket grid og
    marker breakeven-punktet der TC(Q*_EOQ_low) = TC(q_break).
    """
    from step02_basic_eoq import eoq

    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    # Bruk intervall 1 og 2: sammenlign EOQ i intervall 1 med hjornelosning
    # (q_break) paa intervall 2.
    c1 = sub['pris'].iloc[0]
    c2 = sub['pris'].iloc[1]
    q_break = sub['q_min'].iloc[1]
    h1 = i_rate * c1
    h2 = i_rate * c2
    Q1 = eoq(D, K, h1)
    TC1 = total_cost(Q1, D, K, h1, c1)

    # Loser: finn Q saa TC2(Q) = TC1 (med Q > q_break)
    from scipy.optimize import brentq

    def g(q: float) -> float:
        return total_cost(q, D, K, h2, c2) - TC1

    # TC2 ved q_break
    TC2_break = total_cost(q_break, D, K, h2, c2)

    fig, ax = plt.subplots(figsize=(9.5, 5.2))

    Q_grid = np.linspace(1, 3.0 * q_break, 2000)
    ax.plot(Q_grid, [total_cost(q, D, K, h1, c1) for q in Q_grid],
            color=PALETTE['s1d'], linewidth=2.2,
            label=f'Intervall 1 ($c_1={c1:g}$)')
    ax.plot(Q_grid, [total_cost(q, D, K, h2, c2) for q in Q_grid],
            color=PALETTE['s2d'], linewidth=2.2,
            label=f'Intervall 2 ($c_2={c2:g}$)')

    ax.axhline(TC1, color='gray', linestyle='--', alpha=0.6,
               label=f'$TC(Q^*_1)={TC1:,.0f}$')
    ax.axvline(q_break, color=PALETTE['s3d'], linestyle=':',
               label=f'Prisbrudd $q_2={q_break}$')

    ax.plot(Q1, TC1, 'o', color=PALETTE['s1d'], markersize=9,
            markeredgecolor='black', zorder=5)
    ax.plot(q_break, TC2_break, 'o', color=PALETTE['s2d'], markersize=9,
            markeredgecolor='black', zorder=5)

    # Breakeven-punkt: der TC2(Q) = TC1, altsaa Q_be > q_break
    try:
        Q_be = brentq(g, q_break, Q_grid[-1])
        ax.plot(Q_be, TC1, 's', color='gold', markersize=12,
                markeredgecolor='black', zorder=6,
                label=f'Breakeven $Q_{{be}}={Q_be:,.0f}$')
    except Exception:
        Q_be = None

    if TC2_break < TC1:
        decision = 'LONNSOMT aa hoppe til intervall 2'
    else:
        decision = 'IKKE lonnsomt aa hoppe'
    ax.set_title(f'Breakeven-analyse ({sku}): {decision}',
                 fontsize=11, fontweight='bold')
    ax.set_xlabel('Bestillingsmengde $Q$', fontsize=11)
    ax.set_ylabel('Total arlig kostnad (NOK)', fontsize=11)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9)
    ax.tick_params(axis='both', labelsize=9)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    products = build_products()
    breaks = build_price_breaks()

    summary = {}
    for _, p in products.iterrows():
        sku = p['sku']
        bsub = breaks[breaks['sku'] == sku]
        res_au = allunits_optimal(p['D'], p['K'], p['i'], bsub)
        res_in = incremental_optimal(p['D'], p['K'], p['i'], bsub)
        summary[sku] = {
            'allunits': {
                'Q_star': round(res_au['Q_star'], 1),
                'TC_star': round(res_au['TC_star'], 0),
                'c': res_au['c_star'],
                'interval': res_au['j_star'] + 1,
            },
            'incremental': {
                'Q_star': round(res_in['Q_star'], 1),
                'TC_star': round(res_in['TC_star'], 0),
                'c_avg': round(res_in['c_avg_star'], 3),
                'interval': res_in['j_star'] + 1,
            },
            'diff_TC': round(res_in['TC_star'] - res_au['TC_star'], 0),
        }

    print("--- Sammenligning (all-units vs incremental) ---")
    for sku, d in summary.items():
        print(f"{sku}: AU Q*={d['allunits']['Q_star']:>8.1f}  "
              f"TC={d['allunits']['TC_star']:>12.0f}   "
              f"INC Q*={d['incremental']['Q_star']:>8.1f}  "
              f"TC={d['incremental']['TC_star']:>12.0f}   "
              f"diff={d['diff_TC']:>10.0f}")

    with open(OUTPUT_DIR / 'qd_compare.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Figurer: bruk A1
    p = products[products['sku'] == 'A1'].iloc[0]
    plot_compare('A1', p['D'], p['K'], p['i'], breaks[breaks['sku'] == 'A1'],
                 OUTPUT_DIR / 'qd_compare.png')
    plot_breakeven('A1', p['D'], p['K'], p['i'], breaks[breaks['sku'] == 'A1'],
                   OUTPUT_DIR / 'qd_breakeven.png')


if __name__ == '__main__':
    main()
