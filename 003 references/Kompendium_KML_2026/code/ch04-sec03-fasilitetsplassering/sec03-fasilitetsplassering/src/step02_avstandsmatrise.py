"""
Steg 2: Avstandsmatrise og transportkostnad
===========================================
Beregner storsirkel-avstand (Haversine) mellom hver DC-kandidat og hver kunde,
og bygger en transportkostnadsmatrise c_{ij} i NOK per enhet som gaar fra
kandidat i til kunde j (enhetsavstandskostnad ganget med enhetsetterspoersel
haandteres i selve MIP-en i steg 3-4).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Transport: NOK per enhet per km (inkluderer drivstoff, sjaafoer, pakking, ...)
# Verdien er kalibrert slik at UFLP-modellen aapner 3-6 DC-er i baseline; et
# realistisk norsk transportkostnadsnivaa for mindre pakker/paller paa lang
# distanse er i storrelsesorden 1-3 NOK per kolli per km.
TRANSPORT_COST_PER_KM = 1.20  # NOK/enhet/km

# Jordens radius i km
R_EARTH_KM = 6371.0


def haversine_matrix(lat1: np.ndarray, lon1: np.ndarray,
                     lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Vektorisert haversine-avstand mellom to sett av lat/lon-punkter.

    Parametre
    ---------
    lat1, lon1 : array (n,)  -- for eksempel DC-kandidater
    lat2, lon2 : array (m,)  -- for eksempel kunder

    Returnerer matrise (n, m) med avstand i km.
    """
    phi1 = np.deg2rad(lat1)[:, None]
    phi2 = np.deg2rad(lat2)[None, :]
    dphi = phi2 - phi1
    dlam = np.deg2rad(lon2)[None, :] - np.deg2rad(lon1)[:, None]
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    d = 2 * R_EARTH_KM * np.arcsin(np.sqrt(a))
    return d


def plot_distance_histogram(dist_km: np.ndarray, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.hist(dist_km.flatten(), bins=30, color='#8CC8E5', edgecolor='#1F6587',
            linewidth=0.9)
    ax.axvline(np.median(dist_km), color='#5A2C77', linestyle='--',
               linewidth=1.4,
               label=f'Median = {np.median(dist_km):.0f} km')
    ax.axvline(np.mean(dist_km), color='#9C540B', linestyle=':',
               linewidth=1.4,
               label=f'Gjennomsnitt = {np.mean(dist_km):.0f} km')
    ax.set_xlabel('Avstand DC til kunde (km)', fontsize=11)
    ax.set_ylabel('Antall par', fontsize=11)
    ax.set_title('Fordeling av storsirkel-avstander (Haversine)',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: AVSTANDSMATRISE OG TRANSPORTKOSTNAD")
    print("=" * 60)

    df_dc = pd.read_csv(DATA_DIR / 'kandidater.csv')
    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')

    dist_km = haversine_matrix(df_dc['lat'].to_numpy(), df_dc['lon'].to_numpy(),
                               df_cust['lat'].to_numpy(), df_cust['lon'].to_numpy())

    # Transport per enhet = avstand * sats per km
    cost_per_unit = dist_km * TRANSPORT_COST_PER_KM  # NOK per enhet fra i til j
    # Transportkostnad i kroner om all etterspoersel til kunde j dekkes av i
    demand = df_cust['etterspoersel'].to_numpy()
    cost_total = cost_per_unit * demand[None, :]

    # Lagre matrisene
    pd.DataFrame(dist_km, index=df_dc['id'], columns=df_cust['kunde']).to_csv(
        OUTPUT_DIR / 'step02_dist_km.csv')
    pd.DataFrame(cost_per_unit, index=df_dc['id'], columns=df_cust['kunde']).to_csv(
        OUTPUT_DIR / 'step02_cost_per_unit.csv')
    pd.DataFrame(cost_total, index=df_dc['id'], columns=df_cust['kunde']).to_csv(
        OUTPUT_DIR / 'step02_cost_full.csv')
    print(f"Matriser lagret i {OUTPUT_DIR}")

    # Oppsummering
    stats = {
        'transport_sats_per_km': TRANSPORT_COST_PER_KM,
        'maks_avstand_km': round(float(dist_km.max()), 1),
        'min_avstand_km': round(float(dist_km.min()), 1),
        'median_avstand_km': round(float(np.median(dist_km)), 1),
        'gj_avstand_km': round(float(dist_km.mean()), 1),
        'naermest_DC_per_kunde_km_snitt': round(float(dist_km.min(axis=0).mean()), 1),
        'dimensjoner_matrise': list(dist_km.shape),
    }
    with open(OUTPUT_DIR / 'step02_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {OUTPUT_DIR / 'step02_stats.json'}")
    for k, v in stats.items():
        print(f"  {k}: {v}")

    # Figur: avstandsfordeling
    plot_distance_histogram(dist_km, OUTPUT_DIR / 'uflp_distance_hist.png')


if __name__ == '__main__':
    main()
