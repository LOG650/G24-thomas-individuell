"""
Steg 5: Full-dag SimPy-simulering
=================================
Vi simulerer en arbeidsdag der:
  1. Ordrer ankommer til systemet pa tidspunkt o['arrival_min'].
  2. Bolgeplanleggingen tildeler ordrer til bolger (step02).
  3. Ved bolgestart batches ordrer (step03), og batcher legges i en ko.
  4. 8 plukkere tar batcher fra koen og utforer rutene (rutetid fra
     step04 pluss fast plukktid per linje).
  5. Ferdigplukkede batcher gar til pakkestasjonen (SimPy.Resource med
     kapasitet 2), der pakketid = n_lines * pack_time_per_line.

Vi kjorer 4 varianter:
  A) Integrert: MIP-bolger + k-medoids + largest-gap
  B) Bare bolger optimert (FIFO-batching + largest-gap)
  C) Bare batching optimert (FIFO-bolger + k-medoids + largest-gap)
  D) Baseline: FIFO-bolger + tilfeldig batching + S-shape
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import simpy

from common import (
    PALETTE_FILL,
    PALETTE_STROKE,
    kmedoids_or_fallback,
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


def fifo_wave_assignment(orders: list[dict], wave_length_min: float,
                         day_hours: float) -> tuple[dict, list[dict]]:
    """FIFO: tildel hver ordre til forste bolge som starter >= ankomsttid."""
    n_waves = int(day_hours * 60.0 / wave_length_min) + 1
    waves = [
        {"wave_id": w, "start_min": w * wave_length_min, "end_min": (w + 1) * wave_length_min}
        for w in range(n_waves)
    ]
    assignments = {}
    wave_orders = {w["wave_id"]: [] for w in waves}
    for o in orders:
        for w in waves:
            if w["start_min"] >= o["arrival_min"] - 1e-6:
                assignments[o["order_id"]] = w["wave_id"]
                wave_orders[w["wave_id"]].append(o["order_id"])
                break
    return {"wave_orders": wave_orders, "waves": waves}, waves


def build_batches(wave_orders: dict, orders: list[dict], layout: dict,
                  method: str, rng: np.random.Generator,
                  target_batch_size: int = 5) -> dict[int, list[list[int]]]:
    out = {}
    orders_by_id = {o["order_id"]: o for o in orders}
    locs_by_id = {loc["id"]: loc for loc in layout["locations"]}
    for wid, oids in wave_orders.items():
        if not oids:
            out[wid] = []
            continue
        if method == "kmedoids":
            feats = np.array([
                [
                    np.mean([locs_by_id[l]["x"] for l in orders_by_id[o]["line_location_ids"]]),
                    np.mean([locs_by_id[l]["y"] for l in orders_by_id[o]["line_location_ids"]]),
                ]
                for o in oids
            ])
            k = max(1, math.ceil(len(oids) / target_batch_size))
            labels, _ = kmedoids_or_fallback(feats, k, rng)
            batches = [[] for _ in range(k)]
            for i, oid in enumerate(oids):
                batches[labels[i]].append(oid)
            out[wid] = [b for b in batches if b]
        else:
            shuffled = list(oids)
            rng.shuffle(shuffled)
            out[wid] = [
                shuffled[i : i + target_batch_size]
                for i in range(0, len(shuffled), target_batch_size)
            ]
    return out


def batch_route_time(batch: list[int], orders: list[dict], layout: dict,
                     routing: str, resources: dict, rng: np.random.Generator) -> tuple[float, int]:
    """Total tid for a plukke en batch: rutetid + per-linje-plukktid."""
    orders_by_id = {o["order_id"]: o for o in orders}
    locs_by_id = {loc["id"]: loc for loc in layout["locations"]}
    picks: dict[int, list[float]] = {}
    total_lines = 0
    for oid in batch:
        for lid in orders_by_id[oid]["line_location_ids"]:
            loc = locs_by_id[lid]
            picks.setdefault(loc["aisle"], []).append(loc["y"])
            total_lines += 1
    for a in picks:
        picks[a].sort()

    if routing == "largest_gap":
        length, _ = largest_gap_route_length(picks, layout)
    elif routing == "s_shape":
        length, _ = s_shape_route_length(picks, layout)
    else:
        length, _ = random_route_length(picks, layout, rng)

    travel_time = length / resources["picker_speed_m_per_min"]
    pick_time = total_lines * resources["pick_time_per_line_min"]
    return travel_time + pick_time, total_lines


def run_simpy(wave_orders: dict, wave_schedule: list[dict],
              batches_per_wave: dict, orders: list[dict],
              layout: dict, resources: dict, routing: str,
              sim_name: str, seed: int = 0) -> dict:
    """Kjor en SimPy-simulering og mal KPIer."""
    env = simpy.Environment()
    pickers = simpy.Resource(env, capacity=resources["n_pickers"])
    pack = simpy.Resource(env, capacity=resources["n_pack_stations"])
    rng = np.random.default_rng(seed)

    orders_by_id = {o["order_id"]: o for o in orders}
    wave_by_id = {w["wave_id"]: w for w in wave_schedule}

    completion_times: dict[int, float] = {}
    pack_queue_samples: list[tuple[float, int]] = []

    def sample_queue():
        while True:
            pack_queue_samples.append((env.now, len(pack.queue)))
            yield env.timeout(2.0)

    env.process(sample_queue())

    def process_batch(batch: list[int], wave_id: int):
        route_time, n_lines = batch_route_time(
            batch, orders, layout, routing, resources, rng
        )
        with pickers.request() as pr:
            yield pr
            yield env.timeout(route_time)
        pack_time = n_lines * resources["pack_time_per_line_min"]
        with pack.request() as pk:
            yield pk
            yield env.timeout(pack_time)
        for oid in batch:
            completion_times[oid] = env.now

    def wave_release(wave_id: int):
        w = wave_by_id[wave_id]
        yield env.timeout(max(0.0, w["start_min"] - env.now))
        for batch in batches_per_wave.get(wave_id, []):
            env.process(process_batch(batch, wave_id))

    for wid in wave_by_id:
        env.process(wave_release(wid))

    # Run langt nok til alt er ferdig
    env.run(until=24 * 60.0)

    # KPIer
    deadlines = {o["order_id"]: o["deadline_min"] for o in orders}
    on_time = sum(1 for oid, t in completion_times.items() if t <= deadlines[oid] + 1e-6)
    total = len(orders)
    completed = len(completion_times)
    throughput = completed  # antall ordrer plukket/pakket
    avg_completion = float(np.mean(list(completion_times.values()))) if completion_times else 0.0

    # Plukkerproduktivitet: gjennomsnitt linjer plukket per time (aktiv tid)
    total_lines = sum(orders_by_id[oid]["n_lines"] for oid in completion_times)
    # Gjennomsnittlig pakkeko
    qs = np.array([q for _, q in pack_queue_samples])
    avg_pack_queue = float(qs.mean()) if qs.size else 0.0
    max_pack_queue = float(qs.max()) if qs.size else 0.0

    # Plukkertid (approks): sum av (rutetid+plukktid) delt pa n_pickers
    # Simpy-approks: lik total virketid delt pa n_pickers * makstid
    # Her bruker vi: gjennomsnittlig ordrefullforingstid
    # og antar total plukker-utnyttelse = (antall ordrer*gjennomsnittlig batchtid)/((makstid)*n_pickers)

    return {
        "name": sim_name,
        "completed": completed,
        "total_orders": total,
        "on_time": on_time,
        "on_time_share": on_time / total if total else 0.0,
        "throughput": throughput,
        "mean_completion_min": avg_completion,
        "total_lines": total_lines,
        "mean_pack_queue": avg_pack_queue,
        "max_pack_queue": max_pack_queue,
        "pack_queue_series": pack_queue_samples,
        "completion_times": {int(k): v for k, v in completion_times.items()},
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 5: SIMPY-SIMULERING (4 strategier)")
    print("=" * 60)

    data, mip_waves, km_batches = load_all()
    orders = data["orders"]
    layout = data["layout"]
    resources = data["resources"]
    day_hours = data["day_hours"]
    wave_length_min = mip_waves["wave_length_min"]

    # Faktiske MIP-bolger:
    mip_schedule = mip_waves["waves"]
    mip_wave_orders = {int(k): v for k, v in mip_waves["wave_orders"].items()}
    km_batches_per_wave = {int(k): v for k, v in km_batches["wave_batches_kmedoids"].items()}

    # FIFO-bolger (utgangspunkt for baseline B og D):
    fifo_info, fifo_schedule = fifo_wave_assignment(orders, wave_length_min, day_hours)
    fifo_wave_orders = fifo_info["wave_orders"]

    # FIFO-batcher (kronologisk chunking av en bolge)
    def fifo_chunks(wave_orders: dict, target: int = 5) -> dict:
        out = {}
        for wid, oids in wave_orders.items():
            sorted_ids = sorted(oids, key=lambda oid: next(
                o["arrival_min"] for o in orders if o["order_id"] == oid
            ))
            out[wid] = [
                sorted_ids[i : i + target] for i in range(0, len(sorted_ids), target)
            ]
        return out

    runs: list[dict] = []
    # A) Integrert: MIP-bolger + k-medoids + largest-gap
    runs.append(run_simpy(mip_wave_orders, mip_schedule, km_batches_per_wave,
                          orders, layout, resources, routing="largest_gap",
                          sim_name="A) Integrert MIP + k-medoids + largest-gap", seed=101))

    # B) Bare bolger optimert: MIP + FIFO-batching + largest-gap
    fifo_batches_in_mip = fifo_chunks(mip_wave_orders)
    runs.append(run_simpy(mip_wave_orders, mip_schedule, fifo_batches_in_mip,
                          orders, layout, resources, routing="largest_gap",
                          sim_name="B) Bare bolge-MIP + FIFO-batching", seed=102))

    # C) Bare batching optimert: FIFO-bolger + k-medoids + largest-gap
    km_batches_fifo = build_batches(fifo_wave_orders, orders, layout,
                                    method="kmedoids", rng=np.random.default_rng(33))
    runs.append(run_simpy(fifo_wave_orders, fifo_schedule, km_batches_fifo,
                          orders, layout, resources, routing="largest_gap",
                          sim_name="C) FIFO-bolger + k-medoids + largest-gap", seed=103))

    # D) Baseline: FIFO-bolger + tilfeldig batching + S-shape
    random_batches_fifo = build_batches(fifo_wave_orders, orders, layout,
                                        method="random", rng=np.random.default_rng(44))
    runs.append(run_simpy(fifo_wave_orders, fifo_schedule, random_batches_fifo,
                          orders, layout, resources, routing="s_shape",
                          sim_name="D) Baseline: FIFO + tilfeldig + S-shape", seed=104))

    print("\nKPI-sammendrag:")
    print("-" * 90)
    print(f"{'Strategi':55s} {'On-time':>10s} {'Gjsnitt':>10s} {'Pakkeko':>8s}")
    print(f"{'':55s} {'(%)':>10s} {'ferdig (min)':>10s} {'(avg)':>8s}")
    print("-" * 90)
    for r in runs:
        print(
            f"{r['name']:55s} {r['on_time_share'] * 100:>10.1f} "
            f"{r['mean_completion_min']:>10.1f} {r['mean_pack_queue']:>8.2f}"
        )
    print("-" * 90)

    # Lagre uten queue_series (stor)
    out = []
    for r in runs:
        rc = {k: v for k, v in r.items() if k != "pack_queue_series" and k != "completion_times"}
        out.append(rc)
    with open(OUTPUT_DIR / "step05_simpy.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step05_simpy.json'}")

    # Figurer
    plot_pack_queue(runs, OUTPUT_DIR / "intlag_pack_queue.png")


def plot_pack_queue(runs, output_path: Path):
    fig, ax = plt.subplots(figsize=(10, 4.6))
    for r, col_f, col_s in zip(runs, PALETTE_FILL, PALETTE_STROKE):
        series = r["pack_queue_series"]
        if not series:
            continue
        ts = np.array([t for t, _ in series]) / 60.0
        qs = np.array([q for _, q in series])
        ax.plot(ts, qs, color=col_s, lw=1.4, alpha=0.85, label=r["name"])
    ax.set_xlabel("Tid (timer)", fontsize=10)
    ax.set_ylabel("Antall batcher som venter pa pakking", fontsize=10)
    ax.set_title("Kolengde ved pakkestasjonen gjennom dagen", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


if __name__ == "__main__":
    main()
