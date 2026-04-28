"""
Steg 4: Sensitivitetsanalyse
============================
Studerer hvordan optimal totalkostnad reagerer paa:
  - Endret produksjonskapasitet (alpha * W_t implisitt via alpha).
  - Endret etterspoersel (+/- 10 %, +/- 20 %).
  - Skyggeprisen for produksjonsskranken tolkes som marginal
    kostnadsreduksjon per ekstra enhet produksjonskapasitet.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import parameters, MONTHS_NO
from step03_lp_losning import build_and_solve

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

C_SHADOW = '#5A2C77'
C_FILL = '#BD94D7'


def sensitivity_demand(demand: np.ndarray, params: dict,
                       factors: np.ndarray) -> pd.DataFrame:
    rows = []
    for f in factors:
        d_scaled = np.round(demand * f).astype(int)
        res = build_and_solve(d_scaled, params)
        rows.append({
            'faktor': round(float(f), 3),
            'sum_demand': int(d_scaled.sum()),
            'obj': round(res['obj'], 2),
            'total_O': round(sum(res['O']), 2),
            'total_I': round(sum(res['I']), 2),
        })
    return pd.DataFrame(rows)


def sensitivity_capacity(demand: np.ndarray, params: dict,
                         alpha_values: np.ndarray) -> pd.DataFrame:
    rows = []
    for a in alpha_values:
        p = dict(params)
        p['alpha'] = int(a)
        res = build_and_solve(demand, p)
        rows.append({
            'alpha': int(a),
            'obj': round(res['obj'], 2),
            'total_O': round(sum(res['O']), 2),
            'total_P': round(sum(res['P']), 2),
        })
    return pd.DataFrame(rows)


def plot_shadow_prices(duals: np.ndarray, output_path: Path,
                       title: str, ylabel: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    t = np.arange(1, len(duals) + 1)
    ax.bar(t, duals, color=C_FILL, edgecolor=C_SHADOW, linewidth=1.1)
    ax.axhline(0, color='#556270', linewidth=0.8)
    ax.set_xticks(t)
    ax.set_xticklabels(MONTHS_NO, fontsize=10)
    ax.set_xlabel('$t$', fontsize=13)
    ax.set_ylabel(ylabel, fontsize=12)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='both', labelsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_demand_sensitivity(df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(df['faktor'] * 100 - 100, df['obj'] / 1e6,
            'o-', color='#1F6587', markersize=8, linewidth=1.8,
            markerfacecolor='#8CC8E5', markeredgecolor='#1F6587',
            markeredgewidth=1.3)
    ax.set_xlabel('Endring i etterspoersel (%)', fontsize=12)
    ax.set_ylabel('Total kostnad (mill. NOK)', fontsize=12)
    ax.set_title('Kostnadssensitivitet for etterspoerselssjokk',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)
    # Marker null-endring
    ax.axvline(0, color='#556270', linestyle=':', linewidth=1.0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 4: SENSITIVITETSANALYSE")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / 'boat_demand.csv')
    demand = df['etterspoersel'].values.astype(int)
    params = parameters()

    # 1) Skyggepriser fra baseline
    base = build_and_solve(demand, params)
    df_dual = pd.DataFrame({
        'maaned': MONTHS_NO,
        't': np.arange(1, params['T'] + 1),
        'dual_invbal': np.round(base['dual_invbal'], 2),
        'dual_prodcap': np.round(base['dual_prodcap'], 2),
    })
    df_dual.to_csv(OUTPUT_DIR / 'step04_duals.csv', index=False)

    plot_shadow_prices(
        np.array(base['dual_invbal']),
        OUTPUT_DIR / 'agglp_shadow_price.png',
        'Skyggepris for lagerbalanse-skranken (NOK / baat)',
        '$\\pi_t$ (NOK / baat)',
    )

    # 2) Sensitivitet til etterspoersel
    factors = np.array([0.80, 0.90, 1.00, 1.10, 1.20])
    df_dem = sensitivity_demand(demand, params, factors)
    df_dem.to_csv(OUTPUT_DIR / 'step04_demand_sensitivity.csv', index=False)
    print("\n-- Etterspoerselssensitivitet --")
    print(df_dem.to_string(index=False))
    plot_demand_sensitivity(df_dem, OUTPUT_DIR / 'agglp_sensitivity.png')

    # 3) Sensitivitet til produktivitet (alpha)
    alphas = np.array([3, 4, 5, 6])
    df_cap = sensitivity_capacity(demand, params, alphas)
    df_cap.to_csv(OUTPUT_DIR / 'step04_capacity_sensitivity.csv', index=False)
    print("\n-- Produktivitetssensitivitet --")
    print(df_cap.to_string(index=False))

    # 4) Oppsummering
    summary = {
        'max_dual_invbal': round(float(np.max(base['dual_invbal'])), 2),
        'mean_dual_invbal': round(float(np.mean(base['dual_invbal'])), 2),
        'max_dual_prodcap': round(float(np.max(np.abs(base['dual_prodcap']))), 2),
        'base_obj': round(base['obj'], 2),
        'obj_plus10': float(df_dem.loc[df_dem['faktor'] == 1.10, 'obj'].iloc[0]),
        'obj_minus10': float(df_dem.loc[df_dem['faktor'] == 0.90, 'obj'].iloc[0]),
        'obj_plus20': float(df_dem.loc[df_dem['faktor'] == 1.20, 'obj'].iloc[0]),
        'obj_minus20': float(df_dem.loc[df_dem['faktor'] == 0.80, 'obj'].iloc[0]),
    }
    with open(OUTPUT_DIR / 'step04_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    print(f"\nSkyggepris-statistikk og sensitiviteter lagret i {OUTPUT_DIR}")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
