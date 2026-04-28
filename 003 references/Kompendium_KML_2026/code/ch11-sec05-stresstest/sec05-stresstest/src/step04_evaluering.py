"""
Steg 4: Evaluering av scenarier
===============================
Kjorer baseline + alle fem scenarier med flere replikasjoner og lagrer
KPI-tabellen. For hvert scenario beregner vi:
  - Servicenivaa (fill rate)
  - Total kostnad (MNOK)
  - Gjennomsnittlig leveringsforsinkelse (uker)
  - Kostnadsokning vs baseline (MNOK)

Resultatet brukes i steg 5 og 6.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import baseline_supply_chain, OUTPUT_DIR
from step02_baseline_simulering import ScenarioOverrides, run_simulation
from step03_scenarier import all_scenarios


# ============================================================
# Evaluering
# ============================================================

def evaluate_scenario(overrides: ScenarioOverrides, n_replications: int = 30) -> dict:
    """Kjor et scenario n_replications ganger og returner aggregert KPI."""
    sc = baseline_supply_chain()
    service_levels = []
    total_costs = []
    delivery_delays = []
    shortfalls = []
    per_region_sls = {c.name: [] for c in sc.customers}

    for rep in range(n_replications):
        res = run_simulation(sc, overrides=overrides, seed=1000 + rep)
        service_levels.append(res['service_level'])
        total_costs.append(res['total_cost'])
        delivery_delays.append(res['mean_delivery_delay_weeks'])
        shortfalls.append(res['total_shortfall'])
        for r in per_region_sls:
            per_region_sls[r].append(res['per_region_service_level'][r])

    return {
        'scenario': overrides.name,
        'n_reps': n_replications,
        'service_level_mean': float(np.mean(service_levels)),
        'service_level_sd': float(np.std(service_levels, ddof=1)),
        'total_cost_mean': float(np.mean(total_costs)),
        'total_cost_sd': float(np.std(total_costs, ddof=1)),
        'delivery_delay_mean': float(np.mean(delivery_delays)),
        'shortfall_mean': float(np.mean(shortfalls)),
        'per_region_service_level_mean': {
            r: float(np.mean(v)) for r, v in per_region_sls.items()
        },
    }


def evaluate_all(n_reps: int = 30) -> list[dict]:
    """Evaluer baseline + alle scenarier."""
    results: list[dict] = []
    print(f"  Kjorer baseline ({n_reps} replikasjoner) ...")
    results.append(evaluate_scenario(ScenarioOverrides(name='Baseline'), n_reps))
    for sc in all_scenarios():
        print(f"  Kjorer {sc.name} ({n_reps} replikasjoner) ...")
        results.append(evaluate_scenario(sc, n_reps))
    return results


# ============================================================
# Visualisering
# ============================================================

FILLS = ['#CBD5E1', '#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']
STROKES = ['#556270', '#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']


def plot_scenario_compare(results: list[dict], output_path: Path) -> None:
    """Tre paneler: service level, total kostnad, forsinkelse."""
    names = [r['scenario'] for r in results]
    sls = [r['service_level_mean'] for r in results]
    sl_sd = [r['service_level_sd'] for r in results]
    costs = [r['total_cost_mean'] / 1e6 for r in results]
    cost_sd = [r['total_cost_sd'] / 1e6 for r in results]
    delays = [r['delivery_delay_mean'] for r in results]

    short_names = [n.replace('-', '\n', 1) for n in names]

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.8))

    # (a) Service level
    ax = axes[0]
    bars = ax.bar(short_names, [s * 100 for s in sls],
                  yerr=[s * 100 for s in sl_sd], capsize=4,
                  color=FILLS, edgecolor=STROKES, linewidth=1.6)
    ax.axhline(98, color='#961D1C', lw=1.2, linestyle='--', alpha=0.6,
               label='Maal: 98 %')
    for bar, v in zip(bars, sls):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f'{v*100:.1f} %', ha='center', va='bottom',
                fontsize=8, fontweight='bold')
    ax.set_ylim(40, 102)
    ax.set_ylabel('Servicenivaa (%)', fontsize=10)
    ax.set_title('(a) Servicenivaa', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(fontsize=9, loc='lower left')
    plt.setp(ax.get_xticklabels(), fontsize=8)

    # (b) Totalkostnad
    ax = axes[1]
    base_cost = costs[0]
    bars = ax.bar(short_names, costs,
                  yerr=cost_sd, capsize=4,
                  color=FILLS, edgecolor=STROKES, linewidth=1.6)
    ax.axhline(base_cost, color='#556270', lw=1.0, linestyle=':',
               alpha=0.5, label='Baseline')
    for bar, v in zip(bars, costs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6,
                f'{v:.1f}', ha='center', va='bottom',
                fontsize=8, fontweight='bold')
    ax.set_ylabel('Totalkostnad (MNOK / ar)', fontsize=10)
    ax.set_title('(b) Kostnad', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(fontsize=9, loc='upper left')
    plt.setp(ax.get_xticklabels(), fontsize=8)

    # (c) Forsinkelse
    ax = axes[2]
    bars = ax.bar(short_names, delays,
                  color=FILLS, edgecolor=STROKES, linewidth=1.6)
    for bar, v in zip(bars, delays):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.04,
                f'{v:.2f}', ha='center', va='bottom',
                fontsize=8, fontweight='bold')
    ax.set_ylabel('Gj.snitt forsinkelse (uker)', fontsize=10)
    ax.set_title('(c) Leveringsforsinkelse', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    plt.setp(ax.get_xticklabels(), fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


# ============================================================
# Hovedfunksjon
# ============================================================

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 4: EVALUERING AV SCENARIER")
    print("=" * 60)

    n_reps = 30
    results = evaluate_all(n_reps=n_reps)

    baseline = results[0]
    print(f"\n{'Scenario':22s} {'SL (%)':>8s} {'Cost (MNOK)':>13s} {'Delta C (MNOK)':>16s} {'Delay (w)':>11s}")
    for r in results:
        dC = (r['total_cost_mean'] - baseline['total_cost_mean']) / 1e6
        print(f"{r['scenario']:22s} "
              f"{r['service_level_mean']*100:>7.1f}  "
              f"{r['total_cost_mean']/1e6:>13.2f}  "
              f"{dC:>16.2f}  "
              f"{r['delivery_delay_mean']:>10.2f}")

    with open(OUTPUT_DIR / 'step04_evaluation.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False, default=float)
    print(f"\nEvaluering lagret: {OUTPUT_DIR / 'step04_evaluation.json'}")

    plot_scenario_compare(results, OUTPUT_DIR / 'st_scenario_compare.png')


if __name__ == '__main__':
    main()
