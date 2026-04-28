"""
Steg 4: MIP-loesning
====================
Loeser WDP med PuLP + CBC. Sammenligner med naiv tildeling (steg 2).

Figurer:
  * wdp_mip_allocation.png -- stolpediagram med optimal tildeling,
    fargelagt per leverandor og tegnet slik at bundler er gruppert
  * wdp_cost_compare.png -- side-ved-side sammenligning av naiv vs MIP
"""

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

from step03_mip_formulering import build_bids, build_wdp

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

C_S1_FILL = '#8CC8E5'
C_S1_DARK = '#1F6587'
C_S2_FILL = '#97D4B7'
C_S2_DARK = '#307453'
C_S3_FILL = '#F6BA7C'
C_S3_DARK = '#9C540B'
C_S4_FILL = '#BD94D7'
C_S4_DARK = '#5A2C77'
C_S5_FILL = '#ED9F9E'
C_S5_DARK = '#961D1C'
C_TEXT = '#1F2933'

SUP_COLOR = {
    'L1': (C_S1_FILL, C_S1_DARK),
    'L2': (C_S2_FILL, C_S2_DARK),
    'L3': (C_S3_FILL, C_S3_DARK),
    'L4': (C_S4_FILL, C_S4_DARK),
}


def solve_wdp(df_bids: pd.DataFrame, df_cat: pd.DataFrame,
              df_sup: pd.DataFrame,
              diversification: bool = False) -> dict:
    model, x = build_wdp(df_bids, df_cat, df_sup,
                         diversification=diversification)
    solver = pulp.PULP_CBC_CMD(msg=False)
    t0 = time.time()
    status = model.solve(solver)
    t1 = time.time()
    if pulp.LpStatus[status] != 'Optimal':
        return {'status': pulp.LpStatus[status]}

    selected = []
    for _, bid in df_bids.iterrows():
        val = pulp.value(x[bid['bud_id']])
        if val is not None and val > 0.5:
            selected.append(bid['bud_id'])

    df_sel = df_bids[df_bids['bud_id'].isin(selected)].copy()

    # Bygg kategori-allokering
    cat_rows = []
    for _, c in df_cat.iterrows():
        for _, bid in df_sel.iterrows():
            if c['kategori'] in bid['kategorier']:
                cat_rows.append({
                    'kategori': c['kategori'],
                    'navn': c['navn'],
                    'volum': int(c['volum']),
                    'vinner': bid['leverandoer'],
                    'bud_id': bid['bud_id'],
                    'bud_type': bid['type'],
                    'linjekost_NOK': float(
                        bid['totalkost_NOK'] / len(bid['kategorier'])),
                })
                break
    df_alloc = pd.DataFrame(cat_rows)

    # Finn faktiske linjekostnader: ved en bundle har hver kategori
    # sin egen pris_per_enhet*volum (ikke gjennomsnitt)
    df_unit = pd.read_csv(DATA_DIR / 'enkeltbud.csv')
    df_bundle = pd.read_csv(DATA_DIR / 'bundlebud.csv')
    for i, row in df_alloc.iterrows():
        if row['bud_type'] == 'enkelt':
            m = df_unit[df_unit['bud_id'] == row['bud_id']].iloc[0]
            df_alloc.at[i, 'linjekost_NOK'] = float(m['linekost_NOK'])
        else:
            m = df_bundle[(df_bundle['bud_id'] == row['bud_id'])
                          & (df_bundle['kategori'] == row['kategori'])].iloc[0]
            df_alloc.at[i, 'linjekost_NOK'] = float(m['linekost_NOK'])

    total = float(df_alloc['linjekost_NOK'].sum())
    return {
        'status': pulp.LpStatus[status],
        'obj': float(pulp.value(model.objective)),
        'total_faktisk': total,
        'solve_time_s': round(t1 - t0, 3),
        'selected_bids': selected,
        'df_alloc': df_alloc,
        'df_selected': df_sel,
    }


def plot_mip_allocation(df_alloc: pd.DataFrame, df_sup: pd.DataFrame,
                        output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 5.4))

    costs = df_alloc['linjekost_NOK'].to_numpy() / 1e6
    winners = df_alloc['vinner'].tolist()
    types = df_alloc['bud_type'].tolist()
    bud_ids = df_alloc['bud_id'].tolist()
    labels = df_alloc['kategori'].tolist()

    x_pos = np.arange(len(labels))
    colors = [SUP_COLOR[w][0] for w in winners]
    edges = [SUP_COLOR[w][1] for w in winners]
    hatches = ['' if t == 'enkelt' else '//' for t in types]

    bars = ax.bar(x_pos, costs, color=colors, edgecolor=edges, linewidth=1.4,
                  width=0.68)
    for bar, h in zip(bars, hatches):
        bar.set_hatch(h)

    for bar, w, v, bid in zip(bars, winners, costs, bud_ids):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(costs) * 0.01,
                f'{w}\n{bid}\n{v:.2f} MNOK',
                ha='center', va='bottom', fontsize=8.5, color=C_TEXT)

    ax.set_xticks(x_pos)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_xlabel('Kategori', fontsize=11)
    ax.set_ylabel('Linjekostnad (MNOK)', fontsize=11)
    total = costs.sum()
    ax.set_title(f'MIP-tildeling (WDP): optimal kontraktsplan (total = '
                 f'{total:.2f} MNOK)',
                 fontsize=12, fontweight='bold', color=C_TEXT)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, max(costs) * 1.35)

    # Kombinert legend: leverandoer + bundle-markering
    handles = []
    seen = set()
    for w in winners:
        if w in seen:
            continue
        seen.add(w)
        sup_name = df_sup[df_sup['leverandoer'] == w]['navn'].iloc[0]
        handles.append(plt.Rectangle((0, 0), 1, 1,
                                     facecolor=SUP_COLOR[w][0],
                                     edgecolor=SUP_COLOR[w][1],
                                     linewidth=1.2,
                                     label=f'{w}: {sup_name}'))
    handles.append(plt.Rectangle((0, 0), 1, 1, facecolor='white',
                                 edgecolor=C_TEXT, hatch='//', linewidth=1.2,
                                 label='Bundle-bud (alt-eller-ingenting)'))
    ax.legend(handles=handles, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cost_compare(naiv_total: float, mip_total: float,
                      naiv_alloc: pd.DataFrame, mip_alloc: pd.DataFrame,
                      output_path: Path) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.7),
                                    gridspec_kw={'width_ratios': [1.0, 1.6]})

    # Panel 1: total-sammenligning
    methods = ['Naiv\n(laveste enkeltbud)', 'MIP (WDP)']
    totals = np.array([naiv_total, mip_total]) / 1e6
    colors = [C_S3_FILL, C_S2_FILL]
    edges = [C_S3_DARK, C_S2_DARK]
    bars = ax1.bar(methods, totals, color=colors, edgecolor=edges,
                   linewidth=1.6, width=0.5)
    for bar, v in zip(bars, totals):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 f'{v:.2f} MNOK', ha='center', va='bottom', fontsize=11,
                 color=C_TEXT)
    diff = totals[0] - totals[1]
    diff_pct = 100 * diff / totals[0]
    ax1.set_ylabel('Totalkostnad (MNOK)', fontsize=11)
    ax1.set_title(f'Besparelse: {diff:.2f} MNOK ({diff_pct:.1f} %)',
                  fontsize=11, fontweight='bold')
    ax1.set_ylim(0, totals.max() * 1.15)
    ax1.grid(True, alpha=0.3, axis='y')

    # Panel 2: fordeling per leverandoer for begge metoder
    sup_list = ['L1', 'L2', 'L3', 'L4']
    naiv_share = {s: 0.0 for s in sup_list}
    for _, r in naiv_alloc.iterrows():
        naiv_share[r['vinner']] += r['linekost_NOK']
    mip_share = {s: 0.0 for s in sup_list}
    for _, r in mip_alloc.iterrows():
        mip_share[r['vinner']] += r['linjekost_NOK']

    xs = np.arange(len(sup_list))
    width = 0.36
    n_vals = np.array([naiv_share[s] / 1e6 for s in sup_list])
    m_vals = np.array([mip_share[s] / 1e6 for s in sup_list])
    b1 = ax2.bar(xs - width / 2, n_vals, width=width,
                 color=C_S3_FILL, edgecolor=C_S3_DARK, linewidth=1.3,
                 label='Naiv')
    b2 = ax2.bar(xs + width / 2, m_vals, width=width,
                 color=C_S2_FILL, edgecolor=C_S2_DARK, linewidth=1.3,
                 label='MIP (WDP)')
    for bars in (b1, b2):
        for bar in bars:
            h = bar.get_height()
            if h > 0:
                ax2.text(bar.get_x() + bar.get_width() / 2, h,
                         f'{h:.1f}', ha='center', va='bottom', fontsize=9,
                         color=C_TEXT)
    ax2.set_xticks(xs)
    ax2.set_xticklabels(sup_list, fontsize=10)
    ax2.set_xlabel('Leverandoer', fontsize=11)
    ax2.set_ylabel('Tildelt verdi (MNOK)', fontsize=11)
    ax2.set_title('Fordeling per leverandoer', fontsize=11, fontweight='bold')
    ax2.legend(loc='upper right', fontsize=9)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 4: MIP-LOESNING (PuLP + CBC)")
    print("=" * 60)

    df_cat = pd.read_csv(DATA_DIR / 'kategorier.csv')
    df_sup = pd.read_csv(DATA_DIR / 'leverandorer.csv')
    df_unit = pd.read_csv(DATA_DIR / 'enkeltbud.csv')
    df_bundle = pd.read_csv(DATA_DIR / 'bundlebud.csv')

    df_bids = build_bids(df_unit, df_bundle)
    result = solve_wdp(df_bids, df_cat, df_sup, diversification=False)
    assert result['status'] == 'Optimal', f"Ikke optimal: {result['status']}"

    df_alloc = result['df_alloc']
    df_alloc.to_csv(OUTPUT_DIR / 'step04_mip_alloc.csv', index=False)

    # Les naiv losning
    naiv_alloc = pd.read_csv(OUTPUT_DIR / 'step02_naiv_alloc.csv')
    naiv_total = float(naiv_alloc['linekost_NOK'].sum())
    mip_total = float(result['total_faktisk'])

    # Andel per leverandoer
    total_ref = mip_total
    per_sup = {}
    for _, r in df_alloc.iterrows():
        per_sup.setdefault(r['vinner'], 0.0)
        per_sup[r['vinner']] += r['linjekost_NOK']
    per_sup_andel = {k: round(v / total_ref, 4) for k, v in per_sup.items()}

    summary = {
        'status': result['status'],
        'obj_NOK': round(result['obj'], 2),
        'total_faktisk_NOK': round(mip_total, 2),
        'total_MNOK': round(mip_total / 1e6, 3),
        'naiv_total_NOK': round(naiv_total, 2),
        'naiv_total_MNOK': round(naiv_total / 1e6, 3),
        'besparelse_NOK': round(naiv_total - mip_total, 2),
        'besparelse_MNOK': round((naiv_total - mip_total) / 1e6, 3),
        'besparelse_pct': round(100 * (naiv_total - mip_total) / naiv_total, 2),
        'antall_valgte_bud': int(len(result['selected_bids'])),
        'valgte_bud': result['selected_bids'],
        'solve_time_s': result['solve_time_s'],
        'andel_per_leverandoer_MIP': per_sup_andel,
    }
    with open(OUTPUT_DIR / 'step04_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step04_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    plot_mip_allocation(df_alloc, df_sup, OUTPUT_DIR / 'wdp_mip_allocation.png')
    plot_cost_compare(naiv_total, mip_total, naiv_alloc, df_alloc,
                      OUTPUT_DIR / 'wdp_cost_compare.png')


if __name__ == '__main__':
    main()
