"""
Steg 1: Datainnsamling for M/M/1-analyse
========================================
Syntetisk datasett fra en tollstasjon i Oslo havn:
  - Ankomster av lastebiler modelleres som en Poisson-prosess
  - Betjeningstider modelleres som eksponensielt fordelte
Genererer histogrammer og empiriske estimater av lambda og my.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# --- Baseline-parametere for tollstasjonen ---------------------------------
# Enhet: 1 time. Gjennomsnittlig ankomstrate: 8 lastebiler/time.
# Gjennomsnittlig betjeningstid: 5 minutter = 1/12 time, slik at my = 12/time.
# Dette gir baseline-utnyttelse rho = 8/12 = 0,667 -- et godt driftsnivaa
# som gir hanterlig kolengde, men der stigende trafikk fort bringer oss
# mot utnyttelsesveggen.
LAMBDA_TRUE = 8.0   # ankomstrate (kjorety/time)
MU_TRUE = 12.0      # betjeningsrate (kjorety/time)
N_SAMPLES = 1000    # antall observasjoner (drift over ca 125 timer)
SEED = 20260420


def generer_data(lmbda: float, mu: float, n: int, seed: int) -> pd.DataFrame:
    """Generer n ankomster og betjeningstider."""
    rng = np.random.default_rng(seed)
    mellomankomst = rng.exponential(scale=1.0 / lmbda, size=n)
    betjeningstid = rng.exponential(scale=1.0 / mu, size=n)
    ankomsttid = np.cumsum(mellomankomst)
    return pd.DataFrame({
        'ankomsttid': ankomsttid,
        'mellomankomst': mellomankomst,
        'betjeningstid': betjeningstid,
    })


def empiriske_estimater(df: pd.DataFrame) -> dict:
    """Estimer lambda og my fra MLE paa eksponensielle data."""
    lam_hat = 1.0 / df['mellomankomst'].mean()
    mu_hat = 1.0 / df['betjeningstid'].mean()
    return {
        'lambda_sann': LAMBDA_TRUE,
        'mu_sann': MU_TRUE,
        'lambda_estimert': round(lam_hat, 3),
        'mu_estimert': round(mu_hat, 3),
        'rho_sann': round(LAMBDA_TRUE / MU_TRUE, 4),
        'rho_estimert': round(lam_hat / mu_hat, 4),
        'n': int(len(df)),
        'mellomankomst_mean': round(df['mellomankomst'].mean(), 4),
        'betjeningstid_mean': round(df['betjeningstid'].mean(), 4),
        'total_tid_timer': round(df['ankomsttid'].iloc[-1], 1),
    }


def plot_ankomster_og_betjening(df: pd.DataFrame, lmbda: float, mu: float,
                                 output_path: Path) -> None:
    """Histogrammer med tilpasset eksponensiell tetthet."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    # Mellomankomst-tider
    ax = axes[0]
    # Konverter til minutter for lesbarhet
    data_min = df['mellomankomst'].values * 60.0
    ax.hist(data_min, bins=30, density=True, color='#8CC8E5',
            edgecolor='#1F6587', alpha=0.9, label='Empirisk')
    x = np.linspace(0, data_min.max(), 400)
    # Tetthet for eksponensiell med middel 1/lambda (i timer).
    # I minutter: f(x) = (lambda/60) * exp(-lambda/60 * x)
    f_lam = (lmbda / 60.0) * np.exp(-(lmbda / 60.0) * x)
    ax.plot(x, f_lam, color='#1F6587', linewidth=2,
            label=fr'Eksp$(\lambda={lmbda:.0f}/\mathrm{{time}})$')
    ax.set_xlabel('Mellomankomst-tid (min)', fontsize=11)
    ax.set_ylabel('Tetthet', fontsize=11)
    ax.set_title('Mellomankomst-tider', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    # Betjeningstider
    ax = axes[1]
    data_min = df['betjeningstid'].values * 60.0
    ax.hist(data_min, bins=30, density=True, color='#97D4B7',
            edgecolor='#307453', alpha=0.9, label='Empirisk')
    x = np.linspace(0, data_min.max(), 400)
    f_mu = (mu / 60.0) * np.exp(-(mu / 60.0) * x)
    ax.plot(x, f_mu, color='#307453', linewidth=2,
            label=fr'Eksp$(\mu={mu:.0f}/\mathrm{{time}})$')
    ax.set_xlabel('Betjeningstid (min)', fontsize=11)
    ax.set_ylabel('Tetthet', fontsize=11)
    ax.set_title('Betjeningstider', fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING (Tollstasjon Oslo havn)")
    print("=" * 60)

    df = generer_data(LAMBDA_TRUE, MU_TRUE, N_SAMPLES, SEED)

    # Lagre data slik at senere steg kan laste samme datasett
    csv_path = DATA_DIR / 'tollstasjon.csv'
    df.to_csv(csv_path, index=False)
    print(f"Datasett lagret: {csv_path}  ({len(df)} rader)")

    estimater = empiriske_estimater(df)
    print("\n--- Empiriske estimater ---")
    for k, v in estimater.items():
        print(f"  {k}: {v}")

    # Kolmogorov-Smirnov test (tilleggskontroll: samsvarer med eksponensiell?)
    ks_lam = stats.kstest(df['mellomankomst'], 'expon',
                          args=(0, 1.0 / LAMBDA_TRUE))
    ks_mu = stats.kstest(df['betjeningstid'], 'expon',
                         args=(0, 1.0 / MU_TRUE))
    estimater['ks_lambda_pvalue'] = round(float(ks_lam.pvalue), 4)
    estimater['ks_mu_pvalue'] = round(float(ks_mu.pvalue), 4)

    results_path = OUTPUT_DIR / 'step01_results.json'
    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(estimater, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {results_path}")

    fig_path = OUTPUT_DIR / 'mm1_arrivals_service.png'
    plot_ankomster_og_betjening(df, LAMBDA_TRUE, MU_TRUE, fig_path)

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print(f"Observert ankomstrate  lambda_hat = {estimater['lambda_estimert']} /time")
    print(f"Observert betjeningsrate my_hat    = {estimater['mu_estimert']} /time")
    print(f"Empirisk utnyttelse    rho_hat    = {estimater['rho_estimert']}")


if __name__ == '__main__':
    main()
