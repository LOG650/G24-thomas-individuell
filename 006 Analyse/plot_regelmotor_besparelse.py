"""
Genererer Fig11_Regelmotor_Besparelse.png
Panel 1: Fordeling av HVFS-anbefalingar frå regelmotoren
Panel 2: Estimert EOQ-besparelse under tre scenario
"""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from fig_style import apply_style, fig_title, COLORS

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

df_bes = pd.read_excel(RESULTATER_XLSX, sheet_name="BESPARELSE", header=3)

# ── Data ─────────────────────────────────────────────────────────
regel_labels = ["VURDER\nNÆRMERE", "BEHOLD\nLOKALT", "OVERFØR\nHVFS", "MANGLER\nDATA"]
regel_counts = [
    counts.get("VURDER_NÆRMERE", 0),
    counts.get("BEHOLD_LOKALT", 0),
    counts.get("OVERFØR_HVFS", 0),
    counts.get("MANGLER_DATA", 0),
]
regel_total  = sum(regel_counts)
regel_pcts   = [c / regel_total * 100 for c in regel_counts]
regel_colors = [COLORS["orange"], COLORS["red"], COLORS["green"], COLORS["grey"]]

scenario_labels = ["Worst case\n(g = 50 %)", "Base case\n(g = 75 %)", "Best case\n(g = 100 %)"]
scenario_values = [int(v) for v in df_bes["B_HVFS (TNOK/år)"].tolist()]
scenario_colors = [COLORS["red"], COLORS["orange"], COLORS["green"]]

# ── Plot ─────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5),
                                gridspec_kw={"width_ratios": [1.2, 1]})

# ── Panel 1: Fordeling av anbefalingar ──────────────────────────
bars1 = ax1.barh(
    regel_labels, regel_counts, color=regel_colors,
    height=0.6, alpha=0.92, edgecolor="none", zorder=2,
)

for bar, count, pct in zip(bars1, regel_counts, regel_pcts):
    ax1.text(
        bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
        f"{count}  ({pct:.0f} %)",
        ha="left", va="center",
        fontsize=10, fontweight="bold", color=COLORS["title"],
    )

ax1.set_xlabel("Antall artikler")
ax1.set_title("Fordeling av HVFS-anbefalingar")
ax1.set_xlim(0, max(regel_counts) * 1.35)
ax1.invert_yaxis()
ax1.grid(axis="x")

# ── Panel 2: EOQ-besparelse ─────────────────────────────────────
bars2 = ax2.bar(
    scenario_labels, scenario_values, color=scenario_colors,
    width=0.55, alpha=0.92, edgecolor="none", zorder=2,
)

for bar, val in zip(bars2, scenario_values):
    ax2.text(
        bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
        f"{val} T",
        ha="center", va="bottom",
        fontsize=11, fontweight="bold", color=COLORS["title"],
    )

ax2.set_ylabel("Estimert årleg besparelse (TNOK)")
ax2.set_title("EOQ-besparelse – tre scenario")
ax2.set_ylim(0, max(scenario_values) * 1.18)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(
    lambda x, _: f"{x:.0f}"
))

# ── Tittel og eksport ────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "Regelmotor og besparelsesanalyse", "Helse Bergen")

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig11_Regelmotor_Besparelse.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
