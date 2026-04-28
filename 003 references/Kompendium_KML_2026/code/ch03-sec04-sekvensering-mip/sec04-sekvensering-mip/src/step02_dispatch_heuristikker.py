"""
Steg 2: Dispatch-heuristikker (SPT, EDD, ATC)
=============================================
Implementerer tre klassiske dispatch-regler paa enkeltmaskin-problemet:

    * SPT (Shortest Processing Time): sorter etter p_j voksende.
    * EDD (Earliest Due Date): sorter etter d_j voksende.
    * ATC (Apparent Tardiness Cost): dynamisk regel som veier
      vekt, prosesseringstid og gjenstaaende slakk.

For hver regel beregnes sekvens og vektet tardiness. Vi utvider
maskin-scheduleringen med setup-tid s_{ij}: tid for ferdigstillelse
av jobb j paa posisjon k er:

    C_{[k]} = C_{[k-1]} + s_{[k-1],[k]} + p_{[k]}.

Resultatene brukes i step06 som baseline for MIP og SA.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def load_instance(tag: str):
    """Last jobber og setup-matrise for 'small' eller 'large'."""
    df = pd.read_csv(DATA_DIR / f'jobs_{tag}.csv')
    S = np.loadtxt(DATA_DIR / f'setup_{tag}.csv', delimiter=',')
    return df, S


def evaluate_sequence(seq, df: pd.DataFrame, S: np.ndarray) -> dict:
    """Beregn fullforingstid, tardiness og vektet tardiness for gitt sekvens.

    seq inneholder job_id (1-indeksert). Setup-matrisen S har dim (n+1, n+1)
    der indeks 0 er startjobb (dummy).
    """
    p = dict(zip(df['job_id'], df['p']))
    d = dict(zip(df['job_id'], df['d']))
    w = dict(zip(df['job_id'], df['w']))

    completions = {}
    t = 0.0
    prev = 0  # startjobb
    for j in seq:
        t += S[prev, j] + p[j]
        completions[j] = t
        prev = j

    tardiness = {j: max(0.0, completions[j] - d[j]) for j in seq}
    wtard = sum(w[j] * tardiness[j] for j in seq)
    makespan = max(completions.values())
    total_tard = sum(tardiness.values())
    num_tardy = sum(1 for j in seq if tardiness[j] > 1e-9)

    return {
        'sequence': [int(j) for j in seq],
        'completions': {int(j): round(float(completions[j]), 3) for j in seq},
        'tardiness': {int(j): round(float(tardiness[j]), 3) for j in seq},
        'weighted_tardiness': round(float(wtard), 3),
        'total_tardiness': round(float(total_tard), 3),
        'makespan': round(float(makespan), 3),
        'num_tardy': int(num_tardy),
    }


def spt_sequence(df: pd.DataFrame) -> list[int]:
    return df.sort_values(['p', 'job_id']).job_id.tolist()


def edd_sequence(df: pd.DataFrame) -> list[int]:
    return df.sort_values(['d', 'job_id']).job_id.tolist()


def atc_sequence(df: pd.DataFrame, S: np.ndarray, K: float = 2.0) -> list[int]:
    """Apparent Tardiness Cost dispatch (Vepsalainen & Morton 1987).

    Prioritet for jobb j pa tidspunkt t, gitt gjennomsnittlig
    prosesseringstid p_bar:

        pi_j(t) = (w_j / p_j) * exp( -max(d_j - p_j - t, 0) / (K * p_bar) )

    Vi inkluderer setup ved aa legge setup mot siste valgte jobb i 't'.
    """
    jobs = df.copy()
    p_bar = float(jobs['p'].mean())
    remaining = set(jobs['job_id'].tolist())
    seq: list[int] = []
    t = 0.0
    prev = 0

    while remaining:
        best_j = None
        best_pi = -np.inf
        for j in remaining:
            pj = float(jobs.loc[jobs['job_id'] == j, 'p'].iloc[0])
            dj = float(jobs.loc[jobs['job_id'] == j, 'd'].iloc[0])
            wj = float(jobs.loc[jobs['job_id'] == j, 'w'].iloc[0])
            slack = max(dj - pj - (t + S[prev, j]), 0.0)
            pi = (wj / pj) * np.exp(-slack / (K * p_bar))
            if pi > best_pi:
                best_pi = pi
                best_j = j
        seq.append(int(best_j))
        t += S[prev, best_j] + float(jobs.loc[jobs['job_id'] == best_j, 'p'].iloc[0])
        prev = best_j
        remaining.remove(best_j)

    return seq


def plot_tardiness_bar(results: dict, n_tag: str, output_path: Path) -> None:
    """Stolpediagram for vektet tardiness per heuristikk."""
    methods = list(results.keys())
    values = [results[m]['weighted_tardiness'] for m in methods]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    colors = ['#8CC8E5', '#97D4B7', '#F6BA7C']
    bars = ax.bar(methods, values, color=colors, edgecolor='#1F2933', linewidth=0.8)
    for b, v in zip(bars, values):
        ax.text(b.get_x() + b.get_width() / 2, b.get_height() + max(values) * 0.01,
                f'{v:.1f}', ha='center', fontsize=10, color='#1F2933')
    ax.set_ylabel(r'Vektet tardiness $\sum_j w_j T_j$ (timer)', fontsize=12)
    ax.set_title(f'Dispatch-heuristikker, N = {n_tag}', fontsize=12, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 2: DISPATCH-HEURISTIKKER (SPT, EDD, ATC)')
    print('=' * 60)

    all_results = {}
    for tag in ['small', 'large']:
        df, S = load_instance(tag)

        seq_spt = spt_sequence(df)
        seq_edd = edd_sequence(df)
        seq_atc = atc_sequence(df, S)

        res_spt = evaluate_sequence(seq_spt, df, S)
        res_edd = evaluate_sequence(seq_edd, df, S)
        res_atc = evaluate_sequence(seq_atc, df, S)

        all_results[tag] = {
            'SPT': res_spt,
            'EDD': res_edd,
            'ATC': res_atc,
        }

        print(f"\n--- {tag.upper()} (N = {len(df)}) ---")
        for name, r in [('SPT', res_spt), ('EDD', res_edd), ('ATC', res_atc)]:
            print(
                f"  {name}: Sum w_j T_j = {r['weighted_tardiness']:8.2f}, "
                f"Makespan = {r['makespan']:6.2f}, "
                f"# tardy = {r['num_tardy']}"
            )

    # Lagre samlet
    with open(OUTPUT_DIR / 'step02_dispatch_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step02_dispatch_results.json'}")

    # Stolpediagram for liten instans
    df_small, _ = load_instance('small')
    plot_tardiness_bar(all_results['small'], str(len(df_small)),
                       OUTPUT_DIR / 'seqmip_dispatch_small.png')


if __name__ == '__main__':
    main()
