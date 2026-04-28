"""
Steg 2: MRP-eksplosjon (bruttobehov -> nettobehov med tidsforskyvning)
=======================================================================
For en gitt lotstorrelsespolitikk beregner vi for hver komponent fra topp
til bunn av BOM-traet:
  - bruttobehov (fra MPS eller foreldres planlagte ordrestart),
  - nettobehov etter trekk av lagerbeholdning og planlagte mottak,
  - planlagte ordrermottak (lotstorrelse avhenger av politikk),
  - planlagte ordrestart (tidsforskjovet med leveringstid LT).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Dict

import numpy as np
import pandas as pd

from step01_datainnsamling import build_bom, build_mps

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def get_children(components: Dict[str, dict], parent: str) -> list[str]:
    """Hent alle direkte barn av en komponent."""
    return [n for n, c in components.items() if c['parent'] == parent]


def lot_for_lot(net_req: np.ndarray) -> np.ndarray:
    """
    Lot-for-lot: bestiller eksakt nettobehov for perioden.
    Forventes kalt med en fremtidsprofil; returnerer array der forste
    element er anbefalt ordrestorrelse (akkurat nettobehov for perioden).
    """
    out = np.zeros_like(net_req)
    out[0] = net_req[0]
    return out


def mrp_for_item(
    name: str,
    components: Dict[str, dict],
    gross_req: np.ndarray,
    lot_sizing: Callable[[np.ndarray, str, Dict], np.ndarray],
    n_weeks: int,
) -> pd.DataFrame:
    """
    Kjor MRP-logikken for en enkelt komponent med korrekt lagerframskrivning.

    Algoritmen er "nar-trengs-det": vi gar gjennom uke for uke og bestiller
    kun nar projektert lager (startlager + eventuelle tidligere mottak)
    ikke dekker bruttobehov for uken. Lotstorrelsen bestemmes av
    lot_sizing-funksjonen, som far en "fremtidsprofil" av nettobehov for
    denne perioden og framover (tentativ nettobehov uten framtidige ordrer).
    """
    c = components[name]
    lt = int(c['lead_time'])
    on_hand = int(c['on_hand'])

    start_bal = np.zeros(n_weeks, dtype=float)
    end_bal = np.zeros(n_weeks, dtype=float)
    net_req = np.zeros(n_weeks, dtype=float)
    planned_receipts = np.zeros(n_weeks, dtype=float)
    planned_releases = np.zeros(n_weeks, dtype=float)

    remaining = on_hand
    t = 0
    while t < n_weeks:
        start_bal[t] = remaining
        g = gross_req[t]
        if remaining >= g:
            # Dekket av lager, ingen ordre
            net_req[t] = 0
            end_bal[t] = remaining - g
            remaining = end_bal[t]
            t += 1
            continue

        # Nettobehov for denne uken
        shortage = g - remaining
        net_req[t] = shortage

        # Bygg tentativ nettobehov for framtidige uker *uten* framtidige ordrer:
        # vi simulerer at vi bestiller kun for a dekke denne uken, og ser
        # nar neste underskudd oppstar.
        tentative = np.zeros(n_weeks - t, dtype=float)
        tentative[0] = shortage
        # Etter ordren vil sluttlager i uke t vare 0 (hvis vi bestiller akkurat
        # shortage) eller (lotstr - shortage) hvis vi bestiller mer. Lotstr-funksjon
        # kan bestemme hvor mye som er igjen. Her antar vi tentatively at
        # sluttlager er 0 etter uke t, og beregner netto-behov for framtidige
        # uker uten ekstra mottak:
        future_rem = 0.0
        for k in range(1, n_weeks - t):
            gk = gross_req[t + k]
            if future_rem >= gk:
                future_rem -= gk
                tentative[k] = 0
            else:
                tentative[k] = gk - future_rem
                future_rem = 0.0

        # Bestem lotstorrelse via politikken
        qty = lot_sizing(tentative, name, components)
        # Konvensjon: lot_sizing returnerer en array der forste element
        # er ordre plassert i periode t; resten er 0 eller framtidige ordrer
        # (men vi bruker bare forste).
        order_qty = float(qty[0]) if hasattr(qty, '__len__') else float(qty)
        if order_qty < shortage:
            order_qty = shortage  # minste ordre ma dekke underskudd
        order_qty = int(np.ceil(order_qty))

        planned_receipts[t] = order_qty
        end_bal[t] = remaining + order_qty - g
        remaining = end_bal[t]

        # Planlagt ordrestart = t - LT
        start_period = t - lt
        if start_period >= 0:
            planned_releases[start_period] += order_qty
        # Hvis start_period < 0, starter vi i periode 0 (flagget kan loses
        # med sikkerhetslager/flytting av frigitt ordre; for eksemplet antar vi
        # at OH gjor dette unodvendig).

        t += 1

    df = pd.DataFrame({
        'uke': np.arange(1, n_weeks + 1),
        'bruttobehov': gross_req.astype(int),
        'lager_start': start_bal.astype(int),
        'planlagt_mottak': planned_receipts.astype(int),
        'nettobehov': net_req.astype(int),
        'lager_slutt': end_bal.astype(int),
        'planlagt_ordrestart': planned_releases.astype(int),
    })
    df.attrs['name'] = name
    df.attrs['lead_time'] = lt
    df.attrs['on_hand'] = on_hand
    return df


def run_mrp(
    components: Dict[str, dict],
    mps: pd.Series,
    lot_sizing: Callable[[np.ndarray, str, Dict], np.ndarray],
) -> Dict[str, pd.DataFrame]:
    """
    Kjor full MRP top-down for alle komponenter med gitt lotstorrelsespolitikk.

    Returnerer dict {komponent: df med MRP-tabell}.
    """
    n_weeks = int(len(mps))
    results: Dict[str, pd.DataFrame] = {}

    # Sortert etter BOM-niva (niva 0 forst)
    order = sorted(components.keys(), key=lambda k: components[k]['level'])

    # Bruttobehov for topp: MPS
    gross_by_item: Dict[str, np.ndarray] = {}
    for name in order:
        c = components[name]
        if c['parent'] is None:
            gross = mps.values.astype(float).copy()
        else:
            # Bruttobehov for komponent = foreldres planlagte ordrestart * qty_per_parent
            parent_df = results[c['parent']]
            parent_rel = parent_df['planlagt_ordrestart'].values.astype(float)
            gross = parent_rel * c['qty_per_parent']
        gross_by_item[name] = gross
        df = mrp_for_item(name, components, gross, lot_sizing, n_weeks)
        results[name] = df

    return results


def total_cost(mrp_results: Dict[str, pd.DataFrame], components: Dict[str, dict]) -> Dict[str, float]:
    """Beregn totale kostnader: oppstart (per ordre) + lagring (per enhet per uke)."""
    setup_total = 0.0
    hold_total = 0.0
    per_item = {}
    for name, df in mrp_results.items():
        n_orders = int((df['planlagt_mottak'] > 0).sum())
        s = n_orders * components[name]['setup_cost']
        # Lagring pa gjennomsnittlig lager pr uke (bruker slutt-lager som approksimasjon)
        avg_inv = df['lager_slutt'].mean()
        h = avg_inv * components[name]['holding_cost'] * len(df)
        per_item[name] = {
            'oppstart_kr': float(s),
            'lager_kr': float(h),
            'total_kr': float(s + h),
            'antall_ordrer': n_orders,
            'gj_lager': float(avg_inv),
        }
        setup_total += s
        hold_total += h
    return {
        'oppstart_kr_totalt': float(setup_total),
        'lager_kr_totalt': float(hold_total),
        'total_kr_totalt': float(setup_total + hold_total),
        'per_komponent': per_item,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print('\n' + '=' * 60)
    print('STEG 2: MRP-EKSPLOSJON (standardpolicy = lot-for-lot)')
    print('=' * 60)

    components = build_bom()
    mps = build_mps(12)

    def lfl(tentative_net: np.ndarray, name: str, comps: Dict) -> np.ndarray:
        return lot_for_lot(tentative_net)

    results = run_mrp(components, mps, lfl)

    # Skriv ut MRP-tabeller
    for name in sorted(components.keys(), key=lambda k: components[k]['level']):
        df = results[name]
        print(f'\n--- {name} (niva {components[name]["level"]}, LT={components[name]["lead_time"]}) ---')
        print(df.to_string(index=False))

    # Beregn kostnader
    cost = total_cost(results, components)
    print('\nKostnadssammendrag (lot-for-lot):')
    for k, v in cost['per_komponent'].items():
        print(f"  {k:10s}: ordrer={v['antall_ordrer']}, oppstart={v['oppstart_kr']:.0f}, "
              f"lager={v['lager_kr']:.0f}, total={v['total_kr']:.0f}")
    print(f"  TOTALT: {cost['total_kr_totalt']:.0f} kr "
          f"(oppstart {cost['oppstart_kr_totalt']:.0f} + lager {cost['lager_kr_totalt']:.0f})")

    # Lagre MRP-tabeller
    out_path = OUTPUT_DIR / 'mrp_eksplosjon_lfl.json'
    serial = {name: df.to_dict(orient='list') for name, df in results.items()}
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump({'mrp': serial, 'cost': cost}, f, indent=2, ensure_ascii=False)
    print(f'\nMRP-eksplosjon lagret: {out_path}')


if __name__ == '__main__':
    main()
