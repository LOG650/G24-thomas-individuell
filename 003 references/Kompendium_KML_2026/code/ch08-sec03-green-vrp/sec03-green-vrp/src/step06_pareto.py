"""
Steg 6: Pareto-front kostnad vs CO2
===================================
Vi interpolerer mellom distanse-optimert og utslipp-optimert loesning ved
aa optimere en vektet objektivfunksjon

    f_lam(R) = (1 - lam) * dist_norm(R) + lam * em_norm(R)

der dist_norm og em_norm er normaliserte per-rute-kostnader. For lam = 0
tilsvarer dette distanse-optimum (steg 2); for lam = 1 tilsvarer det
utslipps-optimum (steg 4+5). Ved aa variere lam fra 0 til 1 tegner vi
Pareto-fronten.

Hver verdi av lam gir et nytt Clarke-Wright-kjoer med savings basert paa
den vektede kostnaden, fulgt av 2-opt der forbedringer maales paa samme
vektede kostnad.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_distanse_vrp import (
    DATA_DIR, OUTPUT_DIR, load_instance,
    route_distance, route_emissions, route_load, route_set_distance,
    route_set_emissions,
)
from step04_green_cw import try_merge_best


def weighted_edge_cost(i, j, load_kg, D, alpha, beta, kerb, lam, dist_scale, em_scale):
    """Normalisert vektet kost for en kant fra i til j med last load_kg paa bilen."""
    d = D[i, j]
    w = kerb + load_kg
    em = d * (alpha + beta * w)
    return (1 - lam) * d / dist_scale + lam * em / em_scale


def route_weighted_cost(route, D, demands, alpha, beta, kerb,
                         lam, dist_scale, em_scale):
    total_load = sum(demands[c] for c in route if c != 0)
    current_load = total_load
    total_cost = 0.0
    for a, b in zip(route[:-1], route[1:]):
        total_cost += weighted_edge_cost(a, b, current_load, D,
                                          alpha, beta, kerb,
                                          lam, dist_scale, em_scale)
        if b != 0:
            current_load -= demands[b]
    return total_cost


def try_merge_best_weighted(routes_dict, loads, D, demands, capacity,
                             alpha, beta, kerb, lam, dist_scale, em_scale):
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
            c_i = route_weighted_cost(route_i, D, demands, alpha, beta, kerb,
                                       lam, dist_scale, em_scale)
            c_j = route_weighted_cost(route_j, D, demands, alpha, beta, kerb,
                                       lam, dist_scale, em_scale)

            int_i = route_i[1:-1]
            int_j = route_j[1:-1]
            candidates = [
                [0] + int_i + int_j + [0],
                [0] + int_i + list(reversed(int_j)) + [0],
                [0] + list(reversed(int_i)) + int_j + [0],
                [0] + list(reversed(int_i)) + list(reversed(int_j)) + [0],
            ]
            for merged in candidates:
                c_m = route_weighted_cost(merged, D, demands, alpha, beta, kerb,
                                           lam, dist_scale, em_scale)
                delta = (c_i + c_j) - c_m
                if delta > best_delta + 1e-9:
                    best_delta = delta
                    best = (ri, rj, merged)
    return best_delta, best


def green_cw_weighted(df, D, capacity, alpha, beta, kerb, lam,
                      dist_scale, em_scale):
    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    routes = {i: [0, i, 0] for i in range(1, n + 1)}
    loads = {i: float(demands[i]) for i in range(1, n + 1)}

    while True:
        delta, best = try_merge_best_weighted(routes, loads, D, demands,
                                               capacity, alpha, beta, kerb,
                                               lam, dist_scale, em_scale)
        if best is None:
            break
        ri, rj, merged = best
        new_id = ri
        routes[new_id] = merged
        loads[new_id] = loads[ri] + loads[rj]
        if rj != new_id:
            del routes[rj]
            del loads[rj]

    return list(routes.values())


def two_opt_weighted(route, D, demands, alpha, beta, kerb, lam,
                      dist_scale, em_scale):
    best = list(route)
    current_cost = route_weighted_cost(best, D, demands, alpha, beta, kerb,
                                        lam, dist_scale, em_scale)
    improved = True
    while improved:
        improved = False
        n = len(best)
        for i in range(1, n - 2):
            for j in range(i + 1, n - 1):
                candidate = best[:i] + list(reversed(best[i:j + 1])) + best[j + 1:]
                c = route_weighted_cost(candidate, D, demands, alpha, beta, kerb,
                                         lam, dist_scale, em_scale)
                if c < current_cost - 1e-9:
                    best = candidate
                    current_cost = c
                    improved = True
    return best


def solve_for_lambda(df, D, demands, capacity, alpha, beta, kerb, lam,
                     dist_scale, em_scale):
    routes = green_cw_weighted(df, D, capacity, alpha, beta, kerb, lam,
                                dist_scale, em_scale)
    routes = [two_opt_weighted(r, D, demands, alpha, beta, kerb, lam,
                                dist_scale, em_scale) for r in routes]
    dist = route_set_distance(routes, D)
    em_g = route_set_emissions(routes, D, demands, alpha, beta, kerb)
    return routes, dist, em_g


def pareto_filter(points):
    """Filtrer til Pareto-front for (min dist, min em). Beholder ikke-dominerte punkter."""
    # Sorter etter distanse stigende; paa lik distanse velg den med lavest em foerst.
    sorted_points = sorted(points, key=lambda p: (p[1], p[2]))
    front = []
    best_em = np.inf
    for lam, d, em, routes in sorted_points:
        if em < best_em - 1e-6:
            front.append((lam, d, em, routes))
            best_em = em
    return front


def plot_pareto(all_points, front_points, output_path: Path):
    fig, ax = plt.subplots(figsize=(9.5, 6.2))

    # Grupper alle_points etter (d, em) for aa finne unike loesninger
    unique = {}
    for lam, d, em_g, _ in all_points:
        key = (round(d, 3), round(em_g, 1))
        if key not in unique:
            unique[key] = []
        unique[key].append(lam)

    # Plot alle unike loesninger som graa punkter med lambda-intervaller
    for (d, em_g), lams in unique.items():
        em_kg = em_g / 1000.0
        ax.scatter([d], [em_kg], s=70, color='#CBD5E1',
                   edgecolor='#556270', linewidth=0.7, zorder=2)
        lam_str = ', '.join(f'{l:.2f}' for l in sorted(lams))
        ax.annotate(f'$\\lambda \\in \\{{{lam_str}\\}}$',
                    xy=(d, em_kg), xytext=(8, -12),
                    textcoords='offset points',
                    fontsize=8, color='#556270')

    # Pareto-front som linje
    front_d = [p[1] for p in front_points]
    front_e = [p[2] / 1000.0 for p in front_points]
    ax.plot(front_d, front_e, '-', color='#1F6587', linewidth=2.4, zorder=3,
            label='Pareto-front')

    # Marker endepunktene
    i_dmin = int(np.argmin(front_d))
    i_emin = int(np.argmin(front_e))
    ax.scatter([front_d[i_dmin]], [front_e[i_dmin]],
               s=200, marker='D', color='#F6BA7C',
               edgecolor='#9C540B', linewidth=1.4, zorder=5,
               label='Distanse-min')
    ax.scatter([front_d[i_emin]], [front_e[i_emin]],
               s=240, marker='*', color='#97D4B7',
               edgecolor='#307453', linewidth=1.4, zorder=5,
               label='Utslipp-min')

    # Annotasjoner pa endepunktene
    ax.annotate(f'{front_d[i_dmin]:.2f} km\n{front_e[i_dmin]:.2f} kg CO$_2$',
                xy=(front_d[i_dmin], front_e[i_dmin]),
                xytext=(-75, 15), textcoords='offset points',
                fontsize=9, color='#9C540B', ha='left',
                bbox=dict(boxstyle='round,pad=0.3', fc='#FFFFFF',
                           ec='#9C540B', lw=0.8, alpha=0.9))
    ax.annotate(f'{front_d[i_emin]:.2f} km\n{front_e[i_emin]:.2f} kg CO$_2$',
                xy=(front_d[i_emin], front_e[i_emin]),
                xytext=(12, -20), textcoords='offset points',
                fontsize=9, color='#307453', ha='left',
                bbox=dict(boxstyle='round,pad=0.3', fc='#FFFFFF',
                           ec='#307453', lw=0.8, alpha=0.9))

    ax.set_xlabel('Total distanse (km)', fontsize=12)
    ax.set_ylabel('Totale CO$_2$-utslipp (kg)', fontsize=12)
    ax.set_title('Pareto-front: kostnad mot utslipp',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper left', fontsize=10)

    # Marginer basert paa ALLE punkter, slik at dominerte punkter ogsaa vises.
    all_d = [p[1] for p in all_points]
    all_e = [p[2] / 1000.0 for p in all_points]
    d_pad = max(0.3, 0.2 * (max(all_d) - min(all_d)))
    e_pad = max(0.3, 0.2 * (max(all_e) - min(all_e)))
    ax.set_xlim(min(all_d) - d_pad, max(all_d) + d_pad * 1.5)
    ax.set_ylim(min(all_e) - e_pad, max(all_e) + e_pad * 1.5)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 6: PARETO-FRONT KOSTNAD VS UTSLIPP')
    print('=' * 60)

    df, D, summary = load_instance()
    capacity = summary['vehicle_capacity_kg']
    alpha = summary['emission_alpha_g_per_km']
    beta = summary['emission_beta_g_per_kgkm']
    kerb = summary['kerb_weight_kg']

    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    # Kalibrer skalering ved aa kjore CW for lam=0 og lam=1 foerst
    # (saa blir begge termene omtrent i samme stoerrelsesorden etter normalisering).
    with open(OUTPUT_DIR / 'step02_results.json', 'r', encoding='utf-8') as f:
        step02 = json.load(f)
    with open(OUTPUT_DIR / 'step05_results.json', 'r', encoding='utf-8') as f:
        step05 = json.load(f)

    dist_scale = step02['total_distance_km']
    em_scale = step05['total_emissions_kg'] * 1000.0  # gram

    lambdas = [0.00, 0.20, 0.40, 0.55, 0.70, 0.85, 0.95, 1.00]
    all_points = []

    print(f'\n{"lam":>6} {"dist_km":>10} {"em_kg":>10} {"n_rutes":>8}')
    print('-' * 36)
    for lam in lambdas:
        routes, dist_km, em_g = solve_for_lambda(
            df, D, demands, capacity, alpha, beta, kerb, lam,
            dist_scale, em_scale,
        )
        em_kg = em_g / 1000.0
        all_points.append((lam, dist_km, em_g, routes))
        print(f'{lam:>6.2f} {dist_km:>10.2f} {em_kg:>10.2f} {len(routes):>8d}')

    front = pareto_filter(all_points)
    print(f'\nPareto-frontpunkter: {len(front)} / {len(all_points)}')

    plot_pareto(all_points, front, OUTPUT_DIR / 'gvrp_pareto.png')

    result = {
        'dist_scale_km': dist_scale,
        'em_scale_g': em_scale,
        'points': [
            {
                'lambda': round(lam, 3),
                'distance_km': round(d, 3),
                'emissions_kg': round(em / 1000.0, 3),
                'n_routes': len(r),
                'on_pareto_front': any(abs(fl - lam) < 1e-6 for fl, _, _, _ in front),
            }
            for lam, d, em, r in all_points
        ],
    }
    with open(OUTPUT_DIR / 'step06_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {OUTPUT_DIR / "step06_results.json"}')


if __name__ == '__main__':
    main()
