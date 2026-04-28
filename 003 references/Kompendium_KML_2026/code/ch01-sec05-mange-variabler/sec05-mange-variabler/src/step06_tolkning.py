"""
Steg 6: Tolkning med SHAP + feature importance
==============================================
Bruker SHAP (SHapley Additive exPlanations) for å bryte ned
prediksjonene til bidrag fra hver feature. Lagrer:
- SHAP summary plot (global feature importance)
- SHAP bar plot (topp-features)
- En enkelt-prediksjon-forklaring (waterfall / force plot)
- Feature importance fra LightGBM (gain-basert)
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap


def load_all():
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output"
    df = pd.read_parquet(data_dir / "features.parquet")
    with open(output_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    with open(output_dir / "lgbm_model.pkl", "rb") as f:
        model_pack = pickle.load(f)
    return df, splits, model_pack, output_dir


def plot_feature_importance_gain(model_pack: dict, output_path: Path,
                                  top_n: int = 20) -> pd.DataFrame:
    """LightGBM gain-basert feature importance (topp N)."""
    model = model_pack["model"]
    gains = model.feature_importance(importance_type="gain")
    feats = model.feature_name()
    imp = pd.DataFrame({"feature": feats, "gain": gains})
    imp = imp.sort_values("gain", ascending=False).reset_index(drop=True)
    imp["andel_pct"] = 100 * imp["gain"] / imp["gain"].sum()
    top = imp.head(top_n).iloc[::-1]

    fig, ax = plt.subplots(figsize=(9, 6.5))
    colors = ["#8CC8E5"] * len(top)
    ax.barh(top["feature"].values, top["andel_pct"].values,
            color=colors, edgecolor="#1F6587")
    for i, (f, g) in enumerate(zip(top["feature"].values, top["andel_pct"].values)):
        ax.text(g + 0.2, i, f"{g:.1f} %", va="center", fontsize=9)
    ax.set_xlabel("Andel av total gain (%)", fontsize=11)
    ax.set_title(f"LightGBM: de {top_n} viktigste featurene (gain-basert)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")
    return imp


def compute_shap_values(model_pack: dict, X_sample: pd.DataFrame):
    """Beregn SHAP-verdier med TreeExplainer."""
    explainer = shap.TreeExplainer(model_pack["model"])
    shap_values = explainer.shap_values(X_sample)
    # For regresjon returnerer TreeExplainer en 2D array (n_samples, n_features)
    if isinstance(shap_values, list):
        shap_values = shap_values[0]
    base_value = explainer.expected_value
    if isinstance(base_value, (list, np.ndarray)):
        base_value = float(base_value[0])
    return np.asarray(shap_values), float(base_value)


def plot_shap_bar(shap_values: np.ndarray, feature_names: list[str],
                  output_path: Path, top_n: int = 15) -> None:
    """Global feature importance: gjennomsnittlig |SHAP|."""
    mean_abs = np.mean(np.abs(shap_values), axis=0)
    order = np.argsort(mean_abs)[::-1][:top_n]
    names = [feature_names[i] for i in order][::-1]
    vals = mean_abs[order][::-1]
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.barh(names, vals, color="#97D4B7", edgecolor="#307453")
    for i, v in enumerate(vals):
        ax.text(v + 0.05, i, f"{v:.2f}", va="center", fontsize=9)
    ax.set_xlabel(r"Gjennomsnittlig $|\mathrm{SHAP}|$", fontsize=12)
    ax.set_title(f"SHAP global feature importance (topp {top_n})",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_shap_beeswarm(shap_values: np.ndarray, X_sample: pd.DataFrame,
                       output_path: Path, top_n: int = 15) -> None:
    """Klassisk SHAP beeswarm (summary)."""
    fig = plt.figure(figsize=(9, 6.5))
    shap.summary_plot(
        shap_values, X_sample, max_display=top_n, show=False, plot_size=(9, 6.5),
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_shap_waterfall(shap_values: np.ndarray, base_value: float,
                        X_sample: pd.DataFrame, row_idx: int,
                        output_path: Path, top_n: int = 10) -> dict:
    """Waterfall-plot for én enkelt prediksjon."""
    vals = shap_values[row_idx]
    feats = X_sample.columns.tolist()
    # Sorter etter absoluttverdi
    order = np.argsort(np.abs(vals))[::-1][:top_n]
    contrib = [(feats[i], float(vals[i]), float(X_sample.iloc[row_idx, i])) for i in order]

    fig, ax = plt.subplots(figsize=(10, 5.5))
    labels = [f"{f} = {v:.2f}" for f, _, v in contrib][::-1]
    magnitudes = [c[1] for c in contrib][::-1]
    colors = ["#307453" if m > 0 else "#9C540B" for m in magnitudes]
    ax.barh(labels, magnitudes, color=colors, edgecolor="#1F2933")
    for i, m in enumerate(magnitudes):
        ax.text(m + (0.3 if m >= 0 else -0.3), i,
                f"{m:+.2f}", va="center",
                ha="left" if m >= 0 else "right", fontsize=9)
    ax.axvline(0, color="#1F2933", linewidth=0.8)
    total = base_value + float(vals.sum())
    ax.set_xlabel(f"SHAP-bidrag  (base = {base_value:.2f},  prediksjon = {total:.2f})",
                  fontsize=11)
    ax.set_title(
        f"SHAP waterfall for én prediksjon (topp {top_n} features)",
        fontsize=12, fontweight="bold",
    )
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")
    return {"base": base_value, "prediksjon": total,
            "bidrag": [{"feature": f, "verdi": v, "bidrag": m}
                       for f, m, v in contrib]}


def plot_forecast_aggregate(df: pd.DataFrame, splits: dict,
                            output_path: Path, model_pack: dict) -> None:
    """Aggregert total-salg-prognose over testsettet."""
    model = model_pack["model"]
    feature_cols = model_pack["feature_cols"]
    best_iter = model_pack["best_iteration"]

    test_mask = df["t"] >= splits["test_start"]
    X_test = df.loc[test_mask, feature_cols]
    df_test = df.loc[test_mask].copy()
    df_test["pred"] = np.asarray(model.predict(X_test, num_iteration=best_iter)).clip(0)

    agg_actual = df_test.groupby("t")["salg"].sum().reset_index()
    agg_pred = df_test.groupby("t")["pred"].sum().reset_index()

    # Hele historien pluss test
    total_hist = df.groupby("t")["salg"].sum().reset_index()

    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(total_hist["t"].values, total_hist["salg"].values,
            color="#8CC8E5", linewidth=0.8, label="Historisk total (trening + validering)")
    ax.plot(agg_actual["t"].values, agg_actual["salg"].values,
            color="#1F6587", linewidth=1.4, label="Faktisk (test)")
    ax.plot(agg_pred["t"].values, agg_pred["pred"].values,
            color="#9C540B", linewidth=1.4, linestyle="--",
            label="LightGBM-prognose (test)")
    ax.axvline(splits["test_start"] - 0.5, color="#556270",
               linestyle="--", alpha=0.7)
    ax.set_xlabel("$t$ (dag)", fontsize=12)
    ax.set_ylabel("Totalt salg (alle SKU-er)", fontsize=11)
    ax.set_title("Aggregert prognose mot faktisk total-salg på testsettet",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    print(f"\n{'=' * 60}")
    print("STEG 6: TOLKNING MED SHAP")
    print(f"{'=' * 60}")

    df, splits, model_pack, output_dir = load_all()
    feature_cols = model_pack["feature_cols"]

    # Feature importance (gain)
    imp = plot_feature_importance_gain(model_pack,
                                        output_dir / "lgbm_feature_importance.png",
                                        top_n=20)
    imp.to_csv(output_dir / "feature_importance.csv", index=False)
    print(f"\nTopp 10 features (gain-basert):")
    for _, r in imp.head(10).iterrows():
        print(f"  {r['feature']:30s} {r['andel_pct']:5.1f} %")

    # SHAP på et utvalg fra valideringsdataene
    val_mask = (df["t"] >= splits["val_start"]) & (df["t"] <= splits["val_end"])
    X_val = df.loc[val_mask, feature_cols]
    # Sample 2000 rader for håndterbar SHAP-beregning
    rng = np.random.default_rng(42)
    if len(X_val) > 2000:
        sample_idx = rng.choice(len(X_val), 2000, replace=False)
        X_sample = X_val.iloc[sample_idx].reset_index(drop=True)
    else:
        X_sample = X_val.reset_index(drop=True)

    print(f"\nBeregner SHAP-verdier på {len(X_sample):,} valideringsobs...")
    shap_values, base_value = compute_shap_values(model_pack, X_sample)
    print(f"  Base value (global forventet verdi): {base_value:.2f}")
    print(f"  Gj.sn. |SHAP| topp-5:")
    mean_abs = np.mean(np.abs(shap_values), axis=0)
    order = np.argsort(mean_abs)[::-1]
    for j in order[:5]:
        print(f"    {feature_cols[j]:30s} mean|SHAP| = {mean_abs[j]:.3f}")

    # SHAP-figurer
    plot_shap_bar(shap_values, feature_cols,
                  output_dir / "lgbm_shap_bar.png", top_n=15)
    plot_shap_beeswarm(shap_values, X_sample,
                       output_dir / "lgbm_shap_summary.png", top_n=15)

    # Welch et plot av en enkelt-prediksjon (velg en rad der modell predikerer høyt)
    preds_sample = model_pack["model"].predict(
        X_sample, num_iteration=model_pack["best_iteration"])
    high_idx = int(np.argmax(preds_sample))
    waterfall = plot_shap_waterfall(
        shap_values, base_value, X_sample, row_idx=high_idx,
        output_path=output_dir / "lgbm_shap_waterfall.png", top_n=10,
    )
    waterfall_json = {
        "rad_indeks": high_idx,
        "base_value": waterfall["base"],
        "prediksjon": waterfall["prediksjon"],
        "topp_bidrag": waterfall["bidrag"],
    }
    with open(output_dir / "shap_waterfall.json", "w", encoding="utf-8") as f:
        json.dump(waterfall_json, f, indent=2, ensure_ascii=False)
    print(f"SHAP-waterfall lagret: {output_dir / 'shap_waterfall.json'}")

    # Aggregert prognose
    plot_forecast_aggregate(df, splits,
                             output_dir / "lgbm_forecast_aggregate.png",
                             model_pack)

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  SHAP-analyse avdekker at {feature_cols[order[0]]!r} dominerer "
          f"prediksjonene.")
    print(f"  Waterfall-plottet forklarer én konkret prediksjon på "
          f"{waterfall['prediksjon']:.1f} enheter "
          f"(base {waterfall['base']:.1f} + bidrag).")


if __name__ == "__main__":
    main()
