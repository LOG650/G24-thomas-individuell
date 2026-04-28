"""
Steg 4: MIP-loesning
====================
Loeser UFLP med PuLP + CBC. Lagrer optimal objektverdi, aapne lagre,
og en tildelingsmatrise. Genererer kart med de aapne DC-ene og
tildelingene av kunder (linje fra kunde til tilordnet DC).
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

C_CUST = '#1F6587'
C_CUST_FILL = '#8CC8E5'
C_DC_OPEN_FILL = '#97D4B7'
C_DC_OPEN = '#307453'
C_DC_CLOSED_FILL = '#CBD5E1'
C_DC_CLOSED = '#556270'
C_LINE = '#BD94D7'


def solve_uflp(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
               dist_km: np.ndarray,
               solver_time_limit: int | None = None) -> dict:
    model = build_uflp(df_dc, df_cust, dist_km)
    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=solver_time_limit)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', f'Ikke optimal: {pulp.LpStatus[status]}'

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

    # Transportkostnad
    c = dist_km * TRANSPORT_COST_PER_KM
    d = df_cust['etterspoersel'].to_numpy(dtype=float)
    f = df_dc['fast_kostnad'].to_numpy(dtype=float)

    fixed_cost = float((f * y).sum())
    trans_cost = float((c * d[None, :] * x).sum())
    obj = float(pulp.value(model.objective))

    return {
        'status': pulp.LpStatus[status],
        'obj': obj,
        'fixed_cost': fixed_cost,
        'transport_cost': trans_cost,
        'y': y.tolist(),
        'x': x.tolist(),
    }


def assignment_frame(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
                     x: np.ndarray, dist_km: np.ndarray) -> pd.DataFrame:
    """For hver kunde: finn 'primaer' DC (den med stoerst x_ij) og avstand."""
    primary = np.argmax(x, axis=0)
    rows = []
    for j, i in enumerate(primary):
        rows.append({
            'kunde': df_cust.iloc[j]['kunde'],
            'region': df_cust.iloc[j]['region'],
            'etterspoersel': int(df_cust.iloc[j]['etterspoersel']),
            'tildelt_DC': df_dc.iloc[i]['id'],
            'DC_navn': df_dc.iloc[i]['navn'],
            'andel': float(x[i, j]),
            'avstand_km': round(float(dist_km[i, j]), 1),
        })
    return pd.DataFrame(rows)


def plot_solution_map(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
                      y: np.ndarray, assignment: pd.DataFrame,
                      output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 9.0))

    # Forbindelselinjer kunde -> DC
    dc_by_id = {row['id']: (row['lon'], row['lat']) for _, row in df_dc.iterrows()}
    for _, row in assignment.iterrows():
        dc_x, dc_y = dc_by_id[row['tildelt_DC']]
        cust = df_cust[df_cust['kunde'] == row['kunde']].iloc[0]
        ax.plot([cust['lon'], dc_x], [cust['lat'], dc_y],
                color=C_LINE, linewidth=0.7, alpha=0.55, zorder=1)

    # Kunder
    sizes = 8 + (df_cust['etterspoersel'] / df_cust['etterspoersel'].max()) * 110
    ax.scatter(df_cust['lon'], df_cust['lat'], s=sizes,
               c=C_CUST_FILL, edgecolor=C_CUST, linewidth=0.6,
               alpha=0.9, label=f'Kunder (n = {len(df_cust)})', zorder=2)

    # DC-er: apne og lukkede
    open_mask = y.astype(bool)
    closed_mask = ~open_mask
    ax.scatter(df_dc.loc[closed_mask, 'lon'], df_dc.loc[closed_mask, 'lat'],
               s=140, marker='D',
               c=C_DC_CLOSED_FILL, edgecolor=C_DC_CLOSED, linewidth=1.2,
               label=f'Lukket DC (n = {int(closed_mask.sum())})', zorder=3)
    ax.scatter(df_dc.loc[open_mask, 'lon'], df_dc.loc[open_mask, 'lat'],
               s=220, marker='D',
               c=C_DC_OPEN_FILL, edgecolor=C_DC_OPEN, linewidth=1.8,
               label=f'Aapen DC (n = {int(open_mask.sum())})', zorder=4)

    for _, row in df_dc[open_mask].iterrows():
        ax.annotate(row['navn'], (row['lon'], row['lat']),
                    xytext=(7, 7), textcoords='offset points',
                    fontsize=9, color=C_DC_OPEN, fontweight='bold')

    ax.set_xlabel('Lengdegrad (deg E)', fontsize=11)
    ax.set_ylabel('Breddegrad (deg N)', fontsize=11)
    ax.set_title('Optimal UFLP-loesning: aapne DC-er og kundetildelinger',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=9)
    ax.set_aspect(1.9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cost_breakdown(result: dict, output_path: Path) -> None:
    labels = ['Faste kostnader\n(aapning av DC)', 'Transportkostnader']
    values = np.array([result['fixed_cost'], result['transport_cost']]) / 1e6
    colors = ['#97D4B7', '#8CC8E5']
    edges = ['#307453', '#1F6587']

    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    bars = ax.bar(labels, values, color=colors, edgecolor=edges, linewidth=1.3,
                  width=0.55)
    total = values.sum()
    for bar, v in zip(bars, values):
        pct = 100 * v / total if total > 0 else 0
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f'{v:.2f} MNOK\n({pct:.1f}%)',
                ha='center', va='bottom', fontsize=11, color='#1F2933')

    ax.set_ylabel('Kostnad (MNOK/aar)', fontsize=11)
    ax.set_title('Kostnadsfordeling i optimal UFLP-loesning',
                 fontsize=12, fontweight='bold')
    ax.set_ylim(0, values.max() * 1.3)
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

    df_dc = pd.read_csv(DATA_DIR / 'kandidater.csv')
    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    dist_km = pd.read_csv(OUTPUT_DIR / 'step02_dist_km.csv', index_col=0).to_numpy()

    import time
    t0 = time.time()
    result = solve_uflp(df_dc, df_cust, dist_km)
    t1 = time.time()
    result['solve_time_s'] = round(t1 - t0, 3)

    y = np.array(result['y'])
    x = np.array(result['x'])
    open_ids = df_dc[y.astype(bool)]['id'].tolist()
    open_names = df_dc[y.astype(bool)]['navn'].tolist()

    assignment = assignment_frame(df_dc, df_cust, x, dist_km)
    assignment.to_csv(OUTPUT_DIR / 'step04_assignment.csv', index=False)
    print(f"Tildeling lagret: {OUTPUT_DIR / 'step04_assignment.csv'}")

    summary = {
        'status': result['status'],
        'obj_NOK': round(result['obj'], 2),
        'obj_MNOK': round(result['obj'] / 1e6, 3),
        'fixed_cost_NOK': round(result['fixed_cost'], 2),
        'transport_cost_NOK': round(result['transport_cost'], 2),
        'andel_fast': round(100.0 * result['fixed_cost'] / result['obj'], 2),
        'andel_transport': round(100.0 * result['transport_cost'] / result['obj'], 2),
        'antall_aapne_DC': int(y.sum()),
        'aapne_DC_ids': open_ids,
        'aapne_DC_navn': open_names,
        'solve_time_s': result['solve_time_s'],
        'snitt_avstand_km': round(float(assignment['avstand_km'].mean()), 1),
        'maks_avstand_km': round(float(assignment['avstand_km'].max()), 1),
    }
    with open(OUTPUT_DIR / 'step04_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step04_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Figurer
    plot_solution_map(df_dc, df_cust, y, assignment,
                      OUTPUT_DIR / 'uflp_losning_kart.png')
    plot_cost_breakdown(result, OUTPUT_DIR / 'uflp_kostnadsbreakdown.png')


if __name__ == '__main__':
    main()
