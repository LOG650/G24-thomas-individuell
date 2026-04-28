"""
Steg 3: MIP-formulering
=======================
Skriver ut en menneskelig lesbar LP-fil (UFLP) og en snutt av modellen til
konsollen saa leseren faar se det formelle oppsettet.

Modellen
--------
Beslutningsvariabler:
    y_i  = 1 hvis DC-kandidat i aapnes, ellers 0
    x_ij in [0, 1] = andelen av kunde j sin etterspoersel som dekkes fra DC i

Formulering:
    min  sum_i f_i y_i + sum_i sum_j c_ij d_j x_ij
    s.t. sum_i x_ij = 1         for alle j     (all etterspoersel dekkes)
         x_ij <= y_i            for alle i, j  (koblingsskranke)
         y_i in {0, 1}, x_ij >= 0
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

from step02_avstandsmatrise import TRANSPORT_COST_PER_KM

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def build_uflp(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
               dist_km: np.ndarray) -> pulp.LpProblem:
    n = len(df_dc)
    m = len(df_cust)
    f = df_dc['fast_kostnad'].to_numpy(dtype=float)
    d = df_cust['etterspoersel'].to_numpy(dtype=float)
    c = dist_km * TRANSPORT_COST_PER_KM  # NOK per enhet

    model = pulp.LpProblem('UFLP', pulp.LpMinimize)

    # Variabler
    y = [pulp.LpVariable(f'y_{i}', lowBound=0, upBound=1, cat=pulp.LpBinary)
         for i in range(n)]
    x = [[pulp.LpVariable(f'x_{i}_{j}', lowBound=0, upBound=1)
          for j in range(m)] for i in range(n)]

    # Objektfunksjon: faste kostnader + transport
    model += (
        pulp.lpSum(f[i] * y[i] for i in range(n))
        + pulp.lpSum(c[i, j] * d[j] * x[i][j] for i in range(n) for j in range(m))
    ), 'TotalCost'

    # Dekningsskranke: all etterspoersel skal dekkes
    for j in range(m):
        model += (pulp.lpSum(x[i][j] for i in range(n)) == 1), f'Cover_{j}'

    # Koblingsskranke: en kunde kan kun betjenes fra en aapen DC
    for i in range(n):
        for j in range(m):
            model += (x[i][j] - y[i] <= 0), f'Link_{i}_{j}'

    return model


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: MIP-FORMULERING")
    print("=" * 60)

    df_dc = pd.read_csv(DATA_DIR / 'kandidater.csv')
    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    dist_km = pd.read_csv(OUTPUT_DIR / 'step02_dist_km.csv', index_col=0).to_numpy()

    model = build_uflp(df_dc, df_cust, dist_km)

    # Skriv LP-fil for leseren
    lp_path = OUTPUT_DIR / 'uflp_model.lp'
    model.writeLP(str(lp_path))
    print(f"LP-fil lagret: {lp_path}")

    n_vars = len(model.variables())
    n_cons = len(model.constraints)
    # PuLP setter cat='Integer' naar bounds er [0,1] selv om opprettet som Binary
    n_bin = sum(1 for v in model.variables()
                if v.cat in (pulp.LpBinary, 'Integer') and v.name.startswith('y_'))
    n = len(df_dc)
    m = len(df_cust)

    summary = {
        'antall_kandidater_n': int(n),
        'antall_kunder_m': int(m),
        'antall_variabler_total': int(n_vars),
        'antall_binaere_variabler': int(n_bin),
        'antall_kontinuerlige_variabler': int(n_vars - n_bin),
        'antall_skranker': int(n_cons),
        'antall_dekningsskranker': int(m),
        'antall_koblingsskranker': int(n * m),
    }
    with open(OUTPUT_DIR / 'step03_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag lagret: {OUTPUT_DIR / 'step03_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Vis et utdrag av LP-formuleringen
    with open(lp_path, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    print("\n--- Utdrag av LP-formulering ---")
    for line in lines[:20]:
        print(line.rstrip())
    print("  ...")


if __name__ == '__main__':
    main()
