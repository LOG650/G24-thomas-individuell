"""
Steg 3: MIP-formulering for enkeltmaskin-sekvensering
=====================================================
Formulerer det matematiske problemet og dokumenterer modellstorrelsen
for liten og stor instans. Ingen optimering finner sted her --- det
skjer i step04.

Vi bruker predecessor-basert formulering:

    y_{ij} = 1  hvis jobb i er direkte forgjenger til jobb j.

med dummy startnode 0 og dummy sluttnode n+1.

Variabler:
    y_{ij} in {0,1}  for (i,j) i nettverket, i != j      -> N^2 + 2N binaere
    C_j >= 0         for j = 1..N                         -> N kontinuerlige
    T_j >= 0         for j = 1..N                         -> N kontinuerlige
    u_j in [1,N]     for j = 1..N (MTZ-ordning)           -> N kontinuerlige

Skranker:
    (i)   Hver jobb har én forgjenger                   -> N
    (ii)  Hver jobb har én etterfolger                  -> N
    (iii) Startnoden (0) har én etterfolger             -> 1
    (iv)  Sluttnoden (n+1) har én forgjenger            -> 1
    (v)   C_j >= C_i + s_{ij} + p_j - M(1 - y_{ij})     -> (N+1)*N  (ca.)
    (vi)  MTZ: u_i - u_j + N*y_{ij} <= N-1              -> N*(N-1)
    (vii) T_j >= C_j - d_j                              -> N
"""

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def model_size(n: int) -> dict:
    """Beregn antall variabler og skranker i MIP-formuleringen."""
    # y_{ij}: (n+2 noder) x (n+2 noder) uten sykler til/fra seg selv.
    # I praksis: for j in J (n stk): sum_i y_{ij}, og for i in J, sum_j y_{ij}.
    # Antall y-variabler (tilnaermet): (n+1)*n + n*(n+1) - n**2 tillatt
    # Her: i in pred_nodes = {0} U J, j in succ_nodes = J U {n+1}, i != j,
    # og (0, n+1) utelukkes. Antallet = (n+1)*(n+1) - n - 1
    binary_y = (n + 1) * (n + 1) - n - 1
    cont = 3 * n  # C_j, T_j, u_j

    # Skranker:
    #  (i)   Pred: N
    #  (ii)  Succ: N
    #  (iii) Start: 1
    #  (iv)  End:   1
    #  (v)   Completion: N fra start + N*(N-1) mellom jobber
    #  (vi)  MTZ: N*(N-1)
    #  (vii) Tardiness: N
    constraints = 2 * n + 2 + n + n * (n - 1) + n * (n - 1) + n
    return {
        'binary_y': int(binary_y),
        'continuous': int(cont),
        'total_variables': int(binary_y + cont),
        'constraints': int(constraints),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 3: MIP-FORMULERING')
    print('=' * 60)

    summary = {}
    for tag in ['small', 'large']:
        df = pd.read_csv(DATA_DIR / f'jobs_{tag}.csv')
        n = len(df)
        sizes = model_size(n)
        summary[tag] = {'n': n, **sizes}

        print(f"\n--- {tag.upper()} (N = {n}) ---")
        print(f"  Binaere variabler y_{{i,j}}:    {sizes['binary_y']:>10,}")
        print(f"  Kontinuerlige variabler:      {sizes['continuous']:>10,}")
        print(f"  Totalt antall variabler:      {sizes['total_variables']:>10,}")
        print(f"  Antall skranker:              {sizes['constraints']:>10,}")

    with open(OUTPUT_DIR / 'step03_model_size.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nModellstorrelse lagret: {OUTPUT_DIR / 'step03_model_size.json'}")


if __name__ == '__main__':
    main()
