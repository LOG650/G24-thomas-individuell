"""
Steg 1: Datainnsamling
======================
Genererer et realistisk lagermiljo for det integrerte eksempelet:

- 2000+ SKUer med Pareto-fordelte plukkfrekvenser
- 250 kundeordrer som ankommer stokastisk gjennom en 10-timers arbeidsdag
- Hver ordre har 1-8 ordrelinjer med forventet ganske kort plukktid
- Deadlines: 70% same-day (ma ferdig innen dagens slutt), 30% next-day
- Lagerlayout: 20 parallelle ganger, 10 hylleposisjoner per side per gang
- Ressurser: 8 plukkere, 2 pakkestasjoner som deler en flaskehalskapasitet

Resultater lagres som JSON i output/step01_dataset.json + en figur
`intlag_orders_timeline.png`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from common import (
    COL_INKMUTED,
    COL_PRIMARY,
    COL_SECONDARY,
    PALETTE_FILL,
    PALETTE_STROKE,
)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def build_warehouse_layout() -> dict:
    """Bygg lagerlayout: 20 parallelle ganger med 50 hylleposisjoner per side
    (2 x 50 x 20 = 2000 plukklokasjoner).
    """
    n_aisles = 20
    n_levels = 50  # posisjoner per side per gang
    n_sides = 2
    aisle_spacing = 4.0  # meter mellom gangmidter
    shelf_pitch = 0.8  # meter mellom hyllenivaer i y
    front_y = 0.0
    back_y = front_y + (n_levels + 1) * shelf_pitch
    depot = {"x": (n_aisles - 1) * aisle_spacing / 2.0, "y": -3.0}

    locations = []
    loc_id = 0
    for a in range(n_aisles):
        x = a * aisle_spacing
        for lvl in range(n_levels):
            y = front_y + (lvl + 1) * shelf_pitch
            for side in (-1, 1):
                locations.append(
                    {
                        "id": loc_id,
                        "aisle": a,
                        "level": lvl,
                        "side": side,
                        "x": x,
                        "y": y,
                    }
                )
                loc_id += 1

    n_locations = len(locations)
    return {
        "n_aisles": n_aisles,
        "n_levels": n_levels,
        "n_sides": n_sides,
        "aisle_spacing": aisle_spacing,
        "shelf_pitch": shelf_pitch,
        "front_y": front_y,
        "back_y": back_y,
        "depot": depot,
        "n_locations": n_locations,
        "locations": locations,
    }


def generate_sku_frequencies(n_locations: int, rng: np.random.Generator) -> np.ndarray:
    """Generer Pareto-fordelte plukkfrekvenser (sterkt skjevfordelt A/B/C).

    Vi trekker vekt via en Pareto-lignende formel: vekt(i) = (i+1)^(-alpha).
    Omtrent 20% av SKUene skal staa for ~80% av plukkene.
    """
    alpha = 1.0
    ranks = np.arange(1, n_locations + 1, dtype=float)
    weights = ranks ** (-alpha)
    weights = weights / weights.sum()
    # Kast om paa indeksene slik at A-produkter ligger blandet
    order = rng.permutation(n_locations)
    shuffled = np.empty_like(weights)
    shuffled[order] = weights
    return shuffled


def generate_orders(
    layout: dict,
    sku_weights: np.ndarray,
    n_orders: int,
    day_hours: float,
    rng: np.random.Generator,
) -> list[dict]:
    """Generer kundeordrer som ankommer Poisson-jevnt gjennom dagen.

    Hver ordre har 1-8 linjer og hver linje trekkes fra SKUer vektet
    etter plukkfrekvens. Deadlines: 70% same-day, 30% next-day.
    Ankomster: Poisson-jevnt, litt flere om morgen og ettermiddag.
    """
    orders = []

    # Ankomstfordeling: to-topp (morgen + ettermiddag) med Beta-miks
    mix = rng.beta(2.0, 4.0, n_orders)  # morgen
    mix2 = rng.beta(4.0, 2.0, n_orders)  # ettermiddag
    which = rng.random(n_orders) < 0.55
    times_frac = np.where(which, mix, mix2)
    arrival_minutes = np.sort(times_frac * day_hours * 60.0)

    n_locations = layout["n_locations"]
    for i, t in enumerate(arrival_minutes):
        n_lines = int(rng.integers(1, 9))
        line_ids = rng.choice(
            n_locations, size=n_lines, replace=False, p=sku_weights
        ).tolist()
        deadline_class = "same_day" if rng.random() < 0.70 else "next_day"
        if deadline_class == "same_day":
            deadline_min = day_hours * 60.0  # innen dagslutt
        else:
            deadline_min = (day_hours + 12.0) * 60.0  # neste morgen (bokforsing)
        orders.append(
            {
                "order_id": int(i),
                "arrival_min": float(t),
                "n_lines": int(n_lines),
                "line_location_ids": [int(x) for x in line_ids],
                "deadline_class": deadline_class,
                "deadline_min": float(deadline_min),
            }
        )
    return orders


def plot_orders_timeline(orders: list[dict], day_hours: float, output_path: Path) -> None:
    """Tidslinje for ankommende ordrer + linjer per ordre, farget etter deadline."""
    times = np.array([o["arrival_min"] / 60.0 for o in orders])
    lines = np.array([o["n_lines"] for o in orders])
    colors = [PALETTE_STROKE[0] if o["deadline_class"] == "same_day" else PALETTE_STROKE[2] for o in orders]

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.2), sharex=True,
                                    gridspec_kw={"height_ratios": [1, 2]})

    ax1.hist(times, bins=int(day_hours * 2), color=PALETTE_FILL[0], edgecolor=PALETTE_STROKE[0])
    ax1.set_ylabel("Ordrer/halvtime", fontsize=10)
    ax1.set_title("Ordreankomster gjennom dagen", fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3)

    ax2.scatter(times, lines, c=colors, s=22, alpha=0.75, edgecolors="none")
    ax2.set_xlabel("Tid (timer siden arbeidsdagens start)", fontsize=10)
    ax2.set_ylabel("Antall linjer per ordre", fontsize=10)
    ax2.grid(True, alpha=0.3)

    # Lag en manuell legende
    from matplotlib.lines import Line2D
    legend_elems = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE_STROKE[0],
               markersize=8, label="Same-day"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor=PALETTE_STROKE[2],
               markersize=8, label="Next-day"),
    ]
    ax2.legend(handles=legend_elems, loc="upper right", fontsize=9)
    ax2.set_xlim(0, day_hours)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_layout_with_frequency(
    layout: dict, sku_weights: np.ndarray, output_path: Path
) -> None:
    """Visualiser lagerlayout med ABC-klassifisering fargelagt.

    A = topp 20% frekvens, B = neste 30%, C = nederste 50%.
    """
    locs = layout["locations"]
    xs = np.array([loc["x"] for loc in locs])
    ys = np.array([loc["y"] for loc in locs])
    weights = sku_weights

    # ABC-klassifisering
    order = np.argsort(-weights)
    classes = np.empty(len(locs), dtype=int)
    n20 = int(len(locs) * 0.2)
    n50 = int(len(locs) * 0.5)
    classes[order[:n20]] = 0  # A
    classes[order[n20 : n20 + n50]] = 1  # B
    classes[order[n20 + n50 :]] = 2  # C

    fig, ax = plt.subplots(figsize=(10, 6))
    fills = [PALETTE_FILL[0], PALETTE_FILL[1], PALETTE_FILL[3]]
    strokes = [PALETTE_STROKE[0], PALETTE_STROKE[1], PALETTE_STROKE[3]]
    labels = ["A-lokasjoner (topp 20%)", "B-lokasjoner (mellom 30%)", "C-lokasjoner (nederste 50%)"]

    for c in (2, 1, 0):  # plot C forst slik at A havner pa toppen
        mask = classes == c
        ax.scatter(
            xs[mask], ys[mask], s=8, c=fills[c], edgecolors=strokes[c],
            linewidths=0.3, label=labels[c],
        )

    # Depot
    ax.scatter(
        [layout["depot"]["x"]], [layout["depot"]["y"]], marker="s", s=140,
        c=PALETTE_FILL[2], edgecolors=PALETTE_STROKE[2], linewidths=1.5, label="Pakkestasjon",
    )

    ax.set_xlabel("x (meter)", fontsize=10)
    ax.set_ylabel("y (meter)", fontsize=10)
    ax.set_title("Lagerlayout med ABC-klassifisering av plukklokasjoner",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    rng = np.random.default_rng(seed=42)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    layout = build_warehouse_layout()
    print(f"\nLagerlayout: {layout['n_aisles']} ganger x {layout['n_levels']} nivaer x 2 sider")
    print(f"  Totalt {layout['n_locations']} plukklokasjoner")
    print(f"  Dybde: {layout['back_y'] - layout['front_y']:.1f} m per gang")

    sku_weights = generate_sku_frequencies(layout["n_locations"], rng)
    top20 = np.sort(sku_weights)[-int(0.2 * len(sku_weights)) :].sum()
    print(f"  Topp 20% av SKUer dekker {top20 * 100:.1f}% av forventet plukkvolum")

    day_hours = 10.0  # arbeidsdag 08-18
    n_orders = 250
    orders = generate_orders(layout, sku_weights, n_orders, day_hours, rng)

    total_lines = sum(o["n_lines"] for o in orders)
    same_day = sum(1 for o in orders if o["deadline_class"] == "same_day")
    print(f"\nOrdrer: {n_orders} (totalt {total_lines} ordrelinjer)")
    print(f"  Same-day: {same_day} ({same_day / n_orders * 100:.0f}%)")
    print(f"  Gjennomsnittlig linjer/ordre: {total_lines / n_orders:.2f}")
    print(f"  Arbeidsdag: {day_hours:.0f} timer (Poisson-ankomster)")

    # Ressurser. Pakkestasjonen er flaskehals: kapasitet
    # n_pack * wave_len / pack_time_per_line skal vaere lavere enn
    # summen av linjer i en typisk travel bolge.
    resources = {
        "n_pickers": 8,
        "picker_speed_m_per_min": 50.0,  # 3 km/t tilsvarer 50 m/min
        "pick_time_per_line_min": 0.4,  # 24 sek per plukk
        "n_pack_stations": 2,
        "pack_time_per_line_min": 0.85,  # 51 sek per linje (gjor pakking til flaskehals)
    }
    print(
        "\nRessurser:"
        f" {resources['n_pickers']} plukkere,"
        f" {resources['n_pack_stations']} pakkestasjoner"
    )

    dataset = {
        "layout": layout,
        "sku_weights": sku_weights.tolist(),
        "orders": orders,
        "resources": resources,
        "day_hours": day_hours,
    }

    with open(OUTPUT_DIR / "step01_dataset.json", "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"\nDatasett lagret: {OUTPUT_DIR / 'step01_dataset.json'}")

    plot_orders_timeline(orders, day_hours, OUTPUT_DIR / "intlag_orders_timeline.png")
    plot_layout_with_frequency(layout, sku_weights, OUTPUT_DIR / "intlag_layout_abc.png")

    # Kort statistikktabell som JSON for LaTeX
    stats = {
        "n_locations": layout["n_locations"],
        "n_aisles": layout["n_aisles"],
        "n_levels": layout["n_levels"],
        "n_orders": n_orders,
        "n_lines_total": total_lines,
        "same_day_share": same_day / n_orders,
        "mean_lines_per_order": total_lines / n_orders,
        "top20_coverage": float(top20),
        "day_hours": day_hours,
        "n_pickers": resources["n_pickers"],
        "n_pack_stations": resources["n_pack_stations"],
    }
    with open(OUTPUT_DIR / "step01_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
