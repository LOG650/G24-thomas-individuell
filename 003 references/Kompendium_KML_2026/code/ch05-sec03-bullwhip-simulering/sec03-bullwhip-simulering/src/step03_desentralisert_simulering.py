"""
Steg 3: Desentralisert simulering (lokal informasjon)
=====================================================
Kjorer simulatoren med shared_information=False. Hvert trinn
prognostiserer ut fra ordre-inngangen fra trinnet under.

Output:
    - output/orders_decentralized.csv
    - output/decentralized_stats.json
    - output/bullwhip_orders_decentralized.png
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import generate_demand
from step02_basismodell import Tier, bullwhip_ratios, simulate_chain

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Pastell-palett for fire trinn
COLORS = ['#1F6587', '#307453', '#9C540B', '#5A2C77']
COLOR_DEMAND = '#1F2933'


def plot_orders(result: dict, output_path: Path, title: str) -> None:
    """Plott ordre per trinn over tid, sammen med sluttkundeettersporselen."""
    fig, ax = plt.subplots(figsize=(10, 5))
    t = np.arange(1, result['T'] + 1)

    ax.plot(t, result['demand'], color=COLOR_DEMAND, linewidth=2.2,
            label='Sluttkunde $D_t$', zorder=5)
    for k, name in enumerate(result['tier_names']):
        ax.plot(t, result['orders_placed'][k], color=COLORS[k],
                linewidth=1.2, alpha=0.9, label=f'{name} $O_{{{k + 1},t}}$')

    ax.set_xlabel('Uke $t$', fontsize=13)
    ax.set_ylabel('Ordrekvantum', fontsize=13)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=9, ncol=2)
    ax.set_xlim(1, result['T'])
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 3: DESENTRALISERT SIMULERING')
    print('=' * 60)

    demand = generate_demand().values
    tiers = [Tier(name='Detaljist'), Tier(name='Grossist'),
             Tier(name='Distributor'), Tier(name='Fabrikk')]
    result = simulate_chain(demand, tiers=tiers, shared_information=False)

    # Bullwhip-ratio per trinn
    ratios = bullwhip_ratios(result, warmup=10)
    print('\n--- Bullwhip-ratioer (desentralisert) ---')
    print(f'  Var(D)      = {np.var(demand[10:], ddof=1):.2f}')
    for k, name in enumerate(result['tier_names']):
        var_o = float(np.var(result['orders_placed'][k, 10:], ddof=1))
        print(f'  {name:12s}  Var(O) = {var_o:8.2f}   BW = {ratios[k]:5.2f}')

    # Lagre ordreserier
    df = pd.DataFrame(result['orders_placed'].T, columns=result['tier_names'])
    df.insert(0, 'D_t', demand)
    df.index.name = 'uke'
    df.index = df.index + 1
    df.to_csv(OUTPUT_DIR / 'orders_decentralized.csv')
    print(f'\nOrdreserier lagret: {OUTPUT_DIR / "orders_decentralized.csv"}')

    # Lagre statistikk
    stats = {
        'shared_information': False,
        'var_demand': round(float(np.var(demand[10:], ddof=1)), 2),
        'per_tier': {
            name: {
                'var_order': round(float(np.var(result['orders_placed'][k, 10:], ddof=1)), 2),
                'mean_order': round(float(np.mean(result['orders_placed'][k, 10:])), 2),
                'bullwhip_ratio': round(ratios[k], 3),
            }
            for k, name in enumerate(result['tier_names'])
        },
    }
    with open(OUTPUT_DIR / 'decentralized_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f'Statistikk lagret: {OUTPUT_DIR / "decentralized_stats.json"}')

    # Plott
    plot_orders(result, OUTPUT_DIR / 'bullwhip_orders_decentralized.png',
                'Ordre per trinn - desentralisert (lokal informasjon)')


if __name__ == '__main__':
    main()
