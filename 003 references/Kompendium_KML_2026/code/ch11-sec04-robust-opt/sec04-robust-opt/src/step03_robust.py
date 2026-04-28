"""
Steg 3: Robust formulering -- minimax regret
============================================

Gitt usikkerhetsomraadet U = { d :  d_bar_j - delta_j <= d_j <= d_bar_j + delta_j }
finner vi en kapasitet z som minimerer det stoerste tapet sammenlignet med
perfekt-info-loesningen over scenarier trukket fra U:

    min_z  max_{d in S}  [C(z, d) - C*(d)]

der S er et endelig utvalg av scenarioer -- typisk hjoerner av boksen. For LP
med box-usikkerhet naas de verste tilfellene i hjoernene, saa vi trekker en
blanding av hjoerne- og interioere scenarioer for aa faa en representativ
diskretisering.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_utils import (OUTPUT_DIR, cost_at, load_instance,
                          sample_interior_scenarios, sample_vertex_scenarios,
                          solve_deterministic, solve_minimax_regret)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: ROBUST OPTIMERING (minimax regret)")
    print("=" * 60)

    inst = load_instance()

    # Trekk scenarioer: 40 hjoerner + 10 interioere (totalt 50)
    n_vertex = 40
    n_interior = 10
    scen_vert = sample_vertex_scenarios(inst, n_vertex, seed=11111)
    scen_int = sample_interior_scenarios(inst, n_interior, seed=22222)
    scenarios = np.vstack([scen_vert, scen_int])
    S = len(scenarios)
    print(f"Antall scenarioer: {S} ({n_vertex} hjoerner + {n_interior} interioere)")

    # Beregn perfekt-info-kostnad C*(d^s) for hver realisering
    print("\nBeregner perfekt-info optimum C*(d) per scenario ...")
    cstar = np.zeros(S)
    for s in range(S):
        r = solve_deterministic(inst, scenarios[s])
        cstar[s] = r['obj']
    print(f"  snitt C*(d): {cstar.mean():.0f} NOK")
    print(f"  min  C*(d): {cstar.min():.0f} NOK")
    print(f"  maks C*(d): {cstar.max():.0f} NOK")

    # Loes minimax-regret-LPen
    print("\nLoeser minimax-regret-LP ...")
    res = solve_minimax_regret(inst, scenarios, cstar)
    z_rob = res['z']
    max_regret = res['max_regret']

    # Beregn total kostnad per scenario for robust z
    cost_rob = np.array([cost_at(inst, z_rob, scenarios[s])['total']
                         for s in range(S)])
    regret_rob = cost_rob - cstar

    np.savez(OUTPUT_DIR / 'step03_robust.npz',
             z=z_rob, scenarios=scenarios, cstar=cstar,
             cost_rob=cost_rob, regret_rob=regret_rob)

    summary = {
        'antall_scenarioer': int(S),
        'n_vertex': int(n_vertex),
        'n_interior': int(n_interior),
        'maks_regret_MNOK': round(max_regret / 1e6, 3),
        'snitt_regret_MNOK': round(float(regret_rob.mean()) / 1e6, 3),
        'snitt_kostnad_robust_MNOK': round(float(cost_rob.mean()) / 1e6, 3),
        'verste_kostnad_robust_MNOK': round(float(cost_rob.max()) / 1e6, 3),
        'sum_z_robust': round(float(z_rob.sum()), 1),
        'z_per_lager': {inst.df_w['navn'].iloc[i]: round(float(z_rob[i]), 1)
                        for i in range(inst.n)},
    }
    with open(OUTPUT_DIR / 'step03_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step03_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
