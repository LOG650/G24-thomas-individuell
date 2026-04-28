"""
Steg 1: Datainnsamling
======================
Definerer produktkatalogen med etterspørsel, bestillings- og lagerkostnader,
samt kvantumsrabatt-strukturen (prisbrudd) fra leverandøren. Datasettet er
syntetisk, men kalibrert mot realistiske parametre for norsk engrossalg.

Output:
 - data/products.csv          : hovedprodukter med D, K, h-rate
 - data/price_breaks.csv      : prisbrudd per produkt (q_min, q_max, pris)
 - output/qd_price_schedule.png
 - output/qd_products.json
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Farger fra bokens infografikk-palett (s1, s2, s3, s4, s5)
PALETTE = {
    's1': '#8CC8E5', 's1d': '#1F6587',
    's2': '#97D4B7', 's2d': '#307453',
    's3': '#F6BA7C', 's3d': '#9C540B',
    's4': '#BD94D7', 's4d': '#5A2C77',
    's5': '#ED9F9E', 's5d': '#961D1C',
}


def build_products() -> pd.DataFrame:
    """Definer fire produkter for en norsk engrosgrossist.

    Felter:
      - sku, navn
      - D   : arlig ettersporsel (enheter/ar)
      - K   : bestillingskostnad per ordre (NOK)
      - i   : lagerholdsrente (andel av varekostnad per ar)
    """
    rows = [
        dict(sku='A1', navn='Elektrisk handverktoy', D=2400,  K=400, i=0.22),
        dict(sku='B2', navn='Sikkerhetshansker',    D=12000, K=250, i=0.18),
        dict(sku='C3', navn='Smorefett (5 kg)',     D=1800,  K=350, i=0.25),
        dict(sku='D4', navn='LED-lyspaere 9 W',    D=9000,  K=300, i=0.20),
    ]
    return pd.DataFrame(rows)


def build_price_breaks() -> pd.DataFrame:
    """Leverandorens prisbrudd per sku. Allerede sortert pa q_min."""
    # (sku, q_min, q_max, pris_per_enhet)
    rows = [
        # A1: Elektrisk handverktoy
        ('A1',   0,   99, 850.0),
        ('A1', 100,  499, 810.0),
        ('A1', 500, None, 770.0),
        # B2: Sikkerhetshansker
        ('B2',   0,  199, 42.0),
        ('B2', 200,  999, 39.0),
        ('B2', 1000, None, 36.5),
        # C3: Smorefett (5 kg)
        ('C3',   0,   49, 320.0),
        ('C3',  50,  199, 300.0),
        ('C3', 200, None, 285.0),
        # D4: LED-lyspaere 9 W
        ('D4',   0,  299, 55.0),
        ('D4', 300,  999, 51.0),
        ('D4', 1000, None, 48.0),
    ]
    df = pd.DataFrame(rows, columns=['sku', 'q_min', 'q_max', 'pris'])
    return df


def plot_price_schedule(products: pd.DataFrame, breaks: pd.DataFrame, path: Path) -> None:
    """Plot kvantumsrabatt-strukturen for alle produkter."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    colors = [PALETTE['s1d'], PALETTE['s2d'], PALETTE['s3d'], PALETTE['s4d']]

    for ax, (_, prod), color in zip(axes.flat, products.iterrows(), colors):
        sub = breaks[breaks['sku'] == prod['sku']].reset_index(drop=True)
        # Tegn horisontale prislinjer per intervall
        q_max_plot = 1.25 * sub['q_min'].iloc[-1] if sub['q_min'].iloc[-1] > 0 else 1500
        q_max_plot = max(q_max_plot, 1.5 * sub['q_min'].iloc[-1])

        for j, row in sub.iterrows():
            q_lo = row['q_min']
            q_hi = row['q_max'] if pd.notna(row['q_max']) else q_max_plot
            ax.hlines(row['pris'], q_lo, q_hi, colors=color, linewidth=2.5,
                      label=f"Intervall {j+1}")
            # marker prisbrudd
            if j > 0:
                ax.plot(q_lo, row['pris'], 'o', color=color, markersize=6)
                # stiplet loddrett linje som viser hoppet
                prev_price = sub['pris'].iloc[j - 1]
                ax.vlines(q_lo, row['pris'], prev_price, colors=color,
                          linestyles=':', alpha=0.5)

        ax.set_title(f"{prod['sku']}: {prod['navn']}", fontsize=10, fontweight='bold')
        ax.set_xlabel('Bestillingsmengde $Q$ (enheter)', fontsize=9)
        ax.set_ylabel('Enhetspris $c(Q)$ (NOK)', fontsize=9)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='both', labelsize=8)
        ax.set_xlim(left=0, right=q_max_plot)

    fig.suptitle('Leverandorens prisskjema: enhetspris som funksjon av Q',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    products = build_products()
    breaks = build_price_breaks()

    # Lagre kildedata
    products.to_csv(DATA_DIR / 'products.csv', index=False)
    breaks.to_csv(DATA_DIR / 'price_breaks.csv', index=False)
    print(f"Produktdata lagret: {DATA_DIR / 'products.csv'}")
    print(f"Prisbrudd lagret:   {DATA_DIR / 'price_breaks.csv'}")

    print("\n--- Produkter ---")
    print(products.to_string(index=False))
    print("\n--- Prisbrudd ---")
    print(breaks.to_string(index=False))

    # Oppsummering til JSON
    summary = {
        'n_products': int(len(products)),
        'products': products.to_dict(orient='records'),
        'price_breaks': [
            {
                'sku': r.sku,
                'q_min': int(r.q_min),
                'q_max': None if pd.isna(r.q_max) else int(r.q_max),
                'pris': float(r.pris),
            }
            for r in breaks.itertuples(index=False)
        ],
    }
    with open(OUTPUT_DIR / 'qd_products.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag: {OUTPUT_DIR / 'qd_products.json'}")

    plot_price_schedule(products, breaks, OUTPUT_DIR / 'qd_price_schedule.png')


if __name__ == '__main__':
    main()
