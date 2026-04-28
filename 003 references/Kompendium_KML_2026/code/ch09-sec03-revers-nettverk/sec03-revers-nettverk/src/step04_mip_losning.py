"""
Steg 4: MIP-loesning
====================
Loeser det flertrinns reverse nettverket med PuLP + CBC. Lagrer optimal
objektverdi, aapne innsamlingssentre, aapne gjenvinningsanlegg, og de to
flytmatrisene (kunde -> innsamling og innsamling -> gjenvinning).

Genererer to figurer:
  * revnet_optimal_flows.png -- kart med aapne fasiliteter og flytlinjer
  * revnet_cost_breakdown.png -- kostnadsfordeling i den optimale losningen
"""

import json
import time
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

# Farger
C_CUST = '#1F6587'
C_CUST_FILL = '#8CC8E5'
C_IS_OPEN = '#307453'
C_IS_OPEN_FILL = '#97D4B7'
C_IS_CLOSED = '#556270'
C_IS_CLOSED_FILL = '#CBD5E1'
C_GV_OPEN = '#5A2C77'
C_GV_OPEN_FILL = '#BD94D7'
C_GV_CLOSED = '#9C540B'
C_GV_CLOSED_FILL = '#F6BA7C'
C_LINE_L1 = '#8CC8E5'    # primary lys
C_LINE_L2 = '#BD94D7'    # accent lys


def solve_revnet(df_cust: pd.DataFrame, df_is: pd.DataFrame, df_gv: pd.DataFrame,
                 D1: np.ndarray, D2: np.ndarray,
                 r_scale: float = 1.0) -> dict:
    model = build_revnet(df_cust, df_is, df_gv, D1, D2, r_scale=r_scale)
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', \
        f'Ikke optimal: {pulp.LpStatus[status]}'

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

    f = df_is['fast_kostnad'].to_numpy(dtype=float)
    g = df_gv['fast_kostnad'].to_numpy(dtype=float)
    p = df_gv['prosess_kost_per_tonn'].to_numpy(dtype=float)
    C1 = D1 * TRANSPORT_COST_L1_PER_TKM
    C2 = D2 * TRANSPORT_COST_L2_PER_TKM

    fixed_is = float((f * y).sum())
    fixed_gv = float((g * z).sum())
    trans_l1 = float((C1 * x).sum())
    trans_l2 = float((C2 * w).sum())
    proc_cost = float((p[None, :] * w).sum())
    obj = float(pulp.value(model.objective))

    return {
        'status': pulp.LpStatus[status],
        'obj': obj,
        'fixed_is': fixed_is,
        'fixed_gv': fixed_gv,
        'trans_l1': trans_l1,
        'trans_l2': trans_l2,
        'proc_cost': proc_cost,
        'y': y.tolist(),
        'z': z.tolist(),
        'x': x.tolist(),
        'w': w.tolist(),
    }


def assignment_frame(df_cust: pd.DataFrame, df_is: pd.DataFrame,
                     x: np.ndarray, D1: np.ndarray) -> pd.DataFrame:
    """For hver kunde: finn primaer innsamling (stoerste andel) og avstand."""
    primary = np.argmax(x, axis=0)
    rows = []
    for j, i in enumerate(primary):
        rows.append({
            'kunde': df_cust.iloc[j]['kunde'],
            'region': df_cust.iloc[j]['region'],
            'returvolum_tonn': int(df_cust.iloc[j]['returvolum_tonn']),
            'tildelt_IS': df_is.iloc[i]['id'],
            'IS_navn': df_is.iloc[i]['navn'],
            'avstand_km': round(float(D1[i, j]), 1),
        })
    return pd.DataFrame(rows)


def flow_l2_frame(df_is: pd.DataFrame, df_gv: pd.DataFrame,
                  w: np.ndarray, D2: np.ndarray) -> pd.DataFrame:
    rows = []
    n_is, n_gv = w.shape
    for i in range(n_is):
        for k in range(n_gv):
            if w[i, k] > 1e-6:
                rows.append({
                    'IS_id': df_is.iloc[i]['id'],
                    'IS_navn': df_is.iloc[i]['navn'],
                    'GV_id': df_gv.iloc[k]['id'],
                    'GV_navn': df_gv.iloc[k]['navn'],
                    'volum_tonn': round(float(w[i, k]), 1),
                    'avstand_km': round(float(D2[i, k]), 1),
                })
    return pd.DataFrame(rows)


def plot_optimal_flows(df_cust: pd.DataFrame, df_is: pd.DataFrame,
                       df_gv: pd.DataFrame, y: np.ndarray, z: np.ndarray,
                       x: np.ndarray, w: np.ndarray,
                       output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 9.2))

    # --- Ledd 1: kunde -> innsamling (tynne linjer, lys farge)
    n_is, n_k = x.shape
    dc_by_is = {i: (df_is.iloc[i]['lon'], df_is.iloc[i]['lat']) for i in range(n_is)}
    for j in range(n_k):
        i_star = int(np.argmax(x[:, j]))
        if x[i_star, j] < 1e-6:
            continue
        ax.plot([df_cust.iloc[j]['lon'], dc_by_is[i_star][0]],
                [df_cust.iloc[j]['lat'], dc_by_is[i_star][1]],
                color=C_LINE_L1, linewidth=0.7, alpha=0.7, zorder=1)

    # --- Ledd 2: innsamling -> gjenvinning (tykkere, skalerte linjer)
    n_gv = z.shape[0]
    pos_gv = {k: (df_gv.iloc[k]['lon'], df_gv.iloc[k]['lat']) for k in range(n_gv)}
    w_max = w.max() if w.max() > 0 else 1.0
    for i in range(n_is):
        if y[i] == 0:
            continue
        for k in range(n_gv):
            if w[i, k] < 1e-6:
                continue
            lw = 0.8 + 4.0 * (w[i, k] / w_max)
            ax.plot([dc_by_is[i][0], pos_gv[k][0]],
                    [dc_by_is[i][1], pos_gv[k][1]],
                    color=C_LINE_L2, linewidth=lw, alpha=0.75, zorder=2)

    # --- Kunder
    sizes = 10 + (df_cust['returvolum_tonn'] / df_cust['returvolum_tonn'].max()) * 120
    ax.scatter(df_cust['lon'], df_cust['lat'], s=sizes,
               c=C_CUST_FILL, edgecolor=C_CUST, linewidth=0.6,
               alpha=0.9, label=f'Kunder (n = {len(df_cust)})', zorder=3)

    # --- Innsamlingssentre
    open_is = y.astype(bool)
    closed_is = ~open_is
    ax.scatter(df_is.loc[closed_is, 'lon'], df_is.loc[closed_is, 'lat'],
               s=130, marker='s', c=C_IS_CLOSED_FILL, edgecolor=C_IS_CLOSED,
               linewidth=1.1, label=f'Lukket innsamling (n = {int(closed_is.sum())})',
               zorder=4)
    ax.scatter(df_is.loc[open_is, 'lon'], df_is.loc[open_is, 'lat'],
               s=200, marker='s', c=C_IS_OPEN_FILL, edgecolor=C_IS_OPEN,
               linewidth=1.6, label=f'Aapen innsamling (n = {int(open_is.sum())})',
               zorder=5)
    for _, row in df_is[open_is].iterrows():
        ax.annotate(row['navn'], (row['lon'], row['lat']),
                    xytext=(7, 7), textcoords='offset points',
                    fontsize=9, color=C_IS_OPEN, fontweight='bold')

    # --- Gjenvinningsanlegg
    open_gv = z.astype(bool)
    closed_gv = ~open_gv
    ax.scatter(df_gv.loc[closed_gv, 'lon'], df_gv.loc[closed_gv, 'lat'],
               s=220, marker='^', c=C_GV_CLOSED_FILL, edgecolor=C_GV_CLOSED,
               linewidth=1.3, label=f'Lukket gjenvinning (n = {int(closed_gv.sum())})',
               zorder=5)
    ax.scatter(df_gv.loc[open_gv, 'lon'], df_gv.loc[open_gv, 'lat'],
               s=310, marker='^', c=C_GV_OPEN_FILL, edgecolor=C_GV_OPEN,
               linewidth=2.0, label=f'Aapen gjenvinning (n = {int(open_gv.sum())})',
               zorder=6)
    for _, row in df_gv[open_gv].iterrows():
        ax.annotate(row['navn'], (row['lon'], row['lat']),
                    xytext=(8, -16), textcoords='offset points',
                    fontsize=10, color=C_GV_OPEN, fontweight='bold')

    ax.set_xlabel('Lengdegrad (deg E)', fontsize=11)
    ax.set_ylabel('Breddegrad (deg N)', fontsize=11)
    ax.set_title('Optimal flyt i reverst nettverk: kunder -> innsamling -> gjenvinning',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=8.5)
    ax.set_aspect(1.9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cost_breakdown(result: dict, output_path: Path) -> None:
    labels = ['Fast\ninnsamling', 'Fast\ngjenvinning',
              'Transport\nledd 1', 'Transport\nledd 2', 'Prosess-\nkostnad']
    values = np.array([
        result['fixed_is'], result['fixed_gv'],
        result['trans_l1'], result['trans_l2'], result['proc_cost']
    ]) / 1e6
    colors = ['#97D4B7', '#BD94D7', '#8CC8E5', '#F6BA7C', '#ED9F9E']
    edges = ['#307453', '#5A2C77', '#1F6587', '#9C540B', '#961D1C']

    fig, ax = plt.subplots(figsize=(10.0, 4.8))
    bars = ax.bar(labels, values, color=colors, edgecolor=edges, linewidth=1.3,
                  width=0.6)
    total = values.sum()
    for bar, v in zip(bars, values):
        pct = 100 * v / total if total > 0 else 0
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f'{v:.2f}\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=10, color='#1F2933')

    ax.set_ylabel('Kostnad (MNOK/aar)', fontsize=11)
    ax.set_title(f'Kostnadsfordeling: total = {total:.2f} MNOK/aar',
                 fontsize=12, fontweight='bold')
    ax.set_ylim(0, values.max() * 1.35)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 4: MIP-LOESNING (PuLP / CBC)")
    print("=" * 60)

    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    df_is = pd.read_csv(DATA_DIR / 'innsamling.csv')
    df_gv = pd.read_csv(DATA_DIR / 'gjenvinning.csv')
    D1 = pd.read_csv(OUTPUT_DIR / 'step02_dist_l1_km.csv', index_col=0).to_numpy()
    D2 = pd.read_csv(OUTPUT_DIR / 'step02_dist_l2_km.csv', index_col=0).to_numpy()

    t0 = time.time()
    result = solve_revnet(df_cust, df_is, df_gv, D1, D2)
    t1 = time.time()
    result['solve_time_s'] = round(t1 - t0, 3)

    y = np.array(result['y'])
    z = np.array(result['z'])
    x = np.array(result['x'])
    w = np.array(result['w'])

    open_is_ids = df_is[y.astype(bool)]['id'].tolist()
    open_is_names = df_is[y.astype(bool)]['navn'].tolist()
    open_gv_ids = df_gv[z.astype(bool)]['id'].tolist()
    open_gv_names = df_gv[z.astype(bool)]['navn'].tolist()

    assignment = assignment_frame(df_cust, df_is, x, D1)
    assignment.to_csv(OUTPUT_DIR / 'step04_assignment.csv', index=False)
    flow2 = flow_l2_frame(df_is, df_gv, w, D2)
    flow2.to_csv(OUTPUT_DIR / 'step04_flow_l2.csv', index=False)

    summary = {
        'status': result['status'],
        'obj_NOK': round(result['obj'], 2),
        'obj_MNOK': round(result['obj'] / 1e6, 3),
        'fixed_is_NOK': round(result['fixed_is'], 2),
        'fixed_gv_NOK': round(result['fixed_gv'], 2),
        'trans_l1_NOK': round(result['trans_l1'], 2),
        'trans_l2_NOK': round(result['trans_l2'], 2),
        'proc_NOK': round(result['proc_cost'], 2),
        'fixed_is_MNOK': round(result['fixed_is'] / 1e6, 3),
        'fixed_gv_MNOK': round(result['fixed_gv'] / 1e6, 3),
        'trans_l1_MNOK': round(result['trans_l1'] / 1e6, 3),
        'trans_l2_MNOK': round(result['trans_l2'] / 1e6, 3),
        'proc_MNOK': round(result['proc_cost'] / 1e6, 3),
        'antall_aapne_IS': int(y.sum()),
        'aapne_IS_ids': open_is_ids,
        'aapne_IS_navn': open_is_names,
        'antall_aapne_GV': int(z.sum()),
        'aapne_GV_ids': open_gv_ids,
        'aapne_GV_navn': open_gv_names,
        'solve_time_s': result['solve_time_s'],
        'snitt_avstand_l1_km': round(float(assignment['avstand_km'].mean()), 1),
        'maks_avstand_l1_km': round(float(assignment['avstand_km'].max()), 1),
        'snitt_avstand_l2_km': round(float(flow2['avstand_km'].mean()), 1) if not flow2.empty else 0.0,
        'maks_avstand_l2_km': round(float(flow2['avstand_km'].max()), 1) if not flow2.empty else 0.0,
        'total_retur_tonn': int(round(float(df_cust['returvolum_tonn'].sum()))),
    }
    with open(OUTPUT_DIR / 'step04_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step04_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    plot_optimal_flows(df_cust, df_is, df_gv, y, z, x, w,
                       OUTPUT_DIR / 'revnet_optimal_flows.png')
    plot_cost_breakdown(result, OUTPUT_DIR / 'revnet_cost_breakdown.png')


if __name__ == '__main__':
    main()
