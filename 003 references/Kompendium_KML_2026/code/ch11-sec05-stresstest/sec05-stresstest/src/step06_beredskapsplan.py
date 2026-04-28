"""
Steg 6: Beredskapsplan og prioritering
======================================
Sluttresultatet: en prioritert beredskapsplan basert pa hvilke tiltak som
gir storst nytte for de ulike scenariene.

Vi bygger en (tiltak x scenario)-matrise der hver celle er den prosentvise
kostnadsreduksjonen tiltaket gir for det scenariet. Heatmap + rangert
tabell viser hvilke tiltak som er mest virkningsfulle per scenario.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap

from step01_datainnsamling import OUTPUT_DIR


def load_results() -> dict:
    with open(OUTPUT_DIR / 'step05_mitigations.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def build_reduction_matrix(sim_results: dict) -> tuple[list[str], list[str], np.ndarray]:
    """Returner (mitigations, scenarios, reduction_matrix) der hver celle er
    prosent kostnadsreduksjon (tiltak x scenario) ift Status-quo."""
    sq = sim_results['Status-quo']
    scenarios = list(sq['scenario_results'].keys())
    mitigations = [m for m in sim_results.keys() if m != 'Status-quo']

    matrix = np.zeros((len(mitigations), len(scenarios)))
    for i, m in enumerate(mitigations):
        for j, s in enumerate(scenarios):
            sq_cost = sq['scenario_results'][s]['cost_mean']
            mit_cost = sim_results[m]['scenario_results'][s]['cost_mean']
            reduction_pct = 100.0 * (sq_cost - mit_cost) / sq_cost
            matrix[i, j] = reduction_pct
    return mitigations, scenarios, matrix


def plot_prioritization_heatmap(mitigations, scenarios, matrix: np.ndarray,
                                cb_rows: list[dict], output_path: Path) -> None:
    """Heatmap: rader = tiltak, kolonner = scenario; celle = kostnadsreduksjon %."""
    fig = plt.figure(figsize=(13, 6.5))
    gs = fig.add_gridspec(1, 2, width_ratios=[3.0, 1.0], wspace=0.25)
    ax = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    # Lag en tilpasset colormap (hvit -> s2 (mint))
    cmap = LinearSegmentedColormap.from_list(
        'mintramp', ['#FFFFFF', '#C9EBDA', '#97D4B7', '#307453'], N=256)

    vmax = max(10.0, np.nanmax(matrix))
    vmin = min(-5.0, np.nanmin(matrix))
    im = ax.imshow(matrix, cmap=cmap, vmin=vmin, vmax=vmax, aspect='auto')

    ax.set_xticks(np.arange(len(scenarios)))
    ax.set_xticklabels([s.replace('-', '\n', 1) for s in scenarios],
                       fontsize=9, rotation=20, ha='right')
    ax.set_yticks(np.arange(len(mitigations)))
    ax.set_yticklabels(mitigations, fontsize=9)

    # Annotater hver celle
    for i in range(len(mitigations)):
        for j in range(len(scenarios)):
            v = matrix[i, j]
            color = '#FFFFFF' if v > 0.55 * vmax else '#1F2933'
            ax.text(j, i, f'{v:+.1f}%', ha='center', va='center',
                    fontsize=9, color=color, fontweight='bold')

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Kostnadsreduksjon (%)', fontsize=10)
    ax.set_title('Tiltak x scenario: prosentvis kostnadsreduksjon',
                 fontsize=11, fontweight='bold')

    # Panel 2: rangert netto nytte
    sorted_cb = sorted([r for r in cb_rows if r['mitigation'] != 'Status-quo'],
                       key=lambda r: r['net_benefit'], reverse=True)
    names = [r['mitigation'] for r in sorted_cb]
    nbs = [r['net_benefit'] / 1e6 for r in sorted_cb]
    colors = ['#307453' if v > 0 else '#961D1C' for v in nbs]
    y_pos = np.arange(len(names))
    ax2.barh(y_pos, nbs, color=colors, edgecolor='#1F2933', linewidth=1.2, alpha=0.9)
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(names, fontsize=9)
    ax2.invert_yaxis()
    ax2.axvline(0, color='#1F2933', lw=1.0)
    for i, v in enumerate(nbs):
        ax2.text(v + (0.2 if v >= 0 else -0.2), i, f'{v:+.1f}',
                 va='center', ha='left' if v >= 0 else 'right',
                 fontsize=9, fontweight='bold')
    ax2.set_xlabel('Netto arlig nytte (MNOK)', fontsize=10)
    ax2.set_title('Rangert etter nytte', fontsize=11, fontweight='bold')
    ax2.grid(True, axis='x', alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def build_contingency_plan(mitigations, scenarios, matrix, cb_rows) -> list[dict]:
    """For hvert scenario: hvilket tiltak virker best (storst reduksjon)?"""
    # Filter ut status-quo
    cb_map = {r['mitigation']: r for r in cb_rows if r['mitigation'] != 'Status-quo'}
    plan = []
    for j, s in enumerate(scenarios):
        idx = int(np.argmax(matrix[:, j]))
        best = mitigations[idx]
        plan.append({
            'scenario': s,
            'primary_mitigation': best,
            'cost_reduction_pct': float(matrix[idx, j]),
            'annual_cost_mnok': cb_map[best]['annual_impl_cost'] / 1e6,
            'net_benefit_mnok': cb_map[best]['net_benefit'] / 1e6,
        })
    return plan


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 6: BEREDSKAPSPLAN")
    print("=" * 60)

    data = load_results()
    sim_results = data['simulation_results']
    cb = data['cost_benefit']

    mitigations, scenarios, matrix = build_reduction_matrix(sim_results)

    print("\nKostnadsreduksjon (%):")
    print(f"{'':28s} " + " ".join(f"{s[:14]:>14s}" for s in scenarios))
    for i, m in enumerate(mitigations):
        print(f"{m:28s} " + " ".join(f"{matrix[i, j]:>+13.1f}%" for j in range(len(scenarios))))

    plan = build_contingency_plan(mitigations, scenarios, matrix, cb)
    print("\nForeslatt beredskapsplan (primartiltak pr scenario):")
    print(f"{'Scenario':22s} {'Primartiltak':28s} {'Reduksjon':>11s} "
          f"{'Kostnad':>10s} {'Netto':>10s}")
    for row in plan:
        print(f"{row['scenario']:22s} {row['primary_mitigation']:28s} "
              f"{row['cost_reduction_pct']:>+10.1f}% "
              f"{row['annual_cost_mnok']:>9.2f}  "
              f"{row['net_benefit_mnok']:>+9.2f}")

    with open(OUTPUT_DIR / 'step06_contingency.json', 'w', encoding='utf-8') as f:
        json.dump({
            'mitigations': mitigations,
            'scenarios': scenarios,
            'reduction_matrix_pct': matrix.tolist(),
            'contingency_plan': plan,
        }, f, indent=2, ensure_ascii=False)
    print(f"\nBeredskapsplan lagret: {OUTPUT_DIR / 'step06_contingency.json'}")

    plot_prioritization_heatmap(mitigations, scenarios, matrix, cb,
                                OUTPUT_DIR / 'st_prioritization_heatmap.png')


if __name__ == '__main__':
    main()
