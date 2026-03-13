"""
Genererer Fig09_Kmeans_Profil.png
Klyngeprofiler for K-means (K=3) – Helse Bergen
Linjediagram med gjennomsnittleg standardisert verdi per feature per klynge.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# ── Konfigurasjon ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "Georgia", "DejaVu Serif"],
    "font.size": 10,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

C_TITLE = "#1A2A44"
CLUSTER_COLORS = {
    0: "#0B3D8C",   # blå  – K1
    1: "#D68910",   # oransje – K2
    2: "#1E7D45",   # grøn – K3
}

# ── Les data og køyr K-means ────────────────────────────────────
train = pd.read_csv(
    r"C:\G24\G24-thomas-individuell\006 analyse\LOG650_kmeans_train.csv"
)
features = ["LN_CV", "LN_V", "LN_DTCABS"]
feature_labels = ["CV\n(etterspørselsvariasjon)", "Verdi\n(innkjøpsverdi)",
                   "Kostnadsavvik\n(|ΔTC|)"]

scaler = StandardScaler()
X_train = scaler.fit_transform(train[features])
km = KMeans(n_clusters=3, random_state=42, n_init=10)
km.fit(X_train)

centroids = km.cluster_centers_  # (3, 3) – standardiserte centroidar

# ── Plot ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))

x_pos = np.arange(len(features))

for cl in sorted(CLUSTER_COLORS):
    color = CLUSTER_COLORS[cl]
    ax.plot(
        x_pos, centroids[cl],
        marker="o", markersize=8, markerfacecolor=color,
        markeredgecolor="white", markeredgewidth=1.0,
        color=color, linewidth=2.0, alpha=0.85,
        label=f"Klynge {cl + 1} (n={int((km.labels_ == cl).sum())})",
        zorder=3,
    )

# Referanselinje ved 0
ax.axhline(y=0, color="#AAAAAA", linewidth=0.9, linestyle="--",
           alpha=0.6, zorder=1)

# ── Akseformatering ──────────────────────────────────────────────
ax.set_xticks(x_pos)
ax.set_xticklabels(feature_labels, fontsize=10)
ax.set_ylabel("Standardisert gjennomsnitt (z-score)", fontsize=10.5)
ax.set_xlim(-0.3, len(features) - 0.7)

ax.grid(axis="y", alpha=0.20, linewidth=0.6)
ax.set_axisbelow(True)

# ── Legende ──────────────────────────────────────────────────────
ax.legend(
    fontsize=9, framealpha=0.85, edgecolor="#CCCCCC",
    loc="best", borderpad=0.4, handlelength=2.0,
)

# ── Tittel ───────────────────────────────────────────────────────
ax.set_title(
    "Klyngeprofiler for K-means (K=3) \u2013 Helse Bergen",
    fontsize=12, fontweight="bold", color=C_TITLE, pad=10,
)

# ── Eksporter ────────────────────────────────────────────────────
plt.tight_layout()
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig09_Kmeans_Profil.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
for cl in sorted(CLUSTER_COLORS):
    vals = ", ".join(f"{v:.3f}" for v in centroids[cl])
    print(f"  Klynge {cl+1}: [{vals}]")
