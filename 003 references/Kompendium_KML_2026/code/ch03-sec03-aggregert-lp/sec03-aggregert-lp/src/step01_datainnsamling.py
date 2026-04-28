"""
Steg 1: Datainnsamling
======================
Syntetisk 12-måneders etterspørselsdata for en norsk småbåtprodusent
(Fjordkraft Boats AS) med sesongpreg - sommertoppen dominerer.
Kostnads- og kapasitetsparametere spesifiseres og lagres til data/ og output/.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Pastell-palette (infografikk)
C_DEMAND = '#1F6587'      # primary / s1dark
C_CAPACITY = '#9C540B'    # s3dark
C_OVERTIME = '#5A2C77'    # s4dark / accent
C_INVENTORY = '#307453'   # s2dark
C_FILL_1 = '#8CC8E5'      # s1
C_FILL_3 = '#F6BA7C'      # s3
C_FILL_4 = '#BD94D7'      # s4


MONTHS_NO = ['Jan', 'Feb', 'Mar', 'Apr', 'Mai', 'Jun',
             'Jul', 'Aug', 'Sep', 'Okt', 'Nov', 'Des']


def generate_demand(seed: int = 42) -> np.ndarray:
    """12 maaneder syntetisk etterspoersel med tydelig sommertopp.

    Basisform: D_t = base + amp * sin(2 pi (t - phase) / 12) + noise
    Avrundet til heltall (antall baater).
    """
    rng = np.random.default_rng(seed)
    t = np.arange(1, 13)
    base = 120.0
    amp = 70.0
    phase = 3.5  # topp rundt juni-juli
    seasonal = base + amp * np.sin(2 * np.pi * (t - phase) / 12.0)
    noise = rng.normal(0, 5.0, size=12)
    demand = np.maximum(np.round(seasonal + noise).astype(int), 0)
    return demand


def parameters() -> dict:
    """Samle alle LP-parametere paa ett sted."""
    return {
        # Kostnader per enhet
        'c_P': 8000.0,    # Ordinaer produksjonskostnad per baat (NOK)
        'c_O': 11000.0,   # Overtidskostnad per baat (NOK)
        'c_I': 600.0,     # Lagerkostnad per baat per maaned (NOK)
        'c_H': 40000.0,   # Ansettelseskostnad per ansatt (NOK)
        'c_F': 60000.0,   # Oppsigelseskostnad per ansatt (NOK)
        # Kapasitet og arbeidskraft
        'K': 160,          # Ordinaer kapasitet (baater/mnd) ved startnivaa
        'O_max': 40,       # Maksimal overtidskapasitet per mnd
        'alpha': 4,        # Baater per ansatt per mnd (produktivitet)
        # Initialverdier
        'I_0': 20,         # Startlager
        'W_0': 40,         # Startarbeidsstyrke
        # Horisont
        'T': 12,
    }


def make_dataframe(demand: np.ndarray, params: dict) -> pd.DataFrame:
    df = pd.DataFrame({
        'maaned': MONTHS_NO,
        't': np.arange(1, params['T'] + 1),
        'etterspoersel': demand,
        'kapasitet': np.full(params['T'], params['K']),
        'overtid_max': np.full(params['T'], params['O_max']),
    })
    return df


def plot_demand_and_capacity(df: pd.DataFrame, params: dict, output_path: Path) -> None:
    """Soeyleplot av etterspoersel med kapasitetslinje (inkl. overtid)."""
    fig, ax = plt.subplots(figsize=(10, 5))
    t = df['t'].values
    ax.bar(t, df['etterspoersel'], color=C_FILL_1, edgecolor=C_DEMAND,
           linewidth=1.1, label='Etterspoersel $D_t$')
    ax.axhline(params['K'], color=C_CAPACITY, linestyle='--', linewidth=1.6,
               label=f"Ordinaer kapasitet $K = {params['K']}$")
    ax.axhline(params['K'] + params['O_max'], color=C_OVERTIME, linestyle=':',
               linewidth=1.6,
               label=f"Kapasitet + overtid $= {params['K'] + params['O_max']}$")

    ax.set_xticks(t)
    ax.set_xticklabels(df['maaned'], fontsize=10)
    ax.set_xlabel('$t$', fontsize=14)
    ax.set_ylabel('Antall baater', fontsize=12)
    ax.set_title('Maanedlig etterspoersel og produksjonskapasitet',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='both', labelsize=10)
    ax.set_ylim(0, max(df['etterspoersel'].max(), params['K'] + params['O_max']) * 1.15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    demand = generate_demand()
    params = parameters()
    df = make_dataframe(demand, params)

    # Lagre dataset
    csv_path = DATA_DIR / 'boat_demand.csv'
    df.to_csv(csv_path, index=False)
    print(f"Datasett lagret: {csv_path}")

    # Lagre parametere
    params_path = DATA_DIR / 'parameters.json'
    with open(params_path, 'w', encoding='utf-8') as f:
        json.dump(params, f, indent=2)
    print(f"Parametere lagret: {params_path}")

    # Enkel oppsummering
    print(f"\nEtterspoersel per maaned ({params['T']} mnd):")
    for m, d in zip(MONTHS_NO, demand):
        print(f"  {m}: {d}")
    print(f"\nSum etterspoersel: {int(demand.sum())}")
    print(f"Gjennomsnitt:      {demand.mean():.1f}")
    print(f"Maks (topp):       {int(demand.max())}")
    print(f"Min (bunn):        {int(demand.min())}")

    # Deskriptiv statistikk som JSON
    stats = {
        'antall_mnd': int(params['T']),
        'sum': int(demand.sum()),
        'gjennomsnitt': round(float(demand.mean()), 1),
        'std': round(float(demand.std(ddof=1)), 1),
        'min': int(demand.min()),
        'max': int(demand.max()),
        'topp_maaned': MONTHS_NO[int(np.argmax(demand))],
        'bunn_maaned': MONTHS_NO[int(np.argmin(demand))],
    }
    stats_path = OUTPUT_DIR / 'step01_stats.json'
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {stats_path}")

    # Figur
    plot_demand_and_capacity(df, params, OUTPUT_DIR / 'agglp_demand_capacity.png')


if __name__ == '__main__':
    main()
