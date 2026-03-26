"""
Genererer Fig03_Regelmotor.png
Regelmotor – sekvensiell beslutningsflyt for HVFS-anbefaling (R1–R8)
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import pandas as pd
from fig_style import apply_style, fig_title, COLORS, DIAGRAM_COLORS

apply_style()

# ── Les analyseresultater ──────────────────────────────────────
DATA_DIR = Path(__file__).resolve().parent
RESULTATER_XLSX = DATA_DIR / "LOG650_Resultater.xlsx"

if not RESULTATER_XLSX.exists():
    print(f"FEIL: Finner ikke {RESULTATER_XLSX}")
    print("Kjør LOG650_analyse_v2_7.py først for å generere resultatfilen.")
    sys.exit(1)

df = pd.read_excel(RESULTATER_XLSX, sheet_name="RESULTATER", header=1)
counts = df["HVFS_ANBEFALING"].value_counts()
n_total   = len(df)
n_overfor = counts.get("OVERFØR_HVFS", 0)
n_behold  = counts.get("BEHOLD_LOKALT", 0)
n_vurder  = counts.get("VURDER_NÆRMERE", 0)
n_mangler = counts.get("MANGLER_DATA", 0)

fig, ax = plt.subplots(figsize=(12, 9.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis("off")

# ── Fargar ───────────────────────────────────────────────────────
C_INPUT   = DIAGRAM_COLORS["input"]
C_RULE    = DIAGRAM_COLORS["rule"]
C_BEHOLD  = COLORS["red"]
C_OVERFOR = COLORS["green"]
C_VURDER  = COLORS["orange"]
C_SUMMARY = DIAGRAM_COLORS["summary"]

# ── Hjelpefunksjonar ─────────────────────────────────────────────
def box(ax, cx, cy, w, h, label, fc, tc="white", fs=9, zorder=2):
    rect = mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.14",
        facecolor=fc, edgecolor=COLORS["title"],
        linewidth=1.0, zorder=zorder,
    )
    ax.add_patch(rect)
    ax.text(cx, cy, label, ha="center", va="center",
            fontsize=fs, fontweight="bold", color=tc,
            zorder=zorder+1, linespacing=1.25)
    return cx, cy, w, h


def arrow_v(ax, x1, y1, h1, x2, y2, h2, label=None):
    """Vertikal pil frå botn av boks 1 → topp av boks 2."""
    yf = y1 - h1/2
    yt = y2 + h2/2
    ax.annotate("", xy=(x2, yt), xytext=(x1, yf),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["edge"],
                                lw=1.4, mutation_scale=14, zorder=3))
    if label:
        mx = (x1 + x2) / 2
        my = (yf + yt) / 2
        ax.text(mx + 0.12, my, label, ha="left", va="center",
                fontsize=7.5, color=DIAGRAM_COLORS["zone_label"],
                fontstyle="italic", zorder=5)


def arrow_h(ax, cx, cy, hw, direction, tx, ty, th, label=None):
    """Horisontal pil frå side av boks → resultatboks."""
    if direction == "right":
        xf = cx + hw/2
        xt = tx - th/2  # th brukt som w her
    else:
        xf = cx - hw/2
        xt = tx + th/2
    ax.annotate("", xy=(xt, ty), xytext=(xf, cy),
                arrowprops=dict(arrowstyle="-|>", color=COLORS["edge"],
                                lw=1.4, mutation_scale=14, zorder=3))
    if label:
        mx = (xf + xt) / 2
        my = cy + 0.12
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=7.5, color=DIAGRAM_COLORS["zone_label"],
                fontstyle="italic", zorder=5)


# ── Dimensjonar ──────────────────────────────────────────────────
rw = 3.6   # regelbredde
rh = 0.58  # regelhøgde
res_w = 2.4  # resultatbredde
res_h = 0.50
dy = 1.10  # vertikal avstand mellom reglar

cx = 6.0          # senterlinje for reglar
rx_right = 9.8    # resultat høgre
rx_left = 2.2     # resultat venstre

# ── Startboks ────────────────────────────────────────────────────
y = 9.3
inp = box(ax, cx, y, rw, 0.62, f"Artikkel inn\n({n_total} stk)", C_INPUT, fs=10)

# ── Regler ───────────────────────────────────────────────────────
rules = [
    ("R1: XYZ = Z?",                        "right", "BEHOLD\nLOKALT",    C_BEHOLD),
    ("R2: ABC = C og XYZ = Y?",             "right", "BEHOLD\nLOKALT",    C_BEHOLD),
    ("R3: A/B + X +\nFOR_MANGE_ORDRER?",    "left",  "OVERFØR\nHVFS",     C_OVERFOR),
    ("R4: A/B + X +\nK_OVERFØR?",           "left",  "OVERFØR\nHVFS",     C_OVERFOR),
    ("R5: A/B + Y +\nK_OVERFØR?",           "left",  "OVERFØR\nHVFS",     C_OVERFOR),
    ("R6/R7/R8:\nResterende artikler",       "right", "VURDER\nNÆRMERE", C_VURDER),
]

prev = inp
for i, (label, side, res_label, res_color) in enumerate(rules):
    y_rule = 9.3 - (i + 1) * dy
    r = box(ax, cx, y_rule, rw, rh, label, C_RULE, fs=8.5)

    # Nei-pil nedover frå førre
    arrow_v(ax, prev[0], prev[1], prev[3], r[0], r[1], r[3],
            label="Nei" if i > 0 else None)

    # Ja-pil til resultat
    if side == "right":
        res = box(ax, rx_right, y_rule, res_w, res_h, res_label, res_color, fs=8.5)
        arrow_h(ax, cx, y_rule, rw, "right", rx_right, y_rule, res_w, label="Ja")
    else:
        res = box(ax, rx_left, y_rule, res_w, res_h, res_label, res_color, fs=8.5)
        arrow_h(ax, cx, y_rule, rw, "left", rx_left, y_rule, res_w, label="Ja")

    prev = r

# ── Oppsummeringsboks ────────────────────────────────────────────
y_sum = y_rule - dy * 0.95
summary = box(ax, cx, y_sum, 9.0, 0.55,
              f"{n_overfor} OVERFØR  |  {n_behold} BEHOLD  |  {n_vurder} VURDER NÆRMERE  |  {n_mangler} MANGLER DATA",
              C_SUMMARY, fs=9)

# Pil ned til oppsummering
arrow_v(ax, prev[0], prev[1], prev[3], cx, y_sum, 0.55)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "Regelmotor", "Sekvensiell beslutningsflyt for HVFS-anbefaling (R1\u2013R8)")
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig03_Regelmotor.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
