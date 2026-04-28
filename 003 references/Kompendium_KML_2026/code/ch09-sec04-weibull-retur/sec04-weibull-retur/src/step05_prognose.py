"""
Steg 5: Prognose for neste 12 måneder
=====================================
Forventede returer i måned t er summen av salg s <= t vektet med
sannsynligheten for at en enhet solgt i måned s returneres i måned t:

    E[R_t] = sum_{s <= t}  S_s * p_{t - s},

der p_k er sannsynligheten for at en enhet har levetid i intervallet
(k-1, k]:  p_k = F(k) - F(k-1).

Vi antar her at kun returer innen garantiperioden (24 mnd) kommer tilbake.

Konfidensintervall produseres ved parametrisk bootstrap: trekk
(beta*, eta*) fra den asymptotiske normalfordelingen til MLE-estimatet,
rekalkuler forventede returer, og ta 2.5/97.5-prosentilene.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import weibull_min

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

N_MONTHS_HIST = 48
HORIZON = 12           # prognose neste 12 mnd
WARRANTY = 24


def return_pmf(k_max: int, beta: float, eta: float) -> np.ndarray:
    """p_k = F(k) - F(k-1) for k = 1..k_max, avkuttet ved garantivinduet."""
    k = np.arange(1, k_max + 1)
    cdf_k = weibull_min.cdf(k, c=beta, scale=eta)
    cdf_km1 = weibull_min.cdf(np.maximum(k - 1, 0), c=beta, scale=eta)
    p = cdf_k - cdf_km1
    p[k > WARRANTY] = 0.0  # returer utenfor garanti observeres ikke
    return p


def convolve_forecast(sales: np.ndarray, beta: float, eta: float,
                      horizon: int = HORIZON) -> np.ndarray:
    """Beregn forventet retur i mnd t = 1..N+horizon basert paa salg og Weibull-pmf."""
    n_total = len(sales) + horizon
    pmf = return_pmf(k_max=n_total, beta=beta, eta=eta)
    expected = np.zeros(n_total)
    for s_idx, S_s in enumerate(sales):
        s = s_idx + 1
        for t in range(s + 1, n_total + 1):
            k = t - s
            if 1 <= k <= WARRANTY:
                expected[t - 1] += S_s * pmf[k - 1]
    return expected


def sales_projection(sales_hist: pd.DataFrame, horizon: int) -> np.ndarray:
    """Forlenger salg naivt som snittet av de siste 6 månedene."""
    last6 = sales_hist["salg"].tail(6).mean()
    return np.full(horizon, round(last6))


def bootstrap_ci(sales_ext: np.ndarray, fit: dict, n_boot: int = 500,
                 rng_seed: int = 11) -> tuple[np.ndarray, np.ndarray]:
    """Parametrisk bootstrap av prognosebanen."""
    rng = np.random.default_rng(rng_seed)
    mean = np.array([fit["beta_hat"], fit["eta_hat"]])
    se = np.array([fit["se_beta"], fit["se_eta"]])

    # Bruk diagonal kovariansmatrise (ingen gjemt korrelasjon); konservativt.
    boot_paths = np.zeros((n_boot, len(sales_ext)))
    for b in range(n_boot):
        beta_b = max(mean[0] + rng.normal(0, se[0]), 1e-3)
        eta_b = max(mean[1] + rng.normal(0, se[1]), 1e-3)
        boot_paths[b] = convolve_forecast(sales_ext, beta_b, eta_b, horizon=0)

    lower = np.quantile(boot_paths, 0.025, axis=0)
    upper = np.quantile(boot_paths, 0.975, axis=0)
    return lower, upper


def plot_forecast(hist_sales: pd.DataFrame, hist_returns: pd.DataFrame,
                  sales_ext: np.ndarray, expected: np.ndarray,
                  ci_low: np.ndarray, ci_hi: np.ndarray, path: Path) -> None:
    n_total = len(sales_ext)
    t_axis = np.arange(1, n_total + 1)

    fig, ax = plt.subplots(figsize=(10.5, 5))
    # Historiske observerte returer
    ax.bar(hist_returns["t"], hist_returns["returer"], color="#8CC8E5",
           edgecolor="#1F6587", linewidth=0.5, label="Observerte returer", alpha=0.9)
    # Forventet retur (modell)
    ax.plot(t_axis, expected, color="#5A2C77", linewidth=2.2,
            label="Forventet retur (Weibull-konvolvert)")
    # Prognoseregion
    forecast_start = N_MONTHS_HIST + 1
    ax.axvspan(forecast_start - 0.5, n_total + 0.5, color="#F4F7FB", alpha=0.7, zorder=0)
    ax.fill_between(t_axis[forecast_start - 1:],
                    ci_low[forecast_start - 1:],
                    ci_hi[forecast_start - 1:],
                    color="#BD94D7", alpha=0.35, label="95 % KI prognose")
    ax.axvline(forecast_start - 0.5, color="#556270", linestyle=":", linewidth=1.3)
    ax.text(forecast_start + 0.3, ax.get_ylim()[1] * 0.95, "Prognose 12 mnd",
            fontsize=10, color="#556270", fontweight="bold")

    ax.set_xlabel("Måned $t$", fontsize=13)
    ax.set_ylabel("Returer", fontsize=13)
    ax.set_title("12-måneders prognose for returer", fontsize=11, fontweight="bold")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("STEG 5: PROGNOSE")
    print("=" * 60)

    sales_df = pd.read_csv(DATA_DIR / "sales.csv")
    returns_df = pd.read_csv(DATA_DIR / "returns_monthly.csv")

    with open(OUTPUT_DIR / "step03_results.json", "r", encoding="utf-8") as f:
        fit = json.load(f)
    beta, eta = fit["beta_hat"], fit["eta_hat"]

    # Forleng salget med naiv prognose for 12 maaneder
    future_sales = sales_projection(sales_df, HORIZON)
    sales_ext = np.concatenate([sales_df["salg"].to_numpy(), future_sales])

    expected = convolve_forecast(sales_ext, beta, eta, horizon=0)
    ci_low, ci_hi = bootstrap_ci(sales_ext, fit)

    plot_forecast(sales_df, returns_df, sales_ext, expected, ci_low, ci_hi,
                  OUTPUT_DIR / "weib_forecast.png")

    # Lagre prognose-tabell
    forecast_start = N_MONTHS_HIST
    forecast_records = []
    for i in range(HORIZON):
        t = forecast_start + i + 1
        forecast_records.append({
            "t": t,
            "salg_projisert": int(future_sales[i]),
            "forventet_retur": round(float(expected[t - 1]), 1),
            "ci_low": round(float(ci_low[t - 1]), 1),
            "ci_high": round(float(ci_hi[t - 1]), 1),
        })
    forecast_tbl = pd.DataFrame(forecast_records)
    forecast_tbl.to_csv(OUTPUT_DIR / "forecast.csv", index=False)

    total_exp = float(sum(r["forventet_retur"] for r in forecast_records))
    total_low = float(sum(r["ci_low"] for r in forecast_records))
    total_hi = float(sum(r["ci_high"] for r in forecast_records))

    with open(OUTPUT_DIR / "step05_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "horizon_months": HORIZON,
            "forecast_sum": round(total_exp, 1),
            "forecast_sum_ci_low": round(total_low, 1),
            "forecast_sum_ci_high": round(total_hi, 1),
            "forecast_by_month": forecast_records,
            "projected_sales": [int(x) for x in future_sales],
        }, f, indent=2, ensure_ascii=False)

    print(f"Forventet sum returer neste 12 mnd: {total_exp:.0f} "
          f"(95 % KI: {total_low:.0f} - {total_hi:.0f})")
    print("Prognosetabell (første 5):")
    print(forecast_tbl.head())


if __name__ == "__main__":
    main()
