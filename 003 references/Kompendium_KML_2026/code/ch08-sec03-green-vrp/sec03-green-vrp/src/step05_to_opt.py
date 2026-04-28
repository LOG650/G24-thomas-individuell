"""
Steg 5: 2-opt lokal forbedring paa utslipp
==========================================
Gjennomfoerer 2-opt innenfor hver rute med CO2-utslipp som
maalefunksjon (i stedet for distanse). Forskjellen fra klassisk 2-opt er
at reversering av et subsegment endrer lasteprofilen langs ruta, slik at
kostnaden per kant ikke bare er en funksjon av avstand, men ogsaa av
nettopp rekkefoelgen.

Siden 2-opt opererer innenfor en rute uten aa endre kundebelastningen,
er kapasitetsbegrensningen automatisk oppfylt.

Vi kjoerer 2-opt paa loesningen fra Green Clarke-Wright (steg 4).
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


def two_opt_emission_route(route, D, demands, alpha, beta, kerb):
    """Iterer 2-opt paa en rute med CO2-objektet til lokalt optimum."""
    best = list(route)
    current_em = route_emissions(best, D, demands, alpha, beta, kerb)
    improved = True
    while improved:
        improved = False
        n = len(best)
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                candidate = best[:i] + list(reversed(best[i:j + 1])) + best[j + 1:]
                cand_em = route_emissions(candidate, D, demands, alpha, beta, kerb)
                if cand_em < current_em - 1e-6:
                    best = candidate
                    current_em = cand_em
                    improved = True
    return best, current_em


def two_opt_all(routes, D, demands, alpha, beta, kerb):
    out = []
    for r in routes:
        new_r, _ = two_opt_emission_route(r, D, demands, alpha, beta, kerb)
        out.append(new_r)
    return out


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 5: 2-OPT PAA UTSLIPP')
    print('=' * 60)

    df, D, summary = load_instance()
    capacity = summary['vehicle_capacity_kg']
    alpha = summary['emission_alpha_g_per_km']
    beta = summary['emission_beta_g_per_kgkm']
    kerb = summary['kerb_weight_kg']

    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    with open(OUTPUT_DIR / 'step04_results.json', 'r', encoding='utf-8') as f:
        step04 = json.load(f)
    routes_cw = step04['routes']

    em_before_g = route_set_emissions(routes_cw, D, demands, alpha, beta, kerb)
    dist_before = route_set_distance(routes_cw, D)

    routes_opt = two_opt_all(routes_cw, D, demands, alpha, beta, kerb)
    em_after_g = route_set_emissions(routes_opt, D, demands, alpha, beta, kerb)
    dist_after = route_set_distance(routes_opt, D)

    em_before_kg = round(em_before_g / 1000.0, 2)
    em_after_kg = round(em_after_g / 1000.0, 2)
    improvement_pct = 100.0 * (em_before_g - em_after_g) / em_before_g

    print(f'\nCO2 foer 2-opt: {em_before_kg:.2f} kg  (distanse {dist_before:.2f} km)')
    print(f'CO2 etter:      {em_after_kg:.2f} kg  (distanse {dist_after:.2f} km)')
    print(f'Forbedring:     {em_before_kg - em_after_kg:.2f} kg ({improvement_pct:.2f} %)')

    plot_routes(df, routes_opt, D,
                f'Green CW + 2-opt: {len(routes_opt)} ruter, '
                f'{dist_after:.1f} km / {em_after_kg:.1f} kg CO$_2$',
                OUTPUT_DIR / 'gvrp_green_routes.png',
                demands, capacity, alpha, beta, kerb, show_emissions=True)

    result = {
        'n_routes': len(routes_opt),
        'total_distance_km': dist_after,
        'total_emissions_kg': em_after_kg,
        'emissions_before_kg': em_before_kg,
        'improvement_pct': round(improvement_pct, 3),
        'routes': [[int(c) for c in r] for r in routes_opt],
        'route_loads_kg': [float(route_load(r, demands)) for r in routes_opt],
        'route_distances_km': [round(route_distance(r, D), 3) for r in routes_opt],
        'route_emissions_g': [round(route_emissions(r, D, demands, alpha, beta, kerb), 1)
                              for r in routes_opt],
    }
    with open(OUTPUT_DIR / 'step05_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {OUTPUT_DIR / "step05_results.json"}')


if __name__ == '__main__':
    main()
