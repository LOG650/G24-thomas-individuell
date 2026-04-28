"""
Steg 3: All-units kvantumsrabatt
================================
Implementerer all-units-algoritmen:

For hvert prisintervall [q_j, q_{j+1}) med enhetspris c_j:
  1) beregn EOQ_j = sqrt(2 D K / h_j), der h_j = i * c_j,
  2) test feasibility: er EOQ_j i intervallet?
     - hvis ja, setter Q_j = EOQ_j (kandidat)
     - hvis EOQ_j < q_j, setter Q_j = q_j (hjornelosning)
     - hvis EOQ_j >= q_{j+1}, er intervallet inaktivt (EOQ ligger over; bruk
       q_{j+1} kun hvis neste intervall gir hoyere kostnad)
  3) regn TC_j(Q_j) og velg j* som minimerer TC.

Output:
 - output/qd_allunits_table.csv
 - output/qd_allunits_cost.png
 - output/qd_allunits.json
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_products, build_price_breaks, PALETTE
from step02_basic_eoq import eoq, total_cost

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def allunits_optimal(D: float, K: float, i_rate: float,
                     breaks_sku: pd.DataFrame) -> dict:
    """All-units optimalisering for en enkelt sku.

    Algoritme (standard lerebok, Silver et al. 2017):
      1) For hvert intervall j, beregn EOQ_j med c_j.
      2) Dersom EOQ_j er feasible (q_min_j <= EOQ_j <= q_max_j), er Q_j = EOQ_j.
         Ellers: dersom EOQ_j < q_min_j, setter Q_j = q_min_j. Dersom EOQ_j > q_max_j
         (kun mulig for hoyeste intervall, som har uendelig overgrense), finnes ikke.
      3) Beregn TC for hver kandidat og velg minimum.
    """
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    candidates = []
    for _, row in sub.iterrows():
        c = row['pris']
        h = i_rate * c
        Q_eoq = eoq(D, K, h)
        q_lo = row['q_min']
        q_hi = row['q_max'] if pd.notna(row['q_max']) else np.inf

        if Q_eoq < q_lo:
            Q = q_lo
            status = 'corner_low'
        elif Q_eoq > q_hi:
            Q = None
            status = 'infeasible'
        else:
            Q = Q_eoq
            status = 'eoq_interior'

        if Q is None:
            TC = np.inf
        else:
            TC = total_cost(Q, D, K, h, c)

        candidates.append({
            'q_min': int(q_lo),
            'q_max': None if np.isinf(q_hi) else int(q_hi),
            'pris': c,
            'h': h,
            'Q_eoq': Q_eoq,
            'Q_use': Q,
            'TC': TC,
            'status': status,
        })

    tc_list = [cand['TC'] for cand in candidates]
    j_star = int(np.argmin(tc_list))
    return {
        'candidates': candidates,
        'j_star': j_star,
        'Q_star': candidates[j_star]['Q_use'],
        'TC_star': candidates[j_star]['TC'],
        'c_star': candidates[j_star]['pris'],
    }


def plot_total_cost_curve(sku: str, D: float, K: float, i_rate: float,
                          breaks_sku: pd.DataFrame, path: Path,
                          title: str) -> None:
    """Tegn total-kostnadskurven for all-units-strukturen (sagtannprofil)."""
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    q_max_break = sub['q_min'].iloc[-1]
    Q_grid = np.linspace(1, max(3.0 * q_max_break, 800), 3000)

    fig, ax = plt.subplots(figsize=(9, 5.2))

    # Kontinuerlig TC-kurve per intervall (for visualisering)
    palette_light = [PALETTE['s1'], PALETTE['s2'], PALETTE['s3']]
    palette_dark = [PALETTE['s1d'], PALETTE['s2d'], PALETTE['s3d']]

    for j, row in sub.iterrows():
        c = row['pris']
        h = i_rate * c
        q_lo = row['q_min']
        q_hi = row['q_max'] if pd.notna(row['q_max']) else Q_grid[-1]
        # aktiv region
        mask = (Q_grid >= max(q_lo, 1)) & (Q_grid <= q_hi)
        ax.plot(Q_grid[mask], [total_cost(q, D, K, h, c) for q in Q_grid[mask]],
                color=palette_dark[j % len(palette_dark)], linewidth=2.3,
                label=f'Intervall {j + 1}: $c = {c:g}$ NOK')

        # stiplet "hva om intervallet fortsatte"
        mask_ext = (Q_grid >= 1) & ((Q_grid < q_lo) | (Q_grid > q_hi))
        ax.plot(Q_grid[mask_ext],
                [total_cost(q, D, K, h, c) for q in Q_grid[mask_ext]],
                color=palette_dark[j % len(palette_dark)], linewidth=1.0,
                linestyle=':', alpha=0.5)

    # Marker EOQ-kandidatene
    result = allunits_optimal(D, K, i_rate, breaks_sku)
    for j, cand in enumerate(result['candidates']):
        if cand['Q_use'] is None:
            continue
        color = palette_dark[j % len(palette_dark)]
        ax.plot(cand['Q_use'], cand['TC'], 'o', color=color, markersize=10,
                markeredgecolor='black', zorder=5)

    # Marker optimalt valg
    j_star = result['j_star']
    star_Q = result['candidates'][j_star]['Q_use']
    star_TC = result['candidates'][j_star]['TC']
    ax.plot(star_Q, star_TC, '*', color='gold', markersize=22,
            markeredgecolor='black', zorder=6,
            label=f'Optimum: $Q^* = {star_Q:,.0f}$')

    ax.set_xlabel('Bestillingsmengde $Q$', fontsize=11)
    ax.set_ylabel('Total arlig kostnad $TC(Q)$ (NOK)', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=9)
    ax.tick_params(axis='both', labelsize=9)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    products = build_products()
    breaks = build_price_breaks()

    all_rows = []
    summary = {}
    for _, p in products.iterrows():
        sku = p['sku']
        bsub = breaks[breaks['sku'] == sku]
        res = allunits_optimal(p['D'], p['K'], p['i'], bsub)
        summary[sku] = {
            'j_star': res['j_star'] + 1,
            'Q_star': round(res['Q_star'], 1),
            'c_star': res['c_star'],
            'TC_star': round(res['TC_star'], 0),
            'candidates': [
                {
                    'interval': ci + 1,
                    'q_min': cand['q_min'],
                    'q_max': cand['q_max'],
                    'pris': cand['pris'],
                    'Q_eoq': round(cand['Q_eoq'], 1),
                    'Q_use': None if cand['Q_use'] is None else round(cand['Q_use'], 1),
                    'TC': None if np.isinf(cand['TC']) else round(cand['TC'], 0),
                    'status': cand['status'],
                }
                for ci, cand in enumerate(res['candidates'])
            ],
        }
        for ci, cand in enumerate(res['candidates']):
            all_rows.append({
                'sku': sku,
                'interval': ci + 1,
                'q_min': cand['q_min'],
                'q_max': cand['q_max'],
                'pris': cand['pris'],
                'h': cand['h'],
                'Q_eoq': cand['Q_eoq'],
                'Q_use': cand['Q_use'],
                'TC': cand['TC'],
                'status': cand['status'],
                'optimal': ci == res['j_star'],
            })

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_DIR / 'qd_allunits_table.csv', index=False)

    print("\n--- All-units resultater ---")
    pd.set_option('display.float_format', lambda v: f'{v:,.2f}')
    print(df.to_string(index=False))

    with open(OUTPUT_DIR / 'qd_allunits.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag: {OUTPUT_DIR / 'qd_allunits.json'}")

    # Plott for produkt A1 som eksempel i lereboken
    p = products[products['sku'] == 'A1'].iloc[0]
    plot_total_cost_curve(
        'A1', p['D'], p['K'], p['i'], breaks[breaks['sku'] == 'A1'],
        OUTPUT_DIR / 'qd_allunits_cost.png',
        'All-units: total arlig kostnad $TC(Q)$ for A1',
    )


if __name__ == '__main__':
    main()
