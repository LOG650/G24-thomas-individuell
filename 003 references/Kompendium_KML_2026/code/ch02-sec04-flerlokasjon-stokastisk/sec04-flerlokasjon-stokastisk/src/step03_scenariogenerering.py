"""
Steg 3: Scenariogenerering + scenario-reduksjon
===============================================
Genererer ``N_SCEN = 10 000`` scenariør for etterspørsel i en
planleggingsperiode på ``PERIOD_DAYS`` dager, og reduserer til
``N_REDUCED = 60`` representative scenariør ved hjelp av en
Kantorovich-/fast-forward-heuristikk. Vektene summerer til 1.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    CORRELATION,
    LOCATION_PARAMS,
    LOCATIONS,
    SEED,
)

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

N_SCEN = 10_000
N_REDUCED = 60
PERIOD_DAYS = 7  # scenariør beskriver én gjennomgangsperiode


def generate_scenarios(n_scenarios: int = N_SCEN, period_days: int = PERIOD_DAYS,
                       seed: int = SEED + 1) -> np.ndarray:
    """Returnerer array med shape (n_scenarios, n_locations): total etterspørsel
    over ``period_days`` dager per lokasjon.
    """
    rng = np.random.default_rng(seed)
    mus = np.array([LOCATION_PARAMS[l]["mu"] for l in LOCATIONS])
    sigmas = np.array([LOCATION_PARAMS[l]["sigma"] for l in LOCATIONS])

    # Periode-aggregert etterspørsel har mu_p = P * mu, var_p = P * sigma^2
    mu_p = mus * period_days
    sigma_p = sigmas * np.sqrt(period_days)
    cov_p = CORRELATION * np.outer(sigma_p, sigma_p)
    samples = rng.multivariate_normal(mu_p, cov_p, size=n_scenarios)
    samples = np.clip(np.round(samples), 0, None)
    return samples


def fast_forward_reduction(scenarios: np.ndarray, n_reduced: int = N_REDUCED) -> tuple[np.ndarray, np.ndarray]:
    """Fast-forward Kantorovich scenario-reduksjon.

    Implementerer en forenklet variant av Heitsch & Römisch (2003)
    fast-forward heuristikken:

    1. Startpopulasjon: alle scenariør har lik vekt ``1/N``.
    2. Finn det scenarioet som, når lagt til det reduserte settet,
       gir minst Kantorovich-avstand til det opprinnelige settet --
       her approksimert ved å velge scenariø-en-om-gangen som
       minimerer summert L2-avstand til alle andre.
    3. Fjern det utvalgte scenarioet fra kandidatsettet. Gjenta til
       ``n_reduced`` scenariør er valgt.
    4. Tildel vekter: hvert opprinnelig scenario mappes til nærmeste
       utvalgte, og vekten til utvalgte = andel av opprinnelige
       scenariør som mapper til det.

    Returnerer: (reduced_scenarios, weights) der weights summerer til 1.
    """
    n, _ = scenarios.shape
    selected_idx: list[int] = []
    remaining = list(range(n))

    # Forhåndsberegn distanser til første utvalg (start med det
    # "sentrale" scenariet: minimerer sum av avstander til alle)
    dist_matrix = np.linalg.norm(scenarios[:, None, :] - scenarios[None, :, :], axis=2)

    # Første utvalg = argmin sum av distanser (medoid)
    total_dist = dist_matrix.sum(axis=1)
    first = int(np.argmin(total_dist))
    selected_idx.append(first)
    remaining.remove(first)

    # Greedy forward: legg til scenariø som reduserer Kantorovich-
    # avstand mest. Proxy: minimer maks-distanse fra noen kandidat
    # til nærmeste allerede valgte.
    min_dist_to_selected = dist_matrix[first].copy()

    while len(selected_idx) < n_reduced:
        # Finn kandidat som maksimerer nytten: den som har størst
        # avstand til nærmeste allerede valgte scenarieø (dvs.
        # dårligst dekket -- legg til for å redusere total avstand)
        candidate_scores = np.where(
            np.isin(np.arange(n), selected_idx),
            -np.inf,  # ekskluder allerede valgte
            min_dist_to_selected,
        )
        best = int(np.argmax(candidate_scores))
        selected_idx.append(best)
        if best in remaining:
            remaining.remove(best)
        # Oppdater minimumsavstander
        min_dist_to_selected = np.minimum(min_dist_to_selected, dist_matrix[best])

    selected_idx = np.array(selected_idx)
    reduced = scenarios[selected_idx]

    # Tildel vekter: hvert original-scenario mapper til nærmeste utvalgte
    assign = np.argmin(dist_matrix[:, selected_idx], axis=1)
    weights = np.bincount(assign, minlength=n_reduced) / n
    # Normaliser
    weights = weights / weights.sum()
    return reduced, weights


def plot_scenario_reduction(
    full: np.ndarray,
    reduced: np.ndarray,
    weights: np.ndarray,
    output_path: Path,
) -> None:
    """Visualiser reduksjonen i 2D (L1 vs L2)."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # Venstre: alle scenariø som lett sky
    axes[0].scatter(full[:, 0], full[:, 1], s=4, alpha=0.15, c="#8CC8E5")
    axes[0].set_xlabel(r"Total etterspørsel L1 over $R=7$ dager")
    axes[0].set_ylabel(r"Total etterspørsel L2")
    axes[0].set_title(f"Alle {full.shape[0]:,} scenariør", fontsize=12, fontweight="bold")
    axes[0].grid(True, alpha=0.3)

    # Høyre: reduserte med størrelse prop til vekt
    axes[1].scatter(full[:, 0], full[:, 1], s=2, alpha=0.08, c="#8CC8E5", label="Originale")
    size = weights * 6000
    axes[1].scatter(
        reduced[:, 0],
        reduced[:, 1],
        s=size,
        alpha=0.8,
        c="#ED9F9E",
        edgecolors="#961D1C",
        linewidths=1,
        label=f"{len(reduced)} reduserte",
    )
    axes[1].set_xlabel(r"Total etterspørsel L1 over $R=7$ dager")
    axes[1].set_ylabel(r"Total etterspørsel L2")
    axes[1].set_title("Reduserte scenariør (størrelse = vekt $p^s$)", fontsize=12, fontweight="bold")
    axes[1].legend(loc="upper left", fontsize=9)
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 3: Scenariogenerering og scenario-reduksjon")
    print("=" * 60)

    scenarios = generate_scenarios()
    print(f"Genererte {scenarios.shape[0]:,} scenariø av dim {scenarios.shape[1]}")

    reduced, weights = fast_forward_reduction(scenarios, N_REDUCED)
    print(f"Redusert til {reduced.shape[0]} scenariø med vektsum {weights.sum():.4f}")
    print(f"  min vekt = {weights.min():.4f}, maks vekt = {weights.max():.4f}")

    # Sammenlign mean og cov
    mean_full = scenarios.mean(axis=0)
    mean_red = (reduced * weights[:, None]).sum(axis=0)
    cov_full = np.cov(scenarios.T)
    cov_red = np.cov(reduced.T, aweights=weights)

    print("\nSanity check (full vs redusert):")
    for i, loc in enumerate(LOCATIONS):
        print(f"  {loc}: mu = {mean_full[i]:7.2f} vs {mean_red[i]:7.2f}  |  "
              f"sigma = {np.sqrt(cov_full[i, i]):6.2f} vs {np.sqrt(cov_red[i, i]):6.2f}")

    # Lagre for neste steg
    np.savez(
        OUTPUT_DIR / "step03_scenarios.npz",
        reduced=reduced,
        weights=weights,
        full_mean=mean_full,
        full_cov=cov_full,
    )
    with open(OUTPUT_DIR / "step03_reduction_summary.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "n_full": int(scenarios.shape[0]),
                "n_reduced": int(reduced.shape[0]),
                "period_days": PERIOD_DAYS,
                "mean_full": mean_full.round(3).tolist(),
                "mean_reduced": mean_red.round(3).tolist(),
                "sigma_full": np.sqrt(np.diag(cov_full)).round(3).tolist(),
                "sigma_reduced": np.sqrt(np.diag(cov_red)).round(3).tolist(),
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    plot_scenario_reduction(scenarios, reduced, weights, OUTPUT_DIR / "mlstok_scenario_reduction.png")


if __name__ == "__main__":
    main()
