"""
Steg 3: Utslippsmodellen
========================
Utleder og illustrerer den lasteavhengige utslippsmodellen som bindes
til rute-planlegging i de paafoelgende stegene.

For hver kant (i -> j) paa en rute R = (i_0 = 0, i_1, ..., i_m, i_{m+1} = 0)
er CO2-utslippet
    E_{ij}(w) = d_{ij} * (alpha + beta * w)    [g]
der w = kerb + current_load(i) er totalvekt paa kjoeretoeyet naar det
forlater node i. Etter levering hos i_k reduseres current_load med q_{i_k}.

Ruteutslippet er dermed
    E(R) = sum_{k=0..m} d_{i_k, i_{k+1}} * (alpha + beta * w_k)
         = alpha * L(R) + beta * sum_{k=0..m} d_{i_k, i_{k+1}} * w_k

der L(R) er rutens totale distanse. Fordi bilen blir lettere etter hver
leveranse, er kanten fra depot dyrest (tyngst last) og siste kant tilbake
til depot billigst (bare tomvekt).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step02_distanse_vrp import (
    DATA_DIR, OUTPUT_DIR, load_instance, route_emissions, route_distance,
)


def emission_profile(route, D, demands, alpha, beta, kerb):
    """Returner lister med (kum_dist_km, current_load_kg, e_per_km_g)
    langs ruten, for plotting.
    """
    total_load = sum(demands[c] for c in route if c != 0)
    current_load = total_load
    cum_km = 0.0

    profile = {
        'cum_km': [0.0],
        'load_kg': [current_load],
        'weight_kg': [kerb + current_load],
        'e_per_km_g': [alpha + beta * (kerb + current_load)],
        'edge_em_g': [0.0],
        'edge_dist_km': [0.0],
        'from_node': [route[0]],
        'to_node': [route[0]],
    }
    for a, b in zip(route[:-1], route[1:]):
        w = kerb + current_load
        e_per_km = alpha + beta * w
        d = D[a, b]
        edge_em = e_per_km * d

        cum_km += d
        profile['cum_km'].append(cum_km)
        profile['edge_dist_km'].append(d)
        profile['edge_em_g'].append(edge_em)
        if b != 0:
            current_load -= demands[b]
        profile['load_kg'].append(current_load)
        profile['weight_kg'].append(kerb + current_load)
        profile['e_per_km_g'].append(alpha + beta * (kerb + current_load))
        profile['from_node'].append(a)
        profile['to_node'].append(b)
    return profile


def plot_emission_vs_distance(distances_km, emissions_g, edge_loads_kg,
                               output_path: Path):
    """Scatter: per-kant utslippsintensitet vs last.

    Denne figuren illustrerer at en kant-med-full-last forurenser mer per
    km enn samme kant paa tilbakevei med tomt lastrom.
    """
    fig, ax = plt.subplots(figsize=(8.5, 5.0))
    em_per_km = np.array(emissions_g) / np.maximum(np.array(distances_km), 1e-6)
    sc = ax.scatter(edge_loads_kg, em_per_km,
                    c=edge_loads_kg, cmap='viridis',
                    edgecolor='#1F2933', linewidth=0.4, s=55, alpha=0.85)
    cb = plt.colorbar(sc, ax=ax)
    cb.set_label('Lastvekt $L$ (kg)', fontsize=11)
    ax.set_xlabel('Lastvekt paa kant (kg)', fontsize=12)
    ax.set_ylabel('Utslippsintensitet (g CO$_2$/km)', fontsize=12)
    ax.set_title('Lasteavhengig utslipp: hver kant paa alle ruter',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 3: UTSLIPPSMODELLEN (PROFIL PER KANT)')
    print('=' * 60)

    df, D, summary = load_instance()
    alpha = summary['emission_alpha_g_per_km']
    beta = summary['emission_beta_g_per_kgkm']
    kerb = summary['kerb_weight_kg']

    n = len(df)
    demands = np.zeros(n + 1, dtype=float)
    demands[1:] = df['demand_kg'].to_numpy(dtype=float)

    # Les distanse-basislinjen fra steg 2
    with open(OUTPUT_DIR / 'step02_results.json', 'r', encoding='utf-8') as f:
        step02 = json.load(f)
    routes = step02['routes']

    all_dists = []
    all_em = []
    all_loads = []
    profiles = []

    for r in routes:
        prof = emission_profile(r, D, demands, alpha, beta, kerb)
        profiles.append(prof)
        # Skip inngaaende 0-kant
        for k in range(1, len(prof['cum_km'])):
            all_dists.append(prof['edge_dist_km'][k])
            all_em.append(prof['edge_em_g'][k])
            # Kantens "last" er vekt foer leveringen paa node b, dvs.
            # load_kg ved k-1 (siden load_kg[k] er etter leveringen).
            all_loads.append(prof['load_kg'][k - 1])

    plot_emission_vs_distance(all_dists, all_em, all_loads,
                               OUTPUT_DIR / 'gvrp_load_emission_scatter.png')

    # Lagre enkel metrikk som JSON
    metrics = {
        'n_edges': len(all_dists),
        'mean_intensity_g_per_km': round(float(
            np.mean(np.array(all_em) / np.maximum(np.array(all_dists), 1e-6))), 2),
        'max_intensity_g_per_km': round(float(
            np.max(np.array(all_em) / np.maximum(np.array(all_dists), 1e-6))), 2),
        'min_intensity_g_per_km': round(float(
            np.min(np.array(all_em) / np.maximum(np.array(all_dists), 1e-6))), 2),
    }
    print(f'Antall kanter: {metrics["n_edges"]}')
    print(f'Gj.snitt intensitet: {metrics["mean_intensity_g_per_km"]} g CO2/km')
    print(f'Min intensitet:       {metrics["min_intensity_g_per_km"]} g CO2/km')
    print(f'Maks intensitet:     {metrics["max_intensity_g_per_km"]} g CO2/km')

    with open(OUTPUT_DIR / 'step03_metrics.json', 'w', encoding='utf-8') as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)
    print(f'\nMetrikker lagret: {OUTPUT_DIR / "step03_metrics.json"}')


if __name__ == '__main__':
    main()
