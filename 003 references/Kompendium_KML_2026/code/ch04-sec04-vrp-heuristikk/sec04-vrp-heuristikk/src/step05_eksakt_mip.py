"""
Steg 5: Eksakt MIP for CVRP (liten instans)
===========================================
Loser CVRP med en tre-indeks MIP med Miller-Tucker-Zemlin-eliminering
av subsykler. Anvendes kun paa liten instans (N = 15) siden antallet
binaere variabler er O(N^2 * K) og LP-relaksjonen er svak.

Formulering (kapasitert, symmetrisk med skarp capasitet per kjoeretoy K):
    min  sum_{i,j} d_{ij} * x_{ij}
    s.t. sum_j x_{ij} = 1           for i = 1..N         (ut fra hver kunde)
         sum_i x_{ij} = 1           for j = 1..N         (inn til hver kunde)
         sum_j x_{0j} <= K                                (kjoeretoeytak)
         sum_j x_{0j} - sum_i x_{i0} = 0                  (depot balanse)
         u_i - u_j + Q * x_{ij} <= Q - q_j  for i != j >=1 (MTZ + kapasitet)
         q_i <= u_i <= Q            for i = 1..N

Variablene u_i er kumulativ last etter aa ha betjent kunde i. Denne
varianten eliminerer subsykler og haandhever kapasitet i en og samme
skranke (Toth & Vigo 2002).
"""

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

from step02_narmeste_nabo import (
    DATA_DIR, OUTPUT_DIR, load_instance, plot_routes, route_load,
    route_set_distance,
)


def solve_cvrp_mip(df: pd.DataFrame, D: np.ndarray, capacity: int,
                    max_vehicles: int, time_limit: int = 300):
    n = len(df)
    demands = np.zeros(n + 1, dtype=int)
    demands[1:] = df['demand'].to_numpy(dtype=int)

    nodes = list(range(n + 1))
    customers = list(range(1, n + 1))

    prob = pulp.LpProblem('CVRP_MIP', pulp.LpMinimize)

    # x_{ij} = 1 hvis kjoeretoy gaar direkte fra i til j
    x = {
        (i, j): pulp.LpVariable(f'x_{i}_{j}', cat='Binary')
        for i in nodes for j in nodes if i != j
    }
    # u_i = kumulativ last etter aa ha besokt kunde i (MTZ)
    u = {
        i: pulp.LpVariable(f'u_{i}', lowBound=demands[i], upBound=capacity,
                           cat='Continuous')
        for i in customers
    }

    # Objektiv
    prob += pulp.lpSum(D[i, j] * x[(i, j)]
                       for i in nodes for j in nodes if i != j)

    # Hver kunde har noeyaktig en etterfoelger og en foreganger
    for j in customers:
        prob += pulp.lpSum(x[(i, j)] for i in nodes if i != j) == 1
    for i in customers:
        prob += pulp.lpSum(x[(i, j)] for j in nodes if i != j) == 1

    # Antall kjoeretoy = antall ruter ut av depot <= K, inn = ut
    prob += pulp.lpSum(x[(0, j)] for j in customers) <= max_vehicles
    prob += (pulp.lpSum(x[(0, j)] for j in customers)
             == pulp.lpSum(x[(i, 0)] for i in customers))

    # MTZ-kapasitet: u_j >= u_i + q_j - Q(1 - x_{ij})
    Q = capacity
    for i in customers:
        for j in customers:
            if i == j:
                continue
            prob += (u[i] - u[j] + Q * x[(i, j)]
                     <= Q - demands[j])

    solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit)
    t0 = time.time()
    status = prob.solve(solver)
    runtime = time.time() - t0

    if pulp.LpStatus[status] not in ('Optimal', 'Not Solved'):
        print(f'Solver-status: {pulp.LpStatus[status]}')

    # Rekonstruer ruter ut fra x_{ij}
    successor = {}
    for (i, j), var in x.items():
        if var.value() is not None and var.value() > 0.5:
            successor[i] = j

    routes = []
    # Start hver rute fra depot (0) -> f(0), men depot har flere etterfolgere
    # Derfor iterer over x[0,j] separat
    starts = [j for j in customers if x[(0, j)].value() is not None
              and x[(0, j)].value() > 0.5]
    for s in starts:
        route = [0, s]
        cur = s
        while cur != 0:
            nxt = successor.get(cur)
            if nxt is None:
                break
            route.append(nxt)
            cur = nxt
            if cur == 0:
                break
        routes.append(route)

    total = route_set_distance(routes, D)
    obj = pulp.value(prob.objective)
    return {
        'status': pulp.LpStatus[status],
        'objective': round(float(obj), 2) if obj is not None else None,
        'runtime_s': round(runtime, 2),
        'routes': routes,
        'total_distance': total,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 5: EKSAKT MIP (CVRP)')
    print('=' * 60)

    # Kjor kun paa liten instans
    tag = 'small'
    df, D, capacity = load_instance(tag)

    # Antall kjoeretoy: bruk nedre grense pluss litt slakk
    total_demand = int(df['demand'].sum())
    min_vehicles = int(np.ceil(total_demand / capacity))
    max_vehicles = min_vehicles + 2

    print(f"N = {len(df)}, Q = {capacity}, total demand = {total_demand}")
    print(f"Minimum antall kjoeretoy: {min_vehicles}, tillatt: {max_vehicles}")

    result = solve_cvrp_mip(df, D, capacity, max_vehicles, time_limit=300)

    demands = np.zeros(len(df) + 1, dtype=int)
    demands[1:] = df['demand'].to_numpy(dtype=int)

    print(f"\nStatus: {result['status']}")
    print(f"Objektiv (MIP):    {result['objective']} km")
    print(f"Total distanse:    {result['total_distance']} km")
    print(f"Antall ruter:      {len(result['routes'])}")
    print(f"Kjoeretid CBC:     {result['runtime_s']} s")
    for k, r in enumerate(result['routes']):
        print(f"  Rute {k + 1}: {r} (last = {route_load(r, demands)})")

    # Figure for liten instans
    plot_routes(
        df, result['routes'], D,
        f"MIP (optimal): {len(result['routes'])} ruter, "
        f"total {result['total_distance']:.1f} km",
        OUTPUT_DIR / 'vrp_mip_routes.png',
        capacity,
    )

    out = {
        tag: {
            'status': result['status'],
            'objective': result['objective'],
            'total_distance': result['total_distance'],
            'runtime_s': result['runtime_s'],
            'n_routes': len(result['routes']),
            'routes': [[int(c) for c in r] for r in result['routes']],
            'route_loads': [route_load(r, demands) for r in result['routes']],
        }
    }
    with open(OUTPUT_DIR / 'step05_results.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step05_results.json'}")


if __name__ == '__main__':
    main()
