"""
Steg 5: Evaluering av trent pointer-modell paa valideringsinstanser
====================================================================

Vi bruker greedy decoding (i hvert steg velges noden med hoeyeste
sannsynlighet som tilfredsstiller kapasitetsmasken) og maaler:

  - Total distanse for modellens konstruerte rute
  - Gap til eksakt optimum: (d_ml - d_opt) / d_opt
  - Inference-tid per instans

Output:
  output/mlvrp_eval_results.json
  output/mlvrp_routes_ml.png          -- visualisering av 4 valideringsinstanser
  output/mlvrp_gap_histogram.png      -- fordeling av gap paa tvers av valideringssettet
"""

from __future__ import annotations

import json
import pickle
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch

from step01_datainnsamling import VRPInstance, VRPSolution  # noqa: F401
from step03_modell_arkitektur import PointerVRP, build_mask

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def greedy_decode(model: PointerVRP, inst_dict) -> tuple[list, float, float]:
    """Greedy inference for en enkelt instans.

    Returnerer (tour, distance, time_seconds).
    """
    device = next(model.parameters()).device
    X = torch.from_numpy(inst_dict["X"]).unsqueeze(0).to(device)      # (1, N, 4)
    coords = torch.from_numpy(inst_dict["coords"]).unsqueeze(0).to(device)  # (1, N, 2)
    demand = torch.from_numpy(inst_dict["demand"]).unsqueeze(0).to(device)  # (1, N)
    N = X.shape[1]
    capacity = float(inst_dict["capacity"])
    demand_norm = demand.float() / capacity

    t0 = time.perf_counter()
    H = model.encode(X)                       # (1, N, d)
    visited = torch.zeros(1, N, dtype=torch.bool, device=device)
    last_idx = torch.zeros(1, dtype=torch.long, device=device)
    remaining_cap = torch.ones(1, 1, device=device)
    last_was_depot = torch.ones(1, dtype=torch.bool, device=device)

    tour = []
    max_steps = 2 * N
    for _ in range(max_steps):
        mask = build_mask(visited, demand_norm, remaining_cap, last_was_depot)
        if mask.sum() == 0:
            break
        logp = model.step_logp(H, last_idx, remaining_cap, mask)  # (1, N)
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
        # Avslutt naar alle kunder er besoekt og sist vi gikk var til depot
        if visited[0, 1:].all() and is_depot:
            break

    # Sorg for at tour slutter paa depot
    if len(tour) == 0 or tour[-1] != 0:
        tour.append(0)

    t_inf = time.perf_counter() - t0

    # Beregn total distanse
    coords_np = inst_dict["coords"]
    path = [0] + tour
    d = 0.0
    for a, b in zip(path[:-1], path[1:]):
        dx = coords_np[a, 0] - coords_np[b, 0]
        dy = coords_np[a, 1] - coords_np[b, 1]
        d += float(np.sqrt(dx * dx + dy * dy))
    return tour, d, t_inf


def plot_routes(samples, output_path: Path) -> None:
    """Plot fire instanser side om side med ML-ruten tegnet inn."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    palette = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]
    for ax, sample in zip(axes.flat, samples):
        coords = sample["coords_np"]
        tour = sample["tour_ml"]
        n = sample["n"]
        path = [0] + tour
        # Splitt i delruter
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
        for r_idx, route in enumerate(routes):
            nodes = [0] + route + [0]
            xs = coords[nodes, 0]
            ys = coords[nodes, 1]
            ax.plot(xs, ys, "-o",
                    color=palette[r_idx % len(palette)],
                    linewidth=1.6, markersize=6,
                    label=f"Rute {r_idx+1}")
        ax.scatter([coords[0, 0]], [coords[0, 1]],
                   marker="s", s=130, color="#1F2933", zorder=5)
        for i in range(1, n + 1):
            ax.annotate(str(i), (coords[i, 0], coords[i, 1]),
                        xytext=(5, 5), textcoords="offset points",
                        fontsize=8, color="#1F2933")
        ax.set_aspect("equal")
        ax.set_xlim(-0.05, 1.05)
        ax.set_ylim(-0.05, 1.05)
        ax.grid(True, alpha=0.3)
        ax.set_title(
            f"n={n}, ML-distanse {sample['dist_ml']:.2f}, "
            f"optimum {sample['dist_opt']:.2f}, gap "
            f"{100*(sample['dist_ml']/sample['dist_opt']-1):+.1f}%",
            fontsize=10)
        ax.legend(fontsize=8, loc="upper left")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def plot_gap_histogram(gaps: np.ndarray, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(8.2, 4.8))
    ax.hist(gaps * 100, bins=30, color="#8CC8E5", edgecolor="#1F6587", alpha=0.85)
    mean_gap = float(np.mean(gaps)) * 100
    med_gap = float(np.median(gaps)) * 100
    ax.axvline(mean_gap, color="#9C540B", linestyle="--", linewidth=1.6,
               label=f"Gjennomsnitt {mean_gap:.2f}%")
    ax.axvline(med_gap, color="#307453", linestyle=":", linewidth=1.6,
               label=f"Median {med_gap:.2f}%")
    ax.set_xlabel("Gap til eksakt optimum (%)", fontsize=12)
    ax.set_ylabel("Antall instanser", fontsize=12)
    ax.set_title(
        "Fordeling av optimum-gap paa valideringssettet (greedy decoding)",
        fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()


def main():
    print("\n" + "=" * 60)
    print("STEG 5: EVALUERING AV TRENT MODELL")
    print("=" * 60)

    with open(DATA_DIR / "mlvrp_eval_tensors.pkl", "rb") as f:
        val = pickle.load(f)

    ckpt = torch.load(OUTPUT_DIR / "mlvrp_model.pt", map_location="cpu",
                       weights_only=False)
    model = PointerVRP(d_in=4, d_model=ckpt["d_model"])
    model.load_state_dict(ckpt["model_state"])
    model.eval()

    gaps = []
    times_ml = []
    per_instance = []
    samples = []
    with torch.no_grad():
        for idx, inst in enumerate(val):
            tour, d_ml, t_inf = greedy_decode(model, inst)
            d_opt = inst["distance"]
            gap = (d_ml - d_opt) / d_opt
            gaps.append(gap)
            times_ml.append(t_inf)
            per_instance.append({
                "idx": idx, "n": inst["n"],
                "d_ml": d_ml, "d_opt": d_opt, "gap": gap,
                "t_ml_ms": t_inf * 1000,
            })
            if idx < 4:
                samples.append({
                    "coords_np": inst["coords"],
                    "tour_ml": tour,
                    "dist_ml": d_ml,
                    "dist_opt": d_opt,
                    "n": inst["n"],
                })

    gaps = np.array(gaps)
    times_ml = np.array(times_ml)
    results = {
        "n_instances": len(val),
        "mean_gap_percent": float(np.mean(gaps) * 100),
        "median_gap_percent": float(np.median(gaps) * 100),
        "p90_gap_percent": float(np.quantile(gaps, 0.9) * 100),
        "max_gap_percent": float(np.max(gaps) * 100),
        "share_optimal": float((gaps < 1e-6).mean()),
        "share_within_5pct": float((gaps < 0.05).mean()),
        "mean_inference_time_ms": float(np.mean(times_ml) * 1000),
        "median_inference_time_ms": float(np.median(times_ml) * 1000),
    }
    with open(OUTPUT_DIR / "mlvrp_eval_results.json", "w", encoding="utf-8") as f:
        json.dump({"summary": results, "per_instance": per_instance},
                  f, indent=2, ensure_ascii=False)

    plot_routes(samples, OUTPUT_DIR / "mlvrp_routes_ml.png")
    plot_gap_histogram(gaps, OUTPUT_DIR / "mlvrp_gap_histogram.png")

    print("\nOppsummering:")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
