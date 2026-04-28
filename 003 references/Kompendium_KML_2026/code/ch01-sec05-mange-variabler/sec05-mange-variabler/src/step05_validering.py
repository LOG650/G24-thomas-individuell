"""
Steg 5: Modellvalidering og sammenligning mot baselines
=======================================================
Evaluerer LightGBM på testsettet mot:
1. Naiv prognose (samme som forrige uke: y_hat_t = y_{t-7})
2. Glidende gjennomsnitt (28 dagers vindu)
3. SARIMA (per SKU)

Beregner RMSE, MAE og MAPE, og lager sammenligningsfigurer.
"""

from __future__ import annotations

import json
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

warnings.filterwarnings("ignore")


# -----------------------------------------------------------------------------
# Metrics
# -----------------------------------------------------------------------------
def rmse(y, yhat):
    return float(np.sqrt(np.mean((np.asarray(y) - np.asarray(yhat)) ** 2)))


def mae(y, yhat):
    return float(np.mean(np.abs(np.asarray(y) - np.asarray(yhat))))


def mape(y, yhat, eps: float = 0.5):
    y = np.asarray(y, dtype=float)
    yhat = np.asarray(yhat, dtype=float)
    mask = y > eps
    if mask.sum() == 0:
        return float("nan")
    return float(100 * np.mean(np.abs((y[mask] - yhat[mask]) / y[mask])))


# -----------------------------------------------------------------------------
# Baselines
# -----------------------------------------------------------------------------
def naive_forecast(panel: pd.DataFrame, test_start: int) -> pd.DataFrame:
    """Naiv prognose: y_hat(t) = y(t-7) per SKU."""
    panel = panel.sort_values(["sku_id", "t"]).copy()
    panel["naive"] = panel.groupby("sku_id")["salg"].shift(7)
    return panel.loc[panel["t"] >= test_start, ["t", "sku_id", "salg", "naive"]].rename(columns={"naive": "pred"})


def moving_average_forecast(panel: pd.DataFrame, test_start: int,
                            window: int = 28) -> pd.DataFrame:
    """Glidende gjennomsnitt-prognose."""
    panel = panel.sort_values(["sku_id", "t"]).copy()
    panel["ma"] = (
        panel.groupby("sku_id")["salg"].shift(1)
        .groupby(panel["sku_id"]).rolling(window, min_periods=1).mean()
        .reset_index(level=0, drop=True)
    )
    return panel.loc[panel["t"] >= test_start, ["t", "sku_id", "salg", "ma"]].rename(columns={"ma": "pred"})


def sarima_forecast_per_sku(panel: pd.DataFrame, test_start: int,
                            sample_skus: list[str] | None = None) -> pd.DataFrame:
    """SARIMA(1,1,1)(1,0,1)_7 per SKU. Kan være tregt - kjør på utvalg hvis nødvendig."""
    if sample_skus is None:
        sample_skus = panel["sku_id"].unique().tolist()

    preds = []
    for sku in sample_skus:
        sub = panel[panel["sku_id"] == sku].sort_values("t").copy()
        train = sub[sub["t"] < test_start]["salg"].values.astype(float)
        test = sub[sub["t"] >= test_start]
        if len(train) < 60 or len(test) == 0:
            continue
        try:
            mdl = SARIMAX(train, order=(1, 1, 1), seasonal_order=(1, 0, 1, 7),
                          enforce_stationarity=False, enforce_invertibility=False)
            res = mdl.fit(disp=False, maxiter=50)
            fc = res.forecast(steps=len(test))
            preds.append(pd.DataFrame({
                "t": test["t"].values,
                "sku_id": sku,
                "salg": test["salg"].values,
                "pred": np.asarray(fc).clip(0),
            }))
        except Exception:
            # fall back til gjennomsnitt
            preds.append(pd.DataFrame({
                "t": test["t"].values,
                "sku_id": sku,
                "salg": test["salg"].values,
                "pred": np.full(len(test), float(train[-28:].mean())),
            }))
    if not preds:
        return pd.DataFrame(columns=["t", "sku_id", "salg", "pred"])
    return pd.concat(preds, ignore_index=True)


def lightgbm_forecast(df_features: pd.DataFrame, test_start: int,
                      model_pack: dict) -> pd.DataFrame:
    """LightGBM-prognose på testsettet."""
    test_mask = df_features["t"] >= test_start
    X_test = df_features.loc[test_mask, model_pack["feature_cols"]]
    pred = model_pack["model"].predict(X_test, num_iteration=model_pack["best_iteration"])
    pred = np.asarray(pred).clip(0)
    return pd.DataFrame({
        "t": df_features.loc[test_mask, "t"].values,
        "sku_id": df_features.loc[test_mask, "sku_id"].values,
        "salg": df_features.loc[test_mask, "salg"].values,
        "pred": pred,
    })


# -----------------------------------------------------------------------------
# Aggregering av metrikker
# -----------------------------------------------------------------------------
def evaluate_model(name: str, pred_df: pd.DataFrame) -> dict:
    d = pred_df.dropna(subset=["pred"]).copy()
    return {
        "model": name,
        "n": int(len(d)),
        "rmse": rmse(d["salg"], d["pred"]),
        "mae": mae(d["salg"], d["pred"]),
        "mape": mape(d["salg"], d["pred"]),
    }


# -----------------------------------------------------------------------------
# Figurer
# -----------------------------------------------------------------------------
def plot_model_comparison(results: list[dict], output_path: Path) -> None:
    """Søylediagram som sammenligner RMSE, MAE og MAPE."""
    df = pd.DataFrame(results)
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.5))
    colors = ["#ED9F9E", "#F6BA7C", "#BD94D7", "#97D4B7"]

    for ax, metric, title in zip(axes, ["rmse", "mae", "mape"],
                                 ["RMSE", "MAE", "MAPE (%)"]):
        ax.bar(df["model"], df[metric],
               color=colors[:len(df)], edgecolor="#1F2933")
        for i, v in enumerate(df[metric]):
            ax.text(i, v, f"{v:.2f}", ha="center", va="bottom", fontsize=10)
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_ylabel(title, fontsize=11)
        ax.grid(True, axis="y", alpha=0.3)
        plt.setp(ax.get_xticklabels(), rotation=15, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_predictions_vs_actual(preds: dict, output_path: Path,
                                sample_skus: list[str]) -> None:
    """Plott prediksjoner vs faktisk for noen utvalgte SKU-er."""
    fig, axes = plt.subplots(len(sample_skus), 1, figsize=(12, 2.8 * len(sample_skus)),
                             sharex=True)
    if len(sample_skus) == 1:
        axes = [axes]

    palette = {"LightGBM": "#1F6587", "SARIMA": "#5A2C77",
               "MA(28)": "#307453", "Naiv (t-7)": "#9C540B"}
    for ax, sku in zip(axes, sample_skus):
        # Plot actual
        actual = preds["LightGBM"][preds["LightGBM"]["sku_id"] == sku].sort_values("t")
        ax.plot(actual["t"].values, actual["salg"].values,
                color="#1F2933", linewidth=1.1, label="Faktisk", alpha=0.9)
        for name, df in preds.items():
            sub = df[df["sku_id"] == sku].sort_values("t")
            if len(sub) == 0:
                continue
            ax.plot(sub["t"].values, sub["pred"].values,
                    color=palette.get(name, "#556270"), linewidth=1.0,
                    alpha=0.85, label=name)
        ax.set_title(f"SKU {sku}: prognose vs. faktisk på testsettet",
                     fontsize=11, fontweight="bold")
        ax.set_ylabel("Salg", fontsize=10)
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=9, ncol=5, loc="upper left")
    axes[-1].set_xlabel("$t$ (dag)", fontsize=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_error_distribution(preds: dict, output_path: Path) -> None:
    """Feildistribusjon per modell."""
    fig, ax = plt.subplots(figsize=(10, 5))
    palette = {"LightGBM": "#1F6587", "SARIMA": "#5A2C77",
               "MA(28)": "#307453", "Naiv (t-7)": "#9C540B"}
    for name, df in preds.items():
        errors = df["pred"] - df["salg"]
        errors = errors.dropna()
        ax.hist(errors, bins=50, alpha=0.45, color=palette.get(name, "#556270"),
                label=name, edgecolor="white", linewidth=0.3)
    ax.axvline(0, color="#1F2933", linewidth=0.8)
    ax.set_xlabel("Prognosefeil (prognose − faktisk)", fontsize=12)
    ax.set_ylabel("Antall observasjoner", fontsize=11)
    ax.set_title("Feildistribusjon per modell på testsettet",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 5: MODELLVALIDERING OG SAMMENLIGNING")
    print(f"{'=' * 60}")

    panel = pd.read_csv(data_dir / "sales_panel.csv", parse_dates=["dato"])
    df_feat = pd.read_parquet(data_dir / "features.parquet")
    with open(output_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    test_start = splits["test_start"]

    with open(output_dir / "lgbm_model.pkl", "rb") as f:
        model_pack = pickle.load(f)

    print(f"\nTeststart: t = {test_start}, t_max = {splits['t_max']}")
    print("Genererer prognoser...")

    # 1. Naiv
    print("  - Naiv (t-7)")
    naive_df = naive_forecast(panel, test_start)

    # 2. Glidende gjennomsnitt
    print("  - Glidende gjennomsnitt (28 d)")
    ma_df = moving_average_forecast(panel, test_start, window=28)

    # 3. SARIMA - sample 10 SKU-er for praktiske hastighetsgrunner
    sample_sarima_skus = sorted(panel["sku_id"].unique().tolist())[:10]
    print(f"  - SARIMA(1,1,1)(1,0,1)_7 for {len(sample_sarima_skus)} SKU-er")
    sarima_df = sarima_forecast_per_sku(panel, test_start, sample_sarima_skus)

    # 4. LightGBM
    print("  - LightGBM")
    lgbm_df = lightgbm_forecast(df_feat, test_start, model_pack)

    # Begrens alle prognoser til samme SKU-er for rettferdig sammenligning
    common_skus = (set(naive_df["sku_id"].unique())
                   & set(ma_df["sku_id"].unique())
                   & set(sarima_df["sku_id"].unique())
                   & set(lgbm_df["sku_id"].unique()))
    naive_df_c = naive_df[naive_df["sku_id"].isin(common_skus)].copy()
    ma_df_c = ma_df[ma_df["sku_id"].isin(common_skus)].copy()
    sarima_df_c = sarima_df[sarima_df["sku_id"].isin(common_skus)].copy()
    lgbm_df_c = lgbm_df[lgbm_df["sku_id"].isin(common_skus)].copy()

    results = []
    results.append(evaluate_model("Naiv (t-7)", naive_df_c))
    results.append(evaluate_model("MA(28)", ma_df_c))
    results.append(evaluate_model("SARIMA", sarima_df_c))
    results.append(evaluate_model("LightGBM", lgbm_df_c))

    print(f"\n{'Modell':20s} {'n':>8s} {'RMSE':>10s} {'MAE':>10s} {'MAPE (%)':>10s}")
    print("-" * 60)
    for r in results:
        print(f"{r['model']:20s} {r['n']:>8d} {r['rmse']:>10.3f} {r['mae']:>10.3f} "
              f"{r['mape']:>10.2f}")

    # I tillegg: LightGBM-resultat på hele testsettet (alle 50 SKU-er)
    lgbm_full = evaluate_model("LightGBM (alle)", lgbm_df)
    print(f"\nLightGBM på alle {len(lgbm_df['sku_id'].unique())} SKU-er (hele testsettet):")
    print(f"  RMSE={lgbm_full['rmse']:.3f}, MAE={lgbm_full['mae']:.3f}, "
          f"MAPE={lgbm_full['mape']:.2f} %")

    # Lagre resultatene
    pd.DataFrame(results + [lgbm_full]).to_csv(
        output_dir / "validation_results.csv", index=False)
    with open(output_dir / "validation_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "common_skus_results": results,
            "lgbm_all_skus": lgbm_full,
            "common_skus_count": len(common_skus),
            "test_start": test_start,
            "test_end": splits["t_max"],
        }, f, indent=2, ensure_ascii=False)

    # Lagre prognoser i parquet for senere tolkning
    lgbm_df.to_parquet(output_dir / "lgbm_predictions.parquet", index=False)

    # Figurer
    plot_model_comparison(results, output_dir / "lgbm_model_comparison.png")

    # Velg 3 SKU-er for linjeplot (fra dem SARIMA også dekker)
    plot_skus = list(common_skus)[:3]
    preds = {
        "Naiv (t-7)": naive_df_c,
        "MA(28)": ma_df_c,
        "SARIMA": sarima_df_c,
        "LightGBM": lgbm_df_c,
    }
    plot_predictions_vs_actual(preds, output_dir / "lgbm_forecast.png",
                                sample_skus=plot_skus)
    plot_error_distribution(preds, output_dir / "lgbm_error_distribution.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    best = min(results, key=lambda r: r["rmse"])
    worst = max(results, key=lambda r: r["rmse"])
    print(f"  Beste modell:    {best['model']:15s} RMSE={best['rmse']:.3f}")
    print(f"  Dårligste:       {worst['model']:15s} RMSE={worst['rmse']:.3f}")
    red = 100 * (worst["rmse"] - best["rmse"]) / worst["rmse"]
    print(f"  RMSE-reduksjon fra naiv til LightGBM: {red:.1f} %")


if __name__ == "__main__":
    main()
