"""
Steg 5: Sensitivitetsanalyse
============================
To eksperimenter:

(a) p-median-variant: tving eksakt p antall DC-er aapne for
    p = 1, 2, ..., 10 og maal totalkostnad. Faste kostnader er inkludert.

(b) Skalering av faste aapningskostnader: multipliser f_i med en skaleringsfaktor
    beta in {0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0} og loes UFLP paa ny.

Resultatene vises som to figurer (kostnad vs p, kostnad vs beta) og
oppsummeringstabeller til LaTeX.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

from step02_avstandsmatrise import TRANSPORT_COST_PER_KM
from step03_mip_formulering import build_uflp

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def solve_uflp_with_p(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
                      dist_km: np.ndarray, p: int) -> dict:
    """Loes UFLP med ekstra skranke sum_i y_i = p."""
    model = build_uflp(df_dc, df_cust, dist_km)
    # Finn y-variabler og legg til skranken
    y_vars = [v for v in model.variables() if v.name.startswith('y_')]
    model += (pulp.lpSum(y_vars) == p), 'NumOpen'
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    if pulp.LpStatus[status] != 'Optimal':
        return {'status': pulp.LpStatus[status]}

    n = len(df_dc)
    m = len(df_cust)
    var_map = {v.name: v for v in model.variables()}
    y = np.array([int(round(pulp.value(var_map[f'y_{i}']))) for i in range(n)])
    x = np.zeros((n, m))
    for i in range(n):
        for j in range(m):
            v = var_map.get(f'x_{i}_{j}')
            if v is not None:
                x[i, j] = pulp.value(v) or 0.0
    f = df_dc['fast_kostnad'].to_numpy(dtype=float)
    d = df_cust['etterspoersel'].to_numpy(dtype=float)
    c = dist_km * TRANSPORT_COST_PER_KM

    fixed_cost = float((f * y).sum())
    trans_cost = float((c * d[None, :] * x).sum())
    return {
        'p': int(p),
        'status': 'Optimal',
        'obj': float(pulp.value(model.objective)),
        'fixed_cost': fixed_cost,
        'transport_cost': trans_cost,
        'num_open': int(y.sum()),
    }


def solve_uflp_scaled(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
                      dist_km: np.ndarray, beta: float) -> dict:
    """Skalere faste aapningskostnader med beta."""
    df_dc_scaled = df_dc.copy()
    df_dc_scaled['fast_kostnad'] = df_dc['fast_kostnad'] * beta
    model = build_uflp(df_dc_scaled, df_cust, dist_km)
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    n = len(df_dc)
    var_map = {v.name: v for v in model.variables()}
    y = np.array([int(round(pulp.value(var_map[f'y_{i}']))) for i in range(n)])
    f_scaled = df_dc_scaled['fast_kostnad'].to_numpy(dtype=float)
    fixed_cost = float((f_scaled * y).sum())
    obj = float(pulp.value(model.objective))
    return {
        'beta': float(beta),
        'status': pulp.LpStatus[status],
        'obj': obj,
        'fixed_cost': fixed_cost,
        'transport_cost': obj - fixed_cost,
        'num_open': int(y.sum()),
        'open_ids': df_dc[y.astype(bool)]['id'].tolist(),
    }


def plot_sensitivity_p(results: list[dict], output_path: Path) -> None:
    p = np.array([r['p'] for r in results])
    obj = np.array([r['obj'] / 1e6 for r in results])
    fixed = np.array([r['fixed_cost'] / 1e6 for r in results])
    trans = np.array([r['transport_cost'] / 1e6 for r in results])

    fig, ax = plt.subplots(figsize=(9.5, 5.2))

    ax.fill_between(p, 0, fixed, color='#97D4B7', alpha=0.85,
                    label='Faste aapningskostnader')
    ax.fill_between(p, fixed, fixed + trans, color='#8CC8E5', alpha=0.85,
                    label='Transportkostnader')
    ax.plot(p, obj, 'o-', color='#1F6587', linewidth=2.0, markersize=7,
            label='Totalkostnad')

    # Marker min
    j_min = int(np.argmin(obj))
    ax.axvline(p[j_min], color='#5A2C77', linestyle='--', linewidth=1.2)
    ax.annotate(f"Optimalt: p* = {p[j_min]}\nTot = {obj[j_min]:.2f} MNOK",
                xy=(p[j_min], obj[j_min]), xytext=(p[j_min] + 0.6, obj[j_min] + 1.2),
                fontsize=10, color='#5A2C77',
                arrowprops=dict(arrowstyle='->', color='#5A2C77'))

    ax.set_xlabel('Antall aapne DC-er, $p$', fontsize=11)
    ax.set_ylabel('Kostnad (MNOK/aar)', fontsize=11)
    ax.set_title('Sensitivitet: totalkostnad som funksjon av antall aapne DC-er',
                 fontsize=12, fontweight='bold')
    ax.set_xticks(p)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_sensitivity_fcost(results: list[dict], output_path: Path) -> None:
    betas = np.array([r['beta'] for r in results])
    n_open = np.array([r['num_open'] for r in results])
    obj = np.array([r['obj'] / 1e6 for r in results])

    fig, ax1 = plt.subplots(figsize=(9.5, 5.2))

    color1 = '#1F6587'
    ax1.plot(betas, obj, 'o-', color=color1, linewidth=2.0, markersize=7)
    ax1.set_xlabel(r'Skalering av fast aapningskostnad, $\beta$', fontsize=11)
    ax1.set_ylabel('Totalkostnad (MNOK/aar)', fontsize=11, color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    color2 = '#5A2C77'
    ax2.plot(betas, n_open, 's--', color=color2, linewidth=1.6, markersize=7)
    ax2.set_ylabel('Antall aapne DC-er', fontsize=11, color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_yticks(np.arange(int(n_open.min()), int(n_open.max()) + 1))

    ax1.set_title(r'Sensitivitet: hva skjer naar faste kostnader skaleres med $\beta$?',
                  fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: SENSITIVITETSANALYSE")
    print("=" * 60)

    df_dc = pd.read_csv(DATA_DIR / 'kandidater.csv')
    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    dist_km = pd.read_csv(OUTPUT_DIR / 'step02_dist_km.csv', index_col=0).to_numpy()

    # --- (a) p-median-sveip
    p_values = list(range(1, 11))
    results_p: list[dict] = []
    print("\n(a) p-median-sveip:")
    for p in p_values:
        r = solve_uflp_with_p(df_dc, df_cust, dist_km, p)
        results_p.append(r)
        print(f"  p={p}: obj={r['obj']/1e6:7.3f} MNOK "
              f"(faste={r['fixed_cost']/1e6:6.3f}, "
              f"trans={r['transport_cost']/1e6:6.3f})")

    pd.DataFrame(results_p).to_csv(OUTPUT_DIR / 'step05_p_median.csv', index=False)
    plot_sensitivity_p(results_p, OUTPUT_DIR / 'uflp_sensitivitet_p.png')

    # --- (b) Skalering av faste kostnader
    betas = [0.25, 0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    results_b: list[dict] = []
    print("\n(b) Faste aapningskostnader skalert med beta:")
    for beta in betas:
        r = solve_uflp_scaled(df_dc, df_cust, dist_km, beta)
        results_b.append(r)
        print(f"  beta={beta}: obj={r['obj']/1e6:7.3f} MNOK, "
              f"aapne={r['num_open']:2d}")

    pd.DataFrame([
        {k: v for k, v in r.items() if k != 'open_ids'} for r in results_b
    ]).to_csv(OUTPUT_DIR / 'step05_fcost_scaling.csv', index=False)
    plot_sensitivity_fcost(results_b, OUTPUT_DIR / 'uflp_sensitivitet_fkostnad.png')

    # --- Oppsummering
    p_star = int(np.argmin([r['obj'] for r in results_p]))
    summary = {
        'p_star': int(results_p[p_star]['p']),
        'obj_p_star_MNOK': round(results_p[p_star]['obj'] / 1e6, 3),
        'p_sweep_p_values': p_values,
        'p_sweep_obj_MNOK': [round(r['obj'] / 1e6, 3) for r in results_p],
        'beta_values': betas,
        'beta_num_open': [r['num_open'] for r in results_b],
        'beta_obj_MNOK': [round(r['obj'] / 1e6, 3) for r in results_b],
    }
    with open(OUTPUT_DIR / 'step05_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering lagret: {OUTPUT_DIR / 'step05_summary.json'}")


if __name__ == '__main__':
    main()
