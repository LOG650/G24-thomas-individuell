"""
Steg 6: Statistisk sammenligning av heuristikker vs eksakt DP
=============================================================
Sammenligner rutelengder for alle 500 plukklister:
- S-shape
- Return
- Midpoint
- Largest-gap
- Ratliff-Rosenthal (eksakt DP)

Genererer to figurer:
- pickrt_gap_distribution.png : fordeling av prosentvis gap vs optimum
- pickrt_method.png           : prosessdiagram (laget manuelt som matplotlib-figur)
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def load_lengths(fname: str) -> list[float]:
    with open(OUTPUT_DIR / fname, encoding='utf-8') as f:
        return json.load(f)


def gap_pct(heur: list[float], opt: list[float]) -> list[float]:
    return [100.0 * (h - o) / o if o > 0 else 0.0 for h, o in zip(heur, opt)]


def summary_stats(vals: list[float]) -> dict:
    a = np.array(vals)
    return {
        'mean': round(float(a.mean()), 3),
        'std': round(float(a.std(ddof=1)), 3),
        'median': round(float(np.median(a)), 3),
        'p5': round(float(np.percentile(a, 5)), 3),
        'p95': round(float(np.percentile(a, 95)), 3),
        'min': round(float(a.min()), 3),
        'max': round(float(a.max()), 3),
    }


def plot_gap_distribution(gaps: dict[str, list[float]], output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {
        'S-shape': '#1F6587',
        'Return': '#9C540B',
        'Midpoint': '#5A2C77',
        'Largest-gap': '#307453',
    }
    bins = np.linspace(0, max(max(v) for v in gaps.values()) + 5, 40)
    for name, vals in gaps.items():
        ax.hist(vals, bins=bins, alpha=0.45, label=name,
                color=colors.get(name, '#1F2933'),
                edgecolor='white', linewidth=0.5)

    ax.set_xlabel('Prosentvis gap vs. Ratliff-Rosenthal optimum (%)', fontsize=12)
    ax.set_ylabel('Antall plukklister', fontsize=12)
    ax.set_title('Fordeling av gap til optimum over 500 plukklister',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_method_diagram(output_path: Path) -> None:
    """Enkelt prosessdiagram for plukkruteoptimering."""
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4)
    ax.axis('off')

    boxes = [
        (0.5, 'Steg 1\nDatainnsamling\n(lagerlayout + plukklister)', '#8CC8E5', '#1F6587'),
        (2.8, 'Steg 2\nS-shape\n(traversering)', '#97D4B7', '#307453'),
        (5.0, 'Steg 3\nLargest-gap\n(gap-regel)', '#F6BA7C', '#9C540B'),
        (7.2, 'Steg 4\nReturn / Midpoint\n(return-regler)', '#BD94D7', '#5A2C77'),
        (9.4, 'Steg 5\nRatliff-Rosenthal\n(eksakt DP)', '#ED9F9E', '#961D1C'),
    ]
    for (x, text, fill, edge) in boxes:
        rect = plt.Rectangle((x, 1.2), 2.0, 1.8, facecolor=fill, edgecolor=edge,
                             linewidth=1.8, zorder=2)
        ax.add_patch(rect)
        ax.text(x + 1.0, 2.1, text, ha='center', va='center', fontsize=9,
                color='#1F2933', fontweight='bold', zorder=3)

    # piler
    for x in [2.5, 4.7, 6.9, 9.1]:
        ax.annotate('', xy=(x + 0.3, 2.1), xytext=(x, 2.1),
                    arrowprops=dict(arrowstyle='->', color='#556270', lw=1.5))

    # Steg 6 under
    rect = plt.Rectangle((4.0, 0.1), 4.0, 0.9, facecolor='#F4F7FB',
                         edgecolor='#1F2933', linewidth=1.5, zorder=2)
    ax.add_patch(rect)
    ax.text(6.0, 0.55, 'Steg 6: Statistisk sammenligning\n(gjennomsnittlig gap vs optimum)',
            ha='center', va='center', fontsize=9, color='#1F2933',
            fontweight='bold', zorder=3)
    # pil fra over til Steg 6
    ax.annotate('', xy=(6.0, 1.0), xytext=(6.0, 1.2),
                arrowprops=dict(arrowstyle='->', color='#556270', lw=1.5))

    ax.set_title('Plukkruteoptimering: heuristikker vs eksakt DP',
                 fontsize=11, fontweight='bold', pad=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 6: SAMMENLIGNING AV HEURISTIKKER OG EKSAKT DP")
    print("=" * 60)

    sshape = load_lengths('sshape_lengths.json')
    ret = load_lengths('return_lengths.json')
    mid = load_lengths('midpoint_lengths.json')
    lg = load_lengths('largestgap_lengths.json')
    rr = load_lengths('rr_lengths.json')

    print(f"\nLastede rutelengder fra {len(sshape)} plukklister")

    # Snitt
    print("\nGjennomsnittlig rutelengde (meter):")
    print(f"  S-shape:              {np.mean(sshape):7.2f}")
    print(f"  Return:               {np.mean(ret):7.2f}")
    print(f"  Midpoint:             {np.mean(mid):7.2f}")
    print(f"  Largest-gap:          {np.mean(lg):7.2f}")
    print(f"  Ratliff-Rosenthal:    {np.mean(rr):7.2f}")

    # Prosentvise gaps
    gaps = {
        'S-shape': gap_pct(sshape, rr),
        'Return': gap_pct(ret, rr),
        'Midpoint': gap_pct(mid, rr),
        'Largest-gap': gap_pct(lg, rr),
    }

    print("\nGap mot RR-optimum (prosent):")
    print(f"{'Heuristikk':<20}{'Snitt':>10}{'Median':>10}{'P5':>10}{'P95':>10}")
    stats = {}
    for name, vals in gaps.items():
        s = summary_stats(vals)
        stats[name] = s
        print(f"{name:<20}{s['mean']:>10.2f}{s['median']:>10.2f}"
              f"{s['p5']:>10.2f}{s['p95']:>10.2f}")

    results = {
        'n_picklists': len(sshape),
        'mean_lengths': {
            'S-shape': round(float(np.mean(sshape)), 2),
            'Return': round(float(np.mean(ret)), 2),
            'Midpoint': round(float(np.mean(mid)), 2),
            'Largest-gap': round(float(np.mean(lg)), 2),
            'Ratliff-Rosenthal': round(float(np.mean(rr)), 2),
        },
        'gap_statistics_pct': stats,
    }
    with open(OUTPUT_DIR / 'comparison_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nSammenligning lagret: {OUTPUT_DIR / 'comparison_results.json'}")

    # Figurer
    plot_gap_distribution(gaps, OUTPUT_DIR / 'pickrt_gap_distribution.png')
    plot_method_diagram(OUTPUT_DIR / 'pickrt_method.png')


if __name__ == '__main__':
    main()
