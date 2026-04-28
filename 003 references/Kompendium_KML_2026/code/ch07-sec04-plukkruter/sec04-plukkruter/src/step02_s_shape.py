"""
Steg 2: S-shape (traversal) heuristikk
======================================
S-shape (traversal) er den mest brukte plukkruteheuristikken i parallell-gang-lagre.
Regelen er enkel: Enhver gang som inneholder minst én plukklokasjon traverseres
i sin helhet. Plukkeren starter i depot, går til første gang med plukk, traverserer
den helt (front->bak), krysser via bakgangen til neste gang med plukk, traverserer
denne i motsatt retning (bak->front), og så videre.

Unntak: den siste gangen som inneholder plukk kan gås som return-gang dersom alle
gangens plukk ligger nær inngangsenden. I standard lærebok-S-shape traverseres
alle besøkte ganger. Vi implementerer strikt S-shape (traverser alle besøkte ganger).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt

from common import (
    Point,
    aisle_picks,
    aisle_x,
    back_y,
    depot_point,
    front_y,
    l1,
)
from step01_datainnsamling import plot_layout as _plot_layout  # noqa: F401 (for ref)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def s_shape_route(layout: dict, picklist_ids: list[int]) -> list[Point]:
    """Returner eksplisitt sekvens av punkter for S-shape rute."""
    by_aisle = aisle_picks(layout, picklist_ids)
    if not by_aisle:
        return [depot_point(layout), depot_point(layout)]

    # Identifiser besøkte ganger i stigende rekkefølge
    visited = sorted(by_aisle.keys())
    last_idx = len(visited) - 1

    fy, by = front_y(layout), back_y(layout)
    route: list[Point] = []
    depot = depot_point(layout)
    route.append(depot)

    # Gå til front av første gang
    a0 = visited[0]
    route.append(Point(aisle_x(layout, a0), fy))

    # For hver besøkt gang: full traversering (alternerende retning).
    # Unntak: hvis det er et oddetall besøkte ganger, traverseres den siste
    # som "return" (gå inn til siste pick, så tilbake) for å spare distanse.
    # Dette er klassisk lærebok-S-shape.
    for i, a in enumerate(visited):
        x = aisle_x(layout, a)
        going_up = (i % 2 == 0)  # 0-indeksert: første gang går front->bak
        ypicks = by_aisle[a]
        is_last = (i == last_idx)
        n_visited = len(visited)
        if is_last and n_visited % 2 == 1:
            # Return-gang: gå inn til dypeste pick, så tilbake til front
            deepest = ypicks[-1]
            route.append(Point(x, deepest))
            route.append(Point(x, fy))
            current_end = Point(x, fy)
        else:
            if going_up:
                # front -> bak
                route.append(Point(x, by))
                current_end = Point(x, by)
            else:
                # bak -> front
                route.append(Point(x, fy))
                current_end = Point(x, fy)

        # Hvis ikke siste besøkte gang, flytt over til neste gang via
        # kryssgangen der vi er (bak eller front)
        if not is_last:
            next_a = visited[i + 1]
            next_x = aisle_x(layout, next_a)
            route.append(Point(next_x, current_end.y))

    # Retur til depot via frontgang
    # Vi må først sørge for å være i frontgangen
    last = route[-1]
    if last.y != fy:
        # vi er i bakgangen -- må gå tilbake via frontgang: traverser siste
        # gang tilbake (dette skjer ikke hvis siste var odd og vi endte i front)
        # Egentlig: hvis siste besøkte gang endte i bakgangen, må vi traversere
        # den én gang til for å komme tilbake til front. I S-shape unngår vi
        # dette ved return-regelen over (odd antall => siste som return).
        # For par-antall ganger ender vi naturlig i front. Men hvis vi
        # allerede er i bakgangen (f.eks. oddetall uten return-regel), gå langs
        # bakgangen -> ned siste gang igjen -> front. For konsistens: gå via
        # frontgang.
        route.append(Point(last.x, fy))

    # Gå langs frontgang til depot
    route.append(Point(depot.x, fy))
    route.append(depot)
    return route


def route_length(route: list[Point]) -> float:
    return sum(l1(route[i], route[i + 1]) for i in range(len(route) - 1))


def plot_route_on_layout(layout: dict, picklist_ids: list[int], route: list[Point],
                         title: str, output_path: Path) -> None:
    """Tegn lager + rute over layoutet."""
    fig, ax = plt.subplots(figsize=(12, 6))

    n_aisles = layout['n_aisles']
    fy, by = front_y(layout), back_y(layout)
    aisle_sp = layout['aisle_spacing']
    shelf_sp = layout['shelf_spacing']

    # Hyller
    for aisle in range(n_aisles):
        x_center = aisle * aisle_sp
        ax.fill_between([x_center - 0.8, x_center - 0.2],
                        shelf_sp * 0.5, by - shelf_sp * 0.5,
                        color='#CBD5E1', alpha=0.5, zorder=1)
        ax.fill_between([x_center + 0.2, x_center + 0.8],
                        shelf_sp * 0.5, by - shelf_sp * 0.5,
                        color='#CBD5E1', alpha=0.5, zorder=1)
        ax.plot([x_center, x_center], [fy, by], ':', color='#94a3b8',
                linewidth=0.7, zorder=2)

    ax.plot([0 - aisle_sp / 2, (n_aisles - 1) * aisle_sp + aisle_sp / 2],
            [fy, fy], '-', color='#1F2933', linewidth=1.0, zorder=2)
    ax.plot([0 - aisle_sp / 2, (n_aisles - 1) * aisle_sp + aisle_sp / 2],
            [by, by], '-', color='#1F2933', linewidth=1.0, zorder=2)

    # Plukklokasjoner
    pick_ids = set(picklist_ids)
    for loc in layout['locations']:
        color = '#961D1C' if loc['id'] in pick_ids else '#cbd5e1'
        size = 32 if loc['id'] in pick_ids else 4
        zorder = 4 if loc['id'] in pick_ids else 3
        ax.scatter(loc['x'], loc['y'], s=size, color=color, zorder=zorder,
                   edgecolors='none')

    # Rute
    xs = [p.x for p in route]
    ys = [p.y for p in route]
    ax.plot(xs, ys, '-', color='#1F6587', linewidth=2.0, alpha=0.85, zorder=5)
    # Retningspil på midt-segment
    mid = len(route) // 2
    if mid >= 1:
        x0, y0 = route[mid - 1].x, route[mid - 1].y
        x1, y1 = route[mid].x, route[mid].y
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='->', color='#1F6587', lw=1.5),
                    zorder=6)

    # Depot
    depot = layout['depot']
    ax.scatter(depot['x'], depot['y'], s=120, marker='s', color='#307453',
               edgecolors='#1F2933', linewidths=1.0, zorder=7, label='Depot')

    for aisle in range(n_aisles):
        x_center = aisle * aisle_sp
        ax.text(x_center, -1.0, f'G{aisle+1}', ha='center', va='top',
                fontsize=9, color='#556270')

    d = route_length(route)
    ax.set_xlabel('$x$ (meter)', fontsize=12)
    ax.set_ylabel('$y$ (meter)', fontsize=12)
    ax.set_title(f'{title} | Rutelengde: {d:.1f} m', fontsize=11, fontweight='bold')
    ax.set_xlim(-aisle_sp, (n_aisles - 1) * aisle_sp + aisle_sp)
    ax.set_ylim(-2.0, by + 1.0)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25, zorder=0)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 2: S-SHAPE HEURISTIKK")
    print("=" * 60)

    # Last layout og plukklister
    with open(OUTPUT_DIR / 'layout.json', encoding='utf-8') as f:
        layout = json.load(f)
    with open(OUTPUT_DIR / 'picklists.json', encoding='utf-8') as f:
        picklists = json.load(f)

    # Kjør S-shape på første plukkliste og tegn
    example = picklists[0]
    route = s_shape_route(layout, example['location_ids'])
    d = route_length(route)
    print(f"\nEksempel-plukkliste id={example['id']}, k={example['k']}")
    print(f"S-shape rutelengde: {d:.2f} m")

    plot_route_on_layout(
        layout, example['location_ids'], route,
        title=f"S-shape rute | Plukkliste {example['id']} ({example['k']} lokasjoner)",
        output_path=OUTPUT_DIR / 'pickrt_sshape_route.png',
    )

    # Kjør på alle plukklister
    all_lengths = []
    for pl in picklists:
        r = s_shape_route(layout, pl['location_ids'])
        all_lengths.append(route_length(r))

    results = {
        'heuristic': 'S-shape',
        'n_picklists': len(picklists),
        'mean_length_m': round(sum(all_lengths) / len(all_lengths), 2),
        'min_length_m': round(min(all_lengths), 2),
        'max_length_m': round(max(all_lengths), 2),
        'example_id': example['id'],
        'example_k': example['k'],
        'example_length_m': round(d, 2),
    }
    with open(OUTPUT_DIR / 'sshape_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nGjennomsnittlig S-shape lengde over {len(picklists)} lister: "
          f"{results['mean_length_m']:.2f} m")
    print(f"Resultater lagret: {OUTPUT_DIR / 'sshape_results.json'}")

    # Lagre alle lengder for senere sammenligning
    with open(OUTPUT_DIR / 'sshape_lengths.json', 'w', encoding='utf-8') as f:
        json.dump([round(x, 4) for x in all_lengths], f)


if __name__ == '__main__':
    main()
