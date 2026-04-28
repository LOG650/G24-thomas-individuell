"""
Steg 3: Lot-for-lot (LFL) planlegging for alle komponenter
===========================================================
Kjor MRP med lot-for-lot-politikken: en ordre per periode med nettobehov.
Visualiser resultatet som en tidslinje for alle komponenter.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_bom, build_mps, S1, S2, S3, S4, S5, S1D, S2D, S3D, S4D, S5D, INK, INKMUTED
from step02_mrp_eksplosjon import run_mrp, lot_for_lot, total_cost

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def plot_mrp_timeline(results: Dict[str, pd.DataFrame], title: str, output_path: Path) -> None:
    """Plott planlagte ordrestart per komponent som stabler per uke."""
    components_order = ['Sykkel', 'Ramme', 'Hjul', 'Bremsesett', 'Stalrors', 'Eik']
    palette = {
        'Sykkel':      (S1, S1D),
        'Ramme':       (S2, S2D),
        'Hjul':        (S3, S3D),
        'Bremsesett':  (S4, S4D),
        'Stalrors':    (S5, S5D),
        'Eik':         ('#c0c0c0', '#606060'),
    }

    n_items = len(components_order)
    fig, axes = plt.subplots(n_items, 1, figsize=(11, 1.3 * n_items + 1.2), sharex=True)

    for ax, name in zip(axes, components_order):
        df = results[name]
        weeks = df['uke'].values
        rel = df['planlagt_ordrestart'].values
        fc, ec = palette[name]
        ax.bar(weeks, rel, color=fc, edgecolor=ec, lw=1.2, width=0.7)
        for x, y in zip(weeks, rel):
            if y > 0:
                ax.text(x, y + max(rel) * 0.04 + 0.1, str(int(y)),
                        ha='center', va='bottom', fontsize=8, color=INK)
        ax.set_ylabel(name, fontsize=10, rotation=0, ha='right', va='center', labelpad=25,
                      color=INK, fontweight='bold')
        ax.grid(True, axis='y', alpha=0.3)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.set_xticks(weeks)
        y_max = max(1, rel.max() * 1.25)
        ax.set_ylim(0, y_max)
    axes[-1].set_xlabel('Uke $t$', fontsize=12)
    fig.suptitle(title, fontsize=12, fontweight='bold', color=INK, y=0.995)
    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print('\n' + '=' * 60)
    print('STEG 3: LOT-FOR-LOT (LFL)')
    print('=' * 60)

    components = build_bom()
    mps = build_mps(12)

    def lfl(tentative_net: np.ndarray, name: str, comps: Dict) -> np.ndarray:
        return lot_for_lot(tentative_net)

    results = run_mrp(components, mps, lfl)
    cost = total_cost(results, components)

    print(f'\nLFL total kostnad: {cost["total_kr_totalt"]:.0f} kr '
          f'(oppstart {cost["oppstart_kr_totalt"]:.0f} + lager {cost["lager_kr_totalt"]:.0f})')
    for k, v in cost['per_komponent'].items():
        print(f"  {k:10s}: ordrer={v['antall_ordrer']}, total={v['total_kr']:.0f}")

    # Lagre
    serial = {name: df.to_dict(orient='list') for name, df in results.items()}
    with open(OUTPUT_DIR / 'mrp_lfl.json', 'w', encoding='utf-8') as f:
        json.dump({'mrp': serial, 'cost': cost}, f, indent=2, ensure_ascii=False)
    print(f'Lagret: {OUTPUT_DIR / "mrp_lfl.json"}')

    plot_mrp_timeline(results, 'Planlagte ordrestart per komponent - Lot-for-lot (LFL)',
                      OUTPUT_DIR / 'mrp_timeline_lfl.png')


if __name__ == '__main__':
    main()
