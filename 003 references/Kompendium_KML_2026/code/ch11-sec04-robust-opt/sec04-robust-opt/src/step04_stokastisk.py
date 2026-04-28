"""
Steg 4: Scenariobasert stokastisk LP
=====================================
Loeser det to-trinns stokastiske programmet

    min_z  k'z + (1/S) sum_s f(z, d^s)

der d^s er trukket fra et referansefordeling over U. Dette er den
risikonoytrale baseline: den optimerer forventet kostnad, ikke verste
tilfelle.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_utils import (OUTPUT_DIR, cost_at, load_instance,
                          sample_interior_scenarios, solve_stochastic)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 4: STOKASTISK LP (50 scenarioer)")
    print("=" * 60)

    inst = load_instance()
    S = 50
    scenarios = sample_interior_scenarios(inst, S, seed=33333)
    print(f"Antall scenarioer: {S} (uniform trekk fra U)")

    res = solve_stochastic(inst, scenarios)
    z_stoch = res['z']

    # Evaluer z_stoch paa de samme 50 scenarioene
    cost_stoch = np.array([cost_at(inst, z_stoch, scenarios[s])['total']
                           for s in range(S)])

    np.savez(OUTPUT_DIR / 'step04_stochastic.npz',
             z=z_stoch, scenarios=scenarios, cost_stoch=cost_stoch)

    summary = {
        'antall_scenarioer': int(S),
        'E_obj_MNOK': round(float(res['obj']) / 1e6, 3),
        'snitt_kostnad_MNOK': round(float(cost_stoch.mean()) / 1e6, 3),
        'verste_kostnad_MNOK': round(float(cost_stoch.max()) / 1e6, 3),
        'sum_z_stoch': round(float(z_stoch.sum()), 1),
        'z_per_lager': {inst.df_w['navn'].iloc[i]: round(float(z_stoch[i]), 1)
                        for i in range(inst.n)},
    }
    with open(OUTPUT_DIR / 'step04_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step04_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
