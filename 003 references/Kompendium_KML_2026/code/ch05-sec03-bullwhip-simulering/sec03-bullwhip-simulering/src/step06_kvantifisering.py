"""
Steg 6: Kvantifisering og kostnadsestimering
============================================
Produserer en sluttabell med bullwhip-ratioer per trinn og estimerer
kostnadsreduksjonen ved delt informasjon. Kostnadsmodellen er:

    C_k(t) = h * max(I_k(t), 0) + b * max(-I_k(t), 0) + c_order * O_k(t)

der h = 0.5 kr/uke/enhet (holdingskostnad), b = 4.0 kr/enhet (stockout)
og c_order = 1.0 kr/enhet (ordreprosesseringskostnad). Totalkostnad er
sum over trinn og uker (etter warmup).

Output:
    - output/bullwhip_final_stats.json
    - output/final_table.csv
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step01_datainnsamling import generate_demand
from step02_basismodell import Tier, bullwhip_ratios, simulate_chain

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

H_COST = 0.5      # kr per enhet per uke
B_COST = 4.0      # kr per manglende enhet per uke
O_COST = 1.0      # kr per bestilt enhet


def total_cost(result: dict, warmup: int = 10) -> dict:
    """Beregn total kostnad over alle trinn fra uke warmup og utover."""
    K = result['K']
    inv = result['inventory'][:, warmup:]
    orders = result['orders_placed'][:, warmup:]
    holding = H_COST * np.clip(inv, 0.0, None)
    backlog = B_COST * np.clip(-inv, 0.0, None)
    ordering = O_COST * orders
    total = (holding + backlog + ordering).sum()
    per_tier = {
        result['tier_names'][k]: {
            'holding': round(float(holding[k].sum()), 2),
            'backlog': round(float(backlog[k].sum()), 2),
            'ordering': round(float(ordering[k].sum()), 2),
            'total': round(float((holding[k] + backlog[k] + ordering[k]).sum()), 2),
        }
        for k in range(K)
    }
    return {'total_kr': round(float(total), 2), 'per_tier': per_tier}


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 6: KVANTIFISERING')
    print('=' * 60)

    demand = generate_demand().values

    # Desentralisert
    tiers_dec = [Tier(name=n) for n in
                 ['Detaljist', 'Grossist', 'Distributor', 'Fabrikk']]
    res_dec = simulate_chain(demand, tiers=tiers_dec, shared_information=False)
    bw_dec = bullwhip_ratios(res_dec, warmup=10)
    cost_dec = total_cost(res_dec, warmup=10)

    # Delt informasjon
    tiers_shr = [Tier(name=n) for n in
                 ['Detaljist', 'Grossist', 'Distributor', 'Fabrikk']]
    res_shr = simulate_chain(demand, tiers=tiers_shr, shared_information=True)
    bw_shr = bullwhip_ratios(res_shr, warmup=10)
    cost_shr = total_cost(res_shr, warmup=10)

    # Sluttabell
    rows = []
    for k, name in enumerate(res_dec['tier_names']):
        rows.append({
            'Trinn': name,
            'BW_dec': round(bw_dec[k], 3),
            'BW_shared': round(bw_shr[k], 3),
            'Reduksjon_pct': round(
                100.0 * (bw_dec[k] - bw_shr[k]) / bw_dec[k], 1
            ) if bw_dec[k] > 0 else 0.0,
            'Kostnad_dec': cost_dec['per_tier'][name]['total'],
            'Kostnad_shared': cost_shr['per_tier'][name]['total'],
        })
    df = pd.DataFrame(rows)
    df.to_csv(OUTPUT_DIR / 'final_table.csv', index=False)
    print('\n' + df.to_string(index=False))

    savings_pct = (
        100.0 * (cost_dec['total_kr'] - cost_shr['total_kr']) / cost_dec['total_kr']
        if cost_dec['total_kr'] > 0 else 0.0
    )

    final = {
        'bullwhip_decentralized': {n: round(bw_dec[k], 3)
                                   for k, n in enumerate(res_dec['tier_names'])},
        'bullwhip_shared': {n: round(bw_shr[k], 3)
                            for k, n in enumerate(res_shr['tier_names'])},
        'total_cost_decentralized_kr': cost_dec['total_kr'],
        'total_cost_shared_kr': cost_shr['total_kr'],
        'cost_savings_pct': round(savings_pct, 1),
        'cost_savings_kr': round(cost_dec['total_kr'] - cost_shr['total_kr'], 2),
    }
    with open(OUTPUT_DIR / 'bullwhip_final_stats.json', 'w', encoding='utf-8') as f:
        json.dump(final, f, indent=2, ensure_ascii=False)
    print('\n--- Oppsummering ---')
    print(json.dumps(final, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
