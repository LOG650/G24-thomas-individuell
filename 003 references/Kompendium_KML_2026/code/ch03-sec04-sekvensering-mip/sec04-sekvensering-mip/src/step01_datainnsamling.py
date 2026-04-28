"""
Steg 1: Datainnsamling for produksjonssekvensering
==================================================
Genererer syntetiske jobbdata for et enkeltmaskin-sekvenseringsproblem
med vektet tardiness. Datasettet bestaar av to instanser:

    * N=15 jobber (for MIP)
    * N=50 jobber (for dispatch-heuristikker og simulated annealing)

For hver jobb j lagres:
    - p_j : prosesseringstid (timer)
    - d_j : forfallstidspunkt (timer fra t=0)
    - w_j : vekt (viktighetsfaktor for tardiness)
    - s_{ij}: setup/omstillingstid fra jobb i -> j (matrise)

Alle data lagres som CSV i data/ slik at paafolgende steg kan laste dem.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

RNG_SEED = 42


def generate_jobs(n: int, seed: int) -> pd.DataFrame:
    """Generer n jobber med prosesseringstid, forfallstid og vekt.

    Jobbene simulerer ordrer i et flydelsverksted for romfartskomponenter,
    der jobbene har ulik prioritet (vekt) og varierende deadline.
    """
    rng = np.random.default_rng(seed)

    # Prosesseringstider: lognormalfordelt mellom ca. 1 og 8 timer
    processing_times = np.round(rng.lognormal(mean=1.1, sigma=0.45, size=n), 2)
    processing_times = np.clip(processing_times, 1.0, 8.0)

    # Total prosesseringstid (lower bound paa makespan)
    total_p = processing_times.sum()

    # Forfallstider: spredt langs [0.4*total_p, 1.1*total_p] (blanding tight/loose).
    # Den tightere ovre grensen garanterer at noen jobber vil vaere tardy selv
    # i optimal sekvens, slik at tardiness-sammenligningen er meningsfull.
    due_dates = np.round(
        rng.uniform(0.4 * total_p, 1.05 * total_p, size=n), 2
    )

    # Vekter: tre prioritetsklasser (1 = lav, 2 = normal, 5 = hoy)
    weights = rng.choice([1, 2, 5], size=n, p=[0.35, 0.45, 0.20])

    df = pd.DataFrame({
        'job_id': np.arange(1, n + 1),
        'p': processing_times,
        'd': due_dates,
        'w': weights,
    })
    return df


def generate_setup_matrix(n: int, seed: int) -> np.ndarray:
    """Generer (n+1) x (n+1) setup-matrise s_{ij}.

    Indeks 0 er "dummy startjobb" (ingen setup fra start). For i >= 1,
    j >= 1, s_{ij} representerer omstillingstid mellom to forskjellige
    komponenttyper. Egenverdier s_{ii} = 0.
    """
    rng = np.random.default_rng(seed + 100)

    # Baseline setup-tid mellom ulike jobber
    S = np.round(rng.uniform(0.3, 1.5, size=(n + 1, n + 1)), 2)

    # Ingen setup fra "start" eller til samme jobb
    S[0, :] = 0.0
    S[:, 0] = 0.0
    np.fill_diagonal(S, 0.0)

    return S


def plot_job_overview(df: pd.DataFrame, output_path: Path, title_n: int) -> None:
    """Scatter-plott av forfallstid vs prosesseringstid, farget etter vekt."""
    fig, ax = plt.subplots(figsize=(10, 5))

    colors = {1: '#8CC8E5', 2: '#97D4B7', 5: '#ED9F9E'}
    for w in sorted(df['w'].unique()):
        sub = df[df['w'] == w]
        ax.scatter(
            sub['d'], sub['p'],
            s=80, c=colors[int(w)], edgecolor='#1F2933', linewidth=0.8,
            label=f'vekt $w_j = {int(w)}$',
        )

    for _, row in df.iterrows():
        ax.annotate(
            str(int(row['job_id'])),
            xy=(row['d'], row['p']),
            xytext=(4, 4), textcoords='offset points',
            fontsize=8, color='#1F2933',
        )

    ax.set_xlabel('Forfallstid $d_j$ (timer)', fontsize=12)
    ax.set_ylabel('Prosesseringstid $p_j$ (timer)', fontsize=12)
    ax.set_title(
        f'Jobber (N = {title_n}): prioritet, prosesseringstid og forfallstid',
        fontsize=12, fontweight='bold',
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc='upper right', fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING (SEKVENSERING)')
    print('=' * 60)

    summary: dict = {}

    for n, tag in [(6, 'small'), (50, 'large')]:
        seed = RNG_SEED + (0 if tag == 'small' else 1)
        df = generate_jobs(n, seed)
        S = generate_setup_matrix(n, seed)

        df.to_csv(DATA_DIR / f'jobs_{tag}.csv', index=False)
        np.savetxt(DATA_DIR / f'setup_{tag}.csv', S, delimiter=',', fmt='%.2f')

        total_p = float(df['p'].sum())
        summary[tag] = {
            'n_jobs': int(n),
            'total_processing_time': round(total_p, 2),
            'mean_p': round(float(df['p'].mean()), 2),
            'mean_d': round(float(df['d'].mean()), 2),
            'weights_dist': {
                str(int(k)): int(v) for k, v in df['w'].value_counts().items()
            },
            'mean_setup': round(float(S[1:, 1:].mean()), 3),
        }

        print(f"\n--- {tag.upper()} (N = {n}) ---")
        print(f"Total prosesseringstid sum(p_j): {total_p:.2f} t")
        print(f"Gjennomsnitt p_j = {df['p'].mean():.2f} t, d_j = {df['d'].mean():.2f} t")
        print(f"Vektfordeling: {dict(df['w'].value_counts().sort_index())}")

        if tag == 'small':
            plot_job_overview(df, OUTPUT_DIR / 'seqmip_jobs_overview.png', n)

    with open(OUTPUT_DIR / 'step01_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering lagret: {OUTPUT_DIR / 'step01_summary.json'}")


if __name__ == '__main__':
    main()
