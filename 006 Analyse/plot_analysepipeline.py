"""
Genererer Fig02_Analysepipeline.png
Analysepipeline: fra SAP-rådata til HVFS-anbefaling
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
})

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

# ── Fargar: blå gradient (lys → mørk) ───────────────────────────
blues = ["#D6EAFF", "#B3D4F7", "#82BBF0", "#519DE0", "#2E7FCA", "#1A5FAA", "#0B3D8C"]

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
     "color": "#E8F0FE", "edge": "#B8CDE8"},
    {"label": "ANALYSEMODELLER",   "start": 3, "end": 4,
     "color": "#E0ECFA", "edge": "#A8BFE0"},
    {"label": "BESLUTNINGSLOGIKK", "start": 5, "end": 6,
     "color": "#D4E2F5", "edge": "#94ABCF"},
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
        linewidth=0.8, linestyle="--", alpha=0.55, zorder=0,
    )
    ax.add_patch(rect)

    ax.text(
        (x0 + x1) / 2, y1 - 0.13,
        z["label"],
        ha="center", va="top",
        fontsize=7.5, fontweight="bold",
        color="#3A5A8C", style="italic",
        zorder=5,
    )

# ── Teikn boksar ─────────────────────────────────────────────────
for i, label in enumerate(steps):
    x = positions[i]
    y = y_center - box_h / 2

    text_color = "white" if i >= 5 else "#1A2A44"

    rect = mpatches.FancyBboxPatch(
        (x, y), box_w, box_h,
        boxstyle="round,pad=0.10",
        facecolor=blues[i], edgecolor="#2A5A8C",
        linewidth=1.2, zorder=2,
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
    color="#2A5A8C",
    lw=1.6,
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

# ── Tittel ───────────────────────────────────────────────────────
ax.set_title(
    "Analysepipeline: fra SAP-rådata til HVFS-anbefaling",
    fontsize=12, fontweight="bold", pad=8,
    color="#1A2A44",
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig02_Analysepipeline.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
