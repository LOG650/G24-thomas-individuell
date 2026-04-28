"""
Steg 2: Avstandsmatriser og transportkostnader
==============================================
Bygger to avstandsmatriser:
  * D1[i, j]: avstand kunde j -> innsamlingssenter i
  * D2[i, k]: avstand innsamlingssenter i -> gjenvinningsanlegg k

Vi bruker storsirkel-avstand (Haversine) mellom lat/lon-punkter.
Transportkostnadene er linear i avstand, men med ulike satser for de to
leddene: kunde -> innsamling er typisk mindre, fragmentert transport (liten
bil), mens innsamling -> gjenvinning er konsolidert bulktransport (lastebil),
med lavere enhetskostnad per tonn-km.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Transport: NOK per tonn per km.
# Ledd 1 (kunde -> innsamling): fragmentert, liten lastebil, hoeyere sats.
# Ledd 2 (innsamling -> gjenvinning): konsolidert, bulk, lavere sats.
TRANSPORT_COST_L1_PER_TKM = 3.80   # NOK/tonn/km
TRANSPORT_COST_L2_PER_TKM = 2.20   # NOK/tonn/km

R_EARTH_KM = 6371.0


def haversine_matrix(lat1: np.ndarray, lon1: np.ndarray,
                     lat2: np.ndarray, lon2: np.ndarray) -> np.ndarray:
    """Vektorisert haversine-avstand mellom to sett av lat/lon-punkter.

    Returnerer (len(lat1), len(lat2))-matrise i km.
    """
    phi1 = np.deg2rad(lat1)[:, None]
    phi2 = np.deg2rad(lat2)[None, :]
    dphi = phi2 - phi1
    dlam = np.deg2rad(lon2)[None, :] - np.deg2rad(lon1)[:, None]
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlam / 2) ** 2
    d = 2 * R_EARTH_KM * np.arcsin(np.sqrt(a))
    return d


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: AVSTANDSMATRISER OG TRANSPORTKOSTNADER")
    print("=" * 60)

    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')
    df_is = pd.read_csv(DATA_DIR / 'innsamling.csv')
    df_gv = pd.read_csv(DATA_DIR / 'gjenvinning.csv')

    # Ledd 1: kunde -> innsamling
    D1 = haversine_matrix(df_is['lat'].to_numpy(), df_is['lon'].to_numpy(),
                          df_cust['lat'].to_numpy(), df_cust['lon'].to_numpy())

    # Ledd 2: innsamling -> gjenvinning
    D2 = haversine_matrix(df_is['lat'].to_numpy(), df_is['lon'].to_numpy(),
                          df_gv['lat'].to_numpy(), df_gv['lon'].to_numpy())

    # Transportkostnader per tonn (multipliseres med tonn i modellen)
    C1 = D1 * TRANSPORT_COST_L1_PER_TKM
    C2 = D2 * TRANSPORT_COST_L2_PER_TKM

    pd.DataFrame(D1, index=df_is['id'], columns=df_cust['kunde']).to_csv(
        OUTPUT_DIR / 'step02_dist_l1_km.csv')
    pd.DataFrame(D2, index=df_is['id'], columns=df_gv['id']).to_csv(
        OUTPUT_DIR / 'step02_dist_l2_km.csv')
    pd.DataFrame(C1, index=df_is['id'], columns=df_cust['kunde']).to_csv(
        OUTPUT_DIR / 'step02_cost_l1_per_tonn.csv')
    pd.DataFrame(C2, index=df_is['id'], columns=df_gv['id']).to_csv(
        OUTPUT_DIR / 'step02_cost_l2_per_tonn.csv')
    print(f"Matriser lagret i {OUTPUT_DIR}")

    stats = {
        'l1_transport_sats_NOK_per_tkm': TRANSPORT_COST_L1_PER_TKM,
        'l2_transport_sats_NOK_per_tkm': TRANSPORT_COST_L2_PER_TKM,
        'l1_maks_km': round(float(D1.max()), 1),
        'l1_min_km': round(float(D1.min()), 1),
        'l1_median_km': round(float(np.median(D1)), 1),
        'l1_gj_km': round(float(D1.mean()), 1),
        'l1_naermest_IS_per_kunde_km_snitt': round(float(D1.min(axis=0).mean()), 1),
        'l2_maks_km': round(float(D2.max()), 1),
        'l2_min_km': round(float(D2.min()), 1),
        'l2_median_km': round(float(np.median(D2)), 1),
        'l2_gj_km': round(float(D2.mean()), 1),
        'l2_naermest_GV_per_IS_km_snitt': round(float(D2.min(axis=1).mean()), 1),
        'dim_D1': list(D1.shape),
        'dim_D2': list(D2.shape),
    }
    with open(OUTPUT_DIR / 'step02_stats.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {OUTPUT_DIR / 'step02_stats.json'}")
    for k, v in stats.items():
        print(f"  {k}: {v}")


if __name__ == '__main__':
    main()
