"""
Steg 3: MIP-formulering (Winner Determination Problem)
======================================================
Vi modellerer en kombinatorisk innkjopsauksjon der:

  * Mengde av leverandorer S
  * Mengde av kategorier K
  * Mengde av bud B: hvert bud b tilhoerer en leverandoer s(b) og dekker
    en delmengde av kategorier K(b) med en gitt pris og et gitt volum
    per kategori. Et enkeltbud dekker oeyaktig en kategori; et bundle-bud
    dekker flere, og er alt-eller-ingenting.

Beslutningsvariabel
-------------------
  x_b in {0, 1}    for hvert bud b  (1 hvis budet aksepteres)

Objektfunksjon (minimer totalkostnad)
-------------------------------------
  min  sum_b  p_b * x_b        (p_b = totalkostnad for bud b, som er
                                summen av pris_per_enhet * volum over alle
                                kategorier budet dekker)

Skranker
--------
  1) Dekning: hver kategori k dekkes av eksakt ett bud
       sum_{b : k in K(b)}  x_b  =  1      for alle k in K

  2) Kapasitet per leverandoer: ingen leverandoer kan stikke av med mer
     enn andel alpha_s av total kontraktsverdi (C_max). Vi implementerer
     dette som en 'andel'-skranke:
       sum_{b : s(b) = s}  p_b * x_b  <=  alpha_s * C_total     for alle s
     der C_total er total kontraktsverdi beregnet som summen av laveste
     tilgjengelige enhetspris * volum per kategori (dette er en oevre
     grense som alle faktiske tildelinger ligger under, gitt at kategoriene
     maa dekkes).

Denne WDP-varianten er eksakt losbar med PuLP/CBC for moderat storrelse
(her: ca. 20 bud / 8 kategorier). Problemet er NP-hardt i generalfomen.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def build_bids(df_unit: pd.DataFrame,
               df_bundle: pd.DataFrame) -> pd.DataFrame:
    """Bygg en flat budtabell der hver rad er et 'bud' med aggregert total-
    kostnad og en liste over kategorier det dekker."""
    rows = []
    for _, r in df_unit.iterrows():
        rows.append({
            'bud_id': r['bud_id'],
            'type': 'enkelt',
            'leverandoer': r['leverandoer'],
            'kategorier': [r['kategori']],
            'totalkost_NOK': float(r['linekost_NOK']),
        })
    for bid_id, grp in df_bundle.groupby('bud_id'):
        cats = grp['kategori'].tolist()
        totalkost = float(grp['linekost_NOK'].sum())
        supplier = grp['leverandoer'].iloc[0]
        rows.append({
            'bud_id': bid_id,
            'type': 'bundle',
            'leverandoer': supplier,
            'kategorier': sorted(cats),
            'totalkost_NOK': totalkost,
        })
    return pd.DataFrame(rows)


def build_wdp(df_bids: pd.DataFrame, df_cat: pd.DataFrame,
              df_sup: pd.DataFrame,
              diversification: bool = False) -> pulp.LpProblem:
    """Bygg WDP-MIP. Hvis diversification=True brukes andelsbegrensning
    per leverandoer."""
    model = pulp.LpProblem('WDP', pulp.LpMinimize)

    x = {row['bud_id']: pulp.LpVariable(f"x_{row['bud_id']}", cat=pulp.LpBinary)
         for _, row in df_bids.iterrows()}

    # Objekt: total kostnad
    obj = pulp.lpSum(x[bid_id] * row['totalkost_NOK']
                     for bid_id, row in zip(df_bids['bud_id'].to_list(),
                                            df_bids.to_dict('records')))
    model += obj, 'TotalCost'

    # Dekning: hver kategori dekkes av eksakt ett bud
    for _, c in df_cat.iterrows():
        cov = [bid['bud_id'] for _, bid in df_bids.iterrows()
               if c['kategori'] in bid['kategorier']]
        model += (pulp.lpSum(x[b] for b in cov) == 1), f"Cover_{c['kategori']}"

    # Kapasitet/diversifisering per leverandoer
    if diversification:
        C_total = float(df_bids.groupby('kategorier')  # dummy; overstyres under
                        ['totalkost_NOK'].sum().sum())
        # Bruk sum av billigste enkeltbud per kategori som oevre grense
        cheapest = []
        for _, c in df_cat.iterrows():
            cand = [bid['totalkost_NOK'] for _, bid in df_bids.iterrows()
                    if (bid['type'] == 'enkelt'
                        and c['kategori'] in bid['kategorier'])]
            if cand:
                cheapest.append(min(cand))
        C_upper = float(sum(cheapest))

        for _, s in df_sup.iterrows():
            budset = [bid['bud_id'] for _, bid in df_bids.iterrows()
                      if bid['leverandoer'] == s['leverandoer']]
            andel = float(s['kap_andel_maks'])
            model += (pulp.lpSum(x[b] * float(
                df_bids[df_bids['bud_id'] == b]['totalkost_NOK'].iloc[0])
                for b in budset)
                - andel * C_upper <= 0), f"Cap_{s['leverandoer']}"

    return model, x


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: MIP-FORMULERING (Winner Determination Problem)")
    print("=" * 60)

    df_cat = pd.read_csv(DATA_DIR / 'kategorier.csv')
    df_sup = pd.read_csv(DATA_DIR / 'leverandorer.csv')
    df_unit = pd.read_csv(DATA_DIR / 'enkeltbud.csv')
    df_bundle = pd.read_csv(DATA_DIR / 'bundlebud.csv')

    df_bids = build_bids(df_unit, df_bundle)
    df_bids_to_save = df_bids.copy()
    df_bids_to_save['kategorier'] = df_bids_to_save['kategorier'].apply(
        lambda L: ','.join(L))
    df_bids_to_save.to_csv(OUTPUT_DIR / 'step03_bud_oversikt.csv', index=False)

    model, x = build_wdp(df_bids, df_cat, df_sup, diversification=False)
    lp_path = OUTPUT_DIR / 'wdp_model.lp'
    model.writeLP(str(lp_path))
    print(f"LP-fil lagret: {lp_path}")

    n_vars = len(model.variables())
    n_cons = len(model.constraints)
    # PuLP 3.x lagrer binaere variabler som cat='Integer' med 0/1-grenser
    n_bin = sum(1 for v in model.variables()
                if (v.cat in (pulp.LpBinary, 'Binary', 'Integer'))
                and (v.lowBound == 0 and v.upBound == 1))

    summary = {
        'antall_kategorier': int(len(df_cat)),
        'antall_leverandoerer': int(len(df_sup)),
        'antall_enkeltbud': int(len(df_unit)),
        'antall_bundler': int(df_bundle['bud_id'].nunique()),
        'antall_bud_total': int(len(df_bids)),
        'antall_variabler': int(n_vars),
        'antall_binaere_variabler': int(n_bin),
        'antall_skranker': int(n_cons),
        'antall_dekningsskranker': int(len(df_cat)),
        'teoretisk_kombinasjoner': int(2 ** n_bin),
    }
    with open(OUTPUT_DIR / 'step03_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag lagret: {OUTPUT_DIR / 'step03_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Utdrag av LP-formulering
    with open(lp_path, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
    print("\n--- Utdrag av LP-formulering (foerste 22 linjer) ---")
    for line in lines[:22]:
        print(line.rstrip())
    print("  ...")


if __name__ == '__main__':
    main()
