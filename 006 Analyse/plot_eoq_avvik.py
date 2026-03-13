"""
Genererer Fig06_EOQ_Avvik.png
EOQ-avviksanalyse – Helse Bergen 2024–2025
To paneler: scatterplot + statusfordeling
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ── Fargar (konsistent med øvrige figurer) ───────────────────────
C_FOR_MANGE = "#B03A2E"   # raud – for mange ordrar
C_OK        = "#D68910"   # oransje – innanfor toleranse
C_FOR_FAA   = "#0B3D8C"   # blå – for få ordrar
C_TITLE     = "#1A2A44"

# ── Parametrar ──────────────────────────────────────────────────
S = 750          # Ordrekostnad per bestilling (NOK)
H_RATE = 0.20    # Lagerhaldskostnad (andel av einingspris)
THRESHOLD = 50   # Toleransegrense (%)
PERIOD_YEARS = 2 # Dataperiode 2024–2025

# ── Les data ─────────────────────────────────────────────────────
df = pd.read_excel(
    r"C:\G24\G24-thomas-individuell\006 analyse\MASTERFILE V1.xlsx",
    sheet_name="MASTERFILE", header=9,
)

# Filtrer til artiklar med naudsynte kolonner
mask = (
    df["D_ANNUAL"].notna() & (df["D_ANNUAL"] > 0)
    & df["UNIT_PRICE"].notna() & (df["UNIT_PRICE"] > 0)
    & df["ORDER_COUNT"].notna() & (df["ORDER_COUNT"] > 0)
)
d = df[mask].copy()

# ── EOQ-berekningar ─────────────────────────────────────────────
d["H"] = d["UNIT_PRICE"] * H_RATE
d["EOQ"] = np.sqrt(2 * d["D_ANNUAL"] * S / d["H"])
d["ORDERS_PER_YEAR"] = d["ORDER_COUNT"] / PERIOD_YEARS
d["EOQ_ORDERS"] = d["D_ANNUAL"] / d["EOQ"]
d["DEV_PCT"] = ((d["ORDERS_PER_YEAR"] - d["EOQ_ORDERS"]) / d["EOQ_ORDERS"]) * 100

# Status
d["EOQ_STATUS"] = "OK"
d.loc[d["DEV_PCT"] > THRESHOLD, "EOQ_STATUS"] = "FOR_MANGE_ORDRER"
d.loc[d["DEV_PCT"] < -THRESHOLD, "EOQ_STATUS"] = "FOR_FÅ_ORDRER"

# Sorter etter avvik for betre visuell lesbarheit
d = d.sort_values("DEV_PCT").reset_index(drop=True)

# Klipp ekstremverdiar for scatterplot (bevar reelle data)
CLIP_LO, CLIP_HI = -150, 500
d["DEV_PLOT"] = d["DEV_PCT"].clip(CLIP_LO, CLIP_HI)

# Statustal
n_mange = (d["EOQ_STATUS"] == "FOR_MANGE_ORDRER").sum()
n_ok    = (d["EOQ_STATUS"] == "OK").sum()
n_faa   = (d["EOQ_STATUS"] == "FOR_FÅ_ORDRER").sum()

# ── Fargar per punkt ─────────────────────────────────────────────
color_map = {
    "FOR_MANGE_ORDRER": C_FOR_MANGE,
    "OK": C_OK,
    "FOR_FÅ_ORDRER": C_FOR_FAA,
}
d["COLOR"] = d["EOQ_STATUS"].map(color_map)

# ── Plot ─────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5),
                                gridspec_kw={"width_ratios": [2.4, 1]})

# ── Panel 1: Scatterplot ────────────────────────────────────────

# Bakgrunnssoner – teikna først (zorder=0)
ax1.axhspan(-THRESHOLD, THRESHOLD, color="#E8E8E8", alpha=0.5,
            zorder=0, label="OK-sone (±50 %)")
ax1.axhspan(THRESHOLD, CLIP_HI + 50, color=C_FOR_MANGE, alpha=0.06,
            zorder=0)
ax1.axhspan(CLIP_LO - 50, -THRESHOLD, color=C_FOR_FAA, alpha=0.06,
            zorder=0)

# Scatterpunktar
ax1.scatter(
    d.index, d["DEV_PLOT"],
    c=d["COLOR"], s=20, alpha=0.6, edgecolors="none", zorder=2,
)

# Referanselinjer
ax1.axhline(y=0, color="#888888", linewidth=0.8, zorder=1)
ax1.axhline(y=THRESHOLD, color=C_FOR_MANGE, linestyle="--",
            linewidth=1.1, alpha=0.55, zorder=1, label=f"+{THRESHOLD} % terskel")
ax1.axhline(y=-THRESHOLD, color=C_FOR_FAA, linestyle="--",
            linewidth=1.1, alpha=0.55, zorder=1, label=f"\u2212{THRESHOLD} % terskel")

ax1.set_xlabel("Artikler (sortert etter avvik)", fontsize=10.5)
ax1.set_ylabel("Avvik fra optimal ordrefrekvens (%)", fontsize=10.5)
ax1.set_title("EOQ-avvik per artikkel", fontsize=11, fontweight="bold",
              color=C_TITLE, pad=8)

ax1.set_xlim(-5, len(d) + 5)
ax1.set_ylim(CLIP_LO - 10, CLIP_HI + 10)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(100))

ax1.grid(axis="y", alpha=0.20, linewidth=0.6)
ax1.set_axisbelow(True)

ax1.legend(fontsize=8, framealpha=0.85, edgecolor="#CCCCCC",
           loc="upper left", borderpad=0.4, handlelength=1.8)

# ── Panel 2: Stolpediagram ──────────────────────────────────────
categories = ["For mange\nordrer", "OK", "For f\u00e5\nordrer"]
counts = [n_mange, n_ok, n_faa]
bar_colors = [C_FOR_MANGE, C_OK, C_FOR_FAA]

bars = ax2.bar(categories, counts, color=bar_colors, width=0.6,
               alpha=0.75, edgecolor="white", linewidth=0.8, zorder=2)

# Verdiar over kvar stolpe
for bar, val in zip(bars, counts):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
             str(val), ha="center", va="bottom",
             fontsize=10.5, fontweight="bold", color=C_TITLE)

ax2.set_ylabel("Antall artikler", fontsize=10.5)
ax2.set_title("EOQ-statusfordeling", fontsize=11, fontweight="bold",
              color=C_TITLE, pad=8)
ax2.set_ylim(0, max(counts) * 1.15)

ax2.grid(axis="y", alpha=0.20, linewidth=0.6)
ax2.set_axisbelow(True)

# ── Hovudtittel ──────────────────────────────────────────────────
fig.suptitle(
    "EOQ-avviksanalyse – Helse Bergen 2024–2025",
    fontsize=12, fontweight="bold", color=C_TITLE, y=0.98,
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.93])
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig06_EOQ_Avvik.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"FOR_MANGE_ORDRER: {n_mange}, OK: {n_ok}, FOR_FÅ_ORDRER: {n_faa}")
print(f"Totalt: {len(d)} artiklar")
