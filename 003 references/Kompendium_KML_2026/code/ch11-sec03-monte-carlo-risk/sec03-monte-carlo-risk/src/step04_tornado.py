"""
Steg 4: Tornado-diagram
=======================
Sensitivitetsanalyse: en-om-gangen (one-factor-at-a-time) variasjon
av hver risikokilde. For hver driver kjorer vi Monte Carlo ved
lav-verdi og hoy-verdi og viser utslaget paa CVaR_0.95.

Output:
  - output/mcr_tornado.png         : klassisk tornado med positiv/negativ stolpe
  - output/mcr_tornado_results.json : effekten per driver
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    COLOR_INK,
    COLOR_S1,
    COLOR_S1_DARK,
    COLOR_S5,
    COLOR_S5_DARK,
    get_parameters,
)
from step03_monte_carlo import compute_risk_metrics, run_monte_carlo

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


DRIVERS = [
    # (navn, parameter, lav-verdi, hoy-verdi, beskrivelse)
    ('Etterspoersel std',       'demand_std',         1_000, 3_000,
     '$\\sigma_D$'),
    ('Gjennomsnittlig etterspoersel', 'demand_mean', 10_000, 14_000,
     '$\\mu_D$'),
    ('Leveringstid CV',         'lead_time_sdlog',    0.15,  0.45,
     '$\\sigma_{\\ln L}$'),
    ('Leverandorsviktsannsynlighet', 'supplier_fail_prob', 0.02, 0.15,
     '$p_F$'),
    ('Kostnad tapt salg',       'cost_lost_sale',     250.0, 650.0,
     '$c_{ls}$'),
    ('Kostnad hastekjoep',      'cost_expedite',      450.0, 700.0,
     '$c_{ex}$'),
]


def run_tornado(n_runs: int = 4_000) -> list[dict]:
    """For hver driver: beregn CVaR_0.95 ved lav og hoy verdi.

    Returnerer sortert etter absolutt spenn.
    """
    base_params = get_parameters()
    base_params['n_runs'] = n_runs
    # Baseline
    costs_base, _ = run_monte_carlo(base_params)
    base_cvar = compute_risk_metrics(costs_base)['CVaR_0_95']
    base_mean = compute_risk_metrics(costs_base)['mean']
    print(f'  Baseline CVaR = {base_cvar:,.0f} NOK'.replace(',', ' '))
    print(f'  Baseline E[C] = {base_mean:,.0f} NOK'.replace(',', ' '))

    results = []
    for name, key, low, high, symbol in DRIVERS:
        p_low = get_parameters()
        p_low['n_runs'] = n_runs
        p_low[key] = low
        costs_low, _ = run_monte_carlo(p_low, seed_offset=1)
        cvar_low = compute_risk_metrics(costs_low)['CVaR_0_95']

        p_high = get_parameters()
        p_high['n_runs'] = n_runs
        p_high[key] = high
        costs_high, _ = run_monte_carlo(p_high, seed_offset=2)
        cvar_high = compute_risk_metrics(costs_high)['CVaR_0_95']

        effect_low = cvar_low - base_cvar
        effect_high = cvar_high - base_cvar
        span = abs(cvar_high - cvar_low)

        print(f'  {name} [{low}, {high}]: CVaR low={cvar_low:,.0f}, '
              f'high={cvar_high:,.0f}, span={span:,.0f}'.replace(',', ' '))

        results.append({
            'name': name,
            'symbol': symbol,
            'param': key,
            'low': low,
            'high': high,
            'cvar_low': cvar_low,
            'cvar_high': cvar_high,
            'effect_low': effect_low,
            'effect_high': effect_high,
            'span': span,
        })

    results.sort(key=lambda r: r['span'], reverse=True)
    return base_cvar, results


def plot_tornado(base_cvar: float, results: list[dict],
                 output_path: Path) -> None:
    """Klassisk tornado: hver driver har to stolper (lav/hoy) om base."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    names = [r['name'] for r in results]
    effects_low = [r['effect_low'] / 1000 for r in results]
    effects_high = [r['effect_high'] / 1000 for r in results]

    y = np.arange(len(results))

    # Lav verdi (gjor ofte CVaR lavere => negativ)
    ax.barh(y, effects_low, color=COLOR_S1, edgecolor=COLOR_S1_DARK,
            label='Lav verdi', alpha=0.9)
    ax.barh(y, effects_high, color=COLOR_S5, edgecolor=COLOR_S5_DARK,
            label='Hoy verdi', alpha=0.9)

    ax.axvline(0, color=COLOR_INK, linewidth=1)
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()  # stor effekt oeverst
    ax.set_xlabel(r'Endring i $\mathrm{CVaR}_{0{,}95}$ (kNOK)', fontsize=12)
    ax.set_title(r'Tornado-diagram: sensitivitet av $\mathrm{CVaR}_{0{,}95}$ '
                 r'mot hver risikokilde',
                 fontsize=12, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)
    ax.legend(loc='lower right', fontsize=10)

    # Annotate endring
    for i, r in enumerate(results):
        ax.text(r['effect_low'] / 1000, i,
                f' {r["effect_low"]/1000:+.0f}', va='center',
                ha='right' if r['effect_low'] < 0 else 'left',
                fontsize=9, color=COLOR_S1_DARK)
        ax.text(r['effect_high'] / 1000, i,
                f' {r["effect_high"]/1000:+.0f}', va='center',
                ha='right' if r['effect_high'] < 0 else 'left',
                fontsize=9, color=COLOR_S5_DARK)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 4: TORNADO-DIAGRAM')
    print('=' * 60)

    base_cvar, results = run_tornado(n_runs=4_000)

    # Lagre JSON
    out = {
        'base_cvar_0_95': round(base_cvar, 0),
        'drivers': [
            {
                'name': r['name'],
                'symbol': r['symbol'],
                'param': r['param'],
                'low': r['low'],
                'high': r['high'],
                'cvar_low': round(r['cvar_low'], 0),
                'cvar_high': round(r['cvar_high'], 0),
                'effect_low': round(r['effect_low'], 0),
                'effect_high': round(r['effect_high'], 0),
                'span': round(r['span'], 0),
            }
            for r in results
        ],
    }
    json_path = OUTPUT_DIR / 'mcr_tornado_results.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {json_path}')

    plot_tornado(base_cvar, results, OUTPUT_DIR / 'mcr_tornado.png')


if __name__ == '__main__':
    main()
