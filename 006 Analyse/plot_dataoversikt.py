"""
Genererer Fig04_Dataoversikt.png
Dataoversikt: fordeling av nøkkelvariablar for 709 artiklar
Helse Bergen WERKS 3300 LGORT 3001 (2024–2025)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from fig_style import apply_style, fig_title, COLORS

apply_style()

df = pd.read_excel(
    r"C:\G24\G24-thomas-individuell\006 analyse\MASTERFILE V1.xlsx",
    sheet_name="MASTERFILE", header=9,
)

df["ABC_VALUE"] = df["TOTAL_NETWR"].copy()
mask = df["ABC_VALUE"].isna() & df["D_ANNUAL"].notna() & df["UNIT_PRICE"].notna()
df.loc[mask, "ABC_VALUE"] = df.loc[mask, "D_ANNUAL"] * df.loc[mask, "UNIT_PRICE"]

df_val = df[df["ABC_VALUE"].notna() & (df["ABC_VALUE"] > 0)].copy()
df_val = df_val.sort_values("ABC_VALUE", ascending=False).reset_index(drop=True)
total_value = df_val["ABC_VALUE"].sum()
df_val["CUM_PCT"] = df_val["ABC_VALUE"].cumsum() / total_value
df_val["ABC_CLASS"] = "C"
df_val.loc[df_val["CUM_PCT"] <= 0.80, "ABC_CLASS"] = "A"
df_val.loc[(df_val["CUM_PCT"] > 0.80) & (df_val["CUM_PCT"] <= 0.95), "ABC_CLASS"] = "B"

abc_map = df_val.set_index("MATNR")["ABC_CLASS"]
df["ABC_CLASS"] = df["MATNR"].map(abc_map)

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
bars = ax.barh(range(len(topp10)), topp10.values, color=COLORS["blue"],
               alpha=0.92, edgecolor="none")
ax.set_yticks(range(len(topp10)))
labels = [str(n)[:25] + "…" if len(str(n)) > 25 else str(n) for n in topp10.index]
ax.set_yticklabels(labels, fontsize=8)
ax.set_xlabel("Antall artiklar")
ax.set_title("(a) Artiklar per varegruppe", pad=10)
ax.grid(axis="x")  # barh treng x-grid
for bar, val in zip(bars, topp10.values):
    ax.text(val + 1, bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=8, color=COLORS["title"])

# ── (b) Einingspris-fordeling (log-skala) ────────────────────────
ax = axes[0, 1]
prices = df["UNIT_PRICE"].dropna()
prices = prices[prices > 0]
ax.hist(np.log10(prices), bins=30, color=COLORS["blue"], alpha=0.85,
        edgecolor="none")
xticks = [0, 1, 2, 3, 4, 5]
ax.set_xticks(xticks)
ax.set_xticklabels([f"{10**x:,.0f}" for x in xticks], fontsize=8)
ax.set_xlabel("Einingspris (NOK, log-skala)")
ax.set_ylabel("Antall artiklar")
ax.set_title("(b) Einingspris-fordeling", pad=10)
med = np.log10(prices.median())
ax.axvline(med, color=COLORS["orange"], linestyle="--", linewidth=1.5, alpha=0.8)
ax.text(med + 0.1, ax.get_ylim()[1] * 0.9,
        f"Median: {prices.median():.0f} kr", fontsize=9, color=COLORS["orange"])

# ── (c) Årsforbruk-fordeling (log-skala) ─────────────────────────
ax = axes[0, 2]
demand = df["D_ANNUAL"].dropna()
demand = demand[demand > 0]
ax.hist(np.log10(demand), bins=30, color=COLORS["blue"], alpha=0.85,
        edgecolor="none")
xticks_d = [0, 1, 2, 3, 4, 5]
ax.set_xticks(xticks_d)
ax.set_xticklabels([f"{10**x:,.0f}" for x in xticks_d], fontsize=8)
ax.set_xlabel("Årsforbruk (einingar, log-skala)")
ax.set_ylabel("Antall artiklar")
ax.set_title("(c) Årsforbruk-fordeling", pad=10)
med_d = np.log10(demand.median())
ax.axvline(med_d, color=COLORS["orange"], linestyle="--", linewidth=1.5, alpha=0.8)
ax.text(med_d + 0.1, ax.get_ylim()[1] * 0.9,
        f"Median: {demand.median():.0f}", fontsize=9, color=COLORS["orange"])

# ── (d) CV-fordeling med XYZ-grenser ─────────────────────────────
ax = axes[1, 0]
cv = df["CV"].dropna()
cv = cv[cv >= 0]
ax.hist(cv.clip(upper=3.0), bins=40, color=COLORS["blue"], alpha=0.85,
        edgecolor="none", zorder=3)

ax.axvspan(0, 0.5, color=COLORS["green"], alpha=0.08, zorder=1)
ax.axvspan(0.5, 1.0, color=COLORS["orange"], alpha=0.08, zorder=1)
ax.axvspan(1.0, 3.0, color=COLORS["red"], alpha=0.08, zorder=1)

ax.axvline(0.5, color=COLORS["green"], linestyle="--", linewidth=1.0, alpha=0.7, zorder=4)
ax.axvline(1.0, color=COLORS["red"], linestyle="--", linewidth=1.0, alpha=0.7, zorder=4)

ymax = ax.get_ylim()[1]
ax.text(0.25, ymax * 0.92, "X", fontsize=14, fontweight="bold", color=COLORS["green"],
        ha="center", va="top", zorder=5)
ax.text(0.75, ymax * 0.92, "Y", fontsize=14, fontweight="bold", color=COLORS["orange"],
        ha="center", va="top", zorder=5)
ax.text(1.5, ymax * 0.92, "Z", fontsize=14, fontweight="bold", color=COLORS["red"],
        ha="center", va="top", zorder=5)

n_x = (cv < 0.5).sum()
n_y = ((cv >= 0.5) & (cv < 1.0)).sum()
n_z = (cv >= 1.0).sum()
ax.text(0.25, ymax * 0.80, f"n={n_x}", fontsize=8, color=COLORS["green"],
        ha="center", va="top", zorder=5)
ax.text(0.75, ymax * 0.80, f"n={n_y}", fontsize=8, color=COLORS["orange"],
        ha="center", va="top", zorder=5)
ax.text(1.5, ymax * 0.80, f"n={n_z}", fontsize=8, color=COLORS["red"],
        ha="center", va="top", zorder=5)

ax.set_xlabel("Variasjonskoeffisient (CV)")
ax.set_ylabel("Antall artiklar")
ax.set_title("(d) CV-fordeling med XYZ-grenser", pad=10)

# ── (e) ABC-fordeling med verdiandel ─────────────────────────────
ax = axes[1, 1]
abc_counts = df_val["ABC_CLASS"].value_counts().reindex(["A", "B", "C"])
abc_colors = [COLORS["blue"], COLORS["orange"], COLORS["red"]]
bars = ax.bar(["A", "B", "C"], abc_counts.values, color=abc_colors,
              alpha=0.92, edgecolor="none", zorder=3)

abc_val_pct = df_val.groupby("ABC_CLASS")["ABC_VALUE"].sum() / total_value * 100
abc_val_pct = abc_val_pct.reindex(["A", "B", "C"])

for bar, cnt, vpct in zip(bars, abc_counts.values, abc_val_pct.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
            f"{cnt}\n({vpct:.0f} % verdi)", ha="center", va="bottom",
            fontsize=9, fontweight="bold", color=COLORS["title"])

ax.set_xlabel("ABC-klasse")
ax.set_ylabel("Antall artiklar")
ax.set_title("(e) ABC-fordeling og verdiandel", pad=10)
ax.set_ylim(0, abc_counts.max() * 1.25)

# ── (f) Leverandørkonsentrasjon ──────────────────────────────────
ax = axes[1, 2]
supp = df["SUPPLIER_COUNT"].dropna().astype(int)
supp_counts = supp.value_counts().sort_index()
supp_grouped = supp_counts.head(4).copy()
if len(supp_counts) > 4:
    supp_grouped["5+"] = supp_counts.iloc[4:].sum()

bars = ax.bar(range(len(supp_grouped)), supp_grouped.values, color=COLORS["blue"],
              alpha=0.92, edgecolor="none", zorder=3)
ax.set_xticks(range(len(supp_grouped)))
ax.set_xticklabels([str(x) for x in supp_grouped.index])
ax.set_xlabel("Antall leverandørar")
ax.set_ylabel("Antall artiklar")
ax.set_title("(f) Leverandørkonsentrasjon", pad=10)
for bar, val in zip(bars, supp_grouped.values):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 2,
            str(val), ha="center", va="bottom", fontsize=9, color=COLORS["title"])

# ── Tittel og eksport ────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.90])
fig_title(fig, "Dataoversikt", "709 artiklar ved Helse Bergen WERKS 3300, LGORT 3001 (2024–2025)")

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig04_Dataoversikt.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
