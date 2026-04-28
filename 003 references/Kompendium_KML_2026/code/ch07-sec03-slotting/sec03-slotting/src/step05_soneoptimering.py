r"""
Steg 5: Antall soner og effekten av klassegranularitet
=======================================================
Class-based storage tildeler ikke en slot per SKU, men derimot en
\emph{sone} per klasse. Innenfor en sone plasseres SKU-er ofte uten
videre rangering (de alle faar en ``random'' plass innen sin sone).
Dette gir en enklere lagerpolitikk -- en ny SKU kan settes hvor som
helst i sin tildelte sone -- men gir hoyere forventet reisedistanse
enn en full frekvensbasert sortering.

Vi undersoker to spoersmaal:

1. Hvor mye taper vi paa aa bruke sonegruppering istedenfor en
   fullstendig frekvensbasert sortering (continuous assignment)?
2. Hvor mange soner gir best avveining mellom enkelhet og effektivitet?

For hvert antall soner K in {2, 3, 4, 5, 10, 20} deler vi slots i K
like grupper etter distanse, og innenfor hver sone plasserer vi de
SKU-ene som hoerer til klassen i tilfeldig rekkefolge. Vi gjentar dette
med flere tilfeldige frø for aa fange gjennomsnittseffekten.
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
from step03_tilfeldig_baseline import (
    attach_distance,
    expected_distance,
    monte_carlo_distance,
    plot_heatmap,
)


def zone_based_assignment(
    slots: pd.DataFrame, sku_history: pd.DataFrame,
    n_zones: int, seed: int = 0,
) -> pd.DataFrame:
    """Deler slots i n_zones like store soner etter distanse. SKU-ene
    sorteres etter plukkfrekvens og fordeles paa tvers av sonene i
    synkende rekkefoelge: de n_sku/n_zones mest plukkede gaar i sone 1,
    de neste i sone 2, osv. Innenfor en sone plasseres SKU-ene i
    \emph{tilfeldig} rekkefoelge paa de respektive slottene.
    """
    rng = np.random.default_rng(seed)
    sorted_slots = slots.sort_values("d_round_trip").reset_index(drop=True)
    sorted_skus = sku_history.sort_values(
        "plukk_90d", ascending=False
    ).reset_index(drop=True)

    n_slots = len(sorted_slots)
    n_sku = len(sorted_skus)
    # Del slots inn i n_zones omtrent like store grupper
    slot_bounds = np.linspace(0, n_slots, n_zones + 1, dtype=int)
    sku_bounds = np.linspace(0, n_sku, n_zones + 1, dtype=int)

    rows = []
    for z in range(n_zones):
        zone_slots = sorted_slots.iloc[slot_bounds[z]: slot_bounds[z + 1]]
        zone_skus = sorted_skus.iloc[sku_bounds[z]: sku_bounds[z + 1]]
        # Randomiser SKU-rekkefolgen innenfor sonen
        permuted = zone_skus.sample(
            frac=1.0, random_state=seed + z
        ).reset_index(drop=True)
        # Ta minimumet for aa unngaa indeksproblemer
        k = min(len(zone_slots), len(permuted))
        for i in range(k):
            rows.append(
                {
                    "sku_id": permuted.iloc[i]["sku_id"],
                    "slot_id": zone_slots.iloc[i]["slot_id"],
                    "sone": z + 1,
                }
            )
    return pd.DataFrame(rows)


def continuous_assignment(
    slots: pd.DataFrame, sku_history: pd.DataFrame,
) -> pd.DataFrame:
    """Full frekvensbasert sortering: n_sku-te SKU faar n-te naermeste slot."""
    sorted_slots = slots.sort_values("d_round_trip").reset_index(drop=True)
    sorted_skus = sku_history.sort_values(
        "plukk_90d", ascending=False
    ).reset_index(drop=True)
    n = len(sorted_skus)
    assignment = pd.DataFrame(
        {
            "sku_id": sorted_skus["sku_id"].values,
            "slot_id": sorted_slots["slot_id"].values[:n],
        }
    )
    return assignment


def evaluate(
    slots: pd.DataFrame, sku_history: pd.DataFrame, n_zones: int,
    n_trials: int = 30,
) -> dict:
    """Gjentar tilfeldig sonetildeling n_trials ganger og returnerer
    gjennomsnittlig forventet distanse.
    """
    distances = []
    for trial in range(n_trials):
        assignment = zone_based_assignment(
            slots, sku_history, n_zones, seed=1000 + trial,
        )
        merged = assignment.merge(
            slots[["slot_id", "d_round_trip"]], on="slot_id"
        ).merge(
            sku_history[["sku_id", "plukk_90d"]], on="sku_id"
        )
        e = float(
            (merged["d_round_trip"] * merged["plukk_90d"]).sum()
            / merged["plukk_90d"].sum()
        )
        distances.append(e)
    return {
        "n_zones": int(n_zones),
        "mean_e_distance_m": round(float(np.mean(distances)), 3),
        "std_e_distance_m": round(float(np.std(distances)), 3),
        "min_e_distance_m": round(float(np.min(distances)), 3),
        "max_e_distance_m": round(float(np.max(distances)), 3),
    }


def plot_zone_profile(
    results: pd.DataFrame, continuous_e: float,
    random_e: float, output_path: Path,
) -> None:
    """Viser forventet distanse som funksjon av antall soner."""
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.errorbar(
        results["n_zones"], results["mean_e_distance_m"],
        yerr=results["std_e_distance_m"],
        marker="o", color=PRIMARY, lw=2, capsize=4,
        label="Sonebasert (gj.snitt ± 1 std)",
    )
    ax.axhline(random_e, color=S_DARKS[4], ls="--", lw=1.5,
               label=f"Tilfeldig ({random_e:.1f} m)")
    ax.axhline(continuous_e, color=S_DARKS[1], ls=":", lw=1.5,
               label=f"Full sortering ({continuous_e:.1f} m)")
    ax.set_xlabel("Antall soner $K$", fontsize=11)
    ax.set_ylabel("Forventet distanse per plukk (m)", fontsize=11)
    ax.set_title(
        "Effekten av soneantall paa forventet reisedistanse",
        fontsize=12, fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 5: SONEOPTIMERING (antall soner)")
    print("=" * 60)

    slots = pd.read_csv(DATA_DIR / "slots.csv")
    history = pd.read_csv(DATA_DIR / "plukkhistorikk.csv")

    # 1. Kontinuerlig (fullstendig sortering) -- optimal innenfor layouten
    cont = continuous_assignment(slots, history)
    cont_enriched = attach_distance(cont, slots, history)
    cont_e = expected_distance(cont_enriched)
    print(f"Kontinuerlig (full sortering) E[d] = {cont_e:.2f} m")

    # 2. Tilfeldig (samme rutine som step03 for direkte sammenligning)
    rng_state = 12345
    rng = np.random.default_rng(rng_state)
    slot_ids = np.array(slots["slot_id"].tolist(), dtype=object)
    rng.shuffle(slot_ids)
    random_assignment = pd.DataFrame(
        {
            "sku_id": history["sku_id"].values,
            "slot_id": slot_ids[: len(history)],
        }
    )
    random_enriched = attach_distance(random_assignment, slots, history)
    random_e = expected_distance(random_enriched)
    print(f"Tilfeldig E[d] = {random_e:.2f} m")

    # 3. Evaluer ulike soneantall
    zone_counts = [2, 3, 4, 5, 10, 20]
    rows = []
    for k in zone_counts:
        res = evaluate(slots, history, k, n_trials=30)
        res["reduksjon_vs_tilfeldig_pct"] = round(
            (random_e - res["mean_e_distance_m"]) / random_e * 100, 1
        )
        res["gap_vs_kontinuerlig_pct"] = round(
            (res["mean_e_distance_m"] - cont_e) / cont_e * 100, 1
        )
        rows.append(res)
        print(f"  K={k}: E[d] = {res['mean_e_distance_m']:.2f} m "
              f"(red. {res['reduksjon_vs_tilfeldig_pct']:.1f}%, "
              f"gap {res['gap_vs_kontinuerlig_pct']:.1f}%)")

    zone_df = pd.DataFrame(rows)
    zone_df.to_csv(OUTPUT_DIR / "step05_zone_results.csv", index=False)

    # 4. Valgte tre-soners politikk som den vi tar videre
    three_zone = zone_df[zone_df["n_zones"] == 3].iloc[0]
    print(f"\nValgt politikk: K=3, E[d] = "
          f"{three_zone['mean_e_distance_m']:.2f} m")

    # Tildeling for K=3 og bruk en tilfeldig plassering i tillegg
    three_zone_assignment = zone_based_assignment(
        slots, history, n_zones=3, seed=7,
    )
    three_zone_assignment.to_csv(
        DATA_DIR / "tildeling_3zone.csv", index=False,
    )
    enriched = attach_distance(three_zone_assignment, slots, history)
    mc = monte_carlo_distance(enriched, seed=2029)
    mean_mc = float(mc.mean())
    median_mc = float(np.median(mc))
    p95_mc = float(np.percentile(mc, 95))

    summary = {
        "metode": "K3-sonebasert",
        "n_zones": 3,
        "E_kontinuerlig_m": round(cont_e, 2),
        "E_tilfeldig_m": round(random_e, 2),
        "E_sonebasert_mean_m": round(float(three_zone["mean_e_distance_m"]),
                                     2),
        "mc_gjennomsnitt_m": round(mean_mc, 2),
        "mc_median_m": round(median_mc, 2),
        "mc_p95_m": round(p95_mc, 2),
        "mc_std_m": round(float(mc.std()), 2),
        "samples": len(mc),
        "reduksjon_vs_tilfeldig_pct": round(
            (random_e - mean_mc) / random_e * 100, 1
        ),
        "gap_vs_kontinuerlig_pct": round(
            (mean_mc - cont_e) / cont_e * 100, 1
        ),
    }
    with open(OUTPUT_DIR / "step05_optimert_summary.json", "w",
              encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    np.save(OUTPUT_DIR / "mc_distances_optimert.npy", mc)

    plot_zone_profile(
        zone_df, cont_e, random_e,
        OUTPUT_DIR / "slot_zone_profile.png",
    )
    plot_heatmap(
        enriched, slots, history,
        OUTPUT_DIR / "slot_heatmap_optimert.png",
        "K=3 sonebasert tildeling: plukkfrekvens per celle",
    )

    print("\nFerdig med steg 5.\n")


if __name__ == "__main__":
    main()
