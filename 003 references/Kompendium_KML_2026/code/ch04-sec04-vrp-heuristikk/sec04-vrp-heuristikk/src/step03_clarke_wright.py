"""
Steg 3: Clarke-Wright savings-algoritmen (CVRP)
===============================================
Sekvensiell implementasjon av den klassiske savings-heuristikken
(Clarke & Wright 1964).

Idé:
    Initielt har hver kunde sin egen dedikerte rute depot -> i -> depot.
    Besparelsen ved a slaa sammen ruter som ender i i og starter i j er

        s_{ij} = d_{0i} + d_{0j} - d_{ij}

    Sorter (i,j)-par etter s_{ij} fallende, og slaa sammen rutene naar
    s_{ij} > 0, kundene ligger i ulike ruter, og samlet last ikke
    overstiger Q.

Den sekvensielle varianten vokser alltid en eksisterende rute (ved at i
eller j er endepunkt), slik at kvaliteten typisk ligger 5-15 % over
naermeste-nabo og innenfor noen faa prosent av optimum pa smaa instanser.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step02_narmeste_nabo import (
    DATA_DIR, OUTPUT_DIR, load_instance, plot_routes, route_load,
    route_set_distance,
)


def clarke_wright(df: pd.DataFrame, D: np.ndarray, capacity: int):
    """Sekvensiell Clarke-Wright savings-algoritme."""
    n = len(df)
    demands = np.zeros(n + 1, dtype=int)
    demands[1:] = df['demand'].to_numpy(dtype=int)

    # Initialiser: hver kunde i sin egen rute [0, i, 0]
    routes = {i: [0, i, 0] for i in range(1, n + 1)}
    route_of = {i: i for i in range(1, n + 1)}
    loads = {i: int(demands[i]) for i in range(1, n + 1)}

    # Beregn besparelser s_{ij} = d_{0i} + d_{0j} - d_{ij} for i < j
    savings = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            s = D[0, i] + D[0, j] - D[i, j]
            if s > 0:
                savings.append((s, i, j))

    savings.sort(reverse=True)

    for s, i, j in savings:
        ri = route_of[i]
        rj = route_of[j]
        if ri == rj:
            continue  # samme rute allerede
        if loads[ri] + loads[rj] > capacity:
            continue

        route_i = routes[ri]
        route_j = routes[rj]

        # Sjekk at i er endepunkt i sin rute (rett for depot)
        i_is_tail = route_i[-2] == i
        i_is_head = route_i[1] == i
        j_is_tail = route_j[-2] == j
        j_is_head = route_j[1] == j

        merged = None
        if i_is_tail and j_is_head:
            # ... -> i -> 0 + 0 -> j -> ... =>  ... -> i -> j -> ...
            merged = route_i[:-1] + route_j[1:]
        elif i_is_head and j_is_tail:
            merged = route_j[:-1] + route_i[1:]
        elif i_is_tail and j_is_tail:
            # sny rute j slik at j blir head (fortsatt gyldig siden symmetrisk)
            merged = route_i[:-1] + list(reversed(route_j))[1:]
        elif i_is_head and j_is_head:
            merged = list(reversed(route_i))[:-1] + route_j[1:]
        else:
            continue  # minst en av dem er indre kunde, ignorer

        # Utfor merge
        new_id = ri
        routes[new_id] = merged
        loads[new_id] = loads[ri] + loads[rj]
        del routes[rj]
        del loads[rj]
        # Oppdater route_of
        for c in merged:
            if c != 0:
                route_of[c] = new_id

    final_routes = list(routes.values())
    total = route_set_distance(final_routes, D)
    return final_routes, total


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 3: CLARKE-WRIGHT SAVINGS')
    print('=' * 60)

    results = {}
    for tag in ['small', 'large']:
        df, D, capacity = load_instance(tag)
        routes, total = clarke_wright(df, D, capacity)

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
                        f'Clarke-Wright: {len(routes)} ruter, total {total:.1f} km',
                        OUTPUT_DIR / 'vrp_cw_routes.png', capacity)

    with open(OUTPUT_DIR / 'step03_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step03_results.json'}")


if __name__ == '__main__':
    main()
