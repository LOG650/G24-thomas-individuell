"""
Steg 1: Datainnsamling
======================
Genererer syntetisk daglig etterspørsel for L = 4 lokasjoner over
N_total = 360 dager med *korrelert* etterspørsel (positiv korrelasjon
mellom geografisk nære lagre). Data lagres i ``data/`` og en
nettverksfigur lagres i ``output/``.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

LOCATIONS = ["L1", "L2", "L3", "L4"]
N_DAYS = 360
SEED = 20260420

# Per-lokasjon parametre: gj.snitt (mu) og std (sigma) for daglig etterspørsel
LOCATION_PARAMS = {
    "L1": {"mu": 18.0, "sigma": 5.5, "leadtime_days": 2},
    "L2": {"mu": 22.0, "sigma": 6.5, "leadtime_days": 3},
    "L3": {"mu": 14.0, "sigma": 4.5, "leadtime_days": 2},
    "L4": {"mu": 26.0, "sigma": 7.5, "leadtime_days": 4},
}

# Par-vis korrelasjonsmatrise (nærliggende lagre er høyere korrelert)
CORRELATION = np.array(
    [
        [1.00, 0.55, 0.35, 0.20],
        [0.55, 1.00, 0.40, 0.25],
        [0.35, 0.40, 1.00, 0.30],
        [0.20, 0.25, 0.30, 1.00],
    ]
)

# Kostnadsparametre (kr/enhet).
#
# - ``order`` er en liten "ordreprosesseringskost" per bestilt enhet
#   (selve produktkost er utenfor modellen siden salgsprisen dekker
#   den -- vi optimerer *merkost* ved politikk).
# - ``holding`` er lagerkost per enhet per dag.
# - ``backorder`` er strafkost per enhet som ikke leveres (tapt margin
#   + goodwillskade). Denne mæa være betydelig hoayere enn order
#   for at det skal lonne seg å bestille.
# - ``transship`` er variabel kost per lateralt omlastet enhet.
# - ``fixed_order`` er fast bestillingskost per bestilling
#   (setup/transport).
COST_PARAMS = {
    "order": 12.0,          # per bestilt enhet (prosessering)
    "holding": 2.5,         # per enhet ved slutten av dagen
    "backorder": 95.0,      # per enhet restordre (stockout)
    "transship": 8.0,       # per enhet laterale transshipment mellom lagre
    "fixed_order": 400.0,   # fast bestillingskost per bestilling
}


def generate_demand(seed: int = SEED) -> pd.DataFrame:
    """Genererer korrelert daglig etterspørsel med multivariat Gauss.

    Negative trekk trunkeres til 0 og rundes til heltall.
    """
    rng = np.random.default_rng(seed)
    mus = np.array([LOCATION_PARAMS[l]["mu"] for l in LOCATIONS])
    sigmas = np.array([LOCATION_PARAMS[l]["sigma"] for l in LOCATIONS])

    # Bygg kovariansmatrise fra korrelasjon + std
    cov = CORRELATION * np.outer(sigmas, sigmas)
    samples = rng.multivariate_normal(mus, cov, size=N_DAYS)
    samples = np.clip(np.round(samples), 0, None).astype(int)

    dates = pd.date_range("2025-01-01", periods=N_DAYS, freq="D")
    return pd.DataFrame(samples, columns=LOCATIONS, index=dates)


def plot_network(output_path: Path) -> None:
    """Skjematisk tegning av nettverket (hub-eske leverandør + 4 lagre)."""
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_aspect("equal")

    # Leverandør øverst
    supplier_pos = (0.0, 3.0)
    ax.scatter(*supplier_pos, s=800, c="#8CC8E5", edgecolors="#1F6587", linewidths=2, zorder=3)
    ax.text(supplier_pos[0], supplier_pos[1] + 0.45, "Leverandør", ha="center", fontsize=11)

    # Fire lokasjoner i trekant/kvadrat-formasjon under
    positions = {
        "L1": (-2.2, 0.8),
        "L2": (-0.8, -0.6),
        "L3": (0.8, -0.6),
        "L4": (2.2, 0.8),
    }
    for name, (x, y) in positions.items():
        ax.scatter(x, y, s=700, c="#97D4B7", edgecolors="#307453", linewidths=2, zorder=3)
        ax.text(x, y - 0.05, name, ha="center", va="center", fontsize=10, fontweight="bold")
        mu = LOCATION_PARAMS[name]["mu"]
        lt = LOCATION_PARAMS[name]["leadtime_days"]
        ax.text(x, y - 0.55, rf"$\mu={mu:.0f}$, $L={lt}$d", ha="center", fontsize=9, color="#556270")

        # Leveranse fra leverandør (blå stiplet)
        ax.annotate(
            "",
            xy=(x, y + 0.25),
            xytext=supplier_pos,
            arrowprops=dict(arrowstyle="->", color="#1F6587", lw=1.3, ls="--", alpha=0.6),
            zorder=1,
        )

    # Laterale transshipment-forbindelser (gr\u00f8nne, solid)
    pairs = [("L1", "L2"), ("L2", "L3"), ("L3", "L4"), ("L1", "L3"), ("L2", "L4")]
    for a, b in pairs:
        xa, ya = positions[a]
        xb, yb = positions[b]
        ax.annotate(
            "",
            xy=(xb, yb),
            xytext=(xa, ya),
            arrowprops=dict(arrowstyle="<->", color="#307453", lw=1.2, alpha=0.8),
            zorder=2,
        )

    ax.set_xlim(-4, 4)
    ax.set_ylim(-2, 4.5)
    ax.axis("off")

    # Tegnforklaring
    ax.plot([], [], "--", color="#1F6587", label="Bestilling (stage 1)")
    ax.plot([], [], "-", color="#307453", label="Laterale transshipment (stage 2)")
    ax.legend(loc="lower center", fontsize=10, frameon=False, bbox_to_anchor=(0.5, -0.02))

    ax.set_title("Flerlokasjonsnettverk med lateral transshipment", fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_correlation(df: pd.DataFrame, output_path: Path) -> None:
    """Heatmap over empirisk korrelasjonsmatrise."""
    corr = df.corr().values
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)

    ax.set_xticks(range(len(LOCATIONS)))
    ax.set_yticks(range(len(LOCATIONS)))
    ax.set_xticklabels(LOCATIONS)
    ax.set_yticklabels(LOCATIONS)

    for i in range(len(LOCATIONS)):
        for j in range(len(LOCATIONS)):
            ax.text(j, i, f"{corr[i, j]:.2f}", ha="center", va="center",
                    color="white" if abs(corr[i, j]) > 0.5 else "#1F2933", fontsize=11)

    ax.set_title("Empirisk korrelasjon mellom lokasjoner", fontsize=12, fontweight="bold")
    fig.colorbar(im, ax=ax, shrink=0.8, label=r"$\rho$")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def summary_stats(df: pd.DataFrame) -> dict:
    stats = {}
    for loc in LOCATIONS:
        s = df[loc]
        stats[loc] = {
            "mean": float(round(s.mean(), 2)),
            "std": float(round(s.std(ddof=1), 2)),
            "min": int(s.min()),
            "max": int(s.max()),
            "leadtime_days": LOCATION_PARAMS[loc]["leadtime_days"],
        }
    return stats


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 1: Datainnsamling og nettverksdefinisjon")
    print("=" * 60)

    df = generate_demand()
    df.to_csv(DATA_DIR / "demand.csv", index_label="date")
    print(f"Etterspørselsdata lagret: {DATA_DIR / 'demand.csv'} ({df.shape})")

    # Skriv kostnadsparametre til fil for gjenbruk
    with open(DATA_DIR / "params.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "locations": LOCATIONS,
                "location_params": LOCATION_PARAMS,
                "cost_params": COST_PARAMS,
                "n_days": N_DAYS,
                "seed": SEED,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    stats = summary_stats(df)
    print("\nDeskriptiv statistikk per lokasjon:")
    for loc, s in stats.items():
        print(f"  {loc}: {s}")

    with open(OUTPUT_DIR / "step01_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    plot_network(OUTPUT_DIR / "mlstok_network.png")
    plot_correlation(df, OUTPUT_DIR / "mlstok_demand_correlation.png")


if __name__ == "__main__":
    main()
