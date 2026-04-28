"""
Steg 5: Simulated annealing paa 50-jobb instans
===============================================
For N = 50 er MIP beregningsmessig upraktisk (milliarder av
binaere variabler). Vi bruker en enkel simulated annealing-
metaheuristikk:

    * Initiell losning: ATC-sekvens (god start).
    * Nabolosning: swap to tilfeldige posisjoner.
    * Akseptkriterium: DeltaE <= 0 aksepteres; ellers aksepteres
      med sannsynlighet exp(-DeltaE / T).
    * Kjoleplan: geometrisk, T_k = alpha * T_{k-1}.

Lagrer konvergenskurve og beste sekvens for sammenligning i step06.
"""

import json
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_dispatch_heuristikker import (
    atc_sequence, evaluate_sequence, load_instance,
)

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def simulated_annealing(df: pd.DataFrame, S,
                        T0: float = 500.0,
                        alpha: float = 0.995,
                        n_iter: int = 20_000,
                        seed: int = 7) -> dict:
    """SA for enkeltmaskin vektet tardiness."""
    rng = np.random.default_rng(seed)

    # Initiell losning: ATC
    current = atc_sequence(df, S)
    current_cost = evaluate_sequence(current, df, S)['weighted_tardiness']

    best = current[:]
    best_cost = current_cost

    T = T0
    history = [best_cost]
    accepted = 0
    t_start = time.time()

    n = len(current)
    for it in range(n_iter):
        i, j = rng.integers(0, n, size=2)
        if i == j:
            continue
        candidate = current[:]
        candidate[i], candidate[j] = candidate[j], candidate[i]
        cand_cost = evaluate_sequence(candidate, df, S)['weighted_tardiness']

        dE = cand_cost - current_cost
        if dE <= 0 or rng.random() < np.exp(-dE / max(T, 1e-6)):
            current = candidate
            current_cost = cand_cost
            accepted += 1
            if current_cost < best_cost:
                best = current[:]
                best_cost = current_cost

        T *= alpha
        history.append(best_cost)

    t_elapsed = time.time() - t_start
    best_res = evaluate_sequence(best, df, S)
    return {
        'best_sequence': best,
        'best_cost': round(float(best_cost), 3),
        'initial_cost': round(float(history[0]), 3),
        'iterations': int(n_iter),
        'accepted': int(accepted),
        'acceptance_rate': round(accepted / n_iter, 3),
        'solve_time_s': round(t_elapsed, 3),
        'history': [round(float(h), 3) for h in history],
        'evaluation': best_res,
    }


def plot_convergence(history: list[float], initial: float,
                     output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 5))
    iters = np.arange(len(history))
    ax.plot(iters, history, color='#1F6587', linewidth=1.0,
            label='Beste funnet losning')
    ax.axhline(initial, color='#9C540B', linestyle='--', linewidth=1,
               label=f'Initiell (ATC) = {initial:.1f}')
    ax.set_xlabel('Iterasjon $k$', fontsize=12)
    ax.set_ylabel(r'Vektet tardiness $\sum_j w_j T_j$', fontsize=12)
    ax.set_title('Simulated annealing konvergens (N = 50)',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 5: SIMULATED ANNEALING (N = 50)')
    print('=' * 60)

    df, S = load_instance('large')
    print(f"\nStarter SA paa N = {len(df)} jobber...")

    res = simulated_annealing(df, S, T0=500.0, alpha=0.9995, n_iter=20_000, seed=7)

    print(f"\nInitiell (ATC)   : {res['initial_cost']:.2f}")
    print(f"Beste (SA)       : {res['best_cost']:.2f}")
    print(f"Forbedring       : {res['initial_cost'] - res['best_cost']:.2f}")
    print(f"Akseptrate       : {res['acceptance_rate']:.1%}")
    print(f"Losetid SA       : {res['solve_time_s']:.2f} s")

    # Trimm history for JSON-lagring
    to_save = {k: v for k, v in res.items() if k != 'history'}
    with open(OUTPUT_DIR / 'step05_sa_result.json', 'w', encoding='utf-8') as f:
        json.dump(to_save, f, indent=2, ensure_ascii=False)
    with open(OUTPUT_DIR / 'step05_sa_history.json', 'w', encoding='utf-8') as f:
        json.dump({'history': res['history']}, f, indent=2)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step05_sa_result.json'}")

    plot_convergence(res['history'], res['initial_cost'],
                     OUTPUT_DIR / 'seqmip_sa_convergence.png')


if __name__ == '__main__':
    main()
