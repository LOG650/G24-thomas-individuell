"""
Steg 1: Datainnsamling
======================
Syntetiske lokasjonsdata for et reverst distribusjonsnettverk for retur av
EE-avfall (WEEE -- Waste Electrical and Electronic Equipment) i Norge.

Nettverket har tre nivaaer:
  * Kundegruppene (40 lokasjoner) som genererer returvolum
  * Innsamlingssentre (8 kandidatlokasjoner) der retur samles og
    forbehandles (demontering, sortering, pressing)
  * Gjenvinningsanlegg (3 kandidatlokasjoner) der materialene prosesseres
    for materialgjenvinning, energigjenvinning eller trygg deponering

Koordinatene er (lat, lon) i WGS84, valgt slik at de dekker et realistisk
nasjonalt omraade fokusert paa befolkningstette regioner i Soer-, Vest- og
Midt-Norge, samt en representativ lokasjon i Nord-Norge.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Infografikk-farger (book-color-scheme)
C_CUSTOMER = '#1F6587'      # primary - kunder
C_CUSTOMER_FILL = '#8CC8E5'
C_COLLECT = '#307453'       # secondary - innsamling
C_COLLECT_FILL = '#97D4B7'
C_RECYCLE = '#5A2C77'       # accent - gjenvinning
C_RECYCLE_FILL = '#BD94D7'
C_TEXT = '#1F2933'


# ---------------------------------------------------------------------------
#  Nivaa 2: 8 kandidatlokasjoner for innsamlingssentre
# ---------------------------------------------------------------------------
COLLECTION_CANDIDATES = [
    # navn,               lat,    lon,   fast driftskostnad (NOK/aar),
    #                                    kapasitet (tonn/aar)
    ('Oslo',              59.911, 10.757, 3_200_000, 2_800),
    ('Drammen',           59.743, 10.205, 2_400_000, 2_000),
    ('Kristiansand',      58.147,  7.996, 2_100_000, 1_800),
    ('Stavanger',         58.970,  5.733, 2_500_000, 2_200),
    ('Bergen',            60.391,  5.324, 2_700_000, 2_400),
    ('Trondheim',         63.430, 10.395, 2_500_000, 2_100),
    ('Boedoe',            67.280, 14.405, 1_700_000, 1_200),
    ('Hamar',             60.795, 11.068, 1_900_000, 1_600),
]


# ---------------------------------------------------------------------------
#  Nivaa 3: 3 kandidatlokasjoner for gjenvinningsanlegg
# ---------------------------------------------------------------------------
RECYCLING_CANDIDATES = [
    # navn,       lat,    lon,   fast driftskostnad (NOK/aar),
    #                             kapasitet (tonn/aar),
    #                             prosesseringskostnad per tonn (NOK/tonn)
    ('Grenland',  59.141,  9.650, 8_500_000, 7_500, 2_400),
    ('Mo i Rana', 66.314, 14.139, 6_900_000, 5_500, 2_800),
    ('Aalesund',  62.473,  6.150, 7_500_000, 6_500, 2_600),
]


# ---------------------------------------------------------------------------
#  Nivaa 1: Kundegrupper (befolkningssentre) for trekking av returvolum
# ---------------------------------------------------------------------------
CLUSTERS = [
    # senter_navn,    lat,    lon,   vekt (hvor mange kunder trekkes her)
    ('Oslo-omr.',      59.92, 10.75, 0.28),
    ('Bergen-omr.',    60.39,  5.32, 0.15),
    ('Trondheim-omr.', 63.43, 10.40, 0.12),
    ('Stavanger-omr.', 58.97,  5.73, 0.10),
    ('Kristiansand',   58.15,  7.99, 0.08),
    ('Innlandet',      60.80, 11.10, 0.10),
    ('Nord-Norge',     67.50, 15.50, 0.07),
    ('Vestfold-Tel.',  59.20,  9.80, 0.10),
]


def generate_customers(n_customers: int = 40, seed: int = 202609) -> pd.DataFrame:
    """Trekker kundegrupper (f.eks. kommuner/regioner) rundt befolkningssentre.

    Returvolumet er log-normalfordelt for aa faa en realistisk hale med
    mange smaa og faa store kunder. Verdiene er i tonn EE-avfall per aar;
    norske kommuner samler inn om lag 5-10 kg EE-avfall per innbygger per aar.
    """
    rng = np.random.default_rng(seed)
    names, lats, lons, weights = zip(*CLUSTERS)
    weights = np.array(weights) / sum(weights)

    choices = rng.choice(len(CLUSTERS), size=n_customers, p=weights)
    lats_arr = np.array(lats)[choices] + rng.normal(0.0, 0.30, size=n_customers)
    lons_arr = np.array(lons)[choices] + rng.normal(0.0, 0.50, size=n_customers)

    # Log-normal returvolum (tonn/aar); tyngdepunkt rundt 200-400 tonn/aar
    volum = np.round(rng.lognormal(mean=5.4, sigma=0.55, size=n_customers))
    volum = np.clip(volum, 30, None).astype(int)

    customer_names = [f'K{i+1:02d}' for i in range(n_customers)]
    region = [names[choices[i]] for i in range(n_customers)]
    df = pd.DataFrame({
        'kunde': customer_names,
        'region': region,
        'lat': np.round(lats_arr, 4),
        'lon': np.round(lons_arr, 4),
        'returvolum_tonn': volum,
    })
    return df


def collection_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(COLLECTION_CANDIDATES,
                      columns=['navn', 'lat', 'lon',
                               'fast_kostnad', 'kapasitet_tonn'])
    df.insert(0, 'id', [f'IS{i+1:02d}' for i in range(len(df))])
    return df


def recycling_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(RECYCLING_CANDIDATES,
                      columns=['navn', 'lat', 'lon',
                               'fast_kostnad', 'kapasitet_tonn',
                               'prosess_kost_per_tonn'])
    df.insert(0, 'id', [f'GV{i+1:02d}' for i in range(len(df))])
    return df


def plot_network_base(df_cust: pd.DataFrame, df_is: pd.DataFrame,
                      df_gv: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 9.0))

    # Kunder
    sizes = 10 + (df_cust['returvolum_tonn'] / df_cust['returvolum_tonn'].max()) * 130
    ax.scatter(df_cust['lon'], df_cust['lat'], s=sizes,
               c=C_CUSTOMER_FILL, edgecolor=C_CUSTOMER, linewidth=0.8,
               alpha=0.85, label=f'Kunder (n = {len(df_cust)})', zorder=2)

    # Innsamlingssentre
    ax.scatter(df_is['lon'], df_is['lat'], s=180, marker='s',
               c=C_COLLECT_FILL, edgecolor=C_COLLECT, linewidth=1.5,
               label=f'Innsamlingssentre (n = {len(df_is)})', zorder=3)
    for _, row in df_is.iterrows():
        ax.annotate(row['navn'], (row['lon'], row['lat']),
                    xytext=(6, 6), textcoords='offset points',
                    fontsize=8, color=C_COLLECT, fontweight='bold')

    # Gjenvinningsanlegg
    ax.scatter(df_gv['lon'], df_gv['lat'], s=280, marker='^',
               c=C_RECYCLE_FILL, edgecolor=C_RECYCLE, linewidth=1.8,
               label=f'Gjenvinningsanlegg (n = {len(df_gv)})', zorder=4)
    for _, row in df_gv.iterrows():
        ax.annotate(row['navn'], (row['lon'], row['lat']),
                    xytext=(8, -14), textcoords='offset points',
                    fontsize=9, color=C_RECYCLE, fontweight='bold')

    ax.set_xlabel('Lengdegrad (deg E)', fontsize=11)
    ax.set_ylabel('Breddegrad (deg N)', fontsize=11)
    ax.set_title('Reverst nettverk: kunder, innsamlingssentre og gjenvinningsanlegg',
                 fontsize=12, fontweight='bold', color=C_TEXT)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=9)
    ax.set_aspect(1.9)
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

    df_cust = generate_customers()
    df_is = collection_dataframe()
    df_gv = recycling_dataframe()

    df_cust.to_csv(DATA_DIR / 'kunder.csv', index=False)
    df_is.to_csv(DATA_DIR / 'innsamling.csv', index=False)
    df_gv.to_csv(DATA_DIR / 'gjenvinning.csv', index=False)
    print(f"Kunder lagret:          {DATA_DIR / 'kunder.csv'} ({len(df_cust)} rader)")
    print(f"Innsamlingssentre:      {DATA_DIR / 'innsamling.csv'} ({len(df_is)} rader)")
    print(f"Gjenvinningsanlegg:     {DATA_DIR / 'gjenvinning.csv'} ({len(df_gv)} rader)")

    stats = {
        'antall_kunder': int(len(df_cust)),
        'antall_innsamlingskandidater': int(len(df_is)),
        'antall_gjenvinningskandidater': int(len(df_gv)),
        'total_returvolum_tonn': int(df_cust['returvolum_tonn'].sum()),
        'maks_returvolum_tonn': int(df_cust['returvolum_tonn'].max()),
        'min_returvolum_tonn': int(df_cust['returvolum_tonn'].min()),
        'gj_returvolum_tonn': round(float(df_cust['returvolum_tonn'].mean()), 1),
        'median_returvolum_tonn': int(df_cust['returvolum_tonn'].median()),
        'kapasitet_innsamling_total_tonn': int(df_is['kapasitet_tonn'].sum()),
        'kapasitet_gjenvinning_total_tonn': int(df_gv['kapasitet_tonn'].sum()),
        'sum_fast_is_alle_aapne': int(df_is['fast_kostnad'].sum()),
        'sum_fast_gv_alle_aapne': int(df_gv['fast_kostnad'].sum()),
    }
    with open(OUTPUT_DIR / 'step01_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {OUTPUT_DIR / 'step01_stats.json'}")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    plot_network_base(df_cust, df_is, df_gv, OUTPUT_DIR / 'revnet_network_base.png')


if __name__ == '__main__':
    main()
