"""
Steg 4: Ruteplanlegging med largest-gap
=======================================
For hver batch samler vi alle plukkene pa tvers av ordrene, grupperer
dem per gang, og beregner rutelengden via largest-gap-heuristikken.
Vi sammenligner med:
  - S-shape: traverser hver besokt gang fullt
  - Tilfeldig gangrekkefolge + S-shape

Output:
  - JSON med rutelengder per batch for alle strategier
  - Figur 'intlag_route_compare.png' som viser et representativt
    eksempel for alle tre rutetyper i samme batch.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from common import (
    PALETTE_FILL,
    PALETTE_STROKE,
    largest_gap_route_length,
    random_route_length,
    s_shape_route_length,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def load_all():
    with open(OUTPUT_DIR / "step01_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(OUTPUT_DIR / "step02_waves.json", "r", encoding="utf-8") as f:
        waves = json.load(f)
    with open(OUTPUT_DIR / "step03_batches.json", "r", encoding="utf-8") as f:
        batches = json.load(f)
    return data, waves, batches


def picks_by_aisle_for_batch(batch_order_ids: list[int], orders: list[dict],
                              layout: dict) -> dict[int, list[float]]:
    orders_by_id = {o["order_id"]: o for o in orders}
    locs_by_id = {loc["id"]: loc for loc in layout["locations"]}
    picks: dict[int, list[float]] = {}
    for oid in batch_order_ids:
        for lid in orders_by_id[oid]["line_location_ids"]:
            loc = locs_by_id[lid]
            picks.setdefault(loc["aisle"], []).append(loc["y"])
    for a in picks:
        picks[a] = sorted(picks[a])
    return picks


def route_all_batches(wave_batches: dict[str, list[list[int]]],
                      orders: list[dict], layout: dict,
                      rng: np.random.Generator) -> dict:
    """Kjor rutene for alle batcher med alle tre strategier."""
    results = {
        "largest_gap": {"lengths": []},
        "s_shape": {"lengths": []},
        "random": {"lengths": []},
    }
    for wid, batches in wave_batches.items():
        for batch in batches:
            picks = picks_by_aisle_for_batch(batch, orders, layout)
            lg_len, _ = largest_gap_route_length(picks, layout)
            ss_len, _ = s_shape_route_length(picks, layout)
            rd_len, _ = random_route_length(picks, layout, rng)
            results["largest_gap"]["lengths"].append(lg_len)
            results["s_shape"]["lengths"].append(ss_len)
            results["random"]["lengths"].append(rd_len)
    for k in results:
        lens = np.array(results[k]["lengths"])
        results[k]["total_m"] = float(lens.sum())
        results[k]["mean_m"] = float(lens.mean()) if lens.size else 0.0
    return results


def plot_route_compare(example_picks: dict[int, list[float]], layout: dict,
                        output_path: Path) -> None:
    """Vis et eksempel-batch med rute under 3 strategier."""
    rng = np.random.default_rng(7)
    fig, axes = plt.subplots(1, 3, figsize=(13, 5), sharey=True)
    strategies = [
        ("Largest-gap", largest_gap_route_length, PALETTE_STROKE[0]),
        ("S-shape", s_shape_route_length, PALETTE_STROKE[1]),
        ("Tilfeldig", lambda p, l: random_route_length(p, l, rng), PALETTE_STROKE[2]),
    ]
    for ax, (name, fn, col) in zip(axes, strategies):
        length, pts = fn(example_picks, layout)
        # Tegn ganger
        n_aisles = layout["n_aisles"]
        sp = layout["aisle_spacing"]
        front = layout["front_y"]
        back = layout["back_y"]
        for a in range(n_aisles):
            ax.plot([a * sp, a * sp], [front, back], color="#CBD5E1", lw=0.6, zorder=1)

        # Plukkpunkter
        for a, ys in example_picks.items():
            ax.scatter([a * sp] * len(ys), ys, s=30, c=PALETTE_FILL[3],
                       edgecolors=PALETTE_STROKE[3], linewidths=0.5, zorder=3)

        # Rute
        xs_r = [p[0] for p in pts]
        ys_r = [p[1] for p in pts]
        ax.plot(xs_r, ys_r, color=col, lw=2.0, alpha=0.75, zorder=4)

        # Depot
        ax.scatter([layout["depot"]["x"]], [layout["depot"]["y"]], marker="s",
                   s=120, c=PALETTE_FILL[2], edgecolors=PALETTE_STROKE[2],
                   linewidths=1.2, zorder=5)

        ax.set_title(f"{name}: {length:.0f} m", fontsize=11, fontweight="bold")
        ax.set_aspect("equal")
        ax.grid(True, alpha=0.3)
        ax.set_xlabel("x (m)")
    axes[0].set_ylabel("y (m)")
    fig.suptitle("Ruter for samme batch under tre strategier",
                 fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    rng = np.random.default_rng(seed=77)

    print("\n" + "=" * 60)
    print("STEG 4: RUTING (largest-gap)")
    print("=" * 60)

    data, waves, batches = load_all()
    orders = data["orders"]
    layout = data["layout"]

    wave_batches_km = batches["wave_batches_kmedoids"]
    wave_batches_rnd = batches["wave_batches_random"]

    res_km = route_all_batches(wave_batches_km, orders, layout, rng)
    res_rnd = route_all_batches(wave_batches_rnd, orders, layout, rng)

    print("\nTotal reisedistanse per konfigurasjon (meter):")
    print(f"  Integrert (k-medoids + largest-gap): {res_km['largest_gap']['total_m']:,.0f}")
    print(f"  k-medoids + S-shape:                 {res_km['s_shape']['total_m']:,.0f}")
    print(f"  k-medoids + tilfeldig:               {res_km['random']['total_m']:,.0f}")
    print(f"  Tilfeldig batching + largest-gap:    {res_rnd['largest_gap']['total_m']:,.0f}")
    print(f"  Tilfeldig batching + S-shape:        {res_rnd['s_shape']['total_m']:,.0f}")

    # Finn en representativ batch for visualisering
    pretty_wave_id = batches["visualized_wave_id"]
    pretty_batches = wave_batches_km[str(pretty_wave_id)]
    # Velg en batch med moderat stor spredning
    chosen = max(pretty_batches, key=lambda b: len(b))
    example_picks = picks_by_aisle_for_batch(chosen, orders, layout)
    plot_route_compare(example_picks, layout, OUTPUT_DIR / "intlag_route_compare.png")

    out = {
        "kmedoids_largest_gap_total_m": res_km["largest_gap"]["total_m"],
        "kmedoids_largest_gap_mean_m": res_km["largest_gap"]["mean_m"],
        "kmedoids_s_shape_total_m": res_km["s_shape"]["total_m"],
        "kmedoids_random_total_m": res_km["random"]["total_m"],
        "random_batch_largest_gap_total_m": res_rnd["largest_gap"]["total_m"],
        "random_batch_s_shape_total_m": res_rnd["s_shape"]["total_m"],
        "example_batch_order_ids": chosen,
    }
    with open(OUTPUT_DIR / "step04_routes.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step04_routes.json'}")


if __name__ == "__main__":
    main()
