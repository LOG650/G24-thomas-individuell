"""
Steg 2: Erlang-C-formelen og svep over antall kraner c
=======================================================
Implementerer Erlang-C og beregner ytelsesmal (Lq, Wq, P(vent > t))
for c = 1, 2, ..., 10 gitt lambda og mu fra steg 1.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import (
    COLOR_S1, COLOR_S1D, COLOR_S2D, COLOR_S3, COLOR_S3D,
    COLOR_S4D, COLOR_S5D,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# System-parametre fra steg 1
LAMBDA = 2.4   # skip per time
MU = 3.0       # skip per time per kran


def erlang_b(c: int, a: float) -> float:
    """
    Erlang-B formelen (blokkeringsannsynlighet for M/M/c/c).
    Iterativ form (numerisk stabil):
        B(0, a) = 1,  B(c, a) = a B(c-1, a) / (c + a B(c-1, a))
    Brukes som byggekloss for Erlang-C.
    """
    b = 1.0
    for k in range(1, c + 1):
        b = a * b / (k + a * b)
    return b


def erlang_c(c: int, a: float) -> float:
    """
    Erlang-C: sannsynligheten for at en ankommende kunde ma vente.
    a = lambda/mu = tilbudt last (Erlang). Krever c > a for stabilitet.
    Utleder fra Erlang-B:
        C(c, a) = c * B(c, a) / (c - a + a * B(c, a))
    """
    if c <= a:
        return 1.0
    b = erlang_b(c, a)
    return c * b / (c - a + a * b)


def mmc_metrics(c: int, lam: float, mu: float) -> dict:
    """Sentrale ytelsesmal for M/M/c."""
    a = lam / mu
    rho = a / c
    if rho >= 1:
        return {
            'c': c, 'a': a, 'rho': float(rho),
            'C_ca': 1.0, 'Lq': float('inf'), 'Wq': float('inf'),
            'L': float('inf'), 'W': float('inf'), 'stabil': False,
        }
    C = erlang_c(c, a)
    Lq = C * rho / (1 - rho)
    Wq = Lq / lam
    L = Lq + a
    W = Wq + 1.0 / mu
    return {
        'c': c, 'a': a, 'rho': float(rho), 'C_ca': float(C),
        'Lq': float(Lq), 'Wq': float(Wq),
        'L': float(L), 'W': float(W), 'stabil': True,
    }


def prob_wait_greater(t_min: float, c: int, lam: float, mu: float) -> float:
    """
    P(W_q > t) for en ankommende kunde som finner alle c servere opptatt.
    For M/M/c:
        P(W_q > t) = C(c, a) * exp(-(c*mu - lam) * t)
    t gis i timer.
    """
    a = lam / mu
    if c <= a:
        return 1.0
    C = erlang_c(c, a)
    rate = c * mu - lam
    return C * np.exp(-rate * t_min)


def sweep_c(c_values: list[int], lam: float, mu: float,
            t_targets_min: list[float]) -> pd.DataFrame:
    """Bygg oppsummeringstabell over c for ulike ytelsesmal."""
    rows = []
    for c in c_values:
        m = mmc_metrics(c, lam, mu)
        row = {
            'c': c,
            'rho': m['rho'],
            'C_ca': m['C_ca'],
            'Lq': m['Lq'],
            'Wq_min': m['Wq'] * 60 if np.isfinite(m['Wq']) else float('inf'),
            'W_min': m['W'] * 60 if np.isfinite(m['W']) else float('inf'),
        }
        for t_min in t_targets_min:
            key = f'P_wait_gt_{int(t_min)}min'
            row[key] = prob_wait_greater(t_min / 60.0, c, lam, mu)
        rows.append(row)
    return pd.DataFrame(rows)


def plot_probability_wait(df: pd.DataFrame, output_path: Path,
                          target_t_min: float = 10.0) -> None:
    """Plott C(c, a) og P(W_q > target) som funksjon av c."""
    fig, ax = plt.subplots(figsize=(10, 5))

    c_vals = df['c'].values
    ax.plot(c_vals, df['C_ca'].values, 'o-',
            color=COLOR_S1D, linewidth=2, markersize=8,
            label=r'$C(c,a) = P(W_q > 0)$')
    col = f'P_wait_gt_{int(target_t_min)}min'
    ax.plot(c_vals, df[col].values, 's-',
            color=COLOR_S3D, linewidth=2, markersize=8,
            label=rf'$P(W_q > {int(target_t_min)}\,\mathrm{{min}})$')
    ax.axhline(0.05, color=COLOR_S5D, linestyle='--', linewidth=1.5,
               label=r'Servicekrav $= 5\%$')

    ax.set_xlabel(r'Antall kraner $c$', fontsize=12)
    ax.set_ylabel('Sannsynlighet', fontsize=12)
    ax.set_title('Ventesannsynlighet som funksjon av antall kraner',
                 fontsize=12, fontweight='bold')
    ax.set_xticks(c_vals)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_ylim(0, 1.05)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_wq_vs_c(df: pd.DataFrame, output_path: Path) -> None:
    """Plott gjennomsnittlig ventetid Wq (i minutter) og kolengde Lq vs c."""
    # Filtrer vekk ustabile tilstander
    df_stab = df[df['Wq_min'].apply(np.isfinite)].copy()

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.plot(df_stab['c'], df_stab['Wq_min'], 'o-',
             color=COLOR_S1D, linewidth=2, markersize=8,
             label=r'$W_q$ (minutter)')
    ax1.set_xlabel(r'Antall kraner $c$', fontsize=12)
    ax1.set_ylabel(r'$W_q$ (minutter)', fontsize=12, color=COLOR_S1D)
    ax1.tick_params(axis='y', labelcolor=COLOR_S1D)
    ax1.set_xticks(df['c'].values)
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(df_stab['c'], df_stab['Lq'], 's--',
             color=COLOR_S3D, linewidth=2, markersize=8,
             label=r'$L_q$ (skip)')
    ax2.set_ylabel(r'$L_q$ (antall skip i ko)', fontsize=12, color=COLOR_S3D)
    ax2.tick_params(axis='y', labelcolor=COLOR_S3D)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               loc='upper right', fontsize=10)

    ax1.set_title(r'Kolengde $L_q$ og forventet ventetid $W_q$ mot $c$',
                  fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 2: ERLANG-C OG SVEP OVER c")
    print("=" * 60)

    c_values = list(range(1, 11))
    t_targets = [5.0, 10.0, 15.0]
    df = sweep_c(c_values, LAMBDA, MU, t_targets)

    print("\n--- Tabell: Ytelsesmal for c = 1..10 ---")
    print(df.to_string(index=False, float_format=lambda x: f"{x:.4f}"))

    # Lagre som JSON for LaTeX
    results = {
        'lambda': LAMBDA,
        'mu': MU,
        'a': LAMBDA / MU,
        'sweep': df.to_dict(orient='records'),
    }
    out_path = OUTPUT_DIR / 'step02_erlang_c.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {out_path}")

    plot_probability_wait(df, OUTPUT_DIR / 'mmc_prob_wait.png',
                          target_t_min=10.0)
    plot_wq_vs_c(df, OUTPUT_DIR / 'mmc_wq_vs_c.png')

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print("Erlang-C gir ventesannsynligheten; P(Wq > 10 min) faller raskt med c.")


if __name__ == '__main__':
    main()
