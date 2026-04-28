"""
Felles hjelpefunksjoner for plukkruteheuristikker.

Geometrimodell
--------------
Lageret består av N_AISLES parallelle ganger. En rute foregår kun i gangene
og i front-/bakkryssgangen. Vi antar at plukkeren kan gå fra plukkpunkt til
samme x-koordinat som gangmidten med null ekstra avstand (side-til-gang er
innebygget i hylleavstanden). Avstandsfunksjonen er dermed L1 på en graf
der rutenettet består av:
  - Vertikale kanter langs hver gang (x = a*AISLE_SPACING)
  - Horisontale kanter langs frontkryssgangen (y = FRONT_Y)
  - Horisontale kanter langs bakkryssgangen (y = BACK_Y)

Gang-funksjoner
---------------
- aisle_picks(layout, picklist_ids) grupperer plukklokasjoner per gang med
  y-koordinater per gang.
- route_length(layout, sequence) regner total rutelengde gitt en eksplisitt
  sekvens av fysiske punkter (liste av (x, y)-tupler). Avstanden mellom to
  punkter i samme gang er |y1 - y2|; mellom punkter i ulike ganger må
  ruten via front- eller bakkryssgang og velger minste av de to.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    x: float
    y: float


def aisle_picks(layout: dict, picklist_ids: list[int]) -> dict[int, list[float]]:
    """Grupper y-koordinater per gang-indeks for en plukkliste.

    Returnerer et dict som mapper aisle -> sortert liste av y-verdier.
    """
    by_aisle: dict[int, list[float]] = {}
    locs = layout['locations']
    loc_by_id = {loc['id']: loc for loc in locs}
    for pid in picklist_ids:
        loc = loc_by_id[pid]
        by_aisle.setdefault(loc['aisle'], []).append(loc['y'])
    for a in by_aisle:
        by_aisle[a].sort()
    return by_aisle


def aisle_x(layout: dict, aisle: int) -> float:
    return aisle * layout['aisle_spacing']


def depot_point(layout: dict) -> Point:
    d = layout['depot']
    return Point(d['x'], d['y'])


def front_y(layout: dict) -> float:
    return float(layout['front_y'])


def back_y(layout: dict) -> float:
    return float(layout['back_y'])


def l1(p1: Point, p2: Point) -> float:
    return abs(p1.x - p2.x) + abs(p1.y - p2.y)


def path_length(points: list[Point]) -> float:
    """Total L1-distanse gjennom en sekvens av punkter."""
    return sum(l1(points[i], points[i + 1]) for i in range(len(points) - 1))


def aisle_top_bottom(ypicks: list[float]) -> tuple[float, float]:
    return ypicks[0], ypicks[-1]


def largest_gap_in_aisle(ypicks: list[float], front: float, back: float) -> float:
    """Beregn største gap i en gang, inkludert gap fra front til første pick og
    fra siste pick til bakkant. Returnerer lengden av det største gapet.
    """
    if not ypicks:
        return 0.0
    gaps = []
    # gap foran
    gaps.append(ypicks[0] - front)
    # mellomliggende gap mellom etterfølgende picks
    for i in range(1, len(ypicks)):
        gaps.append(ypicks[i] - ypicks[i - 1])
    # gap bak
    gaps.append(back - ypicks[-1])
    return max(gaps)


def traverse_full_aisle_length(layout: dict) -> float:
    """Lengden på full traversering av en gang (front til bak)."""
    return back_y(layout) - front_y(layout)
