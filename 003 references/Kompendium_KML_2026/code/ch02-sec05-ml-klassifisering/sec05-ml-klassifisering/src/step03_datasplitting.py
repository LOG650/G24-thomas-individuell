"""
Steg 3: Datasplitting
=====================
SKU-basert (stratifisert) split fordi vi klassifiserer SKU-er paa deres
aggregerte attributter. Siden selve klassen er definert paa SKU-niva --
ikke paa en tidsrekke -- bruker vi stratifisert split for aa bevare
klassefordelingen i hvert sett. For hyperparametertuning bruker vi
stratifisert 5-fold CV.

- trening: 70 %
- validering: 15 %
- test: 15 %
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split


S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S5 = "#ED9F9E"; S5D = "#961D1C"


def load_features() -> pd.DataFrame:
    data_dir = Path(__file__).parent.parent / "data"
    return pd.read_parquet(data_dir / "features.parquet")


def make_splits(df: pd.DataFrame, seed: int = 42) -> dict:
    """Stratifisert 70/15/15 split paa klasse."""
    idx = np.arange(len(df))
    y = df["klasse"].to_numpy()

    idx_trainval, idx_test = train_test_split(
        idx, test_size=0.15, random_state=seed, stratify=y)
    y_trainval = y[idx_trainval]
    rel_val_size = 0.15 / 0.85
    idx_train, idx_val = train_test_split(
        idx_trainval, test_size=rel_val_size,
        random_state=seed, stratify=y_trainval)

    return {
        "train_idx": idx_train.tolist(),
        "val_idx": idx_val.tolist(),
        "test_idx": idx_test.tolist(),
    }


def plot_split(df: pd.DataFrame, splits: dict, output_path: Path) -> None:
    """Sammenlign klassefordeling i hver split."""
    class_labels = {0: "kontinuerlig", 1: "periodisk", 2: "make-to-order"}
    class_colors = [S1D, S2D, S5D]
    fill_colors = [S1, S2, S5]

    def pct(idx):
        sub = df.iloc[idx]
        return [100 * (sub["klasse"] == k).mean() for k in [0, 1, 2]]

    train_pct = pct(splits["train_idx"])
    val_pct = pct(splits["val_idx"])
    test_pct = pct(splits["test_idx"])

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(3)
    width = 0.25
    for i, (pcts, name, hatch) in enumerate([
        (train_pct, f"Trening ({len(splits['train_idx']):,})", None),
        (val_pct, f"Validering ({len(splits['val_idx']):,})", "//"),
        (test_pct, f"Test ({len(splits['test_idx']):,})", "xx"),
    ]):
        ax.bar(x + (i - 1) * width, pcts, width,
               color=fill_colors, edgecolor=class_colors,
               hatch=hatch, label=name)
    ax.set_xticks(x, [class_labels[k] for k in [0, 1, 2]])
    ax.set_ylabel("Andel av sett (%)", fontsize=11)
    ax.set_title("Klassefordeling -- trening, validering, test",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10, loc="upper right")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 3: DATASPLITTING")
    print(f"{'=' * 60}")

    df = load_features()
    splits = make_splits(df)

    print(f"\n{'Sett':20s}{'Antall':>10s}{'Andel':>12s}")
    for name in ["train_idx", "val_idx", "test_idx"]:
        cnt = len(splits[name])
        print(f"  {name:18s}{cnt:>10,}{100 * cnt / len(df):>11.1f} %")

    # Lagre
    with open(output_dir / "split_info.json", "w", encoding="utf-8") as f:
        json.dump(splits, f)

    plot_split(df, splits, output_dir / "mlklasse_split.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print("  Stratifisert SKU-splitt bevarer klassefordelingen i alle "
          "tre sett og gir rettferdig evaluering.")


if __name__ == "__main__":
    main()
