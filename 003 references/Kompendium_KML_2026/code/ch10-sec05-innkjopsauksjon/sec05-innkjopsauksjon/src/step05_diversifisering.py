"""
Steg 5: Diversifiseringsskranke
===============================
Ledelsen onsker ikke at en enkelt leverandor vinner en dominerende andel
av kontrakten (risikoreduksjon). Vi innforer en 'maks-andel'-skranke per
leverandoer, og varierer grensen alpha_max for aa se hvordan totalkostnad
og antall leverandoerer endrer seg.

Diversifiseringsskranken:
   sum_{b : s(b)=s}  p_b * x_b  <=  alpha_max * C_total    for alle s

der C_total er summen av laveste tilgjengelige enkeltbud per kategori
(en oevre grense paa faktisk kontraktverdi).

Vi kjorer alpha_max i {uten, 0.50, 0.45, 0.40, 0.35, 0.30} og rapporterer
totalkostnad og fordeling per leverandoer for hver.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

from step03_mip_formulering import build_bids

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
C_TEXT = '#1F2933'

SUP_COLOR = {
    'L1': C_S1_FILL,
    'L2': C_S2_FILL,
    'L3': C_S3_FILL,
    'L4': C_S4_FILL,
}
SUP_EDGE = {
    'L1': C_S1_DARK,
    'L2': C_S2_DARK,
    'L3': C_S3_DARK,
    'L4': C_S4_DARK,
}


def solve_with_alpha(df_bids: pd.DataFrame, df_cat: pd.DataFrame,
                     df_sup: pd.DataFrame,
                     alpha_max: float | None,
                     C_upper: float) -> dict:
    model = pulp.LpProblem('WDP_div', pulp.LpMinimize)
    x = {row['bud_id']: pulp.LpVariable(f"x_{row['bud_id']}", cat=pulp.LpBinary)
         for _, row in df_bids.iterrows()}

    bid_map = {row['bud_id']: row for _, row in df_bids.iterrows()}

    obj = pulp.lpSum(x[bid_id] * bid_map[bid_id]['totalkost_NOK']
                     for bid_id in df_bids['bud_id'])
    model += obj, 'TotalCost'

    for _, c in df_cat.iterrows():
        cov = [bid_id for bid_id in df_bids['bud_id']
               if c['kategori'] in bid_map[bid_id]['kategorier']]
        model += (pulp.lpSum(x[b] for b in cov) == 1), f"Cover_{c['kategori']}"

    if alpha_max is not None:
        for _, s in df_sup.iterrows():
            budset = [bid_id for bid_id in df_bids['bud_id']
                      if bid_map[bid_id]['leverandoer'] == s['leverandoer']]
            model += (pulp.lpSum(x[b] * float(bid_map[b]['totalkost_NOK'])
                                 for b in budset)
                      - alpha_max * C_upper <= 0), f"Div_{s['leverandoer']}"

    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    if pulp.LpStatus[status] != 'Optimal':
        return {'status': pulp.LpStatus[status], 'alpha_max': alpha_max}

    selected = [bid_id for bid_id in df_bids['bud_id']
                if pulp.value(x[bid_id]) is not None
                and pulp.value(x[bid_id]) > 0.5]

    total = 0.0
    per_sup = {}
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
        'alpha_max': alpha_max,
        'obj': float(pulp.value(model.objective)),
        'total_NOK': total,
        'per_sup_NOK': per_sup,
        'per_sup_andel': {s: round(v / total, 4) for s, v in per_sup.items()},
        'antall_leverandorer': int(len(per_sup)),
        'valgte_bud': selected,
        'cat_assign': cat_assign,
    }


def plot_diversification(results: list[dict], output_path: Path) -> None:
    """Stablede stolper: andel per leverandoer for hver alpha."""
    labels = []
    stacks = {s: [] for s in ['L1', 'L2', 'L3', 'L4']}
    totals = []
    for r in results:
        a = r['alpha_max']
        labels.append('Uten' if a is None else f'{a:.2f}'.replace('.', ','))
        total = r['total_NOK'] / 1e6
        totals.append(total)
        for s in ['L1', 'L2', 'L3', 'L4']:
            frac = r['per_sup_NOK'].get(s, 0.0) / r['total_NOK']
            stacks[s].append(frac * 100)   # prosent

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.8, 4.8),
                                    gridspec_kw={'width_ratios': [1.3, 1.0]})

    # Panel 1: stablede andeler
    x = np.arange(len(labels))
    bottom = np.zeros(len(labels))
    for s in ['L1', 'L2', 'L3', 'L4']:
        h = np.array(stacks[s])
        ax1.bar(x, h, bottom=bottom, color=SUP_COLOR[s], edgecolor=SUP_EDGE[s],
                linewidth=1.2, width=0.63, label=s)
        for xi, (hi, bi) in enumerate(zip(h, bottom)):
            if hi > 6:
                ax1.text(xi, bi + hi / 2, f'{hi:.0f} %',
                         ha='center', va='center', fontsize=9, color=C_TEXT)
        bottom += h
    ax1.axhline(y=40, color='#961D1C', linestyle=':', linewidth=1.4,
                label=r'40 %-grense')
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, fontsize=10)
    ax1.set_xlabel(r'$\alpha_{\mathrm{maks}}$', fontsize=11)
    ax1.set_ylabel('Andel av kontraktverdi (%)', fontsize=11)
    ax1.set_title('Fordeling per leverandoer', fontsize=11, fontweight='bold')
    ax1.legend(loc='upper right', fontsize=9, ncol=3)
    ax1.set_ylim(0, 118)
    ax1.grid(True, alpha=0.3, axis='y')

    # Panel 2: totalkostnad
    ax2.plot(x, totals, 'o-', color=C_S4_DARK, linewidth=2.0, markersize=8)
    for xi, ti in zip(x, totals):
        ax2.text(xi, ti + max(totals) * 0.008, f'{ti:.2f}',
                 ha='center', va='bottom', fontsize=10, color=C_TEXT)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, fontsize=10)
    ax2.set_xlabel(r'$\alpha_{\mathrm{maks}}$', fontsize=11)
    ax2.set_ylabel('Totalkostnad (MNOK)', fontsize=11)
    ax2.set_title('Prisen for diversifisering', fontsize=11, fontweight='bold')
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: DIVERSIFISERING")
    print("=" * 60)

    df_cat = pd.read_csv(DATA_DIR / 'kategorier.csv')
    df_sup = pd.read_csv(DATA_DIR / 'leverandorer.csv')
    df_unit = pd.read_csv(DATA_DIR / 'enkeltbud.csv')
    df_bundle = pd.read_csv(DATA_DIR / 'bundlebud.csv')

    df_bids = build_bids(df_unit, df_bundle)

    # Beregn C_upper: sum av billigste enkeltbud per kategori
    C_upper = 0.0
    for _, c in df_cat.iterrows():
        cand = df_unit[df_unit['kategori'] == c['kategori']]['linekost_NOK']
        C_upper += float(cand.min())

    alphas = [None, 0.50, 0.45, 0.40, 0.35]
    results = []
    for a in alphas:
        r = solve_with_alpha(df_bids, df_cat, df_sup, a, C_upper)
        if r.get('status') != 'Optimal':
            print(f"\n  alpha_max = {a}  -> IKKE LOESBAR ({r.get('status')})")
            continue
        print(f"\n  alpha_max = {a}  -> total = "
              f"{r['total_NOK']/1e6:.3f} MNOK, "
              f"{r['antall_leverandorer']} leverandoerer, "
              f"valgt: {r['valgte_bud']}")
        results.append(r)

    # Test alpha = 0.30 separat for aa bekrefte infeasibility
    r_inf = solve_with_alpha(df_bids, df_cat, df_sup, 0.30, C_upper)
    infeas_alpha = 0.30 if r_inf.get('status') != 'Optimal' else None

    # Lagrer som tabell
    table = []
    baseline_total = results[0]['total_NOK']
    for r in results:
        a = r['alpha_max']
        row = {
            'alpha_maks': 'Uten' if a is None else round(a, 2),
            'total_NOK': round(r['total_NOK'], 2),
            'total_MNOK': round(r['total_NOK'] / 1e6, 3),
            'diff_vs_uten_MNOK': round((r['total_NOK'] - baseline_total) / 1e6,
                                        3),
            'diff_vs_uten_pct': round(100 * (r['total_NOK'] - baseline_total)
                                        / baseline_total, 3),
            'antall_leverandoerer': r['antall_leverandorer'],
            'valgte_bud': ','.join(r['valgte_bud']),
        }
        for s in ['L1', 'L2', 'L3', 'L4']:
            row[f'andel_{s}'] = r['per_sup_andel'].get(s, 0.0)
        table.append(row)
    df_res = pd.DataFrame(table)
    df_res.to_csv(OUTPUT_DIR / 'step05_diversifisering.csv', index=False)
    print(f"\nTabell lagret: {OUTPUT_DIR / 'step05_diversifisering.csv'}")

    def _find(a):
        return [r['total_NOK'] for r in results if r['alpha_max'] == a]

    summary = {
        'C_upper_NOK': round(C_upper, 2),
        'baseline_MNOK': round(baseline_total / 1e6, 3),
        'alpha_0p50_MNOK': round(_find(0.50)[0] / 1e6, 3) if _find(0.50) else None,
        'alpha_0p45_MNOK': round(_find(0.45)[0] / 1e6, 3) if _find(0.45) else None,
        'alpha_0p40_MNOK': round(_find(0.40)[0] / 1e6, 3) if _find(0.40) else None,
        'alpha_0p35_MNOK': round(_find(0.35)[0] / 1e6, 3) if _find(0.35) else None,
        'alpha_0p30_status': 'Infeasible' if infeas_alpha is not None else 'Optimal',
        'kostnad_div_0p40_MNOK': (round(
            (_find(0.40)[0] - baseline_total) / 1e6, 3)
            if _find(0.40) else None),
        'kostnad_div_0p35_MNOK': (round(
            (_find(0.35)[0] - baseline_total) / 1e6, 3)
            if _find(0.35) else None),
    }
    with open(OUTPUT_DIR / 'step05_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag lagret: {OUTPUT_DIR / 'step05_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    plot_diversification(results, OUTPUT_DIR / 'wdp_sensitivitet.png')


if __name__ == '__main__':
    main()
