"""
Steg 2: Feature engineering for ML-basert lagerklassifisering
=============================================================
Beregner SKU-niva-features som driver klassifiseringen:
- Raw katalog-attributter (volum, pris, lt, etc.)
- Etterspoerselsstatistikk fra transaksjoner (CV, nulldager, trend)
- Rullerende/panel-statistikk (ukentlig volatilitet, peak-ratio)
- Klassiske ABC og XYZ-markoerer (for baseline-sammenligning)
- Kategoriencoding

Figurer:
  mlklasse_feature_overview.png -- korrelasjon av features mot klasse,
                                    og ABC/XYZ-matrise som referanse.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S4 = "#BD94D7"; S4D = "#5A2C77"
S5 = "#ED9F9E"; S5D = "#961D1C"
INK = "#1F2933"


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Last inn katalog, transaksjoner og aggregater."""
    data_dir = Path(__file__).parent.parent / "data"
    catalog = pd.read_csv(data_dir / "sku_catalog.csv")
    master = pd.read_csv(data_dir / "master.csv")
    tx = pd.read_parquet(data_dir / "transactions.parquet")
    return catalog, master, tx


def abc_classify(master: pd.DataFrame) -> pd.Series:
    """Klassisk ABC-klassifisering paa total omsetning (ikke bare salg).
    A = topp 80 %, B = neste 15 %, C = siste 5 %.
    """
    oms = (master["salg_total"] * master["pris"]).rename("omsetning")
    order = oms.sort_values(ascending=False).index
    cum = oms.loc[order].cumsum() / oms.sum()
    abc = pd.Series(index=master.index, dtype=object)
    for idx in order:
        c = cum.loc[idx]
        if c <= 0.80:
            abc.loc[idx] = "A"
        elif c <= 0.95:
            abc.loc[idx] = "B"
        else:
            abc.loc[idx] = "C"
    return abc


def xyz_classify(master: pd.DataFrame) -> pd.Series:
    """Klassisk XYZ-klassifisering paa observert CV.
    X = CV <= 0.5, Y = 0.5 < CV <= 1.0, Z = CV > 1.0.
    """
    cv = master["cv_observert"]
    xyz = pd.Series("Y", index=master.index)
    xyz = xyz.mask(cv <= 0.5, "X")
    xyz = xyz.mask(cv > 1.0, "Z")
    return xyz


def add_demand_panel_features(tx: pd.DataFrame) -> pd.DataFrame:
    """Beregn rike ukentlige statistikker per SKU."""
    tx = tx.copy()
    tx["uke"] = (tx["dato"].dt.isocalendar().year * 100
                 + tx["dato"].dt.isocalendar().week)
    weekly = (tx.groupby(["sku_id", "uke"])["salg"].sum()
              .reset_index()
              .rename(columns={"salg": "ukesalg"}))
    stats = weekly.groupby("sku_id")["ukesalg"].agg(
        uke_gj="mean",
        uke_std="std",
        uke_min="min",
        uke_max="max",
        uke_median="median",
    ).reset_index()
    stats["uke_cv"] = stats["uke_std"] / stats["uke_gj"].replace(0, np.nan)
    stats["uke_cv"] = stats["uke_cv"].fillna(stats["uke_cv"].max())
    stats["peak_ratio"] = stats["uke_max"] / stats["uke_median"].replace(0, np.nan)
    stats["peak_ratio"] = stats["peak_ratio"].replace([np.inf, -np.inf], np.nan).fillna(0.0)

    # Trend (enkel lineaer regresjon paa ukesalg)
    def _trend(g):
        x = np.arange(len(g), dtype=float)
        y = g["ukesalg"].to_numpy(dtype=float)
        if y.std() < 1e-6 or len(y) < 4:
            return 0.0
        return float(np.polyfit(x, y, 1)[0])

    trend = weekly.groupby("sku_id", group_keys=False).apply(
        _trend, include_groups=False).rename("trend_slope")
    trend = trend.reset_index()

    return stats.merge(trend, on="sku_id", how="left")


def build_features(master: pd.DataFrame, tx: pd.DataFrame) -> pd.DataFrame:
    """Bygg full feature-matrise inklusivt ABC/XYZ-markoerer."""
    df = master.copy()

    # Panel-features
    panel = add_demand_panel_features(tx)
    df = df.merge(panel, on="sku_id", how="left")

    # Avledete features
    df["omsetning"] = df["salg_total"] * df["pris"]
    df["log_omsetning"] = np.log1p(df["omsetning"])
    df["log_arsvolum"] = np.log1p(df["arsvolum"])
    df["log_pris"] = np.log1p(df["pris"])
    df["log_holdbarhet"] = np.log1p(df["holdbarhet_dager"])
    df["salg_per_dag_rel"] = df["salg_gj_daglig"] / df["salg_gj_daglig"].max()
    df["lt_x_pris"] = df["leveringstid_dager"] * np.log1p(df["pris"])
    df["subst_lt"] = df["substitusjonsgrad"] * df["leveringstid_dager"]
    df["kampanje_intensitet"] = df["kampanjer_ar"] / 52.0

    # ABC og XYZ
    df["abc"] = abc_classify(df)
    df["xyz"] = xyz_classify(df)
    df["abc_kode"] = df["abc"].map({"A": 0, "B": 1, "C": 2}).astype(int)
    df["xyz_kode"] = df["xyz"].map({"X": 0, "Y": 1, "Z": 2}).astype(int)

    # Kategori-encoding
    df["kategori_kode"] = pd.Categorical(df["kategori"]).codes.astype(int)

    return df


def plot_feature_overview(df: pd.DataFrame, output_path: Path) -> None:
    """Fire-panels oversikt over features og ABC/XYZ-matrise."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 9))
    class_colors = {0: S1D, 1: S2D, 2: S5D}
    fill_colors = {0: S1, 1: S2, 2: S5}
    class_labels = {0: "kontinuerlig", 1: "periodisk", 2: "make-to-order"}

    # Panel 1: boxplot av log_pris per klasse
    ax = axes[0, 0]
    data = [df.loc[df["klasse"] == k, "log_pris"].values for k in [0, 1, 2]]
    bp = ax.boxplot(data, tick_labels=[class_labels[k] for k in [0, 1, 2]],
                    patch_artist=True)
    for patch, k in zip(bp["boxes"], [0, 1, 2]):
        patch.set_facecolor(fill_colors[k])
        patch.set_edgecolor(class_colors[k])
    ax.set_ylabel(r"$\log(1 + \mathrm{pris})$", fontsize=11)
    ax.set_title("Pris per klasse", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel 2: boxplot av leveringstid per klasse
    ax = axes[0, 1]
    data = [df.loc[df["klasse"] == k, "leveringstid_dager"].values for k in [0, 1, 2]]
    bp = ax.boxplot(data, tick_labels=[class_labels[k] for k in [0, 1, 2]],
                    patch_artist=True)
    for patch, k in zip(bp["boxes"], [0, 1, 2]):
        patch.set_facecolor(fill_colors[k])
        patch.set_edgecolor(class_colors[k])
    ax.set_ylabel("Leveringstid (dager)", fontsize=11)
    ax.set_title("Leveringstid per klasse", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel 3: scatter pris vs CV farget etter klasse
    ax = axes[1, 0]
    for k in [0, 1, 2]:
        sub = df[df["klasse"] == k]
        ax.scatter(np.log10(np.clip(sub["pris"], 1, None)),
                   sub["cv_observert"], s=8, alpha=0.4,
                   color=class_colors[k], label=class_labels[k])
    ax.set_xlabel(r"$\log_{10}(\mathrm{pris})$", fontsize=11)
    ax.set_ylabel("Observert CV", fontsize=11)
    ax.set_title("Pris vs variabilitet",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 4: ABC x XYZ-matrise (heatmap)
    ax = axes[1, 1]
    mat = (df.groupby(["abc", "xyz"]).size()
           .unstack(fill_value=0)
           .reindex(index=["A", "B", "C"], columns=["X", "Y", "Z"],
                    fill_value=0))
    im = ax.imshow(mat.values, cmap="Blues", aspect="auto")
    for i in range(3):
        for j in range(3):
            v = mat.values[i, j]
            ax.text(j, i, f"{v:,}", ha="center", va="center",
                    color=INK if v < mat.values.max() / 2 else "white",
                    fontsize=11)
    ax.set_xticks([0, 1, 2], ["X", "Y", "Z"])
    ax.set_yticks([0, 1, 2], ["A", "B", "C"])
    ax.set_xlabel("XYZ (variabilitet)", fontsize=11)
    ax.set_ylabel("ABC (omsetning)", fontsize=11)
    ax.set_title("Klassisk ABC x XYZ-matrise",
                 fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    data_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 2: FEATURE ENGINEERING")
    print(f"{'=' * 60}")

    catalog, master, tx = load_data()
    df = build_features(master, tx)

    # Sett opp eksplisitte feature-kolonner (uten klasse/id)
    exclude = {"sku_id", "kategori", "klasse", "abc", "xyz"}
    feature_cols = [c for c in df.columns if c not in exclude and
                    df[c].dtype.kind in ("i", "f", "u")]

    print(f"\nFeature-matrise: {df.shape[0]:,} SKU-er x {len(feature_cols)} features")
    print("\nFeatures:")
    for f in feature_cols:
        print(f"  {f}")

    # Lagre
    df.to_parquet(data_dir / "features.parquet", index=False)
    with open(output_dir / "feature_cols.json", "w", encoding="utf-8") as f:
        json.dump({
            "feature_cols": feature_cols,
            "n_features": len(feature_cols),
        }, f, indent=2, ensure_ascii=False)

    abc_counts = df["abc"].value_counts().to_dict()
    xyz_counts = df["xyz"].value_counts().to_dict()
    print(f"\nABC-fordeling: {abc_counts}")
    print(f"XYZ-fordeling: {xyz_counts}")

    # Figurer
    plot_feature_overview(df, output_dir / "mlklasse_feature_overview.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  {len(feature_cols)} features bygget fra katalog + transaksjoner.")
    print("  ABC/XYZ markoerer er inkludert som baseline-referanse.")


if __name__ == "__main__":
    main()
