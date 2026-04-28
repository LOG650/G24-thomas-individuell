"""
Steg 4: 2-opt lokal forbedring paa Clarke-Wright-losningen
===========================================================
Etter Clarke-Wright kjorer vi 2-opt innenfor hver rute.

2-opt: Forsok alle reverseringer av et subsegment [i+1 ... j] i rute
sekvensen. Aksepter endringen hvis den reduserer rutens distanse.
Siden ruten er en sykel 0 -> ... -> 0, er 2-opt gyldig innenfor hver
rute uavhengig (den endrer ikke lasten paa ruten).

Iterer til ingen forbedring finnes (lokalt optimum for hver rute).
"""

import json
from pathlib import Path

import numpy as np

from step02_narmeste_nabo import (
    DATA_DIR, OUTPUT_DIR, load_instance, plot_routes, route_load,
    route_set_distance,
)
from step03_clarke_wright import clarke_wright


def route_distance(route, D):
    return sum(D[a, b] for a, b in zip(route[:-1], route[1:]))


def two_opt_route(route, D):
    """Utfor 2-opt paa en enkelt rute til lokalt optimum."""
    best = list(route)
    n = len(best)
    improved = True
    while improved:
        improved = False
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                a, b = best[i - 1], best[i]
                c, d = best[j], best[j + 1]
                delta = (D[a, c] + D[b, d]) - (D[a, b] + D[c, d])
                if delta < -1e-9:
                    best[i:j + 1] = reversed(best[i:j + 1])
                    improved = True
        # Restart fra begynnelsen av ruten etter hver forbedring
    return best


def two_opt_all(routes, D):
    return [two_opt_route(r, D) for r in routes]


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 4: 2-OPT FORBEDRING')
    print('=' * 60)

    results = {}
    for tag in ['small', 'large']:
        df, D, capacity = load_instance(tag)

        # Start fra Clarke-Wright
        cw_routes, cw_total = clarke_wright(df, D, capacity)
        opt_routes = two_opt_all(cw_routes, D)
        opt_total = route_set_distance(opt_routes, D)

        demands = np.zeros(len(df) + 1, dtype=int)
        demands[1:] = df['demand'].to_numpy(dtype=int)

        improvement_pct = 100.0 * (cw_total - opt_total) / cw_total

        results[tag] = {
            'cw_distance': cw_total,
            'two_opt_distance': opt_total,
            'absolute_improvement': round(cw_total - opt_total, 2),
            'relative_improvement_pct': round(improvement_pct, 2),
            'n_routes': len(opt_routes),
            'routes': [[int(c) for c in r] for r in opt_routes],
            'route_loads': [route_load(r, demands) for r in opt_routes],
        }

        print(f"\n--- {tag.upper()} ---")
        print(f"Clarke-Wright distanse:  {cw_total} km")
        print(f"Etter 2-opt:             {opt_total} km")
        print(f"Forbedring:              {cw_total - opt_total:.2f} km ({improvement_pct:.2f} %)")

        if tag == 'large':
            plot_routes(df, opt_routes, D,
                        f'Clarke-Wright + 2-opt: {len(opt_routes)} ruter, total {opt_total:.1f} km',
                        OUTPUT_DIR / 'vrp_2opt_routes.png', capacity)

    with open(OUTPUT_DIR / 'step04_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step04_results.json'}")


if __name__ == '__main__':
    main()
