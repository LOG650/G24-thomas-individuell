"""
Steg 6: Anbefaling og handlingsplan
===================================
Bygger den endelige manedlige anbefalingen som en tabell + oppsummerer
totalkostnader og krever produksjonsvolum.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step01_datainnsamling import parameters, MONTHS_NO
from step03_lp_losning import build_and_solve

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def main() -> None:
    print("\n" + "=" * 60)
    print("STEG 6: ANBEFALING")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / 'boat_demand.csv')
    demand = df['etterspoersel'].values.astype(int)
    params = parameters()
    res = build_and_solve(demand, params)

    plan = pd.DataFrame({
        'Maaned': MONTHS_NO,
        'D_t': demand,
        'P_t': np.round(res['P']).astype(int),
        'O_t': np.round(res['O']).astype(int),
        'I_t': np.round(res['I']).astype(int),
        'H_t': np.round(res['H']).astype(int),
        'F_t': np.round(res['F']).astype(int),
        'W_t': np.round(res['W']).astype(int),
    })
    plan.loc['Sum'] = [
        '-', int(demand.sum()), int(plan['P_t'].sum()), int(plan['O_t'].sum()),
        int(plan['I_t'].sum()), int(plan['H_t'].sum()), int(plan['F_t'].sum()),
        '-',
    ]
    plan.to_csv(OUTPUT_DIR / 'step06_anbefaling.csv', index=False)
    print("\n" + plan.to_string())

    summary = {
        'total_kostnad': round(res['obj'], 2),
        'total_ordinaer_produksjon': int(sum(res['P'])),
        'total_overtidsproduksjon': int(sum(res['O'])),
        'total_lager_i_mnd_enheter': int(sum(res['I'])),
        'total_nyansatte': int(sum(res['H'])),
        'total_oppsagt': int(sum(res['F'])),
        'arbeidsstyrke_slutt': int(res['W'][-1]),
        'arbeidsstyrke_start': int(params['W_0']),
        'sesongtoppmaaned': MONTHS_NO[int(np.argmax(demand))],
    }
    with open(OUTPUT_DIR / 'step06_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print("\nOppsummering:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
