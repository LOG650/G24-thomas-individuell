"""
Steg 6: Sammenligning av metoder (CVRP)
=======================================
Samler alle resultater fra steg 2-5 i en sammenligningstabell og lager
en stolpe-graf som visualiserer total distanse per metode. Beregner
ogsaa gap mellom heuristikkene og MIP-optimum paa liten instans.
"""

import json
from pathlib import Path
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_narmeste_nabo import (
    DATA_DIR, OUTPUT_DIR, load_instance, nearest_neighbor,
)
from step03_clarke_wright import clarke_wright
from step04_to_opt import two_opt_all


def time_method(func, *args):
    t0 = time.time()
    result = func(*args)
    return result, round(time.time() - t0, 3)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 6: SAMMENLIGNING')
    print('=' * 60)

    # Kjor alle metoder paa begge instanser (fristt her for timing)
    records = []

    for tag in ['small', 'large']:
        df, D, capacity = load_instance(tag)
        n = len(df)

        (nn_routes, nn_total), nn_time = time_method(nearest_neighbor, df, D, capacity)
        (cw_routes, cw_total), cw_time = time_method(clarke_wright, df, D, capacity)
        cw_opt_routes = two_opt_all(cw_routes, D)
        # re-tid 2-opt separat for timing
        t0 = time.time()
        cw_opt_routes = two_opt_all(cw_routes, D)
        two_opt_time = round(time.time() - t0, 3)
        two_opt_total = round(sum(
            D[a, b] for r in cw_opt_routes for a, b in zip(r[:-1], r[1:])
        ), 2)

        records.append({
            'instans': tag, 'n': n, 'metode': 'Naermeste-nabo',
            'total': nn_total, 'n_ruter': len(nn_routes), 'tid_s': nn_time,
        })
        records.append({
            'instans': tag, 'n': n, 'metode': 'Clarke-Wright',
            'total': cw_total, 'n_ruter': len(cw_routes), 'tid_s': cw_time,
        })
        records.append({
            'instans': tag, 'n': n, 'metode': 'CW + 2-opt',
            'total': two_opt_total, 'n_ruter': len(cw_opt_routes),
            'tid_s': round(cw_time + two_opt_time, 3),
        })

    # Legg til MIP-resultat for liten instans
    with open(OUTPUT_DIR / 'step05_results.json', 'r', encoding='utf-8') as f:
        mip = json.load(f)
    mip_small = mip['small']
    records.append({
        'instans': 'small', 'n': 15, 'metode': 'MIP (CBC)',
        'total': mip_small['total_distance'],
        'n_ruter': mip_small['n_routes'],
        'tid_s': mip_small['runtime_s'],
    })

    # Beregn gap
    df_res = pd.DataFrame(records)

    # For liten instans: referanse = MIP
    # For stor instans: referanse = best av CW + 2-opt
    mip_small_val = mip_small['total_distance']
    best_large = df_res[df_res['instans'] == 'large']['total'].min()

    gaps = []
    for _, row in df_res.iterrows():
        if row['instans'] == 'small':
            ref = mip_small_val
        else:
            ref = best_large
        gap = 100.0 * (row['total'] - ref) / ref
        gaps.append(round(gap, 2))
    df_res['gap_pct'] = gaps

    print('\nResultater:')
    print(df_res.to_string(index=False))

    df_res.to_csv(OUTPUT_DIR / 'step06_comparison.csv', index=False)
    with open(OUTPUT_DIR / 'step06_comparison.json', 'w', encoding='utf-8') as f:
        json.dump(df_res.to_dict(orient='records'), f, indent=2, ensure_ascii=False)

    # Lag sammenligningsfigur
    plot_comparison(df_res, OUTPUT_DIR / 'vrp_compare_bar.png')


def plot_comparison(df_res: pd.DataFrame, output_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    methods_small = ['MIP (CBC)', 'CW + 2-opt', 'Clarke-Wright', 'Naermeste-nabo']
    methods_large = ['CW + 2-opt', 'Clarke-Wright', 'Naermeste-nabo']
    colors = {
        'MIP (CBC)': '#307453',
        'CW + 2-opt': '#1F6587',
        'Clarke-Wright': '#8CC8E5',
        'Naermeste-nabo': '#ED9F9E',
    }

    for ax, instans, methods, title in [
        (axes[0], 'small', methods_small, 'Liten instans ($N = 15$)'),
        (axes[1], 'large', methods_large, 'Stor instans ($N = 40$)'),
    ]:
        sub = df_res[df_res['instans'] == instans]
        sub = sub.set_index('metode').loc[methods]
        bars = ax.bar(methods, sub['total'], color=[colors[m] for m in methods],
                      edgecolor='#1F2933', linewidth=0.8)
        ax.set_ylabel('Total distanse (km)', fontsize=12)
        ax.set_title(title, fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        for bar, val, gap in zip(bars, sub['total'], sub['gap_pct']):
            ax.annotate(
                f'{val:.1f}\n({gap:+.1f} %)',
                xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
                xytext=(0, 3), textcoords='offset points',
                ha='center', va='bottom', fontsize=9, color='#1F2933',
            )
        ax.tick_params(axis='x', rotation=15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'\nFigur lagret: {output_path}')


if __name__ == '__main__':
    main()
