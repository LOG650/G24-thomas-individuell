"""
Genererer Fig02_Analysepipeline.png
Analysepipeline: fra SAP-rådata til HVFS-anbefaling
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from fig_style import apply_style, fig_title, COLORS, BLUE_GRADIENT, DIAGRAM_COLORS

apply_style()

fig, ax = plt.subplots(figsize=(12, 3.0))
ax.set_xlim(-0.3, 12.3)
ax.set_ylim(-0.15, 2.6)
ax.axis("off")

# ── Stegdefinisjonar ─────────────────────────────────────────────
steps = [
    "SAP S/4HANA\n14 tabeller",
    "Cleaning\nD-01–D-08",
    "MASTERFILE\n709 artikler",
    "ABC / XYZ\nEOQ",
    "K-means\nK = 3",
    "Regelmotor\n8 regler",
    "HVFS-anbefaling\n145 art.",
]

# ── Plassering ───────────────────────────────────────────────────
n = len(steps)
box_w = 1.30
box_h = 1.10
gap = 0.42
total_w = n * box_w + (n - 1) * gap
x_start = (12.0 - total_w) / 2

positions = [x_start + i * (box_w + gap) for i in range(n)]
y_center = 1.05

# ── Bakgrunnssoner (faser) ───────────────────────────────────────
zone_pad_x = 0.18
zone_pad_y_top = 0.72
zone_pad_y_bot = 0.28

zones = [
    {"label": "DATAGRUNNLAG",      "start": 0, "end": 2,
     "color": DIAGRAM_COLORS["zone_1"], "edge": DIAGRAM_COLORS["zone_edge_1"]},
    {"label": "ANALYSEMODELLER",   "start": 3, "end": 4,
     "color": DIAGRAM_COLORS["zone_2"], "edge": DIAGRAM_COLORS["zone_edge_2"]},
    {"label": "BESLUTNINGSLOGIKK", "start": 5, "end": 6,
     "color": DIAGRAM_COLORS["zone_3"], "edge": DIAGRAM_COLORS["zone_edge_3"]},
]

for z in zones:
    x0 = positions[z["start"]] - zone_pad_x
    x1 = positions[z["end"]] + box_w + zone_pad_x
    y0 = y_center - box_h / 2 - zone_pad_y_bot
    y1 = y_center + box_h / 2 + zone_pad_y_top

    rect = mpatches.FancyBboxPatch(
        (x0, y0), x1 - x0, y1 - y0,
        boxstyle="round,pad=0.08",
        facecolor=z["color"], edgecolor=z["edge"],
        linewidth=0.8, linestyle="--", alpha=0.35, zorder=0,
    )
    ax.add_patch(rect)

    ax.text(
        (x0 + x1) / 2, y1 - 0.13,
        z["label"],
        ha="center", va="top",
        fontsize=7.5, fontweight="bold",
        color=DIAGRAM_COLORS["zone_label"], style="italic",
        zorder=5,
    )

# ── Teikn boksar ─────────────────────────────────────────────────
for i, label in enumerate(steps):
    x = positions[i]
    y = y_center - box_h / 2

    text_color = "white" if i >= 5 else COLORS["title"]

    rect = mpatches.FancyBboxPatch(
        (x, y), box_w, box_h,
        boxstyle="round,pad=0.14",
        facecolor=BLUE_GRADIENT[i], edgecolor=COLORS["edge"],
        linewidth=1.0, zorder=2,
    )
    ax.add_patch(rect)

    ax.text(
        x + box_w / 2, y + box_h / 2,
        label,
        ha="center", va="center",
        fontsize=9, fontweight="bold",
        color=text_color, zorder=3,
        linespacing=1.3,
    )

# ── Piler mellom boksar ──────────────────────────────────────────
arrow_props = dict(
    arrowstyle="-|>",
    color=COLORS["edge"],
    lw=1.4,
    mutation_scale=14,
    connectionstyle="arc3,rad=0",
    zorder=4,
)

for i in range(n - 1):
    x_from = positions[i] + box_w
    x_to = positions[i + 1]
    ax.annotate(
        "", xy=(x_to, y_center), xytext=(x_from, y_center),
        arrowprops=arrow_props,
    )

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "Analysepipeline", "Fra SAP-rådata til HVFS-anbefaling")
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig02_Analysepipeline.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
