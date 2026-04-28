"""
Steg 1: Datainnsamling for SARIMA-analyse
=========================================
Laster inn månedlige traktordata (144 observasjoner, jan 2003 - des 2014)
fra data/tractor-sales.csv og genererer tidsserieplott og deskriptiv statistikk.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'

def create_time_series() -> pd.Series:
    """Les traktorsalg fra CSV og returner tidsserie med månedsslutt-indeks."""
    df = pd.read_csv(DATA_DIR / 'tractor-sales.csv', parse_dates=['Month'])
    dates = pd.date_range(start=df['Month'].iloc[0], periods=len(df), freq='ME')
    return pd.Series(df['Sales'].values, index=dates, name='Traktorsalg')

def calculate_statistics(ts: pd.Series) -> dict:
    """Beregn deskriptiv statistikk."""
    stats = ts.describe()
    return {
        'antall': int(stats['count']),
        'gjennomsnitt': round(stats['mean'], 1),
        'standardavvik': round(stats['std'], 1),
        'minimum': int(stats['min']),
        'kvartil_25': round(stats['25%'], 1),
        'median': round(stats['50%'], 1),
        'kvartil_75': round(stats['75%'], 1),
        'maksimum': int(stats['max']),
    }

def plot_time_series(ts: pd.Series, output_path: Path) -> None:
    """Generer tidsserieplott med dobbel x-akse (t nederst, år øverst)."""
    fig, ax = plt.subplots(figsize=(10, 5))

    # Bruk numerisk x-akse (t = 1, 2, ..., 144)
    t = np.arange(1, len(ts) + 1)

    ax.plot(t, ts.values, 'b-', linewidth=1.2, label='Månedlig salg')

    # Legg til trendlinje
    z = np.polyfit(t, ts.values, 1)
    trend = np.poly1d(z)
    ax.plot(t, trend(t), 'r--', linewidth=1, alpha=0.7, label='Lineær trend')

    # Nedre x-akse: t
    ax.set_xlabel('$t$', fontsize=16)
    ax.set_ylabel('$Y_t$', fontsize=16, rotation=0, labelpad=15)
    ax.set_xlim(1, 144)
    ax.set_xticks([1, 25, 49, 73, 97, 121, 144])
    ax.tick_params(axis='both', labelsize=10)

    # Øvre x-akse: årstall
    ax2 = ax.twiny()
    ax2.set_xlim(ax.get_xlim())
    # Plasser årstall ved januar hvert andre år (t=1, 25, 49, 73, 97, 121)
    year_positions = [1, 25, 49, 73, 97, 121]
    year_labels = ['2003', '2005', '2007', '2009', '2011', '2013']
    ax2.set_xticks(year_positions)
    ax2.set_xticklabels(year_labels)
    ax2.tick_params(axis='x', labelsize=10)

    ax.set_title('Månedlig traktorsalg (2003-2014)', fontsize=12, fontweight='bold', pad=35)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")

def main():
    """Hovedfunksjon."""
    # Opprett output-mappe
    output_dir = Path(__file__).parent.parent / 'output'
    output_dir.mkdir(exist_ok=True)

    # Opprett tidsserie
    ts = create_time_series()
    print(f"\nTidsserie opprettet: {len(ts)} observasjoner")
    print(f"Periode: {ts.index[0].strftime('%b %Y')} - {ts.index[-1].strftime('%b %Y')}")

    # Beregn statistikk
    stats = calculate_statistics(ts)
    print("\n--- Deskriptiv statistikk ---")
    for key, value in stats.items():
        print(f"  {key}: {value}")

    # Lagre statistikk som JSON
    stats_path = output_dir / 'descriptive_stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {stats_path}")

    # Generer plott
    plot_path = output_dir / 'sarima_data_plot.png'
    plot_time_series(ts, plot_path)

if __name__ == '__main__':
    main()
