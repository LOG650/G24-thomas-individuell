"""
Steg 3: Diskret hendelsessimulering (DES) av M/M/1
==================================================
Bruker simpy til aa simulere 1000 lastebiler som ankommer og betjenes ved
en enkelt tollstasjon. Sammenligner empiriske ventetids- og kolengde-
estimater med de analytiske M/M/1-formlene fra steg 2.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import simpy

from step01_datainnsamling import LAMBDA_TRUE, MU_TRUE
from step02_analytisk import mm1_formler

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
SEED = 20260420
N_KUNDER = 1000


def simuler_mm1(lmbda: float, mu: float, n_kunder: int, seed: int) -> dict:
    """Kjoer diskret hendelsessimulering av M/M/1 med simpy.

    Registrerer ventetider per kunde (Wq) og tidsvektede kolengder
    (L og Lq beregnes via Little: L = lambda * W).
    """
    rng = np.random.default_rng(seed)
    env = simpy.Environment()
    server = simpy.Resource(env, capacity=1)

    ventetider = []     # tid i ko (Wq) per kunde
    total_tider = []    # tid i systemet (W) per kunde
    hendelser = []      # (tid, antall_i_system) for tidsvektet snitt

    hendelser.append((0.0, 0))
    state = {'i_system': 0}

    def oppdater_state(env, delta):
        state['i_system'] += delta
        hendelser.append((env.now, state['i_system']))

    def kunde(env, navn, server, ventetider, total_tider):
        ankomst = env.now
        oppdater_state(env, +1)
        with server.request() as req:
            yield req
            starttid = env.now
            ventetid = starttid - ankomst
            ventetider.append(ventetid)
            bet_tid = rng.exponential(scale=1.0 / mu)
            yield env.timeout(bet_tid)
            total_tider.append(env.now - ankomst)
            oppdater_state(env, -1)

    def generator(env, server):
        for i in range(n_kunder):
            mellom = rng.exponential(scale=1.0 / lmbda)
            yield env.timeout(mellom)
            env.process(kunde(env, i, server, ventetider, total_tider))

    env.process(generator(env, server))
    env.run()

    # Tidsvektet snitt av antall i system og i ko
    hendelser.sort(key=lambda x: x[0])
    tider = np.array([h[0] for h in hendelser])
    n_inn = np.array([h[1] for h in hendelser])
    delta_t = np.diff(tider)
    # Bruker antallet *for* hendelsen i hvert intervall
    n_prev = n_inn[:-1]
    T = tider[-1]
    if T <= 0:
        L_emp = np.nan
        Lq_emp = np.nan
    else:
        L_emp = float(np.sum(n_prev * delta_t) / T)
        # Antall i ko = max(n_i_system - 1, 0)
        nq_prev = np.maximum(n_prev - 1, 0)
        Lq_emp = float(np.sum(nq_prev * delta_t) / T)

    Wq_emp = float(np.mean(ventetider))
    W_emp = float(np.mean(total_tider))

    return {
        'Wq_emp': Wq_emp,
        'W_emp': W_emp,
        'L_emp': L_emp,
        'Lq_emp': Lq_emp,
        'sluttid': float(T),
        'n_kunder': int(n_kunder),
        'ventetider': ventetider,
        'hendelser': (tider.tolist(), n_inn.tolist()),
    }


def plot_sammenligning(analyt: dict, emp: dict, output_path: Path) -> None:
    """Sol-diagram: analytisk vs empirisk for L, Lq, W, Wq."""
    labels = ['L', r'$L_q$', 'W (min)', r'$W_q$ (min)']
    analyt_vals = [
        analyt['L'],
        analyt['Lq'],
        analyt['W'] * 60.0,
        analyt['Wq'] * 60.0,
    ]
    emp_vals = [
        emp['L_emp'],
        emp['Lq_emp'],
        emp['W_emp'] * 60.0,
        emp['Wq_emp'] * 60.0,
    ]

    x = np.arange(len(labels))
    bredde = 0.36
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.bar(x - bredde / 2, analyt_vals, bredde, color='#8CC8E5',
           edgecolor='#1F6587', label='Analytisk (M/M/1)')
    ax.bar(x + bredde / 2, emp_vals, bredde, color='#F6BA7C',
           edgecolor='#9C540B', label='Simulering (DES)')
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('Verdi', fontsize=11)
    ax.set_title('Analytiske M/M/1-formler vs. DES-simulering',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3, axis='y')

    # Annoter verdier
    for xi, av, ev in zip(x, analyt_vals, emp_vals):
        ax.text(xi - bredde / 2, av, f'{av:.2f}', ha='center', va='bottom',
                fontsize=9, color='#1F6587')
        ax.text(xi + bredde / 2, ev, f'{ev:.2f}', ha='center', va='bottom',
                fontsize=9, color='#9C540B')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_tidsforlop(hendelser, output_path: Path, max_tid: float = 20.0) -> None:
    """Plott antall i system over tid (forste max_tid timer)."""
    tider, n_inn = hendelser
    tider = np.array(tider)
    n_inn = np.array(n_inn)
    mask = tider <= max_tid
    tider = tider[mask]
    n_inn = n_inn[mask]

    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.step(tider, n_inn, where='post', color='#1F6587', linewidth=1.2)
    ax.fill_between(tider, 0, n_inn, step='post', color='#8CC8E5', alpha=0.45)
    ax.set_xlabel('Tid (timer)', fontsize=11)
    ax.set_ylabel(r'Antall i system $N(t)$', fontsize=11)
    ax.set_title('Simulert koforlop ved tollstasjonen (forste 20 timer)',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 3: DISKRET HENDELSESSIMULERING (DES)")
    print("=" * 60)

    analyt = mm1_formler(LAMBDA_TRUE, MU_TRUE)
    emp = simuler_mm1(LAMBDA_TRUE, MU_TRUE, N_KUNDER, SEED)

    print(f"\nBaseline lambda={LAMBDA_TRUE}, my={MU_TRUE}, rho={analyt['rho']:.3f}")
    print(f"  L  analyt={analyt['L']:.3f}  sim={emp['L_emp']:.3f}")
    print(f"  Lq analyt={analyt['Lq']:.3f}  sim={emp['Lq_emp']:.3f}")
    print(f"  W  analyt={analyt['W']*60:.2f}min  sim={emp['W_emp']*60:.2f}min")
    print(f"  Wq analyt={analyt['Wq']*60:.2f}min  sim={emp['Wq_emp']*60:.2f}min")

    resultater = {
        'analytisk': {k: round(v, 5) for k, v in analyt.items()},
        'simulert': {
            'Wq_emp': round(emp['Wq_emp'], 5),
            'W_emp': round(emp['W_emp'], 5),
            'L_emp': round(emp['L_emp'], 5),
            'Lq_emp': round(emp['Lq_emp'], 5),
            'Wq_emp_min': round(emp['Wq_emp'] * 60.0, 3),
            'W_emp_min': round(emp['W_emp'] * 60.0, 3),
            'sluttid_timer': round(emp['sluttid'], 2),
            'n_kunder': emp['n_kunder'],
        },
        'avvik': {
            'L_pct': round(100.0 * abs(emp['L_emp'] - analyt['L']) / analyt['L'], 2),
            'Lq_pct': round(100.0 * abs(emp['Lq_emp'] - analyt['Lq']) / analyt['Lq'], 2),
            'W_pct': round(100.0 * abs(emp['W_emp'] - analyt['W']) / analyt['W'], 2),
            'Wq_pct': round(100.0 * abs(emp['Wq_emp'] - analyt['Wq']) / analyt['Wq'], 2),
        },
    }

    path = OUTPUT_DIR / 'step03_results.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(resultater, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {path}")

    plot_sammenligning(analyt, emp, OUTPUT_DIR / 'mm1_des_vs_analytical.png')
    plot_tidsforlop(emp['hendelser'], OUTPUT_DIR / 'mm1_time_trajectory.png')


if __name__ == '__main__':
    main()
