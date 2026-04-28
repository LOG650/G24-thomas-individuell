"""
Steg 4: Delt informasjon (sentralisert prognose)
================================================
Kjorer simulatoren med shared_information=True. Alle trinn ser
sluttkundeettersporselen D_t og bruker denne i prognosen.

Output:
    - output/orders_shared.csv
    - output/shared_stats.json
    - output/bullwhip_orders_shared.png
    - output/bullwhip_variance_amplification.png
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import generate_demand
from step02_basismodell import Tier, bullwhip_ratios, simulate_chain
from step03_desentralisert_simulering import plot_orders

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Farger
COLOR_DEC = '#ED9F9E'
COLOR_DEC_DARK = '#961D1C'
COLOR_SHR = '#97D4B7'
COLOR_SHR_DARK = '#307453'


def plot_variance_amplification(
    ratios_dec: list[float],
    ratios_shr: list[float],
    tier_names: list[str],
    output_path: Path,
) -> None:
    """Stolpediagram: bullwhip-ratio per trinn, desentralisert vs delt info."""
    x = np.arange(len(tier_names))
    width = 0.38

    fig, ax = plt.subplots(figsize=(9, 5))
    ax.bar(x - width / 2, ratios_dec, width,
           label='Desentralisert', color=COLOR_DEC,
           edgecolor=COLOR_DEC_DARK, linewidth=1.2)
    ax.bar(x + width / 2, ratios_shr, width,
           label='Delt informasjon', color=COLOR_SHR,
           edgecolor=COLOR_SHR_DARK, linewidth=1.2)
    ax.axhline(1.0, color='#556270', linestyle='--', linewidth=1,
               label='BW = 1 (ingen forsterkning)')

    for i, (rd, rs) in enumerate(zip(ratios_dec, ratios_shr)):
        ax.text(i - width / 2, rd, f'{rd:.2f}', ha='center', va='bottom',
                fontsize=9, color=COLOR_DEC_DARK)
        ax.text(i + width / 2, rs, f'{rs:.2f}', ha='center', va='bottom',
                fontsize=9, color=COLOR_SHR_DARK)

    ax.set_xticks(x)
    ax.set_xticklabels(tier_names, fontsize=11)
    ax.set_ylabel(r'Bullwhip-ratio  $\mathrm{Var}(O_k) / \mathrm{Var}(D)$',
                  fontsize=12)
    ax.set_title('Variansforsterkning oppstrom i forsyningskjeden',
                 fontsize=12, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 4: DELT INFORMASJON (SENTRALISERT)')
    print('=' * 60)

    demand = generate_demand().values
    tiers = [Tier(name='Detaljist'), Tier(name='Grossist'),
             Tier(name='Distributor'), Tier(name='Fabrikk')]

    # Delt informasjon
    result_shr = simulate_chain(demand, tiers=tiers, shared_information=True)
    ratios_shr = bullwhip_ratios(result_shr, warmup=10)

    # Desentralisert (for sammenligning)
    tiers_d = [Tier(name='Detaljist'), Tier(name='Grossist'),
               Tier(name='Distributor'), Tier(name='Fabrikk')]
    result_dec = simulate_chain(demand, tiers=tiers_d, shared_information=False)
    ratios_dec = bullwhip_ratios(result_dec, warmup=10)

    print('\n--- Bullwhip-ratioer ---')
    print(f'{"Trinn":12s}{"Desentralisert":>18s}{"Delt info":>18s}')
    for k, name in enumerate(result_shr['tier_names']):
        print(f'{name:12s}{ratios_dec[k]:>18.3f}{ratios_shr[k]:>18.3f}')

    # Lagre CSV
    df = pd.DataFrame(result_shr['orders_placed'].T, columns=result_shr['tier_names'])
    df.insert(0, 'D_t', demand)
    df.index.name = 'uke'
    df.index = df.index + 1
    df.to_csv(OUTPUT_DIR / 'orders_shared.csv')
    print(f'\nOrdreserier lagret: {OUTPUT_DIR / "orders_shared.csv"}')

    stats = {
        'shared_information': True,
        'var_demand': round(float(np.var(demand[10:], ddof=1)), 2),
        'per_tier': {
            name: {
                'bullwhip_decentralized': round(ratios_dec[k], 3),
                'bullwhip_shared': round(ratios_shr[k], 3),
                'reduction_pct': round(
                    100.0 * (ratios_dec[k] - ratios_shr[k]) / ratios_dec[k], 1
                ) if ratios_dec[k] > 0 else 0.0,
            }
            for k, name in enumerate(result_shr['tier_names'])
        },
    }
    with open(OUTPUT_DIR / 'shared_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f'Statistikk lagret: {OUTPUT_DIR / "shared_stats.json"}')

    # Plott
    plot_orders(result_shr, OUTPUT_DIR / 'bullwhip_orders_shared.png',
                'Ordre per trinn - delt informasjon')
    plot_variance_amplification(ratios_dec, ratios_shr,
                                list(result_shr['tier_names']),
                                OUTPUT_DIR / 'bullwhip_variance_amplification.png')


if __name__ == '__main__':
    main()
