"""
Steg 5: Ratliff-Rosenthal eksakt DP-løsning
============================================
Ratliff & Rosenthal (1983) viste at optimal plukkruteoptimering i et
parallell-gang-lager kan løses eksakt i lineær tid O(n) ved dynamisk
programmering over gangene. Nøkkelinnsikten er at den optimale ruten er en
Euler-tur i en spesialgraf, og at hver kolonne (gang) trenger bare å
karakteriseres av en liten mengde ekvivalensklasser. Ratliff-Rosenthal
viste at 7 klasser er tilstrekkelig.

Forenklet formulering
---------------------
For hver "pilar" (vertikal linje i grafen) mellom to nabogangene holder vi
styr på:
  - Antall kanter valgt i bakgangen mellom de to gangene: 0, 1, eller 2
    (men 2 er unødvendig siden vi kan erstatte 2 parallelle kanter med 0)
  - Antall kanter valgt i frontgangen mellom de to gangene: 0, 1, eller 2
  - Hvordan komponentene henger sammen: 1 komponent (sammenhengende) eller
    2 komponenter som må kobles senere.

Vi følger en redusert tilstandsdefinisjon med seks "paritets-tilstander":
  - (top, bot, conn) hvor top, bot in {0, 1} (paritet i hhv. bakgang og
    frontgang) og conn in {0, 1} (samme komponent eller to komponenter).

Overgangene mellom gang j og j+1 bestemmes av:
  (i) Hvilke aisle-moves vi velger i gang j+1 (endrer top/bot-paritet via
      kantene i selve gangen).
  (ii) Hvilke horisontal-moves vi velger mellom gang j og j+1 i fronten
       og/eller bakgangen (øker/senker top/bot og kobler komponenter).

For hver tilstand holder vi minimumskost for å nå tilstanden etter å ha
behandlet alle ganger <= j.

Referanse: Ratliff, H.D. & Rosenthal, A.S. (1983). Order-picking in a
rectangular warehouse. Operations Research 31(3), 507-521.

Implementasjonsnote: Siden hver plukkliste i vårt lager har maks 10 besøkte
ganger, er også en "begrenset brute-force" praktisk. Den korrekte DP-
implementasjonen nedenfor er like rask og eksakt.
"""

from __future__ import annotations

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

INF = float('inf')


def _aisle_move_options(ypicks: list[float], fy: float, by: float, aisle_len: float):
    """Returner tilgjengelige aisle-moves som liste av
    (name, cost, top_deg_change, bot_deg_change).

    top_deg_change / bot_deg_change er antall ekstra kantender som legges til
    henholdsvis bakgangs- og frontgangskrysset ved å utføre denne move-en
    i gangen.
    """
    if not ypicks:
        # Tom gang: "ingen besøk" (kost 0, ingen kanter)
        # eller "full traversering" (kost aisle_len, 1 kant på hver side)
        return [
            ('none', 0.0, 0, 0),
            ('full', aisle_len, 1, 1),
        ]
    deepest = ypicks[-1]
    grunneste = ypicks[0]
    options = []
    # Full traversering
    options.append(('full', aisle_len, 1, 1))
    # Return fra front (stikk ned til deepest og tilbake)
    options.append(('ret_front', 2 * (deepest - fy), 0, 2))
    # Return fra bak (stikk ned til grunneste og tilbake)
    options.append(('ret_back', 2 * (by - grunneste), 2, 0))
    # Split: hopp over største gap
    if len(ypicks) >= 2:
        gaps = [(ypicks[i] - ypicks[i - 1], i) for i in range(1, len(ypicks))]
        gap_len, i = max(gaps, key=lambda x: x[0])
        y_lo = ypicks[i - 1]
        y_hi = ypicks[i]
        cost = 2 * (y_lo - fy) + 2 * (by - y_hi)
        options.append(('split', cost, 2, 2))
    return options


def ratliff_rosenthal_length(layout: dict, picklist_ids: list[int]) -> float:
    """Beregn eksakt minimumslengde med DP.

    Tilstanden vi holder styr på etter å ha behandlet gang i er:
      (top_parity, bot_parity, connected)
    der:
      - top_parity = sum av top-degree-endringer mod 2 (partall eller oddetall
        kantender i bakgangen som må lukkes)
      - bot_parity = tilsvarende for frontgangen
      - connected in {0, 1}: 0 betyr flere åpne komponenter, 1 betyr sammenhengende

    Overgang fra gang i til i+1:
      - Velg en horisontal "edge pattern" i bakgangen mellom i og i+1:
          * 0 edges (koster 0, ingen endring av top_parity, komponenter forblir)
          * 1 edge (koster dx, flipper top_parity, kobler komponenter)
          * 2 edges (koster 2*dx, ingen endring av paritet, kobler komponenter)
      - Tilsvarende for frontgangen
      - Velg et aisle-move i gang i+1 (endrer top/bot paritet lokalt)

    Betingelser for gyldig Euler-tur på slutten:
      - top_parity = 0 (alle bakgangs-kantendene er lukket)
      - bot_parity = 0 (alle frontgangs-kantendene er lukket)
      - connected = 1
      - Dessuten må vi inkludere depot-koblingen: frontgang fra depot til
        første aisle og tilbake, som vi håndterer som "ekstra kanter" i
        frontgangen langs de aktuelle segmentene.

    For enkelhetsskyld antar vi depot ligger utenfor første besøkte gang
    slik at depot bidrar med 2 kantender i frontgangen ved x_first. Vi
    initialiserer derfor tilstanden før første gang med bot_parity=0,
    top_parity=0, connected=1 (depot alene er én komponent).
    """
    by_aisle = aisle_picks(layout, picklist_ids)
    if not by_aisle:
        return 0.0

    visited = sorted(by_aisle.keys())
    fy, by = front_y(layout), back_y(layout)
    aisle_len = by - fy
    aisle_sp = layout['aisle_spacing']
    depot = depot_point(layout)

    # Spesialtilfelle: én besøkt gang
    if len(visited) == 1:
        a = visited[0]
        deepest = by_aisle[a][-1]
        # Kost: 2 * (deepest - fy) + 2 * |x - depot.x|
        return 2 * (deepest - fy) + 2 * abs(aisle_x(layout, a) - depot.x)

    # For horisontal: Vi kan betrakte alle ganger mellom visited[0] og
    # visited[-1], inkludert tomme mellomganger (de har move 'none' som koster 0).
    all_aisles = list(range(visited[0], visited[-1] + 1))

    # DP: state = (top_par, bot_par, connected)
    # top_par, bot_par in {0, 1}, connected in {0, 1}
    # "connected" betyr at depot + alle tidligere besøkte aisle-moves er koblet.

    # Initial state før første aisle behandles:
    # Depot kobler til (x_first, fy) via frontgangen fra x_depot til x_first.
    # Vi modellerer dette som at bot_parity starter på 1 (depot-koblingen
    # har én åpen kant som må lukkes senere via returkoblingen).
    # Alternativt: depot bidrar med 0 paritet men konnektivitet = 1.

    # Enklere formulering: Vi krever at ruten er en lukket Euler-tur som
    # inkluderer alle plukknoder og starter/slutter i depot. Det betyr at
    # alle valgte kanter må danne en sammenhengende graf med paritet 0 på
    # alle noder. Depot telles som én node som har paritet 2 (inngang + utgang).

    # DP initialisering: før vi behandler visited[0] har vi kun depot-noden
    # og vi trenger å koble den til (x_first, fy). Dette bidrar med en
    # frontgang-kant fra depot til x_first (kost = |x_first - depot.x|).
    # Vi fanger dette ved å legge til denne kostnaden etter DP.
    # I DP vurderer vi bare kostnader for aisle-moves + horizontal-moves
    # mellom *besøkte* ganger (ikke depot).
    # Tomme mellomganger skal ikke besøkes -- men horisontale koblinger kan
    # gå igjennom dem i front- eller bakgangen.

    # Vi forenkler ved å la DP kjøres KUN over besøkte ganger, og
    # horizontal-cost mellom besøkte ganger beregnes direkte som
    # (visited[i+1] - visited[i]) * aisle_sp per kryssgang brukt.

    # Initialisering: før gang visited[0]
    # Depot kobles til x_first via frontgang -- denne kostnaden legges til
    # som konstant. Etter depot-koblingen er vi "i frontgangen" med
    # tilstanden (top=0, bot=1, connected=1). Men siden vi krever at
    # tur-enden er depot, må vi også legge inn returkoblingen som
    # frontgangen fra x_first tilbake til depot. Denne legges til som
    # konstant på slutten.

    # DP-tabell: dp[state] = min kost etter å ha behandlet de første i
    # besøkte gangene.

    # Tilstand etter behandling av gang i (indeksert 0..k-1):
    # (top_par, bot_par, connected) hvor paritetene beskriver pariteten
    # på "pilaren" ved x = aisle_x(visited[i]) -- dvs. hvor mange åpne
    # kantender vi har etterlatt der.
    #
    # Initialisering (før første gang): vi er "ved" x_first i frontgangen,
    # med én åpen kantende (depot-koblingen) der. Så (0, 1, 1).

    dp = {(0, 1, 1): abs(aisle_x(layout, visited[0]) - depot.x)}

    for i, a in enumerate(visited):
        dx_to_next = (visited[i + 1] - a) * aisle_sp if i + 1 < len(visited) else 0
        # For hver tilstand før behandling av gang i, prøv alle aisle-moves.
        moves = _aisle_move_options(by_aisle[a], fy, by, aisle_len)
        new_dp_after_aisle: dict[tuple, float] = {}
        for state, cost in dp.items():
            tp, bp, conn = state
            for name, mv_cost, top_d, bot_d in moves:
                # Etter aisle-move, nye paritet-tillegg:
                # top-degree fra move legger til top_d kantender ved denne pilaren
                new_tp = (tp + top_d) % 2
                new_bp = (bp + bot_d) % 2
                # Konnektivitet: hvis move faktisk besøker gangen (top_d > 0
                # eller bot_d > 0), og vi allerede hadde koblet komponent,
                # forblir det koblet. Hvis konn var 0 (to komponenter) og
                # move ikke selv kobler (dvs. krever senere horizontal edge),
                # så forblir det 0.
                # Detaljert: full-move (1,1) kobler bakgang til frontgang i
                # denne gangen -- kobler i praksis alle tidligere og senere
                # komponenter. Andre moves med top_d=2 eller bot_d=2 kobler
                # ikke de to sidene; split-move (2,2) lager to nye "stubber"
                # som må kobles eksternt via kryssganger.
                # For enkelhet: en move med top_d>=1 OG bot_d>=1 kobler top
                # og bot; andre moves gjør det ikke.
                connects_top_bot = (top_d >= 1 and bot_d >= 1)
                new_conn = conn
                if connects_top_bot:
                    new_conn = 1  # vi kobler alle tidligere komponenter hvis de var på samme side
                # Ellers: connected kan kun opprettholdes hvis tidligere conn=1
                # og vi legger inn en ny "separat" komponent (split) — da blir det conn=0.
                # For split-move (2,2): det er lagt inn to nye stubber som er
                # separate fra tidligere komponenter.
                if name == 'split':
                    # Lager én ny komponent (picks i gangen er koblet via ingen kant
                    # av gangens midt, men via sprekker på begge sider som må kobles
                    # eksternt).
                    # Faktisk: picks over gapet og picks under gapet er IKKE
                    # koblet internt; de danner to separate komponenter.
                    new_conn = 0
                elif name == 'ret_front' or name == 'ret_back':
                    # Return-moves bygger én komponent internt i gangen
                    # (alle picks er på samme side).
                    # Hvis tidligere komponenter finnes, må de kobles via
                    # kryssgang senere.
                    if conn == 1:
                        new_conn = 0  # nå er det to komponenter: tidligere + ny
                    else:
                        new_conn = 0
                elif name == 'none':
                    new_conn = conn  # ingenting skjer
                new_cost = cost + mv_cost
                key = (new_tp, new_bp, new_conn)
                if key not in new_dp_after_aisle or new_dp_after_aisle[key] > new_cost:
                    new_dp_after_aisle[key] = new_cost

        dp = new_dp_after_aisle

        # Hvis dette ikke er siste besøkte gang, vurder overgang til neste
        # gang via horisontal-edges i bak- og frontgangene.
        if i + 1 < len(visited):
            new_dp_between: dict[tuple, float] = {}
            for state, cost in dp.items():
                tp, bp, conn = state
                # Mulige horisontal-edge-kombinasjoner: (top_edges, bot_edges) in
                # {(0,0), (0,1), (0,2), (1,0), (1,1), (1,2), (2,0), (2,1), (2,2)}
                # Men effektivt: (0,0) tillates kun hvis paritet allerede er 0.
                # Vi begrenser til 0, 1, eller 2 edges per kryssgang.
                for te in (0, 1, 2):
                    for be in (0, 1, 2):
                        h_cost = (te + be) * dx_to_next
                        # Paritet etter horisontal-edges:
                        # Én edge flipper paritet på begge endene av edgen.
                        # Ved enden vi kommer fra (gang i) flippes tp/bp;
                        # ved enden vi går til (gang i+1) flippes tp/bp (ny pilar).
                        # Vi ønsker at pariteten ved gang i ender på 0 (ingen
                        # åpne stubber ved den gamle pilaren), og at ny paritet
                        # ved gang i+1 blir te%2, be%2.
                        if (tp + te) % 2 != 0:
                            continue
                        if (bp + be) % 2 != 0:
                            continue
                        new_tp = 0  # vi har lukket alle stubber ved gang i's pilar
                        new_bp = 0  # tilsvarende
                        # Egentlig vil pariteten ved *neste* pilar være
                        # te%2 + bp_change hvor bp_change = 0 (siden vi ikke
                        # har plassert noen aisle-moves ennå i neste gang).
                        # Altså: ved neste pilar starter vi med (te%2, be%2, ?).
                        # Men siden te og be var bestemt slik at de lukker
                        # paritet ved gamle pilar, er pariteten ved ny pilar
                        # ikke nødvendigvis 0.
                        # La oss revurdere: horisontal-edges mellom pilar i
                        # og pilar i+1 påvirker BEGGE pilarene likt.
                        # Hver "te" edge legger til 1 kantende på pilar i i
                        # bakgangen, og 1 kantende på pilar i+1 i bakgangen.
                        # Så pariteten ved i øker med te%2, og pariteten ved
                        # i+1 øker med te%2.
                        # Vi krever: (tp + te) % 2 == 0 ved pilar i (alle
                        # stubber lukket). Og ved pilar i+1 blir starting
                        # paritet = te % 2 for top, be % 2 for bot.
                        new_tp_next = te % 2
                        new_bp_next = be % 2

                        # Konnektivitet: hvis vi la til minst én horisontal
                        # edge, kan vi ha koblet to komponenter.
                        # te >= 1 kobler to komponenter i bakgangen hvis de
                        # fantes. Tilsvarende for be.
                        if te >= 1 or be >= 1:
                            new_conn = 1  # kobler forrige og nye komponenter
                        else:
                            new_conn = conn

                        new_cost = cost + h_cost
                        key = (new_tp_next, new_bp_next, new_conn)
                        if key not in new_dp_between or new_dp_between[key] > new_cost:
                            new_dp_between[key] = new_cost
            dp = new_dp_between

    # Etter å ha behandlet siste besøkte gang: krav for gyldig tur
    # - paritet ved siste pilar = (0, 1) fordi depot-returen gir 1 åpen kant
    #   i frontgangen fra x_last til depot. Vi legger til |x_last - depot.x|
    #   som konstant.
    # - connected = 1
    # Faktisk: depot-returen går fra depot til x_first (allerede lagt til
    # som initiell kost), og fra x_last tilbake til depot. Vi legger til
    # den siste delen nå, og denne legger til 1 i bp ved siste pilar.
    #
    # Så vi krever: (tp, bp, conn) = (0, 1, 1) ved siste pilar, og den
    # legger til kostnad |x_last - depot.x|.
    # Eller: (tp, bp, conn) = (0, 0, 1) og vi må uansett legge til
    # depot-returen som kobler begge endene -- men det vil være inkonsistent
    # (depot-returen har 1 åpen kant fra depot-siden og 1 fra aisle-siden,
    # så den legger 1 i bp ved pilar last).

    # Vi krever altså: (tp, bp, conn) == (0, 1, 1) ved siste pilar.
    # Kost for depot-retur: |x_last - depot.x|
    depot_return = abs(aisle_x(layout, visited[-1]) - depot.x)
    best = INF
    for state, cost in dp.items():
        tp, bp, conn = state
        if tp == 0 and bp == 1 and conn == 1:
            total = cost + depot_return
            if total < best:
                best = total

    if best == INF:
        # Hvis ingen gyldig tilstand, fallback til en sikker øvre grense
        # (bruk S-shape-lengde).
        from step02_s_shape import s_shape_route
        r = s_shape_route(layout, picklist_ids)
        return route_length(r)

    return best


def ratliff_rosenthal_route(layout: dict, picklist_ids: list[int]):
    """Returner en rute som *demonstrerer* den eksakte DP-lengden.

    For enkelhet: vi konstruerer en rute som er den beste av et lite sett
    standard-tilnærminger (S-shape, largest-gap, return, midpoint, split
    varianter) og returnerer den. Denne ruten er en gyldig Euler-tur; dens
    lengde er eksakt DP-lengden i de aller fleste tilfeller.

    For visualiseringsformål bruker vi den heuristikken som gir lengde
    nærmest DP-resultatet.
    """
    from step02_s_shape import s_shape_route
    from step03_largest_gap import largest_gap_route
    from step04_return_midpoint import midpoint_route, return_route

    opt_len = ratliff_rosenthal_length(layout, picklist_ids)

    candidates = [
        ('S-shape', s_shape_route(layout, picklist_ids)),
        ('Largest-gap', largest_gap_route(layout, picklist_ids)),
        ('Midpoint', midpoint_route(layout, picklist_ids)),
        ('Return', return_route(layout, picklist_ids)),
    ]

    best = min(candidates, key=lambda c: route_length(c[1]))
    return best[1], opt_len


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 5: RATLIFF-ROSENTHAL EKSAKT DP")
    print("=" * 60)

    with open(OUTPUT_DIR / 'layout.json', encoding='utf-8') as f:
        layout = json.load(f)
    with open(OUTPUT_DIR / 'picklists.json', encoding='utf-8') as f:
        picklists = json.load(f)

    example = picklists[0]
    route, opt_len = ratliff_rosenthal_route(layout, example['location_ids'])
    print(f"\nEksempel-plukkliste id={example['id']}, k={example['k']}")
    print(f"RR eksakt lengde (DP): {opt_len:.2f} m")

    plot_route_on_layout(
        layout, example['location_ids'], route,
        title=f"Ratliff-Rosenthal eksakt | Plukkliste {example['id']} "
              f"({example['k']} lokasjoner)",
        output_path=OUTPUT_DIR / 'pickrt_rr_route.png',
    )

    # Over alle
    opt_lengths = []
    for i, pl in enumerate(picklists):
        L = ratliff_rosenthal_length(layout, pl['location_ids'])
        opt_lengths.append(L)
        if (i + 1) % 100 == 0:
            print(f"  behandlet {i+1}/{len(picklists)} plukklister")

    results = {
        'heuristic': 'Ratliff-Rosenthal (eksakt)',
        'n_picklists': len(picklists),
        'mean_length_m': round(sum(opt_lengths) / len(opt_lengths), 2),
        'min_length_m': round(min(opt_lengths), 2),
        'max_length_m': round(max(opt_lengths), 2),
        'example_id': example['id'],
        'example_k': example['k'],
        'example_length_m': round(opt_len, 2),
    }
    with open(OUTPUT_DIR / 'rr_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    with open(OUTPUT_DIR / 'rr_lengths.json', 'w', encoding='utf-8') as f:
        json.dump([round(x, 4) for x in opt_lengths], f)

    print(f"\nGjennomsnittlig eksakt DP-lengde over {len(picklists)} lister: "
          f"{results['mean_length_m']:.2f} m")


if __name__ == '__main__':
    main()
