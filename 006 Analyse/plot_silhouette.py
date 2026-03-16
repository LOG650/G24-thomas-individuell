"""
Genererer Fig08_Silhouette.png
Silhouette-score for K = 2–7 (treningsdata, n = 389)
Brukt til å begrunne val av optimalt antal klynger.
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from fig_style import apply_style, fig_title, COLORS

apply_style()

# ── Data ─────────────────────────────────────────────────────────
K_values = [2, 3, 4, 5, 6, 7]
scores   = [0.362, 0.383, 0.341, 0.318, 0.305, 0.291]
best_idx = int(np.argmax(scores))
THRESHOLD = 0.30

# ── Plot ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 4))

# Stolpefargar
bar_colors = [COLORS["blue"] if i == best_idx else COLORS["bar_light"]
              for i in range(len(K_values))]

# Stolpediagram
bars = ax.bar(
    K_values, scores, color=bar_colors, width=0.55,
    alpha=0.92, edgecolor="none", zorder=2,
)

# Forbindelseslinje mellom score-punkt
ax.plot(
    K_values, scores, color=COLORS["line"], linewidth=1.2,
    marker="o", markersize=5, markerfacecolor=COLORS["line"],
    alpha=0.7, zorder=3,
)

# Stjernemarkering på beste K
ax.plot(
    K_values[best_idx], scores[best_idx],
    marker="*", markersize=16, color=COLORS["star"],
    markeredgecolor=COLORS["title"], markeredgewidth=0.6,
    zorder=5,
)

# Minstekrav-linje (0.30)
ax.axhline(
    y=THRESHOLD, color=COLORS["grey"], linestyle="--",
    linewidth=1.0, alpha=0.7, zorder=1,
)
ax.text(
    max(K_values) + 0.35, THRESHOLD, "Minstekrav (0,30)",
    ha="left", va="center", fontsize=9, color=COLORS["grey"],
    fontstyle="italic",
)

# Verdietiketter over kvar stolpe
for bar, val, i in zip(bars, scores, range(len(K_values))):
    weight = "bold" if i == best_idx else "normal"
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        val + 0.004, f"{val:.3f}",
        ha="center", va="bottom",
        fontsize=10, fontweight=weight, color=COLORS["title"],
    )

# Annotasjon for beste K
ax.annotate(
    "K = 3 valgt\n(høyest score)",
    xy=(K_values[best_idx], scores[best_idx]),
    xytext=(K_values[best_idx] + 1.4, scores[best_idx] + 0.025),
    fontsize=9, color=COLORS["title"], fontstyle="italic",
    ha="center",
    arrowprops=dict(
        arrowstyle="-|>", color=COLORS["line"],
        lw=1.2, mutation_scale=10,
    ),
    zorder=6,
)

# ── Akseformatering ──────────────────────────────────────────────
ax.set_xlabel("Antall klynger (K)")
ax.set_ylabel("Gjennomsnittlig silhouette-score")
ax.set_xticks(K_values)
ax.set_xlim(1.3, 7.7)
ax.set_ylim(0.25, 0.43)
ax.yaxis.set_major_locator(mticker.MultipleLocator(0.02))

# ── Tittel og eksport ────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "Silhouette-score for K = 2–7", "Treningsdata, n = 389")

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig08_Silhouette.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"Beste K: {K_values[best_idx]} (score = {scores[best_idx]:.3f})")
