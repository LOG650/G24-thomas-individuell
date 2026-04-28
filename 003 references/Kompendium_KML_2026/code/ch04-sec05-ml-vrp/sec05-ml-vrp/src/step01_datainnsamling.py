"""
Steg 1: Datainnsamling for ML-VRP
=================================

Genererer et treningssett av sm[ CVRP-instanser (5--8 kunder) og l\xf8ser hver
instans eksakt med en enkel branch-and-bound / brute-force tilpasset den lille
st\xf8rrelsen. For hvert instans lagres kundekoordinater, etterspoersel,
kapasitet og den optimale ruten (som en ordnet sekvens av kunder inkludert
retur til depot mellom ruter).

Datasettet er det som supervised attention-modellen skal l\xe6re \xe5
rekonstruere: gitt (koordinater, etterspoersel, kapasitet) -> en sekvens av
besoek som minimerer total distanse under kapasitetsbegrensning.

Output:
  data/mlvrp_training_instances.pkl  -- 1000 treningsinstanser med optimal rute
  data/mlvrp_eval_instances.pkl      -- 200 valideringsinstanser
  output/mlvrp_instance.png          -- illustrasjon av en enkelt instans + rute
  output/step01_results.json         -- oppsummering
"""

from __future__ import annotations

import json
import pickle
import time
from dataclasses import dataclass, asdict
from itertools import permutations
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

# ---------------------------------------------------------------
# Konfigurasjon
# ---------------------------------------------------------------
SEED = 20260420
N_TRAIN = 1200
N_EVAL = 200
N_CUSTOMERS_MIN = 5
N_CUSTOMERS_MAX = 7
CAPACITY = 30
DEMAND_MIN = 1
DEMAND_MAX = 9

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
DATA_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


# ---------------------------------------------------------------
# Dataklasser
# ---------------------------------------------------------------
@dataclass
class VRPInstance:
    coords: np.ndarray        # (n+1, 2), index 0 er depot
    demand: np.ndarray        # (n+1,), demand[0] = 0
    capacity: int
    n_customers: int


@dataclass
class VRPSolution:
    tour: list                # liste av kundeindekser (1..n), 0 = retur til depot
    distance: float
    routes: list              # liste av lister (en per rute, inneholder kunder)


# ---------------------------------------------------------------
# Instansgenerator
# ---------------------------------------------------------------
def generate_instance(rng: np.random.Generator, n_customers: int,
                      capacity: int = CAPACITY) -> VRPInstance:
    """Lag en tilfeldig CVRP-instans p\xe5 et [0,1]^2-kvadrat."""
    coords = rng.uniform(0, 1, size=(n_customers + 1, 2))
    coords[0] = [0.5, 0.5]  # depot i senter
    demand = rng.integers(DEMAND_MIN, DEMAND_MAX + 1, size=n_customers + 1)
    demand[0] = 0
    return VRPInstance(coords=coords, demand=demand, capacity=capacity,
                       n_customers=n_customers)


# ---------------------------------------------------------------
# Eksakt loeser ved brute-force permutasjon + split-beslutning
# ---------------------------------------------------------------
def _distance_matrix(coords: np.ndarray) -> np.ndarray:
    diff = coords[:, None, :] - coords[None, :, :]
    return np.sqrt((diff ** 2).sum(axis=-1))


def _best_split(perm: tuple, demand: np.ndarray, capacity: int,
                dist: np.ndarray) -> tuple[float, list]:
    """Gitt en permutasjon av kundene, finn beste splittet inn i kapasiteterte
    ruter via DP paa kundesekvensen (Beasley 1983 'optimal split').
    """
    n = len(perm)
    INF = float("inf")
    f = [0.0] + [INF] * n
    split = [0] * (n + 1)

    # Preberegn demand og interne kantedistanser langs perm
    perm_arr = perm  # tuple for rask index
    dem = [demand[k] for k in perm_arr]
    # intern[k] = dist(perm[k], perm[k+1])   for k=0..n-2
    intern = [dist[perm_arr[k], perm_arr[k + 1]] for k in range(n - 1)]
    # dist_to_depot[k] = dist(0, perm[k])
    d0 = [dist[0, perm_arr[k]] for k in range(n)]

    for j in range(1, n + 1):
        load = 0
        # d_inner = sum(intern[i-1..j-2])
        d_inner = 0.0
        for i in range(j, 0, -1):
            idx = i - 1
            load += dem[idx]
            if load > capacity:
                break
            if i < j:
                d_inner += intern[idx]  # intern[i-1] = dist(perm[i-1], perm[i])
            # Rute distanse = d0[i-1] + d_inner + d0[j-1]
            route_d = d0[idx] + d_inner + d0[j - 1]
            total = f[i - 1] + route_d
            if total < f[j]:
                f[j] = total
                split[j] = i - 1

    # Rekonstruer rutene
    routes = []
    j = n
    while j > 0:
        i = split[j]
        routes.append([perm_arr[x] for x in range(i, j)])
        j = i
    routes.reverse()
    return f[n], routes


def solve_exact(instance: VRPInstance) -> VRPSolution:
    """L\xf8s instans ved \xe5 proeve alle permutasjoner av kundene.

    For hver permutasjon, beregnes optimal split (se _best_split). Total
    kompleksitet er O(n! * n^2) som er overkommelig for n <= 8.
    """
    n = instance.n_customers
    dist = _distance_matrix(instance.coords)
    best_dist = float("inf")
    best_routes: list = []

    customers = tuple(range(1, n + 1))
    for perm in permutations(customers):
        d, routes = _best_split(perm, instance.demand, instance.capacity, dist)
        if d < best_dist:
            best_dist = d
            best_routes = routes

    # Lag tour som sekvens: f.eks. [c1, c2, 0, c3, c4, c5, 0, ...]
    tour = []
    for route in best_routes:
        tour.extend(route)
        tour.append(0)  # retur til depot
    # Fjern trailing 0 dersom du vil; vi beholder det som separator.

    return VRPSolution(tour=tour, distance=best_dist, routes=best_routes)


# ---------------------------------------------------------------
# Plot en enkelt instans
# ---------------------------------------------------------------
def plot_instance(instance: VRPInstance, solution: VRPSolution,
                  output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(6.5, 6.0))
    coords = instance.coords
    palette = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]

    # Ruter
    for r_idx, route in enumerate(solution.routes):
        nodes = [0] + list(route) + [0]
        xs = coords[nodes, 0]
        ys = coords[nodes, 1]
        ax.plot(xs, ys, "-o", color=palette[r_idx % len(palette)],
                linewidth=1.6, markersize=6,
                label=f"Rute {r_idx+1} (last {sum(instance.demand[k] for k in route)})")

    # Depot
    ax.scatter([coords[0, 0]], [coords[0, 1]], marker="s", s=120,
               color="#1F2933", zorder=5, label="Depot")

    # Kundetall
    for i in range(1, instance.n_customers + 1):
        ax.annotate(f"{i} ({instance.demand[i]})",
                    (coords[i, 0], coords[i, 1]),
                    xytext=(6, 6), textcoords="offset points",
                    fontsize=9, color="#1F2933")

    ax.set_xlabel("$x$", fontsize=12)
    ax.set_ylabel("$y$", fontsize=12, rotation=0, labelpad=12)
    ax.set_xlim(-0.05, 1.05)
    ax.set_ylim(-0.05, 1.05)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.set_title(
        f"Eksempel: CVRP-instans med {instance.n_customers} kunder "
        f"(kapasitet {instance.capacity}, total distanse {solution.distance:.2f})",
        fontsize=11, fontweight="bold")
    ax.legend(fontsize=9, loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING FOR ML-VRP")
    print("=" * 60)

    rng = np.random.default_rng(SEED)

    print(f"Genererer {N_TRAIN} treningsinstanser "
          f"({N_CUSTOMERS_MIN}-{N_CUSTOMERS_MAX} kunder hver)...")
    t0 = time.time()
    train = []
    for i in range(N_TRAIN):
        n = int(rng.integers(N_CUSTOMERS_MIN, N_CUSTOMERS_MAX + 1))
        inst = generate_instance(rng, n)
        sol = solve_exact(inst)
        train.append((inst, sol))
        if (i + 1) % 100 == 0:
            elapsed = time.time() - t0
            print(f"  {i+1}/{N_TRAIN}   ({elapsed:.1f} s)")
    t_train = time.time() - t0
    print(f"Trening generert paa {t_train:.1f} s")

    print(f"Genererer {N_EVAL} valideringsinstanser...")
    t0 = time.time()
    val = []
    for i in range(N_EVAL):
        n = int(rng.integers(N_CUSTOMERS_MIN, N_CUSTOMERS_MAX + 1))
        inst = generate_instance(rng, n)
        sol = solve_exact(inst)
        val.append((inst, sol))
    t_val = time.time() - t0
    print(f"Validering generert paa {t_val:.1f} s")

    # Lagre
    train_path = DATA_DIR / "mlvrp_training_instances.pkl"
    with open(train_path, "wb") as f:
        pickle.dump(train, f)
    val_path = DATA_DIR / "mlvrp_eval_instances.pkl"
    with open(val_path, "wb") as f:
        pickle.dump(val, f)
    print(f"Treningsdata lagret: {train_path}")
    print(f"Valideringsdata lagret: {val_path}")

    # Illustrer en instans
    idx = 0
    inst, sol = train[idx]
    plot_instance(inst, sol, OUTPUT_DIR / "mlvrp_instance.png")

    # Oppsummering
    results = {
        "n_train": N_TRAIN,
        "n_eval": N_EVAL,
        "n_customers_min": N_CUSTOMERS_MIN,
        "n_customers_max": N_CUSTOMERS_MAX,
        "capacity": CAPACITY,
        "demand_min": DEMAND_MIN,
        "demand_max": DEMAND_MAX,
        "train_gen_time_s": round(t_train, 2),
        "eval_gen_time_s": round(t_val, 2),
        "avg_customers_train": float(np.mean([t[0].n_customers for t in train])),
        "avg_routes_train": float(np.mean([len(t[1].routes) for t in train])),
        "avg_optimal_distance": float(np.mean([t[1].distance for t in train])),
    }
    with open(OUTPUT_DIR / "step01_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nOppsummering:")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
