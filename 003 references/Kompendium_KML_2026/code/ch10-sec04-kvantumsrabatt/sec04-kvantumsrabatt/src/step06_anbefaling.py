"""
Steg 6: Anbefalinger og arlige besparelser
==========================================
Konkret bestillingsanbefaling per produkt, med kvantifisert arlig besparelse
i forhold til naive EOQ uten rabatt og i forhold til aa 'alltid bestille
minste mengde'.

Output:
 - output/qd_anbefalinger.csv
 - output/qd_anbefalinger.json
 - output/qd_method.png              : prosessdiagram (schematisk)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd

from step01_datainnsamling import build_products, build_price_breaks, PALETTE
from step02_basic_eoq import eoq, total_cost, midprice
from step03_all_units import allunits_optimal

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def naive_policy_cost(D: float, K: float, i_rate: float,
                      breaks_sku: pd.DataFrame) -> dict:
    """Naiv: bruk EOQ med hoyeste (forste) pris, ignorer rabatter."""
    sub = breaks_sku.sort_values('q_min').reset_index(drop=True)
    c = sub['pris'].iloc[0]
    h = i_rate * c
    Q = eoq(D, K, h)
    TC = total_cost(Q, D, K, h, c)
    return {'Q': Q, 'TC': TC, 'c': c}


def plot_method(path: Path) -> None:
    """Prosessdiagram for kvantumsrabatt-algoritmen."""
    fig, ax = plt.subplots(figsize=(10.5, 5.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis('off')

    boxes = [
        (0.3, 3.0, 1.8, 1.3, 'Steg 1\nDatainnsamling\n$D, K, i$,\nprisbrudd', PALETTE['s1']),
        (2.4, 3.0, 1.8, 1.3, 'Steg 2\nKlassisk EOQ\n$Q^* = \\sqrt{2DK/h}$', PALETTE['s2']),
        (4.5, 3.0, 1.8, 1.3, 'Steg 3\nAll-units\nEOQ per intervall', PALETTE['s3']),
        (6.6, 3.0, 1.8, 1.3, 'Steg 4\nIncremental\n$Q_j = \\sqrt{2D(K{+}F_j)/h_j}$', PALETTE['s4']),
        (8.7, 3.0, 1.1, 1.3, 'Steg 5\nSammen-\nligning', PALETTE['s5']),
    ]
    for x, y, w, h, txt, color in boxes:
        rect = mpatches.FancyBboxPatch(
            (x, y), w, h, boxstyle='round,pad=0.05', linewidth=1.2,
            edgecolor='black', facecolor=color, alpha=0.85,
        )
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center',
                fontsize=9, fontweight='bold')

    # Piler
    arrow_kw = dict(arrowstyle='->', lw=1.8, color='black')
    for x_start, x_end in [(2.1, 2.4), (4.2, 4.5), (6.3, 6.6), (8.4, 8.7)]:
        ax.annotate('', xy=(x_end, 3.65), xytext=(x_start, 3.65),
                    arrowprops=arrow_kw)

    # Steg 6
    rect6 = mpatches.FancyBboxPatch(
        (3.5, 0.6), 3.0, 1.3, boxstyle='round,pad=0.05', linewidth=1.2,
        edgecolor='black', facecolor=PALETTE['s1d'], alpha=0.85,
    )
    ax.add_patch(rect6)
    ax.text(5.0, 1.25, 'Steg 6\nAnbefaling og\narlige besparelser',
            ha='center', va='center', fontsize=9.5, fontweight='bold',
            color='white')
    ax.annotate('', xy=(5.0, 1.9), xytext=(5.0, 3.0), arrowprops=arrow_kw)

    ax.set_title('Prosess: EOQ med kvantumsrabatt',
                 fontsize=13, fontweight='bold', pad=6)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    products = build_products()
    breaks = build_price_breaks()

    rows = []
    for _, p in products.iterrows():
        sku = p['sku']
        bsub = breaks[breaks['sku'] == sku]
        c_mid = midprice(sku, breaks)

        # 'basis' = klassisk EOQ med hoyeste pris (dvs. uten aa utnytte rabatt)
        naive = naive_policy_cost(p['D'], p['K'], p['i'], bsub)

        # Anbefalt: all-units optimum
        au = allunits_optimal(p['D'], p['K'], p['i'], bsub)

        saving = naive['TC'] - au['TC_star']
        saving_pct = 100.0 * saving / naive['TC']
        annual_volume = p['D']
        cycle_days = 365 * au['Q_star'] / p['D']
        n_orders = p['D'] / au['Q_star']

        rows.append({
            'sku': sku,
            'navn': p['navn'],
            'D': p['D'],
            'Q_anbefalt': round(au['Q_star'], 1),
            'c_oppnadd': au['c_star'],
            'n_orders_per_year': round(n_orders, 2),
            'cycle_days': round(cycle_days, 1),
            'TC_anbefalt': round(au['TC_star'], 0),
            'TC_naiv_uten_rabatt': round(naive['TC'], 0),
            'arlig_besparelse': round(saving, 0),
            'besparelse_pct': round(saving_pct, 2),
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'qd_anbefalinger.csv', index=False)

    print("\n--- Bestillingsanbefalinger (all-units) ---")
    pd.set_option('display.float_format', lambda v: f'{v:,.2f}')
    print(df.to_string(index=False))

    total_saving = df['arlig_besparelse'].sum()
    total_base = df['TC_naiv_uten_rabatt'].sum()

    print(f"\nSum arlig besparelse over alle produkter: "
          f"{total_saving:,.0f} NOK")
    print(f"Relativ besparelse: {100 * total_saving / total_base:.2f}%")

    summary = {
        'anbefalinger': rows,
        'total_saving_nok': float(total_saving),
        'total_base_nok': float(total_base),
        'relative_saving_pct': float(100 * total_saving / total_base),
    }
    with open(OUTPUT_DIR / 'qd_anbefalinger.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Prosessdiagram
    plot_method(OUTPUT_DIR / 'qd_method.png')


if __name__ == '__main__':
    main()
