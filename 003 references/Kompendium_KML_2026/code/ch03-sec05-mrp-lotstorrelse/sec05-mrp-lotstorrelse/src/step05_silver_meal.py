"""
Steg 5: Silver-Meal-heuristikk
==============================
Silver-Meal velger lotstorrelse ved a minimere gjennomsnittlig kostnad
per periode over et voksende antall dekkede perioder. Starter i forste
periode med nettobehov og stopper a utvide sa snart gjennomsnittskostnaden
okrer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_bom, build_mps
from step02_mrp_eksplosjon import run_mrp, total_cost
from step03_lfl import plot_mrp_timeline

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def silver_meal_lot_sizing(setup_cost: float, holding_cost: float):
    """
    Returnerer en funksjon som tar nettobehov-array og returnerer
    planlagte mottak per periode basert pa Silver-Meal.

    Silver-Meal-logikk (gitt oppstartskost S og lagringskost H per enhet/periode):
      Start ved forste periode t* med net_req > 0.
      Vurder a dekke perioder t*, t*+1, ..., t*+k.
      Gjennomsnittlig kostnad per periode for a dekke k+1 perioder:
         AC(k) = (S + sum_{j=0..k} j * H * net_req[t* + j]) / (k + 1)
      Velg storste k slik at AC(k) <= AC(k+1), bestill sum av net_req[t*..t*+k]
      i periode t*, og gjenta prosessen fra periode t* + k + 1.
    """
    def lot_sizing(tentative_net: np.ndarray, name: str, comps: Dict) -> np.ndarray:
        """
        Silver-Meal: bestem hvor mange framtidige perioder en enkelt ordre
        skal dekke, og returner kvantum i forste element. mrp_for_item bruker
        kun forste element; framtidige mottaksplaner kjores inn i neste
        iterasjon av MRP-lokken (som setter disse via lager_slutt > 0).

        Viktig merknad: siden mrp_for_item evaluerer en ordre om gangen,
        kan Silver-Meal implementeres ved a bestille nok til a dekke de
        forste m periodene som gir lavest gjennomsnittlig kostnad per
        periode. Vi returnerer sa qty i forste periode og null for resten.
        """
        S = comps[name]['setup_cost']
        H = comps[name]['holding_cost']
        T = len(tentative_net)
        out = np.zeros_like(tentative_net)
        if T == 0 or tentative_net[0] <= 0:
            return out

        best_k = 0
        best_ac = float('inf')
        cum_hold = 0.0
        k = 0
        while k < T:
            if tentative_net[k] <= 0 and k > 0:
                # Ingen ekstra behov; ingen ekstra kostnad ved a forlenge
                # dekningen. Vi regner denne uken som "gratis" inkludert.
                # For a unnga uendelig forlenging, bryter vi hvis to
                # paf�lgende nuller oppstar.
                pass
            if k > 0:
                cum_hold += k * H * tentative_net[k]
            n_periods = k + 1
            ac = (S + cum_hold) / n_periods
            if ac <= best_ac:
                best_ac = ac
                best_k = k
                k += 1
            else:
                break

        order_qty = int(np.sum(tentative_net[:best_k + 1]))
        out[0] = order_qty
        return out

    return lot_sizing


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print('\n' + '=' * 60)
    print('STEG 5: SILVER-MEAL HEURISTIKK')
    print('=' * 60)

    components = build_bom()
    mps = build_mps(12)

    # Silver-Meal-funksjonen ma vite S og H per komponent; vi bruker en generell
    # lot_sizing som slar opp i comps
    sm_fn = silver_meal_lot_sizing(setup_cost=0, holding_cost=0)  # dummy, bruker comps

    results = run_mrp(components, mps, sm_fn)
    cost = total_cost(results, components)

    print(f'\nSilver-Meal total kostnad: {cost["total_kr_totalt"]:.0f} kr '
          f'(oppstart {cost["oppstart_kr_totalt"]:.0f} + lager {cost["lager_kr_totalt"]:.0f})')
    for k, v in cost['per_komponent'].items():
        print(f"  {k:10s}: ordrer={v['antall_ordrer']}, total={v['total_kr']:.0f}")

    serial = {name: df.to_dict(orient='list') for name, df in results.items()}
    with open(OUTPUT_DIR / 'mrp_silvermeal.json', 'w', encoding='utf-8') as f:
        json.dump({'mrp': serial, 'cost': cost}, f, indent=2, ensure_ascii=False)
    print(f'Lagret: {OUTPUT_DIR / "mrp_silvermeal.json"}')

    plot_mrp_timeline(results, 'Planlagte ordrestart per komponent - Silver-Meal',
                      OUTPUT_DIR / 'mrp_timeline_silvermeal.png')


if __name__ == '__main__':
    main()
