"""
Steg 2: Grunnleggende EOQ
=========================
Beregner klassisk EOQ uten kvantumsrabatt for alle produkter. Bruker
referanseprisen (det midterste intervallet) som basis for lagerholdskostnaden.

Total arlig kostnad (uten rabatt):
    TC(Q) = c * D + (D / Q) * K + (Q / 2) * h
der h = i * c.

Grunnleggende EOQ-formel:
    Q* = sqrt(2 D K / h)

Output:
 - output/qd_basic_eoq.json
 - output/qd_basic_eoq.csv
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step01_datainnsamling import build_products, build_price_breaks

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def eoq(D: float, K: float, h: float) -> float:
    """Klassisk EOQ-formel (Harris 1913)."""
    return float(np.sqrt(2.0 * D * K / h))


def total_cost(Q: float, D: float, K: float, h: float, c: float) -> float:
    """Total arlig kostnad: varekost + bestilling + lagerhold."""
    return c * D + (D / Q) * K + (Q / 2.0) * h


def midprice(sku: str, breaks: pd.DataFrame) -> float:
    """Bruk prisen i det midterste intervallet som referansepris."""
    sub = breaks[breaks['sku'] == sku].reset_index(drop=True)
    return float(sub['pris'].iloc[len(sub) // 2])


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    products = build_products()
    breaks = build_price_breaks()

    rows = []
    for _, p in products.iterrows():
        c_ref = midprice(p['sku'], breaks)
        h = p['i'] * c_ref
        Q_star = eoq(p['D'], p['K'], h)
        TC = total_cost(Q_star, p['D'], p['K'], h, c_ref)
        rows.append({
            'sku': p['sku'],
            'D': p['D'],
            'K': p['K'],
            'i': p['i'],
            'c_ref': c_ref,
            'h_ref': h,
            'Q_eoq': Q_star,
            'TC_eoq': TC,
            'n_orders': p['D'] / Q_star,
            'cycle_days': 365 * Q_star / p['D'],
        })

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'qd_basic_eoq.csv', index=False)

    print("--- Klassisk EOQ (uten rabatt) ---")
    pd.set_option('display.float_format', lambda v: f'{v:,.2f}')
    print(df.to_string(index=False))

    summary = {
        'formula': "Q* = sqrt(2 D K / h),  h = i * c_ref",
        'rows': [
            {
                'sku': r['sku'],
                'c_ref': round(r['c_ref'], 2),
                'h_ref': round(r['h_ref'], 2),
                'Q_eoq': round(r['Q_eoq'], 1),
                'TC_eoq': round(r['TC_eoq'], 0),
                'n_orders_per_year': round(r['n_orders'], 2),
                'cycle_days': round(r['cycle_days'], 1),
            }
            for r in rows
        ],
    }
    with open(OUTPUT_DIR / 'qd_basic_eoq.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'qd_basic_eoq.json'}")


if __name__ == '__main__':
    main()
