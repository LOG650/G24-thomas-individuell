"""
Steg 1: Datainnsamling for CVRP
===============================
Genererer et syntetisk CVRP-datasett inspirert av urban
hjemleveringsruting fra et sentralt depot i Oslo.

To instanser:
    * N=15 kunder (liten, brukes til eksakt MIP-losning)
    * N=40 kunder (stor, brukes til heuristikker og 2-opt)

For hver kunde lagres:
    - x, y : koordinater (km fra depot-origo)
    - demand : etterspurt volum (kolli)

Kjoretoyene er identiske: kapasitet Q = 45 kolli per bil.

Alle data lagres som CSV i data/ slik at paafolgende steg kan laste dem.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

RNG_SEED = 7
VEHICLE_CAPACITY = 45

# Depot plassert sentralt (Oslo S omtrentlig origo). Kunder spredt i et
# realistisk byomrade pa omtrent 20x20 km.
DEPOT_X, DEPOT_Y = 0.0, 0.0


def generate_customers(n: int, seed: int) -> pd.DataFrame:
    """Generer n kunder med koordinater og etterspoersel.

    Koordinater er modellert som en blanding av tre clustre som
    representerer Oslo indre by (tett), vest og oest (spredte forsteder).
    Etterspoersel er heltalls antall kolli, trukket fra en diskret
    fordeling mellom 1 og 9 med tyngdepunkt rundt 3-5.
    """
    rng = np.random.default_rng(seed)

    # Fordel kunder paa tre clustre
    cluster_centers = np.array([
        [0.5, 1.0],    # indre by
        [-6.0, 2.0],   # vest
        [5.0, -2.0],   # oest
    ])
    cluster_sigma = np.array([2.2, 3.0, 3.2])

    cluster_ids = rng.choice([0, 1, 2], size=n, p=[0.45, 0.30, 0.25])

    xs = np.zeros(n)
    ys = np.zeros(n)
    for i, cid in enumerate(cluster_ids):
        xs[i] = rng.normal(cluster_centers[cid, 0], cluster_sigma[cid])
        ys[i] = rng.normal(cluster_centers[cid, 1], cluster_sigma[cid])

    xs = np.round(xs, 2)
    ys = np.round(ys, 2)

    demands = rng.choice(
        [1, 2, 3, 4, 5, 6, 7, 8, 9],
        size=n,
        p=[0.05, 0.10, 0.18, 0.22, 0.18, 0.12, 0.08, 0.05, 0.02],
    ).astype(int)

    df = pd.DataFrame({
        'customer_id': np.arange(1, n + 1),
        'x': xs,
        'y': ys,
        'demand': demands,
    })
    return df


def build_distance_matrix(df: pd.DataFrame) -> np.ndarray:
    """Returner (n+1) x (n+1) euklidsk avstandsmatrise, med indeks 0 = depot.

    Avstander rundes til 2 desimaler og representerer kilometer.
    """
    n = len(df)
    coords = np.zeros((n + 1, 2))
    coords[0] = [DEPOT_X, DEPOT_Y]
    coords[1:, 0] = df['x'].to_numpy()
    coords[1:, 1] = df['y'].to_numpy()

    diff = coords[:, None, :] - coords[None, :, :]
    D = np.sqrt((diff ** 2).sum(axis=2))
    return np.round(D, 2)


def plot_instance(df: pd.DataFrame, output_path: Path, n: int) -> None:
    """Visualiser kunder og depot pa et kart."""
    fig, ax = plt.subplots(figsize=(9, 7))

    # Kunder, skaler markorstorrelse med etterspoersel
    sizes = 25 + 10 * df['demand'].to_numpy()
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
        s=220, marker='s', c='#F6BA7C', edgecolor='#9C540B', linewidth=1.2,
        zorder=5, label='Depot',
    )

    ax.set_xlabel('$x$ (km fra depot)', fontsize=12)
    ax.set_ylabel('$y$ (km fra depot)', fontsize=12)
    ax.set_title(
        f'CVRP-instans: depot + {n} kunder (kapasitet $Q = {VEHICLE_CAPACITY}$)',
        fontsize=12, fontweight='bold',
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    ax.set_aspect('equal', adjustable='datalim')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING (CVRP)')
    print('=' * 60)

    summary: dict = {'vehicle_capacity': VEHICLE_CAPACITY,
                     'depot': {'x': DEPOT_X, 'y': DEPOT_Y}}

    for n, tag in [(15, 'small'), (40, 'large')]:
        seed = RNG_SEED + (0 if tag == 'small' else 1)
        df = generate_customers(n, seed)
        D = build_distance_matrix(df)

        df.to_csv(DATA_DIR / f'customers_{tag}.csv', index=False)
        np.savetxt(DATA_DIR / f'distance_{tag}.csv', D, delimiter=',', fmt='%.2f')

        total_demand = int(df['demand'].sum())
        min_vehicles = int(np.ceil(total_demand / VEHICLE_CAPACITY))

        summary[tag] = {
            'n_customers': int(n),
            'total_demand': total_demand,
            'mean_demand': round(float(df['demand'].mean()), 2),
            'max_demand': int(df['demand'].max()),
            'min_demand': int(df['demand'].min()),
            'lower_bound_vehicles': min_vehicles,
            'mean_distance_to_depot': round(float(D[0, 1:].mean()), 2),
            'max_distance_to_depot': round(float(D[0, 1:].max()), 2),
        }

        print(f"\n--- {tag.upper()} (N = {n}) ---")
        print(f"Totalt etterspoersel sum(q_i): {total_demand} kolli")
        print(f"Kapasitet per kjoretoy: {VEHICLE_CAPACITY} kolli")
        print(f"Nedre grense antall kjoretoy: {min_vehicles}")
        print(f"Gjennomsnittlig avstand kunde-depot: {summary[tag]['mean_distance_to_depot']} km")

        if tag == 'large':
            plot_instance(df, OUTPUT_DIR / 'vrp_instance.png', n)

    with open(OUTPUT_DIR / 'step01_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering lagret: {OUTPUT_DIR / 'step01_summary.json'}")


if __name__ == '__main__':
    main()
