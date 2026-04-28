"""
Steg 2: ABC-analyse av plukkfrekvens
=====================================
Klassifiser alle SKU-er i tre klasser basert paa plukkfrekvens:

- A-klasse: de faa hoyfrekvente SKU-ene som representerer ca 70% av plukkene
- B-klasse: moderate SKU-er som representerer ca 20% av plukkene
- C-klasse: de mange lavfrekvente SKU-ene som representerer ca 10%

Klassegrensene er standarden i industrien (70/20/10) som brukes naar
klassegrenser ikke er optimert eksplisitt -- optimalisering av grensene
gjores i steg 5.
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

# Standard klassegrenser (andel av kumulativ plukk)
A_SHARE = 0.70
B_SHARE = 0.90  # A + B


def assign_abc(
    history: pd.DataFrame,
    a_share: float = A_SHARE,
    b_share: float = B_SHARE,
) -> pd.DataFrame:
    """Tildeler hver SKU en klasse A/B/C basert paa kumulativ plukkandel.

    SKU-ene sorteres synkende etter plukk_90d, deretter akkumuleres
    andelen. SKU-er som ligger innenfor de forste `a_share` andelene
    blir A, neste til `b_share` blir B, og resten C.
    """
    sorted_df = history.sort_values("plukk_90d", ascending=False).reset_index(
        drop=True
    )
    total = sorted_df["plukk_90d"].sum()
    sorted_df["kum_andel"] = sorted_df["plukk_90d"].cumsum() / total

    classes = []
    for share in sorted_df["kum_andel"]:
        if share <= a_share:
            classes.append("A")
        elif share <= b_share:
            classes.append("B")
        else:
            classes.append("C")
    sorted_df["klasse"] = classes
    sorted_df["rank"] = np.arange(1, len(sorted_df) + 1)
    return sorted_df


def summarize_classes(df: pd.DataFrame) -> pd.DataFrame:
    """Returner en oppsummeringstabell per klasse."""
    total_plukk = df["plukk_90d"].sum()
    rows = []
    for klasse in ["A", "B", "C"]:
        sub = df[df["klasse"] == klasse]
        if len(sub) == 0:
            rows.append({
                "klasse": klasse, "antall_sku": 0, "andel_sku_pct": 0.0,
                "total_plukk_90d": 0, "andel_plukk_pct": 0.0,
                "min_plukk": 0, "max_plukk": 0, "median_plukk": 0,
            })
            continue
        rows.append(
            {
                "klasse": klasse,
                "antall_sku": int(len(sub)),
                "andel_sku_pct": float(round(len(sub) / len(df) * 100, 1)),
                "total_plukk_90d": int(sub["plukk_90d"].sum()),
                "andel_plukk_pct": float(
                    round(sub["plukk_90d"].sum() / total_plukk * 100, 1)
                ),
                "min_plukk": int(sub["plukk_90d"].min()),
                "max_plukk": int(sub["plukk_90d"].max()),
                "median_plukk": int(sub["plukk_90d"].median()),
            }
        )
    return pd.DataFrame(rows)


def plot_abc_distribution(df: pd.DataFrame, output_path: Path) -> None:
    """Histogram av plukkfrekvens med klassetilhorighet farget."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

    # Panel 1: stablet rank-frekvens
    colors = {"A": S_FILLS[4], "B": S_FILLS[2], "C": S_FILLS[0]}
    edges = {"A": S_DARKS[4], "B": S_DARKS[2], "C": S_DARKS[0]}
    for klasse in ["A", "B", "C"]:
        sub = df[df["klasse"] == klasse]
        ax1.bar(
            sub["rank"], sub["plukk_90d"], color=colors[klasse],
            edgecolor=edges[klasse], linewidth=0.2,
            label=f"Klasse {klasse} (n={len(sub)})",
        )
    ax1.set_xlabel("Rangering (synkende plukkfrekvens)", fontsize=11)
    ax1.set_ylabel("Plukklinjer, 90 dager", fontsize=11)
    ax1.set_title("Plukkfrekvens per SKU med klassetilhorighet",
                  fontsize=12, fontweight="bold")
    ax1.grid(True, alpha=0.3, axis="y")
    ax1.legend(loc="upper right", fontsize=10)

    # Panel 2: summary per klasse
    summary = summarize_classes(df)
    x = np.arange(len(summary))
    width = 0.38
    ax2.bar(
        x - width / 2, summary["andel_sku_pct"], width,
        color=S_FILLS[0], edgecolor=S_DARKS[0],
        label="Andel SKU-er (%)",
    )
    ax2.bar(
        x + width / 2, summary["andel_plukk_pct"], width,
        color=S_FILLS[4], edgecolor=S_DARKS[4],
        label="Andel plukk (%)",
    )
    for i, row in summary.iterrows():
        ax2.text(i - width / 2, row["andel_sku_pct"] + 1.5,
                 f"{row['andel_sku_pct']:.1f}", ha="center",
                 fontsize=9, color=S_DARKS[0])
        ax2.text(i + width / 2, row["andel_plukk_pct"] + 1.5,
                 f"{row['andel_plukk_pct']:.1f}", ha="center",
                 fontsize=9, color=S_DARKS[4])
    ax2.set_xticks(x)
    ax2.set_xticklabels(summary["klasse"], fontsize=11)
    ax2.set_ylabel("Prosent", fontsize=11)
    ax2.set_title("ABC-klasser: andel SKU vs andel plukk",
                  fontsize=12, fontweight="bold")
    ax2.grid(True, alpha=0.3, axis="y")
    ax2.legend(loc="upper right", fontsize=10)
    ax2.set_ylim(0, max(summary["andel_sku_pct"].max(),
                        summary["andel_plukk_pct"].max()) * 1.15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 2: ABC-ANALYSE")
    print("=" * 60)

    history = pd.read_csv(DATA_DIR / "plukkhistorikk.csv")
    classified = assign_abc(history)
    classified.to_csv(DATA_DIR / "sku_klasser.csv", index=False)
    print(f"Klassifiserte {len(classified)} SKU-er.")

    summary = summarize_classes(classified)
    print("\nKlassefordeling:")
    print(summary.to_string(index=False))

    summary_path = OUTPUT_DIR / "step02_abc_summary.json"
    summary.to_json(summary_path, orient="records", indent=2,
                    force_ascii=False)
    print(f"\nSammendrag lagret: {summary_path}")

    plot_abc_distribution(classified, OUTPUT_DIR / "slot_abc.png")

    print("\nFerdig med steg 2.\n")


if __name__ == "__main__":
    main()
