"""
Steg 6: Anbefaling
==================
Oppsummerer alle tre scenarier (integrert, desentralisert, revenue-sharing)
i en samletabell som lagres til JSON og brukes direkte i LaTeX-tabellen.
"""

import json
from pathlib import Path

from step01_datainnsamling import (
    MU_DEMAND,
    SIGMA_DEMAND,
    PRICE_RETAIL,
    COST_SUPPLIER,
    SALVAGE_VALUE,
    WHOLESALE_PRICE,
)
from step02_sentralisert import expected_chain_profit, optimal_q
from step03_desentralisert import retailer_profit, supplier_profit, optimal_q_retailer
from step04_revenue_sharing import (
    rs_retailer_profit, rs_supplier_profit, coordinated_wholesale
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 6: ANBEFALING')
    print('=' * 60)

    # --- Scenario 1: integrert --------------------------------------------
    q_chain = optimal_q(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE,
                        MU_DEMAND, SIGMA_DEMAND)
    pi_chain = expected_chain_profit(q_chain, PRICE_RETAIL, COST_SUPPLIER,
                                     SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)

    # --- Scenario 2: desentralisert (ordinaer engrospriskontrakt) ---------
    q_ret = optimal_q_retailer(PRICE_RETAIL, WHOLESALE_PRICE, SALVAGE_VALUE,
                               MU_DEMAND, SIGMA_DEMAND)
    pi_ret_dec = retailer_profit(q_ret, PRICE_RETAIL, WHOLESALE_PRICE,
                                 SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    pi_sup_dec = supplier_profit(q_ret, WHOLESALE_PRICE, COST_SUPPLIER)
    pi_chain_dec = pi_ret_dec + pi_sup_dec

    # --- Scenario 3: revenue-sharing phi = 0.5 ----------------------------
    phi = 0.5
    w_p = coordinated_wholesale(phi, COST_SUPPLIER)
    pi_ret_rs = rs_retailer_profit(q_chain, phi, PRICE_RETAIL, w_p,
                                   SALVAGE_VALUE, MU_DEMAND, SIGMA_DEMAND)
    pi_sup_rs = rs_supplier_profit(q_chain, phi, PRICE_RETAIL, w_p,
                                   COST_SUPPLIER, SALVAGE_VALUE,
                                   MU_DEMAND, SIGMA_DEMAND)
    pi_chain_rs = pi_ret_rs + pi_sup_rs

    rows = [
        {
            'scenario': 'Integrert kjede',
            'q': round(float(q_chain), 1),
            'retailer': round(float(pi_chain), 0),     # det er kjedens samlede
            'supplier': 0,                              # ingen egen lev. profitt
            'kjede': round(float(pi_chain), 0),
            'koordinering': 'Full (referanse)',
        },
        {
            'scenario': 'Desentralisert (engrospris $w = 900$)',
            'q': round(float(q_ret), 1),
            'retailer': round(float(pi_ret_dec), 0),
            'supplier': round(float(pi_sup_dec), 0),
            'kjede': round(float(pi_chain_dec), 0),
            'koordinering': 'Nei -- double marginalization',
        },
        {
            'scenario': fr"Revenue sharing ($\varphi = 0{{,}}5$, $w' = 200$)",
            'q': round(float(q_chain), 1),
            'retailer': round(float(pi_ret_rs), 0),
            'supplier': round(float(pi_sup_rs), 0),
            'kjede': round(float(pi_chain_rs), 0),
            'koordinering': 'Ja -- kjeden koordinert',
        },
    ]

    recommendation = {
        'scenarier': rows,
        'kjede_gap_kr': round(float(pi_chain - pi_chain_dec), 0),
        'kjede_gap_pct': round(float((pi_chain - pi_chain_dec) / pi_chain * 100), 2),
        'valgt_phi': phi,
        'koordinerende_w_prime': round(float(w_p), 0),
        'detaljist_forbedring_pct': round(float((pi_ret_rs - pi_ret_dec)
                                                / pi_ret_dec * 100), 2),
        'leverandor_forbedring_pct': round(float((pi_sup_rs - pi_sup_dec)
                                                 / pi_sup_dec * 100), 2),
    }

    print('\nScenarioer (forventet profitt, NOK):')
    print(f"{'Scenario':40s}  {'Q':>7s}  {'Retailer':>12s}  {'Supplier':>12s}  {'Kjede':>12s}")
    for row in rows:
        print(f"  {row['scenario'][:38]:38s}  "
              f"{row['q']:7.1f}  {row['retailer']:12,.0f}  "
              f"{row['supplier']:12,.0f}  {row['kjede']:12,.0f}")

    print(f"\nVerdi-gap desentralisert vs integrert : "
          f"{pi_chain - pi_chain_dec:,.0f} NOK "
          f"({recommendation['kjede_gap_pct']:.1f}%)")
    print(f"Revenue sharing forbedrer detaljist    : "
          f"{recommendation['detaljist_forbedring_pct']:.1f}%")
    print(f"Revenue sharing forbedrer leverandoer  : "
          f"{recommendation['leverandor_forbedring_pct']:.1f}%")

    with open(OUTPUT_DIR / 'step06_results.json', 'w', encoding='utf-8') as f:
        json.dump(recommendation, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step06_results.json'}")


if __name__ == '__main__':
    main()
