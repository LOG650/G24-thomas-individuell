"""
Steg 1: Datainnsamling for AHP + TOPSIS
=======================================
Definerer leverandører, kriterier, ytelsesmatrise og parvis
sammenligningsmatrise for AHP.

- 6 leverandører (Alfa, Beta, Gamma, Delta, Epsilon, Zeta)
- 5 kriterier (pris, kvalitet, leveringstid, fleksibilitet, bærekraft)
- Parvis sammenligningsmatrise (Saatys 1-9 skala)
- Ytelsesmatrise med realistiske verdier for hver leverandør
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


# ----------------------------------------------------------------------
# Grunndata: leverandører og kriterier
# ----------------------------------------------------------------------

SUPPLIERS = ['Alfa', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta']

CRITERIA = ['Pris', 'Kvalitet', 'Leveringstid', 'Fleksibilitet', 'Bærekraft']

# Typer: 'cost' (lavere er bedre) eller 'benefit' (høyere er bedre)
CRITERION_TYPES = {
    'Pris': 'cost',            # NOK per enhet -- lavere er bedre
    'Kvalitet': 'benefit',     # Skår 1-10 -- høyere er bedre
    'Leveringstid': 'cost',    # Dager -- lavere er bedre
    'Fleksibilitet': 'benefit',  # Skår 1-10 -- høyere er bedre
    'Bærekraft': 'benefit',    # Skår 1-10 -- høyere er bedre
}

# Ytelsesmatrise: rader = leverandører, kolonner = kriterier
# Pris i NOK/enhet, leveringstid i dager, resten på skala 1-10
PERFORMANCE_DATA = np.array([
    # Pris   Kvalitet  Leveringstid  Fleksibilitet  Bærekraft
    [185,    8.2,      14,           7.0,           8.5],   # Alfa
    [165,    7.0,      21,           8.5,           6.0],   # Beta
    [210,    9.1,      10,           6.5,           9.2],   # Gamma
    [175,    7.8,      18,           7.5,           7.0],   # Delta
    [195,    8.6,      12,           8.0,           8.0],   # Epsilon
    [155,    6.4,      25,           9.0,           5.5],   # Zeta
])


# ----------------------------------------------------------------------
# Parvis sammenligningsmatrise (AHP) for de 5 kriteriene
# ----------------------------------------------------------------------
# Saatys skala 1-9:
#   1 = like viktige
#   3 = svakt viktigere, 5 = klart viktigere
#   7 = sterkt viktigere, 9 = absolutt viktigere
#   Resiproke verdier for motsatt retning.
#
# Vi antar en innkjøpssjef som legger mest vekt på kvalitet
# og pris, deretter leveringstid, og litt mindre vekt
# på fleksibilitet og bærekraft.
#
#            Pris  Kval   Lev    Flex   Bær
# Pris       [ 1,   1/2,   2,     3,     3  ],
# Kvalitet   [ 2,   1,     3,     4,     4  ],
# Leveringst [ 1/2, 1/3,   1,     2,     2  ],
# Fleksibili [ 1/3, 1/4,   1/2,   1,     2  ],
# Bærekraft  [ 1/3, 1/4,   1/2,   1/2,   1  ],
PAIRWISE_MATRIX = np.array([
    [1.0,   1/2,  2.0,  3.0,  3.0],
    [2.0,   1.0,  3.0,  4.0,  4.0],
    [1/2,   1/3,  1.0,  2.0,  2.0],
    [1/3,   1/4,  1/2,  1.0,  2.0],
    [1/3,   1/4,  1/2,  1/2,  1.0],
])


def get_performance_dataframe() -> pd.DataFrame:
    """Returnerer ytelsesmatrisen som en pandas DataFrame."""
    return pd.DataFrame(PERFORMANCE_DATA, index=SUPPLIERS, columns=CRITERIA)


def get_pairwise_dataframe() -> pd.DataFrame:
    """Returnerer parvis sammenligningsmatrisen som pandas DataFrame."""
    return pd.DataFrame(PAIRWISE_MATRIX, index=CRITERIA, columns=CRITERIA)


def descriptive_statistics(perf: pd.DataFrame) -> dict:
    """Enkel deskriptiv statistikk per kriterium."""
    stats = {}
    for col in perf.columns:
        s = perf[col]
        stats[col] = {
            'min': float(round(s.min(), 3)),
            'max': float(round(s.max(), 3)),
            'mean': float(round(s.mean(), 3)),
            'std': float(round(s.std(ddof=0), 3)),
            'type': CRITERION_TYPES[col],
        }
    return stats


def plot_performance_heatmap(perf: pd.DataFrame, output_path: Path) -> None:
    """Lag heatmap av ytelsesmatrisen (normalisert per kolonne for sammenligning)."""
    # Min-max-normaliser per kolonne for visualisering (ikke brukt i TOPSIS)
    norm = (perf - perf.min()) / (perf.max() - perf.min())
    # Snu cost-kriterier så høyere er bedre visuelt
    for col in perf.columns:
        if CRITERION_TYPES[col] == 'cost':
            norm[col] = 1.0 - norm[col]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    im = ax.imshow(norm.values, aspect='auto', cmap='Blues', vmin=0, vmax=1)

    ax.set_xticks(range(len(perf.columns)))
    ax.set_xticklabels(perf.columns, fontsize=11)
    ax.set_yticks(range(len(perf.index)))
    ax.set_yticklabels(perf.index, fontsize=11)

    # Vis faktiske (ikke-normaliserte) verdier i cellene
    for i in range(perf.shape[0]):
        for j in range(perf.shape[1]):
            val = perf.values[i, j]
            text = f"{val:.0f}" if val >= 10 else f"{val:.1f}"
            color = 'white' if norm.values[i, j] > 0.55 else 'black'
            ax.text(j, i, text, ha='center', va='center', color=color, fontsize=10)

    ax.set_title('Ytelsesmatrise for leverandører (faktiske verdier; fargeskala: relativ ønskelighet)',
                 fontsize=11, fontweight='bold')
    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Relativ ønskelighet (0 = verst, 1 = best)', fontsize=9)
    cbar.ax.tick_params(labelsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_pairwise_heatmap(pairwise: pd.DataFrame, output_path: Path) -> None:
    """Heatmap av parvis sammenligningsmatrise."""
    fig, ax = plt.subplots(figsize=(7, 6))
    im = ax.imshow(np.log(pairwise.values), cmap='RdBu_r',
                   vmin=-np.log(9), vmax=np.log(9))

    ax.set_xticks(range(len(pairwise.columns)))
    ax.set_xticklabels(pairwise.columns, fontsize=10, rotation=25, ha='right')
    ax.set_yticks(range(len(pairwise.index)))
    ax.set_yticklabels(pairwise.index, fontsize=10)

    for i in range(pairwise.shape[0]):
        for j in range(pairwise.shape[1]):
            val = pairwise.values[i, j]
            if val >= 1:
                text = f"{val:.0f}" if val == int(val) else f"{val:.2f}"
            else:
                text = f"1/{int(round(1/val))}"
            ax.text(j, i, text, ha='center', va='center',
                    color='black', fontsize=11)

    ax.set_title('Parvis sammenligningsmatrise $A$ (Saatys skala 1-9)',
                 fontsize=11, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    DATA_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 1: DATAINNSAMLING")
    print(f"{'='*60}")

    perf = get_performance_dataframe()
    pairwise = get_pairwise_dataframe()

    print(f"\nAntall leverandører: {len(perf.index)}")
    print(f"Antall kriterier:    {len(perf.columns)}")
    print("\n--- Ytelsesmatrise ---")
    print(perf.to_string())
    print("\n--- Parvis sammenligningsmatrise ---")
    print(pairwise.round(3).to_string())

    # Deskriptiv statistikk
    stats = descriptive_statistics(perf)
    print("\n--- Deskriptiv statistikk per kriterium ---")
    for crit, s in stats.items():
        print(f"  {crit:<14s} type={s['type']:<7s}  min={s['min']}  "
              f"max={s['max']}  mean={s['mean']}  std={s['std']}")

    # Lagre grunndata til CSV for inspeksjon
    perf.to_csv(DATA_DIR / 'performance.csv', float_format='%.3f')
    pairwise.to_csv(DATA_DIR / 'pairwise.csv', float_format='%.6f')

    # JSON med alt som kan brukes i LaTeX-tabeller
    results = {
        'suppliers': SUPPLIERS,
        'criteria': CRITERIA,
        'criterion_types': CRITERION_TYPES,
        'performance': perf.round(3).to_dict(orient='index'),
        'pairwise': pairwise.round(6).to_dict(orient='index'),
        'statistics': stats,
    }
    with open(OUTPUT_DIR / 'step01_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step01_results.json'}")

    # Figurer
    plot_performance_heatmap(perf, OUTPUT_DIR / 'ahp_ytelse_heatmap.png')
    plot_pairwise_heatmap(pairwise, OUTPUT_DIR / 'ahp_parvis_heatmap.png')


if __name__ == '__main__':
    main()
