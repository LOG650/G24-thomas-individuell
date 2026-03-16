"""
Genererer Fig09_Kmeans_Klynger.png
K-means klyngeanalyse (K=3) – to paneler:
  Panel 1: Forbruksstabilitet vs Verdi
  Panel 2: Forbruksstabilitet vs Kostnadsavvik
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from fig_style import apply_style, fig_title, COLORS, CLUSTER_COLORS

apply_style()

CLUSTER_NAMES = {0: "K1", 1: "K2", 2: "K3"}

# ── Les data ─────────────────────────────────────────────────────
train = pd.read_csv(
    r"C:\G24\G24-thomas-individuell\006 analyse\LOG650_kmeans_train.csv"
)
test = pd.read_csv(
    r"C:\G24\G24-thomas-individuell\006 analyse\LOG650_kmeans_test.csv"
)

features = ["LN_CV", "LN_V", "LN_DTCABS"]

# ── Standardisering og K-means ──────────────────────────────────
scaler = StandardScaler()
X_train = scaler.fit_transform(train[features])
X_test = scaler.transform(test[features])

km = KMeans(n_clusters=3, random_state=42, n_init=10)
train["CLUSTER"] = km.fit_predict(X_train)
test["CLUSTER"] = km.predict(X_test)

# Z-score kolonnar
for i, f in enumerate(features):
    train[f"z_{f}"] = X_train[:, i]
    test[f"z_{f}"] = X_test[:, i]

centroids = km.cluster_centers_

sil_train = silhouette_score(X_train, train["CLUSTER"])
sil_test = silhouette_score(X_test, test["CLUSTER"])

n_train = train["CLUSTER"].value_counts().sort_index()
n_test = test["CLUSTER"].value_counts().sort_index()

# ── Plot ─────────────────────────────────────────────────────────
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))

def scatter_panel(ax, x_col, y_col, y_label, title):
    feat_idx_x = features.index("LN_CV")
    feat_idx_y = features.index(y_col.replace("z_", ""))

    for cl in sorted(CLUSTER_COLORS):
        color = CLUSTER_COLORS[cl]
        name = CLUSTER_NAMES[cl]
        nt = n_train.get(cl, 0)
        nte = n_test.get(cl, 0)

        mask_tr = train["CLUSTER"] == cl
        ax.scatter(
            train.loc[mask_tr, x_col], train.loc[mask_tr, y_col],
            c=color, s=22, alpha=0.6, edgecolors="none",
            zorder=2, label=f"{name} tren ({nt})",
        )

        mask_te = test["CLUSTER"] == cl
        ax.scatter(
            test.loc[mask_te, x_col], test.loc[mask_te, y_col],
            c="none", s=30, alpha=0.7, edgecolors=color,
            linewidths=1.0, marker="D",
            zorder=3, label=f"{name} test ({nte})",
        )

        ax.scatter(
            centroids[cl, feat_idx_x], centroids[cl, feat_idx_y],
            marker="X", s=130, c=color,
            edgecolors=COLORS["title"], linewidths=0.8,
            zorder=4,
        )

    ax.axhline(y=0, color=COLORS["grey"], linewidth=0.7, linestyle="--",
               alpha=0.5, zorder=0)
    ax.axvline(x=0, color=COLORS["grey"], linewidth=0.7, linestyle="--",
               alpha=0.5, zorder=0)

    ax.set_xlabel("z(ln(CV))  \u2190 stabil | variabel \u2192")
    ax.set_ylabel(y_label)
    ax.set_title(title)
    ax.grid(axis="both")  # scatter treng begge aksar


scatter_panel(
    ax1, "z_LN_CV", "z_LN_V",
    "z(ln(v+1))  \u2190 lav verdi | h\u00f8y verdi \u2192",
    "K-means (K=3): Forbruksstabilitet vs Verdi",
)

scatter_panel(
    ax2, "z_LN_CV", "z_LN_DTCABS",
    "z(ln(|\u0394TC|+1))  \u2190 lavt avvik | h\u00f8yt avvik \u2192",
    "K-means (K=3): Forbruksstabilitet vs Kostnadsavvik",
)

# ── Legende ──────────────────────────────────────────────────────
handles = []
for cl in sorted(CLUSTER_COLORS):
    color = CLUSTER_COLORS[cl]
    name = CLUSTER_NAMES[cl]
    nt = n_train.get(cl, 0)
    nte = n_test.get(cl, 0)
    handles.append(mlines.Line2D(
        [], [], marker="o", color="none", markerfacecolor=color,
        markersize=6, label=f"{name} tren ({nt})",
    ))
    handles.append(mlines.Line2D(
        [], [], marker="D", color="none", markerfacecolor="none",
        markeredgecolor=color, markeredgewidth=1.0,
        markersize=5, label=f"{name} test ({nte})",
    ))
handles.append(mlines.Line2D(
    [], [], marker="X", color="none", markerfacecolor="#666666",
    markeredgecolor=COLORS["title"], markersize=8, label="Centroid",
))

ax1.legend(
    handles=handles, loc="lower left",
    fontsize=7.5, ncol=2, columnspacing=0.8, handletextpad=0.3,
    borderpad=0.4, labelspacing=0.3,
)

# ── Tittel og eksport ────────────────────────────────────────────
plt.tight_layout(rect=[0, 0, 1, 0.88])
fig_title(fig, "K-means klyngeanalyse",
          f"Helse Bergen \u2013 Sil tren = {sil_train:.3f} | Sil test = {sil_test:.3f}")
fig.subplots_adjust(top=0.83)  # ekstra plass under undertittel

out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig09_Kmeans_Klynger.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
print(f"Sil tren={sil_train:.3f}, Sil test={sil_test:.3f}")
print(f"Klyngestorleik (tren): {n_train.to_dict()}")
print(f"Klyngestorleik (test): {n_test.to_dict()}")
