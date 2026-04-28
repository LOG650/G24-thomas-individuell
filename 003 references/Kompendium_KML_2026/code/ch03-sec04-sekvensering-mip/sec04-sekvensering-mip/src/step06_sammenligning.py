"""
Steg 6: Sammenligning av alle metoder
=====================================
Samler resultater fra step02, step04 og step05 og produserer:

    * Tabell (JSON) med vektet tardiness, makespan, losetid og
      optimalitetsgap for hver metode paa baade liten og stor instans.
    * Stolpediagram som sammenligner tardiness.

Optimalitetsgap for dispatch/SA paa liten instans beregnes mot CBC-
optimum. For stor instans finnes ingen kjent optimum, saa SA
sammenlignes mot beste dispatch-losning (referansegap).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_dispatch_heuristikker import (
    load_instance, spt_sequence, edd_sequence, atc_sequence, evaluate_sequence,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def gap_pct(value: float, reference: float) -> float:
    if reference <= 1e-9:
        return float('inf') if value > 1e-9 else 0.0
    return 100.0 * (value - reference) / reference


def build_small_table() -> list[dict]:
    """Tabellrader for N = 6 (MIP er referanse)."""
    df, S = load_instance('small')

    # Dispatch
    res_spt = evaluate_sequence(spt_sequence(df), df, S)
    res_edd = evaluate_sequence(edd_sequence(df), df, S)
    res_atc = evaluate_sequence(atc_sequence(df, S), df, S)

    # MIP resultat fra step04
    with open(OUTPUT_DIR / 'step04_mip_result.json', encoding='utf-8') as f:
        mip = json.load(f)

    mip_opt = mip['weighted_tardiness']
    mip_time = mip['solve_time_s']
    mip_make = mip['makespan']

    rows = [
        {
            'method': 'MIP (CBC)',
            'wtard': mip_opt,
            'makespan': mip_make,
            'num_tardy': mip['num_tardy'],
            'solve_time_s': mip_time,
            'gap_pct': 0.0,
        },
        {
            'method': 'ATC',
            'wtard': res_atc['weighted_tardiness'],
            'makespan': res_atc['makespan'],
            'num_tardy': res_atc['num_tardy'],
            'solve_time_s': 0.0,
            'gap_pct': round(gap_pct(res_atc['weighted_tardiness'], mip_opt), 2),
        },
        {
            'method': 'EDD',
            'wtard': res_edd['weighted_tardiness'],
            'makespan': res_edd['makespan'],
            'num_tardy': res_edd['num_tardy'],
            'solve_time_s': 0.0,
            'gap_pct': round(gap_pct(res_edd['weighted_tardiness'], mip_opt), 2),
        },
        {
            'method': 'SPT',
            'wtard': res_spt['weighted_tardiness'],
            'makespan': res_spt['makespan'],
            'num_tardy': res_spt['num_tardy'],
            'solve_time_s': 0.0,
            'gap_pct': round(gap_pct(res_spt['weighted_tardiness'], mip_opt), 2),
        },
    ]
    return rows


def build_large_table() -> list[dict]:
    df, S = load_instance('large')

    res_spt = evaluate_sequence(spt_sequence(df), df, S)
    res_edd = evaluate_sequence(edd_sequence(df), df, S)
    res_atc = evaluate_sequence(atc_sequence(df, S), df, S)

    with open(OUTPUT_DIR / 'step05_sa_result.json', encoding='utf-8') as f:
        sa = json.load(f)

    # Referanse for gap er beste heuristikk (SA) paa stor instans
    best_ref = min(
        sa['best_cost'],
        res_atc['weighted_tardiness'],
        res_edd['weighted_tardiness'],
        res_spt['weighted_tardiness'],
    )

    rows = [
        {
            'method': 'SA (metaheur.)',
            'wtard': sa['best_cost'],
            'makespan': sa['evaluation']['makespan'],
            'num_tardy': sa['evaluation']['num_tardy'],
            'solve_time_s': sa['solve_time_s'],
            'gap_pct': round(gap_pct(sa['best_cost'], best_ref), 2),
        },
        {
            'method': 'ATC',
            'wtard': res_atc['weighted_tardiness'],
            'makespan': res_atc['makespan'],
            'num_tardy': res_atc['num_tardy'],
            'solve_time_s': 0.0,
            'gap_pct': round(gap_pct(res_atc['weighted_tardiness'], best_ref), 2),
        },
        {
            'method': 'EDD',
            'wtard': res_edd['weighted_tardiness'],
            'makespan': res_edd['makespan'],
            'num_tardy': res_edd['num_tardy'],
            'solve_time_s': 0.0,
            'gap_pct': round(gap_pct(res_edd['weighted_tardiness'], best_ref), 2),
        },
        {
            'method': 'SPT',
            'wtard': res_spt['weighted_tardiness'],
            'makespan': res_spt['makespan'],
            'num_tardy': res_spt['num_tardy'],
            'solve_time_s': 0.0,
            'gap_pct': round(gap_pct(res_spt['weighted_tardiness'], best_ref), 2),
        },
    ]
    return rows


def plot_tardiness_compare(small_rows, large_rows, output_path: Path,
                           n_small: int, n_large: int) -> None:
    """To subplots: liten og stor instans."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    color_map = {
        'MIP (CBC)': '#1F6587',
        'SA (metaheur.)': '#5A2C77',
        'ATC': '#97D4B7',
        'EDD': '#F6BA7C',
        'SPT': '#ED9F9E',
    }

    for ax, rows, title in [
        (axes[0], small_rows, f'N = {n_small} (MIP gir optimum)'),
        (axes[1], large_rows, f'N = {n_large} (MIP upraktisk)'),
    ]:
        methods = [r['method'] for r in rows]
        values = [r['wtard'] for r in rows]
        colors = [color_map.get(m, '#8CC8E5') for m in methods]
        bars = ax.bar(methods, values, color=colors,
                      edgecolor='#1F2933', linewidth=0.8)
        for b, v in zip(bars, values):
            ax.text(b.get_x() + b.get_width() / 2,
                    b.get_height() + max(values) * 0.02,
                    f'{v:.1f}', ha='center', fontsize=9, color='#1F2933')
        ax.set_title(title, fontsize=11, fontweight='bold')
        ax.set_ylabel(r'Vektet tardiness $\sum_j w_j T_j$', fontsize=11)
        ax.grid(True, axis='y', alpha=0.3)
        ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 6: SAMMENLIGNING AV METODER')
    print('=' * 60)

    small_rows = build_small_table()
    large_rows = build_large_table()

    print('\n--- Liten instans N = 6 ---')
    print(f"{'Metode':<18}{'Sum w_j T_j':>14}{'Makespan':>10}"
          f"{'# tardy':>10}{'Tid (s)':>10}{'Gap (%)':>10}")
    for r in small_rows:
        print(f"{r['method']:<18}{r['wtard']:>14.2f}{r['makespan']:>10.2f}"
              f"{r['num_tardy']:>10}{r['solve_time_s']:>10.2f}{r['gap_pct']:>10.2f}")

    print('\n--- Stor instans N = 50 ---')
    print(f"{'Metode':<18}{'Sum w_j T_j':>14}{'Makespan':>10}"
          f"{'# tardy':>10}{'Tid (s)':>10}{'Gap (%)':>10}")
    for r in large_rows:
        print(f"{r['method']:<18}{r['wtard']:>14.2f}{r['makespan']:>10.2f}"
              f"{r['num_tardy']:>10}{r['solve_time_s']:>10.2f}{r['gap_pct']:>10.2f}")

    out = {'small_N15': small_rows, 'large_N50': large_rows}
    with open(OUTPUT_DIR / 'step06_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nSammenligning lagret: {OUTPUT_DIR / 'step06_comparison.json'}")

    df_small, _ = load_instance('small')
    df_large, _ = load_instance('large')
    plot_tardiness_compare(small_rows, large_rows,
                           OUTPUT_DIR / 'seqmip_tardiness_compare.png',
                           n_small=len(df_small), n_large=len(df_large))


if __name__ == '__main__':
    main()
