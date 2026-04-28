"""
Steg 1: Datainnsamling for slotting-eksempel
=============================================
Genererer et syntetisk datasett for et parallell-gang-lager:

- 400 SKU-er med Pareto-fordelt plukkfrekvens
- Lageret er et enkelt rektangulaer grid (10 ganger x 20 hyllekolonner)
- Pakkestasjonen ligger i nedre venstre hjorne (0, 0)
- Plukkhistorikk for 90 dager, med i gjennomsnitt ~350 plukklinjer per dag

Alle resultater skrives til output/ som CSV og JSON for senere steg.
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

# Lagerparametere
N_SKU = 400          # antall produkter
N_AISLES = 10        # antall ganger
N_COLS = 20          # antall hyllekolonner per side av en gang
AISLE_WIDTH = 2.5    # meter (sentrum til sentrum)
COL_WIDTH = 1.0      # meter per hyllekolonne
PICK_HEADER = 3.0    # meter fra gangende til hvor man borjer plukke
N_DAYS = 90          # antall dager med historikk
AVG_LINES_PER_DAY = 350

# Pakkestasjonen ligger i punkt (0,0) - utenfor alle ganger
PACK_X = 0.0
PACK_Y = 0.0


def build_layout(n_aisles: int = N_AISLES, n_cols: int = N_COLS) -> pd.DataFrame:
    """Bygger tabell over alle lokasjoner i lageret.

    Hver lokasjon er et tuppel (aisle, col, side), dvs. gang, kolonne og
    side (venstre/hoyre). Pakkestasjonen er ved (0, 0). En plukker kommer
    inn ved sor-enden av en gang (y = PICK_HEADER) og gaar rett nordover.
    Plukkavstanden beregnes som rettvinklet (Manhattan) distanse fra
    pakkestasjonen til midten av lokasjonen.
    """
    rows = []
    for aisle in range(n_aisles):
        # Sentrum av gang langs x-aksen
        x_center = AISLE_WIDTH / 2.0 + aisle * AISLE_WIDTH
        for col in range(n_cols):
            for side in ("L", "R"):
                # Y-koordinat: 1. kolonne naer pakkestasjon
                y = PICK_HEADER + (col + 0.5) * COL_WIDTH
                # Sidejustering -- side paavirker ikke avstand nevneverdig,
                # men holder fysisk utseende.
                rows.append(
                    {
                        "aisle": aisle,
                        "col": col,
                        "side": side,
                        "x": x_center,
                        "y": y,
                    }
                )
    df = pd.DataFrame(rows)
    # Manhattan-distanse (enkel-veis) fra pakkestasjon til lokasjon:
    # gaa ut langs x-aksen til riktig gang, saa nordover til lokasjon,
    # og til slutt tilbake samme vei.
    df["d_one_way"] = df["x"] + df["y"]
    df["d_round_trip"] = 2.0 * df["d_one_way"]
    df["slot_id"] = [f"A{a:02d}-C{c:02d}-{s}" for a, c, s in
                     zip(df["aisle"], df["col"], df["side"])]
    df = df[["slot_id", "aisle", "col", "side", "x", "y",
             "d_one_way", "d_round_trip"]]
    return df


def generate_pick_frequency(
    n_sku: int = N_SKU, seed: int = SEED
) -> np.ndarray:
    """Generer Pareto-fordelt plukkfrekvens (plukklinjer per dag).

    Bruker en Pareto(alpha=1.16) fordeling, skalert slik at totalen tilsvarer
    AVG_LINES_PER_DAY. Dette gir den klassiske 80/20-fordelingen:
    omtrent 20% av SKU-ene staar for ~80% av plukkene.
    """
    rng = np.random.default_rng(seed)
    # Pareto-lik lognormal-fordeling gir en realistisk lang hale uten at
    # klasse C blir tom ved standard 70/20/10-grenser. sigma = 1.7 gir
    # en typisk lagerkonsentrasjon hvor top 20 % av SKU-ene dekker ca 75 %
    # av plukkene (noe skarpere enn klassisk 80/20, i trad med Pareto-
    # fordelingen for raske omloperselgere).
    raw = rng.lognormal(mean=0.0, sigma=1.7, size=n_sku)
    # Skaler til onsket sum
    freq = raw / raw.sum() * AVG_LINES_PER_DAY
    # Sorter synkende
    freq = np.sort(freq)[::-1]
    return freq


def simulate_pick_history(
    frequencies: np.ndarray, n_days: int = N_DAYS, seed: int = SEED + 1
) -> pd.DataFrame:
    """Simulerer daglig plukkhistorikk: for hver SKU og dag antas antallet
    plukklinjer aa folge en Poisson-fordeling med gjennomsnitt lik daglig
    plukkfrekvens.
    """
    rng = np.random.default_rng(seed)
    n_sku = len(frequencies)
    counts = rng.poisson(lam=frequencies[None, :], size=(n_days, n_sku))
    rows = []
    for sku_idx, total in enumerate(counts.sum(axis=0)):
        rows.append(
            {
                "sku_id": f"S{sku_idx+1:04d}",
                "daglig_freq": float(frequencies[sku_idx]),
                "plukk_90d": int(total),
            }
        )
    return pd.DataFrame(rows)


def plot_pareto(df: pd.DataFrame, output_path: Path) -> None:
    """Pareto-kurve: kumulativ andel plukk vs andel SKU-er."""
    sorted_freq = np.sort(df["plukk_90d"].values)[::-1]
    cum = np.cumsum(sorted_freq) / sorted_freq.sum()
    sku_pct = np.arange(1, len(sorted_freq) + 1) / len(sorted_freq)

    fig, ax = plt.subplots(figsize=(8.5, 4.5))
    ax.plot(sku_pct * 100, cum * 100, color=PRIMARY, lw=2.2,
            label="Kumulativ plukkandel")
    # Reference 80/20 line
    ax.axvline(20, color=S_DARKS[2], ls=":", lw=1.4, alpha=0.75)
    ax.axhline(80, color=S_DARKS[2], ls=":", lw=1.4, alpha=0.75)
    # Finn faktisk kumulativ verdi ved 20% av SKU-ene
    idx20 = int(np.ceil(0.20 * len(sorted_freq))) - 1
    pct_at_20 = cum[idx20] * 100
    ax.plot([20], [pct_at_20], "o", color=S_DARKS[4], markersize=8,
            label=f"20 % SKU → {pct_at_20:.1f} % plukk")

    ax.set_xlabel("Andel SKU-er (%)", fontsize=11)
    ax.set_ylabel("Kumulativ andel plukk (%)", fontsize=11)
    ax.set_title("Pareto-fordeling av plukkfrekvens (400 SKU-er, 90 dager)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.legend(loc="lower right", fontsize=10)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_layout(slots: pd.DataFrame, output_path: Path) -> None:
    """Viser layout-planen med pakkestasjonen som rod sirkel."""
    fig, ax = plt.subplots(figsize=(9, 5.5))
    for aisle in sorted(slots["aisle"].unique()):
        sub = slots[slots["aisle"] == aisle]
        ax.scatter(sub["x"], sub["y"], s=8, color=S_FILLS[0],
                   edgecolor=S_DARKS[0], linewidth=0.4)
    # Pakkestasjon
    ax.plot([PACK_X], [PACK_Y], marker="s", markersize=14,
            color=S_DARKS[4], markeredgecolor="black")
    ax.annotate("Pakkestasjon", xy=(PACK_X, PACK_Y), xytext=(1.2, -0.8),
                fontsize=10, color=S_DARKS[4], fontweight="bold")
    ax.set_xlabel("x (m)", fontsize=11)
    ax.set_ylabel("y (m)", fontsize=11)
    ax.set_title("Lagerlayout: 10 ganger x 20 kolonner x 2 sider (400 slots)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(-1, AISLE_WIDTH * N_AISLES + 1)
    ax.set_ylim(-2, PICK_HEADER + N_COLS * COL_WIDTH + 1)
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

    # 1. Lageret
    slots = build_layout()
    print(f"Antall slots: {len(slots)}")
    print(f"Maksdistanse (round trip): {slots['d_round_trip'].max():.2f} m")
    print(f"Mindistanse (round trip): {slots['d_round_trip'].min():.2f} m")
    slots.to_csv(DATA_DIR / "slots.csv", index=False)

    # 2. Plukkfrekvenser
    freq = generate_pick_frequency()
    history = simulate_pick_history(freq)
    history.to_csv(DATA_DIR / "plukkhistorikk.csv", index=False)

    # Oppsummering
    total_picks = int(history["plukk_90d"].sum())
    top20 = history.nlargest(int(0.2 * len(history)), "plukk_90d")[
        "plukk_90d"
    ].sum()
    print(f"Totalt plukklinjer over 90 dager: {total_picks:,}")
    print(f"  Top 20% SKU-er: {top20:,} plukk "
          f"({top20 / total_picks * 100:.1f}% av total)")

    summary = {
        "antall_sku": int(len(history)),
        "antall_slots": int(len(slots)),
        "antall_dager": int(N_DAYS),
        "plukkhistorikk_total": total_picks,
        "gjennomsnitt_plukk_per_dag": float(round(total_picks / N_DAYS, 1)),
        "maks_sku_frekvens_90d": int(history["plukk_90d"].max()),
        "median_sku_frekvens_90d": int(history["plukk_90d"].median()),
        "andel_plukk_top20": float(round(top20 / total_picks * 100, 1)),
        "maks_round_trip_m": float(round(slots["d_round_trip"].max(), 2)),
        "min_round_trip_m": float(round(slots["d_round_trip"].min(), 2)),
        "gj_round_trip_m": float(round(slots["d_round_trip"].mean(), 2)),
    }
    summary_path = OUTPUT_DIR / "step01_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"Sammendrag lagret: {summary_path}")

    # 3. Figurer
    plot_pareto(history, OUTPUT_DIR / "slot_pareto.png")
    plot_layout(slots, OUTPUT_DIR / "slot_layout.png")

    print("\nFerdig med steg 1.\n")


if __name__ == "__main__":
    main()
