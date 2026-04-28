"""
Steg 6: Trade-off-kurve (forsikringspremie)
============================================
Skalerer usikkerhetsomraadet med en faktor alpha i [0, 1] og gjenberegner
robust minimax-regret-loesning for hver alpha. Plotter E-kostnad og
worst-case kostnad som funksjon av alpha, saa man ser "forsikringspremien"
i robust-politikken.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import (OUTPUT_DIR, cost_at, load_instance,
                          sample_interior_scenarios,
                          sample_vertex_scenarios,
                          solve_deterministic, solve_minimax_regret)

C_EXP = '#1F6587'       # s1dark -- E-kostnad
C_EXP_FILL = '#8CC8E5'
C_WORST = '#961D1C'     # s5dark -- worst-case
C_WORST_FILL = '#ED9F9E'
C_INK = '#1F2933'


def plot_premium_curve(df: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.0))

    ax.plot(df['alpha'], df['worst_MNOK'], marker='o',
            color=C_WORST, markerfacecolor=C_WORST_FILL, markersize=8,
            linewidth=2.0, label='Worst-case kostnad (robust $z^{rob}(\\alpha)$)')
    ax.plot(df['alpha'], df['E_MNOK'], marker='s',
            color=C_EXP, markerfacecolor=C_EXP_FILL, markersize=8,
            linewidth=2.0, label='Forventet kostnad (robust $z^{rob}(\\alpha)$)')

    ax.set_xlabel('Skaleringsfaktor $\\alpha$ (bredde paa usikkerhetsomraadet)',
                   fontsize=11)
    ax.set_ylabel('Kostnad (MNOK)', fontsize=11)
    ax.set_title('Forsikringspremie: forventet vs. verste kostnad som funksjon av $\\alpha$',
                 fontsize=12, fontweight='bold', color=C_INK)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)

    # Annoter skille mellom E og worst (premien) ved alpha=1
    r1 = df.iloc[-1]
    mid = 0.5 * (r1['E_MNOK'] + r1['worst_MNOK'])
    ax.annotate('Premie', xy=(r1['alpha'], mid),
                xytext=(r1['alpha'] - 0.18, mid),
                fontsize=10, color=C_INK, ha='right',
                arrowprops=dict(arrowstyle='->', color=C_INK))

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 6: TRADE-OFF-KURVE")
    print("=" * 60)

    inst = load_instance()
    alphas = np.array([0.0, 0.25, 0.5, 0.75, 1.0, 1.25, 1.5])

    # Evalueringssett (fast alpha = 1)
    eval_S = 300
    eval_scen_base = sample_interior_scenarios(inst, eval_S, seed=77777)
    # Baseline scenarier for robust-LP (hjoerner)
    base_vertex = sample_vertex_scenarios(inst, 32, seed=55555)

    rows = []
    for a in alphas:
        # Skaler bredden: delta -> a * delta
        inst_a = inst
        scaled_scen = inst.d_bar + (base_vertex - inst.d_bar) * a

        print(f"\nalpha = {a}")
        cstar = np.array([solve_deterministic(inst_a, scaled_scen[s])['obj']
                          for s in range(len(scaled_scen))])
        res = solve_minimax_regret(inst_a, scaled_scen, cstar)
        z_rob = res['z']

        # Evaluer paa samme 300 scenarioer (trukket fra U_full) men skalert
        eval_sc = inst.d_bar + (eval_scen_base - inst.d_bar) * a
        costs = np.array([cost_at(inst_a, z_rob, eval_sc[s])['total']
                          for s in range(eval_S)])

        rows.append({
            'alpha': round(float(a), 2),
            'E_NOK': round(float(costs.mean()), 2),
            'worst_NOK': round(float(costs.max()), 2),
            'E_MNOK': round(float(costs.mean()) / 1e6, 3),
            'worst_MNOK': round(float(costs.max()) / 1e6, 3),
            'std_MNOK': round(float(costs.std()) / 1e6, 3),
            'sum_z': round(float(z_rob.sum()), 1),
        })
        print(f"  E[C] = {rows[-1]['E_MNOK']:.3f} MNOK, "
              f"worst = {rows[-1]['worst_MNOK']:.3f} MNOK, "
              f"sum z = {rows[-1]['sum_z']:.1f}")

    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'step06_tradeoff.csv', index=False)
    with open(OUTPUT_DIR / 'step06_tradeoff.json', 'w', encoding='utf-8') as f:
        json.dump(rows, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step06_tradeoff.csv'}")

    plot_premium_curve(df, OUTPUT_DIR / 'ro_premium_curve.png')


if __name__ == '__main__':
    main()
