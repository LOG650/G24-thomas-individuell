"""
Steg 5: Sensitivitetsanalyse
============================
Undersoker hvordan bullwhip-ratioen hos fabrikken (trinn 4) avhenger av
    - leveringstid L (1..4 uker)
    - gjennomgangsperiode R (1..4 uker)
    - sikkerhetslagrets z-verdi (0.8, 1.28, 1.65, 2.05)

Output:
    - output/sensitivity.csv
    - output/bullwhip_sensitivity.png
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


def run_scenario(demand: np.ndarray, L: int, R: int, z: float, shared: bool) -> float:
    """Kjor en simulering og returner bullwhip-ratioen hos fabrikken.

    Skalerer startlageret proporsjonalt med (L + R) slik at pipelinen ikke
    gjor start-situasjonen til en kunstig buffer.
    """
    init_inv = int(100 * (L + R) + 100)
    tiers = [
        Tier(name=n, lead_time=L, review_period=R, service_z=z,
             initial_inventory=init_inv)
        for n in ['Detaljist', 'Grossist', 'Distributor', 'Fabrikk']
    ]
    result = simulate_chain(demand, tiers=tiers, shared_information=shared)
    ratios = bullwhip_ratios(result, warmup=max(10, L + R + 5))
    return ratios[-1]


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 5: SENSITIVITETSANALYSE')
    print('=' * 60)

    demand = generate_demand().values

    L_values = [1, 2, 3, 4]
    R_values = [1, 2]
    z_values = [0.84, 1.28, 1.65, 2.05]  # 80%, 90%, 95%, 98%

    records = []

    # (a) Varier L, holder R=1, z=1.65
    for L in L_values:
        bw_dec = run_scenario(demand, L=L, R=1, z=1.65, shared=False)
        bw_shr = run_scenario(demand, L=L, R=1, z=1.65, shared=True)
        records.append({'variabel': 'L', 'verdi': L, 'bw_dec': bw_dec, 'bw_shr': bw_shr})

    # (b) Varier R, holder L=2, z=1.65
    for R in R_values:
        bw_dec = run_scenario(demand, L=2, R=R, z=1.65, shared=False)
        bw_shr = run_scenario(demand, L=2, R=R, z=1.65, shared=True)
        records.append({'variabel': 'R', 'verdi': R, 'bw_dec': bw_dec, 'bw_shr': bw_shr})

    # (c) Varier z, holder L=2, R=1
    for z in z_values:
        bw_dec = run_scenario(demand, L=2, R=1, z=z, shared=False)
        bw_shr = run_scenario(demand, L=2, R=1, z=z, shared=True)
        records.append({'variabel': 'z', 'verdi': z, 'bw_dec': bw_dec, 'bw_shr': bw_shr})

    df = pd.DataFrame(records)
    df.to_csv(OUTPUT_DIR / 'sensitivity.csv', index=False)
    print(df.to_string(index=False))

    # Plott - tre paneler
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))

    def _plot_panel(ax, variable_name: str, xlabel: str) -> None:
        sub = df[df['variabel'] == variable_name]
        x = sub['verdi'].values
        ax.plot(x, sub['bw_dec'].values, 'o-',
                color='#961D1C', linewidth=2, markersize=7,
                label='Desentralisert')
        ax.plot(x, sub['bw_shr'].values, 's-',
                color='#307453', linewidth=2, markersize=7,
                label='Delt informasjon')
        ax.axhline(1.0, color='#556270', linestyle='--', linewidth=1, alpha=0.6)
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel('Bullwhip-ratio (fabrikk)', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best', fontsize=9)

    _plot_panel(axes[0], 'L', 'Leveringstid $L$ (uker)')
    _plot_panel(axes[1], 'R', 'Gjennomgangsperiode $R$ (uker)')
    _plot_panel(axes[2], 'z', r'Servicenivaa $z$')

    fig.suptitle('Sensitivitet av bullwhip-ratioen hos fabrikken',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'bullwhip_sensitivity.png',
                dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {OUTPUT_DIR / "bullwhip_sensitivity.png"}')

    # Lagre JSON-oppsummering
    summary = {
        'L_sweep': df[df['variabel'] == 'L'].to_dict(orient='records'),
        'R_sweep': df[df['variabel'] == 'R'].to_dict(orient='records'),
        'z_sweep': df[df['variabel'] == 'z'].to_dict(orient='records'),
    }
    with open(OUTPUT_DIR / 'sensitivity.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
