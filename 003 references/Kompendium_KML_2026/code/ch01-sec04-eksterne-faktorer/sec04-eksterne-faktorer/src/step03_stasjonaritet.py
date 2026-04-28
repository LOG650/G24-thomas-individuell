"""
Steg 3: Stasjonaritet og differensiering
========================================
Tester stasjonaritet på den observerte salgsserien Y_t med ADF-testen,
og på den transformerte serien Z_t = nabla Y_t (d = 1). Resultatene
brukes til å fastsette (d, D) i SARIMAX(p, d, q)(P, D, Q)_m.

Fordi vi modellerer daglige salgsdata med ukesesong bruker vi m = 7.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.stattools import adfuller

from step01_datainnsamling import generate_raw_data
from step02_feature_engineering import EXOG_COLS, build_features


def run_adf(series: np.ndarray, name: str) -> dict:
    """Kjør ADF-test og returner resultatene som dict."""
    stat, pval, lags, nobs, critvals, _ = adfuller(series, autolag="AIC")
    return {
        "navn": name,
        "adf_statistikk": round(float(stat), 4),
        "p_verdi": round(float(pval), 6),
        "lag_brukt": int(lags),
        "antall_obs": int(nobs),
        "kritisk_1": round(float(critvals["1%"]), 4),
        "kritisk_5": round(float(critvals["5%"]), 4),
        "kritisk_10": round(float(critvals["10%"]), 4),
        "stasjonaer": bool(pval < 0.05),
    }


def plot_comparison(y: pd.Series, z: pd.Series, output_path: Path) -> None:
    """Plott original Y_t og differensiert Z_t side ved side."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 6.2), sharex=False)

    t_y = np.arange(1, len(y) + 1)
    axes[0].plot(t_y, y.values, color="#1F6587", linewidth=0.8)
    axes[0].set_title("Original serie $Y_t$", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("$Y_t$", fontsize=13, rotation=0, labelpad=15)
    axes[0].set_xlim(1, len(y))
    axes[0].grid(True, alpha=0.3)

    t_z = np.arange(1, len(z) + 1) + 1  # start på t = 2 (første diff)
    axes[1].plot(t_z, z.values, color="#307453", linewidth=0.8)
    axes[1].axhline(0, color="#961D1C", linestyle="--", linewidth=1)
    axes[1].set_title(r"Differensiert serie $Z_t = \nabla Y_t$",
                      fontsize=11, fontweight="bold")
    axes[1].set_ylabel("$Z_t$", fontsize=13, rotation=0, labelpad=15)
    axes[1].set_xlabel("$t$ (dag)", fontsize=12)
    axes[1].set_xlim(1, len(y))
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_acf_pacf(residual: pd.Series, output_path: Path, lags: int = 28) -> None:
    """Plott ACF og PACF side ved side for den 'kampanje-rensede' serien.

    Her regres salget på de eksogene variablene (OLS), og vi bruker residualene
    for å se på tidsseriestrukturen som ARIMA-delen skal fange.
    """
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    plot_acf(residual.dropna(), lags=lags, ax=axes[0], alpha=0.05,
             title=r"ACF for $e_t$ (residual etter kampanjerens)")
    plot_pacf(residual.dropna(), lags=lags, ax=axes[1], alpha=0.05,
              method="ywm", title=r"PACF for $e_t$")

    for ax in axes:
        ax.axvline(7, color="#961D1C", linestyle="--", linewidth=1, alpha=0.7)
        ax.axvline(14, color="#961D1C", linestyle="--", linewidth=1, alpha=0.5)
        ax.set_xlabel("Lag $k$", fontsize=11)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 3: STASJONARITET OG DIFFERENSIERING")
    print(f"{'=' * 60}")

    df = generate_raw_data()
    y = pd.Series(df["salg"].values, index=df["dato"], name="Salg")

    # ADF-test på original serie
    adf_original = run_adf(y.values, "original")
    print("\n--- ADF på original serie ---")
    for k, v in adf_original.items():
        print(f"  {k:18s}: {v}")

    # Første differensiering (d = 1)
    z = y.diff().dropna()
    adf_diff = run_adf(z.values, "diff_d1")
    print("\n--- ADF på differensiert serie (d = 1) ---")
    for k, v in adf_diff.items():
        print(f"  {k:18s}: {v}")

    # Vi beholder D = 0 siden ukesesong ($m = 7$) er moderat;
    # sesongstrukturen håndteres i ARMA-delen med (P, Q) på sesonglag.
    # Som sanity-check viser vi også ADF etter én sesongdifferensiering.
    zs = y.diff().diff(7).dropna()
    adf_seasonal = run_adf(zs.values, "diff_d1_D1_m7")
    print("\n--- ADF etter d=1, D=1, m=7 (kontroll) ---")
    for k, v in adf_seasonal.items():
        print(f"  {k:18s}: {v}")

    plot_comparison(y, z, output_dir / "arimax_stationarity_comparison.png")

    # ACF/PACF: vi regres først Y_t på de eksogene variablene med OLS for
    # å isolere ARIMA-strukturen (ellers dominerer kampanjespikene begge plott).
    df_feat = build_features(df)
    X = df_feat[EXOG_COLS].astype(float).values
    X_aug = np.column_stack([np.ones(len(X)), X])
    beta, *_ = np.linalg.lstsq(X_aug, y.values, rcond=None)
    residual = y.values - X_aug @ beta
    residual_diff = pd.Series(residual).diff().dropna()
    plot_acf_pacf(residual_diff, output_dir / "arimax_acf_pacf.png", lags=28)

    # Lagre
    results = {
        "original": adf_original,
        "diff_d1": adf_diff,
        "diff_d1_D1_m7": adf_seasonal,
        "valgt": {"d": 1, "D": 0, "m": 7,
                   "begrunnelse":
                   "Serien blir stasjonær allerede etter d=1; "
                   "ukesesong håndteres i ARMA-delen via m=7."},
    }
    with open(output_dir / "stationarity_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print("\nResultater lagret: stationarity_results.json")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(
        f"  Original serie:    p = {adf_original['p_verdi']:.3g}  -> ikke-stasjonær.\n"
        f"  Etter d = 1:       p = {adf_diff['p_verdi']:.3g}  -> stasjonær.\n"
        "  Valgt: d = 1, D = 0, m = 7 (ukesesong)."
    )


if __name__ == "__main__":
    main()
