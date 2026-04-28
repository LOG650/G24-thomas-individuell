"""
Steg 4: Frekvensbasert (class-based) tildeling
===============================================
Tildeler SKU-er til slots saa naert pakkestasjonen som mulig gitt deres
klasse:

- A-klasse -> slots med minst rundturs-distanse (``naer sone'')
- B-klasse -> slots med middels rundturs-distanse (``medium sone'')
- C-klasse -> slots med storst rundturs-distanse (``fjern sone'')

Innenfor hver klasse tildeles SKU-ene etter plukkfrekvens: de mest
plukkede faar de naermeste slots innen sin klasse. Klassegrensene
bestemmes av default-verdiene i steg 2 (70/20/10). Steg 5 optimerer
grensene.
"""

import json
from pathlib import Path

import numpy as np
import pandas as pd

from step01_datainnsamling import DATA_DIR, OUTPUT_DIR, S_DARKS, S_FILLS
from step03_tilfeldig_baseline import (
    attach_distance,
    expected_distance,
    monte_carlo_distance,
    plot_distance_histogram,
    plot_heatmap,
)


def class_based_assignment(
    slots: pd.DataFrame, sku_classes: pd.DataFrame, seed: int = 4242,
) -> pd.DataFrame:
    """Tildeler SKU-er til slots basert paa klasse.

    Slots sorteres etter d_round_trip (stigende). SKU-er grupperes i
    klasser A/B/C; A faar de naermeste slots, deretter B, saa C. Innenfor
    hver klasse er tildelingen \\emph{tilfeldig} -- dette reflekterer
    praktisk class-based storage, hvor en ny SKU kan settes hvor som helst
    i sin sone uten videre rangering.
    """
    rng = np.random.default_rng(seed)
    sorted_slots = slots.sort_values("d_round_trip").reset_index(drop=True)

    order = {"A": 0, "B": 1, "C": 2}
    skus = sku_classes.copy()
    skus["klasse_rank"] = skus["klasse"].map(order)
    skus = skus.sort_values("klasse_rank").reset_index(drop=True)

    # Tilfeldig permutasjon innenfor hver klasse
    chunks = []
    for klasse in ["A", "B", "C"]:
        sub = skus[skus["klasse"] == klasse]
        permuted = sub.sample(frac=1.0, random_state=seed).reset_index(
            drop=True
        )
        chunks.append(permuted)
    skus = pd.concat(chunks, ignore_index=True)

    assignment = pd.DataFrame(
        {
            "sku_id": skus["sku_id"].values,
            "klasse": skus["klasse"].values,
            "slot_id": sorted_slots["slot_id"].values[: len(skus)],
        }
    )
    return assignment


def zone_summary(
    assignment: pd.DataFrame, slots: pd.DataFrame, history: pd.DataFrame,
) -> pd.DataFrame:
    """Per-klasse oppsummering av antall slots, plukk og gj. distanse."""
    merged = (
        assignment.merge(slots[["slot_id", "d_round_trip"]], on="slot_id")
        .merge(history[["sku_id", "plukk_90d"]], on="sku_id")
    )
    rows = []
    for klasse in ["A", "B", "C"]:
        sub = merged[merged["klasse"] == klasse]
        total = sub["plukk_90d"].sum()
        if total == 0:
            gj = float("nan")
        else:
            gj = float(
                (sub["d_round_trip"] * sub["plukk_90d"]).sum() / total
            )
        rows.append(
            {
                "klasse": klasse,
                "antall_sku": int(len(sub)),
                "gj_distanse_m": round(gj, 2),
                "min_distanse_m": round(float(sub["d_round_trip"].min()), 2),
                "max_distanse_m": round(float(sub["d_round_trip"].max()), 2),
                "andel_plukk_pct": round(
                    float(total / merged["plukk_90d"].sum() * 100), 1
                ),
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 4: KLASSEBASERT TILDELING")
    print("=" * 60)

    slots = pd.read_csv(DATA_DIR / "slots.csv")
    history = pd.read_csv(DATA_DIR / "plukkhistorikk.csv")
    classes = pd.read_csv(DATA_DIR / "sku_klasser.csv")

    assignment = class_based_assignment(slots, classes)
    assignment.to_csv(DATA_DIR / "tildeling_klassebasert.csv", index=False)

    enriched = attach_distance(assignment, slots, history)
    e_d = expected_distance(enriched)
    print(f"\nForventet distanse per plukk (klassebasert): {e_d:.2f} m")

    mc = monte_carlo_distance(enriched)
    mean_mc = float(mc.mean())
    median_mc = float(np.median(mc))
    p95_mc = float(np.percentile(mc, 95))
    print(f"Monte Carlo gjennomsnitt: {mean_mc:.2f} m")
    print(f"Monte Carlo median: {median_mc:.2f} m")
    print(f"Monte Carlo P95: {p95_mc:.2f} m")

    zones = zone_summary(assignment, slots, history)
    print("\nSoneoppsummering:")
    print(zones.to_string(index=False))
    zones.to_csv(OUTPUT_DIR / "step04_zone_summary.csv", index=False)

    summary = {
        "metode": "klassebasert",
        "analytisk_forventet_m": round(e_d, 2),
        "mc_gjennomsnitt_m": round(mean_mc, 2),
        "mc_median_m": round(median_mc, 2),
        "mc_p95_m": round(p95_mc, 2),
        "mc_std_m": round(float(mc.std()), 2),
        "samples": len(mc),
    }
    with open(OUTPUT_DIR / "step04_classbased_summary.json", "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    np.save(OUTPUT_DIR / "mc_distances_classbased.npy", mc)

    plot_distance_histogram(
        mc, OUTPUT_DIR / "slot_distance_dist_classbased.png",
        mean_mc, "klassebasert tildeling",
    )
    plot_heatmap(
        enriched, slots, history,
        OUTPUT_DIR / "slot_heatmap_classbased.png",
        "Klassebasert tildeling: plukkfrekvens per celle",
    )

    print("\nFerdig med steg 4.\n")


if __name__ == "__main__":
    main()
