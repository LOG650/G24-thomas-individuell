"""
Steg 5: Validering / stresstest
================================
Gitt den optimale planen fra steg 3, sammenligner vi den mot en
naiv chase-strategi og mot flere scenarier (etterspoerselssjokk,
kapasitetsreduksjon). Resultatet er en stresstest-tabell som viser
hvor robust LP-loesningen er.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import parameters, MONTHS_NO
from step03_lp_losning import build_and_solve

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def chase_strategy(demand: np.ndarray, params: dict) -> dict:
    """Naiv 'chase'-strategi: produsere noeyaktig etterspoersel hver mnd.,
    bruke overtid ved kapasitetsoverskridelse og justere arbeidsstyrke.
    """
    T = len(demand)
    alpha = params['alpha']
    O_max = params['O_max']
    W = params['W_0']
    I = params['I_0']
    total = 0.0
    Ps, Os, Is, Hs, Fs, Ws = [], [], [], [], [], []
    for t in range(T):
        # Maal: dekk D_t og holde lager paa null
        needed = max(demand[t] - I, 0)
        # Juster arbeidsstyrke saa alpha*W >= needed (uten overtid)
        target_W = int(np.ceil(needed / alpha))
        if target_W > W:
            H = target_W - W
            F = 0
        elif target_W < W:
            H = 0
            F = W - target_W
        else:
            H = 0
            F = 0
        W_new = W + H - F
        ordinary = min(alpha * W_new, needed)
        overtime = min(needed - ordinary, O_max)
        P = ordinary
        O = overtime
        I_new = I + P + O - demand[t]
        if I_new < 0:
            # Ubetjent etterspoersel -> vi tvinges til positiv lager via mer overtid
            # (ved hjelp av ytterligere bemanning)
            extra = -I_new
            extra_H = int(np.ceil(extra / alpha))
            H += extra_H
            W_new += extra_H
            P = min(alpha * W_new, demand[t] + max(0, -I))
            I_new = I + P + O - demand[t]
        total += (params['c_P'] * P + params['c_O'] * O + params['c_I'] * max(I_new, 0)
                  + params['c_H'] * H + params['c_F'] * F)
        Ps.append(P); Os.append(O); Is.append(max(I_new, 0))
        Hs.append(H); Fs.append(F); Ws.append(W_new)
        W = W_new
        I = max(I_new, 0)
    return {
        'obj': float(total), 'P': Ps, 'O': Os, 'I': Is, 'H': Hs, 'F': Fs, 'W': Ws,
    }


def scenario_table(demand: np.ndarray, params: dict) -> pd.DataFrame:
    """Kjoer flere scenarier og sammenlign totalkostnad med baseline."""
    rows = []

    # Baseline
    base = build_and_solve(demand, params)
    rows.append({
        'scenario': 'Baseline (LP)', 'detalj': 'Original etterspoersel og kapasitet',
        'obj': round(base['obj'], 2),
        'rel_endr_%': 0.00,
    })

    # Chase-heuristikk
    chase = chase_strategy(demand, params)
    rows.append({
        'scenario': 'Chase (heuristikk)',
        'detalj': 'Produser per mnd uten lageroppbygging',
        'obj': round(chase['obj'], 2),
        'rel_endr_%': round(100 * (chase['obj'] - base['obj']) / base['obj'], 2),
    })

    # Etterspoerselssjokk +10 / -10
    for pct in (0.90, 1.10):
        d = np.round(demand * pct).astype(int)
        r = build_and_solve(d, params)
        rows.append({
            'scenario': f'Etterspoersel x {pct:.2f}',
            'detalj': 'Likeverdig skalering alle maaneder',
            'obj': round(r['obj'], 2),
            'rel_endr_%': round(100 * (r['obj'] - base['obj']) / base['obj'], 2),
        })

    # Kapasitetsreduksjon (alpha = 3)
    p = dict(params); p['alpha'] = 3
    r = build_and_solve(demand, p)
    rows.append({
        'scenario': 'Kapasitet: alpha = 3',
        'detalj': 'Produktiviteten reduseres med 25 %',
        'obj': round(r['obj'], 2),
        'rel_endr_%': round(100 * (r['obj'] - base['obj']) / base['obj'], 2),
    })

    # Kapasitetsokning (alpha = 5)
    p = dict(params); p['alpha'] = 5
    r = build_and_solve(demand, p)
    rows.append({
        'scenario': 'Kapasitet: alpha = 5',
        'detalj': 'Produktiviteten oekes med 25 %',
        'obj': round(r['obj'], 2),
        'rel_endr_%': round(100 * (r['obj'] - base['obj']) / base['obj'], 2),
    })

    # Overtidsbegrensning kuttet
    p = dict(params); p['O_max'] = 20
    r = build_and_solve(demand, p)
    rows.append({
        'scenario': 'Overtid: $O_{max}$ = 20',
        'detalj': 'Halvert overtidskapasitet',
        'obj': round(r['obj'], 2),
        'rel_endr_%': round(100 * (r['obj'] - base['obj']) / base['obj'], 2),
    })

    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: VALIDERING / STRESSTEST")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / 'boat_demand.csv')
    demand = df['etterspoersel'].values.astype(int)
    params = parameters()

    table = scenario_table(demand, params)
    path = OUTPUT_DIR / 'step05_stress.csv'
    table.to_csv(path, index=False)
    print(f"Stresstest lagret: {path}")
    print("\n" + table.to_string(index=False))

    with open(OUTPUT_DIR / 'step05_stress.json', 'w', encoding='utf-8') as f:
        json.dump(table.to_dict(orient='records'), f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
