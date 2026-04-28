"""
Steg 4: Parameterestimering (Modelltilpasning)
==============================================
Estimerer SARIMA(1,1,1)(0,1,1)₁₂ modellen ved hjelp av
Maximum Likelihood Estimation (MLE).
"""

import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from step01_datainnsamling import create_time_series

# Undertrykk convergence warnings
warnings.filterwarnings('ignore')


def fit_sarima_model(ts: pd.Series,
                     order: tuple = (1, 1, 1),
                     seasonal_order: tuple = (0, 1, 1, 12)) -> dict:
    """
    Tilpass SARIMA-modell til tidsserien.

    Parameters
    ----------
    ts : pd.Series
        Tidsserien (original skala, ikke log-transformert)
    order : tuple
        (p, d, q) - AR-orden, differensieringsgrad, MA-orden
    seasonal_order : tuple
        (P, D, Q, m) - Sesong-parametere

    Returns
    -------
    dict
        Modellresultater inkludert koeffisienter og diagnostikk
    """
    # Log-transformer dataene (håndterer økende varians)
    log_ts = np.log(ts)

    # Tilpass SARIMA-modell
    model = SARIMAX(
        log_ts,
        order=order,
        seasonal_order=seasonal_order,
        enforce_stationarity=False,
        enforce_invertibility=False
    )

    # Estimer med MLE
    results = model.fit(disp=False)

    return {
        'model': model,
        'results': results,
        'log_ts': log_ts
    }


def extract_coefficients(results) -> dict:
    """
    Trekk ut estimerte koeffisienter med statistikk.

    MLE gir oss:
    - Punktestimater for parameterne
    - Standardfeil (usikkerhet)
    - z-verdier og p-verdier for signifikanstest
    """
    params = results.params
    std_errors = results.bse
    z_values = results.zvalues
    p_values = results.pvalues

    coefficients = {}

    # Mapping av parameternavn til norske beskrivelser
    param_names = {
        'ar.L1': ('phi_1', 'AR(1) koeffisient'),
        'ma.L1': ('theta_1', 'MA(1) koeffisient'),
        'ma.S.L12': ('Theta_1', 'Sesong-MA(1) koeffisient'),
        'sigma2': ('sigma^2', 'Residualvarians')
    }

    for param_key, (symbol, description) in param_names.items():
        if param_key in params.index:
            coefficients[param_key] = {
                'symbol': symbol,
                'beskrivelse': description,
                'estimat': round(float(params[param_key]), 4),
                'standardfeil': round(float(std_errors[param_key]), 4),
                'z_verdi': round(float(z_values[param_key]), 4),
                'p_verdi': round(float(p_values[param_key]), 6),
                'signifikant': bool(p_values[param_key] < 0.05)
            }

    return coefficients


def extract_model_fit_statistics(results) -> dict:
    """
    Trekk ut modelltilpasningsstatistikk.

    - AIC (Akaike Information Criterion): Lavere er bedre
    - BIC (Bayesian Information Criterion): Lavere er bedre, straffer kompleksitet mer
    - Log-likelihood: Hvor godt modellen tilpasser dataene
    """
    return {
        'aic': round(float(results.aic), 2),
        'bic': round(float(results.bic), 2),
        'log_likelihood': round(float(results.llf), 2),
        'n_observasjoner': int(results.nobs),
        'n_parametere': int(len(results.params))
    }


def format_model_equation(coefficients: dict) -> str:
    """
    Formatter den estimerte modelllikningen.
    """
    phi1 = coefficients.get('ar.L1', {}).get('estimat', 0)
    theta1 = coefficients.get('ma.L1', {}).get('estimat', 0)
    Theta1 = coefficients.get('ma.S.L12', {}).get('estimat', 0)

    equation = f"""
    Estimert SARIMA(1,1,1)(0,1,1)[12] modell:

    (1 - {phi1:.4f}B)(1-B)(1-B^12)Y_t = (1 + {theta1:.4f}B)(1 + {Theta1:.4f}B^12)e_t

    der:
    - phi_1 = {phi1:.4f} (AR-koeffisient)
    - theta_1 = {theta1:.4f} (MA-koeffisient)
    - Theta_1 = {Theta1:.4f} (Sesong-MA-koeffisient)
    """
    return equation


def main():
    """Hovedfunksjon for parameterestimering."""
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 4: PARAMETERESTIMERING (MLE)")
    print(f"{'='*60}")

    # 1. Last inn data
    ts = create_time_series()
    print(f"\nTidsserie lastet: {len(ts)} observasjoner")

    # 2. Definer modellspesifikasjon
    order = (1, 1, 1)  # (p, d, q)
    seasonal_order = (0, 1, 1, 12)  # (P, D, Q, m)
    print(f"\nModellspesifikasjon: SARIMA{order}{seasonal_order}")

    # 3. Tilpass modell
    print("\n--- Estimerer modell med Maximum Likelihood ---")
    fitted = fit_sarima_model(ts, order, seasonal_order)
    results = fitted['results']

    # 4. Trekk ut koeffisienter
    coefficients = extract_coefficients(results)

    print("\n--- Estimerte koeffisienter ---")
    print(f"{'Parameter':<15} {'Estimat':>10} {'Std.feil':>10} {'z-verdi':>10} {'p-verdi':>12} {'Signifikant':>12}")
    print("-" * 75)

    for key, coef in coefficients.items():
        sig_marker = "*" if coef['signifikant'] else ""
        print(f"{coef['symbol']:<15} {coef['estimat']:>10.4f} {coef['standardfeil']:>10.4f} "
              f"{coef['z_verdi']:>10.4f} {coef['p_verdi']:>12.6f} {sig_marker:>12}")

    print("\n  * Signifikant ved alpha = 0.05")

    # 5. Modelltilpasningsstatistikk
    fit_stats = extract_model_fit_statistics(results)

    print("\n--- Modelltilpasning ---")
    print(f"  AIC:            {fit_stats['aic']}")
    print(f"  BIC:            {fit_stats['bic']}")
    print(f"  Log-likelihood: {fit_stats['log_likelihood']}")
    print(f"  Observasjoner:  {fit_stats['n_observasjoner']}")

    # 6. Vis modellsummary
    print("\n--- Statsmodels Summary (utdrag) ---")
    print(results.summary().tables[1])

    # 7. Lagre resultater
    model_results = {
        'modell': f"SARIMA{order}{seasonal_order}",
        'koeffisienter': coefficients,
        'tilpasning': fit_stats,
        'beskrivelse': {
            'metode': 'Maximum Likelihood Estimation (MLE)',
            'optimizer': 'L-BFGS-B',
            'log_transformasjon': True
        }
    }

    results_path = output_dir / 'model_estimation_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(model_results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")

    # Lagre full modell for senere bruk (forecast, diagnostikk)
    import pickle
    model_path = output_dir / 'sarima_model.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(fitted, f)
    print(f"Modell lagret: {model_path}")

    # Oppsummering
    print(f"\n{'='*60}")
    print("KONKLUSJON")
    print(f"{'='*60}")
    print(format_model_equation(coefficients))

    print("\n  Tolkning av koeffisienter:")

    ar_coef = coefficients.get('ar.L1', {})
    if ar_coef:
        if ar_coef['signifikant']:
            print(f"  - AR(1): phi_1={ar_coef['estimat']:.4f} er signifikant (p={ar_coef['p_verdi']:.4f})")
        else:
            print(f"  - AR(1): phi_1={ar_coef['estimat']:.4f} er IKKE signifikant (p={ar_coef['p_verdi']:.4f})")

    ma_coef = coefficients.get('ma.L1', {})
    if ma_coef:
        print(f"  - MA(1): theta_1={ma_coef['estimat']:.4f} er {'signifikant' if ma_coef['signifikant'] else 'ikke signifikant'}")

    sma_coef = coefficients.get('ma.S.L12', {})
    if sma_coef:
        print(f"  - Sesong-MA: Theta_1={sma_coef['estimat']:.4f} er {'signifikant' if sma_coef['signifikant'] else 'ikke signifikant'}")


if __name__ == '__main__':
    main()
