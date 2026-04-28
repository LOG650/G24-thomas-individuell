"""
Steg 3: Data-splitting
======================
Tidsseriebasert train/validation/test-splitt, samt walk-forward-folder
for kryssvalidering. Vi må sikre at testdata ligger strengt etter
treningsdata (ingen leakage).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd


def load_features() -> pd.DataFrame:
    """Last inn feature-matrisen fra steg 2."""
    data_dir = Path(__file__).parent.parent / "data"
    df = pd.read_parquet(data_dir / "features.parquet")
    return df


def make_splits(df: pd.DataFrame,
                val_days: int = 60,
                test_days: int = 60) -> dict:
    """Sette opp tren/valid/test-splitt basert på dato.

    Siste `test_days` dager -> test.
    De foregående `val_days` dagene -> validering.
    Resten -> trening.
    """
    t_max = int(df["t"].max())
    test_start = t_max - test_days + 1
    val_start = test_start - val_days
    train_end = val_start - 1

    train_idx = df["t"] <= train_end
    val_idx = (df["t"] >= val_start) & (df["t"] < test_start)
    test_idx = df["t"] >= test_start

    return {
        "t_max": t_max,
        "train_end": int(train_end),
        "val_start": int(val_start),
        "val_end": int(test_start - 1),
        "test_start": int(test_start),
        "train_idx": train_idx,
        "val_idx": val_idx,
        "test_idx": test_idx,
    }


def walk_forward_folds(t_max: int, train_min: int, step: int = 30,
                       horizon: int = 30, n_folds: int = 4) -> list[tuple[int, int, int, int]]:
    """Lag walk-forward-folder for tidsserie-kryssvalidering.

    Hver fold: (train_start, train_end, val_start, val_end)
    """
    folds = []
    for k in range(n_folds):
        train_end = train_min + k * step
        val_start = train_end + 1
        val_end = val_start + horizon - 1
        if val_end > t_max:
            break
        folds.append((1, int(train_end), int(val_start), int(val_end)))
    return folds


def plot_split(df: pd.DataFrame, splits: dict, output_path: Path) -> None:
    """Visualiser tren/valid/test-splitt på total salgstidsserie."""
    total = df.groupby("t")["salg"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(12, 5))

    t_arr = total["t"].values
    sales_arr = total["salg"].values
    train_mask = t_arr <= splits["train_end"]
    val_mask = (t_arr >= splits["val_start"]) & (t_arr <= splits["val_end"])
    test_mask = t_arr >= splits["test_start"]

    ax.plot(t_arr[train_mask], sales_arr[train_mask], color="#1F6587",
            linewidth=0.9, label=f"Trening  (t = 1–{splits['train_end']})")
    ax.plot(t_arr[val_mask], sales_arr[val_mask], color="#9C540B",
            linewidth=1.0, label=f"Validering  (t = {splits['val_start']}–{splits['val_end']})")
    ax.plot(t_arr[test_mask], sales_arr[test_mask], color="#5A2C77",
            linewidth=1.0, label=f"Test  (t = {splits['test_start']}–{splits['t_max']})")

    ax.axvline(splits["train_end"] + 0.5, color="#556270", linestyle="--", alpha=0.7)
    ax.axvline(splits["test_start"] - 0.5, color="#556270", linestyle="--", alpha=0.7)

    ax.set_xlabel("$t$ (dag)", fontsize=12)
    ax.set_ylabel("Totalt salg (alle SKU-er)", fontsize=11)
    ax.set_title("Tidsseriesplitt: trening, validering og test", fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(1, splits["t_max"])
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_walk_forward(folds: list[tuple[int, int, int, int]], t_max: int,
                       output_path: Path) -> None:
    """Visualiser walk-forward-folder som horisontale staver."""
    fig, ax = plt.subplots(figsize=(11, 4.5))
    y_train = mpatches.Patch(color="#8CC8E5", label="Treningsdata")
    y_val = mpatches.Patch(color="#F6BA7C", label="Valideringsdata")

    for k, (ts, te, vs, ve) in enumerate(folds):
        y = len(folds) - k
        ax.barh(y, te - ts + 1, left=ts, color="#8CC8E5",
                edgecolor="#1F6587", height=0.55)
        ax.barh(y, ve - vs + 1, left=vs, color="#F6BA7C",
                edgecolor="#9C540B", height=0.55)
        ax.text(ts - 5, y, f"Fold {k + 1}", va="center", ha="right",
                fontsize=10, fontweight="bold")
    ax.set_yticks([])
    ax.set_xlabel("$t$ (dag)", fontsize=12)
    ax.set_xlim(0, t_max + 20)
    ax.set_title("Walk-forward-kryssvalidering (4 folder)",
                 fontsize=12, fontweight="bold")
    ax.legend(handles=[y_train, y_val], loc="lower right", fontsize=10)
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 3: DATA-SPLITTING")
    print(f"{'=' * 60}")

    df = load_features()
    splits = make_splits(df, val_days=60, test_days=60)

    train_rows = int(splits["train_idx"].sum())
    val_rows = int(splits["val_idx"].sum())
    test_rows = int(splits["test_idx"].sum())
    total = train_rows + val_rows + test_rows

    print(f"\nSplitt-statistikk:")
    print(f"  Trening:    t = 1..{splits['train_end']}  ({train_rows:,} rader, "
          f"{100 * train_rows / total:.1f} %)")
    print(f"  Validering: t = {splits['val_start']}..{splits['val_end']}  ({val_rows:,} rader, "
          f"{100 * val_rows / total:.1f} %)")
    print(f"  Test:       t = {splits['test_start']}..{splits['t_max']}  ({test_rows:,} rader, "
          f"{100 * test_rows / total:.1f} %)")

    # Walk-forward
    folds = walk_forward_folds(t_max=splits["train_end"], train_min=400,
                               step=30, horizon=30, n_folds=4)
    print(f"\nWalk-forward-folder: {len(folds)}")
    for i, (ts, te, vs, ve) in enumerate(folds):
        print(f"  Fold {i + 1}: trening [t={ts}..{te}] -> validering [t={vs}..{ve}]")

    # Lagre splittinfo
    splits_json = {
        "t_max": splits["t_max"],
        "train_end": splits["train_end"],
        "val_start": splits["val_start"],
        "val_end": splits["val_end"],
        "test_start": splits["test_start"],
        "train_rader": train_rows,
        "val_rader": val_rows,
        "test_rader": test_rows,
        "folds": [
            {"fold": i + 1, "train_start": ts, "train_end": te,
             "val_start": vs, "val_end": ve}
            for i, (ts, te, vs, ve) in enumerate(folds)
        ],
    }
    with open(output_dir / "split_info.json", "w", encoding="utf-8") as f:
        json.dump(splits_json, f, indent=2, ensure_ascii=False)
    print(f"Splittinfo lagret: {output_dir / 'split_info.json'}")

    # Figurer
    plot_split(df, splits, output_dir / "lgbm_split.png")
    plot_walk_forward(folds, splits["t_max"], output_dir / "lgbm_walk_forward.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  Siste {splits['t_max'] - splits['test_start'] + 1} dager er holdt helt ut "
          f"som testsett.")
    print(f"  De {splits['val_end'] - splits['val_start'] + 1} dagene før "
          f"brukes til hyperparametertuning.")
    print(f"  {len(folds)} walk-forward-folder gir robust estimat av "
          f"modellens generaliseringsevne.")


if __name__ == "__main__":
    main()
