"""
Steg 4: EOQ-basert lotstorrelse
================================
Beregn okonomisk ordrekvantum (EOQ) basert pa gjennomsnittlig etterspørsel
og anvend det som fast lotstorrelse: hver gang nettobehov > 0, bestilles
EOQ (eller nettobehov hvis storre).
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Dict

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import build_bom, build_mps
from step02_mrp_eksplosjon import run_mrp, total_cost
from step03_lfl import plot_mrp_timeline

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def compute_eoq(demand_per_week: float, setup_cost: float, holding_cost: float) -> float:
    r"""
    EOQ = sqrt(2 * D * S / H), der D er etterspørsel per periode, S oppstart,
    H lagringskostnad per enhet per periode.
    """
    if demand_per_week <= 0 or holding_cost <= 0:
        return 0.0
    return math.sqrt(2.0 * demand_per_week * setup_cost / holding_cost)


def eoq_lot_sizing_factory(components: Dict[str, dict], mps: pd.Series):
    """
    Returnerer en lotstorrelsefunksjon som bruker EOQ per komponent.

    Vi beregner EOQ en gang basert pa total etterspørsel for komponenten
    over horisonten (avledet fra MPS og BOM-multiplikatorer).
    """
    # Beregn total etterspørsel per komponent (bruttobehov totalt / n_uker)
    total_demand = {}
    total_demand['Sykkel'] = float(mps.sum())
    # Lag en rekursiv hjelper: gross for komponent = sum av forelders "releases"*qty
    # For EOQ bruker vi gjennomsnittlig etterspørsel, noe vi kan approksimere som
    # (sum(MPS) * sum av qty-produkter ned til rotkomponent) / n_uker
    def qty_multiplier(name: str) -> float:
        if components[name]['parent'] is None:
            return 1.0
        return components[name]['qty_per_parent'] * qty_multiplier(components[name]['parent'])

    T = float(len(mps))
    for name in components:
        total_demand[name] = float(mps.sum()) * qty_multiplier(name)

    eoq_values: Dict[str, int] = {}
    for name, c in components.items():
        d_wk = total_demand[name] / T
        eoq = compute_eoq(d_wk, c['setup_cost'], c['holding_cost'])
        eoq_values[name] = max(1, int(round(eoq)))

    def eoq_lot_sizing(tentative_net: np.ndarray, name: str, comps: Dict) -> np.ndarray:
        """
        Bestill EOQ som ordrestorrelse for forste periode.
        Hvis nettobehov i forste periode er storre enn EOQ, bestiller vi
        nettobehovet (minst mulig dekning).
        """
        q = eoq_values[name]
        out = np.zeros_like(tentative_net)
        shortage = tentative_net[0] if len(tentative_net) > 0 else 0
        if shortage > 0:
            out[0] = max(q, int(math.ceil(shortage)))
        return out

    return eoq_lot_sizing, eoq_values, total_demand


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print('\n' + '=' * 60)
    print('STEG 4: EOQ-BASERT LOTSTORRELSE')
    print('=' * 60)

    components = build_bom()
    mps = build_mps(12)

    eoq_fn, eoq_values, total_demand = eoq_lot_sizing_factory(components, mps)
    print('\nEOQ-verdier per komponent:')
    for name, q in eoq_values.items():
        c = components[name]
        d_wk = total_demand[name] / len(mps)
        print(f"  {name:10s}: D~{d_wk:.2f}/uke, S={c['setup_cost']}, H={c['holding_cost']}, "
              f"EOQ={q}")

    results = run_mrp(components, mps, eoq_fn)
    cost = total_cost(results, components)

    print(f'\nEOQ total kostnad: {cost["total_kr_totalt"]:.0f} kr '
          f'(oppstart {cost["oppstart_kr_totalt"]:.0f} + lager {cost["lager_kr_totalt"]:.0f})')
    for k, v in cost['per_komponent'].items():
        print(f"  {k:10s}: ordrer={v['antall_ordrer']}, total={v['total_kr']:.0f}")

    serial = {name: df.to_dict(orient='list') for name, df in results.items()}
    with open(OUTPUT_DIR / 'mrp_eoq.json', 'w', encoding='utf-8') as f:
        json.dump({'mrp': serial, 'cost': cost, 'eoq_values': eoq_values},
                  f, indent=2, ensure_ascii=False)
    print(f'Lagret: {OUTPUT_DIR / "mrp_eoq.json"}')

    plot_mrp_timeline(results, 'Planlagte ordrestart per komponent - EOQ',
                      OUTPUT_DIR / 'mrp_timeline_eoq.png')


if __name__ == '__main__':
    main()
