"""
Steg 6: Sensitivitet
====================
To scenarier som belyser robustheten i loesningen:

  (a) Leverandoer L3 trekker seg: fjerner alle bud fra L3 og loeser paa nytt.
  (b) Ny aggressiv budgiver: L2 leverer et nytt aggressivt bundle-bud som
      inkluderer doerer (C6) til lav pris; loeser paa nytt.

Formaalet er aa vise hvor raskt strukturen i tildelingen endres naar
tilbudsbildet endres, og hvor stor betydning enkeltbud har paa totalen.

Vi sammenligner tre varianter:
  * Baseline (uten endring)
  * Scenario A (L3 uten bud)
  * Scenario B (L2 legger til aggressivt nytt bundle-bud)

Resultater presenteres i en enkel sammenligningsfigur.
"""

import json
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


def solve_bids(df_bids: pd.DataFrame, df_cat: pd.DataFrame,
               df_sup: pd.DataFrame) -> dict:
    model, x = build_wdp(df_bids, df_cat, df_sup, diversification=False)
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    if pulp.LpStatus[status] != 'Optimal':
        return {'status': pulp.LpStatus[status]}
    selected = [bid_id for bid_id in df_bids['bud_id']
                if pulp.value(x[bid_id]) is not None
                and pulp.value(x[bid_id]) > 0.5]
    total = 0.0
    per_sup = {}
    bid_map = {row['bud_id']: row for _, row in df_bids.iterrows()}
    cat_assign = {}
    for bid_id in selected:
        bid = bid_map[bid_id]
        total += bid['totalkost_NOK']
        per_sup.setdefault(bid['leverandoer'], 0.0)
        per_sup[bid['leverandoer']] += bid['totalkost_NOK']
        for c in bid['kategorier']:
            cat_assign[c] = bid['leverandoer']
    return {
        'status': 'Optimal',
        'total_NOK': total,
        'per_sup_NOK': per_sup,
        'valgte_bud': selected,
        'cat_assign': cat_assign,
    }


def scenario_b_bids(df_unit: pd.DataFrame,
                    df_bundle: pd.DataFrame,
                    df_cat: pd.DataFrame) -> pd.DataFrame:
    """Scenario B: L2 legger til aggressivt nytt bundle-bud 'B7' som
    dekker C4+C5+C6 til lavere priser."""
    vol = {row['kategori']: int(row['volum']) for _, row in df_cat.iterrows()}
    new_rows = []
    # Aggressivt bundle-bud fra L2 paa isolasjon + gips + vinduer + doerer
    # med betydelig rabatt. Formaalet er aa utfordre den eksisterende
    # B2-bundlen og E_L2_C6-enkeltbudet.
    new_prices = {'C3': 355, 'C4': 232, 'C5': 5720, 'C6': 4580}
    totalkost = sum(p * vol[c] for c, p in new_prices.items())
    for c, p in new_prices.items():
        new_rows.append({
            'bud_id': 'B7',
            'type': 'bundle',
            'leverandoer': 'L2',
            'kategori': c,
            'pris_per_enhet': float(p),
            'volum': int(vol[c]),
            'linekost_NOK': float(p * vol[c]),
            'bundle_totalkost_NOK': float(totalkost),
            'bundle_kategorier': ','.join(sorted(new_prices.keys())),
        })
    return pd.concat([df_bundle, pd.DataFrame(new_rows)], ignore_index=True)


def plot_sensitivity(results: dict, output_path: Path) -> None:
    """Kombinert figur: (venstre) totalkostnad baseline / scenario A / B,
    (hoeyre) kategori-for-kategori leverandoerfarge for hvert scenario."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.3, 5.2),
                                    gridspec_kw={'width_ratios': [0.9, 1.6]})

    labels = ['Baseline', 'Scenario A:\nL3 trekker seg', 'Scenario B:\nL2 nytt bundle']
    totals = np.array([
        results['baseline']['total_NOK'],
        results['scen_A']['total_NOK'],
        results['scen_B']['total_NOK'],
    ]) / 1e6
    colors = [C_S1_FILL, C_S5_FILL, C_S2_FILL]
    edges = [C_S1_DARK, C_S5_DARK, C_S2_DARK]
    bars = ax1.bar(labels, totals, color=colors, edgecolor=edges, linewidth=1.4,
                   width=0.55)
    base = totals[0]
    for bar, v in zip(bars, totals):
        dif = v - base
        txt = f'{v:.2f} MNOK'
        if abs(dif) > 1e-6:
            txt += f'\n({dif:+.2f})'
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                 txt, ha='center', va='bottom', fontsize=10, color=C_TEXT)
    ax1.set_ylabel('Totalkostnad (MNOK)', fontsize=11)
    ax1.set_title('Totalkostnad over scenarier',
                  fontsize=11, fontweight='bold')
    ax1.set_ylim(0, totals.max() * 1.17)
    ax1.grid(True, alpha=0.3, axis='y')

    # Panel 2: kategori-vis leverandoer for hvert scenario
    scen_keys = ['baseline', 'scen_A', 'scen_B']
    scen_names = ['Baseline', 'Scenario A', 'Scenario B']
    cats = sorted(results['baseline']['cat_assign'].keys())
    sup_color = {'L1': C_S1_FILL, 'L2': C_S2_FILL,
                 'L3': C_S3_FILL, 'L4': C_S4_FILL}
    sup_edge = {'L1': C_S1_DARK, 'L2': C_S2_DARK,
                'L3': C_S3_DARK, 'L4': C_S4_DARK}

    y_pos = np.arange(len(scen_keys))
    cell_w = 1.0
    for j, c in enumerate(cats):
        for i, sk in enumerate(scen_keys):
            sup = results[sk]['cat_assign'].get(c, '-')
            col = sup_color.get(sup, '#FFFFFF')
            edg = sup_edge.get(sup, C_TEXT)
            rect = plt.Rectangle((j, i), 0.95, 0.9,
                                 facecolor=col, edgecolor=edg,
                                 linewidth=1.1)
            ax2.add_patch(rect)
            ax2.text(j + 0.475, i + 0.45, sup,
                     ha='center', va='center', fontsize=10, color=C_TEXT)
    ax2.set_xlim(-0.1, len(cats) + 0.1)
    ax2.set_ylim(-0.2, len(scen_keys))
    ax2.set_xticks(np.arange(len(cats)) + 0.475)
    ax2.set_xticklabels(cats, fontsize=10)
    ax2.set_yticks(np.arange(len(scen_keys)) + 0.45)
    ax2.set_yticklabels(scen_names, fontsize=10)
    ax2.invert_yaxis()
    ax2.set_title('Tildelt leverandoer per kategori',
                  fontsize=11, fontweight='bold')
    # Fjerne y-axis spine og ticks
    for spine in ['top', 'right', 'bottom', 'left']:
        ax2.spines[spine].set_visible(False)
    ax2.tick_params(left=False, bottom=False)

    # Legend for leverandoerer
    handles = []
    for s, col in sup_color.items():
        handles.append(plt.Rectangle((0, 0), 1, 1,
                                     facecolor=col, edgecolor=sup_edge[s],
                                     linewidth=1.1, label=s))
    ax2.legend(handles=handles, loc='upper right', ncol=4, fontsize=9,
               bbox_to_anchor=(1.0, -0.03))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 6: SENSITIVITET")
    print("=" * 60)

    df_cat = pd.read_csv(DATA_DIR / 'kategorier.csv')
    df_sup = pd.read_csv(DATA_DIR / 'leverandorer.csv')
    df_unit = pd.read_csv(DATA_DIR / 'enkeltbud.csv')
    df_bundle = pd.read_csv(DATA_DIR / 'bundlebud.csv')

    # Baseline
    df_bids = build_bids(df_unit, df_bundle)
    res_base = solve_bids(df_bids, df_cat, df_sup)

    # Scenario A: L3 trekker seg
    df_unit_A = df_unit[df_unit['leverandoer'] != 'L3'].copy()
    df_bundle_A = df_bundle[df_bundle['leverandoer'] != 'L3'].copy()
    df_bids_A = build_bids(df_unit_A, df_bundle_A)
    res_A = solve_bids(df_bids_A, df_cat, df_sup)

    # Scenario B: L2 legger til nytt aggressivt bundle-bud B7
    df_bundle_B = scenario_b_bids(df_unit, df_bundle, df_cat)
    df_bids_B = build_bids(df_unit, df_bundle_B)
    res_B = solve_bids(df_bids_B, df_cat, df_sup)

    print("\n-- Baseline --")
    print(f"  total = {res_base['total_NOK']/1e6:.3f} MNOK")
    print(f"  bud:   {res_base['valgte_bud']}")
    print("\n-- Scenario A: L3 trekker seg --")
    print(f"  total = {res_A['total_NOK']/1e6:.3f} MNOK")
    print(f"  bud:   {res_A['valgte_bud']}")
    print("\n-- Scenario B: L2 legger til nytt bundle B7 --")
    print(f"  total = {res_B['total_NOK']/1e6:.3f} MNOK")
    print(f"  bud:   {res_B['valgte_bud']}")

    summary = {
        'baseline_MNOK': round(res_base['total_NOK'] / 1e6, 3),
        'scen_A_MNOK': round(res_A['total_NOK'] / 1e6, 3),
        'scen_B_MNOK': round(res_B['total_NOK'] / 1e6, 3),
        'endring_A_MNOK': round((res_A['total_NOK'] - res_base['total_NOK'])
                                 / 1e6, 3),
        'endring_A_pct': round(100 * (res_A['total_NOK']
                                        - res_base['total_NOK'])
                                / res_base['total_NOK'], 2),
        'endring_B_MNOK': round((res_B['total_NOK'] - res_base['total_NOK'])
                                 / 1e6, 3),
        'endring_B_pct': round(100 * (res_B['total_NOK']
                                        - res_base['total_NOK'])
                                / res_base['total_NOK'], 2),
        'valgte_bud_baseline': res_base['valgte_bud'],
        'valgte_bud_A': res_A['valgte_bud'],
        'valgte_bud_B': res_B['valgte_bud'],
    }
    with open(OUTPUT_DIR / 'step06_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag lagret: {OUTPUT_DIR / 'step06_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    plot_sensitivity({'baseline': res_base, 'scen_A': res_A, 'scen_B': res_B},
                     OUTPUT_DIR / 'wdp_sensitivitet_scen.png')


if __name__ == '__main__':
    main()
