"""
Steg 1: Datainnsamling
======================
Syntetiske data for et lite nettverksdesign-problem:
  * 4 kandidatlagre (potensielle hubb-lokasjoner for en norsk sjomat-eksportor)
  * 25 kundeland/-regioner (europeiske og asiatiske markeder)
  * Usikker etterspoersel innenfor et boks-usikkerhetsomraade:
        d_j  i  [d_bar_j - delta_j,  d_bar_j + delta_j]

Produserer CSV-er + en figur som illustrerer usikkerhetsomraadet rundt
nominell etterspoersel.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Infografikk-farger
C_PRIMARY = '#1F6587'       # s1dark - nominal demand
C_PRIMARY_FILL = '#8CC8E5'  # s1 - usikkerhetsomraade
C_SECONDARY = '#307453'     # s2dark - warehouses
C_SECONDARY_FILL = '#97D4B7'
C_ACCENT = '#5A2C77'
C_ACCENT_FILL = '#BD94D7'
C_CORAL = '#ED9F9E'
C_CORAL_DARK = '#961D1C'
C_INK = '#1F2933'


# ---------------------------------------------------------------------------
#  4 kandidatlagre (hubb-lokasjoner)
# ---------------------------------------------------------------------------
WAREHOUSES = [
    # navn,         kap-kostnad k_i (NOK/enhet kap.), maks kap Z_max
    ('Stavanger',   180.0, 3500),  # hovedhubb, moderat pris
    ('Tromsoe',     220.0, 2500),  # lang avstand til Europa
    ('Rotterdam',   260.0, 4500),  # europeisk hubb
    ('Singapore',   300.0, 4000),  # asiatisk hubb
]


# ---------------------------------------------------------------------------
#  25 kundelokasjoner (europeiske + asiatiske markeder)
# ---------------------------------------------------------------------------
MARKETS = [
    # kundenavn, naer-hubb, nominell etterspoersel d_bar_j, usikkerhet delta_j
    # delta/d_bar-forholdet ligger rundt 0.4-0.6 -- betydelig usikkerhet.
    ('Oslo',         'Stavanger',  320, 130),
    ('Stockholm',    'Stavanger',  280, 110),
    ('Kopenhagen',   'Stavanger',  260, 100),
    ('Hamburg',      'Rotterdam',  450, 180),
    ('Berlin',       'Rotterdam',  380, 150),
    ('Paris',        'Rotterdam',  520, 210),
    ('Lyon',         'Rotterdam',  310, 120),
    ('London',       'Rotterdam',  560, 230),
    ('Manchester',   'Rotterdam',  290, 110),
    ('Madrid',       'Rotterdam',  340, 140),
    ('Milano',       'Rotterdam',  300, 120),
    ('Wien',         'Rotterdam',  220,  90),
    ('Warszawa',     'Rotterdam',  260, 110),
    ('Helsinki',     'Stavanger',  180,  70),
    ('Reykjavik',    'Tromsoe',    120,  55),
    ('Murmansk',     'Tromsoe',    140,  65),
    ('St.Petersburg','Stavanger',  210,  90),
    ('Tokyo',        'Singapore',  640, 260),
    ('Osaka',        'Singapore',  380, 160),
    ('Seoul',        'Singapore',  420, 170),
    ('Shanghai',     'Singapore',  580, 240),
    ('Hongkong',     'Singapore',  340, 140),
    ('Singapore-by', 'Singapore',  260, 110),
    ('Bangkok',      'Singapore',  240, 100),
    ('Jakarta',      'Singapore',  200,  90),
]


# ---------------------------------------------------------------------------
#  Transportkostnader c_{ij} (NOK/enhet) og straff (outsourcing) p_j
#  Syntetisk: billig fra naer-hubb, dyrere fra andre hubber; straff hoy.
# ---------------------------------------------------------------------------
def build_cost_matrices(df_w: pd.DataFrame, df_c: pd.DataFrame,
                         seed: int = 202604) -> tuple[np.ndarray, np.ndarray]:
    """Returnerer (c_ij, p_j) i NOK per enhet."""
    rng = np.random.default_rng(seed)
    n = len(df_w)
    m = len(df_c)
    c = np.zeros((n, m))

    # Grunnkostnad per hubb for aa sende til "sitt" nartmarked
    base_near = {
        'Stavanger':  40.0,
        'Tromsoe':    55.0,
        'Rotterdam':  45.0,
        'Singapore':  60.0,
    }
    # "Kryss-hubb" tillegg mellom regioner
    cross_region = {
        ('Stavanger', 'Rotterdam'):  35.0,
        ('Stavanger', 'Tromsoe'):    45.0,
        ('Stavanger', 'Singapore'): 180.0,
        ('Tromsoe',   'Stavanger'):  45.0,
        ('Tromsoe',   'Rotterdam'):  80.0,
        ('Tromsoe',   'Singapore'): 200.0,
        ('Rotterdam', 'Stavanger'):  35.0,
        ('Rotterdam', 'Tromsoe'):    80.0,
        ('Rotterdam', 'Singapore'): 160.0,
        ('Singapore', 'Stavanger'): 180.0,
        ('Singapore', 'Tromsoe'):   200.0,
        ('Singapore', 'Rotterdam'): 160.0,
    }

    wh_names = df_w['navn'].tolist()
    for j in range(m):
        near = df_c.iloc[j]['naer_hubb']
        for i in range(n):
            hubb = wh_names[i]
            if hubb == near:
                c[i, j] = base_near[hubb] + rng.uniform(-5, 10)
            else:
                c[i, j] = base_near[hubb] + cross_region[(hubb, near)] + rng.uniform(-8, 12)
    c = np.round(c, 1)

    # Straff ved manglende levering (spotmarked / tap av kunde): 8-12x dyreste rute
    # Hoy straff tvinger robust-loesningen til aa bygge mer kapasitet enn
    # deterministisk loesning.
    p = np.round(c.max(axis=0) * rng.uniform(8.0, 12.0, size=m), 0)
    return c, p


def warehouses_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(WAREHOUSES, columns=['navn', 'kap_kostnad', 'maks_kap'])
    df.insert(0, 'id', [f'W{i+1}' for i in range(len(df))])
    return df


def customers_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(MARKETS, columns=['navn', 'naer_hubb', 'd_bar', 'delta'])
    df.insert(0, 'id', [f'C{j+1:02d}' for j in range(len(df))])
    return df


def plot_uncertainty_set(df_c: pd.DataFrame, output_path: Path) -> None:
    """Illustrerer boks-usikkerhetsomraadet: nominelle verdier + intervaller."""
    fig, ax = plt.subplots(figsize=(11.0, 5.8))

    m = len(df_c)
    idx = np.arange(m)
    d_bar = df_c['d_bar'].to_numpy()
    delta = df_c['delta'].to_numpy()

    # Usikkerhetsomraade som barer
    ax.bar(idx, 2 * delta, bottom=d_bar - delta, color=C_PRIMARY_FILL,
           edgecolor=C_PRIMARY, linewidth=0.6, width=0.7,
           label='Usikkerhetsomraade $[d_j - \\delta_j,\\ d_j + \\delta_j]$')

    # Nominelle verdier d_bar_j
    ax.scatter(idx, d_bar, color=C_PRIMARY, s=28, zorder=3,
               label='Nominell $d_j$')

    ax.set_xticks(idx)
    ax.set_xticklabels(df_c['navn'], rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('Etterspoersel (tonn/aar)', fontsize=11)
    ax.set_title('Boks-usikkerhetsomraade rundt nominell etterspoersel',
                 fontsize=12, fontweight='bold', color=C_INK)
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(loc='upper right', fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    df_w = warehouses_dataframe()
    df_c = customers_dataframe()
    c, p = build_cost_matrices(df_w, df_c)

    df_w.to_csv(DATA_DIR / 'warehouses.csv', index=False)
    df_c.to_csv(DATA_DIR / 'markets.csv', index=False)
    pd.DataFrame(c, index=df_w['id'], columns=df_c['id']).to_csv(
        DATA_DIR / 'transport_cost.csv')
    pd.Series(p, index=df_c['id'], name='penalty').to_csv(
        DATA_DIR / 'penalty.csv')

    stats = {
        'antall_lagre_n': int(len(df_w)),
        'antall_kunder_m': int(len(df_c)),
        'sum_d_bar': int(df_c['d_bar'].sum()),
        'sum_delta': int(df_c['delta'].sum()),
        'min_d_bar': int(df_c['d_bar'].min()),
        'maks_d_bar': int(df_c['d_bar'].max()),
        'snitt_d_bar': round(float(df_c['d_bar'].mean()), 1),
        'snitt_rel_usikkerhet': round(float((df_c['delta'] / df_c['d_bar']).mean()), 3),
        'sum_maks_kap': int(df_w['maks_kap'].sum()),
        'snitt_kap_kostnad': round(float(df_w['kap_kostnad'].mean()), 1),
        'snitt_transport_c': round(float(c.mean()), 1),
        'snitt_straff_p': round(float(p.mean()), 1),
    }
    with open(OUTPUT_DIR / 'step01_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Statistikk lagret: {OUTPUT_DIR / 'step01_stats.json'}")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    plot_uncertainty_set(df_c, OUTPUT_DIR / 'ro_uncertainty_set.png')


if __name__ == '__main__':
    main()
