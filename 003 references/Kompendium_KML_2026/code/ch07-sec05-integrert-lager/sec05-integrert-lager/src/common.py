"""
Felles hjelpefunksjoner for det integrerte lagereksempelet.

Geometri
--------
Lageret bestaar av N_AISLES parallelle ganger. Hver gang har hoyde
(BACK_Y - FRONT_Y) og er delt i to sider (venstre/hoyre reol) med plukk-
lokasjoner pa 10 y-niveer per side per gang.

Ruten foregaar i gangene og krysser via front- eller bakkryssgangen.
Avstand maales i L1 (manhattan) paa grafen definert under.

Fargevalg (infografikk)
-----------------------
Vi bruker bokens farger:
  s1 fill #8CC8E5, stroke #1F6587 (primary)
  s2 fill #97D4B7, stroke #307453 (secondary)
  s3 fill #F6BA7C, stroke #9C540B
  s4 fill #BD94D7, stroke #5A2C77 (accent)
  s5 fill #ED9F9E, stroke #961D1C
  ink #1F2933, inkmuted #556270, rule #CBD5E1
"""

from __future__ import annotations

import numpy as np

# Farger fra bokens tema
COL_INK = "#1F2933"
COL_INKMUTED = "#556270"
COL_RULE = "#CBD5E1"
COL_PRIMARY = "#1F6587"
COL_SECONDARY = "#307453"
COL_ACCENT = "#5A2C77"

PALETTE_FILL = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
PALETTE_STROKE = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]


def largest_gap_in_aisle(ypicks, front, back):
    """Storste gap i en gang (fra front til forste pick, mellom picks, fra siste pick til bak)."""
    if not ypicks:
        return 0.0
    ys = sorted(ypicks)
    gaps = [ys[0] - front]
    for i in range(1, len(ys)):
        gaps.append(ys[i] - ys[i - 1])
    gaps.append(back - ys[-1])
    return max(gaps)


def largest_gap_route_length(picks_by_aisle, layout):
    """Beregn total rutelengde for largest-gap-heuristikken.

    picks_by_aisle: dict {aisle_idx: [y_values]} for picks i denne batchen.
    layout: dict med aisle_spacing, front_y, back_y, depot (x,y).

    Strategi (klassisk largest-gap, Hall 1993 / De Koster 2007):
      - Forste og siste gang traverseres fullt (full traversal).
      - Mellomganger: plukkeren gaar inn fra front opp til storste gap
        og tilbake, deretter senere fra bak ned til storste gap og
        tilbake. Bare den storste gap-seksjonen i gangen blir ikke
        traversert.
      - Returnerer (total_lengde, sekvens_av_punkter).
    """
    front = float(layout["front_y"])
    back = float(layout["back_y"])
    sp = float(layout["aisle_spacing"])
    depot = layout["depot"]

    aisles = sorted(picks_by_aisle.keys())
    if not aisles:
        return 0.0, [(depot["x"], depot["y"])]

    def ax(a):
        return a * sp

    aisle_len = back - front

    # Hvis bare en gang: ga opp til hoyeste pick, tilbake til front
    if len(aisles) == 1:
        a = aisles[0]
        x = ax(a)
        ys = sorted(picks_by_aisle[a])
        pts = [(depot["x"], depot["y"]), (x, front), (x, ys[-1]), (x, front),
               (depot["x"], depot["y"])]
        total = (
            abs(x - depot["x"]) + abs(front - depot["y"])
            + (ys[-1] - front) * 2
            + abs(x - depot["x"]) + abs(front - depot["y"])
        )
        return total, pts

    # Total for forste+siste gang: full traversering = 2 x aisle_len
    # Mellomganger: 2 x (aisle_len - max_gap)
    # Pluss kryssgang-bevegelse.
    total = 0.0
    points = [(depot["x"], depot["y"])]

    first_a = aisles[0]
    last_a = aisles[-1]

    # Gang 1: gaa fra depot til forste gangs front, traverser til bak
    points.append((ax(first_a), front))
    total += abs(ax(first_a) - depot["x"]) + abs(front - depot["y"])
    points.append((ax(first_a), back))
    total += aisle_len

    # Mellomganger: fra bak, ga inn til storste gap fra oven (ta picks
    # ovenfor), tilbake til bak. Senere kommer vi inn fra front (paa
    # returen) og tar picks nedenfor. Men for klassisk largest-gap er
    # strategien enklere: vi tar begge sider i samme passering ved a
    # entre fra bak, ga ned til storste gap, tilbake opp; siden entre
    # igjen fra front fra siste gang nedover.

    # Vi implementerer den todelte varianten:
    #   Forste passering: fra bak-kryssgangen ned gjennom mellomganger
    #     til siste gang (traverser siste helt, ut pa front).
    #   Andre passering: fra front-kryssgangen tilbake til forste gang,
    #     denne gangen henter vi picks nedenfor largest gap.

    # Passering 1 (paa bakkryssgangen): inn fra bak, ned til nederste
    # pick ovenfor storste gap, og tilbake til bak.
    for i in range(1, len(aisles) - 1):
        a = aisles[i]
        prev_a = aisles[i - 1]
        x = ax(a)
        # Ga langs bakkryssgangen
        points.append((x, back))
        total += abs(x - ax(prev_a))

        ys = sorted(picks_by_aisle[a])
        gaps = [ys[0] - front]
        for j in range(1, len(ys)):
            gaps.append(ys[j] - ys[j - 1])
        gaps.append(back - ys[-1])
        max_gap = max(gaps)
        gap_idx = gaps.index(max_gap)

        if gap_idx == len(gaps) - 1:
            # Storste gap er mellom siste pick og back -- vi ma ga inn
            # fra bak helt ned til ys[0] for a hente alle picks
            bot_visit = ys[0]
            points.append((x, bot_visit))
            total += back - bot_visit
            points.append((x, back))
            total += back - bot_visit
        elif gap_idx == 0:
            # Storste gap er mellom front og ys[0] -- hele gangen
            # plukkes fra bak-siden ned til ys[0]. Da er det bedre a
            # bare ga hele veien ned med de farre picks.
            bot_visit = ys[0]
            points.append((x, bot_visit))
            total += back - bot_visit
            points.append((x, back))
            total += back - bot_visit
        else:
            # Storste gap er mellom ys[gap_idx - 1] og ys[gap_idx] --
            # vi gaar fra bak ned til ys[gap_idx] og tilbake
            bot_visit = ys[gap_idx]
            points.append((x, bot_visit))
            total += back - bot_visit
            points.append((x, back))
            total += back - bot_visit

    # Ga til siste gang langs bakkryssgangen og traverser siste gang fullt
    # (fra bak til front)
    x_last = ax(last_a)
    # Bevegelse langs kryssgangen fra forrige aisle til siste
    prev_x = ax(aisles[-2]) if len(aisles) >= 2 else ax(first_a)
    points.append((x_last, back))
    total += abs(x_last - prev_x)
    points.append((x_last, front))
    total += aisle_len

    # Passering 2 (paa frontkryssgangen): hent picks nedenfor largest-gap
    # fra front-siden i hver mellomgang i omvendt rekkefolge
    cur_x = x_last
    for i in range(len(aisles) - 2, 0, -1):
        a = aisles[i]
        x = ax(a)
        points.append((x, front))
        total += abs(cur_x - x)
        cur_x = x

        ys = sorted(picks_by_aisle[a])
        gaps = [ys[0] - front]
        for j in range(1, len(ys)):
            gaps.append(ys[j] - ys[j - 1])
        gaps.append(back - ys[-1])
        max_gap = max(gaps)
        gap_idx = gaps.index(max_gap)

        if gap_idx == 0:
            # Storste gap er mellom front og ys[0] -- passering 1 tok
            # allerede alle picks fra bak-siden; vi trenger ikke ga inn
            # her.
            pass
        elif gap_idx == len(gaps) - 1:
            # Storste gap er mellom ys[-1] og back -- passering 1 tok
            # allerede alle picks fra bak-siden ned til ys[0]. Vi
            # trenger ikke ga inn her heller.
            pass
        else:
            # Topp-punktet fra front-siden er ys[gap_idx - 1]
            top_visit = ys[gap_idx - 1]
            points.append((x, top_visit))
            total += top_visit - front
            points.append((x, front))
            total += top_visit - front

    # Tilbake til depot
    # Ga fra cur_x til depot langs front
    points.append((depot["x"], front))
    total += abs(cur_x - depot["x"])
    points.append((depot["x"], depot["y"]))
    total += abs(front - depot["y"])

    return total, points


def s_shape_route_length(picks_by_aisle, layout):
    """Enkel S-shape-rute: traverser hver gang med picks helt (eller returner hvis bare en gang)."""
    front = layout["front_y"]
    back = layout["back_y"]
    sp = layout["aisle_spacing"]
    depot = layout["depot"]

    aisles = sorted(picks_by_aisle.keys())
    if not aisles:
        return 0.0, [(depot["x"], depot["y"])]

    points = [(depot["x"], depot["y"])]
    total = 0.0
    first_x = aisles[0] * sp
    points.append((first_x, front))
    total += abs(first_x - depot["x"]) + abs(front - depot["y"])

    cur_y = front
    for i, a in enumerate(aisles):
        x = a * sp
        if i > 0:
            # Beveg langs kryssgang til ny gang
            points.append((x, cur_y))
            total += abs(x - points[-2][0])

        # Avgjor hvilken retning vi skal ga (opp/ned alternerende)
        if cur_y == front:
            points.append((x, back))
            total += back - front
            cur_y = back
        else:
            points.append((x, front))
            total += back - front
            cur_y = front

    # Tilbake til depot
    points.append((depot["x"], cur_y))
    total += abs(points[-2][0] - depot["x"])
    if cur_y != depot["y"]:
        points.append((depot["x"], depot["y"]))
        total += abs(cur_y - depot["y"])
    return total, points


def kmedoids_or_fallback(features, k, rng, max_iter=50):
    """Enkel k-medoids (PAM-style greedy + swap) uten eksterne avhengigheter.

    features: (n, d) numpy-array.
    k: antall medoider.
    Returnerer (labels, medoid_indices).

    Ved k >= n eller k <= 0 returnerer vi en triviell tilordning.
    """
    n = features.shape[0]
    if k <= 0:
        return np.zeros(n, dtype=int), np.array([], dtype=int)
    if k >= n:
        return np.arange(n), np.arange(n)

    # Parvise L2-avstander
    diff = features[:, None, :] - features[None, :, :]
    dists = np.sqrt((diff ** 2).sum(axis=2))

    # k-medoids++-lik initialisering: velg forst en tilfeldig, deretter
    # velg de som er langt unna naermeste eksisterende medoid
    medoids = [int(rng.integers(n))]
    for _ in range(1, k):
        min_d = dists[:, medoids].min(axis=1)
        probs = min_d / max(min_d.sum(), 1e-12)
        chosen = int(rng.choice(n, p=probs))
        medoids.append(chosen)
    medoids = np.array(medoids, dtype=int)

    for _ in range(max_iter):
        # Tildel til naermeste medoid
        labels = np.argmin(dists[:, medoids], axis=1)
        new_medoids = medoids.copy()
        for j in range(k):
            members = np.where(labels == j)[0]
            if len(members) == 0:
                continue
            # Velg medlemmet med minst total intern-avstand
            sub = dists[np.ix_(members, members)]
            best = members[np.argmin(sub.sum(axis=1))]
            new_medoids[j] = best
        if np.array_equal(new_medoids, medoids):
            break
        medoids = new_medoids

    labels = np.argmin(dists[:, medoids], axis=1)
    return labels, medoids


def random_route_length(picks_by_aisle, layout, rng):
    """Naiv rute: besok hver gang i tilfeldig rekkefolge, traverser fullt."""
    aisles = list(picks_by_aisle.keys())
    rng.shuffle(aisles)
    # Samme struktur som s_shape, bare tilfeldig rekkefolge
    shuffled = {a: picks_by_aisle[a] for a in aisles}
    return s_shape_route_length(shuffled, layout)
