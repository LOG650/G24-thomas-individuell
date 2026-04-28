"""
Steg 4: Modellestimering -- LightGBM multiclass
================================================
Trener en LightGBM flerklasse-klassifikator med:
- Lite rutenettsoek over (num_leaves, learning_rate, min_data_in_leaf, ...)
- Stratifisert 5-fold CV paa treningssettet for tuning
- Endelig trening paa trening + validering med early stopping
- Lagrer pickled modell for senere bruk i step05/step06
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
from sklearn.metrics import f1_score, log_loss
from sklearn.model_selection import StratifiedKFold


EXCLUDE_COLS = {
    "sku_id", "kategori", "klasse", "abc", "xyz",
    # Fjern de opplagte \"snarveiene\" som ville lekke ABC/XYZ-
    # relaterte labels -- men behold abc_kode og xyz_kode siden de
    # er interessante features som modellen kan bygge ikke-lineaere
    # kombinasjoner av. Om vi excluderte dem, ville sammenligningen mot
    # baseline ikke vaere rettferdig.
}

CAT_FEATURES = ["kategori_kode", "abc_kode", "xyz_kode"]


S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S4 = "#BD94D7"; S4D = "#5A2C77"
S5 = "#ED9F9E"; S5D = "#961D1C"
INK = "#1F2933"


def load_features_and_splits() -> tuple[pd.DataFrame, dict, list[str]]:
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output"
    df = pd.read_parquet(data_dir / "features.parquet")
    with open(output_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    with open(output_dir / "feature_cols.json", "r", encoding="utf-8") as f:
        feature_cols = json.load(f)["feature_cols"]
    feature_cols = [c for c in feature_cols if c not in EXCLUDE_COLS]
    return df, splits, feature_cols


def train_lgbm(X_train, y_train, X_val, y_val,
               params: dict, num_rounds: int = 600,
               stopping_rounds: int = 40,
               cat_features: list[str] | None = None
               ) -> tuple[lgb.Booster, dict]:
    """Tren LightGBM multiclass med early stopping."""
    train_set = lgb.Dataset(X_train, label=y_train,
                            categorical_feature=cat_features,
                            free_raw_data=False)
    val_set = lgb.Dataset(X_val, label=y_val,
                          categorical_feature=cat_features,
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


def predict_proba(model: lgb.Booster, X: pd.DataFrame) -> np.ndarray:
    """Prediker klasse-sannsynligheter."""
    return model.predict(X, num_iteration=model.best_iteration or model.num_trees())


def macro_f1(y_true: np.ndarray, proba: np.ndarray) -> float:
    y_pred = np.argmax(proba, axis=1)
    return float(f1_score(y_true, y_pred, average="macro"))


def cv_evaluate(df: pd.DataFrame, feature_cols: list[str],
                cat_features: list[str], params: dict,
                train_idx: list[int], n_folds: int = 5) -> dict:
    """Stratifisert 5-fold CV paa treningssettet (for hyperparametertuning)."""
    X = df.loc[train_idx, feature_cols].reset_index(drop=True)
    y = df.loc[train_idx, "klasse"].to_numpy()
    skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)

    f1s, logs, best_iters = [], [], []
    for fold, (tr_i, va_i) in enumerate(skf.split(X, y)):
        model, _ = train_lgbm(
            X.iloc[tr_i], y[tr_i], X.iloc[va_i], y[va_i],
            params, num_rounds=500, stopping_rounds=30,
            cat_features=cat_features,
        )
        proba = predict_proba(model, X.iloc[va_i])
        f1s.append(macro_f1(y[va_i], proba))
        logs.append(float(log_loss(y[va_i], proba, labels=[0, 1, 2])))
        best_iters.append(int(model.best_iteration or model.num_trees()))
    return {
        "f1_mean": float(np.mean(f1s)),
        "f1_std": float(np.std(f1s)),
        "logloss_mean": float(np.mean(logs)),
        "logloss_std": float(np.std(logs)),
        "best_iters": best_iters,
    }


def hyperparameter_search(df: pd.DataFrame, feature_cols: list[str],
                          cat_features: list[str],
                          train_idx: list[int]) -> pd.DataFrame:
    """Rutenettsoek med 6 kombinasjoner."""
    base_params = {
        "objective": "multiclass",
        "num_class": 3,
        "metric": "multi_logloss",
        "verbose": -1,
        "boosting_type": "gbdt",
        "seed": 42,
    }
    grid = [
        {"num_leaves": 31,  "learning_rate": 0.05, "max_depth": -1,
         "feature_fraction": 0.9, "bagging_fraction": 0.9, "bagging_freq": 5,
         "min_data_in_leaf": 20},
        {"num_leaves": 63,  "learning_rate": 0.05, "max_depth": -1,
         "feature_fraction": 0.8, "bagging_fraction": 0.8, "bagging_freq": 5,
         "min_data_in_leaf": 30},
        {"num_leaves": 31,  "learning_rate": 0.03, "max_depth": 8,
         "feature_fraction": 0.9, "bagging_fraction": 0.9, "bagging_freq": 5,
         "min_data_in_leaf": 40},
        {"num_leaves": 127, "learning_rate": 0.05, "max_depth": -1,
         "feature_fraction": 0.7, "bagging_fraction": 0.8, "bagging_freq": 5,
         "min_data_in_leaf": 40},
        {"num_leaves": 15,  "learning_rate": 0.08, "max_depth": 6,
         "feature_fraction": 0.9, "bagging_fraction": 0.9, "bagging_freq": 3,
         "min_data_in_leaf": 20},
        {"num_leaves": 63,  "learning_rate": 0.03, "max_depth": 10,
         "feature_fraction": 0.85, "bagging_fraction": 0.9, "bagging_freq": 5,
         "min_data_in_leaf": 30},
    ]
    rows = []
    for i, g in enumerate(grid, start=1):
        params = {**base_params, **g}
        cv = cv_evaluate(df, feature_cols, cat_features, params, train_idx)
        print(f"  Kombinasjon {i}/{len(grid)}: "
              f"nl={g['num_leaves']:3d}, lr={g['learning_rate']:.2f}, "
              f"d={g['max_depth']:3d} -> macroF1={cv['f1_mean']:.4f} "
              f"(\u00b1{cv['f1_std']:.4f}), logloss={cv['logloss_mean']:.3f}")
        rows.append({**g, **cv})
    return pd.DataFrame(rows).sort_values("f1_mean", ascending=False).reset_index(drop=True)


def plot_training_curve(evals: dict, output_path: Path) -> None:
    """Trenings- og valideringskurve (logloss)."""
    tr = evals["trening"]["multi_logloss"]
    va = evals["validering"]["multi_logloss"]
    iters = np.arange(1, len(tr) + 1)
    best_iter = int(np.argmin(va)) + 1

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(iters, tr, color=S1D, linewidth=1.3, label="Trening")
    ax.plot(iters, va, color=S3D, linewidth=1.3, label="Validering")
    ax.axvline(best_iter, color="#556270", linestyle="--", alpha=0.7,
               label=f"Beste iterasjon ({best_iter})")
    ax.set_xlabel("Iterasjon (antall trær)", fontsize=12)
    ax.set_ylabel("Multi-logloss", fontsize=12)
    ax.set_title("LightGBM treningskurve (multiclass)", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cv_grid(cv_results: pd.DataFrame, output_path: Path) -> None:
    """Stav-plot av CV-resultater."""
    fig, ax = plt.subplots(figsize=(10, 5))
    labels = [f"nl={r.num_leaves}, lr={r.learning_rate}, d={r.max_depth}"
              for r in cv_results.itertuples(index=False)]
    ax.barh(labels, cv_results["f1_mean"].values,
            xerr=cv_results["f1_std"].values,
            color=S1, edgecolor=S1D, capsize=4)
    ax.set_xlabel("Macro-F1 i 5-fold CV", fontsize=11)
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
    print("STEG 4: MODELLESTIMERING -- LightGBM multiclass")
    print(f"{'=' * 60}")

    df, splits, feature_cols = load_features_and_splits()
    cat_features = [c for c in CAT_FEATURES if c in feature_cols]

    print(f"\nAntall features: {len(feature_cols)}")
    print(f"Kategoriske:    {cat_features}")

    # CV paa treningssettet
    print(f"\nHyperparametertuning (5-fold stratifisert CV):")
    t0 = time.time()
    cv_results = hyperparameter_search(df, feature_cols, cat_features,
                                       splits["train_idx"])
    elapsed = time.time() - t0
    print(f"\nTotal CV-tid: {elapsed:.1f} s")

    best = cv_results.iloc[0].to_dict()
    print(f"\nBeste kombinasjon (F1={best['f1_mean']:.4f}):")
    for k in ["num_leaves", "learning_rate", "max_depth",
              "feature_fraction", "bagging_fraction", "min_data_in_leaf"]:
        print(f"  {k:20s}: {best[k]}")

    # Endelig trening paa trening + early stopping paa validering
    final_params = {
        "objective": "multiclass",
        "num_class": 3,
        "metric": "multi_logloss",
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

    X_tr = df.loc[splits["train_idx"], feature_cols]
    y_tr = df.loc[splits["train_idx"], "klasse"].to_numpy()
    X_va = df.loc[splits["val_idx"], feature_cols]
    y_va = df.loc[splits["val_idx"], "klasse"].to_numpy()

    print("\nTrener endelig modell (tren -> valider med early stopping)...")
    model, evals = train_lgbm(X_tr, y_tr, X_va, y_va, final_params,
                              num_rounds=1500, stopping_rounds=60,
                              cat_features=cat_features)
    best_iter = int(model.best_iteration or model.num_trees())
    proba_val = predict_proba(model, X_va)
    f1_val = macro_f1(y_va, proba_val)
    print(f"  Beste iterasjon: {best_iter}")
    print(f"  Valideringsfeil (macro-F1): {f1_val:.4f}")

    # Lagre
    model_path = output_dir / "lgbm_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump({
            "model": model,
            "feature_cols": feature_cols,
            "cat_features": cat_features,
            "params": final_params,
            "best_iteration": best_iter,
            "val_macro_f1": f1_val,
        }, f)
    print(f"Modell lagret: {model_path}")

    cv_results.to_csv(output_dir / "cv_results.csv", index=False)
    with open(output_dir / "hyperparams.json", "w", encoding="utf-8") as f:
        json.dump({
            "best_params": final_params,
            "best_iteration": best_iter,
            "val_macro_f1": f1_val,
            "cv_results": cv_results.to_dict(orient="records"),
        }, f, indent=2, ensure_ascii=False)

    # Figurer
    plot_training_curve(evals, output_dir / "mlklasse_training_curve.png")
    plot_cv_grid(cv_results, output_dir / "mlklasse_cv_results.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  Endelig modell: {best_iter} traer, {len(feature_cols)} features.")
    print(f"  Valideringsfeil: macro-F1 = {f1_val:.4f}")


if __name__ == "__main__":
    main()
