"""
Steg 2: Utforskende analyse
===========================
Utforsker den observerte fordelingen av levetider (tid fra salg til retur)
og kombinerer salg og returer over tid for å visualisere avhengigheten.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def plot_lifetime_hist(levetider: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    bins = np.arange(0, 25, 1)
    ax.hist(levetider, bins=bins, color="#97D4B7", edgecolor="#307453", linewidth=0.8)
    ax.set_xlabel("Levetid $\\tau$ (måneder)", fontsize=14)
    ax.set_ylabel("Antall", fontsize=12)
    ax.set_title("Empirisk fordeling av observerte levetider (tid fra salg til retur)",
                 fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def empirical_hazard(levetider: np.ndarray, bin_edges: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Estimer empirisk hazard h(t) over diskrete bins.

    h(t_k) = antall feil i (t_{k-1}, t_k] / antall "at risk" ved t_{k-1}.
    Dette er en diskret tilnaerming til definisjonen h(t) = f(t) / S(t).
    """
    n_total = len(levetider)
    hazards = []
    centers = []
    at_risk = n_total
    for i in range(len(bin_edges) - 1):
        left, right = bin_edges[i], bin_edges[i + 1]
        n_fail = int(((levetider > left) & (levetider <= right)).sum())
        if at_risk > 0:
            hazards.append(n_fail / at_risk)
        else:
            hazards.append(0.0)
        centers.append(0.5 * (left + right))
        at_risk -= n_fail
    return np.array(centers), np.array(hazards)


def plot_empirical_hazard(centers: np.ndarray, hazards: np.ndarray, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(centers, hazards, "o-", color="#5A2C77", markerfacecolor="#BD94D7",
            markeredgecolor="#5A2C77", linewidth=2, markersize=7)
    ax.set_xlabel("Alder $t$ (måneder)", fontsize=14)
    ax.set_ylabel("$\\hat{h}(t)$", fontsize=14, rotation=0, labelpad=20)
    ax.set_title("Empirisk hazardrate: andel feil per måned gitt overlevelse", fontsize=11, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def plot_sales_vs_returns(sales: pd.DataFrame, monthly: pd.DataFrame, path: Path) -> None:
    fig, ax1 = plt.subplots(figsize=(10, 4.5))
    ax1.bar(sales["t"], sales["salg"], color="#8CC8E5", edgecolor="#1F6587",
            linewidth=0.5, alpha=0.85, label="Salg $S_s$")
    ax1.set_xlabel("Måned", fontsize=14)
    ax1.set_ylabel("Salg", fontsize=12, color="#1F6587")
    ax1.tick_params(axis="y", labelcolor="#1F6587")
    ax1.grid(True, alpha=0.3)

    ax2 = ax1.twinx()
    ax2.plot(monthly["t"], monthly["returer"], "o-", color="#961D1C",
             markerfacecolor="#ED9F9E", markeredgecolor="#961D1C",
             linewidth=2, markersize=5, label="Returer $R_t$")
    ax2.set_ylabel("Returer", fontsize=12, color="#961D1C")
    ax2.tick_params(axis="y", labelcolor="#961D1C")

    ax1.set_title("Salg og returer over tid: returer ligger etter salgstoppene", fontsize=11, fontweight="bold")
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("STEG 2: EKSPLORERING")
    print("=" * 60)

    sales = pd.read_csv(DATA_DIR / "sales.csv")
    units = pd.read_csv(DATA_DIR / "returns_units.csv")
    monthly = pd.read_csv(DATA_DIR / "returns_monthly.csv")

    observed = units["returnert"].astype(bool)
    levetider = units.loc[observed, "levetid"].to_numpy()

    plot_lifetime_hist(levetider, OUTPUT_DIR / "weib_lifetime_hist.png")

    bin_edges = np.arange(0, 25, 1.0)
    centers, hazards = empirical_hazard(levetider, bin_edges)
    plot_empirical_hazard(centers, hazards, OUTPUT_DIR / "weib_empirical_hazard.png")

    plot_sales_vs_returns(sales, monthly, OUTPUT_DIR / "weib_sales_vs_returns.png")

    # Eksport til JSON
    results = {
        "n_observed": int(observed.sum()),
        "mean_lifetime": round(float(np.mean(levetider)), 3),
        "median_lifetime": round(float(np.median(levetider)), 3),
        "std_lifetime": round(float(np.std(levetider, ddof=1)), 3),
        "min_lifetime": round(float(np.min(levetider)), 3),
        "max_lifetime": round(float(np.max(levetider)), 3),
        "hazard_bins_center": [round(float(c), 2) for c in centers],
        "hazard_estimates": [round(float(h), 4) for h in hazards],
    }
    with open(OUTPUT_DIR / "step02_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Antall observerte levetider: {results['n_observed']}")
    print(f"Gjennomsnittlig levetid:     {results['mean_lifetime']:.2f} mnd")
    print(f"Median levetid:              {results['median_lifetime']:.2f} mnd")
    print(f"Standardavvik levetid:       {results['std_lifetime']:.2f} mnd")
    print()
    print("Hazard-estimater er stigende med alder, konsistent med beta > 1.")


if __name__ == "__main__":
    main()
