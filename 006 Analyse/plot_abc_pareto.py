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

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
    "axes.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ── Fargepalett (konsistent med øvrige figurer) ──────────────────
C_A    = "#0B3D8C"   # A-artiklar – mørk blå
C_B    = "#D68910"   # B-artiklar – oransje
C_C    = "#B03A2E"   # C-artiklar – raud
C_LINE = "#2C3E50"   # Pareto-kurve – mørk gråblå
C_TITLE = "#1A2A44"

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

# Stolpediagram – dempet alpha for akademisk uttrykk
colors = [C_A if c == "A" else C_B if c == "B" else C_C
          for c in df_abc["ABC_CLASS"]]
ax1.bar(range(n_tot), df_abc["ABC_VALUE"], color=colors, width=1.0,
        alpha=0.82, zorder=2)

# Pareto-kurve på sekundærakse
ax2 = ax1.twinx()
ax2.plot(range(n_tot), df_abc["CUM_PCT"] * 100, color=C_LINE,
         linewidth=1.6, alpha=0.85, zorder=4)

# Vertikale stiplede linjer ved ABC-grensene
ax1.axvline(x=idx_ab, color=C_A, linestyle="--", linewidth=1.2, alpha=0.4,
            zorder=3)
ax1.axvline(x=idx_bc, color=C_B, linestyle="--", linewidth=1.2, alpha=0.4,
            zorder=3)

# Horisontale referanselinjer ved 80 % og 95 %
ax2.axhline(y=80, color="#AAAAAA", linestyle=":", linewidth=0.7, alpha=0.5)
ax2.axhline(y=95, color="#AAAAAA", linestyle=":", linewidth=0.7, alpha=0.5)

# ── Akseformatering ──────────────────────────────────────────────
ax1.set_xlabel("Artikler (rangert etter verdi)", fontsize=10.5)
ax1.set_ylabel("Innkjøpsverdi (NOK)", fontsize=10.5)
ax2.set_ylabel("Kumulativ andel (%)", fontsize=10.5)

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

# Diskret rutenett – berre horisontalt
ax1.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":", zorder=0)
ax1.set_axisbelow(True)

# Fjern øvre spine på ax2 også
ax2.spines["top"].set_visible(False)

# ── Legende (kompakt, lett) ──────────────────────────────────────
legend_elements = [
    Patch(facecolor=C_A, alpha=0.82,
          label=f"A: {n_a} artikler ({pct_a:.0f} %) – 80 %"),
    Patch(facecolor=C_B, alpha=0.82,
          label=f"B: {n_b} artikler ({pct_b:.0f} %) – 15 %"),
    Patch(facecolor=C_C, alpha=0.82,
          label=f"C: {n_c} artikler ({pct_c:.0f} %) – 5 %"),
    Line2D([0], [0], color=C_LINE, linewidth=1.8, alpha=0.85,
           label="Kumulativ andel (%)"),
]
ax1.legend(
    handles=legend_elements, loc="upper right",
    fontsize=8, framealpha=0.75, edgecolor="#CCCCCC", fancybox=True,
    borderpad=0.5, handlelength=1.4, handletextpad=0.5,
    labelspacing=0.35,
)

# ── Tittel ───────────────────────────────────────────────────────
ax1.set_title(
    "ABC-analyse – Pareto-diagram\n"
    "Helse Bergen WERKS 3300 LGORT 3001 (2024–2025)",
    fontsize=11.5, fontweight="bold", color=C_TITLE, pad=12,
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig05_ABC_Pareto.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"A: {n_a} ({pct_a:.1f} %), B: {n_b} ({pct_b:.1f} %), C: {n_c} ({pct_c:.1f} %)")
