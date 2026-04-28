"""
Steg 4: Modellestimering + hyperparametertuning
===============================================
Trener LightGBM-regressor på feature-matrisen med walk-forward-validering
for hyperparametertuning. Lagrer den beste modellen og parametrene.
"""

from __future__ import annotations

import json
import pickle
import time
from pathlib import Path

import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


# Kolonner som IKKE er features
EXCLUDE_COLS = {"dato", "t", "sku_id", "salg", "kategori", "merke", "butikk"}


def load_features_and_splits() -> tuple[pd.DataFrame, dict]:
    """Last inn features og splittinfo."""
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output"
    df = pd.read_parquet(data_dir / "features.parquet")
    with open(output_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    return df, splits


def select_feature_columns(df: pd.DataFrame) -> list[str]:
    """Velg alle numeriske kolonner som ikke er i EXCLUDE_COLS."""
    cols = [c for c in df.columns if c not in EXCLUDE_COLS]
    # Ikke inkluder rene hjelpe-kolonner som kunne lekke fremtid
    # (f.eks. kamp_neste_1 er ikke en leak hvis vi antar kampanjen er kjent)
    return cols


def train_lgbm(X_train, y_train, X_val, y_val, params: dict,
               num_rounds: int = 2000, stopping_rounds: int = 50,
               cat_features: list[str] | None = None) -> tuple[lgb.Booster, dict]:
    """Tren LightGBM med tidlig stopp."""
    train_set = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_features,
                            free_raw_data=False)
    val_set = lgb.Dataset(X_val, label=y_val, categorical_feature=cat_features,
                          reference=train_set, free_raw_data=False)
    evals_result: dict = {}
    model = lgb.train(
        params,
        train_set,
        num_boost_round=num_rounds,
        valid_sets=[train_set, val_set],
        valid_names=["trening", "validering"],
        callbacks=[
            lgb.early_stopping(stopping_rounds=stopping_rounds, verbose=False),
            lgb.log_evaluation(period=0),
            lgb.record_evaluation(evals_result),
        ],
    )
    return model, evals_result


def evaluate_rmse(model: lgb.Booster, X, y) -> float:
    """Beregn RMSE."""
    pred = model.predict(X, num_iteration=model.best_iteration or model.num_trees())
    return float(np.sqrt(np.mean((pred - y) ** 2)))


def walk_forward_cv(df: pd.DataFrame, feature_cols: list[str],
                    cat_features: list[str], folds: list,
                    params: dict) -> dict:
    """Kjør walk-forward-kryssvalidering og returner gjennomsnittlig RMSE."""
    rmses = []
    best_iters = []
    for fold in folds:
        train_mask = (df["t"] >= fold["train_start"]) & (df["t"] <= fold["train_end"])
        val_mask = (df["t"] >= fold["val_start"]) & (df["t"] <= fold["val_end"])
        Xtr = df.loc[train_mask, feature_cols]
        ytr = df.loc[train_mask, "salg"]
        Xva = df.loc[val_mask, feature_cols]
        yva = df.loc[val_mask, "salg"]
        model, _ = train_lgbm(Xtr, ytr, Xva, yva, params,
                              num_rounds=800, stopping_rounds=50,
                              cat_features=cat_features)
        rmse = evaluate_rmse(model, Xva, yva)
        rmses.append(rmse)
        best_iters.append(int(model.best_iteration or model.num_trees()))
    return {"rmse_mean": float(np.mean(rmses)),
            "rmse_std": float(np.std(rmses)),
            "rmses": [float(r) for r in rmses],
            "best_iters": best_iters}


def hyperparameter_search(df: pd.DataFrame, feature_cols: list[str],
                          cat_features: list[str], folds: list) -> pd.DataFrame:
    """Lite rutenettsøk med 6-10 kombinasjoner."""
    param_grid = [
        {"num_leaves": 31,  "learning_rate": 0.05, "max_depth": -1,
         "feature_fraction": 0.9, "bagging_fraction": 0.9, "bagging_freq": 5,
         "min_data_in_leaf": 20},
        {"num_leaves": 63,  "learning_rate": 0.05, "max_depth": -1,
         "feature_fraction": 0.8, "bagging_fraction": 0.8, "bagging_freq": 5,
         "min_data_in_leaf": 20},
        {"num_leaves": 31,  "learning_rate": 0.03, "max_depth": 8,
         "feature_fraction": 0.9, "bagging_fraction": 0.9, "bagging_freq": 5,
         "min_data_in_leaf": 30},
        {"num_leaves": 127, "learning_rate": 0.05, "max_depth": -1,
         "feature_fraction": 0.7, "bagging_fraction": 0.8, "bagging_freq": 5,
         "min_data_in_leaf": 40},
        {"num_leaves": 63,  "learning_rate": 0.03, "max_depth": 10,
         "feature_fraction": 0.85, "bagging_fraction": 0.9, "bagging_freq": 3,
         "min_data_in_leaf": 30},
        {"num_leaves": 127, "learning_rate": 0.03, "max_depth": 10,
         "feature_fraction": 0.75, "bagging_fraction": 0.8, "bagging_freq": 5,
         "min_data_in_leaf": 50},
    ]
    results = []
    base_params = {
        "objective": "regression",
        "metric": "rmse",
        "verbose": -1,
        "boosting_type": "gbdt",
        "seed": 42,
    }
    for i, g in enumerate(param_grid, start=1):
        params = {**base_params, **g}
        cv = walk_forward_cv(df, feature_cols, cat_features, folds, params)
        print(f"  Kombinasjon {i}/{len(param_grid)}: "
              f"num_leaves={g['num_leaves']:3d}, lr={g['learning_rate']}, "
              f"depth={g['max_depth']}, RMSE={cv['rmse_mean']:.3f} "
              f"(±{cv['rmse_std']:.3f})")
        results.append({
            **g,
            "rmse_mean": cv["rmse_mean"],
            "rmse_std": cv["rmse_std"],
            "best_iters": cv["best_iters"],
        })
    return pd.DataFrame(results).sort_values("rmse_mean").reset_index(drop=True)


def plot_training_curve(evals_result: dict, output_path: Path) -> None:
    """Plott trenings- og valideringskurve."""
    train_rmse = evals_result["trening"]["rmse"]
    val_rmse = evals_result["validering"]["rmse"]
    iters = np.arange(1, len(train_rmse) + 1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(iters, train_rmse, color="#1F6587", linewidth=1.3, label="Trening")
    ax.plot(iters, val_rmse, color="#9C540B", linewidth=1.3, label="Validering")
    best_iter = int(np.argmin(val_rmse)) + 1
    ax.axvline(best_iter, color="#556270", linestyle="--", alpha=0.7,
               label=f"Beste iterasjon ({best_iter})")
    ax.set_xlabel("Iterasjon (antall trær)", fontsize=12)
    ax.set_ylabel("RMSE", fontsize=12)
    ax.set_title("LightGBM treningskurve", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def fig_boosting_sequence(model: lgb.Booster, X_val: pd.DataFrame, y_val: pd.Series,
                          output_path: Path,
                          snapshots: tuple[int, ...] = (1, 10, 100, 1000)) -> None:
    """Lagrer figur som viser hvordan ensemble-prediksjonen og residualene
    bygges opp over iterasjonene. For en håndplukket valideringsseksjon
    tegnes prediksjonskurven ved hvert snapshot; et underpanel viser
    hvordan residualfordelingen krymper."""
    best_iter = int(model.best_iteration or model.num_trees())
    snapshots = tuple(k for k in snapshots if k <= best_iter)

    # Plukk et sammenhengende valideringssegment: første SKU, første 60 dager
    seg = X_val.iloc[:60].copy()
    y_seg = y_val.iloc[:60].values
    x_axis = np.arange(len(seg))

    series_colors = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
    series_dark = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10.5, 6.8),
                                          gridspec_kw={"height_ratios": [1.4, 1.0]})

    ax_top.plot(x_axis, y_seg, color="#1F2933", linewidth=1.6,
                label="Faktisk salg $y$", zorder=5)
    for i, k in enumerate(snapshots):
        pred_k = model.predict(seg, num_iteration=k)
        ax_top.plot(x_axis, pred_k, color=series_dark[i % len(series_dark)],
                    linewidth=1.3, alpha=0.9,
                    label=f"$F_{{{k}}}(x)$ etter {k} trær")
    ax_top.set_xlabel("Dag i valideringssegmentet", fontsize=11)
    ax_top.set_ylabel("Salg (enheter)", fontsize=11)
    ax_top.set_title("Ensembleprediksjonen bygges sekvensielt opp",
                     fontsize=12, fontweight="bold")
    ax_top.legend(fontsize=9, loc="upper right", ncol=2)
    ax_top.grid(True, alpha=0.3)

    # Residualfordelinger krymper over iterasjonene
    bins = np.linspace(-120, 120, 41)
    for i, k in enumerate(snapshots):
        pred_k_full = model.predict(X_val, num_iteration=k)
        resid = y_val.values - pred_k_full
        ax_bot.hist(resid, bins=bins, alpha=0.55,
                    color=series_colors[i % len(series_colors)],
                    edgecolor=series_dark[i % len(series_dark)], linewidth=0.7,
                    label=f"$m={k}$  (std {resid.std():.1f})")
    ax_bot.axvline(0, color="#556270", linewidth=0.8)
    ax_bot.set_xlabel("Residual $r_{i,m} = y_i - F_m(x_i)$", fontsize=11)
    ax_bot.set_ylabel("Antall observasjoner", fontsize=11)
    ax_bot.set_title("Residualene krymper når $m$ vokser",
                     fontsize=12, fontweight="bold")
    ax_bot.legend(fontsize=9, loc="upper right")
    ax_bot.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cv_results(cv_results: pd.DataFrame, output_path: Path) -> None:
    """Plott RMSE per hyperparameterkombinasjon."""
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = [f"nl={r.num_leaves}, lr={r.learning_rate}, d={r.max_depth}"
              for r in cv_results.itertuples(index=False)]
    ax.barh(labels, cv_results["rmse_mean"].values,
            xerr=cv_results["rmse_std"].values,
            color="#8CC8E5", edgecolor="#1F6587", capsize=4)
    ax.set_xlabel("Gjennomsnittlig RMSE over walk-forward-folder", fontsize=11)
    ax.set_title("Hyperparametertuning", fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    ax.invert_yaxis()
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 4: MODELLESTIMERING + HYPERPARAMETERTUNING")
    print(f"{'=' * 60}")

    df, splits = load_features_and_splits()
    feature_cols = select_feature_columns(df)
    cat_features = ["kategori_kode", "merke_kode", "butikk_kode", "sku_id_kode",
                    "ukedag", "maaned", "kvartal"]
    cat_features = [c for c in cat_features if c in feature_cols]
    print(f"\nAntall features brukt: {len(feature_cols)}")
    print(f"Kategoriske features:  {cat_features}")

    # Walk-forward-kryssvalidering
    print(f"\nHyperparametersøk med {len(splits['folds'])} walk-forward-folder:")
    t0 = time.time()
    cv_results = hyperparameter_search(df, feature_cols, cat_features, splits["folds"])
    elapsed = time.time() - t0
    print(f"\nTotal tuning-tid: {elapsed:.1f} s")

    best = cv_results.iloc[0].to_dict()
    print(f"\nBeste kombinasjon (RMSE={best['rmse_mean']:.3f}):")
    print(f"  num_leaves:       {int(best['num_leaves'])}")
    print(f"  learning_rate:    {best['learning_rate']}")
    print(f"  max_depth:        {int(best['max_depth'])}")
    print(f"  feature_fraction: {best['feature_fraction']}")
    print(f"  bagging_fraction: {best['bagging_fraction']}")
    print(f"  min_data_in_leaf: {int(best['min_data_in_leaf'])}")

    # Endelig modell: bruk trening + validering til trening med beste params, og test på testsett
    final_params = {
        "objective": "regression",
        "metric": "rmse",
        "verbose": -1,
        "boosting_type": "gbdt",
        "seed": 42,
        "num_leaves": int(best["num_leaves"]),
        "learning_rate": float(best["learning_rate"]),
        "max_depth": int(best["max_depth"]),
        "feature_fraction": float(best["feature_fraction"]),
        "bagging_fraction": float(best["bagging_fraction"]),
        "bagging_freq": 5,
        "min_data_in_leaf": int(best["min_data_in_leaf"]),
    }

    train_mask = df["t"] <= splits["train_end"]
    val_mask = (df["t"] >= splits["val_start"]) & (df["t"] <= splits["val_end"])
    Xtr = df.loc[train_mask, feature_cols]
    ytr = df.loc[train_mask, "salg"]
    Xva = df.loc[val_mask, feature_cols]
    yva = df.loc[val_mask, "salg"]

    print("\nTrener endelig modell (tren -> valider)...")
    final_model, evals_result = train_lgbm(Xtr, ytr, Xva, yva, final_params,
                                           num_rounds=3000, stopping_rounds=100,
                                           cat_features=cat_features)
    print(f"  Beste iterasjon: {final_model.best_iteration}")
    print(f"  Validering-RMSE: {evaluate_rmse(final_model, Xva, yva):.3f}")
    print(f"  Treningstid for endelig modell: {time.time() - t0:.1f} s (total)")

    # Lagre modell
    model_path = output_dir / "lgbm_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({
            "model": final_model,
            "feature_cols": feature_cols,
            "cat_features": cat_features,
            "params": final_params,
            "best_iteration": int(final_model.best_iteration or final_model.num_trees()),
        }, f)
    print(f"\nModell lagret: {model_path}")

    # Lagre CV-resultater
    cv_results.to_csv(output_dir / "cv_results.csv", index=False)
    with open(output_dir / "hyperparams.json", "w", encoding="utf-8") as f:
        json.dump({
            "best_params": final_params,
            "best_iteration": int(final_model.best_iteration or final_model.num_trees()),
            "cv_results": cv_results.to_dict(orient="records"),
            "n_features": len(feature_cols),
            "cat_features": cat_features,
        }, f, indent=2, ensure_ascii=False)
    print(f"Hyperparametre lagret: {output_dir / 'hyperparams.json'}")

    # Figurer
    plot_training_curve(evals_result, output_dir / "lgbm_training_curve.png")
    plot_cv_results(cv_results, output_dir / "lgbm_cv_results.png")

    # Pedagogisk figur for boosting-sekvensen — lagres direkte i latex-figurmappen
    latex_fig_dir = (Path(__file__).resolve().parents[4]
                     / "latex" / "200-bodymatter" / "part02-omrader"
                     / "ch01-ettersporselprognoser" / "figures")
    if latex_fig_dir.exists():
        fig_boosting_sequence(final_model, Xva, yva,
                              latex_fig_dir / "lgbm_boosting_sequence.png",
                              snapshots=(1, 10, 100, min(1000, final_model.best_iteration or 1000)))
    else:
        print(f"Advarsel: fant ikke {latex_fig_dir}; lagrer i output-mappen i stedet.")
        fig_boosting_sequence(final_model, Xva, yva,
                              output_dir / "lgbm_boosting_sequence.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  LightGBM trent med {len(feature_cols)} features og "
          f"{final_model.best_iteration} trær.")
    print(f"  Beste valideringsfeil: RMSE = {evaluate_rmse(final_model, Xva, yva):.3f}")


if __name__ == "__main__":
    main()
