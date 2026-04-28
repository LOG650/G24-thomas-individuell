"""
Steg 5: Validering -- LightGBM vs naiv ABC-XYZ
===============================================
Evaluerer den tunede LightGBM-modellen paa testsettet og sammenligner
mot en naiv \"ABC-XYZ -> klasse\"-mapping som baseline. Produserer:

- Klassifikasjonsrapport (precision/recall/F1 per klasse)
- Konfusjonsmatrise (LightGBM)
- Per-klasse F1 og overordnet macro-F1
- Sammenligning med ABC-XYZ-baseline
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    classification_report, confusion_matrix, f1_score,
)

S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S4 = "#BD94D7"; S4D = "#5A2C77"
S5 = "#ED9F9E"; S5D = "#961D1C"
INK = "#1F2933"

CLASS_LABELS = {0: "kontinuerlig", 1: "periodisk", 2: "make-to-order"}


def load_all():
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output"
    df = pd.read_parquet(data_dir / "features.parquet")
    with open(output_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    with open(output_dir / "lgbm_model.pkl", "rb") as f:
        model_pack = pickle.load(f)
    return df, splits, model_pack, output_dir


def abc_xyz_baseline(df: pd.DataFrame) -> np.ndarray:
    """Naiv mapping fra ABC-XYZ til optimal klasse:
       AX, AY, BX -> kontinuerlig
       AZ, BY, CX -> periodisk
       BZ, CY, CZ -> make-to-order
    """
    mapping = {
        ("A", "X"): 0, ("A", "Y"): 0, ("B", "X"): 0,
        ("A", "Z"): 1, ("B", "Y"): 1, ("C", "X"): 1,
        ("B", "Z"): 2, ("C", "Y"): 2, ("C", "Z"): 2,
    }
    pairs = list(zip(df["abc"].astype(str), df["xyz"].astype(str)))
    pred = np.array([mapping[p] for p in pairs])
    return pred


def plot_confusion(cm: np.ndarray, title: str, output_path: Path) -> None:
    """Plott konfusjonsmatrise med tallverdier."""
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    im = ax.imshow(cm, cmap="Blues")
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            v = cm[i, j]
            ax.text(j, i, f"{v:,}", ha="center", va="center",
                    color=INK if v < cm.max() / 2 else "white", fontsize=12)
    ax.set_xticks([0, 1, 2], [CLASS_LABELS[i] for i in [0, 1, 2]], rotation=20)
    ax.set_yticks([0, 1, 2], [CLASS_LABELS[i] for i in [0, 1, 2]])
    ax.set_xlabel("Predikert klasse", fontsize=11)
    ax.set_ylabel("Sann klasse", fontsize=11)
    ax.set_title(title, fontsize=12, fontweight="bold")
    plt.colorbar(im, ax=ax, shrink=0.75)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_comparison(f1s: dict, output_path: Path) -> None:
    """Stav-plot F1 per klasse for de to modellene."""
    models = list(f1s.keys())
    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(3)
    width = 0.38
    colors = [S3, S1]
    edges = [S3D, S1D]
    for i, m in enumerate(models):
        ax.bar(x + (i - 0.5) * width, f1s[m]["per_klasse"], width,
               color=colors[i], edgecolor=edges[i], label=m)
        for j, v in enumerate(f1s[m]["per_klasse"]):
            ax.text(x[j] + (i - 0.5) * width, v + 0.01, f"{v:.3f}",
                    ha="center", fontsize=9)
    ax.set_xticks(x, [CLASS_LABELS[k] for k in [0, 1, 2]])
    ax.set_ylabel("F1-score", fontsize=11)
    ax.set_ylim(0, 1.05)
    ax.set_title("F1 per klasse -- ABC-XYZ baseline vs LightGBM",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    df, splits, model_pack, output_dir = load_all()

    print(f"\n{'=' * 60}")
    print("STEG 5: VALIDERING -- ML vs ABC-XYZ baseline")
    print(f"{'=' * 60}")

    feature_cols = model_pack["feature_cols"]
    model = model_pack["model"]

    test_idx = splits["test_idx"]
    test_df = df.iloc[test_idx].reset_index(drop=True)
    y_test = test_df["klasse"].to_numpy()

    # LightGBM prediksjoner
    proba = model.predict(test_df[feature_cols],
                          num_iteration=model.best_iteration or model.num_trees())
    y_pred_lgbm = np.argmax(proba, axis=1)

    # ABC-XYZ baseline
    y_pred_abc = abc_xyz_baseline(test_df)

    # Rapporter
    print("\n--- LightGBM ---")
    report_lgbm = classification_report(
        y_test, y_pred_lgbm, target_names=[CLASS_LABELS[i] for i in [0, 1, 2]],
        output_dict=True, zero_division=0)
    print(classification_report(
        y_test, y_pred_lgbm, target_names=[CLASS_LABELS[i] for i in [0, 1, 2]],
        zero_division=0))

    print("\n--- ABC-XYZ baseline ---")
    report_abc = classification_report(
        y_test, y_pred_abc, target_names=[CLASS_LABELS[i] for i in [0, 1, 2]],
        output_dict=True, zero_division=0)
    print(classification_report(
        y_test, y_pred_abc, target_names=[CLASS_LABELS[i] for i in [0, 1, 2]],
        zero_division=0))

    macro_f1_lgbm = float(f1_score(y_test, y_pred_lgbm, average="macro"))
    macro_f1_abc = float(f1_score(y_test, y_pred_abc, average="macro"))
    acc_lgbm = float(np.mean(y_pred_lgbm == y_test))
    acc_abc = float(np.mean(y_pred_abc == y_test))

    print(f"\nOvergripende:")
    print(f"  LightGBM:  macro-F1 = {macro_f1_lgbm:.4f},  "
          f"accuracy = {acc_lgbm:.4f}")
    print(f"  ABC-XYZ:   macro-F1 = {macro_f1_abc:.4f},  "
          f"accuracy = {acc_abc:.4f}")

    # Konfusjonsmatriser
    cm_lgbm = confusion_matrix(y_test, y_pred_lgbm, labels=[0, 1, 2])
    cm_abc = confusion_matrix(y_test, y_pred_abc, labels=[0, 1, 2])

    plot_confusion(cm_lgbm, "LightGBM -- konfusjonsmatrise paa testsettet",
                   output_dir / "mlklasse_confusion.png")
    plot_confusion(cm_abc, "ABC-XYZ baseline -- konfusjonsmatrise",
                   output_dir / "mlklasse_confusion_abc.png")

    f1_per_lgbm = [float(report_lgbm[CLASS_LABELS[k]]["f1-score"]) for k in [0, 1, 2]]
    f1_per_abc = [float(report_abc[CLASS_LABELS[k]]["f1-score"]) for k in [0, 1, 2]]
    plot_comparison(
        {"ABC-XYZ": {"per_klasse": f1_per_abc, "macro": macro_f1_abc},
         "LightGBM": {"per_klasse": f1_per_lgbm, "macro": macro_f1_lgbm}},
        output_dir / "mlklasse_model_comparison.png",
    )

    # Lagre rapport
    results = {
        "n_test": int(len(test_df)),
        "lightgbm": {
            "macro_f1": macro_f1_lgbm,
            "accuracy": acc_lgbm,
            "per_klasse_f1": f1_per_lgbm,
            "per_klasse_precision": [
                float(report_lgbm[CLASS_LABELS[k]]["precision"]) for k in [0, 1, 2]],
            "per_klasse_recall": [
                float(report_lgbm[CLASS_LABELS[k]]["recall"]) for k in [0, 1, 2]],
            "confusion_matrix": cm_lgbm.tolist(),
        },
        "abc_xyz": {
            "macro_f1": macro_f1_abc,
            "accuracy": acc_abc,
            "per_klasse_f1": f1_per_abc,
            "per_klasse_precision": [
                float(report_abc[CLASS_LABELS[k]]["precision"]) for k in [0, 1, 2]],
            "per_klasse_recall": [
                float(report_abc[CLASS_LABELS[k]]["recall"]) for k in [0, 1, 2]],
            "confusion_matrix": cm_abc.tolist(),
        },
    }
    with open(output_dir / "validation.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Rapport lagret: {output_dir / 'validation.json'}")

    # Lagre prediksjoner for bruk i step06
    pred_df = test_df[["sku_id", "kategori", "klasse"]].copy()
    pred_df["pred_lgbm"] = y_pred_lgbm
    pred_df["pred_abc"] = y_pred_abc
    pred_df.to_csv(output_dir / "test_predictions.csv",
                   index=False, encoding="utf-8")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    lift = 100 * (macro_f1_lgbm - macro_f1_abc) / macro_f1_abc
    print(f"  LightGBM lofter macro-F1 fra {macro_f1_abc:.3f} (ABC-XYZ) til "
          f"{macro_f1_lgbm:.3f}, dvs. +{lift:.1f} % relativ forbedring.")


if __name__ == "__main__":
    main()
