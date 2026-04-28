"""
Steg 1: Datainnsamling for bin packing
======================================
Genererer 80 produkter med realistiske dimensjoner (lengde, bredde, hoyde) og vekt.
Dataene representerer et utvalg av artikler i et norsk netthandelslager, og skal
pakkes i standardesker paa 60 x 40 x 30 cm.

Produktkatalogen inneholder tre segmenter:
  - smaa (40 %): boker, elektronikk, klaer    (ca 2-10 liter)
  - medium (30 %): kjokkenutstyr, sko       (ca 12-28 liter)
  - stor (30 %): stovsugere, gaveesker     (ca 32-45 liter)

Den siste blandingen er bevisst utfordrende: mange store artikler gjor at FFD og
BFD-heuristikkene faar tydelig forsprang over naiv ankomstrekkefolge.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Standardeske (i cm og kg)
BIN_L, BIN_W, BIN_H = 60.0, 40.0, 30.0
BIN_VOLUME_CM3 = BIN_L * BIN_W * BIN_H           # 72 000 cm^3
BIN_VOLUME_L = BIN_VOLUME_CM3 / 1000.0           # 72 liter
BIN_MAX_WEIGHT_KG = 25.0

N_PRODUCTS = 80
SEED = 101


def _dims_from_volume(volume_l: float, rng, klasse: str) -> tuple:
    """Generer plausible (l, b, h) i cm slik at l*b*h/1000 ~ volume_l og
    dimensjonene er trunkert innenfor bin-dimensjonene.

    Prinsipp: bruk klasse-avhengige aspect ratios (l:b:h) og skaler til
    aa treffe maalvolum. Smaa artikler blir ogsaa fysisk smaa i alle dimensjoner.
    """
    target_cm3 = volume_l * 1000.0
    # Basis aspect ratio per klasse - relative proporsjoner, skal skaleres
    if klasse == 'smaa':
        base = (rng.uniform(1.6, 2.4), rng.uniform(1.0, 1.4), rng.uniform(0.6, 1.0))
    elif klasse == 'medium':
        base = (rng.uniform(1.8, 2.5), rng.uniform(1.1, 1.5), rng.uniform(0.7, 1.1))
    else:  # stor
        base = (rng.uniform(2.0, 2.8), rng.uniform(1.2, 1.7), rng.uniform(0.8, 1.2))

    raw_vol = base[0] * base[1] * base[2]
    scale = (target_cm3 / raw_vol) ** (1 / 3)
    L, W, H = base[0] * scale, base[1] * scale, base[2] * scale

    # Truncate til bin-dimensjoner (minus 1 cm for klaring)
    L = min(L, BIN_L - 1.0)
    W = min(W, BIN_W - 1.0)
    H = min(H, BIN_H - 1.0)
    return round(float(L), 1), round(float(W), 1), round(float(H), 1)


def generate_products(n: int = N_PRODUCTS, seed: int = SEED) -> pd.DataFrame:
    """Generer en produktkatalog med 80 artikler fordelt paa tre storrelsesklasser."""
    rng = np.random.default_rng(seed)

    n_small = int(round(0.40 * n))
    n_medium = int(round(0.30 * n))
    n_large = n - n_small - n_medium

    # Trekk volumer uavhengig per klasse
    v_small = rng.uniform(1.5, 10.0, n_small)
    v_medium = rng.uniform(12.0, 28.0, n_medium)
    v_large = rng.uniform(32.0, 45.0, n_large)
    volumes = np.concatenate([v_small, v_medium, v_large])
    klasse = (['smaa'] * n_small + ['medium'] * n_medium + ['stor'] * n_large)

    # Vekter: stort samsvar med volum, men med stoy. Lav tetthet (myke pakninger,
    # tekstiler, papp) gjor at volum er bindende - vekt er sekundaert.
    density = np.where(np.array(klasse) == 'smaa',
                       rng.uniform(0.15, 0.50, n),
                       np.where(np.array(klasse) == 'medium',
                                rng.uniform(0.10, 0.30, n),
                                rng.uniform(0.07, 0.18, n)))
    weights = np.clip(volumes * density, 0.1, BIN_MAX_WEIGHT_KG - 0.5)

    # Bygg dimensjoner fra volum
    dims = [_dims_from_volume(v, rng, k) for v, k in zip(volumes, klasse)]

    df = pd.DataFrame({
        'sku': [f'SKU{i+1:03d}' for i in range(n)],
        'lengde_cm': [d[0] for d in dims],
        'bredde_cm': [d[1] for d in dims],
        'hoyde_cm': [d[2] for d in dims],
        'vekt_kg': np.round(weights, 2),
        'klasse': klasse,
    })
    df['volum_cm3'] = df['lengde_cm'] * df['bredde_cm'] * df['hoyde_cm']
    df['volum_l'] = np.round(df['volum_cm3'] / 1000.0, 2)

    # Bland rekkefolge - naiv first-fit vil da se en uordnet strom av artikler
    order = rng.permutation(n)
    df = df.iloc[order].reset_index(drop=True)

    return df


def calculate_statistics(df: pd.DataFrame) -> dict:
    return {
        'antall_produkter': int(len(df)),
        'bin_lengde_cm': BIN_L,
        'bin_bredde_cm': BIN_W,
        'bin_hoyde_cm': BIN_H,
        'bin_volum_l': round(BIN_VOLUME_L, 1),
        'bin_maks_vekt_kg': BIN_MAX_WEIGHT_KG,
        'volum_mean_l': round(float(df['volum_l'].mean()), 2),
        'volum_std_l': round(float(df['volum_l'].std()), 2),
        'volum_min_l': round(float(df['volum_l'].min()), 2),
        'volum_max_l': round(float(df['volum_l'].max()), 2),
        'volum_sum_l': round(float(df['volum_l'].sum()), 2),
        'vekt_mean_kg': round(float(df['vekt_kg'].mean()), 2),
        'vekt_sum_kg': round(float(df['vekt_kg'].sum()), 2),
        'andel_smaa': round(float((df['klasse'] == 'smaa').mean()), 2),
        'andel_medium': round(float((df['klasse'] == 'medium').mean()), 2),
        'andel_stor': round(float((df['klasse'] == 'stor').mean()), 2),
    }


def plot_products_dist(df: pd.DataFrame, output_path: Path) -> None:
    """Generer fire-panels figur: volumfordeling, vekt, scatter, klassefordeling."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))

    colors = {'smaa': '#8CC8E5', 'medium': '#97D4B7', 'stor': '#F6BA7C'}
    colors_dark = {'smaa': '#1F6587', 'medium': '#307453', 'stor': '#9C540B'}
    order = ['smaa', 'medium', 'stor']

    # Panel 1: volumhistogram
    ax = axes[0, 0]
    for k in order:
        sub = df[df['klasse'] == k]['volum_l']
        ax.hist(sub, bins=12, color=colors[k], edgecolor=colors_dark[k],
                alpha=0.75, label=k)
    ax.axvline(BIN_VOLUME_L, color='#1F2933', linestyle='--', linewidth=1.2,
               label=f'bin = {BIN_VOLUME_L:.0f} l')
    ax.set_xlabel('volum $v_i$ (liter)', fontsize=11)
    ax.set_ylabel('antall produkter', fontsize=11)
    ax.set_title('Volumfordeling', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 2: vekthistogram
    ax = axes[0, 1]
    for k in order:
        sub = df[df['klasse'] == k]['vekt_kg']
        ax.hist(sub, bins=12, color=colors[k], edgecolor=colors_dark[k],
                alpha=0.75, label=k)
    ax.axvline(BIN_MAX_WEIGHT_KG, color='#1F2933', linestyle='--', linewidth=1.2,
               label=f'maks {BIN_MAX_WEIGHT_KG:.0f} kg')
    ax.set_xlabel('vekt $m_i$ (kg)', fontsize=11)
    ax.set_ylabel('antall produkter', fontsize=11)
    ax.set_title('Vektfordeling', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: scatter volum vs vekt
    ax = axes[1, 0]
    for k in order:
        sub = df[df['klasse'] == k]
        ax.scatter(sub['volum_l'], sub['vekt_kg'], color=colors[k],
                   edgecolor=colors_dark[k], s=42, alpha=0.85, label=k)
    ax.set_xlabel('volum $v_i$ (liter)', fontsize=11)
    ax.set_ylabel('vekt $m_i$ (kg)', fontsize=11)
    ax.set_title('Volum og vekt', fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 4: klassefordeling
    ax = axes[1, 1]
    counts = df['klasse'].value_counts().reindex(order)
    bar_colors = [colors[k] for k in counts.index]
    bar_edge = [colors_dark[k] for k in counts.index]
    bars = ax.bar(counts.index, counts.values, color=bar_colors,
                  edgecolor=bar_edge, linewidth=1.2)
    for bar, c in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, c + 0.5, str(int(c)),
                ha='center', va='bottom', fontsize=10)
    ax.set_xlabel('produktklasse', fontsize=11)
    ax.set_ylabel('antall produkter', fontsize=11)
    ax.set_title('Produktklasser', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 1: DATAINNSAMLING")
    print(f"{'='*60}")

    df = generate_products()
    print(f"\nGenerert {len(df)} produkter (seed = {SEED})")
    print(f"Bin-dimensjon: {BIN_L:.0f} x {BIN_W:.0f} x {BIN_H:.0f} cm")
    print(f"Bin-volum: {BIN_VOLUME_L:.1f} liter, maks vekt: {BIN_MAX_WEIGHT_KG:.1f} kg")

    stats = calculate_statistics(df)
    print("\n--- Deskriptiv statistikk ---")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    csv_path = DATA_DIR / 'products.csv'
    df.to_csv(csv_path, index=False)
    print(f"\nProdukter lagret: {csv_path}")

    with open(OUTPUT_DIR / 'step01_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Statistikk lagret: {OUTPUT_DIR / 'step01_stats.json'}")

    plot_products_dist(df, OUTPUT_DIR / 'bp_products_dist.png')


if __name__ == '__main__':
    main()
