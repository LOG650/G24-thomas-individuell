"""
Steg 4: Flaskehalsanalyse
==========================
Identifiser flaskehalsen i basismodellen ved hjelp av
  - hoyest utnyttelsesgrad rho (analytisk indikator)
  - lengst ventetid E[W] (simuleringsobservasjon)
  - storst bidrag til total gjennomlopstid E[V] (sojourn)
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step02_grunnmodell import run_simulation

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

STROKES = {
    'mottak': '#1F6587',
    'kvalitetskontroll': '#307453',
    'pakking': '#9C540B',
    'utsending': '#5A2C77',
}
FILLS = {
    'mottak': '#8CC8E5',
    'kvalitetskontroll': '#97D4B7',
    'pakking': '#F6BA7C',
    'utsending': '#BD94D7',
}


def identify_bottleneck(stations: dict) -> str:
    """Returner navnet pa stasjonen med hoyest utnyttelsesgrad."""
    return max(stations.items(), key=lambda kv: kv[1]['utilization'])[0]


def plot_bottleneck_breakdown(stations: dict, output_path: Path) -> None:
    """Tre panel: rho, E[W], E[V] = E[W] + E[S] per stasjon."""
    names = list(stations.keys())
    labels = {'mottak': 'Mottak', 'kvalitetskontroll': 'Kval.kontr.',
              'pakking': 'Pakking', 'utsending': 'Utsending'}
    rhos = [stations[n]['utilization'] for n in names]
    waits = [stations[n]['mean_wait'] for n in names]
    services = [stations[n]['mean_service'] for n in names]
    sojourns = [stations[n]['mean_sojourn'] for n in names]

    bottleneck = identify_bottleneck(stations)

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    # (a) Utnyttelse
    ax = axes[0]
    colors = [FILLS[n] for n in names]
    edgecolors = [STROKES[n] for n in names]
    ax.bar([labels[n] for n in names], rhos, color=colors, edgecolor=edgecolors, linewidth=1.5)
    for i, r in enumerate(rhos):
        ax.text(i, r + 0.01, f'{r:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_ylim(0, 1.05)
    ax.set_ylabel(r'$\rho$', fontsize=12)
    ax.set_title(r'(a) Utnyttelsesgrad $\rho$', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=20)

    # (b) Ventetid
    ax = axes[1]
    ax.bar([labels[n] for n in names], waits, color=colors, edgecolor=edgecolors, linewidth=1.5)
    for i, w in enumerate(waits):
        ax.text(i, w + max(waits) * 0.02, f'{w:.2f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_ylabel(r'$E[W]$ (min)', fontsize=12)
    ax.set_title('(b) Gjennomsnittlig ventetid $E[W]$', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='x', rotation=20)

    # (c) Sojourn = wait + service (stablet)
    ax = axes[2]
    xs = np.arange(len(names))
    ax.bar(xs, waits, color=colors, edgecolor=edgecolors, linewidth=1.5, label=r'$E[W]$ (venting)')
    ax.bar(xs, services, bottom=waits, color='white', edgecolor=edgecolors, hatch='//',
           linewidth=1.5, label=r'$E[S]$ (service)')
    for i, v in enumerate(sojourns):
        ax.text(i, v + max(sojourns) * 0.02, f'{v:.2f}', ha='center', va='bottom',
                fontsize=10, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels([labels[n] for n in names], rotation=20)
    ax.set_ylabel(r'$E[V]$ (min)', fontsize=12)
    ax.set_title('(c) Oppholdstid pr.\\ stasjon $E[V] = E[W] + E[S]$', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)

    # Merk flaskehalsen
    fig.suptitle(f'Flaskehalsanalyse -- storst trykk pa "{bottleneck}"',
                 fontsize=13, fontweight='bold', y=1.03)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 4: FLASKEHALSANALYSE")
    print("=" * 60)

    # Kjor simulering pa nytt med samme seed for konsistens
    results = run_simulation(n_orders=5000, seed=2025)
    stations = results['stations']

    bn = identify_bottleneck(stations)
    print(f"\nIdentifisert flaskehals: {bn.upper()} (rho = {stations[bn]['utilization']:.3f})")
    print(f"Gjennomsnittlig ventetid i flaskehals: {stations[bn]['mean_wait']:.2f} min")
    print(f"Bidrag til total gjennomlopstid:       {stations[bn]['mean_sojourn']:.2f} min "
          f"(av totalt {results['mean_sojourn']:.2f} min)")
    share = stations[bn]['mean_sojourn'] / results['mean_sojourn']
    print(f"Andel av total gjennomlopstid:         {share*100:.1f}%")

    # Lagre analyse
    analysis = {
        'bottleneck': bn,
        'bottleneck_rho': stations[bn]['utilization'],
        'bottleneck_mean_wait': stations[bn]['mean_wait'],
        'bottleneck_mean_sojourn': stations[bn]['mean_sojourn'],
        'total_mean_sojourn': results['mean_sojourn'],
        'bottleneck_share_of_sojourn': share,
        'ranked_by_rho': sorted(
            [(n, s['utilization']) for n, s in stations.items()],
            key=lambda kv: kv[1], reverse=True,
        ),
    }
    with open(OUTPUT_DIR / 'step04_bottleneck.json', 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"\nAnalyse lagret: {OUTPUT_DIR / 'step04_bottleneck.json'}")

    # Figur
    plot_bottleneck_breakdown(stations, OUTPUT_DIR / 'qnet_bottleneck.png')


if __name__ == '__main__':
    main()
