"""
Steg 3: Batching via k-medoids
==============================
Innenfor hver bolge grupperer vi ordrer i batcher av 4-6 ordrer slik at
ordrer i samme batch har plukklokasjoner som ligger naer hverandre.

Vi representerer hver ordre som en vektor i det 2D gangrommet:
  feat_i = (mean_aisle_x, mean_y)

og kjorer k-medoids (via PAM-aktig greedy + swap) der antall klynger er:
  k = ceil(n_orders_in_wave / target_batch_size)

Alternativ baseline: tilfeldig batching (chunked).
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from common import PALETTE_FILL, PALETTE_STROKE, kmedoids_or_fallback

OUTPUT_DIR = Path(__file__).parent.parent / "output"
TARGET_BATCH_SIZE = 5


def load_inputs():
    with open(OUTPUT_DIR / "step01_dataset.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    with open(OUTPUT_DIR / "step02_waves.json", "r", encoding="utf-8") as f:
        waves = json.load(f)
    return data, waves


def order_feature(order: dict, layout: dict) -> np.ndarray:
    """Gjennomsnittsposisjon for plukkene i en ordre (i gang-koordinater)."""
    locs = layout["locations"]
    loc_by_id = {loc["id"]: loc for loc in locs}
    xs = [loc_by_id[lid]["x"] for lid in order["line_location_ids"]]
    ys = [loc_by_id[lid]["y"] for lid in order["line_location_ids"]]
    return np.array([np.mean(xs), np.mean(ys)])


def kmedoids_batch_orders(order_ids: list[int], features: np.ndarray, k: int,
                          rng: np.random.Generator) -> list[list[int]]:
    """Enkel PAM-lignende k-medoids."""
    if k >= len(order_ids):
        return [[oid] for oid in order_ids]
    labels, medoids = kmedoids_or_fallback(features, k, rng)
    batches = [[] for _ in range(k)]
    for i, oid in enumerate(order_ids):
        batches[labels[i]].append(oid)
    return batches


def random_batch_orders(order_ids: list[int], batch_size: int,
                        rng: np.random.Generator) -> list[list[int]]:
    shuffled = list(order_ids)
    rng.shuffle(shuffled)
    batches = []
    for i in range(0, len(shuffled), batch_size):
        batches.append(shuffled[i : i + batch_size])
    return batches


def compute_batches_for_wave(wave_order_ids: list[int], orders: list[dict],
                              layout: dict, rng: np.random.Generator,
                              method: str = "kmedoids") -> list[list[int]]:
    if not wave_order_ids:
        return []
    orders_by_id = {o["order_id"]: o for o in orders}
    feats = np.array([order_feature(orders_by_id[oid], layout) for oid in wave_order_ids])
    k = max(1, math.ceil(len(wave_order_ids) / TARGET_BATCH_SIZE))
    if method == "kmedoids":
        return kmedoids_batch_orders(wave_order_ids, feats, k, rng)
    else:
        return random_batch_orders(wave_order_ids, TARGET_BATCH_SIZE, rng)


def plot_batch_clusters(wave_order_ids: list[int], orders: list[dict],
                         layout: dict, batches: list[list[int]],
                         output_path: Path) -> None:
    """Vis hvordan ordrer i en bolge klynges i batcher i (x,y)."""
    orders_by_id = {o["order_id"]: o for o in orders}
    locs_by_id = {loc["id"]: loc for loc in layout["locations"]}

    fig, ax = plt.subplots(figsize=(9, 6))
    # Bakgrunn: lett skissering av ganger
    n_aisles = layout["n_aisles"]
    sp = layout["aisle_spacing"]
    front = layout["front_y"]
    back = layout["back_y"]
    for a in range(n_aisles):
        ax.plot([a * sp, a * sp], [front, back], color="#CBD5E1", lw=0.6, zorder=1)

    # Tegn hver batch med sin egen farge
    for b_idx, batch in enumerate(batches):
        color_f = PALETTE_FILL[b_idx % len(PALETTE_FILL)]
        color_s = PALETTE_STROKE[b_idx % len(PALETTE_STROKE)]
        xs, ys = [], []
        for oid in batch:
            o = orders_by_id[oid]
            for lid in o["line_location_ids"]:
                loc = locs_by_id[lid]
                xs.append(loc["x"])
                ys.append(loc["y"])
        ax.scatter(xs, ys, s=28, c=color_f, edgecolors=color_s, linewidths=0.5,
                   label=f"Batch {b_idx + 1} ({len(batch)} ordrer)", zorder=3)

    # Depot
    ax.scatter([layout["depot"]["x"]], [layout["depot"]["y"]], marker="s", s=140,
               c=PALETTE_FILL[2], edgecolors=PALETTE_STROKE[2], linewidths=1.2,
               label="Pakkestasjon", zorder=4)

    ax.set_xlabel("x (meter)", fontsize=10)
    ax.set_ylabel("y (meter)", fontsize=10)
    ax.set_title("k-medoids-batching innenfor en bolge: plukkpunkter fargelagt per batch",
                 fontsize=12, fontweight="bold")
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8, ncol=2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    rng = np.random.default_rng(seed=123)

    print("\n" + "=" * 60)
    print("STEG 3: BATCHING (k-medoids)")
    print("=" * 60)

    data, waves = load_inputs()
    orders = data["orders"]
    layout = data["layout"]

    wave_batches_km = {}
    wave_batches_rnd = {}
    # wave_orders n kommer fra step02 som streng-nokler
    wave_orders = {int(k): v for k, v in waves["wave_orders"].items()}
    for w_id, oids in wave_orders.items():
        wave_batches_km[w_id] = compute_batches_for_wave(oids, orders, layout, rng, method="kmedoids")
        wave_batches_rnd[w_id] = compute_batches_for_wave(oids, orders, layout, rng, method="random")

    # Kompaktheitsmal: gjennomsnittlig aisle-spredning per batch
    def compactness(batches: list[list[int]]) -> float:
        orders_by_id = {o["order_id"]: o for o in orders}
        locs_by_id = {loc["id"]: loc for loc in layout["locations"]}
        spans = []
        for batch in batches:
            aisles = set()
            for oid in batch:
                for lid in orders_by_id[oid]["line_location_ids"]:
                    aisles.add(locs_by_id[lid]["aisle"])
            if aisles:
                spans.append(max(aisles) - min(aisles))
        return float(np.mean(spans)) if spans else 0.0

    all_km_batches = [b for lst in wave_batches_km.values() for b in lst]
    all_rnd_batches = [b for lst in wave_batches_rnd.values() for b in lst]
    comp_km = compactness(all_km_batches)
    comp_rnd = compactness(all_rnd_batches)
    print(f"\nKompaktheit (gjennomsnittlig gang-spenn per batch):")
    print(f"  k-medoids: {comp_km:.2f} ganger")
    print(f"  tilfeldig: {comp_rnd:.2f} ganger")
    print(f"  Forbedring: {(1 - comp_km / comp_rnd) * 100:.0f}%")

    # Velg en representativ bolge for visualisering
    pretty_wave = max(wave_orders.keys(), key=lambda wid: len(wave_orders[wid]))
    plot_batch_clusters(
        wave_orders[pretty_wave], orders, layout,
        wave_batches_km[pretty_wave], OUTPUT_DIR / "intlag_batches_clusters.png",
    )

    out = {
        "wave_batches_kmedoids": {str(k): v for k, v in wave_batches_km.items()},
        "wave_batches_random": {str(k): v for k, v in wave_batches_rnd.items()},
        "compactness_kmedoids_mean_aisle_span": comp_km,
        "compactness_random_mean_aisle_span": comp_rnd,
        "target_batch_size": TARGET_BATCH_SIZE,
        "visualized_wave_id": pretty_wave,
        "n_batches_kmedoids": len(all_km_batches),
        "n_batches_random": len(all_rnd_batches),
    }
    with open(OUTPUT_DIR / "step03_batches.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Resultater lagret: {OUTPUT_DIR / 'step03_batches.json'}")


if __name__ == "__main__":
    main()
