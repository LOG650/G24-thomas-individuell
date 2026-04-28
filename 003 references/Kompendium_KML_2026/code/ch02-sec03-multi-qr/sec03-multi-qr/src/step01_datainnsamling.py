"""
Steg 1: Datainnsamling for flerprodukts (Q,R)-analyse
=====================================================
Genererer et syntetisk datasett for 10 produkter som deler lagerkapasitet
og innkjopsbudsjett hos en norsk distributor. For hvert produkt har vi:

- Gjennomsnittlig ukentlig etterspørsel (D)
- Standardavvik i ukentlig etterspørsel (sigma_D)
- Gjennomsnittlig leveringstid i uker (L)
- Standardavvik i leveringstid (sigma_L)
- Enhetspris (c)
- Bestillingskostnad per ordre (K)
- Lagerholdsrente (h) -- brok av c per ar
- Straffekostnad per mangel (pi)
- Volum per enhet (v_i) -- til kapasitetsskranke
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

SEED = 2026

# Seriefarger fra book-color-scheme (infographics)
S_FILLS = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
S_DARKS = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]
PRIMARY = "#1F6587"
INKMUTED = "#556270"


def generate_products(n: int = 10, seed: int = SEED) -> pd.DataFrame:
    """Generer syntetiske produktparametere for en distributor.

    Returner en DataFrame med en rad per produkt og kolonner:
    produkt_id, kategori, mu_D (ukentlig etterspørsel), sigma_D,
    mu_L (leveringstid i uker), sigma_L, c (enhetspris i NOK),
    K (bestillingskost NOK/ordre), h (lagerholdsrente 1/ar),
    pi (straffekostnad NOK/mangel), v (volum m^3/enhet).
    """
    rng = np.random.default_rng(seed)
    kategorier = [
        "Standard verktoy", "Sikkerhetsutstyr", "El-komponenter",
        "Smoreolje", "Pakning", "Filter", "Bolter", "Lagerbox",
        "Hanske", "Verneutstyr",
    ]
    kategorier = kategorier[:n]

    # Etterspørselsnivaa varierer over produkter (ABC-lignende spredning).
    mu_D = rng.uniform(40, 400, size=n)
    # Variasjonskoeffisient mellom 0.2 og 0.55.
    cv_D = rng.uniform(0.20, 0.55, size=n)
    sigma_D = cv_D * mu_D

    # Leveringstid (uker): gjennomsnitt 1-4 uker, std 10-25%.
    mu_L = rng.uniform(1.0, 4.0, size=n)
    sigma_L = rng.uniform(0.10, 0.25, size=n) * mu_L

    # Enhetspris (NOK): 50 - 2500, priser positivt korrelert med volumverdi.
    c = rng.uniform(50, 2500, size=n)
    # Bestillingskost: 400-1200 NOK per ordre (administrasjon + transport-setup).
    K = rng.uniform(400, 1200, size=n)
    # Lagerholdsrente: 20-30% pr ar (kapital + forsikring + svinn).
    h = rng.uniform(0.20, 0.30, size=n)
    # Straffekostnad per mangel: 0.5 - 1.5 x enhetspris (mistet dekningsbidrag).
    pi = rng.uniform(0.5, 1.5, size=n) * c
    # Volum m^3 per enhet: 0.002 - 0.08 m^3 (smaa til mellomstore artikler).
    v = rng.uniform(0.002, 0.08, size=n)

    df = pd.DataFrame(
        {
            "produkt_id": [f"P{i+1:02d}" for i in range(n)],
            "kategori": kategorier,
            "mu_D": np.round(mu_D, 1),
            "sigma_D": np.round(sigma_D, 2),
            "mu_L": np.round(mu_L, 2),
            "sigma_L": np.round(sigma_L, 3),
            "c": np.round(c, 1),
            "K": np.round(K, 0),
            "h": np.round(h, 3),
            "pi": np.round(pi, 1),
            "v": np.round(v, 4),
        }
    )
    return df


def calculate_summary(df: pd.DataFrame) -> dict:
    """Oppsummeringsstatistikk for hele porteføljen."""
    return {
        "antall_produkter": int(len(df)),
        "total_ukentlig_etterspørsel": float(np.round(df["mu_D"].sum(), 1)),
        "gjennomsnittlig_leveringstid_uker": float(np.round(df["mu_L"].mean(), 2)),
        "gjennomsnittlig_enhetspris_NOK": float(np.round(df["c"].mean(), 1)),
        "gjennomsnittlig_bestillingskost_NOK": float(np.round(df["K"].mean(), 1)),
        "total_lagerverdi_uten_styring_NOK": float(
            np.round((df["mu_D"] * df["mu_L"] * df["c"]).sum(), 0)
        ),
        "total_volum_per_uke_m3": float(np.round((df["mu_D"] * df["v"]).sum(), 2)),
    }


def plot_demand_overview(df: pd.DataFrame, output_path: Path) -> None:
    """To-panel oversikt: etterspørsel (mu_D +/- sigma_D) og leveringstid."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    idx = np.arange(len(df))
    ax = axes[0]
    ax.bar(
        idx, df["mu_D"], color=S_FILLS[0], edgecolor=S_DARKS[0],
        label=r"$\mu_{D_i}$ (gj.snitt)",
    )
    ax.errorbar(
        idx, df["mu_D"], yerr=df["sigma_D"], fmt="none",
        ecolor=S_DARKS[4], capsize=4, label=r"$\pm\sigma_{D_i}$",
    )
    ax.set_xticks(idx)
    ax.set_xticklabels(df["produkt_id"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Enheter / uke", fontsize=11)
    ax.set_title("Ukentlig etterspørsel per produkt", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper right", fontsize=9)

    ax = axes[1]
    ax.bar(
        idx, df["mu_L"], color=S_FILLS[1], edgecolor=S_DARKS[1],
        label=r"$\mu_{L_i}$",
    )
    ax.errorbar(
        idx, df["mu_L"], yerr=df["sigma_L"], fmt="none",
        ecolor=S_DARKS[4], capsize=4, label=r"$\pm\sigma_{L_i}$",
    )
    ax.set_xticks(idx)
    ax.set_xticklabels(df["produkt_id"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Uker", fontsize=11)
    ax.set_title("Leveringstid per produkt", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(loc="upper right", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_portfolio_value(df: pd.DataFrame, output_path: Path) -> None:
    """Pareto-lignende soylediagram: aarsverdi (c * 52 * mu_D) per produkt."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    arlig_verdi = (df["c"] * df["mu_D"] * 52).values
    order = np.argsort(arlig_verdi)[::-1]
    sorted_ids = df["produkt_id"].values[order]
    sorted_val = arlig_verdi[order] / 1e6  # millioner NOK

    bars = ax.bar(
        sorted_ids, sorted_val, color=S_FILLS[2], edgecolor=S_DARKS[2],
    )
    for bar, v in zip(bars, sorted_val):
        ax.text(
            bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.05,
            f"{v:.1f}", ha="center", va="bottom", fontsize=8, color=INKMUTED,
        )
    ax.set_ylabel("Arlig omsetning (MNOK)", fontsize=11)
    ax.set_xlabel("Produkt", fontsize=11)
    ax.set_title(
        "Omsetning per produkt (sortert)", fontsize=12, fontweight="bold",
    )
    ax.grid(True, alpha=0.3, axis="y")
    plt.xticks(rotation=45, ha="right", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    df = generate_products(n=10, seed=SEED)
    print(f"\nGenererte {len(df)} produkter.")
    print(df.to_string(index=False))

    # Lagre som CSV
    csv_path = DATA_DIR / "produkter.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nDatasett lagret: {csv_path}")

    # Oppsummeringsstatistikk
    summary = calculate_summary(df)
    summary_path = OUTPUT_DIR / "step01_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Sammendrag lagret: {summary_path}")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    # Figurer
    plot_demand_overview(df, OUTPUT_DIR / "multiqr_demand.png")
    plot_portfolio_value(df, OUTPUT_DIR / "multiqr_portfolio_value.png")

    print("\nFerdig med steg 1.\n")


if __name__ == "__main__":
    main()
