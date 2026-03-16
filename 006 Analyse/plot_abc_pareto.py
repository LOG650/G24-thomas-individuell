"""
Genererer Fig05_ABC_Pareto.png
ABC-analyse – Pareto-diagram
Helse Bergen WERKS 3300 LGORT 3001 (2024–2025)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from fig_style import apply_style, fig_title, COLORS

apply_style()

ABC_A = 0.80
ABC_B = 0.95

# ── Les data ─────────────────────────────────────────────────────
df = pd.read_excel(
    r"C:\G24\G24-thomas-individuell\006 analyse\MASTERFILE V1.xlsx",
    sheet_name="MASTERFILE", header=9,
)

# Berekn ABC_VALUE (same logikk som hovudscriptet)
df["ABC_VALUE"] = df["TOTAL_NETWR"].copy()
mask = df["ABC_VALUE"].isna() & df["D_ANNUAL"].notna() & df["UNIT_PRICE"].notna()
df.loc[mask, "ABC_VALUE"] = df.loc[mask, "D_ANNUAL"] * df.loc[mask, "UNIT_PRICE"]

# Filtrer og sorter
df_abc = df[df["ABC_VALUE"].notna() & (df["ABC_VALUE"] > 0)].copy()
df_abc = df_abc.sort_values("ABC_VALUE", ascending=False).reset_index(drop=True)

total_value = df_abc["ABC_VALUE"].sum()
df_abc["CUM_VALUE"] = df_abc["ABC_VALUE"].cumsum()
df_abc["CUM_PCT"] = df_abc["CUM_VALUE"] / total_value

# ABC-klassifisering
df_abc["ABC_CLASS"] = "C"
df_abc.loc[df_abc["CUM_PCT"] <= ABC_A, "ABC_CLASS"] = "A"
df_abc.loc[
    (df_abc["CUM_PCT"] > ABC_A) & (df_abc["CUM_PCT"] <= ABC_B), "ABC_CLASS"
] = "B"

n_a = (df_abc["ABC_CLASS"] == "A").sum()
n_b = (df_abc["ABC_CLASS"] == "B").sum()
n_c = (df_abc["ABC_CLASS"] == "C").sum()
n_tot = len(df_abc)

pct_a = n_a / n_tot * 100
pct_b = n_b / n_tot * 100
pct_c = n_c / n_tot * 100

# Grenseindeksar
idx_ab = n_a - 1
idx_bc = n_a + n_b - 1

# ── Plot ─────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(12, 4))

# Stolpediagram
colors = [COLORS["blue"] if c == "A" else COLORS["orange"] if c == "B" else COLORS["red"]
          for c in df_abc["ABC_CLASS"]]
ax1.bar(range(n_tot), df_abc["ABC_VALUE"], color=colors, width=1.0,
        alpha=0.92, edgecolor="none", zorder=2)

# Pareto-kurve på sekundærakse
ax2 = ax1.twinx()
ax2.set_facecolor("none")
ax2.plot(range(n_tot), df_abc["CUM_PCT"] * 100, color=COLORS["line"],
         linewidth=2.0, zorder=4)

# Vertikale stiplede linjer ved ABC-grensene
ax1.axvline(x=idx_ab, color=COLORS["blue"], linestyle="--", linewidth=1.2,
            alpha=0.5, zorder=3)
ax1.axvline(x=idx_bc, color=COLORS["orange"], linestyle="--", linewidth=1.2,
            alpha=0.5, zorder=3)

# Horisontale referanselinjer ved 80 % og 95 %
ax2.axhline(y=80, color=COLORS["grey"], linestyle=":", linewidth=0.8, alpha=0.6)
ax2.axhline(y=95, color=COLORS["grey"], linestyle=":", linewidth=0.8, alpha=0.6)

# ── Akseformatering ──────────────────────────────────────────────
ax1.set_xlabel("Artikler (rangert etter verdi)")
ax1.set_ylabel("Innkjøpsverdi (NOK)")
ax2.set_ylabel("Kumulativ andel (%)")

# Venstre y-akse: konsekvent mill.-notasjon
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x / 1e6:.1f} mill."
))
ax1.yaxis.set_major_locator(mticker.MultipleLocator(0.5e6))

# Høgre y-akse: reine prosentintervall 0–100
ax2.set_ylim(0, 100)
ax2.yaxis.set_major_locator(mticker.MultipleLocator(20))
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x:.0f}"
))

ax1.set_xlim(-1, n_tot + 1)
ax1.set_ylim(bottom=0)

# Fjern spines på ax2 også
for spine in ax2.spines.values():
    spine.set_visible(False)

# ── Legende ──────────────────────────────────────────────────────
legend_elements = [
    Patch(facecolor=COLORS["blue"], alpha=0.92,
          label=f"A: {n_a} artikler ({pct_a:.0f} %) – 80 %"),
    Patch(facecolor=COLORS["orange"], alpha=0.92,
          label=f"B: {n_b} artikler ({pct_b:.0f} %) – 15 %"),
    Patch(facecolor=COLORS["red"], alpha=0.92,
          label=f"C: {n_c} artikler ({pct_c:.0f} %) – 5 %"),
    Line2D([0], [0], color=COLORS["line"], linewidth=2.0,
           label="Kumulativ andel (%)"),
]
ax1.legend(
    handles=legend_elements, loc="upper right",
    handlelength=1.4, handletextpad=0.5, labelspacing=0.35,
)

# ── Tittel og eksport ────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "ABC-analyse – Pareto-diagram", "Helse Bergen WERKS 3300 LGORT 3001 (2024–2025)")

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig05_ABC_Pareto.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"A: {n_a} ({pct_a:.1f} %), B: {n_b} ({pct_b:.1f} %), C: {n_c} ({pct_c:.1f} %)")
