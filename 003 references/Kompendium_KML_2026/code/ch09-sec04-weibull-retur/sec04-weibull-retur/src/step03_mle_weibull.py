"""
Steg 3: MLE-estimering av Weibull-fordelingen
=============================================
Estimerer Weibull-parametrene (beta, eta) fra de observerte levetidene
ved hjelp av Maximum Likelihood Estimation.

Vi håndterer garantisensurering eksplisitt: for enheter solgt i måned s
der den observerte tidshorisonten er T - s måneder (T = siste måned i
datasettet), er risikovinduet min(T - s, 24). Alle enheter som ikke
returneres innen dette vinduet er høyresensurert.

Log-likelihood for Weibull(beta, eta):

    L(beta, eta) = sum_{i in feilet} log f(tau_i; beta, eta)
                 + sum_{j in censurert} log S(c_j; beta, eta)

der f er tetthetsfunksjonen og S overlevelsesfunksjonen.

Konfidensintervall utledes fra inversen av den observerte informasjonen
(negativ Hessian) evaluert i MLE-punktet.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import weibull_min

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

N_MONTHS = 48
WARRANTY_MONTHS = 24


def build_observations(units: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Bygg observasjoner (t_i, delta_i) der delta_i = 1 hvis feilet, 0 hvis sensurert.

    For enheter solgt i maaned s er risikovinduet
        c_s = min(N_MONTHS - s, WARRANTY_MONTHS).

    Returnerer:
      times  - observert tid (levetid hvis feilet, sensur-tid hvis ikke)
      events - 1 for feilet, 0 for sensurert
    """
    times, events = [], []
    for _, row in units.iterrows():
        s = int(row["salgsmaaned"])
        cens_window = min(N_MONTHS - s, WARRANTY_MONTHS)
        if cens_window <= 0:
            continue
        if bool(row["returnert"]) and float(row["levetid"]) <= cens_window:
            times.append(float(row["levetid"]))
            events.append(1)
        else:
            times.append(float(cens_window))
            events.append(0)
    return np.asarray(times), np.asarray(events, dtype=int)


def neg_log_likelihood(params: np.ndarray, times: np.ndarray, events: np.ndarray) -> float:
    """Negativ log-likelihood for Weibull med høyresensurering."""
    beta, eta = params
    if beta <= 0 or eta <= 0:
        return 1e12
    # weibull_min med c=beta, scale=eta: f(t) og S(t) = 1 - F(t)
    logf = weibull_min.logpdf(times, c=beta, scale=eta)
    logS = weibull_min.logsf(times, c=beta, scale=eta)
    ll = np.where(events == 1, logf, logS).sum()
    return -ll


def fit_weibull(times: np.ndarray, events: np.ndarray) -> dict:
    """Fit Weibull-parametre via numerisk MLE. Gir punktestimat og CI."""
    # Startverdier: bruk observerte verdier, anta beta~1
    obs_mean = max(np.mean(times[events == 1]) if (events == 1).any() else np.mean(times), 1.0)
    x0 = np.array([1.5, obs_mean])

    res = minimize(
        neg_log_likelihood,
        x0=x0,
        args=(times, events),
        method="Nelder-Mead",
        options={"xatol": 1e-6, "fatol": 1e-8, "maxiter": 5000},
    )
    beta_hat, eta_hat = res.x
    nll_value = float(res.fun)

    # Observasjonsbasert informasjonsmatrise via numerisk Hessian
    hess = _numerical_hessian(lambda p: neg_log_likelihood(p, times, events), res.x)
    try:
        cov = np.linalg.inv(hess)
        se = np.sqrt(np.diag(cov))
    except np.linalg.LinAlgError:
        se = np.array([np.nan, np.nan])

    z = 1.96
    ci_beta = (beta_hat - z * se[0], beta_hat + z * se[0])
    ci_eta = (eta_hat - z * se[1], eta_hat + z * se[1])

    return {
        "beta_hat": float(beta_hat),
        "eta_hat": float(eta_hat),
        "se_beta": float(se[0]),
        "se_eta": float(se[1]),
        "ci_beta": (float(ci_beta[0]), float(ci_beta[1])),
        "ci_eta": (float(ci_eta[0]), float(ci_eta[1])),
        "log_likelihood": -nll_value,
        "n_failed": int((events == 1).sum()),
        "n_censored": int((events == 0).sum()),
        "n_total": int(len(events)),
    }


def _numerical_hessian(f, x, eps: float = 1e-4) -> np.ndarray:
    """Beregner en to-punkts Hessian via sentrerte differanser."""
    n = len(x)
    H = np.zeros((n, n))
    fx = f(x)
    for i in range(n):
        for j in range(i, n):
            x_pp = x.copy(); x_pp[i] += eps; x_pp[j] += eps
            x_pm = x.copy(); x_pm[i] += eps; x_pm[j] -= eps
            x_mp = x.copy(); x_mp[i] -= eps; x_mp[j] += eps
            x_mm = x.copy(); x_mm[i] -= eps; x_mm[j] -= eps
            if i == j:
                # diagonal
                H[i, i] = (f(x + eps * np.eye(n)[i]) - 2 * fx + f(x - eps * np.eye(n)[i])) / (eps ** 2)
            else:
                val = (f(x_pp) - f(x_pm) - f(x_mp) + f(x_mm)) / (4 * eps ** 2)
                H[i, j] = val
                H[j, i] = val
    return H


def plot_mle_fit(times: np.ndarray, events: np.ndarray, beta: float, eta: float, path: Path) -> None:
    """Visualiser den tilpassede Weibull-fordelingen mot den empiriske tettheten."""
    failed_times = times[events == 1]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    bins = np.arange(0, 25, 1)
    ax.hist(failed_times, bins=bins, density=True, color="#97D4B7",
            edgecolor="#307453", linewidth=0.8, alpha=0.85, label="Empirisk tetthet (feilede)")
    grid = np.linspace(0.01, 24, 400)
    pdf = weibull_min.pdf(grid, c=beta, scale=eta)
    ax.plot(grid, pdf, color="#1F6587", linewidth=2.5,
            label=f"Tilpasset Weibull ($\\hat\\beta$={beta:.2f}, $\\hat\\eta$={eta:.2f})")
    ax.set_xlabel("Levetid $\\tau$ (måneder)", fontsize=13)
    ax.set_ylabel("Tetthet $f(\\tau)$", fontsize=13)
    ax.set_title("Weibull-MLE tilpasset observerte levetider", fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("STEG 3: MLE-ESTIMERING AV WEIBULL")
    print("=" * 60)

    units = pd.read_csv(DATA_DIR / "returns_units.csv")
    times, events = build_observations(units)

    fit = fit_weibull(times, events)
    print(f"n (totalt)                 : {fit['n_total']}")
    print(f"n feilet                   : {fit['n_failed']}")
    print(f"n sensurert                : {fit['n_censored']}")
    print(f"\\hat beta                 : {fit['beta_hat']:.4f}   (SE {fit['se_beta']:.4f})")
    print(f"\\hat eta                  : {fit['eta_hat']:.4f}   (SE {fit['se_eta']:.4f})")
    print(f"95% KI for beta             : [{fit['ci_beta'][0]:.4f}, {fit['ci_beta'][1]:.4f}]")
    print(f"95% KI for eta              : [{fit['ci_eta'][0]:.4f}, {fit['ci_eta'][1]:.4f}]")
    print(f"Log-likelihood              : {fit['log_likelihood']:.3f}")

    plot_mle_fit(times, events, fit["beta_hat"], fit["eta_hat"],
                 OUTPUT_DIR / "weib_mle_fit.png")

    # Serialiser
    serialisable = {k: (list(v) if isinstance(v, tuple) else v) for k, v in fit.items()}
    with open(OUTPUT_DIR / "step03_results.json", "w", encoding="utf-8") as f:
        json.dump(serialisable, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
