"""
Steg 4: Hazardrate-analyse og tolkning
======================================
Plotter de tre sentrale funksjonene i levetidsanalyse: hazardrate h(t),
tetthet f(t) og kumulativ fordeling F(t) for den estimerte Weibull-modellen.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import weibull_min

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def main() -> None:
    print("=" * 60)
    print("STEG 4: HAZARDRATE-ANALYSE")
    print("=" * 60)

    with open(OUTPUT_DIR / "step03_results.json", "r", encoding="utf-8") as f:
        fit = json.load(f)
    beta = float(fit["beta_hat"])
    eta = float(fit["eta_hat"])

    t = np.linspace(0.01, 36, 400)
    pdf = weibull_min.pdf(t, c=beta, scale=eta)
    cdf = weibull_min.cdf(t, c=beta, scale=eta)
    sf = weibull_min.sf(t, c=beta, scale=eta)
    hazard = (beta / eta) * (t / eta) ** (beta - 1.0)

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.3))
    ax1, ax2, ax3 = axes

    ax1.plot(t, hazard, color="#5A2C77", linewidth=2.5)
    ax1.axvline(24, color="#961D1C", linestyle="--", linewidth=1.2, alpha=0.8, label="Garanti (24 m)")
    ax1.set_title("Hazardrate $h(t)$", fontsize=11, fontweight="bold")
    ax1.set_xlabel("$t$ (måneder)", fontsize=12)
    ax1.set_ylabel("$h(t)$", fontsize=12)
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=9)

    ax2.plot(t, pdf, color="#1F6587", linewidth=2.5)
    ax2.fill_between(t, 0, pdf, color="#8CC8E5", alpha=0.4)
    ax2.axvline(24, color="#961D1C", linestyle="--", linewidth=1.2, alpha=0.8)
    ax2.set_title("Tetthet $f(t)$", fontsize=11, fontweight="bold")
    ax2.set_xlabel("$t$ (måneder)", fontsize=12)
    ax2.set_ylabel("$f(t)$", fontsize=12)
    ax2.grid(True, alpha=0.3)

    ax3.plot(t, cdf, color="#307453", linewidth=2.5, label="$F(t)$")
    ax3.plot(t, sf, color="#9C540B", linewidth=2.5, linestyle="--", label="$S(t) = 1-F(t)$")
    ax3.axvline(24, color="#961D1C", linestyle="--", linewidth=1.2, alpha=0.8)
    ax3.set_title("Kumulativ $F(t)$ og overlevelse $S(t)$", fontsize=11, fontweight="bold")
    ax3.set_xlabel("$t$ (måneder)", fontsize=12)
    ax3.grid(True, alpha=0.3)
    ax3.legend(fontsize=9)

    plt.suptitle(f"Weibull({beta:.2f}, {eta:.2f}): levetidskarakteristikker",
                 fontsize=12, fontweight="bold", y=1.02)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "weib_hazard_curve.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {OUTPUT_DIR / 'weib_hazard_curve.png'}")

    # Nøkkelmål
    mean_life = float(eta * np.exp(np.log(np.pi) / 2.0) if beta == 0 else
                      eta * __import__("math").gamma(1.0 + 1.0 / beta))
    median_life = float(eta * (np.log(2.0)) ** (1.0 / beta))
    mttf = mean_life
    p_fail_24 = float(weibull_min.cdf(24, c=beta, scale=eta))
    p_fail_12 = float(weibull_min.cdf(12, c=beta, scale=eta))
    p_fail_36 = float(weibull_min.cdf(36, c=beta, scale=eta))

    results = {
        "beta": beta,
        "eta": eta,
        "mean_life": round(mean_life, 3),
        "median_life": round(median_life, 3),
        "mttf": round(mttf, 3),
        "p_fail_12": round(p_fail_12, 4),
        "p_fail_24": round(p_fail_24, 4),
        "p_fail_36": round(p_fail_36, 4),
    }
    with open(OUTPUT_DIR / "step04_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"MTTF (forventet levetid): {mean_life:.2f} mnd")
    print(f"Median levetid:           {median_life:.2f} mnd")
    print(f"P(feil innen 12 mnd):     {p_fail_12:.3f}")
    print(f"P(feil innen 24 mnd):     {p_fail_24:.3f}")
    print(f"P(feil innen 36 mnd):     {p_fail_36:.3f}")


if __name__ == "__main__":
    main()
