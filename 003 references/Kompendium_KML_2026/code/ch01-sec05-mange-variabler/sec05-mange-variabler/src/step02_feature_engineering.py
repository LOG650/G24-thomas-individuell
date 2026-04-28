"""
Steg 2: Feature engineering for LightGBM
========================================
Bygger 100+ features fra SKU-panelet og værdata:
- Lag-features per SKU (salg t-1, t-7, t-14, t-28)
- Rullerende statistikk (gjennomsnitt, std, maks, min)
- Kalenderfeatures (ukedag, måned, helligdag, jul, uke)
- Priselastisitet (pris_endring, relativ pris)
- Produktfeatures (kategori, merke, butikk - encoded)
- Værfeatures (temperatur, nedbør, solskinn)
- Kampanjefeatures (kampanje-flag, rabatt_pct, pre/post-flag)
- Interaksjoner (kampanje x ukedag, temp x kategori)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Last inn panel, SKU-katalog og værdata."""
    data_dir = Path(__file__).parent.parent / "data"
    panel = pd.read_csv(data_dir / "sales_panel.csv", parse_dates=["dato"])
    sku = pd.read_csv(data_dir / "sku_catalog.csv")
    weather = pd.read_csv(data_dir / "weather.csv", parse_dates=["dato"])
    return panel, sku, weather


def add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    """Legg til kalendervariabler."""
    d = df["dato"]
    df["ukedag"] = d.dt.dayofweek
    df["er_helg"] = (df["ukedag"] >= 5).astype(np.int8)
    df["maaned"] = d.dt.month
    df["kvartal"] = d.dt.quarter
    df["uke"] = d.dt.isocalendar().week.astype(int)
    df["dag_i_maaned"] = d.dt.day
    df["er_manedsslutt"] = (d.dt.day >= 25).astype(np.int8)
    df["er_manedsstart"] = (d.dt.day <= 5).astype(np.int8)
    df["aar"] = d.dt.year
    # Sin/cos-koder for ukedag og måned
    df["ukedag_sin"] = np.sin(2 * np.pi * df["ukedag"] / 7)
    df["ukedag_cos"] = np.cos(2 * np.pi * df["ukedag"] / 7)
    df["maaned_sin"] = np.sin(2 * np.pi * df["maaned"] / 12)
    df["maaned_cos"] = np.cos(2 * np.pi * df["maaned"] / 12)
    # Helligdag og jul
    df["helligdag"] = (
        ((df["maaned"] == 1) & (df["dag_i_maaned"] == 1))
        | ((df["maaned"] == 5) & (df["dag_i_maaned"] == 1))
        | ((df["maaned"] == 5) & (df["dag_i_maaned"] == 17))
        | ((df["maaned"] == 12) & (df["dag_i_maaned"] == 25))
        | ((df["maaned"] == 12) & (df["dag_i_maaned"] == 26))
    ).astype(np.int8)
    christmas_this = pd.to_datetime(df["aar"].astype(str) + "-12-24")
    christmas_next = pd.to_datetime((df["aar"] + 1).astype(str) + "-12-24")
    delta_this = (christmas_this - df["dato"]).dt.days
    delta_next = (christmas_next - df["dato"]).dt.days
    df["dager_til_jul"] = np.where(delta_this >= 0, delta_this, delta_next)
    df["jul_nar"] = (df["dager_til_jul"] <= 7).astype(np.int8)
    return df


def add_lag_features(df: pd.DataFrame, lags: list[int]) -> pd.DataFrame:
    """Legg til lag-features av salg per SKU."""
    df = df.sort_values(["sku_id", "t"]).copy()
    for lag in lags:
        df[f"salg_lag_{lag}"] = df.groupby("sku_id")["salg"].shift(lag)
    return df


def add_rolling_features(df: pd.DataFrame, windows: list[int]) -> pd.DataFrame:
    """Legg til rullerende statistikk (shift(1) så vi ikke lekker fremtid)."""
    df = df.sort_values(["sku_id", "t"]).copy()
    shifted = df.groupby("sku_id")["salg"].shift(1)
    for w in windows:
        df[f"salg_rullmean_{w}"] = (
            shifted.groupby(df["sku_id"]).rolling(w, min_periods=1).mean().reset_index(level=0, drop=True)
        )
        df[f"salg_rullstd_{w}"] = (
            shifted.groupby(df["sku_id"]).rolling(w, min_periods=2).std().reset_index(level=0, drop=True)
        )
        df[f"salg_rullmax_{w}"] = (
            shifted.groupby(df["sku_id"]).rolling(w, min_periods=1).max().reset_index(level=0, drop=True)
        )
        df[f"salg_rullmin_{w}"] = (
            shifted.groupby(df["sku_id"]).rolling(w, min_periods=1).min().reset_index(level=0, drop=True)
        )
        df[f"salg_rullmed_{w}"] = (
            shifted.groupby(df["sku_id"]).rolling(w, min_periods=1).median().reset_index(level=0, drop=True)
        )
        df[f"salg_rullsum_{w}"] = (
            shifted.groupby(df["sku_id"]).rolling(w, min_periods=1).sum().reset_index(level=0, drop=True)
        )
    # Ratio- og momentumfeatures
    if "salg_rullmean_7" in df.columns and "salg_rullmean_28" in df.columns:
        df["salg_mom_7_28"] = df["salg_rullmean_7"] / df["salg_rullmean_28"].replace(0, np.nan)
    if "salg_rullstd_7" in df.columns and "salg_rullmean_7" in df.columns:
        df["salg_cv_7"] = df["salg_rullstd_7"] / df["salg_rullmean_7"].replace(0, np.nan)
    if "salg_rullstd_28" in df.columns and "salg_rullmean_28" in df.columns:
        df["salg_cv_28"] = df["salg_rullstd_28"] / df["salg_rullmean_28"].replace(0, np.nan)
    return df


def add_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Pris-relaterte features."""
    df["rel_pris"] = df["pris"] / df["basispris"]
    df["prisendring"] = 1 - df["rel_pris"]  # Rabatt som fraksjon
    df = df.sort_values(["sku_id", "t"]).copy()
    df["pris_lag_1"] = df.groupby("sku_id")["pris"].shift(1)
    df["pris_endring_1d"] = (df["pris"] - df["pris_lag_1"]) / df["basispris"]
    df["pris_rullmean_7"] = (
        df.groupby("sku_id")["pris"].shift(1).groupby(df["sku_id"])
        .rolling(7, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    return df


def add_weather_features(df: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Koble på værdata."""
    df = df.merge(weather, on="dato", how="left")
    df["temp_varm"] = (df["temperatur"] > 20).astype(np.int8)
    df["temp_kald"] = (df["temperatur"] < 0).astype(np.int8)
    df["regn"] = (df["nedbor"] > 3).astype(np.int8)
    df["solskinn_hoy"] = (df["solskinn"] > 8).astype(np.int8)
    return df


def add_campaign_features(df: pd.DataFrame) -> pd.DataFrame:
    """Kampanje-flag, pre/post-flag per SKU."""
    df = df.sort_values(["sku_id", "t"]).copy()
    df["kamp_lag_1"] = df.groupby("sku_id")["kampanje"].shift(1).fillna(0).astype(np.int8)
    df["kamp_lag_2"] = df.groupby("sku_id")["kampanje"].shift(2).fillna(0).astype(np.int8)
    df["kamp_lag_7"] = df.groupby("sku_id")["kampanje"].shift(7).fillna(0).astype(np.int8)
    df["kamp_neste_1"] = df.groupby("sku_id")["kampanje"].shift(-1).fillna(0).astype(np.int8)
    df["kamp_neste_2"] = df.groupby("sku_id")["kampanje"].shift(-2).fillna(0).astype(np.int8)
    df["pre_kamp"] = ((df["kampanje"] == 0) & (df["kamp_neste_1"] == 1)).astype(np.int8)
    df["pre_kamp_2"] = ((df["kampanje"] == 0) & (df["kamp_neste_2"] == 1)).astype(np.int8)
    df["post_kamp"] = ((df["kampanje"] == 0) & (df["kamp_lag_1"] == 1)).astype(np.int8)
    df["post_kamp_2"] = ((df["kampanje"] == 0) & (df["kamp_lag_2"] == 1)).astype(np.int8)
    # Rullerende kampanjeandel siste 28 dager per SKU
    shifted_kamp = df.groupby("sku_id")["kampanje"].shift(1)
    df["kamp_andel_28"] = (
        shifted_kamp.groupby(df["sku_id"])
        .rolling(28, min_periods=1).mean().reset_index(level=0, drop=True)
    )
    df["rabatt_x_helg"] = df["rabatt_pct"] * (df["ukedag"] >= 5).astype(int)
    df["kamp_x_varm"] = df["kampanje"] * ((df["temperatur"] > 20).astype(int) if "temperatur" in df.columns else 0)
    df["kamp_x_jul"] = df["kampanje"] * df["jul_nar"].astype(int) if "jul_nar" in df.columns else 0
    df["rabatt_pct_sq"] = df["rabatt_pct"] ** 2
    return df


def add_category_encoding(df: pd.DataFrame) -> pd.DataFrame:
    """Label-encode kategoriske variabler for LightGBM."""
    for col in ["kategori", "merke", "butikk", "sku_id"]:
        df[f"{col}_kode"] = pd.Categorical(df[col]).codes.astype(np.int32)
    return df


def add_sku_level_features(df: pd.DataFrame) -> pd.DataFrame:
    """Per-SKU historiske features (tren-leak-fri: beregnet over shift(1))."""
    df = df.sort_values(["sku_id", "t"]).copy()
    shifted = df.groupby("sku_id")["salg"].shift(1)
    df["sku_tidl_mean"] = (
        shifted.groupby(df["sku_id"]).expanding(min_periods=7).mean().reset_index(level=0, drop=True)
    )
    df["sku_tidl_std"] = (
        shifted.groupby(df["sku_id"]).expanding(min_periods=7).std().reset_index(level=0, drop=True)
    )
    df["sku_tidl_maks"] = (
        shifted.groupby(df["sku_id"]).expanding(min_periods=7).max().reset_index(level=0, drop=True)
    )
    # Ukedag-gjennomsnitt per SKU (leak-fritt: shift 7, så forrige uke samme dag)
    df["sku_ukedag_mean_4uk"] = (
        df.groupby(["sku_id", "ukedag"])["salg"].shift(1)
        .groupby([df["sku_id"], df["ukedag"]]).rolling(4, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
    )
    df["sku_ukedag_mean_8uk"] = (
        df.groupby(["sku_id", "ukedag"])["salg"].shift(1)
        .groupby([df["sku_id"], df["ukedag"]]).rolling(8, min_periods=1).mean().reset_index(level=[0, 1], drop=True)
    )
    return df


def add_category_aggregates(df: pd.DataFrame) -> pd.DataFrame:
    """Kategori- og merke-gjennomsnittlig salg (leak-fri aggregat av tidligere dager)."""
    df = df.sort_values(["t", "sku_id"]).copy()
    # For hver (kategori, dato) bruk gjennomsnittet av salg 1 dag og 7 dager før
    for lag in [1, 7]:
        key = f"salg_lag_{lag}"
        if key in df.columns:
            df[f"kat_mean_lag_{lag}"] = df.groupby(["kategori", "t"])[key].transform("mean")
            df[f"merke_mean_lag_{lag}"] = df.groupby(["merke", "t"])[key].transform("mean")
    return df


def build_features(panel: pd.DataFrame, weather: pd.DataFrame) -> pd.DataFrame:
    """Bygg full feature-matrise."""
    df = panel.copy()
    df = add_calendar_features(df)
    df = add_lag_features(df, lags=[1, 2, 3, 7, 14, 21, 28])
    df = add_rolling_features(df, windows=[7, 14, 28])
    df = add_price_features(df)
    df = add_weather_features(df, weather)
    df = add_campaign_features(df)
    df = add_sku_level_features(df)
    df = add_category_aggregates(df)
    df = add_category_encoding(df)
    return df


def plot_feature_correlation(df: pd.DataFrame, output_path: Path) -> None:
    """Plott korrelasjon mellom utvalgte numeriske features og salg."""
    num_cols = [
        "salg_lag_1", "salg_lag_7", "salg_rullmean_7", "salg_rullmean_28",
        "rabatt_pct", "kampanje", "ukedag", "temperatur", "nedbor",
        "rel_pris", "pre_kamp", "post_kamp", "lager", "helligdag",
    ]
    corrs = []
    for c in num_cols:
        if c in df.columns:
            v = df[[c, "salg"]].dropna().corr().iloc[0, 1]
            corrs.append((c, v))
    corrs.sort(key=lambda x: abs(x[1]), reverse=True)

    labels = [x[0] for x in corrs]
    vals = [x[1] for x in corrs]
    colors = ["#1F6587" if v > 0 else "#9C540B" for v in vals]

    fig, ax = plt.subplots(figsize=(9, 5.5))
    ax.barh(labels, vals, color=colors, edgecolor="#1F2933")
    ax.axvline(0, color="#1F2933", linewidth=0.6)
    ax.set_xlabel("Korrelasjon med salg", fontsize=11)
    ax.set_title("Utvalgte features: korrelasjon med daglig salg",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_feature_groups(counts: dict, output_path: Path) -> None:
    """Plott antall features per gruppe."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    groups = list(counts.keys())
    vals = list(counts.values())
    palette = [
        "#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7",
        "#ED9F9E", "#1F6587", "#307453",
    ]
    ax.barh(groups, vals, color=palette[:len(groups)], edgecolor="#1F2933")
    for i, v in enumerate(vals):
        ax.text(v + 0.3, i, str(v), va="center", fontsize=10)
    ax.set_xlabel("Antall features", fontsize=11)
    ax.set_title("Feature engineering: antall features per gruppe",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    ax.invert_yaxis()
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

    panel, sku, weather = load_data()
    df = build_features(panel, weather)
    print(f"\nFeature-matrise: {df.shape[0]:,} rader x {df.shape[1]} kolonner")

    # Gruppér features for rapportering
    lag_feats = [c for c in df.columns if c.startswith("salg_lag_")]
    rull_feats = [c for c in df.columns if "rull" in c] + [c for c in df.columns
                                                            if c in ("salg_mom_7_28", "salg_cv_7", "salg_cv_28")]
    cal_feats = ["ukedag", "er_helg", "maaned", "kvartal", "uke", "dag_i_maaned",
                 "er_manedsstart", "er_manedsslutt", "aar", "ukedag_sin",
                 "ukedag_cos", "maaned_sin", "maaned_cos", "helligdag",
                 "dager_til_jul", "jul_nar"]
    pris_feats = ["pris", "basispris", "rel_pris", "prisendring", "pris_lag_1",
                  "pris_endring_1d", "pris_rullmean_7"]
    vaer_feats = ["temperatur", "nedbor", "solskinn", "temp_varm", "temp_kald",
                  "regn", "solskinn_hoy"]
    kamp_feats = ["kampanje", "rabatt_pct", "kamp_lag_1", "kamp_lag_2", "kamp_lag_7",
                  "kamp_neste_1", "kamp_neste_2", "pre_kamp", "pre_kamp_2",
                  "post_kamp", "post_kamp_2", "kamp_andel_28",
                  "rabatt_x_helg", "kamp_x_varm", "kamp_x_jul", "rabatt_pct_sq"]
    prod_feats = ["kategori_kode", "merke_kode", "butikk_kode", "sku_id_kode"]
    sku_feats = ["sku_tidl_mean", "sku_tidl_std", "sku_tidl_maks",
                 "sku_ukedag_mean_4uk", "sku_ukedag_mean_8uk",
                 "lager", "stockout",
                 "kat_mean_lag_1", "kat_mean_lag_7",
                 "merke_mean_lag_1", "merke_mean_lag_7"]

    feature_groups = {
        "Lag-features": len([c for c in lag_feats if c in df.columns]),
        "Rullerende": len([c for c in rull_feats if c in df.columns]),
        "Kalender": len([c for c in cal_feats if c in df.columns]),
        "Pris": len([c for c in pris_feats if c in df.columns]),
        "Vær": len([c for c in vaer_feats if c in df.columns]),
        "Kampanje": len([c for c in kamp_feats if c in df.columns]),
        "Produkt": len([c for c in prod_feats if c in df.columns]),
        "SKU-nivå": len([c for c in sku_feats if c in df.columns]),
    }
    total_features = sum(feature_groups.values())
    print(f"\nAntall features per gruppe:")
    for g, n in feature_groups.items():
        print(f"  {g:15s}: {n:3d}")
    print(f"  {'TOTAL':15s}: {total_features:3d}")

    # Lagre feature-matrise
    feat_path = data_dir / "features.parquet"
    df.to_parquet(feat_path, index=False)
    print(f"\nFeature-matrise lagret: {feat_path}")

    # Lagre feature-liste og gruppering
    all_feature_cols = (lag_feats + rull_feats + cal_feats + pris_feats
                        + vaer_feats + kamp_feats + prod_feats + sku_feats)
    feature_list = [c for c in all_feature_cols if c in df.columns]
    feature_summary = {
        "total": total_features,
        "per_gruppe": feature_groups,
        "features": feature_list,
    }
    with open(output_dir / "feature_summary.json", "w", encoding="utf-8") as f:
        json.dump(feature_summary, f, indent=2, ensure_ascii=False)
    print(f"Feature-liste lagret: {output_dir / 'feature_summary.json'}")

    # Figurer
    plot_feature_correlation(df, output_dir / "lgbm_feature_correlation.png")
    plot_feature_groups(feature_groups, output_dir / "lgbm_feature_groups.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  {total_features} features generert på tvers av 8 grupper.")
    print("  Lag- og rullerende salgs-features dominerer antallet, men "
          "pris-, vær- og kampanjefeatures gir strukturell informasjon "
          "som SARIMA ikke kan utnytte.")


if __name__ == "__main__":
    main()
