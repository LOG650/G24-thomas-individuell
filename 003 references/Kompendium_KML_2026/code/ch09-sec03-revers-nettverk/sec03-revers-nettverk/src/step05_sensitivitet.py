"""
Steg 5: Sensitivitetsanalyse
============================
Tre eksperimenter:

(a) Returvolumvekst: multipliser r_j med rho i {0.50, 0.75, 1.00, 1.25,
    1.50, 2.00, 2.50} og loes paa nytt. Viser hvordan nettverket vokser
    naar volumet oeker (flere aapne innsamlingssentre, evt. flere
    gjenvinningsanlegg).

(b) Skalering av kapasitet paa innsamlingssentre: multipliser u_i med
    kappa i {0.5, 0.75, 1.0, 1.5, 2.0}. Viser hvor saerbart nettet er
    for at enkeltsentre er mindre enn antatt.

(c) Skalering av faste aapningskostnader for innsamling: multipliser
    f_i med beta i {0.5, 0.75, 1.0, 1.5, 2.0, 3.0}. Viser hvordan
    nettet konsolideres naar det blir dyrere aa aapne sentre.

Resultatene plottes som en kombifigur med tre panel.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

from step02_avstandsmatrise import (TRANSPORT_COST_L1_PER_TKM,
                                    TRANSPORT_COST_L2_PER_TKM)
from step03_mip_formulering import build_revnet

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def solve_parametric(df_cust: pd.DataFrame, df_is: pd.DataFrame,
                     df_gv: pd.DataFrame, D1: np.ndarray, D2: np.ndarray,
                     r_scale: float = 1.0,
                     cap_scale_is: float = 1.0,
                     fcost_scale_is: float = 1.0) -> dict:
    """Loeser modellen med parametriske endringer paa r, u, f."""
    df_is_mod = df_is.copy()
    df_is_mod['kapasitet_tonn'] = df_is['kapasitet_tonn'] * cap_scale_is
    df_is_mod['fast_kostnad'] = df_is['fast_kostnad'] * fcost_scale_is

    model = build_revnet(df_cust, df_is_mod, df_gv, D1, D2, r_scale=r_scale)
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    if pulp.LpStatus[status] != 'Optimal':
        return {'status': pulp.LpStatus[status]}

    n_is = len(df_is)
    n_gv = len(df_gv)
    n_k = len(df_cust)
    var_map = {v.name: v for v in model.variables()}

    y = np.array([int(round(pulp.value(var_map[f'y_{i}']))) for i in range(n_is)])
    z = np.array([int(round(pulp.value(var_map[f'z_{k}']))) for k in range(n_gv)])
    x = np.zeros((n_is, n_k))
    w = np.zeros((n_is, n_gv))
    for i in range(n_is):
        for j in range(n_k):
            val = pulp.value(var_map[f'x_{i}_{j}'])
            x[i, j] = val if val is not None else 0.0
        for k in range(n_gv):
            val = pulp.value(var_map[f'w_{i}_{k}'])
            w[i, k] = val if val is not None else 0.0

    f_mod = df_is_mod['fast_kostnad'].to_numpy(dtype=float)
    g = df_gv['fast_kostnad'].to_numpy(dtype=float)
    p = df_gv['prosess_kost_per_tonn'].to_numpy(dtype=float)
    C1 = D1 * TRANSPORT_COST_L1_PER_TKM
    C2 = D2 * TRANSPORT_COST_L2_PER_TKM

    return {
        'status': 'Optimal',
        'obj': float(pulp.value(model.objective)),
        'fixed_is': float((f_mod * y).sum()),
        'fixed_gv': float((g * z).sum()),
        'trans_l1': float((C1 * x).sum()),
        'trans_l2': float((C2 * w).sum()),
        'proc_cost': float((p[None, :] * w).sum()),
        'num_open_is': int(y.sum()),
        'num_open_gv': int(z.sum()),
        'open_is_ids': df_is[y.astype(bool)]['id'].tolist(),
        'open_gv_ids': df_gv[z.astype(bool)]['id'].tolist(),
    }


def _plot_subplot(ax, xs, obj, n_is, n_gv, xlabel, title, baseline_x):
    color_obj = '#1F6587'
    color_is = '#307453'
    color_gv = '#5A2C77'

    ax.plot(xs, obj, 'o-', color=color_obj, linewidth=2.0, markersize=7,
            label='Totalkostnad (MNOK)')
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel('Totalkostnad (MNOK/aar)', fontsize=10.5, color=color_obj)
    ax.tick_params(axis='y', labelcolor=color_obj)
    ax.grid(True, alpha=0.3)
    ax.set_title(title, fontsize=11, fontweight='bold')
    ax.axvline(baseline_x, color='#CBD5E1', linestyle=':', linewidth=1.0)

    ax2 = ax.twinx()
    ax2.plot(xs, n_is, 's--', color=color_is, linewidth=1.4, markersize=6,
             label='# aapne innsamling')
    ax2.plot(xs, n_gv, '^--', color=color_gv, linewidth=1.4, markersize=7,
             label='# aapne gjenvinning')
    ax2.set_ylabel('Antall aapne', fontsize=10.5)
    ymax = max(max(n_is), max(n_gv)) + 1
    ax2.set_yticks(np.arange(0, ymax + 1))
    ax2.set_ylim(0, ymax)

    # Combine legends
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=8.5)


def plot_sensitivity(rho_values, rho_res,
                     cap_values, cap_res,
                     fcost_values, fcost_res,
                     output_path: Path) -> None:
    fig, axes = plt.subplots(1, 3, figsize=(16.5, 5.2))

    obj_r = [r['obj'] / 1e6 for r in rho_res]
    nis_r = [r['num_open_is'] for r in rho_res]
    ngv_r = [r['num_open_gv'] for r in rho_res]
    _plot_subplot(axes[0], rho_values, obj_r, nis_r, ngv_r,
                  r'Skalering av returvolum, $\rho$',
                  r'(a) Vekst i returvolum', baseline_x=1.0)

    obj_c = [r['obj'] / 1e6 for r in cap_res]
    nis_c = [r['num_open_is'] for r in cap_res]
    ngv_c = [r['num_open_gv'] for r in cap_res]
    _plot_subplot(axes[1], cap_values, obj_c, nis_c, ngv_c,
                  r'Skalering av IS-kapasitet, $\kappa$',
                  r'(b) Kapasitet paa innsamling', baseline_x=1.0)

    obj_b = [r['obj'] / 1e6 for r in fcost_res]
    nis_b = [r['num_open_is'] for r in fcost_res]
    ngv_b = [r['num_open_gv'] for r in fcost_res]
    _plot_subplot(axes[2], fcost_values, obj_b, nis_b, ngv_b,
                  r'Skalering av fast IS-kostnad, $\beta$',
                  r'(c) Faste aapningskostnader', baseline_x=1.0)

    fig.suptitle('Sensitivitetsanalyse for det reverse nettverket',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: SENSITIVITETSANALYSE")
    print("=" * 60)

    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    df_is = pd.read_csv(DATA_DIR / 'innsamling.csv')
    df_gv = pd.read_csv(DATA_DIR / 'gjenvinning.csv')
    D1 = pd.read_csv(OUTPUT_DIR / 'step02_dist_l1_km.csv', index_col=0).to_numpy()
    D2 = pd.read_csv(OUTPUT_DIR / 'step02_dist_l2_km.csv', index_col=0).to_numpy()

    # (a) Returvolumvekst
    # Total IS-kapasitet er 16 100 tonn; baseline-volumet er ~8 600 tonn,
    # sa rho maksimalt kan vaere ~1.87 for at problemet skal vaere mulig.
    rho_values = [0.50, 0.75, 1.00, 1.10, 1.25, 1.50, 1.75]
    rho_res = []
    print("\n(a) Returvolum skalert med rho:")
    for rho in rho_values:
        r = solve_parametric(df_cust, df_is, df_gv, D1, D2, r_scale=rho)
        r['rho'] = rho
        if r.get('status') != 'Optimal':
            print(f"  rho={rho:.2f}: IKKE MULIG ({r.get('status')})")
            r['obj'] = float('nan')
            r['num_open_is'] = 0
            r['num_open_gv'] = 0
        else:
            print(f"  rho={rho:.2f}: obj={r['obj']/1e6:7.3f} MNOK, "
                  f"IS={r['num_open_is']}, GV={r['num_open_gv']}")
        rho_res.append(r)

    # (b) Kapasitetsskalering paa IS.  Med kappa=0.5 er total kapasitet
    # ~8 050 < 8 632 tonn -> ikke mulig.  Vi starter derfor paa 0.75.
    cap_values = [0.75, 1.0, 1.25, 1.5, 2.0]
    cap_res = []
    print("\n(b) IS-kapasitet skalert med kappa:")
    for cap in cap_values:
        r = solve_parametric(df_cust, df_is, df_gv, D1, D2, cap_scale_is=cap)
        r['kappa'] = cap
        if r.get('status') != 'Optimal':
            print(f"  kappa={cap:.2f}: IKKE MULIG ({r.get('status')})")
            r['obj'] = float('nan')
            r['num_open_is'] = 0
            r['num_open_gv'] = 0
        else:
            print(f"  kappa={cap:.2f}: obj={r['obj']/1e6:7.3f} MNOK, "
                  f"IS={r['num_open_is']}, GV={r['num_open_gv']}")
        cap_res.append(r)

    # (c) Fast kostnad paa IS
    fcost_values = [0.5, 0.75, 1.0, 1.5, 2.0, 3.0]
    fcost_res = []
    print("\n(c) Fast IS-kostnad skalert med beta:")
    for beta in fcost_values:
        r = solve_parametric(df_cust, df_is, df_gv, D1, D2, fcost_scale_is=beta)
        r['beta'] = beta
        if r.get('status') != 'Optimal':
            print(f"  beta={beta:.2f}: IKKE MULIG ({r.get('status')})")
            r['obj'] = float('nan')
            r['num_open_is'] = 0
            r['num_open_gv'] = 0
        else:
            print(f"  beta={beta:.2f}: obj={r['obj']/1e6:7.3f} MNOK, "
                  f"IS={r['num_open_is']}, GV={r['num_open_gv']}")
        fcost_res.append(r)

    # Lagre CSV-er
    pd.DataFrame([{k: v for k, v in r.items() if k not in ('open_is_ids', 'open_gv_ids')}
                  for r in rho_res]).to_csv(OUTPUT_DIR / 'step05_rho.csv', index=False)
    pd.DataFrame([{k: v for k, v in r.items() if k not in ('open_is_ids', 'open_gv_ids')}
                  for r in cap_res]).to_csv(OUTPUT_DIR / 'step05_kappa.csv', index=False)
    pd.DataFrame([{k: v for k, v in r.items() if k not in ('open_is_ids', 'open_gv_ids')}
                  for r in fcost_res]).to_csv(OUTPUT_DIR / 'step05_beta.csv', index=False)

    # Figur
    plot_sensitivity(rho_values, rho_res, cap_values, cap_res,
                     fcost_values, fcost_res,
                     OUTPUT_DIR / 'revnet_sensitivitet.png')

    # Oppsummering
    summary = {
        'rho_values': rho_values,
        'rho_num_open_is': [r['num_open_is'] for r in rho_res],
        'rho_num_open_gv': [r['num_open_gv'] for r in rho_res],
        'rho_obj_MNOK': [round(r['obj'] / 1e6, 3) for r in rho_res],
        'kappa_values': cap_values,
        'kappa_num_open_is': [r['num_open_is'] for r in cap_res],
        'kappa_num_open_gv': [r['num_open_gv'] for r in cap_res],
        'kappa_obj_MNOK': [round(r['obj'] / 1e6, 3) for r in cap_res],
        'beta_values': fcost_values,
        'beta_num_open_is': [r['num_open_is'] for r in fcost_res],
        'beta_num_open_gv': [r['num_open_gv'] for r in fcost_res],
        'beta_obj_MNOK': [round(r['obj'] / 1e6, 3) for r in fcost_res],
    }
    with open(OUTPUT_DIR / 'step05_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering lagret: {OUTPUT_DIR / 'step05_summary.json'}")


if __name__ == '__main__':
    main()
