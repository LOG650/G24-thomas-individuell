"""
Steg 2: Distanse-minimerende VRP-baseline (Clarke-Wright)
=========================================================
Klassisk Clarke-Wright savings-heuristikk der besparelsen er
    s_{ij} = d_{0i} + d_{0j} - d_{ij}    (km)

Denne gir baseline-loesningen der vi minimerer total kjoeredistanse og
ignorerer hvor tung bilen er underveis. Vi maaler utslippet post-hoc med
den lasteavhengige utslippsfunksjonen e(w) = alpha + beta * w, slik at vi
ser hvordan distanse-optimale ruter gjoer seg paa CO2-objektet.
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


def load_instance():
    df = pd.read_csv(DATA_DIR / 'customers.csv')
    D = np.loadtxt(DATA_DIR / 'distance.csv', delimiter=',')
    with open(OUTPUT_DIR / 'step01_summary.json', 'r', encoding='utf-8') as f:
        summary = json.load(f)
    return df, D, summary


def clarke_wright(df: pd.DataFrame, D: np.ndarray, capacity_kg: float,
                  savings_fn=None):
    """Sekvensiell Clarke-Wright savings med valgbar savings-funksjon.

    Hvis savings_fn=None, brukes den klassiske distanse-savingen
        s_{ij} = D[0,i] + D[0,j] - D[i,j].
    savings_fn(i, j, D, demands) skal returnere en skalar (hoeyere er bedre).
    """
    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    routes = {i: [0, i, 0] for i in range(1, n + 1)}
    route_of = {i: i for i in range(1, n + 1)}
    loads = {i: float(demands[i]) for i in range(1, n + 1)}

    if savings_fn is None:
        def savings_fn(i, j, D, demands):
            return D[0, i] + D[0, j] - D[i, j]

    savings = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            s = savings_fn(i, j, D, demands)
            if s > 0:
                savings.append((s, i, j))
    savings.sort(reverse=True)

    for s, i, j in savings:
        ri, rj = route_of[i], route_of[j]
        if ri == rj:
            continue
        if loads[ri] + loads[rj] > capacity_kg + 1e-6:
            continue
        route_i, route_j = routes[ri], routes[rj]
        i_is_tail = route_i[-2] == i
        i_is_head = route_i[1] == i
        j_is_tail = route_j[-2] == j
        j_is_head = route_j[1] == j

        merged = None
        if i_is_tail and j_is_head:
            merged = route_i[:-1] + route_j[1:]
        elif i_is_head and j_is_tail:
            merged = route_j[:-1] + route_i[1:]
        elif i_is_tail and j_is_tail:
            merged = route_i[:-1] + list(reversed(route_j))[1:]
        elif i_is_head and j_is_head:
            merged = list(reversed(route_i))[:-1] + route_j[1:]
        else:
            continue

        new_id = ri
        routes[new_id] = merged
        loads[new_id] = loads[ri] + loads[rj]
        del routes[rj]
        del loads[rj]
        for c in merged:
            if c != 0:
                route_of[c] = new_id

    final_routes = list(routes.values())
    return final_routes


def route_distance(route, D):
    return float(sum(D[a, b] for a, b in zip(route[:-1], route[1:])))


def route_set_distance(routes, D):
    return round(sum(route_distance(r, D) for r in routes), 3)


def route_load(route, demands):
    return float(sum(demands[c] for c in route if c != 0))


def route_emissions(route, D, demands, alpha, beta, kerb):
    """Beregn CO2-utslipp (g) for en rute med varierende last.

    Bilen forlater depotet med hele rutens last; for hver kunde som
    betjenes reduseres lasten. Paa siste leg (kunde -> depot) er bilen
    tom for gods.
    """
    total_load = sum(demands[c] for c in route if c != 0)
    current_load = total_load
    emissions_g = 0.0
    for a, b in zip(route[:-1], route[1:]):
        w = kerb + current_load
        e_per_km = alpha + beta * w
        emissions_g += e_per_km * D[a, b]
        # Lever hos b (med mindre b er depot)
        if b != 0:
            current_load -= demands[b]
    return float(emissions_g)


def route_set_emissions(routes, D, demands, alpha, beta, kerb):
    return round(sum(route_emissions(r, D, demands, alpha, beta, kerb)
                     for r in routes), 1)


def plot_routes(df, routes, D, title, output_path, demands, capacity_kg,
                alpha=None, beta=None, kerb=None, show_emissions=False):
    fig, ax = plt.subplots(figsize=(9, 7))

    sizes = 25 + 0.6 * df['demand_kg'].to_numpy()
    ax.scatter(df['x'], df['y'], s=sizes,
               c='#CBD5E1', edgecolor='#556270', linewidth=0.6, zorder=2)
    for _, row in df.iterrows():
        ax.annotate(str(int(row['customer_id'])),
                    xy=(row['x'], row['y']),
                    xytext=(4, 4), textcoords='offset points',
                    fontsize=7, color='#1F2933', zorder=4)
    ax.scatter(0, 0, s=240, marker='s', c='#F6BA7C',
               edgecolor='#9C540B', linewidth=1.2, zorder=5, label='Depot')

    coords = np.zeros((len(df) + 1, 2))
    coords[1:, 0] = df['x'].to_numpy()
    coords[1:, 1] = df['y'].to_numpy()

    for k, route in enumerate(routes):
        xs = [coords[c, 0] for c in route]
        ys = [coords[c, 1] for c in route]
        load = route_load(route, demands)
        color = PALETTE[k % len(PALETTE)]
        label = f'Rute {k + 1} ($q = {int(load)}/{int(capacity_kg)}$ kg'
        if show_emissions and alpha is not None:
            em = route_emissions(route, D, demands, alpha, beta, kerb) / 1000.0
            label += f', {em:.1f} kg CO$_2$)'
        else:
            label += ')'
        ax.plot(xs, ys, '-', color=color, linewidth=1.8, zorder=3,
                label=label)

    ax.set_xlabel('$x$ (km)', fontsize=12)
    ax.set_ylabel('$y$ (km)', fontsize=12)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.set_aspect('equal', adjustable='datalim')
    ax.legend(loc='upper right', fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 2: DISTANSE-BASELINE (CLARKE-WRIGHT)')
    print('=' * 60)

    df, D, summary = load_instance()
    capacity = summary['vehicle_capacity_kg']
    alpha = summary['emission_alpha_g_per_km']
    beta = summary['emission_beta_g_per_kgkm']
    kerb = summary['kerb_weight_kg']

    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    routes = clarke_wright(df, D, capacity)
    total_dist = route_set_distance(routes, D)
    total_em_g = route_set_emissions(routes, D, demands, alpha, beta, kerb)
    total_em_kg = round(total_em_g / 1000.0, 2)

    print(f'\nAntall ruter: {len(routes)}')
    print(f'Total distanse: {total_dist:.2f} km')
    print(f'Total CO2:      {total_em_kg:.2f} kg')
    for k, r in enumerate(routes):
        load = route_load(r, demands)
        dist = route_distance(r, D)
        em = route_emissions(r, D, demands, alpha, beta, kerb) / 1000.0
        print(f'  Rute {k + 1}: last = {load:.0f} kg, {dist:.2f} km, {em:.2f} kg CO2')

    plot_routes(df, routes, D,
                f'Distanse-optimal (Clarke-Wright): {len(routes)} ruter, '
                f'{total_dist:.1f} km / {total_em_kg:.1f} kg CO$_2$',
                OUTPUT_DIR / 'gvrp_distance_routes.png',
                demands, capacity, alpha, beta, kerb, show_emissions=True)

    result = {
        'n_routes': len(routes),
        'total_distance_km': total_dist,
        'total_emissions_kg': total_em_kg,
        'routes': [[int(c) for c in r] for r in routes],
        'route_loads_kg': [float(route_load(r, demands)) for r in routes],
        'route_distances_km': [round(route_distance(r, D), 3) for r in routes],
        'route_emissions_g': [round(route_emissions(r, D, demands, alpha, beta, kerb), 1)
                              for r in routes],
    }
    with open(OUTPUT_DIR / 'step02_results.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {OUTPUT_DIR / "step02_results.json"}')


if __name__ == '__main__':
    main()
