"""
Genererer Fig04_Dataoversikt.png
Dataoversikt: fordeling av nøkkelvariablar for 709 artiklar
Helse Bergen WERKS 3300 LGORT 3001 (2024–2025)
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
    "axes.linewidth": 0.5,
})

# ── Fargepalett ──────────────────────────────────────────────────
C_BLUE   = "#0B3D8C"
C_GREEN  = "#1E7D45"
C_ORANGE = "#D68910"
C_RED    = "#B03A2E"
C_GREY   = "#888888"
C_TITLE  = "#1A2A44"
C_LIGHT  = "#D6EAFF"

# ── Les data ─────────────────────────────────────────────────────
df = pd.read_excel(
    r"C:\G24\G24-thomas-individuell\006 analyse\MASTERFILE V1.xlsx",
    sheet_name="MASTERFILE", header=9,
)

# Berekn ABC_VALUE (same logikk som hovudscriptet)
df["ABC_VALUE"] = df["TOTAL_NETWR"].copy()
mask = df["ABC_VALUE"].isna() & df["D_ANNUAL"].notna() & df["UNIT_PRICE"].notna()
df.loc[mask, "ABC_VALUE"] = df.loc[mask, "D_ANNUAL"] * df.loc[mask, "UNIT_PRICE"]

# ABC-klassifisering
df_val = df[df["ABC_VALUE"].notna() & (df["ABC_VALUE"] > 0)].copy()
df_val = df_val.sort_values("ABC_VALUE", ascending=False).reset_index(drop=True)
total_value = df_val["ABC_VALUE"].sum()
df_val["CUM_PCT"] = df_val["ABC_VALUE"].cumsum() / total_value
df_val["ABC_CLASS"] = "C"
df_val.loc[df_val["CUM_PCT"] <= 0.80, "ABC_CLASS"] = "A"
df_val.loc[(df_val["CUM_PCT"] > 0.80) & (df_val["CUM_PCT"] <= 0.95), "ABC_CLASS"] = "B"

# Merk tilbake til hovud-df
abc_map = df_val.set_index("MATNR")["ABC_CLASS"]
df["ABC_CLASS"] = df["MATNR"].map(abc_map)

# ── Opprett figur (2×3 rutenett) ─────────────────────────────────
fig, axes = plt.subplots(2, 3, figsize=(16, 9))
fig.subplots_adjust(hspace=0.38, wspace=0.30)

# ── (a) Artiklar per varegruppe – topp 10 ────────────────────────
ax = axes[0, 0]
grp = df["WGBEZ"].value_counts()
topp10 = grp.head(10)
andre = grp.iloc[10:].sum() if len(grp) > 10 else 0
if andre > 0:
    topp10 = pd.concat([topp10, pd.Series({"Andre": andre})])

topp10 = topp10.sort_values(ascending=True)
bars = ax.barh(range(len(topp10)), topp10.values, color=C_BLUE, alpha=0.82)
ax.set_yticks(range(len(topp10)))
labels = [str(n)[:25] + "…" if len(str(n)) > 25 else str(n) for n in topp10.index]
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("Antall artiklar", fontsize=9.5)
ax.set_title("(a) Artiklar per varegruppe", fontsize=11, fontweight="bold",
             color=C_TITLE, pad=10)
ax.grid(axis="x", alpha=0.10, linewidth=0.4, linestyle=":")
for bar, val in zip(bars, topp10.values):
    ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=8, color=C_TITLE)

# ── (b) Einingspris-fordeling (log-skala) ────────────────────────
ax = axes[0, 1]
prices = df["UNIT_PRICE"].dropna()
prices = prices[prices > 0]
ax.hist(np.log10(prices), bins=30, color=C_BLUE, alpha=0.75, edgecolor="white",
        linewidth=0.5)
# Sett x-akse til log10-verdiar med lesbare etikettar
xticks = [0, 1, 2, 3, 4, 5]
ax.set_xticks(xticks)
ax.set_xticklabels([f"{10**x:,.0f}" for x in xticks], fontsize=8)
ax.set_xlabel("Einingspris (NOK, log-skala)", fontsize=9.5)
ax.set_ylabel("Antall artiklar", fontsize=9.5)
ax.set_title("(b) Einingspris-fordeling", fontsize=11, fontweight="bold",
             color=C_TITLE, pad=10)
ax.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":")
# Median-linje
med = np.log10(prices.median())
ax.axvline(med, color=C_ORANGE, linestyle="--", linewidth=1.2, alpha=0.8)
ax.text(med + 0.1, ax.get_ylim()[1] * 0.9,
        f"Median: {prices.median():.0f} kr", fontsize=8, color=C_ORANGE)

# ── (c) Årsforbruk-fordeling (log-skala) ─────────────────────────
ax = axes[0, 2]
demand = df["D_ANNUAL"].dropna()
demand = demand[demand > 0]
ax.hist(np.log10(demand), bins=30, color=C_BLUE, alpha=0.75, edgecolor="white",
        linewidth=0.5)
xticks_d = [0, 1, 2, 3, 4, 5]
ax.set_xticks(xticks_d)
ax.set_xticklabels([f"{10**x:,.0f}" for x in xticks_d], fontsize=8)
ax.set_xlabel("Årsforbruk (einingar, log-skala)", fontsize=9.5)
ax.set_ylabel("Antall artiklar", fontsize=9.5)
ax.set_title("(c) Årsforbruk-fordeling", fontsize=11, fontweight="bold",
             color=C_TITLE, pad=10)
ax.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":")
med_d = np.log10(demand.median())
ax.axvline(med_d, color=C_ORANGE, linestyle="--", linewidth=1.2, alpha=0.8)
ax.text(med_d + 0.1, ax.get_ylim()[1] * 0.9,
        f"Median: {demand.median():.0f}", fontsize=8, color=C_ORANGE)

# ── (d) CV-fordeling med XYZ-grenser ─────────────────────────────
ax = axes[1, 0]
cv = df["CV"].dropna()
cv = cv[cv >= 0]
ax.hist(cv.clip(upper=3.0), bins=40, color=C_BLUE, alpha=0.75, edgecolor="white",
        linewidth=0.5, zorder=3)

# Farga bakgrunnssoner
ylim = ax.get_ylim()
ax.axvspan(0, 0.5, color=C_GREEN, alpha=0.08, zorder=1)
ax.axvspan(0.5, 1.0, color=C_ORANGE, alpha=0.08, zorder=1)
ax.axvspan(1.0, 3.0, color=C_RED, alpha=0.08, zorder=1)

# Grenselinjer
ax.axvline(0.5, color=C_GREEN, linestyle="--", linewidth=1.0, alpha=0.7, zorder=4)
ax.axvline(1.0, color=C_RED, linestyle="--", linewidth=1.0, alpha=0.7, zorder=4)

# XYZ-etikettar
ymax = ax.get_ylim()[1]
ax.text(0.25, ymax * 0.92, "X", fontsize=14, fontweight="bold", color=C_GREEN,
        ha="center", va="top", zorder=5)
ax.text(0.75, ymax * 0.92, "Y", fontsize=14, fontweight="bold", color=C_ORANGE,
        ha="center", va="top", zorder=5)
ax.text(1.5, ymax * 0.92, "Z", fontsize=14, fontweight="bold", color=C_RED,
        ha="center", va="top", zorder=5)

n_x = (cv < 0.5).sum()
n_y = ((cv >= 0.5) & (cv < 1.0)).sum()
n_z = (cv >= 1.0).sum()
ax.text(0.25, ymax * 0.80, f"n={n_x}", fontsize=8, color=C_GREEN,
        ha="center", va="top", zorder=5)
ax.text(0.75, ymax * 0.80, f"n={n_y}", fontsize=8, color=C_ORANGE,
        ha="center", va="top", zorder=5)
ax.text(1.5, ymax * 0.80, f"n={n_z}", fontsize=8, color=C_RED,
        ha="center", va="top", zorder=5)

ax.set_xlabel("Variasjonskoeffisient (CV)", fontsize=9.5)
ax.set_ylabel("Antall artiklar", fontsize=9.5)
ax.set_title("(d) CV-fordeling med XYZ-grenser", fontsize=11, fontweight="bold",
             color=C_TITLE, pad=10)
ax.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":")

# ── (e) ABC-fordeling med verdiandel ─────────────────────────────
ax = axes[1, 1]
abc_counts = df_val["ABC_CLASS"].value_counts().reindex(["A", "B", "C"])
abc_colors = [C_BLUE, C_ORANGE, C_RED]
bars = ax.bar(["A", "B", "C"], abc_counts.values, color=abc_colors, alpha=0.82,
              edgecolor="white", linewidth=0.5, zorder=3)

# Verdiandel per klasse
abc_val_pct = df_val.groupby("ABC_CLASS")["ABC_VALUE"].sum() / total_value * 100
abc_val_pct = abc_val_pct.reindex(["A", "B", "C"])

for bar, cnt, vpct in zip(bars, abc_counts.values, abc_val_pct.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
            f"{cnt}\n({vpct:.0f} % verdi)", ha="center", va="bottom",
            fontsize=8.5, fontweight="bold", color=C_TITLE)

ax.set_xlabel("ABC-klasse", fontsize=9.5)
ax.set_ylabel("Antall artiklar", fontsize=9.5)
ax.set_title("(e) ABC-fordeling og verdiandel", fontsize=11, fontweight="bold",
             color=C_TITLE, pad=10)
ax.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":")
ax.set_ylim(0, abc_counts.max() * 1.25)

# ── (f) Leverandørkonsentrasjon ──────────────────────────────────
ax = axes[1, 2]
supp = df["SUPPLIER_COUNT"].dropna().astype(int)
supp_counts = supp.value_counts().sort_index()
# Grupper 5+ saman
supp_grouped = supp_counts.head(4).copy()
if len(supp_counts) > 4:
    supp_grouped["5+"] = supp_counts.iloc[4:].sum()

bars = ax.bar(range(len(supp_grouped)), supp_grouped.values, color=C_BLUE,
              alpha=0.82, edgecolor="white", linewidth=0.5, zorder=3)
ax.set_xticks(range(len(supp_grouped)))
ax.set_xticklabels([str(x) for x in supp_grouped.index], fontsize=9)
ax.set_xlabel("Antall leverandørar", fontsize=9.5)
ax.set_ylabel("Antall artiklar", fontsize=9.5)
ax.set_title("(f) Leverandørkonsentrasjon", fontsize=11, fontweight="bold",
             color=C_TITLE, pad=10)
ax.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":")
for bar, val in zip(bars, supp_grouped.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
            str(val), ha="center", va="bottom", fontsize=8.5, color=C_TITLE)

# ── Hovudtittel ──────────────────────────────────────────────────
fig.suptitle(
    "Dataoversikt: 709 artiklar ved Helse Bergen WERKS 3300, LGORT 3001 (2024–2025)",
    fontsize=13, fontweight="bold", color=C_TITLE, y=0.98,
)

# ── Eksporter ────────────────────────────────────────────────────
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig04_Dataoversikt.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
