"""
Pedagogiske skjematiske figurer for Modell-delen av ch02 sec05
==============================================================
Lagrer direkte i latex-figurmappen for ch02 sec05:

  mlklasse_tree_diagram.png      -- ett lite regresjonstre (3 splits) sammen
                                    med partisjonen den induserer i 2D-feature-
                                    rommet (volum vs CV).
  mlklasse_leaf_vs_level.png     -- skjematisk sammenligning av level-wise og
                                    leaf-wise trevekst.
  mlklasse_boosting_sequence.png -- prediksjons-sekvens over iterasjoner for
                                    den trente multiclass-modellen (3-klasses
                                    softmax der vi viser sannsynlighet for
                                    rett klasse).

Kjoeres frittstaaende:
    python fig_model_diagrams.py
"""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S4 = "#BD94D7"; S4D = "#5A2C77"
S5 = "#ED9F9E"; S5D = "#961D1C"
INK = "#1F2933"
INKMUTED = "#556270"


def _latex_fig_dir() -> Path:
    return (Path(__file__).resolve().parents[4]
            / "latex" / "200-bodymatter" / "part02-omrader"
            / "ch02-lagerstyring" / "figures")


# ------------------------------------------------------------------
# 1. Regresjonstre-diagram + indusert partisjon
# ------------------------------------------------------------------

def _draw_node(ax, x, y, text, color, edge_color, width=2.0, height=0.65):
    box = patches.FancyBboxPatch((x - width / 2, y - height / 2),
                                 width, height,
                                 boxstyle="round,pad=0.05,rounding_size=0.12",
                                 linewidth=1.4, edgecolor=edge_color,
                                 facecolor=color, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center",
            fontsize=10, color=INK, zorder=4)


def _draw_edge(ax, x1, y1, x2, y2, label, label_offset=(0.0, 0.05)):
    ax.plot([x1, x2], [y1 - 0.33, y2 + 0.33], color=INKMUTED,
            linewidth=1.2, zorder=2)
    mx, my = (x1 + x2) / 2 + label_offset[0], (y1 + y2) / 2 + label_offset[1]
    ax.text(mx, my, label, ha="center", va="center",
            fontsize=9, color=INKMUTED,
            bbox=dict(boxstyle="round,pad=0.2", facecolor="white",
                      edgecolor="none"), zorder=4)


def fig_tree_diagram(output_path: Path) -> None:
    """Tegn et lite regresjonstre i en multiklasse-setting: hver
    blad-verdi er en reell \"score\" for klassen \"kontinuerlig\" i den
    trinnvise oppdateringen. Partisjonsdiagrammet bruker volum vs CV
    som de to foermost diskriminative featurene."""
    fig, (ax_tree, ax_part) = plt.subplots(1, 2, figsize=(11.5, 5.2),
                                            gridspec_kw={"width_ratios": [1.05, 1.0]})

    # --- Tre-diagram (venstre) ---
    ax_tree.set_xlim(0, 10)
    ax_tree.set_ylim(0, 6)
    ax_tree.axis("off")
    ax_tree.set_title("Beslutningstre $h_m$ for klasse k=0 (kontinuerlig)",
                      fontsize=12, fontweight="bold",
                      color=INK, loc="left")

    # Rot: log_omsetning > 12.5?
    _draw_node(ax_tree, 5, 5.2, r"log\_omsetning $> 12{,}5$?",
               S1, S1D, width=3.5)
    # Indre noder
    _draw_node(ax_tree, 2.4, 3.4, r"uke\_cv $\leq 0{,}6$?",
               S1, S1D, width=3.0)
    _draw_node(ax_tree, 7.6, 3.4, r"pris $> 300$?",
               S1, S1D, width=3.0)
    # Blader (bladvekter)
    _draw_node(ax_tree, 1.0, 1.5, r"$w_{m,1} = +0{,}42$",
               S5, S5D, width=2.0)
    _draw_node(ax_tree, 3.8, 1.5, r"$w_{m,2} = +0{,}18$",
               S3, S3D, width=2.0)
    _draw_node(ax_tree, 6.3, 1.5, r"$w_{m,3} = -0{,}15$",
               S2, S2D, width=2.0)
    _draw_node(ax_tree, 9.0, 1.5, r"$w_{m,4} = -0{,}68$",
               S1, S1D, width=2.0)
    # Kanter
    _draw_edge(ax_tree, 5, 5.2, 2.4, 3.4, "ja", (-0.2, 0))
    _draw_edge(ax_tree, 5, 5.2, 7.6, 3.4, "nei", (0.2, 0))
    _draw_edge(ax_tree, 2.4, 3.4, 1.0, 1.5, "ja", (-0.15, 0))
    _draw_edge(ax_tree, 2.4, 3.4, 3.8, 1.5, "nei", (0.15, 0))
    _draw_edge(ax_tree, 7.6, 3.4, 6.3, 1.5, "nei", (-0.15, 0))
    _draw_edge(ax_tree, 7.6, 3.4, 9.0, 1.5, "ja", (0.15, 0))

    ax_tree.text(5, 0.35,
                 r"Hver intern node definerer en split; bladene har vekt $w_{m,\ell}$ "
                 r"som bidrar til klasse-scoren.",
                 ha="center", va="center", fontsize=9, color=INKMUTED,
                 style="italic")

    # --- Partisjon (hoeyre): volum vs CV ---
    ax_part.set_xlim(8, 17)
    ax_part.set_ylim(0, 2.0)
    ax_part.set_xlabel(r"log\_omsetning", fontsize=11, color=INK)
    ax_part.set_ylabel(r"uke\_cv", fontsize=11, color=INK)
    ax_part.set_title(r"Indusert partisjon $\{R_{m,\ell}\}$ i feature-rommet",
                      fontsize=12, fontweight="bold", color=INK, loc="left")

    # Forenklet 4-delt partisjon: log_omsetning > 12.5, og innenfor
    # hvert halvplan et annet split.
    rects = [
        # (xy, w, h, fc, ec, lbl)
        ((12.5, 0.0), 4.5, 0.6, S5, S5D, r"$R_{m,1}$, $w=+0{,}42$"),
        ((12.5, 0.6), 4.5, 1.4, S3, S3D, r"$R_{m,2}$, $w=+0{,}18$"),
        ((8.0, 0.0), 4.5, 1.0, S2, S2D, r"$R_{m,3}$, $w=-0{,}15$"),
        ((8.0, 1.0), 4.5, 1.0, S1, S1D, r"$R_{m,4}$, $w=-0{,}68$"),
    ]
    for (xy, w, h, fc, ec, lbl) in rects:
        ax_part.add_patch(patches.Rectangle(xy, w, h, linewidth=1.2,
                                            edgecolor=ec, facecolor=fc,
                                            alpha=0.85))
        ax_part.text(xy[0] + w / 2, xy[1] + h / 2, lbl,
                     ha="center", va="center", fontsize=10, color=INK)

    # Split-linjer
    ax_part.axvline(12.5, color=INK, linewidth=1.1, linestyle="--", alpha=0.6)
    ax_part.text(12.6, 1.95, r"log\_omsetning $= 12{,}5$",
                 color=INKMUTED, fontsize=9, va="top", ha="left")
    ax_part.plot([12.5, 17.0], [0.6, 0.6], color=INK,
                 linewidth=1.1, linestyle="--", alpha=0.6)
    ax_part.text(16.9, 0.62, r"uke\_cv $= 0{,}6$",
                 color=INKMUTED, fontsize=9, va="bottom", ha="right")
    ax_part.plot([8.0, 12.5], [1.0, 1.0], color=INK,
                 linewidth=1.1, linestyle="--", alpha=0.6)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


# ------------------------------------------------------------------
# 2. Level-wise vs Leaf-wise tree growth
# ------------------------------------------------------------------

def fig_leaf_vs_level(output_path: Path) -> None:
    """Sammenlign level-wise (balansert) og leaf-wise (ubalansert)
    trevekst. Begge har 8 blader totalt."""
    fig, (ax_lvl, ax_lwf) = plt.subplots(1, 2, figsize=(11.5, 5.0))

    def draw_small(ax, x, y, leaf=False):
        color = S2 if leaf else S1
        edge = S2D if leaf else S1D
        ax.add_patch(patches.Circle((x, y), 0.25, facecolor=color,
                                    edgecolor=edge, linewidth=1.2, zorder=3))

    def draw_small_line(ax, p1, p2):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INKMUTED,
                linewidth=1.0, zorder=2)

    # --- Level-wise (balansert, dybde 3) ---
    ax_lvl.set_xlim(0, 10)
    ax_lvl.set_ylim(0, 6)
    ax_lvl.axis("off")
    ax_lvl.set_title("Level-wise vekst (balansert)",
                     fontsize=12, fontweight="bold", color=INK, loc="left")
    lvl_nodes = {0: [(5.0, 5.2)]}
    lvl_nodes[1] = [(3.0, 4.0), (7.0, 4.0)]
    lvl_nodes[2] = [(2.0, 2.8), (4.0, 2.8), (6.0, 2.8), (8.0, 2.8)]
    lvl_nodes[3] = [(1.3, 1.6), (2.7, 1.6),
                    (3.3, 1.6), (4.7, 1.6),
                    (5.3, 1.6), (6.7, 1.6),
                    (7.3, 1.6), (8.7, 1.6)]
    for d in (1, 2, 3):
        for i, (x, y) in enumerate(lvl_nodes[d]):
            parent = lvl_nodes[d - 1][i // 2]
            draw_small_line(ax_lvl, parent, (x, y))
    for d in (0, 1, 2):
        for (x, y) in lvl_nodes[d]:
            draw_small(ax_lvl, x, y)
    for (x, y) in lvl_nodes[3]:
        draw_small(ax_lvl, x, y, leaf=True)
    ax_lvl.text(5.0, 0.6, "8 blader, dybde 3, symmetrisk",
                ha="center", va="center", fontsize=10, color=INKMUTED,
                style="italic")

    # --- Leaf-wise (ubalansert) ---
    ax_lwf.set_xlim(0, 10)
    ax_lwf.set_ylim(0, 6)
    ax_lwf.axis("off")
    ax_lwf.set_title("Leaf-wise vekst (ubalansert)",
                     fontsize=12, fontweight="bold", color=INK, loc="left")

    nodes = {
        "root": (5.0, 5.4),
        "v":    (3.0, 4.4),
        "h":    (7.0, 4.4),
        "h.v":  (5.8, 3.4),
        "h.h":  (8.2, 3.4),
        "h.h.v": (7.2, 2.4),
        "h.h.h": (9.0, 2.4),
        "h.h.h.v": (8.4, 1.4),
        "h.h.h.h": (9.6, 1.4),
        "h.h.h.h.v": (9.2, 0.5),
        "h.h.h.h.h": (9.9, 0.5),
    }
    edges = [
        ("root", "v"), ("root", "h"),
        ("h", "h.v"), ("h", "h.h"),
        ("h.h", "h.h.v"), ("h.h", "h.h.h"),
        ("h.h.h", "h.h.h.v"), ("h.h.h", "h.h.h.h"),
        ("h.h.h.h", "h.h.h.h.v"), ("h.h.h.h", "h.h.h.h.h"),
    ]
    nodes.update({"v.v": (2.2, 3.4), "v.h": (3.8, 3.4)})
    edges.extend([("v", "v.v"), ("v", "v.h")])
    leaves = {"v.v.v", "v.v.h", "v.h", "h.v", "h.h.v", "h.h.h.v",
              "h.h.h.h.v", "h.h.h.h.h"}
    nodes.update({"v.v.v": (1.7, 2.4), "v.v.h": (2.7, 2.4)})
    edges.extend([("v.v", "v.v.v"), ("v.v", "v.v.h")])

    for a, b in edges:
        draw_small_line(ax_lwf, nodes[a], nodes[b])
    for key, (x, y) in nodes.items():
        is_leaf = key in leaves
        draw_small(ax_lwf, x, y, leaf=is_leaf)

    ax_lwf.annotate("hoeyest gain velges", xy=(9.3, 2.0), xytext=(6.2, 1.1),
                    fontsize=9, color=S5D,
                    arrowprops=dict(arrowstyle="->", color=S5D, lw=1.1),
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                              edgecolor=S5D))
    ax_lwf.text(5.0, 0.0, "8 blader, dybden vokser der gain er stoerst",
                ha="center", va="center", fontsize=10, color=INKMUTED,
                style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


# ------------------------------------------------------------------
# 3. Boosting-sekvens for multiclass: sannsynlighet for rett klasse
# ------------------------------------------------------------------

def fig_boosting_sequence(output_path: Path) -> None:
    """Last den trente modellen og vis hvordan sannsynligheten for
    den sanne klassen oekes over iterasjonene for et utvalg i
    valideringssettet. Viser ogsaa hvordan multi-logloss faller."""
    import json
    pickle_path = (Path(__file__).parent.parent / "output" / "lgbm_model.pkl")
    with open(pickle_path, "rb") as f:
        bundle = pickle.load(f)
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    best_iter = int(bundle.get("best_iteration", model.num_trees()))

    # Last validation-settet
    import pandas as pd
    data_dir = Path(__file__).parent.parent / "data"
    out_dir = Path(__file__).parent.parent / "output"
    df = pd.read_parquet(data_dir / "features.parquet")
    with open(out_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    val = df.iloc[splits["val_idx"]].reset_index(drop=True)
    X_val = val[feature_cols]
    y_val = val["klasse"].to_numpy()

    snapshots = tuple(k for k in (1, 5, 20, 50, best_iter) if k <= best_iter)

    fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(10.5, 6.8),
                                          gridspec_kw={"height_ratios": [1.2, 1.1]})

    # Top: for et utvalg 40 SKU-er, vis predikert sannsynlighet for
    # den sanne klassen som funksjon av antall traer.
    colors = [S1D, S2D, S3D, S4D, S5D]
    sample = np.arange(min(40, len(X_val)))
    X_sub = X_val.iloc[sample]
    y_sub = y_val[sample]
    n_sub = len(sample)
    iters = np.arange(1, best_iter + 1)

    # For aa unngaa aa kalle predict paa hver iterasjon: bruk et utvalg
    snapshot_probs = []
    for k in snapshots:
        proba = model.predict(X_sub, num_iteration=k)
        # sannsynlighet for rett klasse per SKU
        p_true = proba[np.arange(n_sub), y_sub]
        snapshot_probs.append(p_true)

    # Boxplot per snapshot
    bp = ax_top.boxplot(snapshot_probs, positions=range(len(snapshots)),
                        widths=0.5, patch_artist=True,
                        tick_labels=[f"m={k}" for k in snapshots])
    fill = [S1, S2, S3, S4, S5][:len(snapshots)]
    edge = [S1D, S2D, S3D, S4D, S5D][:len(snapshots)]
    for patch, fc, ec in zip(bp["boxes"], fill, edge):
        patch.set_facecolor(fc)
        patch.set_edgecolor(ec)
    ax_top.axhline(1/3, color="#556270", linestyle="--", linewidth=0.8,
                   alpha=0.7, label=r"tilfeldig ($1/3$)")
    ax_top.set_ylabel(r"$P(\mathrm{rett~klasse} \mid x)$", fontsize=11)
    ax_top.set_ylim(0, 1.05)
    ax_top.set_title(
        r"Softmax-sannsynligheten for rett klasse \o"
        r"ker med antall tr\ae r (40 valideringsobs.)",
        fontsize=12, fontweight="bold")
    ax_top.grid(True, axis="y", alpha=0.3)
    ax_top.legend(fontsize=9)

    # Bunn: multi-logloss over hele validering
    from sklearn.metrics import log_loss
    logs = []
    sample_idx = np.random.default_rng(0).choice(len(X_val), size=300, replace=False)
    X_big = X_val.iloc[sample_idx]
    y_big = y_val[sample_idx]
    iters_sub = list(range(1, 21)) + list(range(22, best_iter + 1, 4))
    for k in iters_sub:
        proba = model.predict(X_big, num_iteration=k)
        logs.append(log_loss(y_big, proba, labels=[0, 1, 2]))
    ax_bot.plot(iters_sub, logs, color=S1D, linewidth=1.3)
    ax_bot.set_xlabel("Iterasjon $m$", fontsize=11)
    ax_bot.set_ylabel(r"Multi-logloss $\mathcal{L}(F_m)$", fontsize=11)
    ax_bot.set_title(r"Tapet faller mot et plat\aa\ naar ensemblet bygges opp",
                     fontsize=12, fontweight="bold")
    ax_bot.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    out = _latex_fig_dir()
    out.mkdir(parents=True, exist_ok=True)

    fig_tree_diagram(out / "mlklasse_tree_diagram.png")
    fig_leaf_vs_level(out / "mlklasse_leaf_vs_level.png")
    fig_boosting_sequence(out / "mlklasse_boosting_sequence.png")


if __name__ == "__main__":
    main()
