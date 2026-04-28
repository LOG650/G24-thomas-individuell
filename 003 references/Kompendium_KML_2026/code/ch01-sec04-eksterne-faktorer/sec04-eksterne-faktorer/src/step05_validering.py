"""
Steg 5: Modellvalidering
========================
Kjører residualdiagnostikk for ARIMAX-modellen fra Steg 4:

  - ACF av residualer
  - Ljung-Box-test ved lag 7, 14 og 21
  - Backtest: hold ut siste 60 dager (inkl. 2 kampanjer), tilpass på resten,
    sammenlign ARIMAX vs. ren SARIMA på predikering av hold-out-perioden.
"""

import json
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.statespace.sarimax import SARIMAX

from step01_datainnsamling import generate_raw_data
from step02_feature_engineering import EXOG_COLS, build_features
from step04_modell_estimering import ORDER, SEASONAL_ORDER

warnings.filterwarnings("ignore")

HOLDOUT_DAYS = 60


def load_models(output_dir: Path) -> tuple[dict, dict]:
    with open(output_dir / "arimax_model.pkl", "rb") as f:
        arimax = pickle.load(f)
    with open(output_dir / "sarima_benchmark_model.pkl", "rb") as f:
        sarima = pickle.load(f)
    return arimax, sarima


def plot_residual_acf(residuals: pd.Series, output_path: Path, lags: int = 28) -> None:
    fig, ax = plt.subplots(figsize=(9, 4))
    plot_acf(residuals.dropna(), lags=lags, ax=ax, alpha=0.05,
             title=r"ACF for residualer $\hat{\varepsilon}_t$ -- ARIMAX")
    ax.axvline(7, color="#961D1C", linestyle="--", linewidth=1, alpha=0.7)
    ax.axvline(14, color="#961D1C", linestyle="--", linewidth=1, alpha=0.5)
    ax.set_xlabel("Lag $k$", fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def run_ljung_box(residuals: pd.Series, lags=(7, 14, 21)) -> pd.DataFrame:
    df = acorr_ljungbox(residuals.dropna(), lags=list(lags), return_df=True)
    return df


def backtest(df_feat: pd.DataFrame, holdout: int = HOLDOUT_DAYS) -> dict:
    """Tilpass ARIMAX og SARIMA på train, predikér hold-out-perioden."""
    n = len(df_feat)
    train = df_feat.iloc[: n - holdout].copy()
    test = df_feat.iloc[n - holdout :].copy()

    y_train = train["salg"].astype(float).values
    y_test = test["salg"].astype(float).values
    X_train = train[EXOG_COLS].astype(float).values
    X_test = test[EXOG_COLS].astype(float).values

    # ARIMAX
    m_x = SARIMAX(
        y_train,
        exog=X_train,
        order=ORDER,
        seasonal_order=SEASONAL_ORDER,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False, maxiter=200)
    fc_x = m_x.forecast(steps=holdout, exog=X_test)

    # SARIMA
    m_s = SARIMAX(
        y_train,
        order=ORDER,
        seasonal_order=SEASONAL_ORDER,
        enforce_stationarity=False,
        enforce_invertibility=False,
    ).fit(disp=False, maxiter=200)
    fc_s = m_s.forecast(steps=holdout)

    err_x = y_test - fc_x
    err_s = y_test - fc_s

    def _metrics(err: np.ndarray, y: np.ndarray) -> dict:
        rmse = float(np.sqrt(np.mean(err ** 2)))
        mae = float(np.mean(np.abs(err)))
        mape = float(np.mean(np.abs(err) / y) * 100)
        return {"RMSE": round(rmse, 2), "MAE": round(mae, 2),
                "MAPE_%": round(mape, 2)}

    return {
        "train_antall": int(len(y_train)),
        "test_antall": int(len(y_test)),
        "ARIMAX": _metrics(err_x, y_test),
        "SARIMA": _metrics(err_s, y_test),
        "dates": test["dato"].values,
        "y_test": y_test,
        "fc_arimax": np.asarray(fc_x),
        "fc_sarima": np.asarray(fc_s),
        "X_test": X_test,
        "t_test": test["t"].values,
    }


def plot_backtest(bt: dict, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(11, 5))
    t = bt["t_test"]
    ax.plot(t, bt["y_test"], "o-", color="#1F6587", linewidth=1.2,
            markersize=3.5, label="Observert")
    ax.plot(t, bt["fc_arimax"], "-", color="#9C540B", linewidth=1.5,
            label=f"ARIMAX  (RMSE {bt['ARIMAX']['RMSE']})")
    ax.plot(t, bt["fc_sarima"], "--", color="#5A2C77", linewidth=1.5,
            label=f"SARIMA  (RMSE {bt['SARIMA']['RMSE']})")

    # Marker kampanjedager i hold-out-perioden
    camp_idx = np.where(bt["X_test"][:, 0] == 1)[0]
    if len(camp_idx) > 0:
        ax.scatter(t[camp_idx], bt["y_test"][camp_idx],
                   color="#F6BA7C", s=120, zorder=4, edgecolor="#9C540B",
                   label="Kampanjedag")

    ax.set_xlabel("$t$ (dag)", fontsize=12)
    ax.set_ylabel("$Y_t$", fontsize=13, rotation=0, labelpad=15)
    ax.set_title("Backtest: ARIMAX vs. SARIMA på de siste 60 dagene",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 5: MODELLVALIDERING")
    print(f"{'=' * 60}")

    arimax, sarima = load_models(output_dir)
    res_x = arimax["results"]

    # Standardiserte innovation-residualer fra state-space-filteret.
    # Vi dropper første 14 observasjoner (burn-in) slik at initialiseringen
    # av filteret ikke dominerer plottene.
    std_resid_raw = res_x.standardized_forecasts_error[0]
    resid = pd.Series(std_resid_raw[14:], name="std_resid").dropna().reset_index(drop=True)
    print(f"\nStandardiserte residualer: n = {len(resid)}, "
          f"mean = {resid.mean():.3f}, std = {resid.std():.3f}")

    # ACF-plot
    plot_residual_acf(resid, output_dir / "arimax_residual_acf.png", lags=28)

    # Ljung-Box
    lb = run_ljung_box(resid, lags=(7, 14, 21))
    print("\n--- Ljung-Box test ---")
    print(lb.to_string(float_format=lambda x: f"{x:.4f}"))

    # Backtest
    print("\n--- Backtest (siste 60 dager) ---")
    df = generate_raw_data()
    df_feat = build_features(df)
    bt = backtest(df_feat, holdout=HOLDOUT_DAYS)
    print(f"  Train: {bt['train_antall']}   Test: {bt['test_antall']}")
    print(f"  ARIMAX: {bt['ARIMAX']}")
    print(f"  SARIMA: {bt['SARIMA']}")

    plot_backtest(bt, output_dir / "arimax_backtest.png")

    # Lagre resultater
    results = {
        "residualer": {
            "antall": int(len(resid)),
            "gjennomsnitt": round(float(resid.mean()), 4),
            "standardavvik": round(float(resid.std()), 4),
        },
        "ljung_box": {
            f"lag_{int(lag)}": {
                "Q": round(float(row["lb_stat"]), 3),
                "p": round(float(row["lb_pvalue"]), 5),
            }
            for lag, row in lb.iterrows()
        },
        "backtest": {
            "train_antall": bt["train_antall"],
            "test_antall": bt["test_antall"],
            "ARIMAX": bt["ARIMAX"],
            "SARIMA": bt["SARIMA"],
        },
    }
    with open(output_dir / "validation_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: validation_results.json")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    lb7 = results["ljung_box"]["lag_7"]
    lb14 = results["ljung_box"]["lag_14"]
    print(
        f"  Ljung-Box(7):  Q = {lb7['Q']}, p = {lb7['p']}\n"
        f"  Ljung-Box(14): Q = {lb14['Q']}, p = {lb14['p']}\n"
        f"  Backtest RMSE: ARIMAX = {bt['ARIMAX']['RMSE']} "
        f"vs. SARIMA = {bt['SARIMA']['RMSE']} -> ARIMAX "
        f"{(1 - bt['ARIMAX']['RMSE'] / bt['SARIMA']['RMSE']) * 100:.0f}% bedre."
    )


if __name__ == "__main__":
    main()
