"""
Steg 1: Datainnsamling for M/M/c-dimensjonering
================================================
Genererer realistiske ankomst- og betjeningsdata for containerskip ved Oslo Havn
containerterminal. Produserer tidsserieplott og deskriptiv statistikk.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Bokens fargepalett (s1..s5 + dark-varianter)
COLOR_S1 = '#8CC8E5'
COLOR_S1D = '#1F6587'
COLOR_S2 = '#97D4B7'
COLOR_S2D = '#307453'
COLOR_S3 = '#F6BA7C'
COLOR_S3D = '#9C540B'
COLOR_S4 = '#BD94D7'
COLOR_S4D = '#5A2C77'
COLOR_S5 = '#ED9F9E'
COLOR_S5D = '#961D1C'
COLOR_ACCENT = '#5A2C77'


def generate_arrival_data(seed: int = 2026) -> pd.DataFrame:
    """
    Generer ankomstdata for containerskip og betjeningstider for kranoperasjonene.

    Antagelse: Poisson-ankomster med lambda = 2,4 skip/time i normal sesong.
    Betjeningstider er eksponentialfordelte med gjennomsnitt 1/mu = 20 min per skip
    (tilsvarer mu = 3,0 skip/time per kran).

    Returnerer DataFrame med kolonner:
      - ankomst_nummer
      - ankomst_tid (timer fra start av observasjonsvinduet)
      - mellomankomst (timer siden forrige skip)
      - betjeningstid (timer en kran bruker pa a losse skipet)
    """
    rng = np.random.default_rng(seed)

    lam = 2.4   # skip per time (ankomstrate)
    mu = 3.0    # skip per time per kran (betjeningsrate)

    n = 500     # antall observerte skipsankomster
    mellomankomst = rng.exponential(scale=1.0 / lam, size=n)
    ankomst_tid = np.cumsum(mellomankomst)
    betjening = rng.exponential(scale=1.0 / mu, size=n)

    df = pd.DataFrame({
        'ankomst_nummer': np.arange(1, n + 1),
        'ankomst_tid': ankomst_tid,
        'mellomankomst': mellomankomst,
        'betjeningstid': betjening,
    })
    return df


def calculate_statistics(df: pd.DataFrame) -> dict:
    """Beregn deskriptiv statistikk for ankomstintervaller og betjeningstider."""
    mellom = df['mellomankomst'].values
    betj = df['betjeningstid'].values

    lam_hat = 1.0 / mellom.mean()
    mu_hat = 1.0 / betj.mean()

    stats = {
        'antall_ankomster': int(len(df)),
        'observasjonsvindu_timer': float(df['ankomst_tid'].iloc[-1]),
        'gjennomsnittlig_mellomankomst_min': float(mellom.mean() * 60),
        'gjennomsnittlig_betjeningstid_min': float(betj.mean() * 60),
        'stddev_mellomankomst_min': float(mellom.std(ddof=1) * 60),
        'stddev_betjeningstid_min': float(betj.std(ddof=1) * 60),
        'estimert_lambda_per_time': float(lam_hat),
        'estimert_mu_per_time': float(mu_hat),
        'tilbudt_last_rho_total': float(lam_hat / mu_hat),
    }
    # Rund av for JSON
    for k, v in stats.items():
        if isinstance(v, float):
            stats[k] = round(v, 4)
    return stats


def plot_arrival_series(df: pd.DataFrame, output_path: Path) -> None:
    """Tidsserieplott av ankomster og kumulativ ankomstprosess over 24 timer."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

    mask = df['ankomst_tid'] <= 24.0
    sub = df[mask]

    # Topp: antall ankomster per time (histogram)
    bins = np.arange(0, 25, 1)
    axes[0].hist(sub['ankomst_tid'].values, bins=bins,
                 color=COLOR_S1, edgecolor=COLOR_S1D, alpha=0.85)
    axes[0].axhline(2.4, color=COLOR_S5D, linestyle='--', linewidth=1.5,
                    label=r'$\lambda = 2{,}4$ skip/time')
    axes[0].set_ylabel('Antall per time', fontsize=11)
    axes[0].set_title('Skipsankomster over 24 timer',
                      fontsize=12, fontweight='bold')
    axes[0].legend(loc='upper right', fontsize=10)
    axes[0].grid(True, alpha=0.3)

    # Bunn: fordeling av betjeningstider
    axes[1].hist(df['betjeningstid'].values * 60, bins=30,
                 color=COLOR_S2, edgecolor=COLOR_S2D, alpha=0.85, density=True)
    # Overlagre eksponentialfordeling
    x = np.linspace(0, (df['betjeningstid'].max() * 60), 200)
    mu_min = 1.0 / (df['betjeningstid'].mean() * 60)
    axes[1].plot(x, mu_min * np.exp(-mu_min * x), color=COLOR_S5D,
                 linewidth=1.8, label=r'Exp($1/\mu$)')
    axes[1].set_xlabel('Betjeningstid (minutter)', fontsize=11)
    axes[1].set_ylabel('Tetthet', fontsize=11)
    axes[1].set_title('Fordeling av betjeningstider per kran',
                      fontsize=12, fontweight='bold')
    axes[1].legend(loc='upper right', fontsize=10)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    df = generate_arrival_data()
    csv_path = DATA_DIR / 'containerterminal-ankomster.csv'
    df.to_csv(csv_path, index=False)
    print(f"Data lagret: {csv_path}")

    stats = calculate_statistics(df)
    print("\n--- Deskriptiv statistikk ---")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    stats_path = OUTPUT_DIR / 'step01_descriptive_stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Statistikk lagret: {stats_path}")

    plot_path = OUTPUT_DIR / 'mmc_arrivals.png'
    plot_arrival_series(df, plot_path)

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print(f"Observert lambda ~ {stats['estimert_lambda_per_time']:.3f} skip/time")
    print(f"Observert mu     ~ {stats['estimert_mu_per_time']:.3f} skip/time per kran")
    print(f"Tilbudt last rho ~ {stats['tilbudt_last_rho_total']:.3f} Erlang")
    print("Med en kran er rho > 1 -> systemet er ustabilt. Vi trenger flere kraner.")


if __name__ == '__main__':
    main()
