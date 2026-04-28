"""
Steg 5: Sensitivitetsanalyse
============================
Hvordan varierer koordineringsbesparelsen med
- leverandør-ledetid L_0 (1, 3, 5, 7, 10, 14 dager)
- variabilitet i etterspørsel (skaleringsfaktor 0.5, 1.0, 1.5, 2.0 paa sigma_d)

For hver kombinasjon beregnes analytisk total holdekostnad under begge
politikker og relativ besparelse vises i to heatmap/line-plots.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

OUTPUT_DIR = Path(__file__).parent.parent / "output"

S_FILLS = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
S_DARKS = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]
PRIMARY = "#1F6587"
INKMUTED = "#556270"
INK = "#1F2933"

ALPHA = 0.95


def load_params() -> dict:
    with open(OUTPUT_DIR / "step01_parameters.json", "r", encoding="utf-8") as f:
        return json.load(f)


def compute_costs_for(params: dict, L0: float, sigma_scale: float) -> dict:
    """Beregn analytisk aarlig holdekostnad for begge politikker."""
    mu_d = np.array(params["mu_d"])
    sigma_d = np.array(params["sigma_d"]) * sigma_scale
    L_reg = np.array(params["L_reg"])
    R = params["R"]
    mu_D0 = float(mu_d.sum())
    sigma_D0 = float(np.sqrt(np.sum(sigma_d ** 2)))
    h_install = np.array(params["h_install"])
    h_ech = np.array(params["h_ech"])
    b = params["b_region"]

    # Uavhengig: konservativ naiv (S planlagt for L_0 + L_i + R),
    # men faktisk pipeline = L_i. Overstock = (L_0 + R/2) * mu_d + SS.
    z_uav = norm.ppf(ALPHA)
    L_eff = L0 + L_reg + R
    SS_reg_uav = z_uav * np.sqrt(L_eff * sigma_d ** 2)
    EI_reg_uav = (L0 + 0.5 * R) * mu_d + SS_reg_uav
    SS_0_uav = z_uav * np.sqrt((L0 + R) * sigma_D0 ** 2)
    EI_0_uav = 0.5 * R * mu_D0 + SS_0_uav
    H_uav = (h_install[0] * EI_0_uav +
             np.sum(h_install[1:] * EI_reg_uav)) * 365

    # Clark-Scarf: riktig dimensjonert for L_i + R, faktisk pipeline = L_i.
    # Dermed er EI_i = R/2 * mu_d + SS.
    alpha_reg = b / (b + h_ech[1:])
    z_reg = norm.ppf(alpha_reg)
    SS_reg_cs = z_reg * np.sqrt((L_reg + R) * sigma_d ** 2)
    EI_reg_cs = 0.5 * R * mu_d + SS_reg_cs
    alpha_0 = b / (b + h_ech[0])
    z_0 = norm.ppf(alpha_0)
    SS_0_cs = z_0 * np.sqrt((L0 + R) * sigma_D0 ** 2)
    EI_0_cs = 0.5 * R * mu_D0 + SS_0_cs
    H_cs = (h_install[0] * EI_0_cs +
            np.sum(h_install[1:] * EI_reg_cs)) * 365

    return {
        "L0": L0,
        "sigma_scale": sigma_scale,
        "H_uav": float(H_uav),
        "H_cs": float(H_cs),
        "rel_saving": float((H_uav - H_cs) / H_uav),
    }


def sweep_L0(params: dict, L0_list: list[float]) -> list[dict]:
    return [compute_costs_for(params, L0, 1.0) for L0 in L0_list]


def sweep_sigma(params: dict, scales: list[float]) -> list[dict]:
    return [compute_costs_for(params, params["L_sentral"], s) for s in scales]


def plot_sensitivity(L0_sweep: list[dict], sigma_sweep: list[dict],
                     output_path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    # --- Venstre: vs. L_0 ---
    ax = axes[0]
    L0_arr = np.array([r["L0"] for r in L0_sweep])
    H_uav = np.array([r["H_uav"] for r in L0_sweep]) / 1000
    H_cs = np.array([r["H_cs"] for r in L0_sweep]) / 1000
    ax.plot(L0_arr, H_uav, "o-", color=S_DARKS[0], lw=2,
            markersize=7, label="Uavhengig (s,S)")
    ax.plot(L0_arr, H_cs, "s-", color=S_DARKS[1], lw=2,
            markersize=7, label="Clark-Scarf")
    ax.fill_between(L0_arr, H_cs, H_uav,
                    color=S_FILLS[2], alpha=0.5, label="Besparelse")
    ax.set_xlabel(r"Leverandør-ledetid $L_0$ (dager)", fontsize=11)
    ax.set_ylabel("Holdekostnad (kNOK/aar)", fontsize=11)
    ax.set_title(r"Kostnad vs.\ $L_0$", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc="upper left")

    # --- H\o yre: vs. sigma-skala ---
    ax = axes[1]
    sig_arr = np.array([r["sigma_scale"] for r in sigma_sweep])
    H_uav = np.array([r["H_uav"] for r in sigma_sweep]) / 1000
    H_cs = np.array([r["H_cs"] for r in sigma_sweep]) / 1000
    ax.plot(sig_arr, H_uav, "o-", color=S_DARKS[0], lw=2,
            markersize=7, label="Uavhengig (s,S)")
    ax.plot(sig_arr, H_cs, "s-", color=S_DARKS[1], lw=2,
            markersize=7, label="Clark-Scarf")
    ax.fill_between(sig_arr, H_cs, H_uav,
                    color=S_FILLS[2], alpha=0.5, label="Besparelse")
    ax.set_xlabel(r"Variabilitetsfaktor (x $\sigma_{d_i}$)", fontsize=11)
    ax.set_ylabel("Holdekostnad (kNOK/aar)", fontsize=11)
    ax.set_title(r"Kostnad vs.\ variabilitet", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc="upper left")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 5: SENSITIVITETSANALYSE")
    print("=" * 60)

    params = load_params()

    # Sensitivitet vs L_0
    L0_list = [1.0, 3.0, 5.0, 7.0, 10.0, 14.0]
    L0_sweep = sweep_L0(params, L0_list)
    print("\nL_0  | H_uav (kNOK) | H_cs (kNOK) | Besparelse (%)")
    for r in L0_sweep:
        print(f" {r['L0']:4.1f} | {r['H_uav']/1000:8.0f}     | "
              f"{r['H_cs']/1000:8.0f}   | {r['rel_saving']*100:5.1f}")

    # Sensitivitet vs variabilitet
    scales = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
    sigma_sweep = sweep_sigma(params, scales)
    print("\nSig-skala | H_uav (kNOK) | H_cs (kNOK) | Besparelse (%)")
    for r in sigma_sweep:
        print(f"  {r['sigma_scale']:4.2f}    | {r['H_uav']/1000:8.0f}     | "
              f"{r['H_cs']/1000:8.0f}   | {r['rel_saving']*100:5.1f}")

    plot_sensitivity(L0_sweep, sigma_sweep,
                     OUTPUT_DIR / "echelon_sensitivity.png")

    out = {
        "L0_sweep": L0_sweep,
        "sigma_sweep": sigma_sweep,
    }
    path = OUTPUT_DIR / "step05_sensitivitet.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {path}")
    print("\nFerdig med steg 5.\n")


if __name__ == "__main__":
    main()
