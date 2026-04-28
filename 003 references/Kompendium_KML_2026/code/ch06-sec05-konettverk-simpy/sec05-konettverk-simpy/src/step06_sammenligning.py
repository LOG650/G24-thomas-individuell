"""
Steg 6: Sammenligning og KPI-er
===============================
  - qnet_whatif_compare.png : ventetid og gjennomstromning for alle scenariene
  - qnet_throughput.png     : gjennomstromning vs. ankomstrate (mettede regimer)
  - qnet_method.png         : prosessdiagram for simuleringsstudien
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step02_grunnmodell import run_simulation

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


# ============================================================
# Hjelper
# ============================================================

def plot_whatif_comparison(output_path: Path) -> None:
    """Les step05_whatif.json og lag sammenligningsfigur."""
    with open(OUTPUT_DIR / 'step05_whatif.json', encoding='utf-8') as f:
        data = json.load(f)

    labels_map = {
        'baseline': 'Basismodell',
        'A_extra_server': '(A) Ekstra\npakkeserver',
        'B_less_var': '(B) Redusert\nvariabilitet',
        'C_surge': '(C) Ankomsttopp\n$\\lambda=42$/t',
    }
    order = ['baseline', 'A_extra_server', 'B_less_var', 'C_surge']
    colors_fill = ['#8CC8E5', '#97D4B7', '#BD94D7', '#ED9F9E']
    colors_stroke = ['#1F6587', '#307453', '#5A2C77', '#961D1C']

    means = [data[k]['mean_sojourn'] for k in order]
    p95s = [data[k]['p95_sojourn'] for k in order]
    thrus = [data[k]['throughput_per_hour'] for k in order]
    rho_pakk = [data[k]['stations']['pakking']['utilization'] for k in order]

    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))

    xs = np.arange(len(order))
    width = 0.38

    # (a) E[V] og P95[V]
    ax = axes[0]
    ax.bar(xs - width / 2, means, width, color=colors_fill, edgecolor=colors_stroke,
           linewidth=1.5, label=r'$E[V]$')
    ax.bar(xs + width / 2, p95s, width, color='white',
           edgecolor=colors_stroke, hatch='//', linewidth=1.5, label=r'$P_{95}[V]$')
    for i, (m, p) in enumerate(zip(means, p95s)):
        ax.text(i - width / 2, m + 0.3, f'{m:.1f}', ha='center', fontsize=9)
        ax.text(i + width / 2, p + 0.3, f'{p:.1f}', ha='center', fontsize=9)
    ax.set_xticks(xs)
    ax.set_xticklabels([labels_map[k] for k in order], fontsize=9)
    ax.set_ylabel('Gjennomlopstid (min)', fontsize=11)
    ax.set_title('(a) Total gjennomlopstid', fontsize=11, fontweight='bold')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)

    # (b) gjennomstromning
    ax = axes[1]
    ax.bar(xs, thrus, color=colors_fill, edgecolor=colors_stroke, linewidth=1.5)
    for i, t in enumerate(thrus):
        ax.text(i, t + 0.6, f'{t:.1f}', ha='center', fontsize=10, fontweight='bold')
    ax.set_xticks(xs)
    ax.set_xticklabels([labels_map[k] for k in order], fontsize=9)
    ax.set_ylabel('Ordrer / time', fontsize=11)
    ax.set_title('(b) Gjennomstromning', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)

    # (c) rho ved pakking (flaskehals)
    ax = axes[2]
    ax.bar(xs, rho_pakk, color=colors_fill, edgecolor=colors_stroke, linewidth=1.5)
    for i, r in enumerate(rho_pakk):
        ax.text(i, r + 0.012, f'{r:.3f}', ha='center', fontsize=9, fontweight='bold')
    ax.axhline(1.0, color='#961D1C', linestyle='--', linewidth=1.2, alpha=0.7)
    ax.set_xticks(xs)
    ax.set_xticklabels([labels_map[k] for k in order], fontsize=9)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel(r'$\rho$ pakking', fontsize=11)
    ax.set_title('(c) Utnyttelsesgrad i flaskehals', fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)

    fig.suptitle('What-if-sammenligning: fire scenarier', fontsize=13, fontweight='bold', y=1.02)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_throughput_vs_lambda(output_path: Path) -> None:
    """Gjennomlopstid og gjennomstromning vs. ankomstrate for baseline vs. +server."""
    lambdas = [25, 30, 35, 40, 45, 50, 55, 60]

    baseline_sojourn = []
    baseline_tp = []
    extra_sojourn = []
    extra_tp = []
    for lam in lambdas:
        r_b = run_simulation(n_orders=3000, seed=11, arrival_rate_per_hour=lam)
        r_a = run_simulation(n_orders=3000, seed=11, arrival_rate_per_hour=lam,
                             station_overrides={'pakking': {'servers': 3}})
        baseline_sojourn.append(r_b['mean_sojourn'])
        baseline_tp.append(r_b['throughput_per_hour'])
        extra_sojourn.append(r_a['mean_sojourn'])
        extra_tp.append(r_a['throughput_per_hour'])
        print(f"  lambda={lam:>3d}  baseline E[V]={r_b['mean_sojourn']:6.2f}  "
              f"extra E[V]={r_a['mean_sojourn']:6.2f}")

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    # (a) Gjennomlopstid
    ax = axes[0]
    ax.plot(lambdas, baseline_sojourn, 'o-', color='#1F6587', linewidth=2,
            markersize=7, label='Basismodell (c$_{pakking}$=2)')
    ax.plot(lambdas, extra_sojourn, 's-', color='#307453', linewidth=2,
            markersize=7, label='Med ekstra server (c$_{pakking}$=3)')
    ax.set_xlabel(r'Ankomstrate $\lambda$ (ordrer/time)', fontsize=11)
    ax.set_ylabel(r'$E[V]$ (min)', fontsize=11)
    ax.set_title('(a) Gjennomlopstid vs. ankomstrate', fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    # (b) Gjennomstromning
    ax = axes[1]
    ax.plot(lambdas, baseline_tp, 'o-', color='#1F6587', linewidth=2, markersize=7,
            label='Basismodell')
    ax.plot(lambdas, extra_tp, 's-', color='#307453', linewidth=2, markersize=7,
            label='Med ekstra server')
    ax.plot(lambdas, lambdas, '--', color='#556270', linewidth=1.2, alpha=0.7,
            label=r'$y=\lambda$ (ideell)')
    ax.set_xlabel(r'Ankomstrate $\lambda$ (ordrer/time)', fontsize=11)
    ax.set_ylabel('Gjennomstromning (ordrer/time)', fontsize=11)
    ax.set_title('(b) Gjennomstromning vs. ankomstrate', fontsize=11, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")

    # Lagre tabelldata
    with open(OUTPUT_DIR / 'step06_throughput_sweep.json', 'w', encoding='utf-8') as f:
        json.dump({
            'lambdas': lambdas,
            'baseline_mean_sojourn': baseline_sojourn,
            'baseline_throughput': baseline_tp,
            'extra_mean_sojourn': extra_sojourn,
            'extra_throughput': extra_tp,
        }, f, indent=2)


def plot_method_diagram(output_path: Path) -> None:
    """Flytskjema for simuleringsstudien (steg 1-6)."""
    fig, ax = plt.subplots(figsize=(12, 4.5))

    steps = [
        ('1. Data-\ninnsamling', '#8CC8E5', '#1F6587'),
        ('2. Grunn-\nmodell', '#97D4B7', '#307453'),
        ('3. Basis-\nsimulering', '#F6BA7C', '#9C540B'),
        ('4. Flaskehals-\nanalyse', '#BD94D7', '#5A2C77'),
        ('5. What-if\nscenarier', '#ED9F9E', '#961D1C'),
        ('6. Sammen-\nligning', '#8CC8E5', '#1F6587'),
    ]

    x_pos = np.linspace(0.5, 11, len(steps))
    y = 0.5
    w, h = 1.3, 1.0

    for (x, (label, fill, stroke)) in zip(x_pos, steps):
        rect = plt.Rectangle((x - w / 2, y - h / 2), w, h,
                             facecolor=fill, edgecolor=stroke, linewidth=2, zorder=2)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center', fontsize=10,
                color=stroke, fontweight='bold', zorder=3)

    for i in range(len(steps) - 1):
        ax.annotate('', xy=(x_pos[i + 1] - w / 2, y),
                    xytext=(x_pos[i] + w / 2, y),
                    arrowprops=dict(arrowstyle='->', color='#556270', lw=1.8), zorder=1)

    # Tilbakekobling fra steg 6 til steg 2 (iterasjon)
    ax.annotate('', xy=(x_pos[1], y + h / 2 + 0.05),
                xytext=(x_pos[-1], y + h / 2 + 0.05),
                arrowprops=dict(arrowstyle='->', color='#1F6587', lw=1.5,
                                connectionstyle='arc3,rad=-0.3'))
    ax.text((x_pos[1] + x_pos[-1]) / 2, y + h / 2 + 0.65, 'Iterativ forbedring',
            ha='center', fontsize=10, color='#1F6587', fontweight='bold')

    ax.set_xlim(-0.2, 11.8)
    ax.set_ylim(-0.3, 1.9)
    ax.axis('off')
    ax.set_title('Simuleringsstudie: prosessdiagram', fontsize=12, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 6: SAMMENLIGNING OG METODE")
    print("=" * 60)

    plot_whatif_comparison(OUTPUT_DIR / 'qnet_whatif_compare.png')

    print("\nKjorer throughput-sweep (8 x 2 simuleringer) ...")
    plot_throughput_vs_lambda(OUTPUT_DIR / 'qnet_throughput.png')

    plot_method_diagram(OUTPUT_DIR / 'qnet_method.png')


if __name__ == '__main__':
    main()
