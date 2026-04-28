"""
Steg 3: Tilfeldig tildeling -- baseline
========================================
Beregner forventet reisedistanse per plukklinje for en tilfeldig tildeling
av SKU-er til slots (random storage). To maaltall rapporteres:

1. Analytisk forventning: E[d] = (1/N) sum_i d_i -- gjennomsnitt av
   rundturs-distansen over alle slots, vektet likt.
2. Monte Carlo: trekk plukklinjer proporsjonalt med plukkfrekvens, og
   simuler gjennomsnittlig distanse per plukk gjennom realistiske
   plukklister.

Distanse maales som enkelt plukk (en linje per tur til pakkestasjonen).
I praksis vil en ordre bestaa av flere linjer som plukkes i samme tur;
her bruker vi per-linje rundtur som en enkel, sammenlignbar baseline.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import (
    DATA_DIR,
    OUTPUT_DIR,
    PRIMARY,
    INKMUTED,
    S_DARKS,
    S_FILLS,
)


def random_assignment(
    slots: pd.DataFrame, sku_classes: pd.DataFrame, seed: int = 2027
) -> pd.DataFrame:
    """Tildel SKU-er til slots uniformt tilfeldig.

    Hver SKU faar nayaktig en slot, og hver slot har hoyst en SKU.
    Returneres som DataFrame med kolonnene sku_id og slot_id.
    """
    rng = np.random.default_rng(seed)
    slot_ids = np.array(slots["slot_id"].tolist(), dtype=object)
    rng.shuffle(slot_ids)
    # Ta kun de forste N_SKU
    n = len(sku_classes)
    assignment = pd.DataFrame(
        {"sku_id": sku_classes["sku_id"].values, "slot_id": slot_ids[:n]}
    )
    return assignment


def attach_distance(
    assignment: pd.DataFrame, slots: pd.DataFrame,
    history: pd.DataFrame,
) -> pd.DataFrame:
    """Legger til distanse og daglig frekvens per SKU."""
    merged = assignment.merge(
        slots[["slot_id", "d_round_trip"]], on="slot_id", how="left"
    )
    merged = merged.merge(
        history[["sku_id", "plukk_90d"]], on="sku_id", how="left"
    )
    return merged


def expected_distance(assignment: pd.DataFrame) -> float:
    """Forventet reisedistanse per plukklinje (vektet gjennomsnitt)."""
    total_picks = assignment["plukk_90d"].sum()
    weighted = (assignment["d_round_trip"] * assignment["plukk_90d"]).sum()
    return float(weighted / total_picks)


def monte_carlo_distance(
    assignment: pd.DataFrame, n_samples: int = 50_000,
    seed: int = 2028,
) -> np.ndarray:
    """Trekker plukklinjer proporsjonalt med plukkfrekvens og returnerer
    distansene.
    """
    rng = np.random.default_rng(seed)
    probs = assignment["plukk_90d"].values / assignment["plukk_90d"].sum()
    distances = assignment["d_round_trip"].values
    idx = rng.choice(len(assignment), size=n_samples, p=probs, replace=True)
    return distances[idx]


def plot_distance_histogram(
    distances: np.ndarray, output_path: Path,
    mean_d: float, label: str,
) -> None:
    """Histogram av simulerte plukkdistanser."""
    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.hist(distances, bins=40, color=S_FILLS[0], edgecolor=S_DARKS[0])
    ax.axvline(mean_d, color=S_DARKS[4], ls="--", lw=2,
               label=f"Gj.snitt = {mean_d:.1f} m")
    ax.set_xlabel("Rundturs-distanse per plukklinje (m)", fontsize=11)
    ax.set_ylabel("Antall simulerte plukk", fontsize=11)
    ax.set_title(f"Distansefordeling ved {label}", fontsize=12,
                 fontweight="bold")
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_heatmap(
    assignment: pd.DataFrame, slots: pd.DataFrame,
    history: pd.DataFrame, output_path: Path, title: str,
) -> None:
    """Heatmap over lagerlayout som viser plukkfrekvens per lokasjon."""
    # assignment kan allerede ha plukk_90d-kolonne. Lag et rent grunnlag.
    base = assignment[["sku_id", "slot_id"]].drop_duplicates("sku_id")
    merged = base.merge(slots, on="slot_id", how="left").merge(
        history[["sku_id", "plukk_90d"]], on="sku_id", how="left"
    )
    # Agreger per (aisle, col) ved aa summere over side L/R
    grouped = (
        merged.groupby(["aisle", "col"])["plukk_90d"]
        .sum()
        .reset_index()
    )
    n_aisles = int(grouped["aisle"].max()) + 1
    n_cols = int(grouped["col"].max()) + 1
    grid = np.zeros((n_cols, n_aisles))
    for _, row in grouped.iterrows():
        grid[int(row["col"]), int(row["aisle"])] = row["plukk_90d"]

    fig, ax = plt.subplots(figsize=(8, 5))
    # Vi plotter "sor" nederst: col=0 er naer pakkestasjonen (y = PICK_HEADER)
    im = ax.imshow(
        grid, origin="lower", cmap="YlOrRd",
        aspect="auto", interpolation="nearest",
    )
    ax.set_xlabel("Gang (aisle)", fontsize=11)
    ax.set_ylabel("Kolonne (col, naermest pakkestasjon nederst)", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xticks(range(n_aisles))
    ax.set_yticks(range(0, n_cols, 2))
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Plukk per celle (90 dager)", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 3: TILFELDIG TILDELING (BASELINE)")
    print("=" * 60)

    slots = pd.read_csv(DATA_DIR / "slots.csv")
    history = pd.read_csv(DATA_DIR / "plukkhistorikk.csv")
    classes = pd.read_csv(DATA_DIR / "sku_klasser.csv")

    assignment = random_assignment(slots, classes)
    enriched = attach_distance(assignment, slots, history)
    enriched.to_csv(DATA_DIR / "tildeling_tilfeldig.csv", index=False)

    e_d = expected_distance(enriched)
    print(f"\nAnalytisk forventet distanse per plukk: {e_d:.2f} m")

    mc = monte_carlo_distance(enriched)
    mean_mc = float(mc.mean())
    median_mc = float(np.median(mc))
    p95_mc = float(np.percentile(mc, 95))
    print(f"Monte Carlo gjennomsnitt: {mean_mc:.2f} m")
    print(f"Monte Carlo median: {median_mc:.2f} m")
    print(f"Monte Carlo P95: {p95_mc:.2f} m")

    summary = {
        "metode": "tilfeldig",
        "analytisk_forventet_m": round(e_d, 2),
        "mc_gjennomsnitt_m": round(mean_mc, 2),
        "mc_median_m": round(median_mc, 2),
        "mc_p95_m": round(p95_mc, 2),
        "mc_std_m": round(float(mc.std()), 2),
        "mc_min_m": round(float(mc.min()), 2),
        "mc_max_m": round(float(mc.max()), 2),
        "samples": len(mc),
    }
    with open(OUTPUT_DIR / "step03_random_summary.json", "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Lagre rene MC-distanser til bruk i senere steg
    np.save(OUTPUT_DIR / "mc_distances_random.npy", mc)

    plot_distance_histogram(
        mc, OUTPUT_DIR / "slot_distance_dist_random.png",
        mean_mc, "tilfeldig tildeling",
    )
    plot_heatmap(
        enriched, slots, history,
        OUTPUT_DIR / "slot_heatmap_random.png",
        "Tilfeldig tildeling: plukkfrekvens per celle",
    )

    print("\nFerdig med steg 3.\n")


if __name__ == "__main__":
    main()
