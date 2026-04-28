"""
Steg 6: Sammenligning av ML-modellen, Clarke-Wright og eksakt solver
=====================================================================

Vi genererer tre instansstoerelser -- sm  (n=6), middels (n=10) og stor
(n=20) -- og evaluerer tre loesningsmetoder:

  1) Eksakt MIP / branch-and-bound via permutasjonsenumerering (kun for n<=8).
  2) Clarke-Wright savings-heuristikk (inkl. 2-opt forbedring).
  3) Den trente ML-pointermodellen med greedy decoding.

For hver instansgruppe registreres gjennomsnittlig distanse, gap til
Clarke-Wright (referansen), gjennomsnittstid og beste oppnaadde ruter.

Output:
  output/mlvrp_comparison.json
  output/mlvrp_gap_runtime.png
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

from step01_datainnsamling import generate_instance, solve_exact, VRPInstance
from step02_feature_engineering import build_features
from step03_modell_arkitektur import PointerVRP, build_mask
from step05_evaluering import greedy_decode

OUTPUT_DIR = Path(__file__).parent.parent / "output"


# ---------------------------------------------------------------
# Clarke-Wright savings-heuristikk
# ---------------------------------------------------------------
def clarke_wright(instance: VRPInstance) -> tuple[list, float, float]:
    """Klassisk Clarke-Wright savings. Returnerer (routes, distanse, tid)."""
    t0 = time.perf_counter()
    n = instance.n_customers
    coords = instance.coords
    demand = instance.demand
    cap = instance.capacity

    def dist(a, b):
        dx = coords[a, 0] - coords[b, 0]
        dy = coords[a, 1] - coords[b, 1]
        return float(np.sqrt(dx * dx + dy * dy))

    # Savings for alle kundepar (i,j)
    pairs = []
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            s = dist(0, i) + dist(0, j) - dist(i, j)
            pairs.append((s, i, j))
    pairs.sort(reverse=True)

    # Initialisering: hver kunde har sin egen rute depot-i-depot
    route_of = {i: [i] for i in range(1, n + 1)}
    load_of = {i: demand[i] for i in range(1, n + 1)}

    # Parent-peker per kunde
    belongs_to = {i: i for i in range(1, n + 1)}

    for s, i, j in pairs:
        if s <= 0:
            break
        ri = belongs_to[i]
        rj = belongs_to[j]
        if ri == rj:
            continue
        ra = route_of[ri]
        rb = route_of[rj]
        if load_of[ri] + load_of[rj] > cap:
            continue
        # i maa vaere endre paa ra og j endre paa rb
        if ra[0] == i:
            ra = ra[::-1]
        if rb[-1] == j:
            rb = rb[::-1]
        if ra[-1] != i or rb[0] != j:
            continue
        merged = ra + rb
        merged_load = load_of[ri] + load_of[rj]
        new_key = min(ri, rj)
        # Oppdater
        route_of[new_key] = merged
        load_of[new_key] = merged_load
        for node in merged:
            belongs_to[node] = new_key
        old_key = max(ri, rj)
        if old_key != new_key:
            route_of.pop(old_key, None)
            load_of.pop(old_key, None)

    routes = list(route_of.values())

    # 2-opt forbedring per rute
    def route_distance(route):
        if not route:
            return 0.0
        d = dist(0, route[0])
        for k in range(len(route) - 1):
            d += dist(route[k], route[k + 1])
        d += dist(route[-1], 0)
        return d

    def two_opt(route):
        improved = True
        best = route[:]
        best_d = route_distance(best)
        while improved:
            improved = False
            for i_ in range(len(best) - 1):
                for j_ in range(i_ + 1, len(best)):
                    new_route = best[:i_] + best[i_:j_ + 1][::-1] + best[j_ + 1:]
                    new_d = route_distance(new_route)
                    if new_d + 1e-9 < best_d:
                        best = new_route
                        best_d = new_d
                        improved = True
        return best, best_d

    total = 0.0
    opt_routes = []
    for route in routes:
        r2, d2 = two_opt(route)
        opt_routes.append(r2)
        total += d2

    t = time.perf_counter() - t0
    return opt_routes, total, t


# ---------------------------------------------------------------
# ML-evaluering paa spesifikk instans
# ---------------------------------------------------------------
def ml_solve(model: PointerVRP, instance: VRPInstance,
             n_max: int) -> tuple[list, float, float]:
    """ML-loesning for en instans, med pointer-modellen.

    Paddet X og coords saa det matcher n_max kjent under trening. Noder
    over n_customers er skjulte via demand-masken fordi de har demand=0
    men we explicitly mask dem i build_mask-krav.
    """
    X = np.zeros((n_max + 1, 4), dtype=np.float32)
    Xf = build_features(instance)
    n = instance.n_customers
    X[:n + 1] = Xf
    coords = np.zeros((n_max + 1, 2), dtype=np.float32)
    coords[:n + 1] = instance.coords
    demand = np.zeros(n_max + 1, dtype=np.int64)
    demand[:n + 1] = instance.demand
    inst_dict = {
        "X": X, "coords": coords, "demand": demand,
        "capacity": int(instance.capacity), "n": n,
    }

    # Vi lager en modifisert greedy som tar hensyn til at noder > n er
    # padding og aldri skal velges.
    device = next(model.parameters()).device
    Xt = torch.from_numpy(X).unsqueeze(0).to(device)
    coordst = torch.from_numpy(coords).unsqueeze(0).to(device)
    demandt = torch.from_numpy(demand).unsqueeze(0).to(device)
    Ntot = Xt.shape[1]
    capacity = float(instance.capacity)
    demand_norm = demandt.float() / capacity
    pad_mask = torch.zeros(1, Ntot, dtype=torch.bool, device=device)
    pad_mask[0, :n + 1] = True

    t0 = time.perf_counter()
    with torch.no_grad():
        H = model.encode(Xt)
        visited = torch.zeros(1, Ntot, dtype=torch.bool, device=device)
        last_idx = torch.zeros(1, dtype=torch.long, device=device)
        remaining_cap = torch.ones(1, 1, device=device)
        last_was_depot = torch.ones(1, dtype=torch.bool, device=device)

        tour = []
        for _ in range(4 * n + 5):
            mask = build_mask(visited, demand_norm, remaining_cap, last_was_depot)
            mask = mask & pad_mask
            if mask.sum() == 0:
                break
            logp = model.step_logp(H, last_idx, remaining_cap, mask)
            action = int(torch.argmax(logp, dim=-1).item())
            tour.append(action)
            is_depot = (action == 0)
            if not is_depot:
                visited[0, action] = True
                remaining_cap = remaining_cap - demand_norm[0, action].view(1, 1)
            else:
                remaining_cap = torch.ones(1, 1, device=device)
            last_idx[0] = action
            last_was_depot[0] = is_depot
            if visited[0, 1:n + 1].all() and is_depot:
                break
    if not tour or tour[-1] != 0:
        tour.append(0)
    t = time.perf_counter() - t0

    # Rute-distanse
    path = [0] + tour
    d = 0.0
    for a, b in zip(path[:-1], path[1:]):
        dx = coords[a, 0] - coords[b, 0]
        dy = coords[a, 1] - coords[b, 1]
        d += float(np.sqrt(dx * dx + dy * dy))
    # Splitt i ruter til visning
    routes = []
    cur = []
    for node in path[1:]:
        if node == 0:
            if cur:
                routes.append(cur)
                cur = []
        else:
            cur.append(node)
    if cur:
        routes.append(cur)
    return routes, d, t


# ---------------------------------------------------------------
# Eksakt for n<=8 gjenbrukt fra step01
# ---------------------------------------------------------------
def exact_solve(instance: VRPInstance) -> tuple[list, float, float]:
    t0 = time.perf_counter()
    sol = solve_exact(instance)
    t = time.perf_counter() - t0
    return sol.routes, sol.distance, t


# ---------------------------------------------------------------
# Main: tre sett
# ---------------------------------------------------------------
def main():
    print("\n" + "=" * 60)
    print("STEG 6: SAMMENLIGNING ML / CW / EKSAKT")
    print("=" * 60)

    ckpt = torch.load(OUTPUT_DIR / "mlvrp_model.pt", map_location="cpu",
                       weights_only=False)
    model = PointerVRP(d_in=4, d_model=ckpt["d_model"])
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    n_max_train = int(ckpt["n_max"])

    rng = np.random.default_rng(31415)
    sets = [
        ("smaa", 6, 30, True),     # eksakt mulig
        ("middels", 10, 30, False),  # eksakt ikke mulig (brute-force)
        ("store", 20, 30, False),
    ]
    N_PER_SET = 30

    summary = {}
    for name, n_cust, capacity, do_exact in sets:
        rows = []
        for i in range(N_PER_SET):
            inst = generate_instance(rng, n_cust, capacity=capacity)
            row = {"i": i, "n": n_cust}
            # Clarke-Wright
            _, d_cw, t_cw = clarke_wright(inst)
            row["d_cw"] = d_cw
            row["t_cw"] = t_cw
            # ML
            # Hvis n > n_max_train er instansen utenfor fordelingen; bruk
            # storste padded-stoerelse, men noder > n vil bli skjult av
            # pad_mask. Dette illustrerer generaliseringsevne.
            n_max_used = max(n_cust, n_max_train)
            _, d_ml, t_ml = ml_solve(model, inst, n_max=n_max_used)
            row["d_ml"] = d_ml
            row["t_ml"] = t_ml
            # Eksakt
            if do_exact:
                _, d_opt, t_opt = exact_solve(inst)
                row["d_opt"] = d_opt
                row["t_opt"] = t_opt
            rows.append(row)
        # Aggregatoer
        d_cw_mean = float(np.mean([r["d_cw"] for r in rows]))
        d_ml_mean = float(np.mean([r["d_ml"] for r in rows]))
        t_cw_mean = float(np.mean([r["t_cw"] for r in rows]))
        t_ml_mean = float(np.mean([r["t_ml"] for r in rows]))
        block = {
            "n_customers": n_cust,
            "n_instances": N_PER_SET,
            "mean_distance_cw": d_cw_mean,
            "mean_distance_ml": d_ml_mean,
            "mean_time_cw_ms": t_cw_mean * 1000,
            "mean_time_ml_ms": t_ml_mean * 1000,
            "gap_ml_vs_cw_percent":
                100.0 * (d_ml_mean - d_cw_mean) / d_cw_mean,
        }
        if do_exact:
            d_opt_mean = float(np.mean([r["d_opt"] for r in rows]))
            t_opt_mean = float(np.mean([r["t_opt"] for r in rows]))
            block["mean_distance_opt"] = d_opt_mean
            block["mean_time_opt_ms"] = t_opt_mean * 1000
            block["gap_cw_vs_opt_percent"] = \
                100.0 * (d_cw_mean - d_opt_mean) / d_opt_mean
            block["gap_ml_vs_opt_percent"] = \
                100.0 * (d_ml_mean - d_opt_mean) / d_opt_mean
        summary[name] = block
        print(f"\n[{name}] n={n_cust}:")
        for k, v in block.items():
            print(f"  {k}: {v}")

    with open(OUTPUT_DIR / "mlvrp_comparison.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Figur: gap og tid
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12.5, 5.0))
    labels = ["n=6 (smaa)", "n=10 (middels)", "n=20 (store)"]
    x = np.arange(len(labels))
    width = 0.35

    # Gap-panelet: bruk gap_ml_vs_cw_percent; legg i tilleggsdata hvis
    # eksakt finnes.
    gaps_ml_vs_cw = [summary["smaa"]["gap_ml_vs_cw_percent"],
                     summary["middels"]["gap_ml_vs_cw_percent"],
                     summary["store"]["gap_ml_vs_cw_percent"]]
    gaps_ml_vs_opt = [summary["smaa"].get("gap_ml_vs_opt_percent", np.nan),
                      np.nan, np.nan]
    gaps_cw_vs_opt = [summary["smaa"].get("gap_cw_vs_opt_percent", np.nan),
                      np.nan, np.nan]
    ax1.bar(x - width / 2, gaps_cw_vs_opt, width,
            color="#F6BA7C", edgecolor="#9C540B",
            label="Clarke-Wright vs optimum")
    ax1.bar(x + width / 2, gaps_ml_vs_opt, width,
            color="#8CC8E5", edgecolor="#1F6587",
            label="ML vs optimum")
    # Legg til en sekundaer barre for middels/store: ML vs CW
    for xi, g in zip(x[1:], gaps_ml_vs_cw[1:]):
        ax1.bar(xi, g, width * 0.7, color="#BD94D7", edgecolor="#5A2C77",
                label="ML vs Clarke-Wright" if xi == x[1] else None,
                alpha=0.85)
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Gap (%)", fontsize=11)
    ax1.set_title("Loesningskvalitet: gap mot referanse", fontsize=11,
                  fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")
    ax1.legend(fontsize=9, loc="upper left")

    # Tid
    times_cw = [summary[s]["mean_time_cw_ms"] for s in ("smaa", "middels", "store")]
    times_ml = [summary[s]["mean_time_ml_ms"] for s in ("smaa", "middels", "store")]
    times_opt = [summary["smaa"].get("mean_time_opt_ms", np.nan), np.nan, np.nan]
    ax2.bar(x - width, times_opt, width, color="#ED9F9E", edgecolor="#961D1C",
            label="Eksakt (brute-force)")
    ax2.bar(x, times_cw, width, color="#F6BA7C", edgecolor="#9C540B",
            label="Clarke-Wright")
    ax2.bar(x + width, times_ml, width, color="#8CC8E5", edgecolor="#1F6587",
            label="ML (pointer)")
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels)
    ax2.set_ylabel("Gjennomsnittlig tid per instans (ms)", fontsize=11)
    ax2.set_yscale("log")
    ax2.set_title("Beregningstid", fontsize=11, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y", which="both")
    ax2.legend(fontsize=9, loc="upper left")

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mlvrp_gap_runtime.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"\nFigur lagret: {OUTPUT_DIR / 'mlvrp_gap_runtime.png'}")


if __name__ == "__main__":
    main()
