"""
Genererer Fig03_Regelmotor.png
Regelmotor – sekvensiell beslutningsflyt for HVFS-anbefaling (R1–R8)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
})

fig, ax = plt.subplots(figsize=(12, 9.5))
ax.set_xlim(0, 12)
ax.set_ylim(0, 10)
ax.axis("off")

# ── Fargar ───────────────────────────────────────────────────────
C_INPUT   = "#0B3D8C"   # datainngang
C_RULE    = "#3D5A80"   # beslutningsregel
C_BEHOLD  = "#B03A2E"   # raud – behold lokalt
C_OVERFOR = "#1E7D45"   # grøn – overfør HVFS
C_VURDER  = "#D68910"   # oransje – til vurdering
C_SUMMARY = "#2C3E50"   # oppsummering

# ── Hjelpefunksjonar ─────────────────────────────────────────────
def box(ax, cx, cy, w, h, label, fc, tc="white", fs=9, zorder=2):
    rect = mpatches.FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.08",
        facecolor=fc, edgecolor="#1A2A44",
        linewidth=1.1, zorder=zorder,
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
                arrowprops=dict(arrowstyle="-|>", color="#2A5A8C",
                                lw=1.4, mutation_scale=13, zorder=3))
    if label:
        mx = (x1 + x2) / 2
        my = (yf + yt) / 2
        ax.text(mx + 0.12, my, label, ha="left", va="center",
                fontsize=7.5, color="#3A5A8C", fontstyle="italic", zorder=5)


def arrow_h(ax, cx, cy, hw, direction, tx, ty, th, label=None):
    """Horisontal pil frå side av boks → resultatboks."""
    if direction == "right":
        xf = cx + hw/2
        xt = tx - th/2  # th brukt som w her
    else:
        xf = cx - hw/2
        xt = tx + th/2
    ax.annotate("", xy=(xt, ty), xytext=(xf, cy),
                arrowprops=dict(arrowstyle="-|>", color="#2A5A8C",
                                lw=1.4, mutation_scale=13, zorder=3))
    if label:
        mx = (xf + xt) / 2
        my = cy + 0.12
        ax.text(mx, my, label, ha="center", va="bottom",
                fontsize=7.5, color="#3A5A8C", fontstyle="italic", zorder=5)


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
inp = box(ax, cx, y, rw, 0.62, "Artikkel inn\n(709 stk)", C_INPUT, fs=10)

# ── Regler ───────────────────────────────────────────────────────
rules = [
    ("R1: XYZ = Z?",                        "right", "BEHOLD\nLOKALT",    C_BEHOLD),
    ("R2: ABC = C og XYZ = Y?",             "right", "BEHOLD\nLOKALT",    C_BEHOLD),
    ("R3: A/B + X +\nFOR_MANGE_ORDRER?",    "left",  "OVERFØR\nHVFS",     C_OVERFOR),
    ("R4: K_OVERFØR +\nFOR_MANGE_ORDRER?",  "left",  "OVERFØR\nHVFS",     C_OVERFOR),
    ("R5: A/B + X/Y?",                      "left",  "OVERFØR\nHVFS",     C_OVERFOR),
    ("R6/R7/R8:\nResterende artikler",       "right", "TIL VURDERING\n(manuell)", C_VURDER),
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
              "145 OVERFØR  |  257 BEHOLD  |  284 TIL VURDERING  |  23 MANGLER DATA",
              C_SUMMARY, fs=9)

# Pil ned til oppsummering
arrow_v(ax, prev[0], prev[1], prev[3], cx, y_sum, 0.55)

# ── Tittel ───────────────────────────────────────────────────────
ax.set_title(
    "Regelmotor – sekvensiell beslutningsflyt for HVFS-anbefaling (R1–R8)",
    fontsize=12, fontweight="bold", pad=10, color="#1A2A44",
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig03_Regelmotor.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
