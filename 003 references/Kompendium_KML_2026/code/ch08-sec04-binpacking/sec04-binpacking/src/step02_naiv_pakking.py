"""
Steg 2: Naiv 1D bin packing (first-fit i ankomstrekkefolge)
===========================================================
Baseline som representerer "pakk produktene etter som de kommer inn i lageret".
Her reduserer vi problemet til en 1D-variant basert paa volum:
    plasser hvert produkt i forste aapne bin som har nok ledig volum og
    som ikke bryter vektgrensen.
"""

import json
from pathlib import Path
from typing import List

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

BIN_VOLUME_L = 72.0
BIN_MAX_WEIGHT_KG = 25.0


class Bin:
    """Enkel 1D bin med volum- og vektrestriksjon."""

    __slots__ = ('id', 'items', 'used_volume', 'used_weight')

    def __init__(self, bin_id: int):
        self.id = bin_id
        self.items: List[dict] = []
        self.used_volume = 0.0
        self.used_weight = 0.0

    @property
    def remaining_volume(self) -> float:
        return BIN_VOLUME_L - self.used_volume

    @property
    def remaining_weight(self) -> float:
        return BIN_MAX_WEIGHT_KG - self.used_weight

    def can_fit(self, item: dict) -> bool:
        return (item['volum_l'] <= self.remaining_volume + 1e-9
                and item['vekt_kg'] <= self.remaining_weight + 1e-9)

    def add(self, item: dict) -> None:
        self.items.append(item)
        self.used_volume += item['volum_l']
        self.used_weight += item['vekt_kg']


def first_fit(items: List[dict]) -> List[Bin]:
    """First-Fit: plasser hvert element i forste bin der det passer."""
    bins: List[Bin] = []
    for it in items:
        placed = False
        for b in bins:
            if b.can_fit(it):
                b.add(it)
                placed = True
                break
        if not placed:
            new_bin = Bin(bin_id=len(bins) + 1)
            new_bin.add(it)
            bins.append(new_bin)
    return bins


def summarize_bins(bins: List[Bin]) -> dict:
    n_bins = len(bins)
    total_volume_used = sum(b.used_volume for b in bins)
    total_weight = sum(b.used_weight for b in bins)
    capacity = n_bins * BIN_VOLUME_L
    util = total_volume_used / capacity if capacity > 0 else 0.0
    fill_per_bin = [b.used_volume / BIN_VOLUME_L for b in bins]
    return {
        'antall_bins': n_bins,
        'total_volum_l': round(total_volume_used, 2),
        'total_vekt_kg': round(total_weight, 2),
        'kapasitet_l': round(capacity, 2),
        'volumutnyttelse': round(util, 4),
        'fyllingsgrad_mean': round(float(np.mean(fill_per_bin)), 4),
        'fyllingsgrad_min': round(float(np.min(fill_per_bin)), 4),
        'fyllingsgrad_max': round(float(np.max(fill_per_bin)), 4),
    }


def plot_bins(bins: List[Bin], title: str, output_path: Path,
              highlight_color: str = '#8CC8E5',
              highlight_edge: str = '#1F6587') -> None:
    """Visualiser fyllingsgrad per bin som stablete stolper."""
    n = len(bins)
    fig_w = max(6.5, min(12, 0.34 * n + 4))
    fig, ax = plt.subplots(figsize=(fig_w, 5))

    x = np.arange(1, n + 1)
    fill = np.array([b.used_volume / BIN_VOLUME_L for b in bins])

    ax.bar(x, fill, color=highlight_color, edgecolor=highlight_edge,
           linewidth=0.9, label='brukt volum')
    # Kontur for full bin
    ax.bar(x, 1 - fill, bottom=fill, color='#F4F7FB',
           edgecolor='#CBD5E1', linewidth=0.6, label='ledig volum')

    mean_fill = fill.mean()
    ax.axhline(mean_fill, color='#1F2933', linestyle='--', linewidth=1.1,
               label=f'gj.sn. = {mean_fill:.2f}')

    ax.set_xlabel('bin-nummer $j$', fontsize=11)
    ax.set_ylabel('fyllingsgrad $f_j$', fontsize=11)
    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.set_xlim(0.4, n + 0.6)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='lower right', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def load_items() -> List[dict]:
    df = pd.read_csv(DATA_DIR / 'products.csv')
    return df.to_dict(orient='records')


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 2: NAIV FIRST-FIT I ANKOMSTREKKEFOLGE")
    print(f"{'='*60}")

    items = load_items()
    print(f"Laster {len(items)} produkter fra data/products.csv")

    bins = first_fit(items)
    summary = summarize_bins(bins)

    print("\n--- Resultat (naiv FF) ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    # Lagre resultat
    with open(OUTPUT_DIR / 'step02_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Resultater lagret: {OUTPUT_DIR / 'step02_results.json'}")

    plot_bins(bins, 'Naiv First-Fit (ankomstrekkefolge)',
              OUTPUT_DIR / 'bp_naive_packing.png',
              highlight_color='#ED9F9E', highlight_edge='#961D1C')


if __name__ == '__main__':
    main()
