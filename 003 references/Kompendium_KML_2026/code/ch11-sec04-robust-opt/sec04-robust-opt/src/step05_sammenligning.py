"""
Steg 5: Sammenligning
======================
Evaluerer de tre kapasitetsvektorene

    z_det     -- fra deterministisk baseline (nominell d_bar)
    z_stoch   -- fra scenariobasert stokastisk LP (50 scenarier)
    z_rob     -- fra minimax-regret

paa et felles evalueringssett (500 nye scenarier trukket fra U). Rapporterer
forventet kostnad, verste kostnad, standardavvik og regret pr strategi.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from model_utils import (OUTPUT_DIR, cost_at, load_instance,
                          sample_interior_scenarios, solve_deterministic)

C_DET = '#ED9F9E'       # s5 coral
C_DET_DARK = '#961D1C'
C_STOCH = '#8CC8E5'     # s1 blue
C_STOCH_DARK = '#1F6587'
C_ROB = '#97D4B7'       # s2 green
C_ROB_DARK = '#307453'
C_INK = '#1F2933'


def evaluate_strategy(inst, z: np.ndarray, scenarios: np.ndarray) -> np.ndarray:
    """Returnerer totalkostnad per scenario."""
    return np.array([cost_at(inst, z, scenarios[s])['total']
                     for s in range(len(scenarios))])


def plot_cost_distribution(costs: dict, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 5.0))

    cols = [(C_DET_DARK, C_DET), (C_STOCH_DARK, C_STOCH), (C_ROB_DARK, C_ROB)]
    labels = ['Deterministisk', 'Stokastisk', 'Robust (minimax regret)']
    bins = np.linspace(min(c.min() for c in costs.values()) / 1e6,
                        max(c.max() for c in costs.values()) / 1e6,
                        25)
    for (edge, fill), label, key in zip(cols, labels, ['det', 'stoch', 'rob']):
        ax.hist(costs[key] / 1e6, bins=bins, alpha=0.55,
                color=fill, edgecolor=edge, linewidth=1.1, label=label)

    ax.set_xlabel('Totalkostnad C(z, d) (MNOK)', fontsize=11)
    ax.set_ylabel('Antall scenarioer', fontsize=11)
    ax.set_title('Kostnadsfordeling over 500 evalueringsscenarioer',
                 fontsize=12, fontweight='bold', color=C_INK)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_solutions_compare(inst, z_det, z_stoch, z_rob, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    x = np.arange(inst.n)
    w = 0.25

    ax.bar(x - w, z_det, w, color=C_DET, edgecolor=C_DET_DARK,
           linewidth=1.2, label='Deterministisk $z^{det}$')
    ax.bar(x, z_stoch, w, color=C_STOCH, edgecolor=C_STOCH_DARK,
           linewidth=1.2, label='Stokastisk $z^{stoch}$')
    ax.bar(x + w, z_rob, w, color=C_ROB, edgecolor=C_ROB_DARK,
           linewidth=1.2, label='Robust $z^{rob}$')

    ax.set_xticks(x)
    ax.set_xticklabels(inst.df_w['navn'], fontsize=10)
    ax.set_ylabel('Kapasitet $z_i$ (tonn/aar)', fontsize=11)
    ax.set_title('Kapasitetsallokering paa tvers av strategier',
                 fontsize=12, fontweight='bold', color=C_INK)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_regret_scatter(regret: dict, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    order = ['det', 'stoch', 'rob']
    labels = ['Deterministisk', 'Stokastisk', 'Robust']
    fills = [C_DET, C_STOCH, C_ROB]
    edges = [C_DET_DARK, C_STOCH_DARK, C_ROB_DARK]

    positions = range(len(order))
    data = [regret[k] / 1e6 for k in order]
    bp = ax.boxplot(data, positions=list(positions), widths=0.55,
                     patch_artist=True, showfliers=True)
    for patch, fill, edge in zip(bp['boxes'], fills, edges):
        patch.set_facecolor(fill)
        patch.set_edgecolor(edge)
        patch.set_linewidth(1.2)
    for med in bp['medians']:
        med.set_color(C_INK)
        med.set_linewidth(1.4)

    ax.set_xticks(list(positions))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel('Regret $C(z, d) - C^*(d)$ (MNOK)', fontsize=11)
    ax.set_title('Regret-fordeling over 500 scenarioer',
                 fontsize=12, fontweight='bold', color=C_INK)
    ax.grid(True, alpha=0.3, axis='y')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: SAMMENLIGNING")
    print("=" * 60)

    inst = load_instance()

    # Last inn z-vektorer
    z_det = np.load(OUTPUT_DIR / 'step02_z_det.npz')['z']
    z_stoch = np.load(OUTPUT_DIR / 'step04_stochastic.npz')['z']
    z_rob = np.load(OUTPUT_DIR / 'step03_robust.npz')['z']

    # Evalueringssett: 500 nye scenarioer trukket fra U
    eval_S = 500
    eval_scen = sample_interior_scenarios(inst, eval_S, seed=99999)
    print(f"Evaluerer 3 strategier paa {eval_S} nye scenarioer ...")

    # Perfekt-info-kostnad per scenario (for regret)
    print("  beregner C*(d) paa evalueringssettet ...")
    cstar_eval = np.array([solve_deterministic(inst, eval_scen[s])['obj']
                           for s in range(eval_S)])

    print("  evaluerer z_det ...")
    cost_det = evaluate_strategy(inst, z_det, eval_scen)
    print("  evaluerer z_stoch ...")
    cost_stoch = evaluate_strategy(inst, z_stoch, eval_scen)
    print("  evaluerer z_rob ...")
    cost_rob = evaluate_strategy(inst, z_rob, eval_scen)

    regret = {
        'det':   cost_det - cstar_eval,
        'stoch': cost_stoch - cstar_eval,
        'rob':   cost_rob - cstar_eval,
    }
    costs = {'det': cost_det, 'stoch': cost_stoch, 'rob': cost_rob}

    # Worst-case over evalueringssettet
    summary_rows = []
    for key, name in [('det', 'Deterministisk'),
                       ('stoch', 'Stokastisk'),
                       ('rob', 'Robust')]:
        c = costs[key]
        r = regret[key]
        summary_rows.append({
            'Strategi': name,
            'E_kostnad_MNOK': round(c.mean() / 1e6, 3),
            'worst_kostnad_MNOK': round(c.max() / 1e6, 3),
            'std_kostnad_MNOK': round(c.std() / 1e6, 3),
            'E_regret_MNOK': round(r.mean() / 1e6, 3),
            'maks_regret_MNOK': round(r.max() / 1e6, 3),
            'sum_kapasitet': round(float({'det': z_det, 'stoch': z_stoch,
                                          'rob': z_rob}[key].sum()), 1),
        })
    df_sum = pd.DataFrame(summary_rows)
    df_sum.to_csv(OUTPUT_DIR / 'step05_summary.csv', index=False)

    # "Forsikringspremie" av robust losning
    premium_rob_abs = cost_rob.mean() - cost_stoch.mean()
    premium_rob_pct = 100 * premium_rob_abs / cost_stoch.mean()
    worst_reduction_abs = cost_stoch.max() - cost_rob.max()
    worst_reduction_pct = 100 * worst_reduction_abs / cost_stoch.max()

    summary = {
        'eval_S': int(eval_S),
        'rad': summary_rows,
        'forsikringspremie_abs_MNOK': round(premium_rob_abs / 1e6, 3),
        'forsikringspremie_pct': round(premium_rob_pct, 2),
        'worst_case_reduksjon_abs_MNOK': round(worst_reduction_abs / 1e6, 3),
        'worst_case_reduksjon_pct': round(worst_reduction_pct, 2),
    }
    with open(OUTPUT_DIR / 'step05_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering lagret: {OUTPUT_DIR / 'step05_summary.json'}")
    print(df_sum.to_string(index=False))
    print(f"\nForsikringspremie (E[C_rob] - E[C_stoch]): "
          f"+{premium_rob_abs/1e6:.3f} MNOK ({premium_rob_pct:+.2f}%)")
    print(f"Worst-case reduksjon (max C_stoch -> max C_rob): "
          f"-{worst_reduction_abs/1e6:.3f} MNOK ({worst_reduction_pct:+.2f}%)")

    # Figurer
    plot_cost_distribution(costs, OUTPUT_DIR / 'ro_cost_distribution.png')
    plot_solutions_compare(inst, z_det, z_stoch, z_rob,
                           OUTPUT_DIR / 'ro_solutions_compare.png')
    plot_regret_scatter(regret, OUTPUT_DIR / 'ro_regret_scatter.png')


if __name__ == '__main__':
    main()
