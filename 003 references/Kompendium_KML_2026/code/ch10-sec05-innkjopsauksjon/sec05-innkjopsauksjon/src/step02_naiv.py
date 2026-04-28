"""
Steg 2: Naiv tildeling (laveste enhetspris per kategori)
========================================================
Naiv metode: for hver kategori, tildel leverandoeren med laveste enhetspris
(blant enkeltbudene). Bundler ignoreres, kapasitetsbegrensninger ignoreres
(dvs. en leverandor kan i prinsippet vinne alle kategorier hvis den har
laveste pris i alle).

Dette er "lav-henteurt frukt"-tilnaermingen som mange innkjoeperavdelinger
bruker som utgangspunkt. Resultatet her blir sammenligningsgrunnlaget i
kapittelet.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

C_S1_FILL = '#8CC8E5'
C_S1_DARK = '#1F6587'
C_S2_FILL = '#97D4B7'
C_S2_DARK = '#307453'
C_S3_FILL = '#F6BA7C'
C_S3_DARK = '#9C540B'
C_S4_FILL = '#BD94D7'
C_S4_DARK = '#5A2C77'
C_TEXT = '#1F2933'

SUP_COLOR = {
    'L1': (C_S1_FILL, C_S1_DARK),
    'L2': (C_S2_FILL, C_S2_DARK),
    'L3': (C_S3_FILL, C_S3_DARK),
    'L4': (C_S4_FILL, C_S4_DARK),
}


def naive_allocation(df_cat: pd.DataFrame, df_unit: pd.DataFrame,
                     df_sup: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, c in df_cat.iterrows():
        cand = df_unit[df_unit['kategori'] == c['kategori']]
        if cand.empty:
            raise ValueError(f"Ingen bud paa kategori {c['kategori']}")
        best = cand.loc[cand['pris_per_enhet'].idxmin()]
        sup_name = df_sup[df_sup['leverandoer'] == best['leverandoer']
                          ]['navn'].iloc[0]
        rows.append({
            'kategori': c['kategori'],
            'navn': c['navn'],
            'volum': int(c['volum']),
            'vinner': best['leverandoer'],
            'vinner_navn': sup_name,
            'pris_per_enhet': float(best['pris_per_enhet']),
            'linekost_NOK': float(best['linekost_NOK']),
        })
    return pd.DataFrame(rows)


def plot_naive_allocation(df_alloc: pd.DataFrame, df_sup: pd.DataFrame,
                          output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10.8, 5.0))

    order = df_alloc['kategori'].tolist()
    costs = df_alloc['linekost_NOK'].to_numpy() / 1e6
    winners = df_alloc['vinner'].tolist()

    colors = [SUP_COLOR[w][0] for w in winners]
    edges = [SUP_COLOR[w][1] for w in winners]
    bars = ax.bar(order, costs, color=colors, edgecolor=edges, linewidth=1.3,
                  width=0.65)

    for bar, w, v in zip(bars, winners, costs):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max(costs) * 0.01,
                f'{w}\n{v:.2f} MNOK', ha='center', va='bottom',
                fontsize=9.5, color=C_TEXT)

    ax.set_xlabel('Kategori', fontsize=11)
    ax.set_ylabel('Linjekostnad (MNOK)', fontsize=11)
    total = costs.sum()
    ax.set_title(f'Naiv tildeling: laveste enhetspris per kategori '
                 f'(total = {total:.2f} MNOK)',
                 fontsize=12, fontweight='bold', color=C_TEXT)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, max(costs) * 1.22)

    # Legg til leverandor-legend
    handles = []
    seen = set()
    for w in winners:
        if w in seen:
            continue
        seen.add(w)
        sup_name = df_sup[df_sup['leverandoer'] == w]['navn'].iloc[0]
        handles.append(plt.Rectangle((0, 0), 1, 1,
                                     facecolor=SUP_COLOR[w][0],
                                     edgecolor=SUP_COLOR[w][1],
                                     linewidth=1.2,
                                     label=f'{w}: {sup_name}'))
    ax.legend(handles=handles, loc='upper left', fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: NAIV TILDELING")
    print("=" * 60)

    df_cat = pd.read_csv(DATA_DIR / 'kategorier.csv')
    df_unit = pd.read_csv(DATA_DIR / 'enkeltbud.csv')
    df_sup = pd.read_csv(DATA_DIR / 'leverandorer.csv')

    df_alloc = naive_allocation(df_cat, df_unit, df_sup)
    df_alloc.to_csv(OUTPUT_DIR / 'step02_naiv_alloc.csv', index=False)

    total = float(df_alloc['linekost_NOK'].sum())
    per_sup = (df_alloc.groupby('vinner')['linekost_NOK'].sum() / total).to_dict()

    summary = {
        'total_kostnad_NOK': round(total, 2),
        'total_kostnad_MNOK': round(total / 1e6, 3),
        'antall_kategorier': int(len(df_alloc)),
        'antall_leverandoerer_brukt': int(df_alloc['vinner'].nunique()),
        'andel_per_leverandoer': {k: round(v, 4) for k, v in per_sup.items()},
    }
    with open(OUTPUT_DIR / 'step02_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {OUTPUT_DIR / 'step02_summary.json'}")
    for k, v in summary.items():
        print(f"  {k}: {v}")

    plot_naive_allocation(df_alloc, df_sup, OUTPUT_DIR / 'wdp_naive_allocation.png')


if __name__ == '__main__':
    main()
