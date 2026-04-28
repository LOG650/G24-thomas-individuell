"""
Steg 5: 2D shelf-packing (pedagogisk visualisering)
===================================================
For aa gjore 2D-varianten konkret, pakker vi en rekke produkter i et rektangel
60 x 40 cm (bunnflaten av standardesken) med Next-Fit Decreasing Height
(NFDH) shelf-algoritmen:

  - Sorter artiklene etter fallende hoyde.
  - Legg til i aktiv hylle saa lenge det er plass i bredden.
  - Start en ny hylle over naar det ikke er mer plass.

Dette er en klassisk 2D shelf-heuristikk som gir en nedre grense paa full-
utnyttelse og lar oss tegne en intuitiv layout av hvordan artiklene ligger i
esken.
"""

import json
from pathlib import Path
from typing import List

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

SHELF_W = 60.0   # eske-lengde (cm) - horisontal akse
SHELF_H = 40.0   # eske-bredde (cm)  - vertikal akse

N_DEMO = 18      # antall artikler i demoen


def nfdh_pack(rects: List[dict], W: float = SHELF_W, H: float = SHELF_H) -> dict:
    """Next-Fit Decreasing Height for 2D shelf-pakking.

    Hver `rect` forventer noklene w og h (cm). Returner en dict med placements
    og hyllemetadata.
    """
    # Sorter etter fallende hoyde
    sorted_rects = sorted(rects, key=lambda r: r['h'], reverse=True)

    shelves = []          # liste av (y_bottom, shelf_height)
    placements = []       # liste av (rect, x, y, shelf_idx)

    shelf_y = 0.0
    shelf_x = 0.0
    shelf_h_current = 0.0

    for r in sorted_rects:
        if r['w'] > W or r['h'] > H:
            continue  # passer ikke

        # Hvis forste rect i hyllen, aapne ny hylle
        if shelf_h_current == 0.0:
            if shelf_y + r['h'] > H + 1e-9:
                break  # ikke mer plass vertikalt
            shelf_h_current = r['h']
            shelves.append({'y': shelf_y, 'h': shelf_h_current})

        # Passer rect i bredden paa aktiv hylle?
        if shelf_x + r['w'] <= W + 1e-9:
            placements.append({
                'sku': r.get('sku', ''),
                'x': shelf_x, 'y': shelf_y,
                'w': r['w'], 'h': r['h'],
                'shelf': len(shelves) - 1,
            })
            shelf_x += r['w']
        else:
            # Lukk hyllen, aapne ny
            new_y = shelf_y + shelf_h_current
            if new_y + r['h'] > H + 1e-9:
                break
            shelf_y = new_y
            shelf_x = 0.0
            shelf_h_current = r['h']
            shelves.append({'y': shelf_y, 'h': shelf_h_current})
            placements.append({
                'sku': r.get('sku', ''),
                'x': shelf_x, 'y': shelf_y,
                'w': r['w'], 'h': r['h'],
                'shelf': len(shelves) - 1,
            })
            shelf_x += r['w']

    used_area = sum(p['w'] * p['h'] for p in placements)
    total_area = W * H
    utilization = used_area / total_area if total_area > 0 else 0.0

    return {
        'placements': placements,
        'shelves': shelves,
        'used_area_cm2': used_area,
        'total_area_cm2': total_area,
        'utilization': utilization,
        'n_packed': len(placements),
    }


def plot_shelf_layout(result: dict, title: str, output_path: Path) -> None:
    """Tegn pakkelayout: eske-rektangel med rektangulaere artikler og hyllestrek."""
    W, H = SHELF_W, SHELF_H
    fig, ax = plt.subplots(figsize=(9, 6.2))

    # Eskerammen
    box = patches.Rectangle((0, 0), W, H, linewidth=2.0,
                            edgecolor='#1F2933', facecolor='#F4F7FB')
    ax.add_patch(box)

    # Artikler - alternerende farger for visuell gruppering
    fill_palette = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']
    edge_palette = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']

    for p in result['placements']:
        idx = p['shelf'] % len(fill_palette)
        rect = patches.Rectangle((p['x'], p['y']), p['w'], p['h'],
                                 linewidth=0.9,
                                 edgecolor=edge_palette[idx],
                                 facecolor=fill_palette[idx],
                                 alpha=0.85)
        ax.add_patch(rect)
        # Legg SKU-etikett sentrert hvis rektangelet er stort nok
        if p['w'] >= 7 and p['h'] >= 5:
            ax.text(p['x'] + p['w'] / 2, p['y'] + p['h'] / 2,
                    p['sku'].replace('SKU', ''),
                    ha='center', va='center', fontsize=8, color='#1F2933')

    # Hyllestreker
    for s in result['shelves']:
        ax.plot([0, W], [s['y'], s['y']], color='#556270',
                linestyle=':', linewidth=0.8)

    util = result['utilization']
    n = result['n_packed']
    ax.set_xlim(-1, W + 1)
    ax.set_ylim(-1, H + 2)
    ax.set_aspect('equal')
    ax.set_xlabel('lengde (cm)', fontsize=11)
    ax.set_ylabel('bredde (cm)', fontsize=11)
    ax.set_title(f'{title} - {n} artikler, areautnyttelse = {util:.1%}',
                 fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 5: 2D SHELF-PACKING (PEDAGOGISK)")
    print(f"{'='*60}")

    df = pd.read_csv(DATA_DIR / 'products.csv')
    # For 2D shelf-visualisering viser vi bunnflaten av esken.
    # Vi genererer et syntetisk utvalg av smaa, flate artikler (bokformat)
    # slik at flere artikler faktisk rommes i 2D-layouten og den
    # pedagogiske illustrasjonen blir leselig.
    rng_demo = np.random.default_rng(31415)
    widths = rng_demo.uniform(8, 18, N_DEMO)
    heights = rng_demo.uniform(6, 14, N_DEMO)
    demo = pd.DataFrame({
        'sku': [f'A{i+1:02d}' for i in range(N_DEMO)],
        'lengde_cm': np.round(widths, 1),
        'bredde_cm': np.round(heights, 1),
    })
    demo['volum_l'] = demo['lengde_cm'] * demo['bredde_cm'] / 100.0

    rects = [{
        'sku': r['sku'],
        'w': float(r['lengde_cm']),
        'h': float(r['bredde_cm']),
    } for _, r in demo.iterrows()]

    result = nfdh_pack(rects)
    print(f"\nPakket {result['n_packed']} av {len(rects)} artikler")
    print(f"Areautnyttelse: {result['utilization']:.3f}")
    print(f"Antall hyller: {len(result['shelves'])}")

    out = {
        'shelf_w_cm': SHELF_W,
        'shelf_h_cm': SHELF_H,
        'n_candidates': int(len(rects)),
        'n_packed': int(result['n_packed']),
        'antall_hyller': int(len(result['shelves'])),
        'utilization': round(result['utilization'], 4),
    }
    with open(OUTPUT_DIR / 'step05_results.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Resultater lagret: {OUTPUT_DIR / 'step05_results.json'}")

    plot_shelf_layout(result, 'NFDH shelf-pakking i 60 x 40 cm eske',
                      OUTPUT_DIR / 'bp_shelf_layout.png')


if __name__ == '__main__':
    main()
