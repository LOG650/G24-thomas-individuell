"""
Steg 3: First-Fit Decreasing (FFD)
==================================
Sorter produktene etter fallende volum og kjor deretter first-fit. FFD har
en bevist worst-case garanti: antall bins < (11/9) OPT + 6/9 (1D klassisk).
"""

import json
from pathlib import Path
from typing import List

import pandas as pd

from step02_naiv_pakking import (
    Bin,
    first_fit,
    summarize_bins,
    plot_bins,
    BIN_VOLUME_L,
)

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def ffd(items: List[dict]) -> List[Bin]:
    """Sorter etter fallende volum og kjor first-fit."""
    sorted_items = sorted(items, key=lambda x: x['volum_l'], reverse=True)
    return first_fit(sorted_items)


def load_items() -> List[dict]:
    df = pd.read_csv(DATA_DIR / 'products.csv')
    return df.to_dict(orient='records')


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 3: FIRST-FIT DECREASING (FFD)")
    print(f"{'='*60}")

    items = load_items()
    bins = ffd(items)
    summary = summarize_bins(bins)

    print("\n--- Resultat (FFD) ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    with open(OUTPUT_DIR / 'step03_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Resultater lagret: {OUTPUT_DIR / 'step03_results.json'}")

    plot_bins(bins, 'First-Fit Decreasing (FFD)',
              OUTPUT_DIR / 'bp_ffd_packing.png',
              highlight_color='#8CC8E5', highlight_edge='#1F6587')


if __name__ == '__main__':
    main()
