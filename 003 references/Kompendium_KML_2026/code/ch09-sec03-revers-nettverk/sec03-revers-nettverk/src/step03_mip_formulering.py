"""
Steg 3: MIP-formulering
=======================
Flertrinn (multi-echelon) reverst fasilitetslokaliseringsproblem med
kapasitetsbegrensninger paa begge nivaaer.

Mengder
-------
  J   = mengden av kunder (40)
  I   = mengden av kandidat-innsamlingssentre (8)
  K   = mengden av kandidat-gjenvinningsanlegg (3)

Parametre
---------
  r_j      = returvolum fra kunde j (tonn/aar)
  f_i      = fast aapningskostnad for innsamlingssenter i (NOK/aar)
  g_k      = fast aapningskostnad for gjenvinningsanlegg k (NOK/aar)
  u_i      = kapasitet paa innsamlingssenter i (tonn/aar)
  v_k      = kapasitet paa gjenvinningsanlegg k (tonn/aar)
  p_k      = prosesseringskostnad per tonn ved gjenvinning k (NOK/tonn)
  c^1_{ij} = transportkostnad per tonn: kunde j -> innsamling i (NOK/tonn)
  c^2_{ik} = transportkostnad per tonn: innsamling i -> gjenvinning k (NOK/tonn)

Beslutningsvariabler
--------------------
  y_i      in {0,1}      : 1 hvis innsamlingssenter i aapnes
  z_k      in {0,1}      : 1 hvis gjenvinningsanlegg k aapnes
  x_{ij}   in [0, r_j]   : tonn returvolum fra kunde j sendt til innsamling i
  w_{ik}   in [0, oo)    : tonn returvolum fra innsamling i sendt til gjenvinning k

Modell
------
  min  sum_i f_i y_i + sum_k g_k z_k
       + sum_i sum_j c^1_{ij} x_{ij}
       + sum_i sum_k c^2_{ik} w_{ik}
       + sum_i sum_k p_k w_{ik}

  s.t. sum_i x_{ij} = r_j           for alle j    (all retur dekkes)
       sum_j x_{ij} <= u_i y_i      for alle i    (kapasitet innsamling)
       sum_k w_{ik} = sum_j x_{ij}  for alle i    (flyt-balanse ved innsamling)
       sum_i w_{ik} <= v_k z_k      for alle k    (kapasitet gjenvinning)
       x_{ij} >= 0, w_{ik} >= 0, y_i, z_k in {0,1}
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

from step02_avstandsmatrise import (TRANSPORT_COST_L1_PER_TKM,
                                    TRANSPORT_COST_L2_PER_TKM)

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def build_revnet(df_cust: pd.DataFrame, df_is: pd.DataFrame, df_gv: pd.DataFrame,
                 D1: np.ndarray, D2: np.ndarray,
                 r_scale: float = 1.0) -> pulp.LpProblem:
    """Bygger flertrinn reverst MIP. r_scale skalerer alle returvolum."""
    n_is = len(df_is)
    n_gv = len(df_gv)
    n_k = len(df_cust)

    r = df_cust['returvolum_tonn'].to_numpy(dtype=float) * r_scale
    f = df_is['fast_kostnad'].to_numpy(dtype=float)
    g = df_gv['fast_kostnad'].to_numpy(dtype=float)
    u = df_is['kapasitet_tonn'].to_numpy(dtype=float)
    v = df_gv['kapasitet_tonn'].to_numpy(dtype=float)
    p = df_gv['prosess_kost_per_tonn'].to_numpy(dtype=float)

    C1 = D1 * TRANSPORT_COST_L1_PER_TKM   # [n_is x n_k]
    C2 = D2 * TRANSPORT_COST_L2_PER_TKM   # [n_is x n_gv]

    model = pulp.LpProblem('ReverseNetwork', pulp.LpMinimize)

    # Binaere aapningsvariabler
    y = [pulp.LpVariable(f'y_{i}', cat=pulp.LpBinary) for i in range(n_is)]
    z = [pulp.LpVariable(f'z_{k}', cat=pulp.LpBinary) for k in range(n_gv)]

    # Flytvariabler (tonn)
    # x[i][j]: fra kunde j til innsamling i
    x = [[pulp.LpVariable(f'x_{i}_{j}', lowBound=0, upBound=float(r[j]))
          for j in range(n_k)] for i in range(n_is)]
    # w[i][k]: fra innsamling i til gjenvinning k
    w = [[pulp.LpVariable(f'w_{i}_{k}', lowBound=0)
          for k in range(n_gv)] for i in range(n_is)]

    # Objektfunksjon
    obj_terms = []
    obj_terms += [f[i] * y[i] for i in range(n_is)]
    obj_terms += [g[k] * z[k] for k in range(n_gv)]
    obj_terms += [C1[i, j] * x[i][j] for i in range(n_is) for j in range(n_k)]
    obj_terms += [C2[i, k] * w[i][k] for i in range(n_is) for k in range(n_gv)]
    obj_terms += [p[k] * w[i][k] for i in range(n_is) for k in range(n_gv)]
    model += pulp.lpSum(obj_terms), 'TotalCost'

    # Dekning: all retur fra kunde j skal samles
    for j in range(n_k):
        model += (pulp.lpSum(x[i][j] for i in range(n_is)) == r[j]), f'Cover_{j}'

    # Kapasitet + kobling innsamlingssenter
    for i in range(n_is):
        model += (pulp.lpSum(x[i][j] for j in range(n_k))
                  - u[i] * y[i] <= 0), f'CapIS_{i}'

    # Flyt-balanse: det som kommer inn til i, sendes videre
    for i in range(n_is):
        inflow = pulp.lpSum(x[i][j] for j in range(n_k))
        outflow = pulp.lpSum(w[i][k] for k in range(n_gv))
        model += (inflow - outflow == 0), f'Flow_{i}'

    # Kapasitet + kobling gjenvinningsanlegg
    for k in range(n_gv):
        model += (pulp.lpSum(w[i][k] for i in range(n_is))
                  - v[k] * z[k] <= 0), f'CapGV_{k}'

    return model


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: MIP-FORMULERING")
    print("=" * 60)

    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    df_is = pd.read_csv(DATA_DIR / 'innsamling.csv')
    df_gv = pd.read_csv(DATA_DIR / 'gjenvinning.csv')
    D1 = pd.read_csv(OUTPUT_DIR / 'step02_dist_l1_km.csv', index_col=0).to_numpy()
    D2 = pd.read_csv(OUTPUT_DIR / 'step02_dist_l2_km.csv', index_col=0).to_numpy()

    model = build_revnet(df_cust, df_is, df_gv, D1, D2)

    lp_path = OUTPUT_DIR / 'revnet_model.lp'
    model.writeLP(str(lp_path))
    print(f"LP-fil lagret: {lp_path}")

    n_vars = len(model.variables())
    n_cons = len(model.constraints)
    n_bin = sum(1 for v in model.variables()
                if v.cat in (pulp.LpBinary, 'Integer'))

    n_is = len(df_is)
    n_gv = len(df_gv)
    n_k = len(df_cust)

    summary = {
        'antall_kunder': int(n_k),
        'antall_innsamlingskandidater': int(n_is),
        'antall_gjenvinningskandidater': int(n_gv),
        'antall_variabler_total': int(n_vars),
        'antall_binaere_variabler': int(n_bin),
        'antall_kontinuerlige_variabler': int(n_vars - n_bin),
        'antall_skranker': int(n_cons),
        'antall_dekningsskranker': int(n_k),
        'antall_kapasitet_IS': int(n_is),
        'antall_flytbalanse': int(n_is),
        'antall_kapasitet_GV': int(n_gv),
        'antall_flytvariabler_l1': int(n_is * n_k),
        'antall_flytvariabler_l2': int(n_is * n_gv),
    }
    with open(OUTPUT_DIR / 'step03_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag lagret: {OUTPUT_DIR / 'step03_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Utdrag av LP-formulering
    with open(lp_path, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    print("\n--- Utdrag av LP-formulering ---")
    for line in lines[:24]:
        print(line.rstrip())
    print("  ...")


if __name__ == '__main__':
    main()
