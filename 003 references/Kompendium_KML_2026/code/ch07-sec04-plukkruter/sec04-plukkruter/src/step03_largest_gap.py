"""
Steg 3: Largest-gap heuristikk
==============================
Largest-gap er en forbedret plukkruteheuristikk for parallell-gang-lagre
(Hall 1993). Regelen er:

  - Den første og siste besøkte gangen traverseres helt (front -> bak).
  - For hver mellom-gang identifiseres det *største gapet* blant gapene:
      g_front  = y[0] - y_front           (fra frontgang til første plukk)
      g_i      = y[i] - y[i-1]             (mellom plukk i-1 og i)
      g_back   = y_back - y[-1]            (fra siste plukk til bakgang)
    Hvis største gap er g_front   -> besøk gangen kun fra baksiden (return fra bak)
    Hvis største gap er g_back    -> besøk gangen kun fra frontsiden (return fra front)
    Hvis største gap er et mellom-gap -> besøk gangen fra begge sider (split)

  - Sammenkobling mellom ganger skjer i front- og bakgangen. Ruten kan ses
    som en *loop*: gå fra depot langs frontgangen og besøk frontside-segmentene
    underveis; full-traverser siste gang; gå tilbake langs bakgangen og besøk
    baksidesegmentene; full-traverser første gang nedover; tilbake til depot.

Totalkostnaden består av:
  - Sum av gangkostnader per besøkt gang (traverse eller return eller split)
  - Horisontal koblingskost: (siste - første) * aisle_sp i hver kryssgang brukt.
    Klassisk largest-gap bruker frontgangen fra første til siste besøkte gang
    én gang (for frontsideoperasjoner) og bakgangen tilsvarende én gang.

Denne implementasjonen beregner total rutelengde korrekt og bygger en
eksplisitt Euler-tur for visualisering.
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


def _aisle_plan_lg(ypicks: list[float], fy: float, by: float) -> dict:
    """Largest-gap-plan for en mellom-gang.

    Returnerer dict med:
      - 'front_to': float eller None (hvor langt ned gangen frontside-besøket går)
      - 'back_to':  float eller None (hvor langt ned gangen baksidebesøket går)
    """
    n = len(ypicks)
    gaps = [(ypicks[0] - fy, 'front_edge')]
    for i in range(1, n):
        gaps.append((ypicks[i] - ypicks[i - 1], 'mid', i))
    gaps.append((by - ypicks[-1], 'back_edge'))

    # sort desc by gap length
    gaps.sort(key=lambda g: g[0], reverse=True)
    g = gaps[0]
    kind = g[1]
    if kind == 'front_edge':
        return {'front_to': None, 'back_to': ypicks[0]}
    if kind == 'back_edge':
        return {'front_to': ypicks[-1], 'back_to': None}
    # mid-gap: g = (gap, 'mid', i) med ypicks[i-1] og ypicks[i]
    i = g[2]
    y_lo = ypicks[i - 1]
    y_hi = ypicks[i]
    return {'front_to': y_lo, 'back_to': y_hi}


def largest_gap_length(layout: dict, picklist_ids: list[int]) -> float:
    """Beregn rutelengde for largest-gap direkte (uten å bygge eksplisitt rute)."""
    by_aisle = aisle_picks(layout, picklist_ids)
    if not by_aisle:
        return 0.0

    visited = sorted(by_aisle.keys())
    fy, by = front_y(layout), back_y(layout)
    aisle_len = by - fy
    aisle_sp = layout['aisle_spacing']
    depot = depot_point(layout)

    # Kostnad i gangene
    aisle_cost = 0.0
    if len(visited) == 1:
        # Én gang besøkt: return fra front
        a = visited[0]
        deepest = by_aisle[a][-1]
        aisle_cost = 2 * (deepest - fy)
        horiz_cost = 2 * abs(aisle_x(layout, a) - depot.x)
        return aisle_cost + horiz_cost

    # Første og siste gang: full traversering (hver: aisle_len)
    aisle_cost += aisle_len  # første gang front -> bak
    aisle_cost += aisle_len  # siste gang bak -> front

    # Mellomganger: følg largest-gap regelen
    for a in visited[1:-1]:
        plan = _aisle_plan_lg(by_aisle[a], fy, by)
        if plan['front_to'] is not None:
            aisle_cost += 2 * (plan['front_to'] - fy)
        if plan['back_to'] is not None:
            aisle_cost += 2 * (by - plan['back_to'])

    # Horisontal koblingskost:
    # Ruten har struktur:
    #   depot -> frontgang x_first -> frontgang frem til x_last (span) ->
    #   siste gangs full traversering (vertikal, i aisle_cost) ->
    #   bakgang fra x_last tilbake til x_first (span) ->
    #   første gangs full traversering (vertikal, i aisle_cost) ->
    #   frontgang fra x_first tilbake til depot.
    # Horisontal totalt = 2 * |x_first - depot.x| + 2 * span
    span = (visited[-1] - visited[0]) * aisle_sp
    depot_to_first = 2 * abs(aisle_x(layout, visited[0]) - depot.x)
    horiz_cost = 2 * span + depot_to_first
    return aisle_cost + horiz_cost


def largest_gap_route(layout: dict, picklist_ids: list[int]) -> list[Point]:
    """Bygg en eksplisitt Euler-tur som tilsvarer largest-gap rutekostnaden."""
    by_aisle = aisle_picks(layout, picklist_ids)
    if not by_aisle:
        return [depot_point(layout), depot_point(layout)]

    visited = sorted(by_aisle.keys())
    fy, by = front_y(layout), back_y(layout)
    depot = depot_point(layout)

    if len(visited) == 1:
        a = visited[0]
        x = aisle_x(layout, a)
        deepest = by_aisle[a][-1]
        return [depot, Point(x, fy), Point(x, deepest), Point(x, fy),
                Point(depot.x, fy), depot]

    # Plan for hver mellomgang
    plans = {a: _aisle_plan_lg(by_aisle[a], fy, by) for a in visited[1:-1]}

    route: list[Point] = [depot]
    x_first = aisle_x(layout, visited[0])
    x_last = aisle_x(layout, visited[-1])

    # 1) Depot -> front av første gang (via frontgangen)
    route.append(Point(x_first, fy))

    # 2) Frontside-pass: gå langs frontgangen fra første til siste gang.
    #    - For første gang: stikk ned til dypeste plukk (midlertidig; vi
    #      traverserer den helt på slutten) -- men klassisk largest-gap
    #      full-traverserer den allerede her. Vi gjør det på slutten for
    #      tydelighet.
    #    - For hver mellomgang: stikk ned til front_to (hvis != None) og opp.
    #    - For siste gang: full traverse (front -> bak). Etter dette er vi
    #      i bakgangen.
    for idx, a in enumerate(visited):
        x = aisle_x(layout, a)
        if route[-1].x != x or route[-1].y != fy:
            # Flytt til (x, fy)
            if route[-1].y != fy:
                # burde ikke skje i dette passet
                pass
            route.append(Point(x, fy))

        if idx == 0:
            # Første gang: vi full-traverserer her (front -> bak), slik at vi
            # kan ta bakside-passet direkte etter.
            route.append(Point(x, by))
            current_y = by
            break  # etter full traversering av første gang fortsetter vi
            # bakside-passet uten å gjøre frontside-pass på mellomganger.
            # Vi må håndtere mellomganger både fra front og bak. Den
            # klassiske strukturen krever at vi gjør frontside-passet FØR
            # første gang traverseres. Men da må vi gå depot -> frontgang -> alle
            # mellomganger frontside -> siste gang full-traverse -> bakgang
            # tilbake -> mellomganger bakside -> første gang bak -> front -> depot.

    # Restart med korrekt rekkefølge (basert på analyse over)
    route = [depot]
    # 1) Depot -> frontgang ved første gang (men vi sparer første gang til slutt)
    route.append(Point(x_first, fy))

    # 2) Frontside-pass: gå fra første gangs x til siste gangs x langs frontgangen.
    #    For hver mellomgang: stikk ned til front_to og tilbake.
    #    Første gang dekkes ikke her (spares til slutt); siste gang
    #    full-traverseres på slutten av dette passet.
    current_x = x_first
    for a in visited[1:-1]:
        x = aisle_x(layout, a)
        plan = plans[a]
        if plan['front_to'] is not None:
            # gå horisontalt til x
            route.append(Point(x, fy))
            route.append(Point(x, plan['front_to']))
            route.append(Point(x, fy))
            current_x = x

    # Gå til siste gang i frontgangen
    route.append(Point(x_last, fy))
    # Full traverse siste gang (front -> bak)
    route.append(Point(x_last, by))

    # 3) Bakside-pass: gå fra siste til første gangs x langs bakgangen.
    #    For hver mellomgang: stikk ned til back_to og tilbake.
    for a in reversed(visited[1:-1]):
        x = aisle_x(layout, a)
        plan = plans[a]
        if plan['back_to'] is not None:
            route.append(Point(x, by))
            route.append(Point(x, plan['back_to']))
            route.append(Point(x, by))

    # Gå til første gang i bakgangen
    route.append(Point(x_first, by))
    # Full traverse første gang (bak -> front)
    route.append(Point(x_first, fy))

    # 4) Tilbake til depot via frontgangen
    route.append(Point(depot.x, fy))
    route.append(depot)
    return route


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 3: LARGEST-GAP HEURISTIKK")
    print("=" * 60)

    with open(OUTPUT_DIR / 'layout.json', encoding='utf-8') as f:
        layout = json.load(f)
    with open(OUTPUT_DIR / 'picklists.json', encoding='utf-8') as f:
        picklists = json.load(f)

    example = picklists[0]
    route = largest_gap_route(layout, example['location_ids'])
    d_route = route_length(route)
    d_calc = largest_gap_length(layout, example['location_ids'])
    print(f"\nEksempel-plukkliste id={example['id']}, k={example['k']}")
    print(f"Largest-gap lengde (rute):   {d_route:.2f} m")
    print(f"Largest-gap lengde (formel): {d_calc:.2f} m")

    plot_route_on_layout(
        layout, example['location_ids'], route,
        title=f"Largest-gap rute | Plukkliste {example['id']} ({example['k']} lokasjoner)",
        output_path=OUTPUT_DIR / 'pickrt_largestgap_route.png',
    )

    all_lengths = []
    for pl in picklists:
        L = largest_gap_length(layout, pl['location_ids'])
        all_lengths.append(L)

    results = {
        'heuristic': 'Largest-gap',
        'n_picklists': len(picklists),
        'mean_length_m': round(sum(all_lengths) / len(all_lengths), 2),
        'min_length_m': round(min(all_lengths), 2),
        'max_length_m': round(max(all_lengths), 2),
        'example_id': example['id'],
        'example_k': example['k'],
        'example_length_m': round(d_calc, 2),
    }
    with open(OUTPUT_DIR / 'largestgap_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nGjennomsnittlig Largest-gap lengde over {len(picklists)} lister: "
          f"{results['mean_length_m']:.2f} m")
    print(f"Resultater lagret: {OUTPUT_DIR / 'largestgap_results.json'}")

    with open(OUTPUT_DIR / 'largestgap_lengths.json', 'w', encoding='utf-8') as f:
        json.dump([round(x, 4) for x in all_lengths], f)


if __name__ == '__main__':
    main()
