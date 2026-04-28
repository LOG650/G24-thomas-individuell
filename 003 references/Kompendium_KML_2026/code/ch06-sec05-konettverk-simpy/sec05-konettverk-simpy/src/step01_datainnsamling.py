"""
Steg 1: Datainnsamling for konettverk-simulering
================================================
Definerer et e-handels-oppfyllelsessenter med 4 stasjoner i serie:
  - mottak (M/M/1 mottakspult)
  - kvalitetskontroll (M/G/1 med lognormal servicetid)
  - pakking (M/M/c med c=2 parallelle pakkestasjoner)
  - utsending (M/U/1 med uniform servicetid -- lasting pa lastebil)

Ankomstprosess: Poisson med lambda = 40 ordrer/time.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def network_parameters() -> dict:
    """Returner parametere for basismodell-konettverket."""
    return {
        'arrival_rate': 40.0,  # ordrer per time (Poisson)
        'stations': {
            'mottak': {
                'order': 1,
                'servers': 1,
                'service_dist': 'exponential',
                'service_mean': 1.2,  # minutter
                'service_params': {'mean': 1.2},
            },
            'kvalitetskontroll': {
                'order': 2,
                'servers': 1,
                'service_dist': 'lognormal',
                'service_mean': 1.2,  # minutter
                # lognormal parametre valgt slik at
                # E[S] = exp(mu + sigma^2/2) = 1.2 og CV ~ 0.6
                'service_params': {'mu': 0.0306, 'sigma': 0.55},
            },
            'pakking': {
                'order': 3,
                'servers': 2,  # parallelle servere
                'service_dist': 'exponential',
                'service_mean': 2.8,  # minutter per server
                'service_params': {'mean': 2.8},
            },
            'utsending': {
                'order': 4,
                'servers': 1,
                'service_dist': 'uniform',
                'service_mean': 1.1,  # minutter = (a+b)/2
                'service_params': {'low': 0.8, 'high': 1.4},
            },
        },
    }


def compute_theoretical_utilization(params: dict) -> dict:
    """Beregn teoretisk utnyttelsesgrad rho = lambda * E[S] / c per stasjon."""
    lam = params['arrival_rate'] / 60.0  # konverter til ordrer/minutt
    util = {}
    for name, s in params['stations'].items():
        mean_service = s['service_mean']
        c = s['servers']
        util[name] = lam * mean_service / c
    return util


def plot_topology(params: dict, output_path: Path) -> None:
    """Visualiser konettverkets topologi."""
    fig, ax = plt.subplots(figsize=(11, 4))

    station_names = ['mottak', 'kvalitetskontroll', 'pakking', 'utsending']
    labels = ['Mottak\n(M/M/1)', 'Kvalitetskontroll\n(M/G/1)',
              'Pakking\n(M/M/2)', 'Utsending\n(M/U/1)']
    # Pastel-farger (s1..s5) fra bokens farge-tema
    fills = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7']
    strokes = ['#1F6587', '#307453', '#9C540B', '#5A2C77']

    x_positions = [1, 3, 5, 7]
    y = 0.5
    width = 1.3
    height = 0.9

    for x, label, fill, stroke in zip(x_positions, labels, fills, strokes):
        rect = plt.Rectangle((x - width / 2, y - height / 2), width, height,
                             facecolor=fill, edgecolor=stroke, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=10,
                color=stroke, fontweight='bold', zorder=3)

    # Piler mellom stasjoner
    for i in range(len(x_positions) - 1):
        ax.annotate('', xy=(x_positions[i + 1] - width / 2, y),
                    xytext=(x_positions[i] + width / 2, y),
                    arrowprops=dict(arrowstyle='->', color='#556270', lw=1.8), zorder=1)

    # Ankomstpil
    ax.annotate('', xy=(x_positions[0] - width / 2, y), xytext=(-0.1, y),
                arrowprops=dict(arrowstyle='->', color='#1F6587', lw=2))
    ax.text(-0.15, y + 0.55, r'$\lambda = 40$/time', ha='left', va='center',
            fontsize=11, color='#1F6587', fontweight='bold')

    # Utgangspil
    ax.annotate('', xy=(x_positions[-1] + width, y),
                xytext=(x_positions[-1] + width / 2, y),
                arrowprops=dict(arrowstyle='->', color='#307453', lw=2))
    ax.text(x_positions[-1] + width + 0.1, y + 0.55, 'Leverte ordrer',
            ha='left', va='center', fontsize=11, color='#307453', fontweight='bold')

    ax.set_xlim(-0.8, 9.5)
    ax.set_ylim(-0.3, 1.6)
    ax.axis('off')
    ax.set_title('Konettverk for e-handel: 4 stasjoner i serie', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_service_distributions(params: dict, output_path: Path) -> None:
    """Vis tettheter for de tre ulike servicefordelingene."""
    rng = np.random.default_rng(seed=42)
    n = 50000

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    # Eksponensiell (mottak)
    ax = axes[0]
    s = params['stations']['mottak']
    samples = rng.exponential(s['service_params']['mean'], n)
    ax.hist(samples, bins=60, density=True, color='#8CC8E5', edgecolor='#1F6587', alpha=0.85)
    ax.set_xlim(0, 6)
    ax.set_title(f"Mottak: Exp($\\mu={s['service_params']['mean']}$ min)", fontsize=11, fontweight='bold')
    ax.set_xlabel('Servicetid (min)')
    ax.set_ylabel('Tetthet')
    ax.grid(True, alpha=0.3)

    # Lognormal (kvalitetskontroll)
    ax = axes[1]
    s = params['stations']['kvalitetskontroll']
    samples = rng.lognormal(mean=s['service_params']['mu'], sigma=s['service_params']['sigma'], size=n)
    ax.hist(samples, bins=60, density=True, color='#97D4B7', edgecolor='#307453', alpha=0.85)
    ax.set_xlim(0, 5)
    ax.set_title(f"Kvalitetskontroll: Lognorm($\\mu={s['service_params']['mu']:.3f}$, $\\sigma={s['service_params']['sigma']:.2f}$)",
                 fontsize=11, fontweight='bold')
    ax.set_xlabel('Servicetid (min)')
    ax.grid(True, alpha=0.3)

    # Uniform (utsending)
    ax = axes[2]
    s = params['stations']['utsending']
    samples = rng.uniform(s['service_params']['low'], s['service_params']['high'], n)
    ax.hist(samples, bins=60, density=True, color='#BD94D7', edgecolor='#5A2C77', alpha=0.85)
    ax.set_xlim(0, 2.0)
    ax.set_title(f"Utsending: Unif({s['service_params']['low']}, {s['service_params']['high']})",
                 fontsize=11, fontweight='bold')
    ax.set_xlabel('Servicetid (min)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    params = network_parameters()
    util = compute_theoretical_utilization(params)

    print(f"\nAnkomstrate (lambda): {params['arrival_rate']:.1f} ordrer/time "
          f"= {params['arrival_rate'] / 60:.4f} ordrer/min")
    print("\nStasjoner:")
    for name, s in params['stations'].items():
        print(f"  {name:20s} | c={s['servers']} | dist={s['service_dist']:12s} "
              f"| E[S]={s['service_mean']:.2f} min | rho={util[name]:.3f}")

    # Lagre parametere som JSON
    results = {
        'arrival_rate_per_hour': params['arrival_rate'],
        'arrival_rate_per_min': params['arrival_rate'] / 60.0,
        'stations': {
            name: {
                'servers': s['servers'],
                'service_dist': s['service_dist'],
                'service_mean_min': s['service_mean'],
                'service_params': s['service_params'],
                'utilization_theoretical': round(util[name], 4),
            }
            for name, s in params['stations'].items()
        },
    }
    with open(OUTPUT_DIR / 'step01_network_params.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nParametere lagret: {OUTPUT_DIR / 'step01_network_params.json'}")

    # Generer figurer
    plot_topology(params, OUTPUT_DIR / 'qnet_topology.png')
    plot_service_distributions(params, OUTPUT_DIR / 'qnet_service_dists.png')


if __name__ == '__main__':
    main()
