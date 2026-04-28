"""
Steg 5: Modellvalidering (Diagnostikk)
======================================
Evaluerer modellkvaliteten ved å analysere residualene.
Sjekker om residualene oppfører seg som hvit støy.
"""

import json
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox

from step01_datainnsamling import create_time_series

warnings.filterwarnings('ignore')


def load_fitted_model(output_dir: Path) -> dict:
    """Last inn den tidligere tilpassede modellen."""
    model_path = output_dir / 'sarima_model.pkl'
    with open(model_path, 'rb') as f:
        return pickle.load(f)


def get_residuals(fitted_model: dict) -> pd.Series:
    """Hent residualene fra den tilpassede modellen."""
    results = fitted_model['results']
    residuals = results.resid
    return residuals


def ljung_box_test(residuals: pd.Series, lags: list = [12, 24]) -> dict:
    """
    Utfør Ljung-Box test for autokorrelasjon i residualene.

    Ljung-Box statistikken:
    Q = n(n+2) Σ(k=1 to h) [ρ_k² / (n-k)]

    Under H₀ (ingen autokorrelasjon): Q ~ χ²(h-p-q)

    Hypoteser:
    H₀: Residualene er uavhengige (hvit støy)
    H₁: Det finnes autokorrelasjon i residualene

    Beslutningsregel: Forkast H₀ hvis p < 0.05
    """
    results = []

    for lag in lags:
        lb_result = acorr_ljungbox(residuals, lags=[lag], return_df=True)

        results.append({
            'lag': lag,
            'lb_statistikk': round(float(lb_result['lb_stat'].values[0]), 4),
            'p_verdi': round(float(lb_result['lb_pvalue'].values[0]), 6),
            'signifikant': bool(lb_result['lb_pvalue'].values[0] < 0.05),
            'konklusjon': 'Autokorrelasjon påvist' if lb_result['lb_pvalue'].values[0] < 0.05
                         else 'Ingen signifikant autokorrelasjon'
        })

    return results


def residual_statistics(residuals: pd.Series) -> dict:
    """
    Beregn deskriptiv statistikk for residualene.

    For hvit støy forventer vi:
    - Gjennomsnitt ≈ 0
    - Normalfordelte residualer
    """
    # Shapiro-Wilk test for normalitet (kun for n < 5000)
    if len(residuals) < 5000:
        shapiro_stat, shapiro_p = stats.shapiro(residuals.dropna())
    else:
        shapiro_stat, shapiro_p = np.nan, np.nan

    # Jarque-Bera test for normalitet
    jb_result = stats.jarque_bera(residuals.dropna())
    jb_stat, jb_p = jb_result.statistic, jb_result.pvalue
    skewness = stats.skew(residuals.dropna())
    kurtosis = stats.kurtosis(residuals.dropna()) + 3  # scipy returns excess kurtosis

    return {
        'n': len(residuals.dropna()),
        'gjennomsnitt': round(float(residuals.mean()), 6),
        'standardavvik': round(float(residuals.std()), 6),
        'skjevhet': round(float(skewness), 4),
        'kurtose': round(float(kurtosis), 4),
        'shapiro_wilk': {
            'statistikk': round(float(shapiro_stat), 4) if not np.isnan(shapiro_stat) else None,
            'p_verdi': round(float(shapiro_p), 6) if not np.isnan(shapiro_p) else None
        },
        'jarque_bera': {
            'statistikk': round(float(jb_stat), 4),
            'p_verdi': round(float(jb_p), 6),
            'normalfordelt': bool(jb_p > 0.05)
        }
    }


def plot_residual_diagnostics(residuals: pd.Series, output_dir: Path) -> None:
    """
    Generer diagnostiske plott for residualene.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))

    # 1. Residualer over tid
    ax1 = axes[0, 0]
    ax1.plot(residuals.index, residuals.values, 'b-', linewidth=0.8)
    ax1.axhline(y=0, color='r', linestyle='--', linewidth=1)
    ax1.set_xlabel('År', fontsize=11)
    ax1.set_ylabel('Residual', fontsize=11)
    ax1.set_title('Residualer over tid', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)

    # 2. ACF av residualer
    ax2 = axes[0, 1]
    plot_acf(residuals.dropna(), ax=ax2, lags=24, alpha=0.05,
             title='ACF av residualer')
    ax2.set_xlabel('Lag (måneder)', fontsize=11)
    ax2.set_ylabel('Korrelasjon', fontsize=11)
    # Marker sesonglag
    for lag in [12, 24]:
        ax2.axvline(x=lag, color='red', linestyle='--', alpha=0.3, linewidth=1)

    # 3. Histogram med normalfordeling
    ax3 = axes[1, 0]
    residuals_clean = residuals.dropna()
    ax3.hist(residuals_clean, bins=20, density=True, alpha=0.7,
             color='steelblue', edgecolor='white', label='Residualer')

    # Legg til normalfordelingskurve
    x = np.linspace(residuals_clean.min(), residuals_clean.max(), 100)
    ax3.plot(x, stats.norm.pdf(x, residuals_clean.mean(), residuals_clean.std()),
             'r-', linewidth=2, label='Normalfordeling')
    ax3.set_xlabel('Residualverdi', fontsize=11)
    ax3.set_ylabel('Tetthet', fontsize=11)
    ax3.set_title('Histogram av residualer', fontsize=12, fontweight='bold')
    ax3.legend(fontsize=10)

    # 4. Q-Q plott
    ax4 = axes[1, 1]
    stats.probplot(residuals_clean, dist="norm", plot=ax4)
    ax4.set_title('Q-Q plott (normalitet)', fontsize=12, fontweight='bold')
    ax4.get_lines()[0].set_markerfacecolor('steelblue')
    ax4.get_lines()[0].set_markersize(5)

    plt.tight_layout()
    plt.savefig(output_dir / 'sarima_residual_diagnostics.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_dir / 'sarima_residual_diagnostics.png'}")


def plot_residual_acf(residuals: pd.Series, output_path: Path) -> None:
    """
    Generer kun ACF-plott av residualer (for LaTeX).
    """
    fig, ax = plt.subplots(figsize=(10, 4.5))

    plot_acf(residuals.dropna(), ax=ax, lags=24, alpha=0.05,
             title='')
    ax.set_xlabel('$k$', fontsize=16)
    ax.set_ylabel(r'$\rho_k$', fontsize=16, rotation=0, labelpad=15)
    ax.set_title('ACF av residualer fra SARIMA(1,1,1)(0,1,1)[12]',
                 fontsize=12, fontweight='bold')

    # Marker sesonglag
    for lag in [12, 24]:
        ax.axvline(x=lag, color='red', linestyle='--', alpha=0.3, linewidth=1)

    ax.tick_params(axis='both', labelsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    """Hovedfunksjon for modellvalidering."""
    output_dir = Path(__file__).parent.parent / 'output'

    print(f"\n{'='*60}")
    print("STEG 5: MODELLVALIDERING (DIAGNOSTIKK)")
    print(f"{'='*60}")

    # 1. Last inn modell
    print("\n--- Laster inn tilpasset modell ---")
    fitted = load_fitted_model(output_dir)
    results = fitted['results']

    # 2. Hent residualer
    residuals = get_residuals(fitted)
    print(f"  Residualer hentet: {len(residuals.dropna())} verdier")

    # 3. Residualstatistikk
    print("\n--- Residualstatistikk ---")
    resid_stats = residual_statistics(residuals)
    print(f"  Gjennomsnitt:   {resid_stats['gjennomsnitt']:.6f} (forventet ~ 0)")
    print(f"  Standardavvik:  {resid_stats['standardavvik']:.6f}")
    print(f"  Skjevhet:       {resid_stats['skjevhet']:.4f} (forventet ~ 0)")
    print(f"  Kurtose:        {resid_stats['kurtose']:.4f} (forventet ~ 3)")

    # 4. Ljung-Box test
    print("\n--- Ljung-Box test for autokorrelasjon ---")
    lb_results = ljung_box_test(residuals, lags=[12, 24])

    print(f"\n  {'Lag':<8} {'Q-statistikk':>15} {'p-verdi':>12} {'Konklusjon':<30}")
    print("  " + "-" * 70)
    for result in lb_results:
        print(f"  {result['lag']:<8} {result['lb_statistikk']:>15.4f} "
              f"{result['p_verdi']:>12.6f} {result['konklusjon']:<30}")

    # 5. Normalitetstest
    print("\n--- Normalitetstest (Jarque-Bera) ---")
    jb = resid_stats['jarque_bera']
    print(f"  JB-statistikk: {jb['statistikk']:.4f}")
    print(f"  p-verdi:       {jb['p_verdi']:.6f}")
    print(f"  Konklusjon:    {'Normalfordelt' if jb['normalfordelt'] else 'Ikke normalfordelt'}")

    # 6. Generer diagnostiske plott
    print("\n--- Genererer diagnostiske plott ---")
    plot_residual_diagnostics(residuals, output_dir)
    plot_residual_acf(residuals, output_dir / 'sarima_residual_acf.png')

    # 7. Lagre resultater
    diagnostics = {
        'residual_statistikk': resid_stats,
        'ljung_box_test': lb_results,
        'konklusjon': {
            'hvit_stoy': all(not r['signifikant'] for r in lb_results),
            'beskrivelse': 'Residualene oppfører seg som hvit støy'
                          if all(not r['signifikant'] for r in lb_results)
                          else 'Det finnes signifikant autokorrelasjon i residualene'
        }
    }

    results_path = output_dir / 'diagnostics_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(diagnostics, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")

    # Oppsummering
    print(f"\n{'='*60}")
    print("KONKLUSJON")
    print(f"{'='*60}")

    all_ok = all(not r['signifikant'] for r in lb_results)

    if all_ok:
        print("\n  [OK] Ljung-Box test: Ingen signifikant autokorrelasjon i residualene")
        print("  [OK] Residualene oppfoerer seg som hvit stoey")
        print("  [OK] Modellen SARIMA(1,1,1)(0,1,1)[12] er adekvat")
        print("\n  Modellen fanger opp all systematisk struktur i dataene.")
        print("  Vi kan gaa videre til prognose (Steg 6).")
    else:
        print("\n  [X] Det finnes signifikant autokorrelasjon i residualene")
        print("  [X] Modellen kan forbedres")
        print("\n  Vurder aa:")
        print("    - Oeke AR eller MA-orden")
        print("    - Legge til sesongkomponenter")
        print("    - Undersoeke strukturelle brudd")


if __name__ == '__main__':
    main()
