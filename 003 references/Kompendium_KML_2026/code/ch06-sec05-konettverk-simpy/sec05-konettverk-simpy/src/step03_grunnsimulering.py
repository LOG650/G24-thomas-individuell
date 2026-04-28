"""
Steg 3: Grunnsimulering
=======================
Kjor baseline-simulering med 5000 ordrer og lagre metrikker + figurer:
  - utnyttelsesgrad per stasjon (qnet_utilization.png)
  - ventetidsfordeling per stasjon (qnet_waiting_dist.png)
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step02_grunnmodell import run_simulation

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Farger (s1..s4 fra fargetemaet)
FILLS = {
    'mottak': '#8CC8E5',
    'kvalitetskontroll': '#97D4B7',
    'pakking': '#F6BA7C',
    'utsending': '#BD94D7',
}
STROKES = {
    'mottak': '#1F6587',
    'kvalitetskontroll': '#307453',
    'pakking': '#9C540B',
    'utsending': '#5A2C77',
}


def plot_utilization(station_stats: dict, output_path: Path) -> None:
    """Stolpediagram over utnyttelsesgrad per stasjon."""
    names = list(station_stats.keys())
    rhos = [station_stats[n]['utilization'] for n in names]
    labels = ['Mottak', 'Kvalitetskontroll', 'Pakking', 'Utsending']

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(labels, rhos, color=[FILLS[n] for n in names],
                  edgecolor=[STROKES[n] for n in names], linewidth=1.8)
    for bar, rho in zip(bars, rhos):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015,
                f'{rho:.3f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.axhline(1.0, color='#961D1C', linestyle='--', linewidth=1.5, alpha=0.7, label=r'$\rho = 1$')
    ax.axhline(0.85, color='#9C540B', linestyle=':', linewidth=1.2, alpha=0.6, label=r'$\rho = 0{,}85$ (varselgrense)')
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(r'Utnyttelsesgrad $\rho$', fontsize=12)
    ax.set_title('Utnyttelsesgrad per stasjon (basismodell, 5000 ordrer)', fontsize=12, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_waiting_distribution(station_stats: dict, output_path: Path) -> None:
    """Histogram over ventetidsfordeling per stasjon (2x2 rutenett)."""
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    labels = {'mottak': 'Mottak', 'kvalitetskontroll': 'Kvalitetskontroll',
              'pakking': 'Pakking', 'utsending': 'Utsending'}
    names = ['mottak', 'kvalitetskontroll', 'pakking', 'utsending']

    for ax, name in zip(axes.flat, names):
        waits = np.array(station_stats[name]['wait_times'])
        mw = station_stats[name]['mean_wait']
        p95 = station_stats[name]['p95_wait']

        # Klipp av ekstreme haler for visualisering
        upper = np.percentile(waits, 99) if len(waits) > 0 else 1.0
        upper = max(upper, 0.5)
        bins = np.linspace(0, upper, 40)

        ax.hist(waits, bins=bins, color=FILLS[name], edgecolor=STROKES[name],
                linewidth=1.2, alpha=0.85)
        ax.axvline(mw, color='#961D1C', linestyle='--', linewidth=1.5,
                   label=f'E[W]={mw:.2f} min')
        ax.axvline(p95, color='#1F6587', linestyle=':', linewidth=1.5,
                   label=f'P95={p95:.2f} min')
        ax.set_title(labels[name], fontsize=11, fontweight='bold', color=STROKES[name])
        ax.set_xlabel('Ventetid (min)')
        ax.set_ylabel('Antall ordrer')
        ax.legend(fontsize=9)
        ax.grid(True, alpha=0.3)

    fig.suptitle('Ventetidsfordeling per stasjon (basismodell, 5000 ordrer)',
                 fontsize=13, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 3: GRUNNSIMULERING")
    print("=" * 60)
    print("Kjorer 5000 ordrer gjennom basismodellen ...")

    results = run_simulation(n_orders=5000, seed=2025)

    print(f"\nSim-sluttid: {results['sim_end_min']:.1f} min = {results['sim_end_min']/60:.1f} time")
    print(f"Antall leverte ordrer: {results['n_orders_completed']}")
    print(f"Gjennomstromning: {results['throughput_per_hour']:.2f} ordrer/time")
    print(f"Gjennomsnittlig gjennomlopstid: {results['mean_sojourn']:.2f} min")
    print(f"95-prosentil gjennomlopstid:    {results['p95_sojourn']:.2f} min")
    print("\nPer stasjon:")
    print(f"  {'Stasjon':20s} {'n':>6s} {'rho':>8s} {'E[W]':>8s} {'P95[W]':>9s} {'E[S]':>8s} {'E[V]':>8s}")
    for name, s in results['stations'].items():
        print(f"  {name:20s} {s['n']:>6d} {s['utilization']:>8.3f} "
              f"{s['mean_wait']:>8.2f} {s['p95_wait']:>9.2f} "
              f"{s['mean_service']:>8.2f} {s['mean_sojourn']:>8.2f}")

    # Lagre resultater (uten de store listene for JSON-kompakthet, men behold for figurer)
    summary = {
        'sim_end_min': results['sim_end_min'],
        'n_orders_completed': results['n_orders_completed'],
        'throughput_per_hour': results['throughput_per_hour'],
        'mean_sojourn': results['mean_sojourn'],
        'p95_sojourn': results['p95_sojourn'],
        'stations': {
            name: {k: v for k, v in s.items() if k not in ('wait_times', 'sojourn_times')}
            for name, s in results['stations'].items()
        },
    }
    with open(OUTPUT_DIR / 'step03_baseline.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    # Full dump (inkl. lister for senere analyse)
    np.savez_compressed(
        OUTPUT_DIR / 'step03_baseline_raw.npz',
        order_sojourn=np.array(results['order_sojourn']),
        **{f'wait_{k}': np.array(v['wait_times']) for k, v in results['stations'].items()},
    )
    print(f"Sammendrag lagret: {OUTPUT_DIR / 'step03_baseline.json'}")

    # Plott
    plot_utilization(results['stations'], OUTPUT_DIR / 'qnet_utilization.png')
    plot_waiting_distribution(results['stations'], OUTPUT_DIR / 'qnet_waiting_dist.png')


if __name__ == '__main__':
    main()
