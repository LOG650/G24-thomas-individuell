"""
Steg 2: Feature engineering
===========================
Bygger de eksogene (X)-variablene som ARIMAX skal få tilgang til:

  x_kampanje   : binær indikator, 1 når dagen er kampanjedag
  x_rabatt     : rabattprosent (0 dersom ingen kampanje)
  x_foer_1     : 1 dagen rett før kampanjestart   (pre-buying dip)
  x_foer_2     : 1 to dager før kampanjestart
  x_etter_1    : 1 dagen etter kampanjeslutt       (post-campaign dip)
  x_etter_2    : 1 to dager etter kampanjeslutt
  x_etter_3    : 1 tre dager etter kampanjeslutt

Ukedags-dummier håndteres implisitt av SARIMAX gjennom sesongkomponent;
vi lar derfor ukesesongen ligge i ARIMA-delen (sesonglag 7).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import generate_raw_data

EXOG_COLS = [
    "x_kampanje",
    "x_rabatt",
    "x_foer_1",
    "x_foer_2",
    "x_etter_1",
    "x_etter_2",
    "x_etter_3",
]


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Bygg alle feature-kolonner og returner utvidet DataFrame."""
    out = df.copy()
    n = len(out)
    camp = out["kampanje"].values
    disc = out["rabatt"].values

    out["x_kampanje"] = camp.astype(int)
    out["x_rabatt"] = disc

    # Finn kampanjestart og -slutt
    starts, ends = [], []
    for i in range(n):
        if camp[i] == 1 and (i == 0 or camp[i - 1] == 0):
            starts.append(i)
        if camp[i] == 1 and (i == n - 1 or camp[i + 1] == 0):
            ends.append(i)

    for col in ["x_foer_1", "x_foer_2", "x_etter_1", "x_etter_2", "x_etter_3"]:
        out[col] = 0

    for s in starts:
        if s - 1 >= 0 and camp[s - 1] == 0:
            out.iat[s - 1, out.columns.get_loc("x_foer_1")] = 1
        if s - 2 >= 0 and camp[s - 2] == 0:
            out.iat[s - 2, out.columns.get_loc("x_foer_2")] = 1

    for e in ends:
        if e + 1 < n and camp[e + 1] == 0:
            out.iat[e + 1, out.columns.get_loc("x_etter_1")] = 1
        if e + 2 < n and camp[e + 2] == 0:
            out.iat[e + 2, out.columns.get_loc("x_etter_2")] = 1
        if e + 3 < n and camp[e + 3] == 0:
            out.iat[e + 3, out.columns.get_loc("x_etter_3")] = 1

    return out


def plot_feature_example(df: pd.DataFrame, output_path: Path,
                          window: tuple[int, int] = (115, 140)) -> None:
    """Plott et vindu rundt én kampanje som illustrerer feature-utvidelsen."""
    lo, hi = window
    sub = df[(df["t"] >= lo) & (df["t"] <= hi)].copy()

    fig, axes = plt.subplots(2, 1, figsize=(11, 6), sharex=True,
                             gridspec_kw={"height_ratios": [2.2, 1.4]})

    ax1 = axes[0]
    ax1.plot(sub["t"], sub["salg"], "o-", color="#1F6587", linewidth=1.2,
             markersize=4.5, label="Salg $Y_t$")

    # Marker kampanjedager
    camp_days = sub[sub["x_kampanje"] == 1]
    ax1.scatter(camp_days["t"], camp_days["salg"], color="#9C540B",
                s=65, zorder=5, label="Kampanjedag")
    foer_days = sub[(sub["x_foer_1"] == 1) | (sub["x_foer_2"] == 1)]
    ax1.scatter(foer_days["t"], foer_days["salg"], color="#5A2C77",
                s=45, zorder=5, marker="s", label="Før-kampanje")
    etter_days = sub[(sub["x_etter_1"] == 1) | (sub["x_etter_2"] == 1)
                     | (sub["x_etter_3"] == 1)]
    ax1.scatter(etter_days["t"], etter_days["salg"], color="#307453",
                s=45, zorder=5, marker="^", label="Etter-kampanje")

    ax1.set_ylabel("$Y_t$", fontsize=13, rotation=0, labelpad=14)
    ax1.grid(True, alpha=0.3)
    ax1.legend(loc="upper right", fontsize=9, ncol=2)
    ax1.set_title("Feature engineering: kampanjen t = 120--124 med omkringliggende dager",
                  fontsize=11, fontweight="bold")

    ax2 = axes[1]
    features = ["x_kampanje", "x_rabatt", "x_foer_1", "x_foer_2",
                "x_etter_1", "x_etter_2", "x_etter_3"]
    colors = ["#1F6587", "#9C540B", "#5A2C77", "#5A2C77",
              "#307453", "#307453", "#307453"]
    # Plott feature-verdiene som heatmap-aktige søyler (én rad per feature)
    for row, (feat, c) in enumerate(zip(features, colors)):
        vals = sub[feat].values.astype(float)
        if feat == "x_rabatt":
            norm = vals / max(vals.max(), 1)
        else:
            norm = vals
        ax2.bar(sub["t"], norm, bottom=row, color=c, alpha=0.75, width=1.0,
                edgecolor="white", linewidth=0.3)
    ax2.set_yticks(np.arange(len(features)) + 0.5)
    ax2.set_yticklabels(features, fontsize=9)
    ax2.set_xlabel("$t$ (dag)", fontsize=12)
    ax2.set_xlim(lo - 0.5, hi + 0.5)
    ax2.set_ylim(0, len(features))
    ax2.grid(False)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def summarise_features(df: pd.DataFrame) -> dict:
    """Sammendrag av feature-kolonnene."""
    summary = {}
    for col in EXOG_COLS:
        summary[col] = {
            "antall_1": int((df[col] > 0).sum()),
            "min": float(df[col].min()),
            "max": float(df[col].max()),
        }
    return summary


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 2: FEATURE ENGINEERING")
    print(f"{'=' * 60}")

    df = generate_raw_data()
    df_feat = build_features(df)

    summary = summarise_features(df_feat)
    print("\n--- Feature-sammendrag ---")
    for col, d in summary.items():
        print(f"  {col:12s}  antall_aktive={d['antall_1']:>4d}  "
              f"min={d['min']:.1f}  max={d['max']:.1f}")

    feat_path = output_dir / "features.csv"
    df_feat.to_csv(feat_path, index=False, encoding="utf-8")
    print(f"\nFeatures lagret: {feat_path}")

    with open(output_dir / "feature_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_feature_example(df_feat, output_dir / "arimax_features.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(
        "  Vi har konstruert 7 eksogene variabler som beskriver\n"
        "  kampanjen (binær + rabatt %) og kampanjens omland (pre-buying\n"
        "  2 dager før, post-campaign 3 dager etter). Disse mates inn i\n"
        "  SARIMAX(..., exog=X) i Steg 4."
    )


if __name__ == "__main__":
    main()
