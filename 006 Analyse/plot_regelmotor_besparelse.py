"""
Genererer Fig10_Regelmotor_Besparelse.png
Panel 1: Fordeling av HVFS-anbefalingar frå regelmotoren
Panel 2: Estimert EOQ-besparelse under tre scenario
"""

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

C_TITLE = "#1A2A44"

# Fargar (konsistent med øvrige figurer)
C_OVERFOR  = "#1E7D45"   # grøn – overfør HVFS
C_BEHOLD   = "#B03A2E"   # raud – behold lokalt
C_VURDER   = "#D68910"   # oransje – vurder nærmare
C_MANGLER  = "#888888"   # grå – manglar data

# Besparelsesfargar
C_WORST = "#B03A2E"   # raud
C_BASE  = "#D68910"   # oransje
C_BEST  = "#1E7D45"   # grøn

# ── Data ─────────────────────────────────────────────────────────
# Regelmotor-resultat (frå Fig03 oppsummering, n=709)
regel_labels = ["VURDER\nNÆRMERE", "BEHOLD\nLOKALT", "OVERFØR\nHVFS", "MANGLER\nDATA"]
regel_counts = [284, 257, 145, 23]
regel_total  = sum(regel_counts)
regel_pcts   = [c / regel_total * 100 for c in regel_counts]
regel_colors = [C_VURDER, C_BEHOLD, C_OVERFOR, C_MANGLER]

# Besparelse-scenario (EOQ-basert)
scenario_labels = ["Worst case\n(g = 50 %)", "Base case\n(g = 75 %)", "Best case\n(g = 100 %)"]
scenario_values = [301, 452, 602]  # tusen NOK
scenario_colors = [C_WORST, C_BASE, C_BEST]

# ── Plot ─────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5),
                                gridspec_kw={"width_ratios": [1.2, 1]})

# ── Panel 1: Fordeling av anbefalingar ──────────────────────────
bars1 = ax1.barh(
    regel_labels, regel_counts, color=regel_colors,
    height=0.6, alpha=0.80, edgecolor="white", linewidth=1.0, zorder=2,
)

# Verdiar og prosent til høgre for kvar stolpe
for bar, count, pct in zip(bars1, regel_counts, regel_pcts):
    ax1.text(
        bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
        f"{count}  ({pct:.0f} %)",
        ha="left", va="center",
        fontsize=10, fontweight="bold", color=C_TITLE,
    )

ax1.set_xlabel("Antall artikler", fontsize=10.5)
ax1.set_title("Fordeling av HVFS-anbefalingar", fontsize=11,
              fontweight="bold", color=C_TITLE, pad=8)
ax1.set_xlim(0, max(regel_counts) * 1.35)
ax1.invert_yaxis()

ax1.grid(axis="x", alpha=0.20, linewidth=0.6)
ax1.set_axisbelow(True)

# ── Panel 2: EOQ-besparelse ─────────────────────────────────────
bars2 = ax2.bar(
    scenario_labels, scenario_values, color=scenario_colors,
    width=0.55, alpha=0.80, edgecolor="white", linewidth=1.0, zorder=2,
)

# Verdiar over kvar stolpe
for bar, val in zip(bars2, scenario_values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
        f"{val} T",
        ha="center", va="bottom",
        fontsize=11, fontweight="bold", color=C_TITLE,
    )

ax2.set_ylabel("Estimert årleg besparelse (TNOK)", fontsize=10.5)
ax2.set_title("EOQ-besparelse – tre scenario", fontsize=11,
              fontweight="bold", color=C_TITLE, pad=8)
ax2.set_ylim(0, max(scenario_values) * 1.18)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x:.0f}"
))

ax2.grid(axis="y", alpha=0.20, linewidth=0.6)
ax2.set_axisbelow(True)

# ── Hovudtittel ──────────────────────────────────────────────────
fig.suptitle(
    "Regelmotor og besparelsesanalyse \u2013 Helse Bergen",
    fontsize=12, fontweight="bold", color=C_TITLE, y=0.98,
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.93])
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig10_Regelmotor_Besparelse.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
