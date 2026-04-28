"""
Steg 2: Naermeste-nabo-heuristikk (CVRP)
========================================
Konstruktiv basislinje for CVRP: start en ny rute fra depot, dra gjentatte
ganger til naermeste ubesokte kunde som kan leveres innenfor gjenstaende
kapasitet, returner til depot nar ingen slike kunder finnes, og gjenta
til alle kunder er besokt.

Enkel og svaert rask (O(N^2)), men ignorerer global struktur og gir
typisk 15-40 % hoyere distanse enn Clarke-Wright eller 2-opt.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

PALETTE = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C',
           '#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']


def load_instance(tag: str):
    df = pd.read_csv(DATA_DIR / f'customers_{tag}.csv')
    D = np.loadtxt(DATA_DIR / f'distance_{tag}.csv', delimiter=',')
    with open(OUTPUT_DIR / 'step01_summary.json', 'r', encoding='utf-8') as f:
        summary = json.load(f)
    capacity = summary['vehicle_capacity']
    return df, D, capacity


def nearest_neighbor(df: pd.DataFrame, D: np.ndarray, capacity: int):
    """Konstruer CVRP-losning med naermeste-nabo.

    Returnerer (routes, total_distance). Hver rute er en liste
    [0, c1, c2, ..., 0] av kundeindeks (1..N), med depot som 0.
    """
    n = len(df)
    demands = np.zeros(n + 1, dtype=int)
    demands[1:] = df['demand'].to_numpy(dtype=int)

    unvisited = set(range(1, n + 1))
    routes = []

    while unvisited:
        route = [0]
        load = 0
        current = 0
        while True:
            # Finn naermeste ubesokte kunde som passer i gjenstaende kapasitet
            best = None
            best_dist = np.inf
            for j in unvisited:
                if load + demands[j] > capacity:
                    continue
                if D[current, j] < best_dist:
                    best_dist = D[current, j]
                    best = j
            if best is None:
                break
            route.append(best)
            load += demands[best]
            current = best
            unvisited.remove(best)
        route.append(0)
        routes.append(route)

    total = route_set_distance(routes, D)
    return routes, total


def route_set_distance(routes, D: np.ndarray) -> float:
    total = 0.0
    for r in routes:
        for a, b in zip(r[:-1], r[1:]):
            total += D[a, b]
    return round(float(total), 2)


def route_load(route, demands) -> int:
    return int(sum(demands[c] for c in route if c != 0))


def plot_routes(df, routes, D, title, output_path, capacity):
    fig, ax = plt.subplots(figsize=(9, 7))

    demands = np.zeros(len(df) + 1, dtype=int)
    demands[1:] = df['demand'].to_numpy(dtype=int)

    # Plot kunder
    sizes = 25 + 10 * df['demand'].to_numpy()
    ax.scatter(df['x'], df['y'], s=sizes,
               c='#CBD5E1', edgecolor='#556270', linewidth=0.6, zorder=2)
    for _, row in df.iterrows():
        ax.annotate(str(int(row['customer_id'])),
                    xy=(row['x'], row['y']),
                    xytext=(4, 4), textcoords='offset points',
                    fontsize=7, color='#1F2933', zorder=4)
    ax.scatter(0, 0, s=220, marker='s', c='#F6BA7C',
               edgecolor='#9C540B', linewidth=1.2, zorder=5, label='Depot')

    # Plot ruter
    coords = np.zeros((len(df) + 1, 2))
    coords[1:, 0] = df['x'].to_numpy()
    coords[1:, 1] = df['y'].to_numpy()

    for k, route in enumerate(routes):
        xs = [coords[c, 0] for c in route]
        ys = [coords[c, 1] for c in route]
        load = route_load(route, demands)
        color = PALETTE[k % len(PALETTE)]
        ax.plot(xs, ys, '-', color=color, linewidth=1.8, zorder=3,
                label=f'Rute {k + 1} ($q = {load}/{capacity}$)')

    ax.set_xlabel('$x$ (km)', fontsize=12)
    ax.set_ylabel('$y$ (km)', fontsize=12)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='datalim')
    ax.legend(loc='upper right', fontsize=8, ncol=1)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 2: NAERMESTE-NABO-HEURISTIKK')
    print('=' * 60)

    results = {}
    for tag in ['small', 'large']:
        df, D, capacity = load_instance(tag)
        routes, total = nearest_neighbor(df, D, capacity)

        demands = np.zeros(len(df) + 1, dtype=int)
        demands[1:] = df['demand'].to_numpy(dtype=int)

        results[tag] = {
            'total_distance': total,
            'n_routes': len(routes),
            'routes': [[int(c) for c in r] for r in routes],
            'route_loads': [route_load(r, demands) for r in routes],
        }

        print(f"\n--- {tag.upper()} ---")
        print(f"Antall ruter: {len(routes)}")
        print(f"Total distanse: {total} km")
        for k, r in enumerate(routes):
            print(f"  Rute {k + 1}: {r} (last = {route_load(r, demands)})")

        if tag == 'large':
            plot_routes(df, routes, D,
                        f'Naermeste-nabo: {len(routes)} ruter, total {total:.1f} km',
                        OUTPUT_DIR / 'vrp_nn_routes.png', capacity)

    with open(OUTPUT_DIR / 'step02_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step02_results.json'}")


if __name__ == '__main__':
    main()
