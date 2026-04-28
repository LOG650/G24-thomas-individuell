"""
Steg 2: Stasjonaritet og differensiering
========================================
Utfører ADF-test, log-transformasjon, og differensiering for SARIMA-analyse.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller

from step01_datainnsamling import create_time_series


def adf_test(series: pd.Series, name: str) -> dict:
    """
    Kjør Augmented Dickey-Fuller (ADF) test og returner resultater.

    H₀: Serien har enhetsrot (ikke-stasjonær)
    H₁: Serien er stasjonær
    """
    result = adfuller(series.dropna(), autolag='AIC')
    return {
        'serie': name,
        'adf_statistic': float(round(result[0], 4)),
        'p_verdi': float(round(result[1], 6)),
        'lags_brukt': int(result[2]),
        'observasjoner': int(result[3]),
        'kritiske_verdier': {
            '1%': float(round(result[4]['1%'], 4)),
            '5%': float(round(result[4]['5%'], 4)),
            '10%': float(round(result[4]['10%'], 4)),
        },
        'stasjonaer': bool(result[1] < 0.05)
    }


def apply_transformations(ts: pd.Series) -> dict:
    """
    Anvend transformasjoner for å oppnå stasjonaritet.

    1. Log-transformasjon: Stabiliserer variansen
    2. Førstegrads differensiering (d=1): Fjerner trend
    3. Sesongdifferensiering (D=1, m=12): Fjerner årlig mønster
    """
    # Log-transformasjon
    log_ts = np.log(ts)

    # Førstegrads differensiering
    log_diff1 = log_ts.diff(1)

    # Sesongdifferensiering (m=12)
    log_diff1_12 = log_diff1.diff(12).dropna()

    return {
        'original': ts,
        'log': log_ts,
        'log_diff1': log_diff1,
        'log_diff1_12': log_diff1_12
    }


def plot_comparison(original: pd.Series, differenced: pd.Series, output_path: Path) -> None:
    """Generer sammenligning mellom original og differensiert serie."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 7))

    # Numeriske t-verdier
    t_original = np.arange(1, len(original) + 1)  # t = 1, ..., 144
    # Differensiert serie starter ved t=14 (mister 13 obs til differensiering)
    t_diff = np.arange(14, 14 + len(differenced))  # t = 14, ..., 144

    # Øvre subplot: Original serie
    ax1 = axes[0]
    ax1.plot(t_original, original.values, 'b-', linewidth=1.2)
    ax1.set_ylabel('$Y_t$', fontsize=16, rotation=0, labelpad=15)
    ax1.set_title('Original tidsserie (ikke-stasjonær)', fontsize=12, fontweight='bold', pad=35)
    ax1.set_xlim(1, 144)
    ax1.set_xticks([1, 25, 49, 73, 97, 121, 144])
    ax1.grid(True, alpha=0.3)
    ax1.tick_params(axis='both', labelsize=10)

    # Øvre x-akse med årstall for ax1
    ax1_twin = ax1.twiny()
    ax1_twin.set_xlim(ax1.get_xlim())
    year_positions = [1, 25, 49, 73, 97, 121]
    year_labels = ['2003', '2005', '2007', '2009', '2011', '2013']
    ax1_twin.set_xticks(year_positions)
    ax1_twin.set_xticklabels(year_labels)
    ax1_twin.tick_params(axis='x', labelsize=10)

    # Nedre subplot: Differensiert serie
    ax2 = axes[1]
    ax2.plot(t_diff, differenced.values, 'g-', linewidth=1.0)
    ax2.axhline(y=0, color='r', linestyle='--', linewidth=0.8, alpha=0.7)
    ax2.set_xlabel('$t$', fontsize=16)
    ax2.set_ylabel('$Z_t$', fontsize=16, rotation=0, labelpad=15)
    ax2.set_title('Etter log-transformasjon og differensiering (stasjonær)', fontsize=12, fontweight='bold')
    ax2.set_xlim(1, 144)
    ax2.set_xticks([1, 25, 49, 73, 97, 121, 144])
    ax2.grid(True, alpha=0.3)
    ax2.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_differenced(differenced: pd.Series, output_path: Path) -> None:
    """Generer plott av differensiert serie."""
    fig, ax = plt.subplots(figsize=(10, 4))

    ax.plot(differenced.index, differenced.values, 'g-', linewidth=1.0, label='Differensiert serie')
    ax.axhline(y=0, color='r', linestyle='--', linewidth=0.8, alpha=0.7, label='Null-linje')

    ax.set_xlabel('År', fontsize=11)
    ax.set_ylabel('Differensiert log-salg', fontsize=11)
    ax.set_title('Log-differensiert tidsserie: $\\nabla \\nabla_{12} \\log(Y_t)$', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    """Hovedfunksjon for stasjonaritetsanalyse."""
    # Output-mappe
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)

    # 1. Last inn data
    ts = create_time_series()
    print(f"\n{'='*60}")
    print("STEG 2: STASJONARITET OG DIFFERENSIERING")
    print(f"{'='*60}")
    print(f"\nTidsserie lastet: {len(ts)} observasjoner")

    # 2. ADF-test på original serie
    print("\n--- ADF-test: Original serie ---")
    adf_original = adf_test(ts, 'Original')
    print(f"  ADF-statistikk: {adf_original['adf_statistic']}")
    print(f"  P-verdi: {adf_original['p_verdi']}")
    print(f"  Kritiske verdier: {adf_original['kritiske_verdier']}")
    print(f"  Konklusjon: {'Stasjonær' if adf_original['stasjonaer'] else 'Ikke-stasjonær'}")

    # 3. Anvend transformasjoner
    print("\n--- Transformasjoner ---")
    print("  1. Log-transformasjon (stabiliserer variansen)")
    print("  2. Førstegrads differensiering (d=1, fjerner trend)")
    print("  3. Sesongdifferensiering (D=1, m=12, fjerner årlig mønster)")

    transformed = apply_transformations(ts)
    differenced = transformed['log_diff1_12']
    print(f"\n  Differensiert serie: {len(differenced)} observasjoner")
    print(f"  (13 observasjoner tapt til differensiering)")

    # 4. ADF-test på differensiert serie
    print("\n--- ADF-test: Differensiert serie ---")
    adf_differenced = adf_test(differenced, 'Differensiert')
    print(f"  ADF-statistikk: {adf_differenced['adf_statistic']}")
    print(f"  P-verdi: {adf_differenced['p_verdi']}")
    print(f"  Kritiske verdier: {adf_differenced['kritiske_verdier']}")
    print(f"  Konklusjon: {'Stasjonær' if adf_differenced['stasjonaer'] else 'Ikke-stasjonær'}")

    # 5. Generer plott
    print("\n--- Genererer figurer ---")
    plot_comparison(ts, differenced, output_dir / 'sarima_stationarity_comparison.png')
    plot_differenced(differenced, output_dir / 'sarima_differenced_plot.png')

    # 6. Lagre resultater som JSON
    results = {
        'original_serie': {
            'adf_test': adf_original,
            'observasjoner': len(ts)
        },
        'differensiert_serie': {
            'adf_test': adf_differenced,
            'observasjoner': len(differenced),
            'transformasjoner': [
                'log-transformasjon',
                'førstegrads differensiering (d=1)',
                'sesongdifferensiering (D=1, m=12)'
            ]
        },
        'sesongperiode': 12,
        'konklusjon': {
            'd': 1,
            'D': 1,
            'm': 12,
            'beskrivelse': 'Serien er stasjonær etter log-transformasjon, førstegrads differensiering og sesongdifferensiering.'
        }
    }

    results_path = output_dir / 'stationarity_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")

    # Oppsummering
    print(f"\n{'='*60}")
    print("KONKLUSJON")
    print(f"{'='*60}")
    print(f"  • Original serie er IKKE-STASJONÆR (p = {adf_original['p_verdi']})")
    print(f"  • Etter transformasjon er serien STASJONÆR (p = {adf_differenced['p_verdi']})")
    print(f"  • Sesongperiode: m = 12 (månedlige data, årlig syklus)")
    print(f"  • SARIMA-parametere: d=1, D=1, m=12")


if __name__ == '__main__':
    main()
