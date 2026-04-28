"""
Steg 1: Datainnsamling for Clark-Scarf multi-echelon
=====================================================
Genererer parametere for et 2-tier distribusjonssystem med ett sentrallager
(node 0) og fire regionlagre (node 1-4) hos en norsk farmasidistributor.

For hver region: daglig etterspørsel (normalfordelt), ledetid fra sentrallager,
og lokale lager-, bestillings- og mangelkostnader.

Figurer:
- echelon_network.png  (nettverksdiagram)
- echelon_demand_profile.png  (daglig etterspørsel per region)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

SEED = 4242

# Color scheme
S_FILLS = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
S_DARKS = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]
PRIMARY = "#1F6587"
INKMUTED = "#556270"
INK = "#1F2933"


def get_network_parameters() -> dict:
    """Parametere for Clark-Scarf-nettverket.

    Sentrallager: indeks 0
    Regionlagre: indeks 1..N
    """
    rng = np.random.default_rng(SEED)

    N = 4  # antall regionlagre

    # Regionsnavn (norske byer)
    regioner = ["Oslo", "Bergen", "Trondheim", "Tromsø"]

    # Daglig etterspørsel per region (enheter/dag): normalfordelt
    mu_d = np.array([85.0, 62.0, 45.0, 30.0])
    sigma_d = np.array([22.0, 18.0, 14.0, 11.0])

    # Ledetid sentrallager -> regionlager (dager)
    L_reg = np.array([2.0, 3.0, 4.0, 5.0])

    # Ledetid leverandør -> sentrallager (dager)
    L_sentral = 7.0

    # Kostnadsparametere per enhet (felles produkt)
    c = 120.0  # innkj\o pspris per enhet (NOK)

    # Echelon-holdekostnader: h0 < h1 ...
    # Installasjonsholdekost per enhet per dag
    h_install = np.array([
        0.015,  # sentral (lav)
        0.030,  # region 1
        0.032,  # region 2
        0.034,  # region 3
        0.036,  # region 4
    ]) * c  # = NOK per enhet per dag lagret
    # => h0=1.80, h_reg ~ 3.6-4.3 NOK/enhet/dag

    # Mangelkostnad per enhet per periode (backorder), kun regionlagre
    # (sentrallageret har intern backorder behandlet av modellen)
    b_region = 28.0  # NOK per enhet (tapt kunde / ekspress)

    # Periodisk gjennomgang; R = 1 dag (daglig gjennomgang)
    R = 1.0

    # Echelon holdekost: h^e_i = h_install_i - h_install_parent
    # For sentrallageret er "parent" leverandoren med pris = 0
    h_ech = np.zeros(N + 1)
    h_ech[0] = h_install[0]
    for i in range(1, N + 1):
        h_ech[i] = h_install[i] - h_install[0]

    params = {
        "N": N,
        "regioner": regioner,
        "mu_d": mu_d.tolist(),
        "sigma_d": sigma_d.tolist(),
        "L_reg": L_reg.tolist(),
        "L_sentral": L_sentral,
        "c": c,
        "h_install": h_install.tolist(),
        "h_ech": h_ech.tolist(),
        "b_region": b_region,
        "R": R,
        "seed": SEED,
    }
    # Total daglig etterspørsel ved sentrallager
    params["mu_D0"] = float(mu_d.sum())
    params["sigma_D0"] = float(np.sqrt(np.sum(sigma_d ** 2)))
    return params


def plot_network(params: dict, output_path: Path) -> None:
    """Nettverksdiagram: sentrallager + 4 regionlagre."""
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.set_aspect("equal")
    ax.axis("off")

    # Leverandør
    lev_xy = (0.8, 3.0)
    ax.add_patch(
        patches.FancyBboxPatch(
            (lev_xy[0] - 0.55, lev_xy[1] - 0.45), 1.1, 0.9,
            boxstyle="round,pad=0.04", linewidth=1.8,
            edgecolor=INKMUTED, facecolor="#F4F7FB",
        )
    )
    ax.text(lev_xy[0], lev_xy[1], "Leverand\u00f8r", ha="center", va="center",
            fontsize=10, color=INK)

    # Sentrallager
    sent_xy = (3.7, 3.0)
    ax.add_patch(
        patches.FancyBboxPatch(
            (sent_xy[0] - 0.7, sent_xy[1] - 0.5), 1.4, 1.0,
            boxstyle="round,pad=0.04", linewidth=2.0,
            edgecolor=S_DARKS[0], facecolor=S_FILLS[0],
        )
    )
    ax.text(sent_xy[0], sent_xy[1] + 0.15, "Sentrallager",
            ha="center", va="center", fontsize=10.5,
            fontweight="bold", color=INK)
    ax.text(sent_xy[0], sent_xy[1] - 0.22, r"node $i=0$",
            ha="center", va="center", fontsize=9, color=INKMUTED)

    # Pil leverandor -> sentrallager (med L_sentral)
    ax.annotate(
        "", xy=(sent_xy[0] - 0.72, sent_xy[1]), xytext=(lev_xy[0] + 0.57, lev_xy[1]),
        arrowprops=dict(arrowstyle="->", lw=1.8, color=INKMUTED),
    )
    ax.text(
        (lev_xy[0] + sent_xy[0]) / 2, lev_xy[1] + 0.32,
        rf"$L_0 = {params['L_sentral']:.0f}$ dager",
        ha="center", va="bottom", fontsize=9, color=INKMUTED,
    )

    # Regionlagre (4) langs h\o yre side
    N = params["N"]
    region_x = 7.5
    region_ys = np.linspace(0.8, 5.2, N)[::-1]  # fra topp til bunn
    for i, (y, region) in enumerate(zip(region_ys, params["regioner"])):
        # box
        ax.add_patch(
            patches.FancyBboxPatch(
                (region_x - 0.8, y - 0.35), 1.6, 0.7,
                boxstyle="round,pad=0.03", linewidth=1.5,
                edgecolor=S_DARKS[1], facecolor=S_FILLS[1],
            )
        )
        ax.text(region_x, y + 0.07, region, ha="center", va="center",
                fontsize=9.5, fontweight="bold", color=INK)
        ax.text(region_x, y - 0.15,
                f"$i={i+1}$, $L_{i+1}={params['L_reg'][i]:.0f}$ d",
                ha="center", va="center", fontsize=8, color=INKMUTED)

        # Pil sentral -> region
        ax.annotate(
            "", xy=(region_x - 0.82, y),
            xytext=(sent_xy[0] + 0.72, sent_xy[1]),
            arrowprops=dict(arrowstyle="->", lw=1.4, color=S_DARKS[0], alpha=0.75),
        )

        # Kundeetterspørsel-pil
        ax.annotate(
            "", xy=(region_x + 1.65, y), xytext=(region_x + 0.82, y),
            arrowprops=dict(arrowstyle="->", lw=1.3, color=S_DARKS[4]),
        )
        ax.text(region_x + 1.73, y,
                rf"$D_{{{i+1},t}}\sim\mathcal{{N}}({params['mu_d'][i]:.0f}, {params['sigma_d'][i]:.0f}^2)$",
                ha="left", va="center", fontsize=8, color=INK)

    # Title labels above
    ax.text(3.7, 5.5, "Tier 1", ha="center", fontsize=10,
            fontweight="bold", color=S_DARKS[0])
    ax.text(7.5, 5.7, "Tier 2", ha="center", fontsize=10,
            fontweight="bold", color=S_DARKS[1])

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_demand_profile(params: dict, output_path: Path) -> None:
    """Bar chart: daglig etterspørsel (mu_d, sigma_d) per region."""
    fig, ax = plt.subplots(figsize=(8, 4.0))
    mu = np.array(params["mu_d"])
    sig = np.array(params["sigma_d"])
    regioner = params["regioner"]
    x = np.arange(len(regioner))

    bars = ax.bar(x, mu, color=S_FILLS[1], edgecolor=S_DARKS[1],
                  label=r"$\mu_{d_i}$", zorder=3)
    ax.errorbar(x, mu, yerr=sig, fmt="none",
                ecolor=S_DARKS[4], capsize=5, lw=1.5,
                label=r"$\pm\sigma_{d_i}$", zorder=4)

    # Sentrallager aggregert (referansebar)
    ax.axhline(params["mu_D0"], color=S_DARKS[0], linestyle="--",
               lw=1.3,
               label=rf"$\mu_{{D_0}}={params['mu_D0']:.0f}$ (sentralt)")

    for bar, m in zip(bars, mu):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                f"{m:.0f}", ha="center", va="bottom", fontsize=9, color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels(regioner, fontsize=10)
    ax.set_ylabel("Enheter / dag", fontsize=11)
    ax.set_title("Daglig etterspørsel per region", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y", zorder=0)
    ax.legend(fontsize=9, loc="upper right")
    ax.set_ylim(0, max(mu) + max(sig) + 30)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING - CLARK-SCARF NETTVERK")
    print("=" * 60)

    params = get_network_parameters()

    # Oppsummering
    print(f"\nAntall regionlagre: {params['N']}")
    print(f"Regioner: {params['regioner']}")
    print(f"Ledetid leverandor->sentrallager: {params['L_sentral']:.1f} dager")
    print("Ledetid sentrallager->region:",
          [f"{L:.1f}" for L in params["L_reg"]])
    print(f"Daglig etterspørsel (sentralt aggregert): "
          f"mu={params['mu_D0']:.1f}, sigma={params['sigma_D0']:.2f}")

    # Lagre parametere
    params_path = OUTPUT_DIR / "step01_parameters.json"
    with open(params_path, "w", encoding="utf-8") as f:
        json.dump(params, f, indent=2, ensure_ascii=False)
    print(f"\nParametere lagret: {params_path}")

    # Tabell i data/
    df = pd.DataFrame({
        "region_id": list(range(1, params["N"] + 1)),
        "region": params["regioner"],
        "mu_d": params["mu_d"],
        "sigma_d": params["sigma_d"],
        "L_reg": params["L_reg"],
        "h_install": params["h_install"][1:],
        "h_ech": params["h_ech"][1:],
    })
    df.to_csv(DATA_DIR / "regioner.csv", index=False)
    print(f"Tabell lagret: {DATA_DIR / 'regioner.csv'}")

    # Figurer
    plot_network(params, OUTPUT_DIR / "echelon_network.png")
    plot_demand_profile(params, OUTPUT_DIR / "echelon_demand_profile.png")

    print("\nFerdig med steg 1.\n")


if __name__ == "__main__":
    main()
