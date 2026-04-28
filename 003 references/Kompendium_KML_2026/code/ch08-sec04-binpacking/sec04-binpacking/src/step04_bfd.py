"""
Steg 4: Best-Fit Decreasing (BFD)
=================================
Sorter produktene etter fallende volum. For hvert element velg den bin-en
som gir minst ledig plass etter innlegging (tightest fit). Hvis ingen passer,
aapne en ny bin. BFD tenderer til aa fylle sterke bins forst og gir typisk
mer jevn fyllingsgrad enn FFD.
"""

import json
from pathlib import Path
from typing import List

import pandas as pd

from step02_naiv_pakking import (
    Bin,
    summarize_bins,
    plot_bins,
    BIN_VOLUME_L,
)

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def bfd(items: List[dict]) -> List[Bin]:
    """Best-Fit Decreasing: sorter fallende volum, plasser i tightest bin."""
    sorted_items = sorted(items, key=lambda x: x['volum_l'], reverse=True)
    bins: List[Bin] = []

    for it in sorted_items:
        best_bin = None
        best_slack = float('inf')
        for b in bins:
            if b.can_fit(it):
                slack = b.remaining_volume - it['volum_l']
                if slack < best_slack:
                    best_slack = slack
                    best_bin = b
        if best_bin is not None:
            best_bin.add(it)
        else:
            new_bin = Bin(bin_id=len(bins) + 1)
            new_bin.add(it)
            bins.append(new_bin)
    return bins


def load_items() -> List[dict]:
    df = pd.read_csv(DATA_DIR / 'products.csv')
    return df.to_dict(orient='records')


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 4: BEST-FIT DECREASING (BFD)")
    print(f"{'='*60}")

    items = load_items()
    bins = bfd(items)
    summary = summarize_bins(bins)

    print("\n--- Resultat (BFD) ---")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    with open(OUTPUT_DIR / 'step04_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Resultater lagret: {OUTPUT_DIR / 'step04_results.json'}")

    plot_bins(bins, 'Best-Fit Decreasing (BFD)',
              OUTPUT_DIR / 'bp_bfd_packing.png',
              highlight_color='#97D4B7', highlight_edge='#307453')


if __name__ == '__main__':
    main()
