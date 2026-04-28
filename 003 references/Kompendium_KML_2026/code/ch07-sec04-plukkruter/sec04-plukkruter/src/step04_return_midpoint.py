"""
Steg 4: Return og Midpoint heuristikker
=======================================
- Return: Plukkeren går inn i hver besøkt gang fra frontsiden, ned til
  dypeste plukk, og tilbake til frontgangen. Alle bevegelser mellom ganger
  skjer i frontgangen. Ingen bruk av bakgangen.

- Midpoint: Lageret deles i to halvdeler ved midtpunktet y = (fy+by)/2.
  Plukk i nedre halvdel besøkes fra frontsiden (return), plukk i øvre
  halvdel besøkes fra baksiden (return ovenfra). Den første og siste
  besøkte gangen traverseres helt.
"""

import json
from pathlib import Path

from common import (
    Point,
    aisle_picks,
    aisle_x,
    back_y,
    depot_point,
    front_y,
)
from step02_s_shape import plot_route_on_layout, route_length

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def return_route(layout: dict, picklist_ids: list[int]) -> list[Point]:
    """Return-heuristikk: alle ganger besøkes fra frontsiden."""
    by_aisle = aisle_picks(layout, picklist_ids)
    if not by_aisle:
        return [depot_point(layout), depot_point(layout)]

    visited = sorted(by_aisle.keys())
    fy = front_y(layout)
    depot = depot_point(layout)

    route: list[Point] = [depot]
    for a in visited:
        x = aisle_x(layout, a)
        deepest = by_aisle[a][-1]
        route.append(Point(x, fy))
        route.append(Point(x, deepest))
        route.append(Point(x, fy))
    route.append(Point(depot.x, fy))
    route.append(depot)
    return route


def midpoint_route(layout: dict, picklist_ids: list[int]) -> list[Point]:
    """Midpoint-heuristikk.

    - Første og siste besøkte gang: full traversering (for å komme seg til
      bakgangen og tilbake).
    - Mellomganger: plukk i nedre halvdel (y <= midpoint) besøkes fra
      frontsiden (return), plukk i øvre halvdel (y > midpoint) besøkes fra
      baksiden (return).
    """
    by_aisle = aisle_picks(layout, picklist_ids)
    if not by_aisle:
        return [depot_point(layout), depot_point(layout)]

    visited = sorted(by_aisle.keys())
    fy, by = front_y(layout), back_y(layout)
    midy = (fy + by) / 2
    depot = depot_point(layout)

    if len(visited) == 1:
        a = visited[0]
        x = aisle_x(layout, a)
        deepest = by_aisle[a][-1]
        return [depot, Point(x, fy), Point(x, deepest), Point(x, fy),
                Point(depot.x, fy), depot]

    route: list[Point] = [depot]
    # Første gang: full traversering (front -> bak)
    a0 = visited[0]
    x0 = aisle_x(layout, a0)
    route.append(Point(x0, fy))
    route.append(Point(x0, by))

    # Gå langs bakgangen og besøk øvre-halvdel-plukk i mellomganger
    for a in visited[1:-1]:
        x = aisle_x(layout, a)
        ypicks = by_aisle[a]
        upper = [y for y in ypicks if y > midy]
        if upper:
            grunneste = min(upper)  # dypeste fra baksiden = minste y i øvre halvdel
            if route[-1].y != by:
                route.append(Point(route[-1].x, by))
            route.append(Point(x, by))
            route.append(Point(x, grunneste))
            route.append(Point(x, by))

    # Siste gang: traverser bak -> front
    aL = visited[-1]
    xL = aisle_x(layout, aL)
    if route[-1].y != by:
        route.append(Point(route[-1].x, by))
    route.append(Point(xL, by))
    route.append(Point(xL, fy))

    # Gå tilbake langs frontgangen og besøk nedre-halvdel-plukk i mellomganger
    for a in reversed(visited[1:-1]):
        x = aisle_x(layout, a)
        ypicks = by_aisle[a]
        lower = [y for y in ypicks if y <= midy]
        if lower:
            dypeste = max(lower)
            if route[-1].y != fy:
                route.append(Point(route[-1].x, fy))
            route.append(Point(x, fy))
            route.append(Point(x, dypeste))
            route.append(Point(x, fy))

    # Tilbake til depot
    if route[-1].y != fy:
        route.append(Point(route[-1].x, fy))
    route.append(Point(depot.x, fy))
    route.append(depot)
    return route


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 4: RETURN OG MIDPOINT HEURISTIKKER")
    print("=" * 60)

    with open(OUTPUT_DIR / 'layout.json', encoding='utf-8') as f:
        layout = json.load(f)
    with open(OUTPUT_DIR / 'picklists.json', encoding='utf-8') as f:
        picklists = json.load(f)

    example = picklists[0]

    # Return
    ret_route = return_route(layout, example['location_ids'])
    ret_d = route_length(ret_route)
    print(f"\nEksempel-plukkliste id={example['id']}, k={example['k']}")
    print(f"Return rutelengde:    {ret_d:.2f} m")

    mid_route = midpoint_route(layout, example['location_ids'])
    mid_d = route_length(mid_route)
    print(f"Midpoint rutelengde:  {mid_d:.2f} m")

    plot_route_on_layout(
        layout, example['location_ids'], ret_route,
        title=f"Return-rute | Plukkliste {example['id']} ({example['k']} lokasjoner)",
        output_path=OUTPUT_DIR / 'pickrt_return_route.png',
    )
    plot_route_on_layout(
        layout, example['location_ids'], mid_route,
        title=f"Midpoint-rute | Plukkliste {example['id']} ({example['k']} lokasjoner)",
        output_path=OUTPUT_DIR / 'pickrt_midpoint_route.png',
    )

    # Over alle
    ret_lengths, mid_lengths = [], []
    for pl in picklists:
        r = return_route(layout, pl['location_ids'])
        m = midpoint_route(layout, pl['location_ids'])
        ret_lengths.append(route_length(r))
        mid_lengths.append(route_length(m))

    ret_res = {
        'heuristic': 'Return',
        'n_picklists': len(picklists),
        'mean_length_m': round(sum(ret_lengths) / len(ret_lengths), 2),
        'min_length_m': round(min(ret_lengths), 2),
        'max_length_m': round(max(ret_lengths), 2),
        'example_id': example['id'],
        'example_k': example['k'],
        'example_length_m': round(ret_d, 2),
    }
    mid_res = {
        'heuristic': 'Midpoint',
        'n_picklists': len(picklists),
        'mean_length_m': round(sum(mid_lengths) / len(mid_lengths), 2),
        'min_length_m': round(min(mid_lengths), 2),
        'max_length_m': round(max(mid_lengths), 2),
        'example_id': example['id'],
        'example_k': example['k'],
        'example_length_m': round(mid_d, 2),
    }
    with open(OUTPUT_DIR / 'return_results.json', 'w', encoding='utf-8') as f:
        json.dump(ret_res, f, indent=2, ensure_ascii=False)
    with open(OUTPUT_DIR / 'midpoint_results.json', 'w', encoding='utf-8') as f:
        json.dump(mid_res, f, indent=2, ensure_ascii=False)

    with open(OUTPUT_DIR / 'return_lengths.json', 'w', encoding='utf-8') as f:
        json.dump([round(x, 4) for x in ret_lengths], f)
    with open(OUTPUT_DIR / 'midpoint_lengths.json', 'w', encoding='utf-8') as f:
        json.dump([round(x, 4) for x in mid_lengths], f)

    print(f"\nReturn gjennomsnitt:   {ret_res['mean_length_m']:.2f} m")
    print(f"Midpoint gjennomsnitt: {mid_res['mean_length_m']:.2f} m")


if __name__ == '__main__':
    main()
