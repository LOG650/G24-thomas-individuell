"""
Steg 1: Datainnsamling for disposisjonsbeslutning
==================================================
Genererer syntetisk datasett med 800 returnerte elektronikkenheter
fra en norsk returhandlingssentral. Hvert produkt har tilstandsscore,
alder, merke og kosmetisk/funksjonell vurdering.

Dataene lagres i output/returned_units.csv for gjenbruk i senere steg.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

RNG_SEED = 20260420
N_UNITS = 800

BRANDS = ['NordicTech', 'ElektroNor', 'ViksTek', 'FjordLine']
BRAND_WEIGHTS = [0.38, 0.27, 0.22, 0.13]

# Pris-nivå (verdi ny) per merke i NOK
BRAND_BASE_PRICE = {
    'NordicTech': 6200.0,
    'ElektroNor': 4800.0,
    'ViksTek': 3600.0,
    'FjordLine': 2400.0,
}


def generate_returns(n: int = N_UNITS, seed: int = RNG_SEED) -> pd.DataFrame:
    """Generer syntetisk returdata.

    Tilstandsscore 1-5 (1=ubrukelig, 5=tilnærmet ny). Alder i måneder.
    Kosmetisk og funksjonell grad korrelerer med tilstanden, men med støy.
    """
    rng = np.random.default_rng(seed)

    # Tilstandsscore er skjev mot middels (3) -- realistisk fordeling
    # i en returhåndteringssentral som tar inn både nyreturer og brukte
    # gjenvinningsvarer.
    condition_probs = [0.10, 0.22, 0.34, 0.22, 0.12]
    condition = rng.choice([1, 2, 3, 4, 5], size=n, p=condition_probs)

    # Alder (måneder) korrelerer med tilstand -- eldre varer har lavere score
    age_mean = 36 - 5 * condition  # forventet alder i måneder
    age = np.clip(rng.normal(age_mean, 6.0), 0, 60).astype(int)

    brand = rng.choice(BRANDS, size=n, p=BRAND_WEIGHTS)

    # Kosmetisk grad (1-5) avhenger delvis av tilstand + støy
    cosmetic = np.clip(
        np.round(condition + rng.normal(0, 0.7, size=n)).astype(int), 1, 5
    )
    # Funksjonell grad (1-5) avhenger enda sterkere av tilstand
    functional = np.clip(
        np.round(condition + rng.normal(0, 0.5, size=n)).astype(int), 1, 5
    )

    df = pd.DataFrame({
        'unit_id': np.arange(1, n + 1),
        'condition': condition,
        'age_months': age,
        'brand': brand,
        'cosmetic_grade': cosmetic,
        'functional_grade': functional,
        'new_price_nok': [BRAND_BASE_PRICE[b] for b in brand],
    })
    return df


def plot_condition_histogram(df: pd.DataFrame, output_path: Path) -> None:
    """Histogram over tilstandsscore stablet per merke."""
    fig, ax = plt.subplots(figsize=(9, 4.8))

    colors = {
        'NordicTech': '#8CC8E5',
        'ElektroNor': '#97D4B7',
        'ViksTek': '#F6BA7C',
        'FjordLine': '#BD94D7',
    }
    edge_colors = {
        'NordicTech': '#1F6587',
        'ElektroNor': '#307453',
        'ViksTek': '#9C540B',
        'FjordLine': '#5A2C77',
    }

    bottom = np.zeros(5)
    x = np.arange(1, 6)
    for brand in BRANDS:
        counts = np.array([
            int(((df['brand'] == brand) & (df['condition'] == c)).sum())
            for c in x
        ])
        ax.bar(
            x, counts, bottom=bottom,
            color=colors[brand], edgecolor=edge_colors[brand],
            linewidth=1.2, label=brand,
        )
        bottom += counts

    ax.set_xlabel('Tilstandsscore $c$', fontsize=14)
    ax.set_ylabel('Antall enheter', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels(['1\n(ubrukelig)', '2', '3\n(middels)', '4', '5\n(tilnærmet ny)'])
    ax.set_title('Fordeling av tilstandsscore per merke',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def compute_summary(df: pd.DataFrame) -> dict:
    """Beregn oppsummeringsstatistikk."""
    summary = {
        'antall_enheter': int(len(df)),
        'antall_merker': int(df['brand'].nunique()),
        'gjennomsnittlig_tilstand': round(float(df['condition'].mean()), 2),
        'median_tilstand': int(df['condition'].median()),
        'gjennomsnittlig_alder_mnd': round(float(df['age_months'].mean()), 1),
        'gjennomsnittlig_nypris_nok': round(float(df['new_price_nok'].mean()), 0),
        'tilstandsfordeling': {
            int(c): int((df['condition'] == c).sum()) for c in range(1, 6)
        },
        'merkefordeling': {
            str(b): int((df['brand'] == b).sum()) for b in BRANDS
        },
    }
    return summary


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 1: DATAINNSAMLING")
    print(f"{'='*60}")

    df = generate_returns()
    print(f"\nGenerert {len(df)} returenheter.")
    print(df.head())

    csv_path = DATA_DIR / 'returned_units.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nData lagret: {csv_path}")

    summary = compute_summary(df)
    print("\n--- Oppsummering ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    with open(OUTPUT_DIR / 'step01_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_condition_histogram(df, OUTPUT_DIR / 'disp_condition_hist.png')


if __name__ == '__main__':
    main()
