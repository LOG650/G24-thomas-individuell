"""
Steg 4: Kostnadsoptimering
============================
Total kostnad per time = c_k * c + c_w * L
der c_k er kapasitetskostnad per kran per time og c_w er ventekostnad per skip
per time (ventende skip + skip under betjening, dvs. totalt L i systemet).
Finn c som minimerer total kostnad.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import COLOR_S1D, COLOR_S3D, COLOR_S5D
from step02_erlang_c import LAMBDA, MU, mmc_metrics

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Kostnadsparametre (NOK/time)
C_KRAN = 3500.0    # Kapasitetskost per kran per time (lonn, energi, avskrivning)
C_VENT = 8500.0    # Ventekost per skip per time (kaiLeie, kontraktsbot)


def total_cost(c: int, lam: float, mu: float,
               c_k: float = C_KRAN, c_w: float = C_VENT) -> dict:
    m = mmc_metrics(c, lam, mu)
    if not m['stabil']:
        return {
            'c': c, 'kapkost': c_k * c, 'ventkost': float('inf'),
            'totkost': float('inf'), 'Lq': float('inf'), 'L': float('inf'),
        }
    kap = c_k * c
    vent_total = c_w * m['L']   # ventekost pa alle skip i systemet
    vent_queue = c_w * m['Lq']  # (alternativ: kun pa ventende)
    return {
        'c': c,
        'kapkost': kap,
        'ventkost_total': vent_total,
        'ventkost_kun_ko': vent_queue,
        'totkost': kap + vent_total,
        'totkost_kun_ko': kap + vent_queue,
        'Lq': m['Lq'],
        'L': m['L'],
        'Wq_min': m['Wq'] * 60,
        'rho': m['rho'],
    }


def optimize_cost(c_values: list[int], lam: float, mu: float) -> pd.DataFrame:
    rows = [total_cost(c, lam, mu) for c in c_values]
    return pd.DataFrame(rows)


def plot_cost_curve(df: pd.DataFrame, c_star: int,
                    output_path: Path) -> None:
    """Plot totalkostnad som sum av kapasitetskost og ventekost."""
    fig, ax = plt.subplots(figsize=(10, 5))
    df_stab = df[df['totkost'].apply(np.isfinite)].copy()

    c_vals = df_stab['c'].values
    ax.plot(c_vals, df_stab['kapkost'], 's-',
            color=COLOR_S1D, linewidth=2, markersize=7,
            label='Kapasitetskostnad')
    ax.plot(c_vals, df_stab['ventkost_total'], '^-',
            color=COLOR_S3D, linewidth=2, markersize=7,
            label='Ventekostnad')
    ax.plot(c_vals, df_stab['totkost'], 'o-',
            color=COLOR_S5D, linewidth=2.5, markersize=8,
            label='Totalkostnad')

    # Marker optimal c
    idx = df_stab.index[df_stab['c'] == c_star]
    if len(idx) > 0:
        y_star = df_stab.loc[idx[0], 'totkost']
        ax.axvline(c_star, color='gray', linestyle=':', linewidth=1.2)
        ax.annotate(rf'$c^* = {c_star}$',
                    xy=(c_star, y_star),
                    xytext=(c_star + 0.4, y_star * 1.05),
                    fontsize=12, color='gray')

    ax.set_xlabel(r'Antall kraner $c$', fontsize=12)
    ax.set_ylabel('Kostnad (NOK/time)', fontsize=12)
    ax.set_title('Kostnadsoptimering: Kapasitet mot ventetid',
                 fontsize=12, fontweight='bold')
    ax.set_xticks(c_vals)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper center', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 4: KOSTNADSOPTIMERING")
    print("=" * 60)

    c_values = list(range(1, 11))
    df = optimize_cost(c_values, LAMBDA, MU)
    # Finn c* pa total kostnad
    df_stab = df[df['totkost'].apply(np.isfinite)].copy()
    c_star = int(df_stab.loc[df_stab['totkost'].idxmin(), 'c'])

    print("\n--- Kostnadstabell ---")
    show_cols = ['c', 'rho', 'Wq_min', 'Lq', 'L',
                 'kapkost', 'ventkost_total', 'totkost']
    print(df[show_cols].to_string(index=False,
                                  float_format=lambda x: f"{x:,.2f}"))

    print(f"\nKostnadsoptimalt antall kraner: c* = {c_star}")
    row = df[df['c'] == c_star].iloc[0]
    print(f"  Totalkostnad ved c*  : {row['totkost']:,.0f} NOK/time")
    print(f"  Kapasitetskostnad    : {row['kapkost']:,.0f} NOK/time")
    print(f"  Ventekostnad         : {row['ventkost_total']:,.0f} NOK/time")
    print(f"  Wq                   : {row['Wq_min']:.2f} min")
    print(f"  rho                  : {row['rho']:.3f}")

    out = {
        'parametre': {
            'c_kran_nok_per_time': C_KRAN,
            'c_vent_nok_per_skip_per_time': C_VENT,
            'lambda': LAMBDA,
            'mu': MU,
        },
        'c_optimal': c_star,
        'tabell': df.to_dict(orient='records'),
        'valgt_ytelse': {
            'totkost_per_time': float(row['totkost']),
            'kapkost_per_time': float(row['kapkost']),
            'ventkost_per_time': float(row['ventkost_total']),
            'Wq_min': float(row['Wq_min']),
            'Lq': float(row['Lq']),
            'L': float(row['L']),
            'rho': float(row['rho']),
        },
    }
    path = OUTPUT_DIR / 'step04_cost_optim.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Lagret: {path}")

    plot_cost_curve(df, c_star, OUTPUT_DIR / 'mmc_cost_curve.png')

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print(f"Kostnadsoptimalt antall kraner er {c_star}.")


if __name__ == '__main__':
    main()
