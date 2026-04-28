"""
Steg 1: Datainnsamling
======================
Genererer syntetisk sluttkundeettersporsel over 104 uker (2 ar) for
et norsk FMCG-produkt (f.eks. sukker eller lettmelk) solgt gjennom en
4-trinns forsyningskjede. Ettersporselen folger et normalfordelt
basisnivaa med svak arssesong og en forhoyet periode rundt Black
Friday og jul (uke 47-52).

Output:
  - output/demand.csv               : ukentlig ettersporsel D_t
  - output/demand_stats.json        : deskriptiv statistikk
  - output/bullwhip_demand.png      : tidsserieplott av ettersporselen
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Farger (pastell-infografikk)
COLOR_S1 = '#8CC8E5'
COLOR_S1_DARK = '#1F6587'
COLOR_S3 = '#F6BA7C'
COLOR_S3_DARK = '#9C540B'
COLOR_INK = '#1F2933'


def generate_demand(n_weeks: int = 104, seed: int = 7) -> pd.Series:
    """Generer ukentlig sluttkundeettersporsel med trend, sesong og Black Friday-topp.

    Modellen er
        D_t = mu + A*sin(2*pi*t/52) + peak_t + eps_t
    med mu = 100, A = 10, peak = +40 i ukene 47-52 og eps_t ~ N(0, 5^2).
    """
    rng = np.random.default_rng(seed)
    t = np.arange(1, n_weeks + 1)
    mu = 100.0
    seasonal = 10.0 * np.sin(2.0 * np.pi * t / 52.0)
    peak = np.zeros(n_weeks)
    for year in range(n_weeks // 52 + 1):
        start = 47 + 52 * year
        end = 52 + 52 * year
        peak[(t >= start) & (t <= end)] = 40.0
    noise = rng.normal(0.0, 5.0, size=n_weeks)
    demand = np.clip(mu + seasonal + peak + noise, 0.0, None)
    return pd.Series(demand, index=pd.RangeIndex(1, n_weeks + 1, name='uke'), name='D_t')


def describe(demand: pd.Series) -> dict:
    """Deskriptiv statistikk for ettersporselen."""
    return {
        'antall_uker': int(len(demand)),
        'gjennomsnitt': round(float(demand.mean()), 2),
        'standardavvik': round(float(demand.std(ddof=1)), 2),
        'minimum': round(float(demand.min()), 2),
        'maksimum': round(float(demand.max()), 2),
        'varians': round(float(demand.var(ddof=1)), 2),
        'cv_prosent': round(100.0 * float(demand.std(ddof=1) / demand.mean()), 2),
    }


def plot_demand(demand: pd.Series, output_path: Path) -> None:
    """Plott ettersporselen med gjennomsnitt og Black Friday/jul-markering."""
    fig, ax = plt.subplots(figsize=(10, 4.5))
    t = demand.index.values
    y = demand.values
    mu = float(demand.mean())

    ax.plot(t, y, color=COLOR_S1_DARK, linewidth=1.3, label='$D_t$')
    ax.axhline(mu, color=COLOR_INK, linestyle='--', linewidth=1,
               label=fr'Gj.snitt $\bar{{D}} = {mu:.1f}$')

    # Marker Black Friday / jul-perioden
    for year in range(len(demand) // 52 + 1):
        start = 47 + 52 * year
        end = 52 + 52 * year
        if end <= len(demand):
            ax.axvspan(start, end, color=COLOR_S3, alpha=0.35,
                       label='Black Friday / jul' if year == 0 else None)

    ax.set_xlabel('Uke $t$', fontsize=13)
    ax.set_ylabel('$D_t$', fontsize=13, rotation=0, labelpad=15)
    ax.set_title('Ukentlig sluttkundeettersporsel over 104 uker',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)
    ax.set_xlim(1, len(demand))
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING')
    print('=' * 60)

    demand = generate_demand()
    csv_path = OUTPUT_DIR / 'demand.csv'
    demand.to_csv(csv_path, header=True)
    print(f'Ettersporsel lagret: {csv_path}')

    stats = describe(demand)
    print('\n--- Deskriptiv statistikk ---')
    for key, value in stats.items():
        print(f'  {key}: {value}')

    json_path = OUTPUT_DIR / 'demand_stats.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f'Statistikk lagret: {json_path}')

    plot_demand(demand, OUTPUT_DIR / 'bullwhip_demand.png')


if __name__ == '__main__':
    main()
