"""
Steg 6: Prognose (Forecasting)
==============================
Genererer 12-måneders prognose for 2015 basert på
den tilpassede SARIMA(1,1,1)(0,1,1)₁₂ modellen.
"""

import json
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import create_time_series

warnings.filterwarnings('ignore')


def load_fitted_model(output_dir: Path) -> dict:
    """Last inn den tidligere tilpassede modellen."""
    model_path = output_dir / 'sarima_model.pkl'
    with open(model_path, 'rb') as f:
        return pickle.load(f)


def generate_forecast(fitted_model: dict, steps: int = 12, alpha: float = 0.05) -> dict:
    """
    Generer prognose med konfidensintervaller.

    Parameters
    ----------
    fitted_model : dict
        Den tilpassede modellen fra step04
    steps : int
        Antall perioder å prognosere (default 12 måneder)
    alpha : float
        Signifikansnivå for konfidensintervall (default 0.05 for 95% CI)

    Returns
    -------
    dict
        Prognoser med punktestimater og konfidensintervaller
    """
    results = fitted_model['results']
    log_ts = fitted_model['log_ts']

    # Generer prognose på log-skala
    forecast_obj = results.get_forecast(steps=steps)

    # Punktestimater (log-skala)
    log_forecast = forecast_obj.predicted_mean

    # Konfidensintervaller (log-skala)
    conf_int = forecast_obj.conf_int(alpha=alpha)

    # Transformer tilbake fra log-skala
    forecast = np.exp(log_forecast)
    lower = np.exp(conf_int.iloc[:, 0])
    upper = np.exp(conf_int.iloc[:, 1])

    # Opprett datoindeks for prognoser
    last_date = log_ts.index[-1]
    forecast_dates = pd.date_range(start=last_date + pd.DateOffset(months=1),
                                   periods=steps, freq='ME')

    return {
        'dates': forecast_dates,
        'forecast': forecast.values,
        'lower': lower.values,
        'upper': upper.values,
        'log_forecast': log_forecast.values,
        'log_lower': conf_int.iloc[:, 0].values,
        'log_upper': conf_int.iloc[:, 1].values,
        'alpha': alpha,
        'confidence_level': f"{int((1-alpha)*100)}%"
    }


def create_forecast_table(forecast_data: dict) -> pd.DataFrame:
    """
    Opprett en tabell med prognoseresultater.
    """
    df = pd.DataFrame({
        'Måned': [d.strftime('%B %Y') for d in forecast_data['dates']],
        'Prognose': np.round(forecast_data['forecast'], 0).astype(int),
        'Nedre 95%': np.round(forecast_data['lower'], 0).astype(int),
        'Øvre 95%': np.round(forecast_data['upper'], 0).astype(int)
    })

    # Beregn intervalbredde
    df['Intervallbredde'] = df['Øvre 95%'] - df['Nedre 95%']

    return df


def plot_forecast(ts: pd.Series, forecast_data: dict, output_path: Path) -> None:
    """
    Generer prognoseplott med historiske data og konfidensintervall.
    """
    fig, ax = plt.subplots(figsize=(12, 6))

    # Numeriske t-verdier
    t_hist = np.arange(1, len(ts) + 1)  # t = 1, ..., 144
    t_forecast = np.arange(len(ts) + 1, len(ts) + 1 + len(forecast_data['forecast']))  # t = 145, ..., 156

    # Historiske data
    ax.plot(t_hist, ts.values, 'b-', linewidth=1.2, label='Historisk salg')

    # Prognose
    forecast_values = forecast_data['forecast']
    lower = forecast_data['lower']
    upper = forecast_data['upper']

    ax.plot(t_forecast, forecast_values, 'r-', linewidth=2,
            marker='o', markersize=5, label='Prognose 2015')

    # Konfidensintervall
    ax.fill_between(t_forecast, lower, upper,
                    color='red', alpha=0.2, label='95% konfidensintervall')

    # Vertikal linje ved prognosestart
    ax.axvline(x=144, color='gray', linestyle='--', linewidth=1, alpha=0.7)

    # Formatering
    ax.set_xlabel('$t$', fontsize=16)
    ax.set_ylabel('$Y_t$', fontsize=16, rotation=0, labelpad=15)
    ax.set_title('SARIMA(1,1,1)(0,1,1)$_{12}$ Prognose for 2015', fontsize=12, fontweight='bold', pad=35)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)
    ax.set_xlim(1, 156)
    ax.set_xticks([1, 25, 49, 73, 97, 121, 144, 156])

    # Øvre x-akse med årstall
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    year_positions = [1, 25, 49, 73, 97, 121, 145]
    year_labels = ['2003', '2005', '2007', '2009', '2011', '2013', '2015']
    ax2.set_xticks(year_positions)
    ax2.set_xticklabels(year_labels)
    ax2.tick_params(axis='x', labelsize=10)

    # Juster y-aksen for å vise hele konfidensintervallet
    y_min = min(ts.min(), lower.min()) * 0.9
    y_max = max(ts.max(), upper.max()) * 1.05
    ax.set_ylim(y_min, y_max)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_forecast_detail(ts: pd.Series, forecast_data: dict, output_path: Path) -> None:
    """
    Generer detaljert prognoseplott (kun siste 2 år + prognose).
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    # Kun siste 24 måneder av historiske data
    ts_recent = ts[-24:]

    # Historiske data
    ax.plot(ts_recent.index, ts_recent.values, 'b-', linewidth=1.5,
            marker='o', markersize=4, label='Historisk salg (2013-2014)')

    # Prognose
    forecast_dates = forecast_data['dates']
    forecast_values = forecast_data['forecast']
    lower = forecast_data['lower']
    upper = forecast_data['upper']

    ax.plot(forecast_dates, forecast_values, 'r-', linewidth=2,
            marker='s', markersize=6, label='Prognose (2015)')

    # Konfidensintervall
    ax.fill_between(forecast_dates, lower, upper,
                    color='red', alpha=0.15, label='95% konfidensintervall')

    # Vertikal linje ved prognosestart
    ax.axvline(x=ts.index[-1], color='gray', linestyle='--', linewidth=1.5, alpha=0.7)
    ax.text(ts.index[-1], ax.get_ylim()[1]*0.95, '  Prognose\n  starter',
            fontsize=9, color='gray', va='top')

    # Formatering
    ax.set_xlabel('År', fontsize=11)
    ax.set_ylabel('Antall traktorer solgt', fontsize=11)
    ax.set_title('Detaljert prognose: Siste 2 år + 12 måneders prognose',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def calculate_annual_summary(forecast_data: dict) -> dict:
    """
    Beregn årssammendrag for prognosen.
    """
    forecast = forecast_data['forecast']
    lower = forecast_data['lower']
    upper = forecast_data['upper']

    return {
        'aarlig_sum_prognose': int(np.sum(forecast)),
        'aarlig_sum_nedre': int(np.sum(lower)),
        'aarlig_sum_ovre': int(np.sum(upper)),
        'gjennomsnittlig_maanedlig': int(np.mean(forecast)),
        'hoeyeste_maaned': {
            'maaned': forecast_data['dates'][np.argmax(forecast)].strftime('%B'),
            'verdi': int(np.max(forecast))
        },
        'laveste_maaned': {
            'maaned': forecast_data['dates'][np.argmin(forecast)].strftime('%B'),
            'verdi': int(np.min(forecast))
        }
    }


def main():
    """Hovedfunksjon for prognose."""
    output_dir = Path(__file__).parent.parent / 'output'

    print(f"\n{'='*60}")
    print("STEG 6: PROGNOSE (FORECASTING)")
    print(f"{'='*60}")

    # 1. Last inn modell og data
    print("\n--- Laster inn modell og data ---")
    fitted = load_fitted_model(output_dir)
    ts = create_time_series()
    print(f"  Historiske data: {ts.index[0].strftime('%b %Y')} - {ts.index[-1].strftime('%b %Y')}")

    # 2. Generer 12-måneders prognose
    print("\n--- Genererer 12-måneders prognose for 2015 ---")
    forecast_data = generate_forecast(fitted, steps=12, alpha=0.05)

    # 3. Opprett prognosetabell
    forecast_table = create_forecast_table(forecast_data)

    print("\n  Månedlige prognoser:")
    print(f"\n  {'Måned':<15} {'Prognose':>10} {'Nedre 95%':>12} {'Øvre 95%':>12}")
    print("  " + "-" * 55)
    for _, row in forecast_table.iterrows():
        print(f"  {row['Måned']:<15} {row['Prognose']:>10} {row['Nedre 95%']:>12} {row['Øvre 95%']:>12}")

    # 4. Årssammendrag
    annual = calculate_annual_summary(forecast_data)
    print(f"\n--- Årssammendrag 2015 ---")
    print(f"  Total prognose:     {annual['aarlig_sum_prognose']:,} enheter")
    print(f"  95% intervall:      [{annual['aarlig_sum_nedre']:,}, {annual['aarlig_sum_ovre']:,}]")
    print(f"  Månedlig snitt:     {annual['gjennomsnittlig_maanedlig']} enheter")
    print(f"  Høyeste måned:      {annual['hoeyeste_maaned']['maaned']} ({annual['hoeyeste_maaned']['verdi']})")
    print(f"  Laveste måned:      {annual['laveste_maaned']['maaned']} ({annual['laveste_maaned']['verdi']})")

    # 5. Sammenlign med 2014
    sales_2014 = ts[-12:].sum()
    growth = (annual['aarlig_sum_prognose'] - sales_2014) / sales_2014 * 100
    print(f"\n--- Sammenligning med 2014 ---")
    print(f"  Salg 2014:          {int(sales_2014):,} enheter")
    print(f"  Prognose 2015:      {annual['aarlig_sum_prognose']:,} enheter")
    print(f"  Forventet vekst:    {growth:.1f}%")

    # 6. Generer plott
    print("\n--- Genererer prognoseplott ---")
    plot_forecast(ts, forecast_data, output_dir / 'sarima_forecast.png')
    plot_forecast_detail(ts, forecast_data, output_dir / 'sarima_forecast_detail.png')

    # 7. Lagre resultater
    # Konverter dates til strenger for JSON-serialisering
    forecast_results = {
        'prognoser': [
            {
                'maaned': d.strftime('%Y-%m'),
                'maaned_navn': d.strftime('%B %Y'),
                'prognose': int(round(f)),
                'nedre_95': int(round(l)),
                'ovre_95': int(round(u))
            }
            for d, f, l, u in zip(
                forecast_data['dates'],
                forecast_data['forecast'],
                forecast_data['lower'],
                forecast_data['upper']
            )
        ],
        'aarssammendrag': annual,
        'sammenligning_2014': {
            'salg_2014': int(sales_2014),
            'prognose_2015': annual['aarlig_sum_prognose'],
            'vekst_prosent': round(growth, 1)
        },
        'modell': 'SARIMA(1,1,1)(0,1,1)[12]',
        'konfidensnivu': '95%'
    }

    results_path = output_dir / 'forecast_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(forecast_results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")

    # Lagre CSV for enkel bruk
    csv_path = output_dir / 'forecast_2015.csv'
    forecast_table.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"CSV lagret: {csv_path}")

    # Oppsummering
    print(f"\n{'='*60}")
    print("KONKLUSJON")
    print(f"{'='*60}")
    print(f"""
  SARIMA(1,1,1)(0,1,1)[12] prognose for 2015:

  - Totalt forventet salg: {annual['aarlig_sum_prognose']:,} traktorer
  - 95% konfidensintervall: [{annual['aarlig_sum_nedre']:,}, {annual['aarlig_sum_ovre']:,}]
  - Forventet vekst fra 2014: {growth:.1f}%

  Sesongmoensteret fortsetter:
  - Hoeysesong: Juli-August (hoeyest salg)
  - Lavsesong: November (lavest salg)

  Begrensninger:
  - Prognosen forutsetter at historiske moenstre fortsetter
  - Uventede hendelser (markedsendringer, etc.) er ikke inkludert
  - Konfidensintervallene blir bredere lenger frem i tid
    """)


if __name__ == '__main__':
    main()
