"""
Steg 4: Utnyttelsesveggen -- Wq som funksjon av rho
==================================================
Plotter hvordan ventetiden Wq eksploderer naar rho -> 1 for M/M/1.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import MU_TRUE
from step02_analytisk import mm1_formler

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def plot_rho_kurve(mu: float, output_path: Path) -> None:
    rho_grid = np.linspace(0.01, 0.99, 500)
    Wq_min = np.array([mm1_formler(rho * mu, mu)['Wq'] for rho in rho_grid]) * 60.0
    L_vals = np.array([mm1_formler(rho * mu, mu)['L'] for rho in rho_grid])

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8))

    # Wq(rho)
    ax1.plot(rho_grid, Wq_min, color='#1F6587', linewidth=2.2)
    ax1.fill_between(rho_grid, 0, Wq_min,
                     where=(rho_grid <= 0.7), color='#97D4B7', alpha=0.55,
                     label=r'Trygg sone $\rho \leq 0{,}7$')
    ax1.fill_between(rho_grid, 0, Wq_min,
                     where=(rho_grid > 0.7) & (rho_grid <= 0.85),
                     color='#F6BA7C', alpha=0.55,
                     label=r'Varsel $0{,}7 < \rho \leq 0{,}85$')
    ax1.fill_between(rho_grid, 0, Wq_min,
                     where=(rho_grid > 0.85),
                     color='#ED9F9E', alpha=0.55,
                     label=r'Kritisk $\rho > 0{,}85$')
    ax1.axvline(x=0.85, color='#961D1C', linestyle='--', linewidth=1.2,
                alpha=0.8)
    ax1.set_xlabel(r'Utnyttelsesgrad $\rho = \lambda/\mu$', fontsize=12)
    ax1.set_ylabel(r'Ventetid $W_q$ (min)', fontsize=12)
    ax1.set_title(r'Ventetid eksploderer naar $\rho \to 1$',
                  fontsize=12, fontweight='bold')
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 60)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc='upper left', fontsize=9)

    # L(rho)
    ax2.plot(rho_grid, L_vals, color='#5A2C77', linewidth=2.2)
    ax2.axvline(x=0.85, color='#961D1C', linestyle='--', linewidth=1.2,
                alpha=0.8)
    ax2.set_xlabel(r'Utnyttelsesgrad $\rho$', fontsize=12)
    ax2.set_ylabel(r'Gjennomsnittlig antall i system $L$', fontsize=12)
    ax2.set_title(r'Kolengde $L = \rho/(1-\rho)$',
                  fontsize=12, fontweight='bold')
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 25)
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 4: UTNYTTELSESVEGGEN")
    print("=" * 60)

    # Tabellerte verdier ved terskelpunkter
    rho_tabell = [0.50, 0.70, 0.80, 0.85, 0.90, 0.95, 0.99]
    rader = []
    for rho in rho_tabell:
        f = mm1_formler(rho * MU_TRUE, MU_TRUE)
        rader.append({
            'rho': rho,
            'L': round(f['L'], 3),
            'Lq': round(f['Lq'], 3),
            'W_min': round(f['W'] * 60.0, 2),
            'Wq_min': round(f['Wq'] * 60.0, 2),
        })
        print(f"  rho={rho:.2f}: Wq={f['Wq']*60:.2f} min  L={f['L']:.2f}")

    path = OUTPUT_DIR / 'step04_results.json'
    with open(path, 'w', encoding='utf-8') as f_out:
        json.dump({'terskelverdier': rader}, f_out, indent=2,
                  ensure_ascii=False)
    print(f"\nResultater lagret: {path}")

    plot_rho_kurve(MU_TRUE, OUTPUT_DIR / 'mm1_rho_waiting.png')


if __name__ == '__main__':
    main()
