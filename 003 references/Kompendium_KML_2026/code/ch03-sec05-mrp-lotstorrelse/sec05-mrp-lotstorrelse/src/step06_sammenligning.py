"""
Steg 6: Sammenligning av lotstorrelsesmetoder (LFL vs EOQ vs Silver-Meal)
=========================================================================
Kjor MRP med alle tre lotstorrelsespolitikker og sammenlign totale
oppstarts- og lagerkostnader per komponent og totalt.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_bom, build_mps, S1, S2, S3, S1D, S2D, S3D, INK, INKMUTED
from step02_mrp_eksplosjon import run_mrp, total_cost, lot_for_lot
from step04_eoq_lotsizing import eoq_lot_sizing_factory
from step05_silver_meal import silver_meal_lot_sizing

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def plot_method_diagram(output_path: Path) -> None:
    """
    Plott en prosessfigur som viser MRP-stegene (Steg 1..6).
    """
    steps = [
        ('Steg 1', 'Datainnsamling\n(BOM, LT, OH, MPS)'),
        ('Steg 2', 'BOM-eksplosjon\n(topp -> bunn)'),
        ('Steg 3', 'Lot-for-lot\n(LFL)'),
        ('Steg 4', 'EOQ-lotstorrelse'),
        ('Steg 5', 'Silver-Meal\nheuristikk'),
        ('Steg 6', 'Sammenligning\n(kostnad + plan)'),
    ]
    fig, ax = plt.subplots(figsize=(12, 3.0))
    n = len(steps)
    x_pos = np.linspace(0, 11, n)
    palette = [S1, S2, S3, S1, S2, S3]
    darks = [S1D, S2D, S3D, S1D, S2D, S3D]
    for i, (code, text) in enumerate(steps):
        x = x_pos[i]
        rect = plt.Rectangle((x - 0.8, 0.3), 1.6, 1.3,
                             fc=palette[i], ec=darks[i], lw=1.5, zorder=2)
        ax.add_patch(rect)
        ax.text(x, 1.3, code, fontsize=11, fontweight='bold', color=INK,
                ha='center', va='center', zorder=3)
        ax.text(x, 0.75, text, fontsize=9, color=INK,
                ha='center', va='center', zorder=3)
        if i < n - 1:
            ax.annotate('', xy=(x_pos[i + 1] - 0.85, 0.95), xytext=(x + 0.85, 0.95),
                        arrowprops=dict(arrowstyle='->', color=INKMUTED, lw=1.5))
    ax.set_xlim(-1, 12)
    ax.set_ylim(0, 2)
    ax.axis('off')
    ax.set_title('MRP-prosess med lotstorrelsesvalg',
                 fontsize=12, fontweight='bold', color=INK, pad=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def plot_cost_comparison(costs: Dict[str, dict], output_path: Path) -> None:
    """Sojlediagram: total kostnad per metode, delt i oppstart og lagring."""
    methods = list(costs.keys())
    setup_costs = [costs[m]['oppstart_kr_totalt'] for m in methods]
    hold_costs = [costs[m]['lager_kr_totalt'] for m in methods]
    totals = [costs[m]['total_kr_totalt'] for m in methods]

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    x = np.arange(len(methods))
    width = 0.55
    bars1 = ax.bar(x, setup_costs, width, color=S1, edgecolor=S1D, lw=1.2,
                   label='Oppstartskostnad')
    bars2 = ax.bar(x, hold_costs, width, bottom=setup_costs, color=S2, edgecolor=S2D,
                   lw=1.2, label='Lagerkostnad')

    # Legg til totaltall over stablene
    for i, tot in enumerate(totals):
        ax.text(i, tot + max(totals) * 0.02, f'{tot:,.0f} kr'.replace(',', ' '),
                ha='center', va='bottom', fontsize=10, fontweight='bold', color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels(methods, fontsize=11)
    ax.set_ylabel('Total kostnad (kr) over 12 uker', fontsize=11)
    ax.set_title('Sammenligning av lotstorrelsesmetoder',
                 fontsize=12, fontweight='bold', color=INK)
    ax.legend(loc='upper right', frameon=False, fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_ylim(0, max(totals) * 1.18)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print('\n' + '=' * 60)
    print('STEG 6: SAMMENLIGNING AV METODER (LFL / EOQ / SILVER-MEAL)')
    print('=' * 60)

    components = build_bom()
    mps = build_mps(12)

    def lfl_fn(net_req: np.ndarray, name: str, comps: Dict) -> np.ndarray:
        return lot_for_lot(net_req)

    eoq_fn, eoq_values, _ = eoq_lot_sizing_factory(components, mps)
    sm_fn = silver_meal_lot_sizing(0, 0)

    all_results = {
        'LFL':         run_mrp(components, mps, lfl_fn),
        'EOQ':         run_mrp(components, mps, eoq_fn),
        'Silver-Meal': run_mrp(components, mps, sm_fn),
    }

    costs = {m: total_cost(r, components) for m, r in all_results.items()}

    print('\nSammendrag per metode:')
    print(f'{"Metode":<14}{"Oppstart":>12}{"Lager":>12}{"Total":>12}')
    print('-' * 50)
    for m in all_results:
        c = costs[m]
        print(f'{m:<14}{c["oppstart_kr_totalt"]:>12,.0f}'
              f'{c["lager_kr_totalt"]:>12,.0f}{c["total_kr_totalt"]:>12,.0f}')

    # Per-komponent-detaljer: antall ordrer per metode
    print('\nAntall ordrer per komponent:')
    print(f'{"Komponent":<12}', end='')
    for m in all_results:
        print(f'{m:>14}', end='')
    print()
    for name in ['Sykkel', 'Ramme', 'Hjul', 'Bremsesett', 'Stalrors', 'Eik']:
        print(f'{name:<12}', end='')
        for m in all_results:
            n_ord = int((all_results[m][name]['planlagt_mottak'] > 0).sum())
            print(f'{n_ord:>14}', end='')
        print()

    # Lagre sammendrag
    summary = {
        'costs': costs,
        'eoq_values': eoq_values,
        'methods': list(all_results.keys()),
    }
    with open(OUTPUT_DIR / 'mrp_sammenligning.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f'\nSammenligning lagret: {OUTPUT_DIR / "mrp_sammenligning.json"}')

    # Lagre konsoliderte MRP-resultater per metode (for tabell i tex)
    consolidated = {}
    for m, res in all_results.items():
        consolidated[m] = {name: df.to_dict(orient='list') for name, df in res.items()}
    with open(OUTPUT_DIR / 'mrp_alle_metoder.json', 'w', encoding='utf-8') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)

    # Figurer
    plot_cost_comparison(costs, OUTPUT_DIR / 'mrp_cost_compare.png')
    plot_method_diagram(OUTPUT_DIR / 'mrp_method.png')


if __name__ == '__main__':
    main()
