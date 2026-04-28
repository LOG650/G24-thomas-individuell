"""
Steg 6: Backtest og validering
==============================
Holder ut de siste 6 månedene av historikken, estimerer Weibull kun på
tidlige data, og sammenligner modellens forventede retur mot observert
retur i test-perioden. Rapporterer MAE og RMSE.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

# gjenbruker noen funksjoner fra step03/step05
from step03_mle_weibull import build_observations, fit_weibull
from step05_prognose import convolve_forecast

HOLDOUT = 6  # siste 6 mnd
N_MONTHS = 48
WARRANTY = 24


def main() -> None:
    print("=" * 60)
    print("STEG 6: BACKTEST OG VALIDERING")
    print("=" * 60)

    sales_df = pd.read_csv(DATA_DIR / "sales.csv")
    units_all = pd.read_csv(DATA_DIR / "returns_units.csv")
    monthly = pd.read_csv(DATA_DIR / "returns_monthly.csv")

    train_cutoff = N_MONTHS - HOLDOUT
    # For treningsdata: behandle alt som ble registrert etter train_cutoff
    # som ukjent (h0ryresensurer levetider der returmaaned > train_cutoff).
    units_train = units_all.copy()
    retmask = units_train["returnert"].astype(bool) & (units_train["returmaaned"] > train_cutoff)
    units_train.loc[retmask, "returnert"] = False
    units_train.loc[retmask, "returmaaned"] = np.nan

    # Modifisere build_observations' sensureringsvindu: bruk train_cutoff som Tmax
    times = []
    events = []
    for _, row in units_train.iterrows():
        s = int(row["salgsmaaned"])
        cens_window = min(train_cutoff - s, WARRANTY)
        if cens_window <= 0:
            continue
        if bool(row["returnert"]) and float(row["levetid"]) <= cens_window:
            times.append(float(row["levetid"]))
            events.append(1)
        else:
            times.append(float(cens_window))
            events.append(0)
    times = np.asarray(times)
    events = np.asarray(events, dtype=int)

    fit = fit_weibull(times, events)
    beta, eta = fit["beta_hat"], fit["eta_hat"]
    print(f"Trenings-MLE: beta={beta:.3f}, eta={eta:.3f}")

    # Bruk faktisk salg (observert, ikke projisert) i backtest-horisonten
    sales_full = sales_df["salg"].to_numpy()
    expected = convolve_forecast(sales_full, beta, eta, horizon=0)

    # Sammenlign i holdout-perioden
    obs = monthly["returer"].to_numpy()
    pred_ho = expected[train_cutoff:]
    obs_ho = obs[train_cutoff:]

    mae = float(np.mean(np.abs(obs_ho - pred_ho)))
    rmse = float(np.sqrt(np.mean((obs_ho - pred_ho) ** 2)))
    mape = float(np.mean(np.abs((obs_ho - pred_ho) / np.where(obs_ho == 0, 1, obs_ho))) * 100)

    print(f"Backtest (siste {HOLDOUT} mnd):")
    for t, (o, p) in enumerate(zip(obs_ho, pred_ho), start=train_cutoff + 1):
        print(f"  t={t:>2}  obs={o:>4}  pred={p:7.1f}")
    print(f"MAE   = {mae:.2f}")
    print(f"RMSE  = {rmse:.2f}")
    print(f"MAPE  = {mape:.2f} %")

    # Figur
    fig, ax = plt.subplots(figsize=(10.5, 4.5))
    t_axis = np.arange(1, N_MONTHS + 1)
    ax.bar(t_axis, obs, color="#97D4B7", edgecolor="#307453", linewidth=0.5,
           alpha=0.9, label="Observerte returer")
    ax.plot(t_axis[:train_cutoff], expected[:train_cutoff],
            color="#1F6587", linewidth=2.0, alpha=0.7, label="Modell (trening)")
    ax.plot(t_axis[train_cutoff:], expected[train_cutoff:],
            color="#5A2C77", linewidth=2.5, label="Modell (backtest)")
    ax.axvline(train_cutoff + 0.5, color="#556270", linestyle=":", linewidth=1.3)
    ax.set_xlabel("Måned $t$", fontsize=13)
    ax.set_ylabel("Returer", fontsize=13)
    ax.set_title(f"Backtest siste {HOLDOUT} måneder: MAE={mae:.1f}, RMSE={rmse:.1f}",
                 fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "weib_backtest.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {OUTPUT_DIR / 'weib_backtest.png'}")

    # Lagre
    records = [
        {"t": int(train_cutoff + i + 1),
         "observert": int(obs_ho[i]),
         "prediksjon": round(float(pred_ho[i]), 1)}
        for i in range(HOLDOUT)
    ]
    with open(OUTPUT_DIR / "step06_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "holdout_months": HOLDOUT,
            "train_beta": round(beta, 4),
            "train_eta": round(eta, 4),
            "mae": round(mae, 3),
            "rmse": round(rmse, 3),
            "mape_pct": round(mape, 3),
            "per_month": records,
        }, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
