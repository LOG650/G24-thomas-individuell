"""
Steg 3: Servicedimensjonering - finn minimal c
===============================================
Gitt servicekrav P(W_q > 10 min) < 5%, finn minste antall kraner c
som moter kravet. Viser ogsa sensitivitet for ulike servicemal.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import COLOR_S1D, COLOR_S2D, COLOR_S3D, COLOR_S5D
from step02_erlang_c import (
    LAMBDA, MU, erlang_c, prob_wait_greater, mmc_metrics,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def minimum_c_for_service(lam: float, mu: float, t_min: float,
                          target_prob: float,
                          c_max: int = 30) -> dict:
    """
    Finn minste c slik at P(W_q > t_min) < target_prob.
    Returnerer diagnostikk pa a vise "over og under".
    """
    a = lam / mu
    c_min = int(np.ceil(a)) + 1  # stabilitetskrav

    for c in range(c_min, c_max + 1):
        p = prob_wait_greater(t_min / 60.0, c, lam, mu)
        if p < target_prob:
            # Kontrast med c-1 dersom den er stabil
            if c - 1 > a:
                p_prev = prob_wait_greater(t_min / 60.0, c - 1, lam, mu)
            else:
                p_prev = 1.0
            return {
                'c_optimal': int(c),
                'a': float(a),
                'target_prob': float(target_prob),
                't_min': float(t_min),
                'p_wait_gt_t_at_c': float(p),
                'p_wait_gt_t_at_c_minus_1': float(p_prev),
            }
    return {
        'c_optimal': None,
        'a': float(a),
        'target_prob': float(target_prob),
        't_min': float(t_min),
        'message': 'ingen c <= c_max moter kravet',
    }


def plot_service_sensitivity(lam: float, mu: float,
                             output_path: Path) -> None:
    """Heat map over (c, t) med iso-konturer for P(Wq > t)."""
    c_values = np.arange(2, 9)
    t_minutes = np.linspace(0.0, 30.0, 120)
    Z = np.zeros((len(c_values), len(t_minutes)))
    for i, c in enumerate(c_values):
        for j, t in enumerate(t_minutes):
            Z[i, j] = prob_wait_greater(t / 60.0, int(c), lam, mu)

    fig, ax = plt.subplots(figsize=(10, 5))
    for i, c in enumerate(c_values):
        ax.plot(t_minutes, Z[i], linewidth=1.8, label=rf'$c = {c}$')
    ax.axhline(0.05, color=COLOR_S5D, linestyle='--', linewidth=1.2,
               label=r'Servicekrav $5\%$')
    ax.axvline(10, color='gray', linestyle=':', linewidth=1.0,
               label=r'$t = 10$ min')
    ax.set_xlabel(r'Ventetid $t$ (minutter)', fontsize=12)
    ax.set_ylabel(r'$P(W_q > t)$', fontsize=12)
    ax.set_title('Halefordeling av ventetid for ulike bemanningsnivaer',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 3: SERVICEDIMENSJONERING")
    print("=" * 60)

    # Primaer beslutning: P(Wq > 10 min) < 5%
    result = minimum_c_for_service(LAMBDA, MU, t_min=10.0, target_prob=0.05)

    print("\n--- Minimal c for servicekrav ---")
    for k, v in result.items():
        print(f"  {k}: {v}")

    # Sensitivitet for flere kombinasjoner
    combos = [
        (5.0, 0.10), (10.0, 0.05), (10.0, 0.10),
        (15.0, 0.05), (20.0, 0.05),
    ]
    sensitivity = []
    for t_min, target in combos:
        r = minimum_c_for_service(LAMBDA, MU, t_min=t_min, target_prob=target)
        sensitivity.append({
            't_min': t_min,
            'target_prob': target,
            'c_optimal': r['c_optimal'],
            'p_wait_at_c': r.get('p_wait_gt_t_at_c'),
        })

    print("\n--- Sensitivitet av c for ulike servicemal ---")
    for r in sensitivity:
        c_str = r['c_optimal'] if r['c_optimal'] else '>30'
        p_str = f"{r['p_wait_at_c']:.4f}" if r['p_wait_at_c'] is not None else 'n/a'
        print(f"  P(Wq > {r['t_min']:>4.1f} min) < {r['target_prob']*100:>4.1f}%"
              f"  ->  c = {c_str} (P = {p_str})")

    # Ytelsesmal ved valgt c
    c_star = result['c_optimal']
    m = mmc_metrics(c_star, LAMBDA, MU)
    m_readable = {
        'c_valgt': int(c_star),
        'rho': m['rho'],
        'C_ca': m['C_ca'],
        'Lq': m['Lq'],
        'Wq_min': m['Wq'] * 60,
        'W_min': m['W'] * 60,
    }

    # Lagre
    out = {
        'valg_av_c': result,
        'sensitivitet': sensitivity,
        'ytelse_ved_c_stjerne': m_readable,
    }
    json_path = OUTPUT_DIR / 'step03_service_dim.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nLagret: {json_path}")

    # Figur
    plot_service_sensitivity(LAMBDA, MU,
                             OUTPUT_DIR / 'mmc_service_tails.png')

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print(f"Minste c som moter P(Wq > 10 min) < 5%: c = {c_star}")
    print(f"Gir rho = {m['rho']:.3f}, Wq ~ {m['Wq']*60:.2f} min,"
          f" Lq ~ {m['Lq']:.3f} skip i ko.")


if __name__ == '__main__':
    main()
