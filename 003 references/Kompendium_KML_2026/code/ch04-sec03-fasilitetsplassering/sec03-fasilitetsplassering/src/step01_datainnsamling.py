"""
Steg 1: Datainnsamling
======================
Syntetiske lokasjonsdata for UFLP-eksempelet: 15 kandidater for
distribusjonssentre i Skandinavia (Norge + Sverige), samt 80
kundelokasjoner med etterspoersel. Koordinatene er (lat, lon) i WGS84,
valgt slik at de dekker et realistisk geografisk omraade med fokus
paa befolkningstette regioner (Oslo/Bergen, Stockholm/Goeteborg).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Infografikk-farger (book-color-scheme)
C_CANDIDATE = '#5A2C77'    # accent - DC-kandidater (loker)
C_CANDIDATE_FILL = '#BD94D7'
C_CUSTOMER = '#1F6587'     # primary - kunder
C_CUSTOMER_FILL = '#8CC8E5'
C_TEXT = '#1F2933'         # ink


# ---------------------------------------------------------------------------
#  Kandidater: 15 realistiske lokasjoner for DC i Skandinavia
# ---------------------------------------------------------------------------
CANDIDATES = [
    # navn,               lat,    lon,   fast aapningskostnad (NOK/aar)
    ('Oslo',              59.911, 10.757, 4_500_000),
    ('Drammen',           59.743, 10.205, 3_200_000),
    ('Kristiansand',      58.147,  7.996, 2_800_000),
    ('Stavanger',         58.970,  5.733, 3_300_000),
    ('Bergen',            60.391,  5.324, 3_600_000),
    ('Aalesund',          62.473,  6.150, 2_400_000),
    ('Trondheim',         63.430, 10.395, 3_400_000),
    ('Bodoe',             67.280, 14.405, 2_200_000),
    ('Tromsoe',           69.649, 18.956, 2_100_000),
    ('Goeteborg',         57.709, 11.974, 3_800_000),
    ('Stockholm',         59.329, 18.069, 4_800_000),
    ('Malmoe',            55.605, 13.003, 3_500_000),
    ('Oerebro',           59.275, 15.213, 2_700_000),
    ('Sundsvall',         62.390, 17.307, 2_500_000),
    ('Umeaa',             63.825, 20.263, 2_400_000),
]


# ---------------------------------------------------------------------------
#  Kunder: 80 syntetiske lokasjoner, samlet rundt 5 befolkningssentre
# ---------------------------------------------------------------------------
CLUSTERS = [
    # senter_navn,    lat,    lon,   vekt (hvor mange kunder trekkes her)
    ('Oslo-omr.',      59.92, 10.75, 0.24),
    ('Bergen-omr.',    60.39,  5.32, 0.12),
    ('Trondheim-omr.', 63.43, 10.40, 0.10),
    ('Tromsoe-omr.',   69.65, 18.96, 0.05),
    ('Stockholm-omr.', 59.33, 18.07, 0.22),
    ('Goeteborg-omr.', 57.71, 11.97, 0.14),
    ('Malmoe-omr.',    55.60, 13.00, 0.08),
    ('Umeaa-omr.',     63.82, 20.26, 0.05),
]


def generate_customers(n_customers: int = 80, seed: int = 202604) -> pd.DataFrame:
    """Trekker kundelokasjoner rundt befolkningssentre med normalfordelt stoey.

    Etterspoerselen er log-normalfordelt for aa faa et realistisk hale:
    noen faa store kunder og mange smaa.
    """
    rng = np.random.default_rng(seed)
    names, lats, lons, weights = zip(*CLUSTERS)
    weights = np.array(weights) / sum(weights)

    choices = rng.choice(len(CLUSTERS), size=n_customers, p=weights)
    lats = np.array(lats)[choices] + rng.normal(0.0, 0.35, size=n_customers)
    lons = np.array(lons)[choices] + rng.normal(0.0, 0.55, size=n_customers)

    # Log-normal etterspoersel i enheter/aar, avrundet til naermeste 10
    demand = np.round(rng.lognormal(mean=6.2, sigma=0.55, size=n_customers) / 10) * 10
    demand = np.clip(demand, 50, None).astype(int)

    customer_names = [f'K{i+1:02d}' for i in range(n_customers)]
    region = [names[choices[i]] for i in range(n_customers)]
    df = pd.DataFrame({
        'kunde': customer_names,
        'region': region,
        'lat': np.round(lats, 4),
        'lon': np.round(lons, 4),
        'etterspoersel': demand,
    })
    return df


def candidates_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(CANDIDATES, columns=['navn', 'lat', 'lon', 'fast_kostnad'])
    df.insert(0, 'id', [f'DC{i+1:02d}' for i in range(len(df))])
    return df


def plot_candidates_customers(df_dc: pd.DataFrame, df_cust: pd.DataFrame,
                              output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 9.0))

    # Kunder som små sirkler, skalert etter etterspoersel
    sizes = 8 + (df_cust['etterspoersel'] / df_cust['etterspoersel'].max()) * 110
    ax.scatter(df_cust['lon'], df_cust['lat'], s=sizes,
               c=C_CUSTOMER_FILL, edgecolor=C_CUSTOMER, linewidth=0.8,
               alpha=0.85, label=f'Kunder (n = {len(df_cust)})')

    # DC-kandidater som diamanter
    ax.scatter(df_dc['lon'], df_dc['lat'], s=180, marker='D',
               c=C_CANDIDATE_FILL, edgecolor=C_CANDIDATE, linewidth=1.5,
               label=f'DC-kandidater (n = {len(df_dc)})', zorder=3)

    for _, row in df_dc.iterrows():
        ax.annotate(row['navn'], (row['lon'], row['lat']),
                    xytext=(6, 6), textcoords='offset points',
                    fontsize=8, color=C_CANDIDATE, fontweight='bold')

    ax.set_xlabel('Lengdegrad (deg E)', fontsize=11)
    ax.set_ylabel('Breddegrad (deg N)', fontsize=11)
    ax.set_title('Skandinavisk distribusjonsnettverk: kandidater og kunder',
                 fontsize=12, fontweight='bold', color=C_TEXT)
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=9)
    ax.set_aspect(1.9)  # en enkel geografisk-korreksjon for Skandinavia
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

    df_dc = candidates_dataframe()
    df_cust = generate_customers()

    df_dc.to_csv(DATA_DIR / 'kandidater.csv', index=False)
    df_cust.to_csv(DATA_DIR / 'kunder.csv', index=False)
    print(f"Kandidater lagret: {DATA_DIR / 'kandidater.csv'} ({len(df_dc)} rader)")
    print(f"Kunder lagret:     {DATA_DIR / 'kunder.csv'} ({len(df_cust)} rader)")

    # Deskriptiv statistikk
    stats = {
        'antall_kandidater': int(len(df_dc)),
        'antall_kunder': int(len(df_cust)),
        'total_etterspoersel': int(df_cust['etterspoersel'].sum()),
        'maks_etterspoersel': int(df_cust['etterspoersel'].max()),
        'min_etterspoersel': int(df_cust['etterspoersel'].min()),
        'gj_etterspoersel': round(float(df_cust['etterspoersel'].mean()), 1),
        'median_etterspoersel': int(df_cust['etterspoersel'].median()),
        'sum_fast_kostnad_alle_aapne': int(df_dc['fast_kostnad'].sum()),
        'snitt_fast_kostnad': int(df_dc['fast_kostnad'].mean()),
    }
    with open(OUTPUT_DIR / 'step01_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {OUTPUT_DIR / 'step01_stats.json'}")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Figur
    plot_candidates_customers(df_dc, df_cust, OUTPUT_DIR / 'uflp_kandidater_kunder.png')


if __name__ == '__main__':
    main()
