"""
Steg 3: Monte Carlo-simulering (10 000 runs)
============================================
Kjor 10 000 uavhengige aar-simuleringer. For hver run beregnes total
aarskostnad. Empirisk kostnadsfordeling gir forventet verdi og
risikomaalene VaR_0.95 og CVaR_0.95.

Output:
  - output/mcr_cost_dist.png    : histogram av total aarskostnad
  - output/mcr_var_cvar.png     : histogram med VaR og CVaR markert
  - output/mcr_mc_results.json  : naikkeltall (gjennomsnitt, std, VaR, CVaR, ...)
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import (
    COLOR_INK,
    COLOR_S1,
    COLOR_S1_DARK,
    COLOR_S3,
    COLOR_S3_DARK,
    COLOR_S5,
    COLOR_S5_DARK,
    get_parameters,
)
from step02_basissimulering import simulate_single_run

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def run_monte_carlo(params: dict, n_runs: int | None = None,
                    seed_offset: int = 0) -> np.ndarray:
    """Kjor n_runs uavhengige ars-simuleringer og returner totalkostnader."""
    if n_runs is None:
        n_runs = params['n_runs']
    rng = np.random.default_rng(params['seed'] + seed_offset)
    costs = np.zeros(n_runs)
    breakdown = {'holding': np.zeros(n_runs),
                 'expedite': np.zeros(n_runs),
                 'lost_sales': np.zeros(n_runs)}
    for i in range(n_runs):
        run = simulate_single_run(params, rng)
        costs[i] = run['total_cost']
        breakdown['holding'][i] = run['holding_cost']
        breakdown['expedite'][i] = run['expedite_cost']
        breakdown['lost_sales'][i] = run['lost_sales_cost']
    return costs, breakdown


def compute_risk_metrics(costs: np.ndarray, alpha: float = 0.95) -> dict:
    """Beregn gjennomsnitt, std, VaR og CVaR for kostnadsfordelingen."""
    mean = float(np.mean(costs))
    std = float(np.std(costs, ddof=1))
    var_alpha = float(np.quantile(costs, alpha))
    cvar_alpha = float(np.mean(costs[costs >= var_alpha]))
    return {
        'alpha': alpha,
        'n_runs': int(costs.size),
        'mean': round(mean, 0),
        'std': round(std, 0),
        'min': round(float(costs.min()), 0),
        'max': round(float(costs.max()), 0),
        'q05': round(float(np.quantile(costs, 0.05)), 0),
        'q25': round(float(np.quantile(costs, 0.25)), 0),
        'median': round(float(np.quantile(costs, 0.50)), 0),
        'q75': round(float(np.quantile(costs, 0.75)), 0),
        'q95': round(var_alpha, 0),
        'VaR_0_95': round(var_alpha, 0),
        'CVaR_0_95': round(cvar_alpha, 0),
    }


def plot_cost_distribution(costs: np.ndarray, output_path: Path) -> None:
    """Histogram av totalkostnader med gjennomsnitt og median markert."""
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(costs / 1000, bins=60, color=COLOR_S1,
            edgecolor=COLOR_S1_DARK, alpha=0.85)
    mean = np.mean(costs) / 1000
    median = np.median(costs) / 1000
    ax.axvline(mean, color=COLOR_INK, linestyle='--', linewidth=1.5,
               label=f'Gj.snitt = {mean:,.0f} kNOK'.replace(',', ' '))
    ax.axvline(median, color=COLOR_S3_DARK, linestyle=':', linewidth=1.5,
               label=f'Median = {median:,.0f} kNOK'.replace(',', ' '))
    ax.set_xlabel('Total aarskostnad (kNOK)', fontsize=12)
    ax.set_ylabel('Frekvens', fontsize=12)
    ax.set_title('Fordeling av total aarskostnad (10 000 runs)',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def plot_var_cvar(costs: np.ndarray, metrics: dict, output_path: Path) -> None:
    """Histogram hvor hale >= VaR er uthevet, med VaR og CVaR annotert."""
    fig, ax = plt.subplots(figsize=(10, 5))

    var = metrics['VaR_0_95']
    cvar = metrics['CVaR_0_95']
    mean = metrics['mean']

    # Hovedhistogram
    below = costs[costs < var] / 1000
    above = costs[costs >= var] / 1000
    bins = np.linspace(costs.min() / 1000, costs.max() / 1000, 60)
    ax.hist(below, bins=bins, color=COLOR_S1, edgecolor=COLOR_S1_DARK,
            alpha=0.85, label=r'Kostnad $< \mathrm{VaR}_{0{,}95}$')
    ax.hist(above, bins=bins, color=COLOR_S5, edgecolor=COLOR_S5_DARK,
            alpha=0.85, label=r'Hale: kostnad $\geq \mathrm{VaR}_{0{,}95}$')

    # VaR og CVaR loddrette linjer
    ax.axvline(var / 1000, color=COLOR_S5_DARK, linestyle='--', linewidth=2,
               label=fr'$\mathrm{{VaR}}_{{0{{,}}95}} = {var/1000:,.0f}$ kNOK'
               .replace(',', ' '))
    ax.axvline(cvar / 1000, color=COLOR_INK, linestyle='-.', linewidth=2,
               label=fr'$\mathrm{{CVaR}}_{{0{{,}}95}} = {cvar/1000:,.0f}$ kNOK'
               .replace(',', ' '))
    ax.axvline(mean / 1000, color=COLOR_S3_DARK, linestyle=':', linewidth=1.5,
               label=fr'$E[C] = {mean/1000:,.0f}$ kNOK'.replace(',', ' '))

    ax.set_xlabel('Total aarskostnad (kNOK)', fontsize=12)
    ax.set_ylabel('Frekvens', fontsize=12)
    ax.set_title(r'Kostnadsfordeling med $\mathrm{VaR}_{0{,}95}$ og '
                 r'$\mathrm{CVaR}_{0{,}95}$',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 3: MONTE CARLO-SIMULERING (10 000 runs)')
    print('=' * 60)

    params = get_parameters()
    costs, breakdown = run_monte_carlo(params)
    metrics = compute_risk_metrics(costs, alpha=0.95)

    print('\n--- Risikomaal ---')
    for key, value in metrics.items():
        print(f'  {key}: {value}')

    # Kostnadsfordeling per kategori (gjennomsnitt)
    avg_breakdown = {k: float(np.mean(v)) for k, v in breakdown.items()}
    print('\n--- Gjennomsnittlig kostnadsfordeling ---')
    for k, v in avg_breakdown.items():
        print(f'  {k}: {v:,.0f} NOK'.replace(',', ' '))

    # Lagre alle kostnader (CSV for videre bruk) og metrics
    pd.DataFrame({'total_cost': costs,
                  'holding_cost': breakdown['holding'],
                  'expedite_cost': breakdown['expedite'],
                  'lost_sales_cost': breakdown['lost_sales']}).to_csv(
        OUTPUT_DIR / 'mcr_costs.csv', index=False)

    out = {
        'metrics': metrics,
        'avg_breakdown': {k: round(v, 0) for k, v in avg_breakdown.items()},
    }
    json_path = OUTPUT_DIR / 'mcr_mc_results.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {json_path}')

    plot_cost_distribution(costs, OUTPUT_DIR / 'mcr_cost_dist.png')
    plot_var_cvar(costs, metrics, OUTPUT_DIR / 'mcr_var_cvar.png')


if __name__ == '__main__':
    main()
