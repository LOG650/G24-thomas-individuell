"""
Steg 1: Datainnsamling
======================
Syntetisk innkjopsauksjon for norsk entreprenoer (Nordbygg Entreprenoer AS)
som skal kjoepe byggevarer til et stort boligprosjekt.

Kategorier (produktgrupper som skal anskaffes, K = 8):
  C1  Betong og moertel     (volum = 1200 m3)
  C2  Armeringsstaal         (volum =  180 tonn)
  C3  Isolasjon              (volum = 4000 m2)
  C4  Gips og plater         (volum = 6500 m2)
  C5  Vinduer                (volum =  420 stk)
  C6  Dorer                  (volum =  350 stk)
  C7  Elektro (kabel etc.)   (volum =  12000 m)
  C8  Ror (VVS-komponenter)  (volum =   9000 m)

Leverandorer (S = 4):
  L1  Bygg & Beton AS       (betong/armering sterk)
  L2  Interior Leverandor   (gips/isolasjon/vinduer sterk)
  L3  Elektro Grossist AS   (elektro/ror sterk)
  L4  Totalleverandor Nord  (bredt sortiment, moderat pris)

Hver leverandor gir bud pa:
  * enkeltkategorier (single-item bids): pris per enhet og kapasitet
  * bundler (combinatorial bids): rabatterte pakker som gir lavere totalpris
    dersom hele bundlen tildeles samme leverandor
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Infografikk-farger (book-color-scheme)
C_S1_FILL = '#8CC8E5'   # primary lys
C_S1_DARK = '#1F6587'
C_S2_FILL = '#97D4B7'   # secondary lys
C_S2_DARK = '#307453'
C_S3_FILL = '#F6BA7C'
C_S3_DARK = '#9C540B'
C_S4_FILL = '#BD94D7'
C_S4_DARK = '#5A2C77'
C_S5_FILL = '#ED9F9E'
C_S5_DARK = '#961D1C'
C_TEXT = '#1F2933'
C_RULE = '#CBD5E1'


# ---------------------------------------------------------------------------
#  Kategorier: navn, enhet, etterspoert volum
# ---------------------------------------------------------------------------
CATEGORIES = [
    ('C1', 'Betong og moertel', 'm3',   1200),
    ('C2', 'Armeringsstaal',     'tonn',  180),
    ('C3', 'Isolasjon',          'm2',   4000),
    ('C4', 'Gips og plater',     'm2',   6500),
    ('C5', 'Vinduer',            'stk',   420),
    ('C6', 'Doerer',             'stk',   350),
    ('C7', 'Elektro (kabel)',    'm',   12000),
    ('C8', 'Roer (VVS)',         'm',    9000),
]

# ---------------------------------------------------------------------------
#  Leverandorer: navn og total kapasitet (som fraksjon av total innkjops-
#  volum; bruker volumandel siden enheter varierer). Kapasitets-begrensning
#  modelleres ogsaa som maksimal andel av total kontraktverdi.
# ---------------------------------------------------------------------------
SUPPLIERS = [
    ('L1', 'Bygg & Beton AS',    0.55),   # kan ta inntil 55% av total kontrakt
    ('L2', 'Interior Leverandor', 0.50),
    ('L3', 'Elektro Grossist AS', 0.50),
    ('L4', 'Totalleverandoer Nord', 0.65),
]


# Enhetspriser per leverandoer per kategori (NOK per enhet).
# None = leverandoeren byr ikke paa denne kategorien.
# Tall er realistiske norske priser anno 2025 (synthetisk).
UNIT_BIDS = {
    # cat: {supplier_id: unit_price}
    'C1': {'L1': 2150.0,  'L2': None,    'L3': None,    'L4': 2290.0},
    'C2': {'L1': 14_200,  'L2': None,    'L3': None,    'L4': 14_900},
    'C3': {'L1':   430,   'L2':   395,   'L3': None,    'L4':   415},
    'C4': {'L1':   285,   'L2':   255,   'L3': None,    'L4':   272},
    'C5': {'L1': None,    'L2':  6100,   'L3': None,    'L4':  6350},
    'C6': {'L1': None,    'L2':  4850,   'L3': None,    'L4':  4980},
    'C7': {'L1': None,    'L2': None,    'L3':    28.5, 'L4':    31.0},
    'C8': {'L1': None,    'L2': None,    'L3':    42.0, 'L4':    45.5},
}


# Bundle-bud: hver bundle er (bundle_id, leverandoer, {kategori: pris_per_enhet})
# Pris per enhet inne i bundlen er lavere enn det tilsvarende enkeltbudet
# (rabatt for samlet tildeling av hele bundlen). I MIP behandler vi bundlen
# som en 'alt-eller-ingenting'-binaer variabel som dekker hele volumet i
# hver kategori den omfatter.
BUNDLE_BIDS = [
    # L1: 'Raabygg-pakke' -- betong + armering
    ('B1', 'L1', {'C1': 2050.0, 'C2': 13_700}),

    # L2: 'Interior-pakke' -- isolasjon + gips + vinduer
    ('B2', 'L2', {'C3': 370, 'C4': 238, 'C5': 5850}),

    # L2: 'Vegg-pakke' -- kun isolasjon + gips
    ('B3', 'L2', {'C3': 378, 'C4': 246}),

    # L3: 'Tekniske fag' -- elektro + roer
    ('B4', 'L3', {'C7': 26.8, 'C8': 40.0}),

    # L4: 'Storekspanded-pakke' -- alle 8 kategorier, moderat rabatt
    ('B5', 'L4', {'C1': 2190, 'C2': 14_300, 'C3': 395, 'C4': 258,
                  'C5': 6080, 'C6': 4770, 'C7': 29.6, 'C8': 43.5}),

    # L4: 'Finish-pakke' -- gips + doer + elektro
    ('B6', 'L4', {'C4': 260, 'C6': 4820, 'C7': 30.2}),
]


def categories_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(CATEGORIES, columns=['kategori', 'navn', 'enhet', 'volum'])
    return df


def suppliers_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(SUPPLIERS,
                      columns=['leverandoer', 'navn', 'kap_andel_maks'])
    return df


def unit_bids_dataframe(df_cat: pd.DataFrame,
                        df_sup: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, c in df_cat.iterrows():
        for _, s in df_sup.iterrows():
            price = UNIT_BIDS[c['kategori']].get(s['leverandoer'])
            if price is None:
                continue
            linekost = price * c['volum']
            rows.append({
                'bud_id': f"E_{s['leverandoer']}_{c['kategori']}",
                'type': 'enkelt',
                'leverandoer': s['leverandoer'],
                'kategori': c['kategori'],
                'pris_per_enhet': float(price),
                'volum': int(c['volum']),
                'linekost_NOK': float(linekost),
            })
    return pd.DataFrame(rows)


def bundle_bids_dataframe(df_cat: pd.DataFrame) -> pd.DataFrame:
    volum_per_cat = {row['kategori']: row['volum'] for _, row in df_cat.iterrows()}
    rows = []
    for bundle_id, supplier, prices in BUNDLE_BIDS:
        cat_list = sorted(prices.keys())
        totalkost = sum(prices[c] * volum_per_cat[c] for c in cat_list)
        for c in cat_list:
            rows.append({
                'bud_id': bundle_id,
                'type': 'bundle',
                'leverandoer': supplier,
                'kategori': c,
                'pris_per_enhet': float(prices[c]),
                'volum': int(volum_per_cat[c]),
                'linekost_NOK': float(prices[c] * volum_per_cat[c]),
                'bundle_totalkost_NOK': float(totalkost),
                'bundle_kategorier': ','.join(cat_list),
            })
    return pd.DataFrame(rows)


def plot_bid_matrix(df_unit: pd.DataFrame, df_bundle: pd.DataFrame,
                    df_cat: pd.DataFrame, df_sup: pd.DataFrame,
                    output_path: Path) -> None:
    """Heatmap: linjekostnad per leverandoer x kategori (enkeltbud).
    Inkluderer ogsaa markoerer for bundle-kategorier."""
    fig, ax = plt.subplots(figsize=(11.5, 5.2))

    n_sup = len(df_sup)
    n_cat = len(df_cat)
    mat = np.full((n_sup, n_cat), np.nan)
    for _, r in df_unit.iterrows():
        i = df_sup.index[df_sup['leverandoer'] == r['leverandoer']][0]
        j = df_cat.index[df_cat['kategori'] == r['kategori']][0]
        mat[i, j] = r['linekost_NOK'] / 1e6  # MNOK

    cmap = plt.get_cmap('Blues')
    im = ax.imshow(mat, aspect='auto', cmap=cmap)

    # Annoter linjekostnad
    for i in range(n_sup):
        for j in range(n_cat):
            if np.isnan(mat[i, j]):
                ax.text(j, i, '-', ha='center', va='center',
                        fontsize=10, color=C_RULE)
            else:
                val = mat[i, j]
                txtcolor = 'white' if val > np.nanmax(mat) * 0.55 else C_TEXT
                ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                        fontsize=9.5, color=txtcolor)

    # Bundle-overlegg: marker celler som inngaar i en bundle med farget kant
    bundle_colors = {'B1': C_S1_DARK, 'B2': C_S2_DARK, 'B3': C_S2_DARK,
                     'B4': C_S3_DARK, 'B5': C_S4_DARK, 'B6': C_S4_DARK}
    seen_markers = set()
    for bundle_id in df_bundle['bud_id'].unique():
        rows = df_bundle[df_bundle['bud_id'] == bundle_id]
        supplier = rows['leverandoer'].iloc[0]
        i = df_sup.index[df_sup['leverandoer'] == supplier][0]
        for _, r in rows.iterrows():
            j = df_cat.index[df_cat['kategori'] == r['kategori']][0]
            color = bundle_colors.get(bundle_id, C_S5_DARK)
            rect = plt.Rectangle((j - 0.45, i - 0.45), 0.9, 0.9,
                                 fill=False, edgecolor=color,
                                 linewidth=2.3, linestyle='--')
            ax.add_patch(rect)

    ax.set_xticks(range(n_cat))
    ax.set_xticklabels([f"{c}\n{n}" for c, n in zip(df_cat['kategori'],
                                                     df_cat['navn'])],
                       fontsize=9.5)
    ax.set_yticks(range(n_sup))
    ax.set_yticklabels([f"{s}\n{n}" for s, n in zip(df_sup['leverandoer'],
                                                     df_sup['navn'])],
                       fontsize=10)
    ax.set_title('Budmatrise: enkeltbud (MNOK) + bundle-markering (stiplet)',
                 fontsize=12, fontweight='bold', color=C_TEXT)

    cbar = plt.colorbar(im, ax=ax, shrink=0.8)
    cbar.set_label('Linjekostnad (MNOK)', fontsize=10)
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

    df_cat = categories_dataframe()
    df_sup = suppliers_dataframe()
    df_unit = unit_bids_dataframe(df_cat, df_sup)
    df_bundle = bundle_bids_dataframe(df_cat)

    df_cat.to_csv(DATA_DIR / 'kategorier.csv', index=False)
    df_sup.to_csv(DATA_DIR / 'leverandorer.csv', index=False)
    df_unit.to_csv(DATA_DIR / 'enkeltbud.csv', index=False)
    df_bundle.to_csv(DATA_DIR / 'bundlebud.csv', index=False)

    print(f"Kategorier lagret:  {DATA_DIR / 'kategorier.csv'} ({len(df_cat)})")
    print(f"Leverandorer:       {DATA_DIR / 'leverandorer.csv'} ({len(df_sup)})")
    print(f"Enkeltbud:          {DATA_DIR / 'enkeltbud.csv'} ({len(df_unit)})")
    print(f"Bundle-bud (linjer): {DATA_DIR / 'bundlebud.csv'} "
          f"({len(df_bundle)} linjer / "
          f"{df_bundle['bud_id'].nunique()} bundler)")

    stats = {
        'antall_kategorier': int(len(df_cat)),
        'antall_leverandoerer': int(len(df_sup)),
        'antall_enkeltbud': int(len(df_unit)),
        'antall_bundler': int(df_bundle['bud_id'].nunique()),
        'antall_bundle_linjer': int(len(df_bundle)),
        'antall_kat_uten_alle_leverandoerer': int(
            sum(1 for c in df_cat['kategori']
                if sum(1 for v in UNIT_BIDS[c].values() if v is not None) < 4)
        ),
        'total_etterspurt_linjer': int(len(df_cat)),
    }
    with open(OUTPUT_DIR / 'step01_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {OUTPUT_DIR / 'step01_stats.json'}")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    plot_bid_matrix(df_unit, df_bundle, df_cat, df_sup,
                    OUTPUT_DIR / 'wdp_bid_matrix.png')


if __name__ == '__main__':
    main()
