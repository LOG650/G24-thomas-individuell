"""
Steg 4: Incremental (marginal) kvantumsrabatt
=============================================
Under incremental-ordninga gjelder lav pris bare for enhetene *over* hver
grense. Total varekost blir en stykkevis lineaer, voksende funksjon A(Q) der
pendenten innenfor intervall j er c_j.

Gjennomsnittlig enhetspris er:
    c_avg(Q) = A(Q) / Q.

Total arlig kostnad:
    TC_inc(Q) = A(Q) * D / Q + (D / Q) * K + (Q / 2) * h_inc(Q),
der vi setter h_inc(Q) = i * c_avg(Q) (standard lerebokkonvensjon).

For hvert intervall j kan vi losse:
    dTC/dQ = 0  ==>  Q_j^* = sqrt( 2 D (K + F_j) / (i * c_j) ),
der F_j = A(q_min_j) - c_j * q_min_j er den "faste" delen som baeres med inn
i intervallet. For j = 1 er F_1 = 0. Se Silver et al. (2017) kap. 5.

Output:
 - output/qd_incremental_table.csv
 - output/qd_incremental_cost.png
 - output/qd_incremental.json
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_products, build_price_breaks, PALETTE

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def cumulative_purchase_cost(Q: float, breaks_sku: pd.DataFrame) -> float:
    """A(Q): kumulativ varekost for Q enheter under incremental-ordning."""
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    total = 0.0
    q_left = Q
    for j, row in sub.iterrows():
        q_lo = row['q_min']
        q_hi = row['q_max'] if pd.notna(row['q_max']) else np.inf
        width = q_hi - q_lo
        if q_left <= 0:
            break
        take = min(q_left, width)
        total += take * row['pris']
        q_left -= take
    return float(total)


def fixed_part_F(j: int, breaks_sku: pd.DataFrame) -> float:
    """F_j = A(q_min_j) - c_j * q_min_j.

    Den 'faste kostnaden' som er akkumulert naar vi er pa grensa til intervall j.
    """
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    q_j = sub['q_min'].iloc[j]
    if j == 0:
        return 0.0
    A_at = cumulative_purchase_cost(q_j, sub)
    c_j = sub['pris'].iloc[j]
    return float(A_at - c_j * q_j)


def incremental_optimal(D: float, K: float, i_rate: float,
                        breaks_sku: pd.DataFrame) -> dict:
    """Incremental optimalisering.

    For hvert intervall j:
      Q_j = sqrt( 2 D (K + F_j) / (i * c_j) ).
    Pa grunn av konveksitet er kandidaten feasible dersom q_min_j <= Q_j < q_max_j.
    Ellers setter vi kandidaten til nermeste tillatte grense.
    """
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    candidates = []
    for j, row in sub.iterrows():
        c_j = row['pris']
        F_j = fixed_part_F(j, sub)
        q_lo = row['q_min']
        q_hi = row['q_max'] if pd.notna(row['q_max']) else np.inf

        Q_unc = float(np.sqrt(2.0 * D * (K + F_j) / (i_rate * c_j)))
        if Q_unc < q_lo:
            Q = q_lo
            status = 'corner_low'
        elif Q_unc > q_hi:
            Q = q_hi
            status = 'corner_high'
        else:
            Q = Q_unc
            status = 'interior'

        # Total arlig kostnad for incremental
        A = cumulative_purchase_cost(Q, sub)
        c_avg = A / Q if Q > 0 else 0.0
        h = i_rate * c_avg
        TC = A * D / Q + D * K / Q + 0.5 * Q * h

        candidates.append({
            'j': j + 1,
            'q_min': int(q_lo),
            'q_max': None if np.isinf(q_hi) else int(q_hi),
            'c_j': c_j,
            'F_j': F_j,
            'Q_unc': Q_unc,
            'Q_use': Q,
            'c_avg': c_avg,
            'h': h,
            'TC': TC,
            'status': status,
        })

    tc = [cand['TC'] for cand in candidates]
    j_star = int(np.argmin(tc))
    return {
        'candidates': candidates,
        'j_star': j_star,
        'Q_star': candidates[j_star]['Q_use'],
        'TC_star': candidates[j_star]['TC'],
        'c_avg_star': candidates[j_star]['c_avg'],
    }


def plot_incremental_cost(sku: str, D: float, K: float, i_rate: float,
                          breaks_sku: pd.DataFrame, path: Path,
                          title: str) -> None:
    """Tegn kontinuerlig TC_inc(Q) for incremental-ordninga.

    Incremental-TC er glatt (ikke sagtann) fordi A(Q) er stykkevis lineaer og
    kontinuerlig.
    """
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    q_max_break = sub['q_min'].iloc[-1]
    Q_grid = np.linspace(1, max(3.0 * q_max_break, 800), 3000)

    fig, ax = plt.subplots(figsize=(9, 5.2))

    TC_vals = []
    for q in Q_grid:
        A = cumulative_purchase_cost(q, sub)
        c_avg = A / q
        h = i_rate * c_avg
        TC_vals.append(A * D / q + D * K / q + 0.5 * q * h)
    TC_vals = np.array(TC_vals)

    ax.plot(Q_grid, TC_vals, color=PALETTE['s4d'], linewidth=2.4,
            label='$TC_{\\mathrm{inc}}(Q)$')

    # Marker prisbruddene som vertikale linjer
    for j in range(1, len(sub)):
        q_br = sub['q_min'].iloc[j]
        ax.axvline(q_br, color='gray', linestyle=':', alpha=0.5)
        ax.text(q_br, ax.get_ylim()[0] if False else max(TC_vals) * 0.98,
                f'$q_{j+1}={q_br}$', rotation=90, va='top', fontsize=8,
                color='gray')

    # Marker kandidater
    result = incremental_optimal(D, K, i_rate, breaks_sku)
    for cand in result['candidates']:
        ax.plot(cand['Q_use'], cand['TC'], 'o', markersize=9,
                markerfacecolor=PALETTE['s3'], markeredgecolor='black', zorder=4)

    j_star = result['j_star']
    star_Q = result['candidates'][j_star]['Q_use']
    star_TC = result['candidates'][j_star]['TC']
    ax.plot(star_Q, star_TC, '*', color='gold', markersize=22,
            markeredgecolor='black', zorder=5,
            label=f'Optimum: $Q^* = {star_Q:,.0f}$')

    ax.set_xlabel('Bestillingsmengde $Q$', fontsize=11)
    ax.set_ylabel('Total arlig kostnad $TC_{\\mathrm{inc}}(Q)$ (NOK)', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='best', fontsize=10)
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
        res = incremental_optimal(p['D'], p['K'], p['i'], bsub)
        summary[sku] = {
            'j_star': res['j_star'] + 1,
            'Q_star': round(res['Q_star'], 1),
            'c_avg_star': round(res['c_avg_star'], 3),
            'TC_star': round(res['TC_star'], 0),
            'candidates': [
                {
                    'interval': cand['j'],
                    'q_min': cand['q_min'],
                    'q_max': cand['q_max'],
                    'c_j': cand['c_j'],
                    'F_j': round(cand['F_j'], 1),
                    'Q_unc': round(cand['Q_unc'], 1),
                    'Q_use': round(cand['Q_use'], 1),
                    'c_avg': round(cand['c_avg'], 3),
                    'TC': round(cand['TC'], 0),
                    'status': cand['status'],
                }
                for cand in res['candidates']
            ],
        }
        for cand in res['candidates']:
            all_rows.append({
                'sku': sku,
                **cand,
                'optimal': (cand['j'] - 1) == res['j_star'],
            })

    df = pd.DataFrame(all_rows)
    df.to_csv(OUTPUT_DIR / 'qd_incremental_table.csv', index=False)

    print("\n--- Incremental resultater ---")
    pd.set_option('display.float_format', lambda v: f'{v:,.2f}')
    print(df.to_string(index=False))

    with open(OUTPUT_DIR / 'qd_incremental.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag: {OUTPUT_DIR / 'qd_incremental.json'}")

    # Plott for A1
    p = products[products['sku'] == 'A1'].iloc[0]
    plot_incremental_cost(
        'A1', p['D'], p['K'], p['i'], breaks[breaks['sku'] == 'A1'],
        OUTPUT_DIR / 'qd_incremental_cost.png',
        'Incremental: total arlig kostnad $TC_{\\mathrm{inc}}(Q)$ for A1',
    )


if __name__ == '__main__':
    main()
