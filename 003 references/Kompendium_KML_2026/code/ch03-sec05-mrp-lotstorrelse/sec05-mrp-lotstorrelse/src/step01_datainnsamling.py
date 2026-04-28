"""
Steg 1: Datainnsamling for MRP-eksempel (sykkelmontering)
=========================================================
Definerer en tre-nivas stykkliste (BOM) for en sykkel, samt leveringstider,
lagerbeholdning, kostnadsparametere og hovedproduksjonsplan (MPS) over
12 uker. Lagrer parametere og genererer BOM-traet som figur.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import networkx as nx

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
DATA_DIR = Path(__file__).parent.parent / 'data'

# Farger fra bokens fargeskjema (infografikk)
S1 = '#8CC8E5'   # lys bla
S2 = '#97D4B7'   # lys gron
S3 = '#F6BA7C'   # lys orange
S4 = '#BD94D7'   # lys lilla
S5 = '#ED9F9E'   # lys korall
S1D = '#1F6587'
S2D = '#307453'
S3D = '#9C540B'
S4D = '#5A2C77'
S5D = '#961D1C'
INK = '#1F2933'
INKMUTED = '#556270'


def build_bom() -> dict:
    """
    Bygg en 3-nivas BOM for produktet "Sykkel" (sluttprodukt).

    Struktur:
        Sykkel (niva 0)
        |-- Ramme (niva 1)      1 per sykkel
        |   |-- Stalrors (niva 2)   4 per ramme
        |-- Hjul (niva 1)       2 per sykkel
        |   |-- Eik (niva 2)        32 per hjul
        |-- Bremsesett (niva 1) 1 per sykkel

    Returnerer dict med komponentdata.
    """
    components = {
        'Sykkel':      {'level': 0, 'parent': None,       'qty_per_parent': 1,  'lead_time': 1, 'on_hand': 10, 'setup_cost': 200, 'holding_cost': 5.0,  'eoq_demand_wk': None},
        'Ramme':       {'level': 1, 'parent': 'Sykkel',   'qty_per_parent': 1,  'lead_time': 2, 'on_hand': 15, 'setup_cost': 150, 'holding_cost': 2.5,  'eoq_demand_wk': None},
        'Hjul':        {'level': 1, 'parent': 'Sykkel',   'qty_per_parent': 2,  'lead_time': 1, 'on_hand': 30, 'setup_cost': 100, 'holding_cost': 1.5,  'eoq_demand_wk': None},
        'Bremsesett':  {'level': 1, 'parent': 'Sykkel',   'qty_per_parent': 1,  'lead_time': 1, 'on_hand': 20, 'setup_cost':  80, 'holding_cost': 1.2,  'eoq_demand_wk': None},
        'Stalrors':    {'level': 2, 'parent': 'Ramme',    'qty_per_parent': 4,  'lead_time': 2, 'on_hand': 40, 'setup_cost':  60, 'holding_cost': 0.4,  'eoq_demand_wk': None},
        'Eik':         {'level': 2, 'parent': 'Hjul',     'qty_per_parent': 32, 'lead_time': 1, 'on_hand': 300,'setup_cost':  50, 'holding_cost': 0.05, 'eoq_demand_wk': None},
    }
    return components


def build_mps(n_weeks: int = 12) -> pd.Series:
    """
    Bygg hovedproduksjonsplanen (MPS) for sluttproduktet "Sykkel" over 12 uker.
    Variasjon: sesong og kampanjer.
    """
    weeks = np.arange(1, n_weeks + 1)
    base = 20
    # Sesongbolge + en kampanje i uke 7-9
    mps = base + 4 * np.sin(2 * np.pi * (weeks - 1) / 12.0)
    mps[6:9] += 10  # kampanje
    mps = np.round(mps).astype(int)
    return pd.Series(mps, index=pd.Index(weeks, name='uke'), name='MPS')


def plot_bom_tree(components: dict, output_path: Path) -> None:
    """Plott BOM-treet som et hierarkisk trediagram."""
    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Posisjonering (niva -> y, indeks innen niva -> x)
    level_items = {0: [], 1: [], 2: []}
    for name, c in components.items():
        level_items[c['level']].append(name)

    positions = {}
    level_y = {0: 2.5, 1: 1.5, 2: 0.5}
    # Setter x-posisjoner slik at barn ligger under foreldre
    # Niva 0: sykkel sentralt
    positions['Sykkel'] = (3.0, level_y[0])
    # Niva 1: Ramme, Hjul, Bremsesett
    positions['Ramme']      = (1.0, level_y[1])
    positions['Hjul']       = (3.0, level_y[1])
    positions['Bremsesett'] = (5.0, level_y[1])
    # Niva 2
    positions['Stalrors'] = (1.0, level_y[2])
    positions['Eik']      = (3.0, level_y[2])

    colors = {
        0: (S1, S1D),
        1: (S2, S2D),
        2: (S3, S3D),
    }

    # Tegn kanter (foreldre -> barn) med qty-label
    for name, c in components.items():
        if c['parent'] is None:
            continue
        x1, y1 = positions[c['parent']]
        x2, y2 = positions[name]
        ax.plot([x1, x2], [y1 - 0.18, y2 + 0.18], color=INKMUTED, lw=1.0, zorder=1)
        # qty-label midt pa kanten
        mx, my = (x1 + x2) / 2.0, (y1 + y2) / 2.0
        ax.text(mx + 0.08, my, f"x{c['qty_per_parent']}",
                fontsize=9, color=INK, ha='left', va='center',
                bbox=dict(boxstyle='round,pad=0.15', fc='white', ec=INKMUTED, lw=0.5))

    # Tegn noder
    for name, (x, y) in positions.items():
        fc, ec = colors[components[name]['level']]
        box_w, box_h = 1.5, 0.36
        rect = plt.Rectangle((x - box_w / 2, y - box_h / 2), box_w, box_h,
                             fc=fc, ec=ec, lw=1.6, zorder=2)
        ax.add_patch(rect)
        lt = components[name]['lead_time']
        oh = components[name]['on_hand']
        ax.text(x, y + 0.04, name, fontsize=10.5, fontweight='bold',
                color=INK, ha='center', va='center', zorder=3)
        ax.text(x, y - 0.13, f'LT={lt}, OH={oh}', fontsize=8,
                color=INKMUTED, ha='center', va='center', zorder=3)

    # Niva-labels
    for lvl, ypos in level_y.items():
        ax.text(-0.3, ypos, f'Niva {lvl}', fontsize=10, color=INKMUTED,
                ha='right', va='center', fontweight='bold')

    ax.set_xlim(-1.2, 6.4)
    ax.set_ylim(0.0, 3.2)
    ax.axis('off')
    ax.set_title('Stykkliste (BOM) for sykkelmontering',
                 fontsize=12, fontweight='bold', color=INK, pad=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def plot_mps(mps: pd.Series, output_path: Path) -> None:
    """Plott MPS som sojlediagram."""
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(mps.index, mps.values, color=S1, edgecolor=S1D, lw=1.2, width=0.7)
    for x, y in zip(mps.index, mps.values):
        ax.text(x, y + 0.5, str(int(y)), ha='center', va='bottom',
                fontsize=9, color=INK)
    ax.set_xlabel('Uke $t$', fontsize=12)
    ax.set_ylabel('Bruttoetterspørsel $D_t$ (sykler)', fontsize=12)
    ax.set_title('Hovedproduksjonsplan (MPS) for sluttprodukt',
                 fontsize=12, fontweight='bold', color=INK)
    ax.set_xticks(mps.index)
    ax.grid(True, axis='y', alpha=0.3)
    ax.set_axisbelow(True)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING (MRP / BOM)')
    print('=' * 60)

    components = build_bom()
    mps = build_mps(n_weeks=12)

    print('\nKomponenter:')
    df_bom = pd.DataFrame(components).T
    print(df_bom[['level', 'parent', 'qty_per_parent', 'lead_time', 'on_hand',
                  'setup_cost', 'holding_cost']].to_string())

    print('\nMPS for Sykkel:')
    print(mps.to_string())

    # Lagre som JSON
    data = {
        'components': components,
        'mps': {int(k): int(v) for k, v in mps.items()},
        'n_weeks': int(len(mps)),
    }
    with open(OUTPUT_DIR / 'bom_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f'\nData lagret: {OUTPUT_DIR / "bom_data.json"}')

    # Lagre BOM og MPS som CSV i data/ for konsistens
    df_bom.to_csv(DATA_DIR / 'bom.csv', index_label='component')
    mps.to_csv(DATA_DIR / 'mps.csv')
    print(f'BOM lagret: {DATA_DIR / "bom.csv"}')
    print(f'MPS lagret: {DATA_DIR / "mps.csv"}')

    # Generer figurer
    plot_bom_tree(components, OUTPUT_DIR / 'mrp_bom_tree.png')
    plot_mps(mps, OUTPUT_DIR / 'mrp_mps.png')


if __name__ == '__main__':
    main()
