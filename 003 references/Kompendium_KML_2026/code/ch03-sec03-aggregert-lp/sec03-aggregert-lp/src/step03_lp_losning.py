"""
Steg 3: LP-loesning
===================
Formulerer og loeser LP-modellen med PuLP (CBC-solver).
Henter ut primal- og dualvariabler (skyggepriser) og lagrer alt
som JSON + CSV + figurer.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pulp

from step01_datainnsamling import parameters, MONTHS_NO

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

C_PROD = '#8CC8E5'
C_OVER = '#BD94D7'
C_INV = '#97D4B7'
C_DEMAND = '#1F6587'
C_PROD_DARK = '#1F6587'
C_OVER_DARK = '#5A2C77'
C_INV_DARK = '#307453'


def build_and_solve(demand: np.ndarray, params: dict) -> dict:
    """Bygg LP med PuLP og returner all relevant informasjon."""
    T = params['T']
    c_P, c_O, c_I = params['c_P'], params['c_O'], params['c_I']
    c_H, c_F = params['c_H'], params['c_F']
    O_max = params['O_max']
    alpha = params['alpha']
    I_0, W_0 = params['I_0'], params['W_0']

    model = pulp.LpProblem('AggregatePP', pulp.LpMinimize)

    # Beslutningsvariabler
    P = [pulp.LpVariable(f'P_{t}', lowBound=0) for t in range(1, T + 1)]
    O = [pulp.LpVariable(f'O_{t}', lowBound=0, upBound=O_max) for t in range(1, T + 1)]
    I = [pulp.LpVariable(f'I_{t}', lowBound=0) for t in range(1, T + 1)]
    H = [pulp.LpVariable(f'H_{t}', lowBound=0) for t in range(1, T + 1)]
    F = [pulp.LpVariable(f'F_{t}', lowBound=0) for t in range(1, T + 1)]
    W = [pulp.LpVariable(f'W_{t}', lowBound=0) for t in range(1, T + 1)]

    # Objekt
    model += pulp.lpSum(
        c_P * P[t] + c_O * O[t] + c_I * I[t] + c_H * H[t] + c_F * F[t]
        for t in range(T)
    ), 'TotalCost'

    # Skranker
    inv_names = []
    wf_names = []
    prod_names = []
    for t in range(T):
        prev_I = I_0 if t == 0 else I[t - 1]
        prev_W = W_0 if t == 0 else W[t - 1]
        inv_name = f'InvBal_{t + 1}'
        wf_name = f'WfBal_{t + 1}'
        prod_name = f'ProdCap_{t + 1}'
        model += (prev_I + P[t] + O[t] - demand[t] == I[t]), inv_name
        model += (prev_W + H[t] - F[t] == W[t]), wf_name
        model += (P[t] - alpha * W[t] <= 0), prod_name
        inv_names.append(inv_name)
        wf_names.append(wf_name)
        prod_names.append(prod_name)

    # Solver
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', f'LP ikke optimal: {pulp.LpStatus[status]}'

    def _pi(name: str) -> float:
        c = model.constraints.get(name)
        if c is None or c.pi is None:
            return 0.0
        return float(c.pi)

    # Hent ut verdier
    result = {
        'status': pulp.LpStatus[status],
        'obj': float(pulp.value(model.objective)),
        'P': [float(pulp.value(v)) for v in P],
        'O': [float(pulp.value(v)) for v in O],
        'I': [float(pulp.value(v)) for v in I],
        'H': [float(pulp.value(v)) for v in H],
        'F': [float(pulp.value(v)) for v in F],
        'W': [float(pulp.value(v)) for v in W],
        # Skyggepriser
        'dual_invbal': [_pi(n) for n in inv_names],
        'dual_wfbal': [_pi(n) for n in wf_names],
        'dual_prodcap': [_pi(n) for n in prod_names],
    }
    return result


def plot_plan_bar(result: dict, demand: np.ndarray, output_path: Path) -> None:
    """Stablet soeylediagram: P_t + O_t og etterspoerselslinje + lagerlinje."""
    T = len(demand)
    t = np.arange(1, T + 1)
    P = np.array(result['P'])
    O = np.array(result['O'])
    I = np.array(result['I'])

    fig, ax = plt.subplots(figsize=(11, 5.5))

    ax.bar(t, P, color=C_PROD, edgecolor=C_PROD_DARK, linewidth=1.0,
           label='Ordinaer produksjon $P_t$')
    ax.bar(t, O, bottom=P, color=C_OVER, edgecolor=C_OVER_DARK, linewidth=1.0,
           label='Overtid $O_t$')
    ax.plot(t, demand, 'o-', color=C_DEMAND, linewidth=2.0, markersize=6,
            label='Etterspoersel $D_t$')
    ax.plot(t, I, 's--', color=C_INV_DARK, linewidth=1.6, markersize=5,
            label='Lager $I_t$ (slutt av mnd.)')

    ax.set_xticks(t)
    ax.set_xticklabels(MONTHS_NO, fontsize=10)
    ax.set_xlabel('$t$', fontsize=13)
    ax.set_ylabel('Antall baater', fontsize=12)
    ax.set_title('Optimal produksjonsplan: $P_t$, $O_t$, $I_t$ vs. $D_t$',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9, ncol=2)
    ax.grid(True, alpha=0.3, axis='y')
    ax.tick_params(axis='both', labelsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cost_breakdown(result: dict, params: dict, output_path: Path) -> None:
    """Kostnadsfordeling (pie + bar)."""
    c_P, c_O, c_I = params['c_P'], params['c_O'], params['c_I']
    c_H, c_F = params['c_H'], params['c_F']

    components = {
        'Ordinaer produksjon': c_P * sum(result['P']),
        'Overtid': c_O * sum(result['O']),
        'Lager': c_I * sum(result['I']),
        'Ansettelse': c_H * sum(result['H']),
        'Oppsigelse': c_F * sum(result['F']),
    }
    labels = list(components.keys())
    values = np.array([components[k] for k in labels])

    fig, ax = plt.subplots(figsize=(9.5, 5))
    colors = ['#8CC8E5', '#BD94D7', '#97D4B7', '#F6BA7C', '#ED9F9E']
    edge = ['#1F6587', '#5A2C77', '#307453', '#9C540B', '#961D1C']
    bars = ax.barh(labels, values / 1e3, color=colors, edgecolor=edge, linewidth=1.2)
    total = values.sum()
    for bar, v in zip(bars, values):
        pct = 100 * v / total if total > 0 else 0
        ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
                f'{v/1e3:,.0f} k  ({pct:.1f}%)'.replace(',', ' '),
                va='center', fontsize=10, color='#1F2933')
    ax.set_xlabel('Kostnad (tusen NOK)', fontsize=12)
    ax.set_title('Kostnadsfordeling i optimal plan', fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    ax.set_xlim(0, (values.max() / 1e3) * 1.35)
    ax.tick_params(axis='both', labelsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def solve_with_scipy(demand: np.ndarray, params: dict) -> float:
    """Kryssjekk med scipy.optimize.linprog for robusthet (bare obj)."""
    from scipy.optimize import linprog

    T = params['T']
    # Variabelrekkefoelge: [P_1..P_T, O_1..O_T, I_1..I_T, H_1..H_T, F_1..F_T, W_1..W_T]
    n = 6 * T

    def idx(block, t):
        return block * T + t  # 0-indeksert

    c = np.zeros(n)
    for t in range(T):
        c[idx(0, t)] = params['c_P']
        c[idx(1, t)] = params['c_O']
        c[idx(2, t)] = params['c_I']
        c[idx(3, t)] = params['c_H']
        c[idx(4, t)] = params['c_F']
    # c_W = 0

    # Likhetsskranker
    A_eq_rows = []
    b_eq = []
    # Lagerbalanse: I_{t-1} + P_t + O_t - D_t = I_t  =>
    # P_t + O_t - I_t + I_{t-1} = D_t      (I_0 kjent)
    for t in range(T):
        row = np.zeros(n)
        row[idx(0, t)] = 1.0   # P_t
        row[idx(1, t)] = 1.0   # O_t
        row[idx(2, t)] = -1.0  # -I_t
        if t >= 1:
            row[idx(2, t - 1)] = 1.0
            rhs = float(demand[t])
        else:
            rhs = float(demand[t]) - params['I_0']
        A_eq_rows.append(row)
        b_eq.append(rhs)

    # Arbeidsbalanse: W_{t-1} + H_t - F_t - W_t = 0
    for t in range(T):
        row = np.zeros(n)
        row[idx(3, t)] = 1.0   # H_t
        row[idx(4, t)] = -1.0  # -F_t
        row[idx(5, t)] = -1.0  # -W_t
        if t >= 1:
            row[idx(5, t - 1)] = 1.0
            rhs = 0.0
        else:
            rhs = -params['W_0']
        A_eq_rows.append(row)
        b_eq.append(rhs)

    A_eq = np.array(A_eq_rows)
    b_eq = np.array(b_eq)

    # Uliketsskranker: P_t - alpha W_t <= 0
    A_ub_rows = []
    b_ub = []
    for t in range(T):
        row = np.zeros(n)
        row[idx(0, t)] = 1.0
        row[idx(5, t)] = -float(params['alpha'])
        A_ub_rows.append(row)
        b_ub.append(0.0)
    A_ub = np.array(A_ub_rows)
    b_ub = np.array(b_ub)

    # Bounds
    bounds = []
    for block in range(6):
        for t in range(T):
            if block == 1:  # O_t
                bounds.append((0.0, float(params['O_max'])))
            else:
                bounds.append((0.0, None))

    res = linprog(c, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method='highs')
    assert res.success, f"scipy linprog feilet: {res.message}"
    return float(res.fun)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: LP-LOESNING (PuLP / CBC)")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / 'boat_demand.csv')
    demand = df['etterspoersel'].values.astype(int)
    params = parameters()

    result = build_and_solve(demand, params)
    scipy_obj = solve_with_scipy(demand, params)

    print(f"\nStatus (PuLP/CBC):  {result['status']}")
    print(f"Total kostnad:      {result['obj']:,.2f} NOK".replace(',', ' '))
    print(f"Total kostnad (scipy): {scipy_obj:,.2f} NOK".replace(',', ' '))
    print(f"Avvik CBC vs HiGHS: {abs(result['obj'] - scipy_obj):.4f}")

    # Loesningstabell
    df_plan = pd.DataFrame({
        'maaned': MONTHS_NO,
        't': np.arange(1, params['T'] + 1),
        'D_t': demand,
        'P_t': np.round(result['P'], 2),
        'O_t': np.round(result['O'], 2),
        'I_t': np.round(result['I'], 2),
        'H_t': np.round(result['H'], 2),
        'F_t': np.round(result['F'], 2),
        'W_t': np.round(result['W'], 2),
    })
    plan_path = OUTPUT_DIR / 'step03_plan.csv'
    df_plan.to_csv(plan_path, index=False)
    print(f"\nPlan lagret: {plan_path}")

    # Skyggepriser
    df_dual = pd.DataFrame({
        'maaned': MONTHS_NO,
        't': np.arange(1, params['T'] + 1),
        'dual_invbal': np.round(result['dual_invbal'], 2),
        'dual_wfbal': np.round(result['dual_wfbal'], 2),
        'dual_prodcap': np.round(result['dual_prodcap'], 2),
    })
    dual_path = OUTPUT_DIR / 'step03_duals.csv'
    df_dual.to_csv(dual_path, index=False)
    print(f"Skyggepriser lagret: {dual_path}")

    # Figurer
    plot_plan_bar(result, demand, OUTPUT_DIR / 'agglp_plan_bar.png')
    plot_cost_breakdown(result, params, OUTPUT_DIR / 'agglp_cost_breakdown.png')

    # Oppsummering
    summary = {
        'status': result['status'],
        'obj_cbc': round(result['obj'], 2),
        'obj_scipy': round(scipy_obj, 2),
        'cost_prod': round(params['c_P'] * sum(result['P']), 2),
        'cost_overtime': round(params['c_O'] * sum(result['O']), 2),
        'cost_inv': round(params['c_I'] * sum(result['I']), 2),
        'cost_hire': round(params['c_H'] * sum(result['H']), 2),
        'cost_fire': round(params['c_F'] * sum(result['F']), 2),
        'total_P': round(sum(result['P']), 2),
        'total_O': round(sum(result['O']), 2),
        'total_I': round(sum(result['I']), 2),
        'total_H': round(sum(result['H']), 2),
        'total_F': round(sum(result['F']), 2),
    }
    with open(OUTPUT_DIR / 'step03_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering:")
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
