"""
Steg 6: Anbefaling under ulike preferanseprofiler
==================================================
Hva er den anbefalte leverandøren dersom innkjøpssjefen vektlegger
andre ting enn baseline-profilen? Vi definerer tre alternative
profiler og kjører TOPSIS for hver:

  * Baseline           -- AHP-vekter fra steg 2
  * Kostnadsfokus      -- tung vekt på pris og leveringstid
  * Kvalitetsfokus     -- tung vekt på kvalitet og bærekraft
  * Fleksibilitetsfokus-- tung vekt på fleksibilitet og leveringstid

Sammenligningen viser hvor robust vinneren er på tvers av ulike
strategiske prioriteringer.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    CRITERIA,
    CRITERION_TYPES,
    SUPPLIERS,
    get_pairwise_dataframe,
    get_performance_dataframe,
)
from step02_ahp_vekter import ahp_eigenvector_weights
from step03_topsis import topsis_scores

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def build_profiles(w_base: np.ndarray) -> dict:
    """Returnerer ordbok med navngitte vektprofiler (summerer til 1)."""
    # Rekkefølge: Pris, Kvalitet, Leveringstid, Fleksibilitet, Bærekraft
    profiles = {
        'Baseline (AHP)': w_base,
        'Kostnadsfokus':  np.array([0.40, 0.20, 0.25, 0.08, 0.07]),
        'Kvalitetsfokus': np.array([0.15, 0.45, 0.10, 0.10, 0.20]),
        'Fleksibilitetsfokus': np.array([0.15, 0.20, 0.25, 0.30, 0.10]),
    }
    # Normaliser for sikkerhets skyld
    for k in profiles:
        profiles[k] = profiles[k] / profiles[k].sum()
    return profiles


def plot_profile_comparison(
    profiles: dict,
    C_by_profile: dict,
    output_path: Path,
) -> None:
    """Gruppert søylediagram: C_i per leverandør for hver profil."""
    fig, ax = plt.subplots(figsize=(11, 5.5))
    profile_names = list(profiles.keys())
    n_profiles = len(profile_names)
    n_sup = len(SUPPLIERS)

    colors = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7']
    width = 0.82 / n_profiles
    x = np.arange(n_sup)

    for i, pname in enumerate(profile_names):
        offset = (i - (n_profiles - 1) / 2) * width
        ax.bar(x + offset, C_by_profile[pname], width,
               label=pname, color=colors[i % len(colors)],
               edgecolor='black', linewidth=0.5)

    ax.set_xticks(x)
    ax.set_xticklabels(SUPPLIERS, fontsize=11)
    ax.set_ylabel('Nærhetsskår $C_i$', fontsize=11)
    ax.set_title('TOPSIS-skår under ulike preferanseprofiler',
                 fontsize=12, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    ax.legend(loc='upper right', fontsize=9, ncol=2)
    ax.tick_params(axis='both', labelsize=10)
    ax.set_ylim(0, 1.0)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 6: ANBEFALING UNDER ULIKE PROFILER")
    print(f"{'='*60}")

    perf = get_performance_dataframe()
    X = perf.values.astype(float)
    ctypes = [CRITERION_TYPES[c] for c in CRITERIA]

    A_pair = get_pairwise_dataframe().values
    w_base, _ = ahp_eigenvector_weights(A_pair)

    profiles = build_profiles(w_base)

    # Kjør TOPSIS per profil
    C_by_profile: dict = {}
    rank_by_profile: dict = {}
    winners = {}
    for name, w in profiles.items():
        out = topsis_scores(X, w, ctypes)
        C_by_profile[name] = out['C']
        order = np.argsort(-out['C'])
        rank_by_profile[name] = order.argsort() + 1
        winners[name] = SUPPLIERS[int(order[0])]

    print("\n--- Vinner per profil ---")
    for name, winner in winners.items():
        w = profiles[name]
        C_win = C_by_profile[name][SUPPLIERS.index(winner)]
        w_str = ', '.join(f'{c}:{wi:.2f}' for c, wi in zip(CRITERIA, w))
        print(f"  {name:<22s} -> {winner}  (C={C_win:.4f})")
        print(f"     vekter: {w_str}")

    # Full tabell
    print("\n--- C-skår per profil ---")
    header = f"  {'Leverandør':<10s}" + ''.join(f'{n:>22s}' for n in profiles)
    print(header)
    for i, s in enumerate(SUPPLIERS):
        row = f"  {s:<10s}"
        for name in profiles:
            row += f'{C_by_profile[name][i]:>22.4f}'
        print(row)

    # Serialiser
    serial = {
        'profiles': {k: [float(round(x, 6)) for x in v.tolist()]
                     for k, v in profiles.items()},
        'C': {k: [float(round(x, 6)) for x in v.tolist()]
              for k, v in C_by_profile.items()},
        'rank': {k: [int(x) for x in v.tolist()]
                 for k, v in rank_by_profile.items()},
        'winners': winners,
        'criteria': CRITERIA,
        'suppliers': SUPPLIERS,
    }
    with open(OUTPUT_DIR / 'step06_results.json', 'w', encoding='utf-8') as f:
        json.dump(serial, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step06_results.json'}")

    # Figur
    plot_profile_comparison(profiles, C_by_profile,
                            OUTPUT_DIR / 'ahp_profiler.png')


if __name__ == '__main__':
    main()
