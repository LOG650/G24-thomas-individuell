"""
Steg 6: Sammenligning, nedre grense og transportbesparelser
===========================================================
1. Beregn en enkel kontinuerlig nedre grense (LP-relaksasjon):
       LB = ceil( max( sum(v_i)/V , sum(m_i)/M ) )
   dvs. ingen losning kan bruke faerre enn LB bins gitt volum- og vektkrav.

2. Sammenlign naiv FF, FFD og BFD paa antall bins, volumutnyttelse og gap til LB.

3. Estimer transportbesparelser: faerre bins => faerre palleplasser og lavere CO2.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_naiv_pakking import first_fit, summarize_bins, BIN_VOLUME_L, BIN_MAX_WEIGHT_KG
from step03_ffd import ffd
from step04_bfd import bfd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Transportparametre (pedagogiske, ikke bransjekilde)
CO2_PER_BIN_KG = 1.3      # gjennomsnittlig CO2 per bin i distribusjon (kg CO2e)
HANDLING_COST_PER_BIN = 14.0  # handteringskostnad per bin (NOK)


def continuous_lower_bound(df: pd.DataFrame) -> dict:
    """Kontinuerlig nedre grense for 1D bin packing med vekt- og volumrestriksjon."""
    total_v = float(df['volum_l'].sum())
    total_m = float(df['vekt_kg'].sum())
    lb_volume = total_v / BIN_VOLUME_L
    lb_weight = total_m / BIN_MAX_WEIGHT_KG
    lb_cont = max(lb_volume, lb_weight)
    lb_int = int(np.ceil(lb_cont))
    return {
        'sum_volum_l': round(total_v, 2),
        'sum_vekt_kg': round(total_m, 2),
        'LB_volum': round(lb_volume, 4),
        'LB_vekt': round(lb_weight, 4),
        'LB_kontinuerlig': round(lb_cont, 4),
        'LB_heltall': lb_int,
    }


def plot_comparison(rows: list, lb_int: int, output_path: Path) -> None:
    """Sammenlign metodene i to paneler: antall bins og volumutnyttelse."""
    names = [r['metode'] for r in rows]
    bins_used = [r['antall_bins'] for r in rows]
    util = [r['volumutnyttelse'] for r in rows]

    colors_fill = ['#ED9F9E', '#8CC8E5', '#97D4B7']
    colors_edge = ['#961D1C', '#1F6587', '#307453']

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8))

    # Panel 1: antall bins med LB-linje
    ax = axes[0]
    bars = ax.bar(names, bins_used, color=colors_fill,
                  edgecolor=colors_edge, linewidth=1.2)
    for bar, v in zip(bars, bins_used):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.2, str(int(v)),
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.axhline(lb_int, color='#1F2933', linestyle='--', linewidth=1.3,
               label=f'nedre grense LB = {lb_int}')
    ax.set_ylabel('antall bins $K$', fontsize=11)
    ax.set_title('Antall bins per metode', fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(fontsize=9)
    ax.set_ylim(0, max(bins_used) + 3)

    # Panel 2: volumutnyttelse
    ax = axes[1]
    util_pct = [u * 100 for u in util]
    bars = ax.bar(names, util_pct, color=colors_fill,
                  edgecolor=colors_edge, linewidth=1.2)
    for bar, v in zip(bars, util_pct):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.7,
                f'{v:.1f}%'.replace('.', ','),
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    ax.set_ylabel('volumutnyttelse (%)', fontsize=11)
    ax.set_title('Volumutnyttelse', fontsize=11, fontweight='bold')
    ax.set_ylim(0, 100)
    ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def load_items():
    df = pd.read_csv(DATA_DIR / 'products.csv')
    return df, df.to_dict(orient='records')


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 6: SAMMENLIGNING OG TRANSPORTBESPARELSER")
    print(f"{'='*60}")

    df, items = load_items()

    # Nedre grense
    lb = continuous_lower_bound(df)
    print("\n--- Kontinuerlig nedre grense ---")
    for k, v in lb.items():
        print(f"  {k}: {v}")

    # Kjor alle tre metoder
    results = []
    for name, fn in [('Naiv FF', first_fit), ('FFD', ffd), ('BFD', bfd)]:
        bins = fn(items)
        s = summarize_bins(bins)
        gap_abs = s['antall_bins'] - lb['LB_heltall']
        gap_rel = gap_abs / lb['LB_heltall'] if lb['LB_heltall'] > 0 else 0.0
        row = {
            'metode': name,
            'antall_bins': s['antall_bins'],
            'volumutnyttelse': s['volumutnyttelse'],
            'gap_bins': gap_abs,
            'gap_rel': round(gap_rel, 4),
            'fyllingsgrad_mean': s['fyllingsgrad_mean'],
        }
        results.append(row)

    print("\n--- Sammenligning ---")
    for r in results:
        print(f"  {r['metode']:<10s} | bins = {r['antall_bins']:>3d} | "
              f"util = {r['volumutnyttelse']:.3f} | gap = +{r['gap_bins']} "
              f"({r['gap_rel']*100:.1f}%)")

    # Transportbesparelse naiv FF -> FFD og naiv FF -> BFD
    naiv = results[0]
    ffd_r = results[1]
    bfd_r = results[2]

    def savings(base: dict, alt: dict) -> dict:
        bins_saved = base['antall_bins'] - alt['antall_bins']
        co2_saved = bins_saved * CO2_PER_BIN_KG
        handling_saved = bins_saved * HANDLING_COST_PER_BIN
        return {
            'bins_redusert': bins_saved,
            'prosent_redusert': round(bins_saved / base['antall_bins'], 4),
            'co2_spart_kg': round(co2_saved, 2),
            'handtering_spart_nok': round(handling_saved, 2),
        }

    savings_ffd = savings(naiv, ffd_r)
    savings_bfd = savings(naiv, bfd_r)

    print("\n--- Transportbesparelse (naiv -> FFD) ---")
    for k, v in savings_ffd.items():
        print(f"  {k}: {v}")
    print("\n--- Transportbesparelse (naiv -> BFD) ---")
    for k, v in savings_bfd.items():
        print(f"  {k}: {v}")

    out = {
        'lower_bound': lb,
        'results': results,
        'savings_naiv_vs_ffd': savings_ffd,
        'savings_naiv_vs_bfd': savings_bfd,
        'parametre': {
            'co2_per_bin_kg': CO2_PER_BIN_KG,
            'handling_cost_per_bin_nok': HANDLING_COST_PER_BIN,
            'bin_volum_l': BIN_VOLUME_L,
            'bin_maks_vekt_kg': BIN_MAX_WEIGHT_KG,
        },
    }
    with open(OUTPUT_DIR / 'step06_results.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step06_results.json'}")

    plot_comparison(results, lb['LB_heltall'], OUTPUT_DIR / 'bp_compare.png')


if __name__ == '__main__':
    main()
