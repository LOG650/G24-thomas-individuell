"""
Steg 2: Deterministisk baseline
================================
Loeser deterministisk LP ved bruk av nominell etterspoersel d_bar.

Dette er "optimer for forventet scenario"-baseline-en som vi senere
sammenligner robust og stokastisk loesning mot.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from model_utils import OUTPUT_DIR, load_instance, solve_deterministic


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: DETERMINISTISK LP (nominell etterspoersel)")
    print("=" * 60)

    inst = load_instance()
    res = solve_deterministic(inst, inst.d_bar)

    z = res['z']
    fixed_cost = float((inst.k * z).sum())
    trans_cost = float((inst.c * res['x']).sum())
    penalty_cost = float((inst.p * res['u']).sum())
    total = res['obj']

    df_z = pd.DataFrame({
        'lager': inst.df_w['navn'],
        'kapasitet': np.round(z, 2),
        'maks_kap': inst.z_max,
        'utnytting_pct': np.round(100 * z / inst.z_max, 1),
    })
    df_z.to_csv(OUTPUT_DIR / 'step02_kapasitet.csv', index=False)
    np.savez(OUTPUT_DIR / 'step02_z_det.npz', z=z)

    summary = {
        'obj_NOK': round(total, 2),
        'obj_MNOK': round(total / 1e6, 3),
        'fixed_cost_MNOK': round(fixed_cost / 1e6, 3),
        'transport_cost_MNOK': round(trans_cost / 1e6, 3),
        'penalty_cost_MNOK': round(penalty_cost / 1e6, 3),
        'sum_z': round(float(z.sum()), 1),
        'sum_d_bar': float(inst.d_bar.sum()),
        'antall_apne': int(np.sum(z > 1e-6)),
        'z_per_lager': {inst.df_w['navn'].iloc[i]: round(float(z[i]), 1)
                        for i in range(inst.n)},
    }
    with open(OUTPUT_DIR / 'step02_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step02_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
