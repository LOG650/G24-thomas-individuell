"""
Steg 4: Losning av MIP med PuLP/CBC for liten instans
======================================================
Formulerer og losser enkeltmaskin-sekvenseringsproblemet med vektet
tardiness og setup-tider.

Formulering (prioriterer tett LP-relaksering): "predecessor"-basert
med disjunktive skranker.

    y_{ij} = 1 hvis jobb i er DIREKTE forgjenger til jobb j.
    Dummy start  0 og dummy slutt n+1.

Skranker:
    (i)   Hver jobb j har akkurat én forgjenger:   sum_i y_{ij} = 1 for j in J.
    (ii)  Hver jobb i har akkurat én etterfolger:  sum_j y_{ij} = 1 for i in J.
    (iii) Start (0) har én etterfolger:            sum_j y_{0j} = 1.
    (iv)  Slutt (n+1) har én forgjenger:           sum_i y_{i,n+1} = 1.
    (v)   Fullforingstid via predecessor:          C_j >= C_i + s_{ij} + p_j - M(1-y_{ij}).
    (vi)  Ingen syklus (MTZ):                      u_i - u_j + N*y_{ij} <= N-1.
    (vii) Tardiness:                               T_j >= C_j - d_j, T_j >= 0.

Objektiv:
    min sum_j w_j T_j.
"""

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def solve_mip(df: pd.DataFrame, S: np.ndarray, time_limit: int = 120) -> dict:
    """Los sekvensering med CBC via PuLP. Returnerer sekvens + statistikk."""
    jobs = df['job_id'].tolist()
    n = len(jobs)
    p = dict(zip(df['job_id'], df['p']))
    d = dict(zip(df['job_id'], df['d']))
    w = dict(zip(df['job_id'], df['w']))

    start_node = 0
    end_node = n + 1

    total_p = float(df['p'].sum())
    total_s = float(S[1:, 1:].max()) * n
    M = total_p + total_s + float(df['d'].max()) + 50.0

    prob = pulp.LpProblem('WeightedTardiness', pulp.LpMinimize)

    # Immediate-predecessor binaries y_{ij}.
    # i in {0} U J, j in J U {n+1}, i != j.
    pred_nodes = [start_node] + jobs
    succ_nodes = jobs + [end_node]

    y = {}
    for i in pred_nodes:
        for j in succ_nodes:
            if i == j:
                continue
            if i == start_node and j == end_node:
                continue
            y[i, j] = pulp.LpVariable(f'y_{i}_{j}', cat='Binary')

    # Continuous completion times
    C = {j: pulp.LpVariable(f'C_{j}', lowBound=0) for j in jobs}
    # MTZ ordering variables
    u = {j: pulp.LpVariable(f'u_{j}', lowBound=1, upBound=n) for j in jobs}
    # Tardiness
    T = {j: pulp.LpVariable(f'T_{j}', lowBound=0) for j in jobs}

    # Objective
    prob += pulp.lpSum(w[j] * T[j] for j in jobs)

    # (i) Hver jobb j har akkurat én forgjenger
    for j in jobs:
        prob += pulp.lpSum(y[i, j] for i in pred_nodes
                           if (i, j) in y) == 1, f'pred_{j}'

    # (ii) Hver jobb i har akkurat én etterfolger
    for i in jobs:
        prob += pulp.lpSum(y[i, j] for j in succ_nodes
                           if (i, j) in y) == 1, f'succ_{i}'

    # (iii) Start (0) -> nøyaktig én jobb
    prob += pulp.lpSum(y[start_node, j] for j in jobs
                       if (start_node, j) in y) == 1, 'start'

    # (iv) Nøyaktig én jobb -> slutt (n+1)
    prob += pulp.lpSum(y[i, end_node] for i in jobs
                       if (i, end_node) in y) == 1, 'end'

    # (v) Fullforingstid ifolge predecessor (inkluder setup og prosessering)
    #     For startjobb: C_j >= 0 + 0 + p_j = p_j.
    for j in jobs:
        prob += C[j] >= p[j] - M * (1 - y[start_node, j]), f'Cstart_{j}'
    for i in jobs:
        for j in jobs:
            if i == j:
                continue
            prob += C[j] >= C[i] + S[i, j] + p[j] - M * (1 - y[i, j]), f'Csucc_{i}_{j}'

    # (vi) MTZ-skranker for aa hindre sub-sykler blant jobbene
    for i in jobs:
        for j in jobs:
            if i == j:
                continue
            prob += u[i] - u[j] + n * y[i, j] <= n - 1, f'mtz_{i}_{j}'

    # (vii) Tardiness
    for j in jobs:
        prob += T[j] >= C[j] - d[j], f'tard_{j}'

    # Warm-start fra beste dispatch-losning (EDD/ATC) slik at CBC
    # raskt finner god ovre grense. Vi velger den av dem som gir
    # lavest vektet tardiness.
    from step02_dispatch_heuristikker import (
        edd_sequence, atc_sequence, evaluate_sequence,
    )
    edd_seq = edd_sequence(df)
    atc_seq = atc_sequence(df, S)
    edd_val = evaluate_sequence(edd_seq, df, S)['weighted_tardiness']
    atc_val = evaluate_sequence(atc_seq, df, S)['weighted_tardiness']
    warm_seq = edd_seq if edd_val <= atc_val else atc_seq

    # Sett initial verdier for y, C, T, u basert paa warm_seq
    prev_node = start_node
    t_sim = 0.0
    for pos, jj in enumerate(warm_seq, start=1):
        key = (prev_node, jj)
        if key in y:
            y[key].setInitialValue(1)
        t_sim += (S[prev_node, jj] if prev_node != start_node else 0.0) + p[jj]
        C[jj].setInitialValue(t_sim)
        T[jj].setInitialValue(max(0.0, t_sim - d[jj]))
        u[jj].setInitialValue(pos)
        prev_node = jj
    # Fra siste jobb til dummy slutt
    key_end = (prev_node, end_node)
    if key_end in y:
        y[key_end].setInitialValue(1)
    # Sett alle ovrige y til 0
    for k_ij, var in y.items():
        if var.value() is None:
            var.setInitialValue(0)

    # Los
    solver = pulp.PULP_CBC_CMD(msg=True, timeLimit=time_limit, warmStart=True)
    t_start = time.time()
    prob.solve(solver)
    t_elapsed = time.time() - t_start

    status = pulp.LpStatus[prob.status]
    print(f"  PuLP status: {status}, tid: {t_elapsed:.1f} s, "
          f"tidsgrense: {time_limit} s")

    # Ekstraher sekvens ved aa traversere y
    sequence = []
    current = start_node
    visited = set()
    for _ in range(n):
        found = None
        for j in succ_nodes:
            key = (current, j)
            if key in y and pulp.value(y[key]) is not None and pulp.value(y[key]) > 0.5:
                found = j
                break
        if found is None or found == end_node or found in visited:
            break
        sequence.append(int(found))
        visited.add(found)
        current = found

    # Ekstraher verdier
    completions = {int(j): round(float(pulp.value(C[j])), 3) for j in jobs}
    tardiness = {int(j): round(max(0.0, float(pulp.value(C[j])) - d[j]), 3) for j in jobs}
    wtard = sum(w[j] * tardiness[int(j)] for j in jobs)
    makespan = max(completions.values())
    num_tardy = sum(1 for j in jobs if tardiness[int(j)] > 1e-6)

    return {
        'status': status,
        'sequence': sequence,
        'completions': completions,
        'tardiness': tardiness,
        'weighted_tardiness': round(float(wtard), 3),
        'makespan': round(float(makespan), 3),
        'num_tardy': int(num_tardy),
        'solve_time_s': round(t_elapsed, 3),
        'objective': round(float(pulp.value(prob.objective)), 3),
    }


def plot_gantt(result: dict, df: pd.DataFrame, S: np.ndarray,
               output_path: Path, title: str) -> None:
    """Gantt-diagram: bar per jobb med setup i lys grau."""
    p = dict(zip(df['job_id'], df['p']))
    d = dict(zip(df['job_id'], df['d']))
    w = dict(zip(df['job_id'], df['w']))

    fig, ax = plt.subplots(figsize=(12, 5))

    color_by_w = {1: '#8CC8E5', 2: '#97D4B7', 5: '#ED9F9E'}

    t = 0.0
    prev = 0
    yticks = []
    ylabels = []
    for idx, j in enumerate(result['sequence']):
        y = idx
        setup = S[prev, j]
        if setup > 0:
            ax.barh(y, setup, left=t, height=0.7,
                    color='#CBD5E1', edgecolor='#556270', linewidth=0.5)
        t += setup
        ax.barh(y, p[j], left=t, height=0.7,
                color=color_by_w[int(w[j])], edgecolor='#1F2933', linewidth=0.8)

        tardy = (t + p[j]) > d[j] + 1e-9
        ax.plot([d[j], d[j]], [y - 0.35, y + 0.35], color='#961D1C',
                linestyle='--', linewidth=1.2)

        ax.text(t + p[j] / 2, y, f'J{j}', ha='center', va='center',
                fontsize=8, color='#1F2933', fontweight='bold')

        if tardy:
            ax.text(t + p[j] + 0.15, y, '*', color='#961D1C',
                    fontsize=12, fontweight='bold', va='center')

        t += p[j]
        prev = j
        yticks.append(y)
        ylabels.append(f'pos {idx + 1}')

    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Tid (timer)', fontsize=12)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.grid(True, axis='x', alpha=0.3)

    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#8CC8E5', edgecolor='#1F2933', label=r'$w_j = 1$'),
        Patch(facecolor='#97D4B7', edgecolor='#1F2933', label=r'$w_j = 2$'),
        Patch(facecolor='#ED9F9E', edgecolor='#1F2933', label=r'$w_j = 5$'),
        Patch(facecolor='#CBD5E1', edgecolor='#556270', label='Setup'),
    ]
    ax.legend(handles=legend_elements, loc='lower right', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 4: MIP-LOSNING MED CBC')
    print('=' * 60)

    df = pd.read_csv(DATA_DIR / 'jobs_small.csv')
    S = np.loadtxt(DATA_DIR / 'setup_small.csv', delimiter=',')

    print(f"\nLoser enkeltmaskin MIP med N = {len(df)} jobber...")
    result = solve_mip(df, S, time_limit=180)

    print(f"\nStatus: {result['status']}")
    print(f"Optimal sekvens: {result['sequence']}")
    print(f"Sum w_j T_j (objektiv):  {result['weighted_tardiness']:.2f}")
    print(f"Makespan:                 {result['makespan']:.2f}")
    print(f"Antall tardy jobber:      {result['num_tardy']}")
    print(f"Losetid CBC:              {result['solve_time_s']:.2f} s")

    with open(OUTPUT_DIR / 'step04_mip_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step04_mip_result.json'}")

    plot_gantt(result, df, S,
               OUTPUT_DIR / 'seqmip_gantt_mip.png',
               f'MIP (optimal): N = {len(df)}, '
               fr'$\sum w_j T_j$ = {result["weighted_tardiness"]:.1f}')

    # Sammenligne med SPT-Gantt paa samme instans
    from step02_dispatch_heuristikker import spt_sequence, evaluate_sequence
    spt_res = evaluate_sequence(spt_sequence(df), df, S)
    plot_gantt(spt_res, df, S,
               OUTPUT_DIR / 'seqmip_gantt_spt.png',
               f'SPT (heuristikk): N = {len(df)}, '
               fr'$\sum w_j T_j$ = {spt_res["weighted_tardiness"]:.1f}')


if __name__ == '__main__':
    main()
