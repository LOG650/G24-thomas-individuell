"""
Steg 5: Sensitivitet mot ankomstrate (sesongtopper)
====================================================
Hvordan endrer kapasitetsbehovet seg nar lambda varierer (+/- 30%)?
Produserer et sesongprofil-plott og en tabell som viser anbefalt c
for lav, normal og hoy ankomstrate.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import (
    COLOR_S1, COLOR_S1D, COLOR_S2, COLOR_S2D, COLOR_S3,
    COLOR_S3D, COLOR_S5D,
)
from step02_erlang_c import MU, mmc_metrics, prob_wait_greater
from step03_servicedimensjonering import minimum_c_for_service
from step04_kostnadsoptimering import C_KRAN, C_VENT, total_cost

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

LAMBDA_BASE = 2.4


def scenario_table() -> pd.DataFrame:
    """Bygg scenariotabell med lav, normal og hoy ankomstrate."""
    scenarios = [
        ('Lavseesong',   0.70 * LAMBDA_BASE),
        ('Skuldersesong', 0.90 * LAMBDA_BASE),
        ('Normal',       1.00 * LAMBDA_BASE),
        ('Travelt',      1.20 * LAMBDA_BASE),
        ('Topp',         1.30 * LAMBDA_BASE),
    ]
    rows = []
    for name, lam in scenarios:
        res_service = minimum_c_for_service(lam, MU, t_min=10.0,
                                            target_prob=0.05)
        c_service = res_service['c_optimal']
        # Finn kostnadsoptimal c ogsa
        c_vals = list(range(1, 15))
        costs = [total_cost(c, lam, MU) for c in c_vals]
        c_cost = min((r for r in costs if np.isfinite(r['totkost'])),
                     key=lambda r: r['totkost'])['c']
        m_service = mmc_metrics(c_service, lam, MU)
        m_cost = mmc_metrics(c_cost, lam, MU)
        rows.append({
            'scenario': name,
            'lambda': round(lam, 3),
            'rho_ved_c1': round(lam / MU, 3),
            'c_service': c_service,
            'c_kostnad': c_cost,
            'Wq_min_service': round(m_service['Wq'] * 60, 2),
            'Wq_min_kost': round(m_cost['Wq'] * 60, 2),
        })
    return pd.DataFrame(rows)


def plot_sensitivity(df: pd.DataFrame, output_path: Path) -> None:
    """Soylediagram over anbefalt c per scenario."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(df))
    width = 0.35

    ax.bar(x - width / 2, df['c_service'], width,
           color=COLOR_S1, edgecolor=COLOR_S1D,
           label='Servicekrav (P(Wq>10 min) < 5%)')
    ax.bar(x + width / 2, df['c_kostnad'], width,
           color=COLOR_S3, edgecolor=COLOR_S3D,
           label='Kostnadsoptimalt')

    # Annotere rho
    for i, rho in enumerate(df['rho_ved_c1']):
        ax.text(x[i], -1.0, rf'$\rho_1={rho:.2f}$',
                ha='center', va='top', fontsize=9, color='gray')

    ax.set_xticks(x)
    ax.set_xticklabels(df['scenario'].tolist(), rotation=0, fontsize=10)
    ax.set_ylabel(r'Anbefalt antall kraner $c$', fontsize=12)
    ax.set_title('Kapasitetsbehov under ulike ankomstscenarioer',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper left', fontsize=10)
    ax.set_ylim(0, max(df[['c_service', 'c_kostnad']].max()) + 2)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_wq_heatmap(output_path: Path) -> None:
    """Heatmap over Wq i minutter for ulike lambda og c."""
    lam_values = np.linspace(1.4, 3.5, 22)
    c_values = np.arange(1, 9)
    Z = np.full((len(c_values), len(lam_values)), np.nan)
    for i, c in enumerate(c_values):
        for j, lam in enumerate(lam_values):
            m = mmc_metrics(int(c), lam, MU)
            if m['stabil']:
                Z[i, j] = m['Wq'] * 60
    # Klipp for lesbarhet
    Z = np.clip(Z, 0, 60)

    fig, ax = plt.subplots(figsize=(10, 5))
    pcm = ax.imshow(Z, origin='lower', aspect='auto',
                    extent=[lam_values[0], lam_values[-1],
                            c_values[0] - 0.5, c_values[-1] + 0.5],
                    cmap='viridis')
    cbar = fig.colorbar(pcm, ax=ax)
    cbar.set_label(r'$W_q$ (minutter, klippet til 60)', fontsize=11)

    # Markerer basis-lambda
    ax.axvline(LAMBDA_BASE, color='white', linestyle='--', linewidth=1.2,
               label=r'$\lambda_{\mathrm{normal}} = 2{,}4$')
    ax.set_xlabel(r'Ankomstrate $\lambda$ (skip/time)', fontsize=12)
    ax.set_ylabel(r'Antall kraner $c$', fontsize=12)
    ax.set_yticks(c_values)
    ax.set_title(r'Forventet ventetid $W_q$ som funksjon av '
                 r'ankomstrate og bemanning',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_peak_vs_offpeak(output_path: Path) -> None:
    """Sammenlign ventetidsfordeling for normal vs topp-sesong med c = 3."""
    fig, ax = plt.subplots(figsize=(10, 5))
    t_minutes = np.linspace(0, 40, 200)
    cases = [
        (LAMBDA_BASE, 3, COLOR_S2D, 'Normal, $c=3$'),
        (LAMBDA_BASE * 1.30, 3, COLOR_S5D, 'Topp, $c=3$ (underdimensjonert)'),
        (LAMBDA_BASE * 1.30, 4, COLOR_S1D, 'Topp, $c=4$ (forsterket)'),
    ]
    for lam, c, col, label in cases:
        m = mmc_metrics(c, lam, MU)
        if not m['stabil']:
            continue
        p = [prob_wait_greater(t / 60.0, c, lam, MU) for t in t_minutes]
        ax.plot(t_minutes, p, color=col, linewidth=2.0, label=label)
    ax.axhline(0.05, color='gray', linestyle='--', linewidth=1.0,
               label=r'Servicekrav $5\%$')
    ax.set_xlabel(r'Ventetid $t$ (minutter)', fontsize=12)
    ax.set_ylabel(r'$P(W_q > t)$', fontsize=12)
    ax.set_title(r'Halefordeling: Normal sesong vs. topp-sesong',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 5: SENSITIVITET")
    print("=" * 60)

    df = scenario_table()
    print("\n--- Scenariotabell ---")
    print(df.to_string(index=False))

    json_path = OUTPUT_DIR / 'step05_sensitivity.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(df.to_dict(orient='records'), f, indent=2, ensure_ascii=False)
    print(f"Lagret: {json_path}")

    plot_sensitivity(df, OUTPUT_DIR / 'mmc_sensitivity.png')
    plot_wq_heatmap(OUTPUT_DIR / 'mmc_heatmap.png')
    plot_peak_vs_offpeak(OUTPUT_DIR / 'mmc_peaks_off.png')

    print("\n" + "=" * 60)
    print("KONKLUSJON")
    print("=" * 60)
    print("Kapasitetsbehovet skalerer ikke-lineaert med ankomstrate.")
    print("I topp-sesong kreves ofte en ekstra kran for a bevare servicen.")


if __name__ == '__main__':
    main()
