"""
Genererer Fig07_EOQ_Avvik.png
EOQ-avviksanalyse – Helse Bergen 2024–2025
To paneler: scatterplot + statusfordeling
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from fig_style import apply_style, fig_title, COLORS

apply_style()

S = 750
H_RATE = 0.20
THRESHOLD = 50
PERIOD_YEARS = 2

df = pd.read_excel(
    r"C:\G24\G24-thomas-individuell\006 analyse\MASTERFILE V1.xlsx",
    sheet_name="MASTERFILE", header=9,
)

mask = (
    df["D_ANNUAL"].notna() & (df["D_ANNUAL"] > 0)
    & df["UNIT_PRICE"].notna() & (df["UNIT_PRICE"] > 0)
    & df["ORDER_COUNT"].notna() & (df["ORDER_COUNT"] > 0)
)
d = df[mask].copy()

d["H"] = d["UNIT_PRICE"] * H_RATE
d["EOQ"] = np.sqrt(2 * d["D_ANNUAL"] * S / d["H"])
d["ORDERS_PER_YEAR"] = d["ORDER_COUNT"] / PERIOD_YEARS
d["EOQ_ORDERS"] = d["D_ANNUAL"] / d["EOQ"]
d["DEV_PCT"] = ((d["ORDERS_PER_YEAR"] - d["EOQ_ORDERS"]) / d["EOQ_ORDERS"]) * 100

d["EOQ_STATUS"] = "OK"
d.loc[d["DEV_PCT"] > THRESHOLD, "EOQ_STATUS"] = "FOR_MANGE_ORDRER"
d.loc[d["DEV_PCT"] < -THRESHOLD, "EOQ_STATUS"] = "FOR_FÅ_ORDRER"

d = d.sort_values("DEV_PCT").reset_index(drop=True)

CLIP_LO, CLIP_HI = -150, 500
d["DEV_PLOT"] = d["DEV_PCT"].clip(CLIP_LO, CLIP_HI)

n_mange = (d["EOQ_STATUS"] == "FOR_MANGE_ORDRER").sum()
n_ok    = (d["EOQ_STATUS"] == "OK").sum()
n_faa   = (d["EOQ_STATUS"] == "FOR_FÅ_ORDRER").sum()

color_map = {
    "FOR_MANGE_ORDRER": COLORS["red"],
    "OK": COLORS["orange"],
    "FOR_FÅ_ORDRER": COLORS["blue"],
}
d["COLOR"] = d["EOQ_STATUS"].map(color_map)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5),
                                gridspec_kw={"width_ratios": [2.4, 1]})

# ── Panel 1: Scatterplot ────────────────────────────────────────
ax1.axhspan(-THRESHOLD, THRESHOLD, color="#E0E0E0", alpha=0.5,
            zorder=0, label="OK-sone (±50 %)")
ax1.axhspan(THRESHOLD, CLIP_HI + 50, color=COLORS["red"], alpha=0.04,
            zorder=0)
ax1.axhspan(CLIP_LO - 50, -THRESHOLD, color=COLORS["blue"], alpha=0.04,
            zorder=0)

ax1.scatter(
    d.index, d["DEV_PLOT"],
    c=d["COLOR"], s=18, alpha=0.65, edgecolors="none", zorder=2,
)

ax1.axhline(y=0, color=COLORS["grey"], linewidth=0.8, zorder=1)
ax1.axhline(y=THRESHOLD, color=COLORS["red"], linestyle="--",
            linewidth=1.1, alpha=0.55, zorder=1, label=f"+{THRESHOLD} % terskel")
ax1.axhline(y=-THRESHOLD, color=COLORS["blue"], linestyle="--",
            linewidth=1.1, alpha=0.55, zorder=1, label=f"\u2212{THRESHOLD} % terskel")

ax1.set_xlabel("Artikler (sortert etter avvik)")
ax1.set_ylabel("Avvik fra optimal ordrefrekvens (%)")
ax1.set_title("EOQ-avvik per artikkel")

ax1.set_xlim(-5, len(d) + 5)
ax1.set_ylim(CLIP_LO - 10, CLIP_HI + 10)
ax1.yaxis.set_major_locator(mticker.MultipleLocator(100))

ax1.legend(fontsize=8, loc="upper left", borderpad=0.4, handlelength=1.8)

# ── Panel 2: Stolpediagram ──────────────────────────────────────
categories = ["For mange\nordrer", "OK", "For f\u00e5\nordrer"]
counts = [n_mange, n_ok, n_faa]
bar_colors = [COLORS["red"], COLORS["orange"], COLORS["blue"]]

bars = ax2.bar(categories, counts, color=bar_colors, width=0.6,
               alpha=0.92, edgecolor="none", zorder=2)

for bar, val in zip(bars, counts):
    ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 8,
             str(val), ha="center", va="bottom",
             fontsize=11, fontweight="bold", color=COLORS["title"])

ax2.set_ylabel("Antall artikler")
ax2.set_title("EOQ-statusfordeling")
ax2.set_ylim(0, max(counts) * 1.15)

# ── Tittel og eksport ────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.90])
fig_title(fig, "EOQ-avviksanalyse", "Helse Bergen 2024–2025")

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig07_EOQ_Avvik.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"FOR_MANGE_ORDRER: {n_mange}, OK: {n_ok}, FOR_FÅ_ORDRER: {n_faa}")
print(f"Totalt: {len(d)} artiklar")
