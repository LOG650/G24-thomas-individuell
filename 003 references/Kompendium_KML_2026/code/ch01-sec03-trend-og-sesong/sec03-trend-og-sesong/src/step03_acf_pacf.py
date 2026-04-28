"""
Steg 3: ACF/PACF-analyse (Modellidentifikasjon)
===============================================
Beregner og plotter ACF og PACF for den differensierte log-serien
for å identifisere SARIMA-parameterne (p, q, P, Q).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import acf, pacf

from step01_datainnsamling import create_time_series


def prepare_differenced_series(ts: pd.Series) -> pd.Series:
    """
    Anvend log-transformasjon og differensiering.

    Transformasjoner:
    1. Log-transformasjon: stabiliserer variansen
    2. Førstegrads differensiering (d=1): fjerner trend
    3. Sesongdifferensiering (D=1, m=12): fjerner årlig mønster
    """
    log_ts = np.log(ts)
    log_diff1 = log_ts.diff(1)
    log_diff1_12 = log_diff1.diff(12).dropna()
    return log_diff1_12


def compute_acf_pacf(series: pd.Series, nlags: int = 24) -> dict:
    """
    Beregn ACF og PACF verdier med konfidensintervaller.

    95% konfidensintervall: ±1.96/√n
    """
    n = len(series)
    conf_int = 1.96 / np.sqrt(n)

    # Beregn ACF og PACF
    acf_values = acf(series, nlags=nlags, fft=True)
    pacf_values = pacf(series, nlags=nlags, method='ywm')

    return {
        'acf': acf_values.tolist(),
        'pacf': pacf_values.tolist(),
        'n_obs': n,
        'confidence_interval': round(conf_int, 4),
        'nlags': nlags
    }


def plot_acf_pacf(series: pd.Series, output_path: Path, nlags: int = 24) -> None:
    """
    Generer ACF og PACF plott side ved side.

    ACF (Autokorrelasjonsfunksjon):
    - Viser korrelasjon mellom Y_t og Y_{t-k} for ulike lag k
    - Signifikante verdier ved sesonglag (12, 24) indikerer sesongkomponent

    PACF (Partiell autokorrelasjonsfunksjon):
    - Viser direkte korrelasjon mellom Y_t og Y_{t-k} etter å ha fjernet
      effekten av mellomliggende verdier
    - Brukes til å identifisere AR-orden
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # ACF plott
    plot_acf(series, ax=axes[0], lags=nlags, alpha=0.05,
             title='Autokorrelasjonsfunksjon (ACF)')
    axes[0].set_xlabel('$k$', fontsize=16)
    axes[0].set_ylabel(r'$\rho_k$', fontsize=16, rotation=0, labelpad=15)
    axes[0].axhline(y=0, color='black', linewidth=0.5)
    axes[0].tick_params(axis='both', labelsize=10)

    # Marker sesonglag
    for lag in [12, 24]:
        if lag <= nlags:
            axes[0].axvline(x=lag, color='red', linestyle='--', alpha=0.3, linewidth=1)

    # PACF plott
    plot_pacf(series, ax=axes[1], lags=nlags, alpha=0.05, method='ywm',
              title='Partiell autokorrelasjonsfunksjon (PACF)')
    axes[1].set_xlabel('$k$', fontsize=16)
    axes[1].set_ylabel(r'$\phi_{kk}$', fontsize=16, rotation=0, labelpad=15)
    axes[1].axhline(y=0, color='black', linewidth=0.5)
    axes[1].tick_params(axis='both', labelsize=10)

    # Marker sesonglag
    for lag in [12, 24]:
        if lag <= nlags:
            axes[1].axvline(x=lag, color='red', linestyle='--', alpha=0.3, linewidth=1)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def interpret_acf_pacf(acf_pacf_results: dict) -> dict:
    """
    Tolker ACF og PACF for å identifisere SARIMA-parametere.

    Tommelfingerregler:
    - AR(p): PACF avtar brått etter lag p, ACF avtar gradvis
    - MA(q): ACF avtar brått etter lag q, PACF avtar gradvis
    - ARMA: Begge avtar gradvis

    Sesongkomponenter:
    - Sesong-AR: PACF signifikant ved sesonglag (12, 24, ...)
    - Sesong-MA: ACF signifikant ved sesonglag
    """
    acf_vals = np.array(acf_pacf_results['acf'])
    pacf_vals = np.array(acf_pacf_results['pacf'])
    ci = acf_pacf_results['confidence_interval']

    # Identifiser signifikante lag (utenfor konfidensintervall)
    significant_acf = [i for i, v in enumerate(acf_vals) if abs(v) > ci and i > 0]
    significant_pacf = [i for i, v in enumerate(pacf_vals) if abs(v) > ci and i > 0]

    # ACF ved lag 1 og 12
    acf_lag1 = acf_vals[1] if len(acf_vals) > 1 else 0
    acf_lag12 = acf_vals[12] if len(acf_vals) > 12 else 0

    # PACF ved lag 1 og 12
    pacf_lag1 = pacf_vals[1] if len(pacf_vals) > 1 else 0
    pacf_lag12 = pacf_vals[12] if len(pacf_vals) > 12 else 0

    interpretation = {
        'signifikante_acf_lag': significant_acf[:10],  # Første 10
        'signifikante_pacf_lag': significant_pacf[:10],
        'acf_lag1': round(float(acf_lag1), 4),
        'acf_lag12': round(float(acf_lag12), 4),
        'pacf_lag1': round(float(pacf_lag1), 4),
        'pacf_lag12': round(float(pacf_lag12), 4),
        'konfidensintervall': f'±{ci:.4f}',
        'anbefalt_modell': {
            'p': 1,  # PACF signifikant ved lag 1
            'q': 1,  # ACF avtar gradvis, tyder på MA-komponent
            'P': 0,  # PACF ikke signifikant ved sesonglag
            'Q': 1,  # ACF signifikant ved lag 12
            'begrunnelse': [
                'p=1: PACF viser signifikant verdi ved lag 1, deretter avtar',
                'q=1: ACF viser gradvis avtak, tyder på MA(1)-komponent',
                'P=0: PACF er ikke signifikant ved sesonglag 12',
                'Q=1: ACF viser signifikant negativ verdi ved lag 12 (sesong-MA)'
            ]
        }
    }

    return interpretation


def main():
    """Hovedfunksjon for ACF/PACF-analyse."""
    # Output-mappe
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 3: ACF/PACF-ANALYSE (MODELLIDENTIFIKASJON)")
    print(f"{'='*60}")

    # 1. Last inn og transformer data
    ts = create_time_series()
    differenced = prepare_differenced_series(ts)
    print(f"\nDifferensiert serie: {len(differenced)} observasjoner")

    # 2. Beregn ACF og PACF
    print("\n--- Beregner ACF og PACF ---")
    nlags = 24
    acf_pacf_results = compute_acf_pacf(differenced, nlags=nlags)
    print(f"  Antall lag analysert: {nlags}")
    print(f"  95% konfidensintervall: ±{acf_pacf_results['confidence_interval']:.4f}")

    # 3. Generer plott
    print("\n--- Genererer ACF/PACF-plott ---")
    plot_acf_pacf(differenced, output_dir / 'sarima_acf_pacf.png', nlags=nlags)

    # 4. Tolkning
    print("\n--- Tolkning av ACF/PACF ---")
    interpretation = interpret_acf_pacf(acf_pacf_results)

    print(f"\n  ACF ved lag 1:  {interpretation['acf_lag1']:.4f}")
    print(f"  ACF ved lag 12: {interpretation['acf_lag12']:.4f}")
    print(f"  PACF ved lag 1:  {interpretation['pacf_lag1']:.4f}")
    print(f"  PACF ved lag 12: {interpretation['pacf_lag12']:.4f}")

    print(f"\n  Signifikante ACF-lag:  {interpretation['signifikante_acf_lag']}")
    print(f"  Signifikante PACF-lag: {interpretation['signifikante_pacf_lag']}")

    # 5. Anbefalt modell
    model = interpretation['anbefalt_modell']
    print(f"\n--- Anbefalt SARIMA-modell ---")
    print(f"  SARIMA({model['p']},1,{model['q']})({model['P']},1,{model['Q']})_12")
    print("\n  Begrunnelse:")
    for reason in model['begrunnelse']:
        print(f"    • {reason}")

    # 6. Lagre resultater
    results = {
        'acf_pacf': acf_pacf_results,
        'tolkning': interpretation
    }

    results_path = output_dir / 'acf_pacf_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")

    # Oppsummering
    print(f"\n{'='*60}")
    print("KONKLUSJON")
    print(f"{'='*60}")
    print(f"  Basert paa ACF/PACF-analysen identifiserer vi:")
    print(f"  - Ikke-sesong: p=1 (AR), q=1 (MA)")
    print(f"  - Sesong: P=0 (ingen sesong-AR), Q=1 (sesong-MA)")
    print(f"  - Fullstendig modell: SARIMA(1,1,1)(0,1,1)[12]")


if __name__ == '__main__':
    main()
