"""
Genererer Fig01_Lagerstruktur.png
Lagerstruktur – Helse Vest forsyningskjede (forenklet)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
})

fig, ax = plt.subplots(figsize=(12, 5.0))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.0)
ax.axis("off")

# ── Hjelpefunksjonar ─────────────────────────────────────────────
def draw_box(ax, cx, cy, w, h, label, facecolor, textcolor="#1A2A44",
             fontsize=9, zorder=2):
    """Teikn ein boks med avrunda hjørner, sentrert på (cx, cy)."""
    x = cx - w / 2
    y = cy - h / 2
    rect = mpatches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.10",
        facecolor=facecolor, edgecolor="#2A5A8C",
        linewidth=1.2, zorder=zorder,
    )
    ax.add_patch(rect)
    ax.text(cx, cy, label,
            ha="center", va="center",
            fontsize=fontsize, fontweight="bold",
            color=textcolor, zorder=zorder + 1,
            linespacing=1.3)
    return (cx, cy, w, h)


def draw_arrow(ax, x1, y1, h1, x2, y2, h2, label=None, label_side="right"):
    """Pil frå botn av boks 1 til topp av boks 2."""
    y_from = y1 - h1 / 2
    y_to = y2 + h2 / 2
    ax.annotate(
        "", xy=(x2, y_to), xytext=(x1, y_from),
        arrowprops=dict(
            arrowstyle="-|>", color="#2A5A8C", lw=1.6,
            mutation_scale=14, connectionstyle="arc3,rad=0",
            zorder=4,
        ),
    )
    if label:
        # Plasser label ved sidan av pila
        mx = (x1 + x2) / 2
        my = (y_from + y_to) / 2
        offset_x = 0.15 if label_side == "right" else -0.15
        ha = "left" if label_side == "right" else "right"
        ax.text(mx + offset_x, my, label,
                ha=ha, va="center",
                fontsize=8, fontstyle="italic",
                color="#3A5A8C", zorder=5)


# ── Fargepalett (mørk → lys nedover i hierarkiet) ───────────────
c_top = "#0B3D8C"       # HVFS – mørkast
c_mid_main = "#1A5FAA"  # Helse Bergen – hovudfokus
c_mid_side = "#B3D4F7"  # HUS / Stavanger – sidegrener (lys)
c_bot = "#D6EAFF"       # Seksjon/post – lysast

# ── Dimensjonar ──────────────────────────────────────────────────
bw_top = 3.4;  bh = 0.72
bw_mid = 2.8
bw_side = 2.0
bw_bot = 2.2

# ── Nivå 1: HVFS ────────────────────────────────────────────────
hvfs = draw_box(ax, 6.0, 4.15, bw_top, bh,
                "HVFS\nHelse Vest Forsyningssentral",
                c_top, textcolor="white", fontsize=10)

# ── Nivå 2: Tre senter ──────────────────────────────────────────
hus = draw_box(ax, 2.0, 2.75, bw_side, bh,
               "HUS\n(eksempel)", c_mid_side)

hb = draw_box(ax, 6.0, 2.75, bw_mid + 0.6, bh,
              "Helse Bergen\nWERKS 3300 / LGORT 3001",
              c_mid_main, textcolor="white", fontsize=9)

stav = draw_box(ax, 10.0, 2.75, bw_side, bh,
                "Stavanger\n(eksempel)", c_mid_side)

# ── Nivå 3: Seksjonar ───────────────────────────────────────────
sek1 = draw_box(ax, 4.6, 1.35, bw_bot, bh,
                "Seksjon/post\nHelse Bergen", c_bot)

sek2 = draw_box(ax, 7.4, 1.35, bw_bot, bh,
                "Seksjon/post\nHelse Bergen", c_bot)

# ── Piler ────────────────────────────────────────────────────────
# HVFS → tre senter
draw_arrow(ax, hvfs[0], hvfs[1], hvfs[3],
           hus[0], hus[1], hus[3])

draw_arrow(ax, hvfs[0], hvfs[1], hvfs[3],
           hb[0], hb[1], hb[3],
           label="Sentralleveranse", label_side="right")

draw_arrow(ax, hvfs[0], hvfs[1], hvfs[3],
           stav[0], stav[1], stav[3])

# Helse Bergen → Seksjonar
draw_arrow(ax, hb[0], hb[1], hb[3],
           sek1[0], sek1[1], sek1[3])

draw_arrow(ax, hb[0], hb[1], hb[3],
           sek2[0], sek2[1], sek2[3])

# ── Tittel ───────────────────────────────────────────────────────
ax.set_title(
    "Lagerstruktur – Helse Vest forsyningskjede (forenklet)",
    fontsize=12, fontweight="bold", pad=10,
    color="#1A2A44",
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig01_Lagerstruktur.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
