"""
Steg 1: Datainnsamling for Green VRP
====================================
Genererer et syntetisk datasett for groenn ruteplanlegging i Oslo med
lavutslippssone: ett sentralt depot og 25 kunder. For hver kunde lagres
koordinater (km fra depot) og etterspoersel i kilogram gods.

Kjoeretoeyet er en tung varebil med:
    - Tomvekt (kerb)  w0 = 2500 kg
    - Lastkapasitet   Q  = 1800 kg
    - Total maks.     w_max = w0 + Q = 4300 kg
    - Drivstoff       diesel, CO2-utslipp ca. 2,68 kg per liter

Utslippsfunksjonen (per km) modelleres som lineaer i total vekt:
    e(w) = alpha + beta * w       [g CO2 per km]

der alpha er baseline utslipp fra tomvekt + rullemotstand og beta er den
marginale oekningen per ekstra kg last. Vi kalibrerer alpha og beta slik
at:
    e(w0)       ~ 900 g CO2/km   (tom bil)
    e(w0 + Q)   ~ 1260 g CO2/km  (full bil, +40 %)

Dette gir alpha ~ 375 g/km og beta ~ 0,21 g CO2/(kg * km), i samme stoerrelsesorden
som empiriske parametre i Bektas og Laporte (2011).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

RNG_SEED = 42

# Kjoeretoeysparametere
KERB_WEIGHT_KG = 2500.0        # w0: tomvekt (kg)
VEHICLE_CAPACITY_KG = 1800.0   # Q: maksimal lastevekt (kg)

# Utslippsparametere (kalibrert)
EMISSION_ALPHA_G = 375.0       # g CO2 per km, baseline (tom bil-komponenten)
EMISSION_BETA_G = 0.21         # g CO2 per (kg * km), marginal last-bidrag

# Depot ved origo (Oslo sentrum)
DEPOT_X, DEPOT_Y = 0.0, 0.0


def generate_customers(n: int, seed: int) -> pd.DataFrame:
    """Generer n kunder med koordinater og etterspoersel i kg.

    Tre clustre som likner paa Oslo-omraadet:
        - Sentrum (tett rundt depot, mange smaa ordrer)
        - Vest (spredt, middels ordrer)
        - Oest (spredt, store ordrer til butikker)
    """
    rng = np.random.default_rng(seed)

    cluster_centers = np.array([
        [0.5, 0.8],    # sentrum
        [-5.5, 1.5],   # vest
        [4.8, -2.0],   # oest/syd
    ])
    cluster_sigma = np.array([1.8, 2.6, 2.8])
    cluster_weights = [0.40, 0.32, 0.28]
    cluster_ids = rng.choice([0, 1, 2], size=n, p=cluster_weights)

    xs = np.zeros(n)
    ys = np.zeros(n)
    for i, cid in enumerate(cluster_ids):
        xs[i] = rng.normal(cluster_centers[cid, 0], cluster_sigma[cid])
        ys[i] = rng.normal(cluster_centers[cid, 1], cluster_sigma[cid])

    xs = np.round(xs, 2)
    ys = np.round(ys, 2)

    # Etterspoersel i kg: lognormal fordeling med tyngdepunkt rundt
    # 120-220 kg per kunde (dagligvarer/tunge matvarer).
    raw_demand = rng.lognormal(mean=np.log(160.0), sigma=0.55, size=n)
    demand_kg = np.clip(np.round(raw_demand, 0), 30.0, 500.0)

    df = pd.DataFrame({
        'customer_id': np.arange(1, n + 1),
        'x': xs,
        'y': ys,
        'demand_kg': demand_kg.astype(int),
    })
    return df


def build_distance_matrix(df: pd.DataFrame) -> np.ndarray:
    """Returner (n+1) x (n+1) euklidsk avstandsmatrise i km. Indeks 0 = depot."""
    n = len(df)
    coords = np.zeros((n + 1, 2))
    coords[0] = [DEPOT_X, DEPOT_Y]
    coords[1:, 0] = df['x'].to_numpy()
    coords[1:, 1] = df['y'].to_numpy()

    diff = coords[:, None, :] - coords[None, :, :]
    D = np.sqrt((diff ** 2).sum(axis=2))
    return np.round(D, 3)


def plot_instance(df: pd.DataFrame, output_path: Path) -> None:
    """Visualiser kunder og depot paa kart."""
    fig, ax = plt.subplots(figsize=(9, 7))

    # Kunder med areal proporsjonalt med etterspoersel
    sizes = 25 + 0.6 * df['demand_kg'].to_numpy()
    ax.scatter(
        df['x'], df['y'],
        s=sizes, c='#8CC8E5', edgecolor='#1F6587', linewidth=0.8,
        zorder=3, label='Kunde (areal $\\propto q_i$)',
    )
    for _, row in df.iterrows():
        ax.annotate(
            str(int(row['customer_id'])),
            xy=(row['x'], row['y']),
            xytext=(4, 4), textcoords='offset points',
            fontsize=7, color='#1F2933', zorder=4,
        )

    ax.scatter(
        DEPOT_X, DEPOT_Y,
        s=240, marker='s', c='#F6BA7C', edgecolor='#9C540B', linewidth=1.2,
        zorder=5, label='Depot',
    )

    ax.set_xlabel('$x$ (km fra depot)', fontsize=12)
    ax.set_ylabel('$y$ (km fra depot)', fontsize=12)
    ax.set_title(
        f'Green VRP-instans: depot + {len(df)} kunder, kapasitet $Q = {int(VEHICLE_CAPACITY_KG)}$ kg',
        fontsize=12, fontweight='bold',
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_aspect('equal', adjustable='datalim')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def plot_emission_function(output_path: Path) -> None:
    """Illustrer den lineaere utslippsfunksjonen e(w) over totalvekt."""
    w0 = KERB_WEIGHT_KG
    Q = VEHICLE_CAPACITY_KG
    w = np.linspace(w0, w0 + Q, 200)
    e = EMISSION_ALPHA_G + EMISSION_BETA_G * w

    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(w, e, color='#1F6587', linewidth=2.2, label='$e(w) = \\alpha + \\beta w$')
    ax.fill_between(w, e, color='#8CC8E5', alpha=0.35)

    ax.axvline(w0, color='#9C540B', linestyle='--', linewidth=1.2)
    ax.axvline(w0 + Q, color='#961D1C', linestyle='--', linewidth=1.2)
    ax.annotate('Tom ($w_0 = 2500$ kg)', xy=(w0, e[0]), xytext=(w0 + 50, e[0] - 30),
                fontsize=9, color='#9C540B')
    ax.annotate('Full last ($w_0 + Q = 4300$ kg)',
                xy=(w0 + Q, e[-1]), xytext=(w0 + 120, e[-1] - 30),
                fontsize=9, color='#961D1C')

    ax.set_xlabel('Totalvekt $w$ (kg)', fontsize=12)
    ax.set_ylabel('Utslipp $e(w)$ (g CO$_2$ per km)', fontsize=12)
    ax.set_title('Lasteavhengig utslippsfunksjon per km',
                 fontsize=12, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right', fontsize=11)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING (GREEN VRP)')
    print('=' * 60)

    n = 25
    df = generate_customers(n, RNG_SEED)
    D = build_distance_matrix(df)

    df.to_csv(DATA_DIR / 'customers.csv', index=False)
    np.savetxt(DATA_DIR / 'distance.csv', D, delimiter=',', fmt='%.3f')

    total_demand = int(df['demand_kg'].sum())
    min_vehicles = int(np.ceil(total_demand / VEHICLE_CAPACITY_KG))

    summary = {
        'n_customers': int(n),
        'total_demand_kg': total_demand,
        'mean_demand_kg': round(float(df['demand_kg'].mean()), 1),
        'max_demand_kg': int(df['demand_kg'].max()),
        'min_demand_kg': int(df['demand_kg'].min()),
        'vehicle_capacity_kg': VEHICLE_CAPACITY_KG,
        'kerb_weight_kg': KERB_WEIGHT_KG,
        'emission_alpha_g_per_km': EMISSION_ALPHA_G,
        'emission_beta_g_per_kgkm': EMISSION_BETA_G,
        'emission_empty_g_per_km': EMISSION_ALPHA_G + EMISSION_BETA_G * KERB_WEIGHT_KG,
        'emission_full_g_per_km': EMISSION_ALPHA_G + EMISSION_BETA_G * (KERB_WEIGHT_KG + VEHICLE_CAPACITY_KG),
        'lower_bound_vehicles': min_vehicles,
        'mean_distance_to_depot_km': round(float(D[0, 1:].mean()), 2),
        'max_distance_to_depot_km': round(float(D[0, 1:].max()), 2),
        'depot': {'x': DEPOT_X, 'y': DEPOT_Y},
    }

    print(f'N = {n} kunder')
    print(f'Sum etterspoersel: {total_demand} kg')
    print(f'Kapasitet per bil: {int(VEHICLE_CAPACITY_KG)} kg')
    print(f'Nedre grense antall biler: {min_vehicles}')
    print(f'Utslipp tom: {summary["emission_empty_g_per_km"]:.1f} g/km')
    print(f'Utslipp full: {summary["emission_full_g_per_km"]:.1f} g/km')
    print(f'Forhold full/tom: '
          f'{summary["emission_full_g_per_km"] / summary["emission_empty_g_per_km"]:.3f}')

    plot_instance(df, OUTPUT_DIR / 'gvrp_instance.png')
    plot_emission_function(OUTPUT_DIR / 'gvrp_load_emission_profile.png')

    with open(OUTPUT_DIR / 'step01_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f'\nOppsummering lagret: {OUTPUT_DIR / "step01_summary.json"}')


if __name__ == '__main__':
    main()
