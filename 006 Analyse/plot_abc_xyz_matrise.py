"""
Genererer Fig06_ABC_XYZ_Matrise.png
ABC/XYZ klassifiseringsmatrise
Helse Bergen WERKS 3300 LGORT 3001
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
    "axes.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ── Fargar (same som regelmotor) ────────────────────────────────
C_GREEN  = "#1E7D45"   # Klare HVFS-kandidatar
C_ORANGE = "#D68910"   # Vurder nærmare
C_RED    = "#B03A2E"   # Behold lokalt
C_TITLE  = "#1A2A44"

# Fargematrise [ABC-rad][XYZ-kolonne]
#              X           Y           Z
COLOR_MAP = [
    [C_GREEN,  C_GREEN,  C_ORANGE],   # A
    [C_GREEN,  C_ORANGE, C_RED],      # B
    [C_ORANGE, C_RED,    C_RED],      # C
]

# ── Les data ─────────────────────────────────────────────────────
df = pd.read_excel(
    r"C:\G24\G24-thomas-individuell\006 analyse\MASTERFILE V1.xlsx",
    sheet_name="MASTERFILE", header=9,
)

# ABC-klassifisering (same logikk som Pareto-diagrammet)
df["ABC_VALUE"] = df["TOTAL_NETWR"].copy()
mask = df["ABC_VALUE"].isna() & df["D_ANNUAL"].notna() & df["UNIT_PRICE"].notna()
df.loc[mask, "ABC_VALUE"] = df.loc[mask, "D_ANNUAL"] * df.loc[mask, "UNIT_PRICE"]

df_abc = df[df["ABC_VALUE"].notna() & (df["ABC_VALUE"] > 0)].copy()
df_abc = df_abc.sort_values("ABC_VALUE", ascending=False).reset_index(drop=True)
total_value = df_abc["ABC_VALUE"].sum()
df_abc["CUM_PCT"] = df_abc["ABC_VALUE"].cumsum() / total_value

df_abc["ABC_CLASS"] = "C"
df_abc.loc[df_abc["CUM_PCT"] <= 0.80, "ABC_CLASS"] = "A"
df_abc.loc[
    (df_abc["CUM_PCT"] > 0.80) & (df_abc["CUM_PCT"] <= 0.95), "ABC_CLASS"
] = "B"

# XYZ-klassifisering frå CV
df_abc["XYZ_CLASS"] = pd.cut(
    df_abc["CV"],
    bins=[-0.001, 0.5, 1.0, float("inf")],
    labels=["X", "Y", "Z"],
)

# Filtrer til rader med begge klassifiseringar
both = df_abc[df_abc["ABC_CLASS"].notna() & df_abc["XYZ_CLASS"].notna()].copy()
total = len(both)

# Bygg krysstabell
ct = pd.crosstab(both["ABC_CLASS"], both["XYZ_CLASS"])
for c in ["X", "Y", "Z"]:
    if c not in ct.columns:
        ct[c] = 0
for r in ["A", "B", "C"]:
    if r not in ct.index:
        ct.loc[r] = 0
ct = ct.loc[["A", "B", "C"], ["X", "Y", "Z"]]

# ── Plot ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 7))

# Grid-dimensjonar i datakoordinatar
cell = 1.0
cols, rows = 3, 3
grid_w = cols * cell
grid_h = rows * cell

# Margins rundt grid (i datakoordinatar)
margin_left = 2.2
margin_top = 0.6
margin_bottom = 1.8
margin_right = 0.4

total_w = margin_left + grid_w + margin_right
total_h = margin_top + grid_h + margin_bottom

ax.set_xlim(0, total_w)
ax.set_ylim(total_h, 0)  # invertert y
ax.set_aspect("equal")
ax.axis("off")

# Origo for gridet
gx0 = margin_left
gy0 = margin_top

abc_labels = ["A", "B", "C"]
xyz_labels = ["X", "Y", "Z"]

for row_i, abc in enumerate(abc_labels):
    for col_i, xyz in enumerate(xyz_labels):
        n = int(ct.loc[abc, xyz])
        pct = n / total * 100
        color = COLOR_MAP[row_i][col_i]

        x = gx0 + col_i * cell
        y = gy0 + row_i * cell

        rect = FancyBboxPatch(
            (x, y), cell, cell,
            boxstyle="square,pad=0",
            facecolor=color, edgecolor="white", linewidth=1.5,
        )
        ax.add_patch(rect)

        # Tal
        ax.text(
            x + cell / 2, y + cell * 0.42, str(n),
            ha="center", va="center",
            fontsize=22, fontweight="bold", color="white",
        )
        # Prosent
        ax.text(
            x + cell / 2, y + cell * 0.68, f"({pct:.0f} %)",
            ha="center", va="center",
            fontsize=12, color="white", alpha=0.92,
        )

# ── Y-akselablar (ABC – verdi) ─────────────────────────────────
y_labels = [
    "A – Høy verdi",
    "B – Middels verdi",
    "C – Lav verdi",
]
for i, lbl in enumerate(y_labels):
    ax.text(
        gx0 - 0.12, gy0 + i * cell + cell / 2, lbl,
        ha="right", va="center",
        fontsize=10, fontweight="bold", color=C_TITLE,
    )

# ── X-akselablar (XYZ – etterspørselsvariasjon) ────────────────
x_labels = [
    "X – Stabil\n(CV < 0,5)",
    "Y – Variabel\n(CV 0,5–1,0)",
    "Z – Uregelmessig\n(CV > 1,0)",
]
y_xlabel = gy0 + grid_h + 0.15
for i, lbl in enumerate(x_labels):
    ax.text(
        gx0 + i * cell + cell / 2, y_xlabel, lbl,
        ha="center", va="top",
        fontsize=9, fontweight="bold", color=C_TITLE,
    )

# ── Aksetitlar ──────────────────────────────────────────────────
ax.text(
    gx0 + grid_w / 2, y_xlabel + 0.65,
    "Etterspørselsvariasjon",
    ha="center", va="top",
    fontsize=11, fontweight="bold", color=C_TITLE,
)
ax.text(
    gx0 - 1.55, gy0 + grid_h / 2,
    "Verdi (ABC)",
    ha="center", va="center",
    fontsize=11, fontweight="bold", color=C_TITLE, rotation=90,
)

# ── Tittel ───────────────────────────────────────────────────────
ax.text(
    gx0 + grid_w / 2, 0.05,
    "ABC/XYZ klassifiseringsmatrise\nHelse Bergen WERKS 3300 LGORT 3001",
    ha="center", va="top",
    fontsize=11.5, fontweight="bold", color=C_TITLE,
)

# ── Legende ──────────────────────────────────────────────────────
legend_elements = [
    mpatches.Patch(facecolor=C_GREEN,  label="Klare HVFS-kandidatar"),
    mpatches.Patch(facecolor=C_ORANGE, label="Vurder nærmare"),
    mpatches.Patch(facecolor=C_RED,    label="Behold lokalt"),
]
ax.legend(
    handles=legend_elements, loc="lower right",
    fontsize=8.5, framealpha=0.75, edgecolor="#CCCCCC", fancybox=True,
    bbox_to_anchor=(1.0, 0.0),
)

# ── Eksporter ────────────────────────────────────────────────────
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig06_ABC_XYZ_Matrise.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"Totalt klassifisert: {total} artiklar")
