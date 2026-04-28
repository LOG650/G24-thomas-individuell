"""
Steg 2: Bolgeplanlegging via tidsindeksert MIP
==============================================
Formulerer og loser:

  min     sum_{i,w} c_{i,w} * x_{i,w}       (straff for sen tildeling)
  s.t.    sum_w x_{i,w} = 1                 for hver ordre i
          sum_i n_lines_i * x_{i,w} <= C_w  for hver bolge w (pakkekapasitet)
          sum_{w > w_max(i)} x_{i,w} = 0    ordre tildeles kun bolger
                                             der den kan rekke deadline
          x_{i,w} binaer

Bolgene er 5 tidsvinduer av 2 timer: [0-2, 2-4, 4-6, 6-8, 8-10].
Pakkestasjonen har kapasitet = n_pack_stations * pack_rate * window_len.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pulp

from common import COL_PRIMARY, COL_SECONDARY, PALETTE_FILL, PALETTE_STROKE

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def load_dataset() -> dict:
    with open(OUTPUT_DIR / "step01_dataset.json", "r", encoding="utf-8") as f:
        return json.load(f)


def build_waves(day_hours: float, wave_length_min: float = 120.0) -> list[dict]:
    """Lag bolger som dekker arbeidsdagen + en etterslep-bolge for next-day."""
    n_waves = int(day_hours * 60.0 / wave_length_min)
    waves = []
    for w in range(n_waves):
        waves.append(
            {
                "wave_id": w,
                "start_min": w * wave_length_min,
                "end_min": (w + 1) * wave_length_min,
            }
        )
    # Next-day-bolge (for next-day-ordrer som ikke passer inn i dagens bolger)
    waves.append(
        {
            "wave_id": n_waves,
            "start_min": day_hours * 60.0,
            "end_min": day_hours * 60.0 + wave_length_min,
        }
    )
    return waves


def feasible_waves_for_order(order: dict, waves: list[dict]) -> list[int]:
    """Hvilke bolger kan denne ordren tildeles uten a bryte deadline?"""
    feas = []
    for w in waves:
        # Ordren kan kun tildeles bolger som starter >= ankomst
        if w["start_min"] < order["arrival_min"] - 1e-6:
            continue
        # Ordren ma vaere ferdig pakket for deadline: bolge-slutt <= deadline
        if w["end_min"] > order["deadline_min"] + 1e-6:
            continue
        feas.append(w["wave_id"])
    return feas


def solve_wave_mip(orders: list[dict], waves: list[dict], resources: dict,
                   wave_length_min: float = 120.0, verbose: bool = False) -> dict:
    """Los tidsindeksert MIP for bolgetildeling."""
    n_pack = resources["n_pack_stations"]
    pack_rate = 1.0 / resources["pack_time_per_line_min"]  # linjer/min per stasjon
    cap_per_wave = n_pack * pack_rate * wave_length_min  # linjer per bolge
    print(f"  Pakkekapasitet per bolge: {cap_per_wave:.0f} linjer")

    # MIP
    prob = pulp.LpProblem("wave_assignment", pulp.LpMinimize)
    x = {}
    for o in orders:
        feas = feasible_waves_for_order(o, waves)
        if not feas:
            # Ordren kan ikke rekke deadline i noe bolge -- ma tildeles
            # forste feasible (vi slar paa myk straff i saa fall)
            feas = [w["wave_id"] for w in waves]
        o["feasible_waves"] = feas
        for w_id in feas:
            x[(o["order_id"], w_id)] = pulp.LpVariable(
                f"x_{o['order_id']}_{w_id}", cat=pulp.LpBinary
            )

    # Malfunksjon: straff sen tildeling + svak straff for ujevn fordeling
    # Straff = w_id (tidlig bolge = lav straff) -- dette trekker ordrer mot
    # tidlige bolger og frigjor kapasitet for sent ankommende ordrer
    prob += pulp.lpSum(
        (w_id + 1) * x[(o["order_id"], w_id)]
        for o in orders
        for w_id in o["feasible_waves"]
    )

    # Hver ordre tildeles noyaktig en bolge
    for o in orders:
        prob += pulp.lpSum(x[(o["order_id"], w_id)] for w_id in o["feasible_waves"]) == 1

    # Pakkekapasitetsbegrensning per bolge
    for w in waves:
        w_id = w["wave_id"]
        lines_in_wave = pulp.lpSum(
            o["n_lines"] * x[(o["order_id"], w_id)]
            for o in orders
            if w_id in o["feasible_waves"]
        )
        prob += lines_in_wave <= cap_per_wave

    solver = pulp.PULP_CBC_CMD(msg=int(verbose))
    status = prob.solve(solver)
    assert pulp.LpStatus[status] == "Optimal", f"Solver-status: {pulp.LpStatus[status]}"

    assignments = {}
    wave_loads = {w["wave_id"]: 0 for w in waves}
    wave_orders = {w["wave_id"]: [] for w in waves}
    for o in orders:
        chosen = None
        for w_id in o["feasible_waves"]:
            v = x[(o["order_id"], w_id)].value()
            if v is not None and v > 0.5:
                chosen = w_id
                break
        assignments[o["order_id"]] = int(chosen)
        wave_loads[chosen] += o["n_lines"]
        wave_orders[chosen].append(o["order_id"])

    return {
        "assignments": assignments,
        "wave_loads": wave_loads,
        "wave_orders": wave_orders,
        "wave_capacity": cap_per_wave,
        "objective": pulp.value(prob.objective),
        "waves": waves,
        "wave_length_min": wave_length_min,
    }


def plot_waves(result: dict, orders: list[dict], output_path: Path) -> None:
    """Gantt-liknende figur: for hver bolge, stablet sokylediagram med ordrer fargelagt etter deadline."""
    waves = result["waves"]
    wave_orders = result["wave_orders"]
    capacity = result["wave_capacity"]

    # Farger: same-day (bla), next-day (oransje)
    fills = {"same_day": PALETTE_FILL[0], "next_day": PALETTE_FILL[2]}
    strokes = {"same_day": PALETTE_STROKE[0], "next_day": PALETTE_STROKE[2]}

    orders_by_id = {o["order_id"]: o for o in orders}

    fig, ax = plt.subplots(figsize=(10, 4.6))
    width = 0.8
    x_pos = np.arange(len(waves))
    for i, w in enumerate(waves):
        bottom = 0
        for oid in wave_orders[w["wave_id"]]:
            o = orders_by_id[oid]
            cls = o["deadline_class"]
            ax.bar(
                i, o["n_lines"], bottom=bottom, width=width,
                color=fills[cls], edgecolor=strokes[cls], linewidth=0.25,
            )
            bottom += o["n_lines"]

    # Kapasitetsstrek
    ax.axhline(capacity, ls="--", color=PALETTE_STROKE[4], lw=1.5, label=f"Pakkekapasitet = {capacity:.0f} linjer")

    ax.set_xticks(x_pos)
    labels = []
    for w in waves:
        h0 = w["start_min"] / 60.0
        h1 = w["end_min"] / 60.0
        labels.append(f"W{w['wave_id']}\n{h0:.0f}-{h1:.0f}t")
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylabel("Linjer tildelt bolgen", fontsize=10)
    ax.set_title("Bolgetildeling fra MIP (fargelagt etter deadline-klasse)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")

    # Manuell legende
    from matplotlib.patches import Patch
    handles = [
        Patch(facecolor=fills["same_day"], edgecolor=strokes["same_day"], label="Same-day"),
        Patch(facecolor=fills["next_day"], edgecolor=strokes["next_day"], label="Next-day"),
        plt.Line2D([0], [0], color=PALETTE_STROKE[4], ls="--", lw=1.5,
                   label=f"Kapasitet {capacity:.0f}"),
    ]
    ax.legend(handles=handles, loc="upper right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 2: BOLGEPLANLEGGING (MIP)")
    print("=" * 60)

    data = load_dataset()
    orders = data["orders"]
    resources = data["resources"]
    day_hours = data["day_hours"]

    waves = build_waves(day_hours, wave_length_min=120.0)
    print(f"\nBolger: {len(waves)} (lengde 120 min hver)")

    result = solve_wave_mip(orders, waves, resources, wave_length_min=120.0, verbose=False)

    print("\nBolgebelastning (linjer):")
    for w in waves:
        wid = w["wave_id"]
        n_ord = len(result["wave_orders"][wid])
        load = result["wave_loads"][wid]
        print(f"  W{wid}: {n_ord:3d} ordrer, {load:4d} linjer (kap: {result['wave_capacity']:.0f})")
    print(f"\nMalfunksjonsverdi: {result['objective']:.1f}")

    # Lagre
    out = {
        "assignments": result["assignments"],
        "wave_loads": result["wave_loads"],
        "wave_orders": result["wave_orders"],
        "wave_capacity": result["wave_capacity"],
        "waves": result["waves"],
        "wave_length_min": result["wave_length_min"],
        "objective": float(result["objective"]),
    }
    with open(OUTPUT_DIR / "step02_waves.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step02_waves.json'}")

    plot_waves(result, orders, OUTPUT_DIR / "intlag_waves.png")


if __name__ == "__main__":
    main()
