"""
Genererer Fig10_Kmeans_Profil.png
Klyngeprofiler for K-means (K=3) – Helse Bergen
Linjediagram med gjennomsnittleg standardisert verdi per feature per klynge.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from fig_style import apply_style, fig_title, COLORS, CLUSTER_COLORS

apply_style()

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

centroids = km.cluster_centers_

# ── Plot ─────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 4))

x_pos = np.arange(len(features))

for cl in sorted(CLUSTER_COLORS):
    color = CLUSTER_COLORS[cl]
    ax.plot(
        x_pos, centroids[cl],
        marker="o", markersize=9, markerfacecolor=color,
        markeredgecolor="white", markeredgewidth=1.2,
        color=color, linewidth=2.0,
        label=f"Klynge {cl + 1} (n={int((km.labels_ == cl).sum())})",
        zorder=3,
    )
    ax.fill_between(x_pos, 0, centroids[cl], color=color, alpha=0.07, zorder=1)

ax.axhline(y=0, color=COLORS["grey"], linewidth=0.9, linestyle="--",
           alpha=0.6, zorder=1)

ax.set_xticks(x_pos)
ax.set_xticklabels(feature_labels)
ax.set_ylabel("Standardisert gjennomsnitt (z-score)")
ax.set_xlim(-0.3, len(features) - 0.7)

ax.legend(loc="best", borderpad=0.4, handlelength=2.0)

plt.tight_layout()
fig_title(fig, "Klyngeprofiler for K-means (K=3)", "Helse Bergen")

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig10_Kmeans_Profil.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
for cl in sorted(CLUSTER_COLORS):
    vals = ", ".join(f"{v:.3f}" for v in centroids[cl])
    print(f"  Klynge {cl+1}: [{vals}]")
