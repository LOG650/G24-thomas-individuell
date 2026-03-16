"""
Genererer Fig01_Lagerstruktur.png
Lagerstruktur – Helse Vest forsyningskjede (forenklet)
"""

import matplotlib.pyplot as plt
from fig_style import apply_style, fig_title, COLORS, HIER_COLORS, draw_box, draw_arrow_v

apply_style()

fig, ax = plt.subplots(figsize=(12, 5.0))
ax.set_xlim(0, 12)
ax.set_ylim(0, 5.0)
ax.axis("off")

# ── Dimensjonar ──────────────────────────────────────────────────
bw_top = 3.4;  bh = 0.72
bw_mid = 2.8
bw_side = 2.0
bw_bot = 2.2

# ── Nivå 1: HVFS ────────────────────────────────────────────────
hvfs = draw_box(ax, 6.0, 4.15, bw_top, bh,
                "HVFS\nHelse Vest Forsyningssentral",
                HIER_COLORS["top"], textcolor="white", fontsize=10)

# ── Nivå 2: Tre senter ──────────────────────────────────────────
hus = draw_box(ax, 2.0, 2.75, bw_side, bh,
               "HUS\n(eksempel)", HIER_COLORS["mid_side"])

hb = draw_box(ax, 6.0, 2.75, bw_mid + 0.6, bh,
              "Helse Bergen\nWERKS 3300 / LGORT 3001",
              HIER_COLORS["mid_main"], textcolor="white", fontsize=9)

stav = draw_box(ax, 10.0, 2.75, bw_side, bh,
                "Stavanger\n(eksempel)", HIER_COLORS["mid_side"])

# ── Nivå 3: Seksjonar ───────────────────────────────────────────
sek1 = draw_box(ax, 4.6, 1.35, bw_bot, bh,
                "Seksjon/post\nHelse Bergen", HIER_COLORS["bottom"])

sek2 = draw_box(ax, 7.4, 1.35, bw_bot, bh,
                "Seksjon/post\nHelse Bergen", HIER_COLORS["bottom"])

# ── Piler ────────────────────────────────────────────────────────
# HVFS → tre senter
draw_arrow_v(ax, hvfs[0], hvfs[1], hvfs[3],
             hus[0], hus[1], hus[3])

draw_arrow_v(ax, hvfs[0], hvfs[1], hvfs[3],
             hb[0], hb[1], hb[3],
             label="Sentralleveranse")

draw_arrow_v(ax, hvfs[0], hvfs[1], hvfs[3],
             stav[0], stav[1], stav[3])

# Helse Bergen → Seksjonar
draw_arrow_v(ax, hb[0], hb[1], hb[3],
             sek1[0], sek1[1], sek1[3])

draw_arrow_v(ax, hb[0], hb[1], hb[3],
             sek2[0], sek2[1], sek2[3])

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "Lagerstruktur", "Helse Vest forsyningskjede (forenklet)")
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig01_Lagerstruktur.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
