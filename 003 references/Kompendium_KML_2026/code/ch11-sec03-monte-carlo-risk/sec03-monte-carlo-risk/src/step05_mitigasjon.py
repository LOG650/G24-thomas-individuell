"""
Steg 5: Mitigasjonstiltak
=========================
Evaluerer tre mitigasjonstiltak ved a endre modellparametre og
re-kjore Monte Carlo:
  1. Hoyere sikkerhetslager (fra 400 -> 800 enheter)
  2. Dobbel sourcing: reduserer leverandorsviktsannsynlighet
     p_F fra 0.08 til 0.02 og kostnad hastekjoep faller litt
     (lettere tilgang paa alternativ leverandor).
  3. Kombinasjon av begge tiltakene.

For hver strategi beregnes E[C], VaR_0.95 og CVaR_0.95 og
sammenlignes med baseline.

Output:
  - output/mcr_mitigation.png       : fire histogram + oppsummeringspanel
  - output/mcr_mitigation.json      : sammenligning av risikomaal
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    COLOR_INK,
    COLOR_S1,
    COLOR_S1_DARK,
    COLOR_S2,
    COLOR_S2_DARK,
    COLOR_S3,
    COLOR_S3_DARK,
    COLOR_S5,
    COLOR_S5_DARK,
    get_parameters,
)
from step03_monte_carlo import compute_risk_metrics, run_monte_carlo

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def run_strategy(name: str, overrides: dict, n_runs: int = 6_000,
                 seed_offset: int = 0) -> dict:
    """Kjor MC for en strategi og returner metrics + costs."""
    params = get_parameters()
    params['n_runs'] = n_runs
    params.update(overrides)
    costs, _ = run_monte_carlo(params, seed_offset=seed_offset)
    metrics = compute_risk_metrics(costs)
    print(f'  {name}: E[C]={metrics["mean"]:,.0f}  '
          f'VaR={metrics["VaR_0_95"]:,.0f}  '
          f'CVaR={metrics["CVaR_0_95"]:,.0f}'.replace(',', ' '))
    return {'name': name, 'costs': costs, 'metrics': metrics,
            'overrides': overrides}


def plot_mitigation(strategies: list[dict], output_path: Path) -> None:
    """Fire histogram side ved side + panel med risikomaal."""
    fig = plt.figure(figsize=(13.5, 7.5))
    gs = fig.add_gridspec(2, 4, hspace=0.35, wspace=0.30)

    colors = [COLOR_S5, COLOR_S1, COLOR_S2, COLOR_S3]
    edges = [COLOR_S5_DARK, COLOR_S1_DARK, COLOR_S2_DARK, COLOR_S3_DARK]

    # Felles x-akse
    all_costs = np.concatenate([s['costs'] for s in strategies])
    xmin, xmax = all_costs.min() / 1000, all_costs.max() / 1000
    bins = np.linspace(xmin, xmax, 50)

    # Oeverste rad: histogram per strategi
    for i, (strat, c, e) in enumerate(zip(strategies, colors, edges)):
        ax = fig.add_subplot(gs[0, i])
        ax.hist(strat['costs'] / 1000, bins=bins, color=c, edgecolor=e,
                alpha=0.85)
        var = strat['metrics']['VaR_0_95'] / 1000
        cvar = strat['metrics']['CVaR_0_95'] / 1000
        ax.axvline(var, color=COLOR_S5_DARK, linestyle='--', linewidth=1.3)
        ax.axvline(cvar, color=COLOR_INK, linestyle='-.', linewidth=1.3)
        ax.set_title(strat['name'], fontsize=10, fontweight='bold')
        ax.set_xlabel('kNOK', fontsize=9)
        if i == 0:
            ax.set_ylabel('Frekvens', fontsize=9)
        ax.grid(True, alpha=0.3)

    # Nederste rad: sammenligning av E[C], VaR, CVaR
    ax = fig.add_subplot(gs[1, :])
    names = [s['name'] for s in strategies]
    means = [s['metrics']['mean'] / 1000 for s in strategies]
    vars_ = [s['metrics']['VaR_0_95'] / 1000 for s in strategies]
    cvars = [s['metrics']['CVaR_0_95'] / 1000 for s in strategies]

    x = np.arange(len(names))
    width = 0.25
    ax.bar(x - width, means, width, color=COLOR_S1, edgecolor=COLOR_S1_DARK,
           label='$E[C]$')
    ax.bar(x, vars_, width, color=COLOR_S3, edgecolor=COLOR_S3_DARK,
           label=r'$\mathrm{VaR}_{0{,}95}$')
    ax.bar(x + width, cvars, width, color=COLOR_S5, edgecolor=COLOR_S5_DARK,
           label=r'$\mathrm{CVaR}_{0{,}95}$')

    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=10)
    ax.set_ylabel('Kostnad (kNOK)', fontsize=11)
    ax.set_title('Risikomaal per strategi', fontsize=11, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)

    # Annotate tall
    for xi, m, v, c in zip(x, means, vars_, cvars):
        ax.text(xi - width, m + 5, f'{m:.0f}', ha='center', fontsize=8)
        ax.text(xi, v + 5, f'{v:.0f}', ha='center', fontsize=8)
        ax.text(xi + width, c + 5, f'{c:.0f}', ha='center', fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 5: MITIGASJONSTILTAK')
    print('=' * 60)

    strategies = []
    strategies.append(run_strategy(
        'Baseline', {}, n_runs=6_000, seed_offset=10))
    strategies.append(run_strategy(
        'Hoyere sikkerhetslager', {'safety_stock_units': 800},
        n_runs=6_000, seed_offset=20))
    strategies.append(run_strategy(
        'Dobbel sourcing',
        {'supplier_fail_prob': 0.02, 'cost_expedite': 500.0},
        n_runs=6_000, seed_offset=30))
    strategies.append(run_strategy(
        'Kombinert tiltak',
        {'safety_stock_units': 800, 'supplier_fail_prob': 0.02,
         'cost_expedite': 500.0},
        n_runs=6_000, seed_offset=40))

    # Lagre JSON
    out = {
        'strategies': [
            {
                'name': s['name'],
                'overrides': s['overrides'],
                'metrics': s['metrics'],
            }
            for s in strategies
        ],
    }
    json_path = OUTPUT_DIR / 'mcr_mitigation.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {json_path}')

    plot_mitigation(strategies, OUTPUT_DIR / 'mcr_mitigation.png')


if __name__ == '__main__':
    main()
