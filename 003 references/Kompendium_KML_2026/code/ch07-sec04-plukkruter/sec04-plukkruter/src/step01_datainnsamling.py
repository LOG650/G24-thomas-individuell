"""
Steg 1: Datainnsamling for plukkruteeksempel
=============================================
Genererer et syntetisk parallell-gang-lager med 10 ganger, 20 hyller per side og
2 sider per gang (totalt 400 plukklokasjoner). Deretter genereres 500 plukklister
med tilfeldige størrelser mellom 10 og 30 lokasjoner.

Lagrer layout og plukklister som JSON i output/.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Lagerparametere
N_AISLES = 10            # antall ganger
N_SHELVES = 20           # antall hyllerader per side
N_SIDES = 2              # to sider per gang (venstre og høyre)
AISLE_SPACING = 5.0      # meter mellom gangsentre
SHELF_SPACING = 1.0      # meter mellom hyller langs en gang
CROSS_AISLE_Y_FRONT = 0.0
CROSS_AISLE_Y_BACK = (N_SHELVES + 1) * SHELF_SPACING  # bakre kryssgang
DEPOT_AISLE = 0          # depot ligger til venstre for gang 0

N_PICKLISTS = 500
MIN_PICKS = 10
MAX_PICKS = 30

RNG_SEED = 20260420


def build_layout() -> dict:
    """Bygg parallell-gang-lager som dict med lokasjoner og kryssganger.

    Koordinatsystem:
    - x = horisontal posisjon (gang-indeks * AISLE_SPACING)
    - y = vertikal posisjon (hylle-indeks * SHELF_SPACING)
    Hver gang har to sider (venstre/høyre) med x-offset +/- 0.5.
    Depot plasseres til venstre for gang 0 i fronten (y=0).
    """
    locations = []  # liste av dict-er med id, aisle, shelf, side, x, y
    loc_id = 0
    for aisle in range(N_AISLES):
        x_center = aisle * AISLE_SPACING
        for shelf in range(1, N_SHELVES + 1):
            y = shelf * SHELF_SPACING
            for side in ('L', 'R'):
                x = x_center - 0.5 if side == 'L' else x_center + 0.5
                locations.append({
                    'id': loc_id,
                    'aisle': aisle,
                    'shelf': shelf,
                    'side': side,
                    'x': x,
                    'y': y,
                })
                loc_id += 1

    depot = {
        'id': -1,
        'x': DEPOT_AISLE * AISLE_SPACING - AISLE_SPACING / 2,
        'y': CROSS_AISLE_Y_FRONT,
    }

    return {
        'n_aisles': N_AISLES,
        'n_shelves': N_SHELVES,
        'n_sides': N_SIDES,
        'aisle_spacing': AISLE_SPACING,
        'shelf_spacing': SHELF_SPACING,
        'front_y': CROSS_AISLE_Y_FRONT,
        'back_y': CROSS_AISLE_Y_BACK,
        'depot': depot,
        'locations': locations,
        'n_locations': len(locations),
    }


def generate_picklists(layout: dict, n_lists: int = N_PICKLISTS,
                       min_picks: int = MIN_PICKS, max_picks: int = MAX_PICKS,
                       seed: int = RNG_SEED) -> list:
    """Generer n_lists plukklister, hver med k_i tilfeldige lokasjoner (uten repetisjon)."""
    rng = np.random.default_rng(seed)
    n_loc = layout['n_locations']
    picklists = []
    for i in range(n_lists):
        k = int(rng.integers(min_picks, max_picks + 1))
        ids = rng.choice(n_loc, size=k, replace=False).tolist()
        picklists.append({'id': i, 'k': k, 'location_ids': [int(x) for x in ids]})
    return picklists


def plot_layout(layout: dict, picklist: list, output_path: Path) -> None:
    """Tegn lageret i fugleperspektiv med én eksempel-plukkliste markert."""
    fig, ax = plt.subplots(figsize=(12, 6))

    n_aisles = layout['n_aisles']
    n_shelves = layout['n_shelves']
    front_y = layout['front_y']
    back_y = layout['back_y']

    # Tegn hyller (grå rektangler langs hver gang)
    for aisle in range(n_aisles):
        x_center = aisle * AISLE_SPACING
        ax.fill_between([x_center - 0.8, x_center - 0.2],
                        SHELF_SPACING * 0.5, back_y - SHELF_SPACING * 0.5,
                        color='#CBD5E1', alpha=0.5, zorder=1)
        ax.fill_between([x_center + 0.2, x_center + 0.8],
                        SHELF_SPACING * 0.5, back_y - SHELF_SPACING * 0.5,
                        color='#CBD5E1', alpha=0.5, zorder=1)
        # Gangmidtlinje (for referanse)
        ax.plot([x_center, x_center], [front_y, back_y], ':', color='#94a3b8',
                linewidth=0.7, zorder=2)

    # Kryssganger (front og bak)
    ax.plot([0 - AISLE_SPACING / 2, (n_aisles - 1) * AISLE_SPACING + AISLE_SPACING / 2],
            [front_y, front_y], '-', color='#1F2933', linewidth=1.0, zorder=2)
    ax.plot([0 - AISLE_SPACING / 2, (n_aisles - 1) * AISLE_SPACING + AISLE_SPACING / 2],
            [back_y, back_y], '-', color='#1F2933', linewidth=1.0, zorder=2)

    # Plukklokasjoner markert
    pick_ids = set(picklist)
    for loc in layout['locations']:
        color = '#961D1C' if loc['id'] in pick_ids else '#cbd5e1'
        size = 28 if loc['id'] in pick_ids else 4
        zorder = 4 if loc['id'] in pick_ids else 3
        ax.scatter(loc['x'], loc['y'], s=size, color=color, zorder=zorder,
                   edgecolors='none')

    # Depot
    depot = layout['depot']
    ax.scatter(depot['x'], depot['y'], s=120, marker='s', color='#307453',
               edgecolors='#1F2933', linewidths=1.0, zorder=5, label='Depot')

    # Gangnummer
    for aisle in range(n_aisles):
        x_center = aisle * AISLE_SPACING
        ax.text(x_center, -1.0, f'G{aisle+1}', ha='center', va='top',
                fontsize=9, color='#556270')

    ax.set_xlabel('$x$ (meter)', fontsize=12)
    ax.set_ylabel('$y$ (meter)', fontsize=12)
    ax.set_title('Parallell-gang-lager: 10 ganger x 20 hyller x 2 sider = 400 lokasjoner',
                 fontsize=11, fontweight='bold')
    ax.set_xlim(-AISLE_SPACING, (n_aisles - 1) * AISLE_SPACING + AISLE_SPACING)
    ax.set_ylim(-2.0, back_y + 1.0)
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.25, zorder=0)

    # Legende manuelt
    from matplotlib.lines import Line2D
    legend_items = [
        Line2D([0], [0], marker='s', color='w', markerfacecolor='#307453',
               markeredgecolor='#1F2933', markersize=10, label='Depot'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#961D1C',
               markersize=8, label='Plukklokasjon (ordre)'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#cbd5e1',
               markersize=5, label='Ledig hylleplass'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    layout = build_layout()
    print(f"\nLayout bygget:")
    print(f"  Ganger:       {layout['n_aisles']}")
    print(f"  Hyller/side:  {layout['n_shelves']}")
    print(f"  Sider/gang:   {layout['n_sides']}")
    print(f"  Total lokasjoner: {layout['n_locations']}")
    print(f"  Gangbredde (senter-senter): {layout['aisle_spacing']} m")
    print(f"  Hylleavstand:               {layout['shelf_spacing']} m")
    print(f"  Frontgang y:  {layout['front_y']}")
    print(f"  Bakgang y:    {layout['back_y']}")

    picklists = generate_picklists(layout)
    sizes = [pl['k'] for pl in picklists]
    print(f"\nGenererte {len(picklists)} plukklister")
    print(f"  Min picks: {min(sizes)}")
    print(f"  Max picks: {max(sizes)}")
    print(f"  Snitt:     {np.mean(sizes):.2f}")

    # Lagre layout
    with open(OUTPUT_DIR / 'layout.json', 'w', encoding='utf-8') as f:
        json.dump(layout, f, indent=2, ensure_ascii=False)
    print(f"\nLayout lagret: {OUTPUT_DIR / 'layout.json'}")

    # Lagre plukklister
    with open(OUTPUT_DIR / 'picklists.json', 'w', encoding='utf-8') as f:
        json.dump(picklists, f, indent=2, ensure_ascii=False)
    print(f"Plukklister lagret: {OUTPUT_DIR / 'picklists.json'}")

    # Plot layout med ett eksempel
    example_picklist = picklists[0]['location_ids']
    plot_layout(layout, example_picklist, OUTPUT_DIR / 'pickrt_layout.png')

    # Oppsummering av eksempel-plukklisten
    summary = {
        'n_aisles': layout['n_aisles'],
        'n_shelves': layout['n_shelves'],
        'n_sides': layout['n_sides'],
        'n_locations': layout['n_locations'],
        'n_picklists': len(picklists),
        'pick_size_min': int(min(sizes)),
        'pick_size_max': int(max(sizes)),
        'pick_size_mean': round(float(np.mean(sizes)), 2),
        'example_picklist_id': picklists[0]['id'],
        'example_picklist_k': picklists[0]['k'],
        'aisle_spacing_m': AISLE_SPACING,
        'shelf_spacing_m': SHELF_SPACING,
    }
    with open(OUTPUT_DIR / 'step01_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Oppsummering lagret: {OUTPUT_DIR / 'step01_summary.json'}")


if __name__ == '__main__':
    main()
