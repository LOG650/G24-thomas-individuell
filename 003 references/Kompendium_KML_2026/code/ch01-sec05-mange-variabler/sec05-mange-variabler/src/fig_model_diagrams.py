"""
Pedagogiske skjematiske figurer for Modell-delen av sec05
=========================================================
Lagrer direkte i latex-figurmappen for sec05:

  lgbm_tree_diagram.png     -- ett lite regresjonstre (3 splits) sammen med
                               den akseparallelle partisjonen den induserer
                               i 2D-feature-rommet.
  lgbm_leaf_vs_level.png    -- skjematisk sammenligning av level-wise og
                               leaf-wise trevekst.
  lgbm_boosting_sequence.png -- (bonus) prediksjon- og residualfigur for
                                 boosting-sekvensen, laget fra den
                                 tidligere pickled modellen.

Kjøres frittstående:
    python fig_model_diagrams.py
"""

from __future__ import annotations

import pickle
from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


# ----- tema-farger (speiler theme.tex) -----
S1 = "#8CC8E5"
S1D = "#1F6587"
S2 = "#97D4B7"
S2D = "#307453"
S3 = "#F6BA7C"
S3D = "#9C540B"
S4 = "#BD94D7"
S4D = "#5A2C77"
S5 = "#ED9F9E"
S5D = "#961D1C"
INK = "#1F2933"
INKMUTED = "#556270"
RULE = "#CBD5E1"


def _latex_fig_dir() -> Path:
    return (Path(__file__).resolve().parents[4]
            / "latex" / "200-bodymatter" / "part02-omrader"
            / "ch01-ettersporselprognoser" / "figures")


# ------------------------------------------------------------------
# 1. Regresjonstre-diagram + indusert partisjon i feature-rommet
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


def _leaf_color(value: float) -> str:
    # Bladene fargelegges fra blå (lav prediksjon) til rød (høy prediksjon).
    palette = [S1, S2, S3, S5]
    idx = min(len(palette) - 1, max(0, int(round(value))))
    return palette[idx]


def fig_tree_diagram(output_path: Path) -> None:
    """Tegn et lite regresjonstre (3 splits, 4 blader) ved siden av den
    akseparallelle partisjonen det induserer i 2D-feature-rommet."""
    fig, (ax_tree, ax_part) = plt.subplots(1, 2, figsize=(11.5, 5.2),
                                            gridspec_kw={"width_ratios": [1.05, 1.0]})

    # --- Tre-diagram til venstre ---
    ax_tree.set_xlim(0, 10)
    ax_tree.set_ylim(0, 6)
    ax_tree.axis("off")
    ax_tree.set_title("Beslutningstre $h_m$", fontsize=12, fontweight="bold",
                      color=INK, loc="left")

    # Rot: rabatt > 20 %?
    _draw_node(ax_tree, 5, 5.2, "rabatt > 20 %?", S1, S1D, width=3.0)
    # To indre noder
    _draw_node(ax_tree, 2.4, 3.4, "ukedag $\\in$ {fre, lør}?",
               S1, S1D, width=3.2)
    _draw_node(ax_tree, 7.6, 3.4, "temperatur > 18°?",
               S1, S1D, width=3.0)
    # Blader
    _draw_node(ax_tree, 1.0, 1.5, "$w_{m,1} = 95$", S2, S2D, width=2.0)
    _draw_node(ax_tree, 3.8, 1.5, "$w_{m,2} = 180$", S3, S3D, width=2.0)
    _draw_node(ax_tree, 6.3, 1.5, "$w_{m,3} = 250$", S3, S3D, width=2.0)
    _draw_node(ax_tree, 9.0, 1.5, "$w_{m,4} = 410$", S5, S5D, width=2.0)
    # Kanter
    _draw_edge(ax_tree, 5, 5.2, 2.4, 3.4, "nei", (-0.2, 0))
    _draw_edge(ax_tree, 5, 5.2, 7.6, 3.4, "ja", (0.2, 0))
    _draw_edge(ax_tree, 2.4, 3.4, 1.0, 1.5, "nei", (-0.15, 0))
    _draw_edge(ax_tree, 2.4, 3.4, 3.8, 1.5, "ja", (0.15, 0))
    _draw_edge(ax_tree, 7.6, 3.4, 6.3, 1.5, "nei", (-0.15, 0))
    _draw_edge(ax_tree, 7.6, 3.4, 9.0, 1.5, "ja", (0.15, 0))

    # Liten forklaring under
    ax_tree.text(5, 0.35,
                 "Hver intern node definerer en split-regel; hvert blad har en vekt $w_{m,\\ell}$.",
                 ha="center", va="center", fontsize=9, color=INKMUTED, style="italic")

    # --- Partisjon til høyre ---
    ax_part.set_xlim(0, 40)
    ax_part.set_ylim(0, 35)
    ax_part.set_xlabel("rabatt (%)", fontsize=11, color=INK)
    ax_part.set_ylabel("temperatur (°C)", fontsize=11, color=INK)
    ax_part.set_title("Indusert partisjon $\\{R_{m,\\ell}\\}$ av feature-rommet",
                      fontsize=12, fontweight="bold", color=INK, loc="left")

    # Fire akse-parallelle rektangler. Ukedag = alternativ akse, men for
    # visualiseringen viser vi rabatt (x) vs temperatur (y) og grupperer
    # ukedag-valget som én akse (strekkodet midtdel). Vi forenkler ved å
    # bruke to splittprinsipper på rabatt (>20) og temperatur (>18), og
    # behandler den ene venstre-halvdelen som "ukedag-splittet".
    # R1: rabatt<=20 og ukedag=nei  → lav salg (95)
    # R2: rabatt<=20 og ukedag=ja   → middels (180)
    # R3: rabatt>20  og temp<=18    → høy (250)
    # R4: rabatt>20  og temp>18     → veldig høy (410)

    rects = [
        ((0, 0), 20, 17.5, S2, S2D, "$R_{m,1}$\n$w=95$"),
        ((0, 17.5), 20, 17.5, S3, S3D, "$R_{m,2}$\n$w=180$"),
        ((20, 0), 20, 18, S3, S3D, "$R_{m,3}$\n$w=250$"),
        ((20, 18), 20, 17, S5, S5D, "$R_{m,4}$\n$w=410$"),
    ]
    for (xy, w, h, fc, ec, lbl) in rects:
        ax_part.add_patch(patches.Rectangle(xy, w, h, linewidth=1.2,
                                            edgecolor=ec, facecolor=fc,
                                            alpha=0.85))
        ax_part.text(xy[0] + w / 2, xy[1] + h / 2, lbl,
                     ha="center", va="center", fontsize=10, color=INK)

    # Split-linjer
    ax_part.axvline(20, color=INK, linewidth=1.1, linestyle="--", alpha=0.6)
    ax_part.text(20.3, 34.5, "rabatt = 20 %", color=INKMUTED, fontsize=9,
                 va="top", ha="left")
    ax_part.plot([20, 40], [18, 18], color=INK, linewidth=1.1,
                 linestyle="--", alpha=0.6)
    ax_part.text(39.5, 18.3, "temp = 18°", color=INKMUTED, fontsize=9,
                 va="bottom", ha="right")
    ax_part.plot([0, 20], [17.5, 17.5], color=INK, linewidth=1.1,
                 linestyle="--", alpha=0.6)
    ax_part.text(0.5, 17.8, "ukedag-splitt (skjematisk)",
                 color=INKMUTED, fontsize=9, va="bottom", ha="left")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


# ------------------------------------------------------------------
# 2. Level-wise vs Leaf-wise tree growth
# ------------------------------------------------------------------

def _tree_nodes(positions):
    """Tegn noder og kanter for et lite skjematisk tre."""
    return positions


def fig_leaf_vs_level(output_path: Path) -> None:
    """Tegn to trær side om side: level-wise (balansert) og leaf-wise
    (ubalansert), begge med 8 blader."""
    fig, (ax_lvl, ax_lwf) = plt.subplots(1, 2, figsize=(11.5, 5.0))

    # --- Level-wise (balansert, dybde 3, 8 blader) ---
    ax_lvl.set_xlim(0, 10)
    ax_lvl.set_ylim(0, 6)
    ax_lvl.axis("off")
    ax_lvl.set_title("Level-wise vekst (balansert)",
                     fontsize=12, fontweight="bold", color=INK, loc="left")

    def draw_small(ax, x, y, leaf=False):
        color = S2 if leaf else S1
        edge = S2D if leaf else S1D
        ax.add_patch(patches.Circle((x, y), 0.25, facecolor=color,
                                    edgecolor=edge, linewidth=1.2, zorder=3))

    def draw_small_line(ax, p1, p2):
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=INKMUTED,
                linewidth=1.0, zorder=2)

    # Dybde 0 (rot)
    lvl_nodes = {0: [(5.0, 5.2)]}
    # Dybde 1
    lvl_nodes[1] = [(3.0, 4.0), (7.0, 4.0)]
    # Dybde 2
    lvl_nodes[2] = [(2.0, 2.8), (4.0, 2.8), (6.0, 2.8), (8.0, 2.8)]
    # Dybde 3 (blader)
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

    # --- Leaf-wise (ubalansert, 8 blader) ---
    ax_lwf.set_xlim(0, 10)
    ax_lwf.set_ylim(0, 6)
    ax_lwf.axis("off")
    ax_lwf.set_title("Leaf-wise vekst (ubalansert)",
                     fontsize=12, fontweight="bold", color=INK, loc="left")

    # En gren splittes mye dypere enn de andre.
    # Struktur: rot -> v, h; h -> hv, hh; hh -> hhv, hhh; hhh -> hhhv, hhhh; ...
    # Plasser noder manuelt.
    nodes = {
        "root": (5.0, 5.4),
        "v":    (3.0, 4.4),      # blad (lukket)
        "h":    (7.0, 4.4),
        "h.v":  (5.8, 3.4),      # blad
        "h.h":  (8.2, 3.4),
        "h.h.v": (7.2, 2.4),     # blad
        "h.h.h": (9.0, 2.4),
        "h.h.h.v": (8.4, 1.4),   # blad
        "h.h.h.h": (9.6, 1.4),
        "h.h.h.h.v": (9.2, 0.5), # blad
        "h.h.h.h.h": (9.9, 0.5), # blad
    }
    edges = [
        ("root", "v"), ("root", "h"),
        ("h", "h.v"), ("h", "h.h"),
        ("h.h", "h.h.v"), ("h.h", "h.h.h"),
        ("h.h.h", "h.h.h.v"), ("h.h.h", "h.h.h.h"),
        ("h.h.h.h", "h.h.h.h.v"), ("h.h.h.h", "h.h.h.h.h"),
    ]
    # Vi må legge til én "v"-gren på venstre side for å få 8 blader totalt.
    # Bruk en "venstregren splittes én gang": v deles inn i v.v (blad) og v.h (blad)
    nodes.update({
        "v.v": (2.2, 3.4),
        "v.h": (3.8, 3.4),
    })
    edges.extend([("v", "v.v"), ("v", "v.h")])

    # Bestem blader (slutt-noder)
    leaves = {"v.v", "v.h", "h.v", "h.h.v", "h.h.h.v", "h.h.h.h.v",
              "h.h.h.h.h"}  # 7 så langt
    # Legg til én blad mer for å oppnå 8 totalt: gjør også "h.h.h.v" til blad og
    # legg til "v.h.v" og "v.h.h" for å nå 8 totalt? Enkleste: la de 7 stå og
    # legg til v.v-splitt en gang til.
    nodes.update({
        "v.v.v": (1.7, 2.4),
        "v.v.h": (2.7, 2.4),
    })
    edges.extend([("v.v", "v.v.v"), ("v.v", "v.v.h")])
    leaves.discard("v.v")
    leaves.update({"v.v.v", "v.v.h"})
    # Nå har vi blader: v.v.v, v.v.h, v.h, h.v, h.h.v, h.h.h.v, h.h.h.h.v, h.h.h.h.h = 8

    # Tegn kanter
    for a, b in edges:
        draw_small_line(ax_lwf, nodes[a], nodes[b])

    # Tegn noder
    for key, (x, y) in nodes.items():
        is_leaf = key in leaves
        draw_small(ax_lwf, x, y, leaf=is_leaf)

    # Marker den gjentatt splittede grenen med "høyest gain"
    ax_lwf.annotate("høyest gain velges", xy=(9.3, 2.0), xytext=(6.2, 1.1),
                    fontsize=9, color=S5D,
                    arrowprops=dict(arrowstyle="->", color=S5D, lw=1.1),
                    bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                              edgecolor=S5D))

    ax_lwf.text(5.0, 0.0, "8 blader, dybden vokser der gain er størst",
                ha="center", va="center", fontsize=10, color=INKMUTED,
                style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


# ------------------------------------------------------------------
# 3. Boosting-sekvens (gjenbruker fra step04 med pickled modell)
# ------------------------------------------------------------------

def fig_boosting_sequence_from_pickle(output_path: Path) -> None:
    from step04_modell_estimering import (
        fig_boosting_sequence, load_features_and_splits,
    )
    pickle_path = Path(__file__).parent.parent / "output" / "lgbm_model.pkl"
    with open(pickle_path, "rb") as f:
        bundle = pickle.load(f)
    model = bundle["model"]
    feature_cols = bundle["feature_cols"]
    best_iter = int(bundle.get("best_iteration", model.best_iteration or 1000))

    df, splits = load_features_and_splits()
    val_mask = (df["t"] >= splits["val_start"]) & (df["t"] <= splits["val_end"])
    X_val = df.loc[val_mask, feature_cols].reset_index(drop=True)
    y_val = df.loc[val_mask, "salg"].reset_index(drop=True)

    snapshots = tuple(k for k in (1, 10, 100, 1000) if k <= best_iter)
    fig_boosting_sequence(model, X_val, y_val, output_path, snapshots=snapshots)


def main() -> None:
    out = _latex_fig_dir()
    out.mkdir(parents=True, exist_ok=True)

    fig_tree_diagram(out / "lgbm_tree_diagram.png")
    fig_leaf_vs_level(out / "lgbm_leaf_vs_level.png")
    fig_boosting_sequence_from_pickle(out / "lgbm_boosting_sequence.png")


if __name__ == "__main__":
    main()
