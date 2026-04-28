"""
Steg 4: Utslippsbevisst Clarke-Wright (Green CW)
================================================
Modifisert Clarke-Wright der savings beregnes paa utslipp i stedet for
distanse:

    s^E_{ij} = E_sep(i) + E_sep(j) - E_merge(i, j)

der E_sep(i) er CO2-utslippet paa den separate ruten (0 -> i -> 0) og
E_merge(i, j) er utslippet paa den sammenslaatte ruten. Denne formu-
leringen tar ikke bare hensyn til at fellesroute sparer avstand, men ogsaa
at den tyngste delen av rutene gir stoerst marginal gevinst naar bilen
kan skuve godset til kunden som ligger naermest depotet foerst.

Siden E_merge(i, j) avhenger av retning og av kundenes etterspoersel i
hele ruta, maa savings reberegnes ved hver merge. Derfor velger vi en
sekvensiell greedy implementasjon: ved hvert skritt beregner vi merge-
gevinsten for alle gyldige par (endepunkt-endepunkt, kapasitet OK),
velger den stoerste positive, gjennomfoerer merge, og gjentar.

Hver merge krever O(N^2) arbeid, og vi gjoer opp til N-1 merger, saa
total kompleksitet er O(N^3) --- fortsatt praktisk for N = 25.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step02_distanse_vrp import (
    DATA_DIR, OUTPUT_DIR, load_instance, plot_routes,
    route_distance, route_emissions, route_load, route_set_distance,
    route_set_emissions,
)


def total_emissions_of_routes(routes, D, demands, alpha, beta, kerb):
    return sum(route_emissions(r, D, demands, alpha, beta, kerb) for r in routes)


def try_merge_best(routes_dict, loads, D, demands, capacity, alpha, beta, kerb):
    """Finn det beste paret av ruter som reduserer total utslipp mest.

    Returnerer (best_delta, ri, rj, merged_route) eller (0, None, None, None).
    """
    # Kandidater: alle par (ri, rj) av forskjellige ruter der endepunktene
    # kan hektes sammen og samlet last <= kapasitet.
    ids = list(routes_dict.keys())
    best_delta = 0.0
    best = None

    for a_idx in range(len(ids)):
        for b_idx in range(a_idx + 1, len(ids)):
            ri = ids[a_idx]
            rj = ids[b_idx]
            if loads[ri] + loads[rj] > capacity + 1e-6:
                continue

            route_i = routes_dict[ri]
            route_j = routes_dict[rj]
            e_i = route_emissions(route_i, D, demands, alpha, beta, kerb)
            e_j = route_emissions(route_j, D, demands, alpha, beta, kerb)

            # Fire maater aa sette sammen to ruter paa (head/tail matching).
            # Hver rute har formen [0, ..., 0]. La interior_i = route_i[1:-1],
            # interior_j = route_j[1:-1].
            int_i = route_i[1:-1]
            int_j = route_j[1:-1]

            candidates = [
                [0] + int_i + int_j + [0],                 # i-forlengs, j-forlengs
                [0] + int_i + list(reversed(int_j)) + [0], # j reverseres
                [0] + list(reversed(int_i)) + int_j + [0], # i reverseres
                [0] + list(reversed(int_i)) + list(reversed(int_j)) + [0],
            ]

            for merged in candidates:
                e_m = route_emissions(merged, D, demands, alpha, beta, kerb)
                delta = (e_i + e_j) - e_m  # positiv = besparelse
                if delta > best_delta + 1e-6:
                    best_delta = delta
                    best = (ri, rj, merged)

    return best_delta, best


def green_clarke_wright(df, D, capacity_kg, alpha, beta, kerb):
    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    routes = {i: [0, i, 0] for i in range(1, n + 1)}
    loads = {i: float(demands[i]) for i in range(1, n + 1)}

    iterations = 0
    while True:
        best_delta, best = try_merge_best(routes, loads, D, demands,
                                           capacity_kg, alpha, beta, kerb)
        if best is None:
            break
        ri, rj, merged = best
        new_id = ri
        routes[new_id] = merged
        loads[new_id] = loads[ri] + loads[rj]
        if rj != new_id:
            del routes[rj]
            del loads[rj]
        iterations += 1

    return list(routes.values()), iterations


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 4: GREEN CLARKE-WRIGHT (UTSLIPPSBEVISST)')
    print('=' * 60)

    df, D, summary = load_instance()
    capacity = summary['vehicle_capacity_kg']
    alpha = summary['emission_alpha_g_per_km']
    beta = summary['emission_beta_g_per_kgkm']
    kerb = summary['kerb_weight_kg']

    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    routes, iters = green_clarke_wright(df, D, capacity, alpha, beta, kerb)

    total_dist = route_set_distance(routes, D)
    total_em_g = route_set_emissions(routes, D, demands, alpha, beta, kerb)
    total_em_kg = round(total_em_g / 1000.0, 2)

    print(f'\nIterasjoner (merges): {iters}')
    print(f'Antall ruter:         {len(routes)}')
    print(f'Total distanse:       {total_dist:.2f} km')
    print(f'Total CO2:            {total_em_kg:.2f} kg')
    for k, r in enumerate(routes):
        load = route_load(r, demands)
        dist = route_distance(r, D)
        em = route_emissions(r, D, demands, alpha, beta, kerb) / 1000.0
        print(f'  Rute {k + 1}: last = {load:.0f} kg, {dist:.2f} km, {em:.2f} kg CO2')

    plot_routes(df, routes, D,
                f'Green Clarke-Wright: {len(routes)} ruter, '
                f'{total_dist:.1f} km / {total_em_kg:.1f} kg CO$_2$',
                OUTPUT_DIR / 'gvrp_green_cw_routes.png',
                demands, capacity, alpha, beta, kerb, show_emissions=True)

    result = {
        'n_routes': len(routes),
        'iterations': int(iters),
        'total_distance_km': total_dist,
        'total_emissions_kg': total_em_kg,
        'routes': [[int(c) for c in r] for r in routes],
        'route_loads_kg': [float(route_load(r, demands)) for r in routes],
        'route_distances_km': [round(route_distance(r, D), 3) for r in routes],
        'route_emissions_g': [round(route_emissions(r, D, demands, alpha, beta, kerb), 1)
                              for r in routes],
    }
    with open(OUTPUT_DIR / 'step04_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {OUTPUT_DIR / "step04_results.json"}')


if __name__ == '__main__':
    main()
