"""
Genererer Fig08_Silhouette.png
Silhouette-score for K = 2–7 (treningsdata, n = 389)
Brukt til å begrunne val av optimalt antal klynger.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
    "axes.linewidth": 0.5,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# ── Fargar (blå palett, konsistent med øvrige figurer) ───────────
C_BAR      = "#7FB3E0"   # lys blå – vanlege stolpar
C_BEST     = "#0B3D8C"   # mørk blå – beste K
C_LINE     = "#2C3E50"   # mørk gråblå – forbindelseslinje
C_TITLE    = "#1A2A44"
C_THRESH   = "#888888"   # grå – minstekrav-linje
C_STAR     = "#D4A017"   # gull – stjernemarkering

# ── Data ─────────────────────────────────────────────────────────
K_values = [2, 3, 4, 5, 6, 7]
scores   = [0.362, 0.383, 0.341, 0.318, 0.305, 0.291]
best_idx = int(np.argmax(scores))
THRESHOLD = 0.30

# ── Plot ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4))

# Stolpefargar
bar_colors = [C_BEST if i == best_idx else C_BAR for i in range(len(K_values))]

# Stolpediagram
bars = ax.bar(
    K_values, scores, color=bar_colors, width=0.55,
    alpha=0.82, edgecolor="white", linewidth=1.0, zorder=2,
)

# Forbindelseslinje mellom score-punkt
ax.plot(
    K_values, scores, color=C_LINE, linewidth=1.0,
    marker="o", markersize=5, markerfacecolor=C_LINE,
    alpha=0.7, zorder=3,
)

# Stjernemarkering på beste K
ax.plot(
    K_values[best_idx], scores[best_idx],
    marker="*", markersize=16, color=C_STAR,
    markeredgecolor=C_TITLE, markeredgewidth=0.6,
    zorder=5,
)

# Minstekrav-linje (0.30)
ax.axhline(
    y=THRESHOLD, color=C_THRESH, linestyle="--",
    linewidth=1.0, alpha=0.7, zorder=1,
)
ax.text(
    max(K_values) + 0.35, THRESHOLD, "Minstekrav (0,30)",
    ha="left", va="center", fontsize=8, color=C_THRESH,
    fontstyle="italic",
)

# Verdietiketter over kvar stolpe
for bar, val, i in zip(bars, scores, range(len(K_values))):
    y_offset = 0.004
    weight = "bold" if i == best_idx else "normal"
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val + y_offset, f"{val:.3f}",
        ha="center", va="bottom",
        fontsize=9.5, fontweight=weight, color=C_TITLE,
    )

# Annotasjon for beste K
ax.annotate(
    "K = 3 valgt\n(høyest score)",
    xy=(K_values[best_idx], scores[best_idx]),
    xytext=(K_values[best_idx] + 1.4, scores[best_idx] + 0.025),
    fontsize=9, color=C_TITLE, fontstyle="italic",
    ha="center",
    arrowprops=dict(
        arrowstyle="-|>", color=C_LINE,
        lw=1.2, mutation_scale=10,
    ),
    zorder=6,
)

# ── Akseformatering ──────────────────────────────────────────────
ax.set_xlabel("Antall klynger (K)", fontsize=10.5)
ax.set_ylabel("Gjennomsnittlig silhouette-score", fontsize=10.5)
ax.set_xticks(K_values)
ax.set_xlim(1.3, 7.7)
ax.set_ylim(0.25, 0.43)
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.02))

# Diskret horisontalt rutenett
ax.grid(axis="y", alpha=0.10, linewidth=0.4, linestyle=":")
ax.set_axisbelow(True)

# ── Tittel ───────────────────────────────────────────────────────
ax.set_title(
    "Silhouette-score for K = 2–7\n"
    "(treningsdata, n = 389)",
    fontsize=11.5, fontweight="bold", color=C_TITLE, pad=12,
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig08_Silhouette.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"Beste K: {K_values[best_idx]} (score = {scores[best_idx]:.3f})")
