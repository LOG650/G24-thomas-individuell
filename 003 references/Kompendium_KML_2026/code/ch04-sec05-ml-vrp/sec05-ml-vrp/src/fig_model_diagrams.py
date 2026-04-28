"""
Pedagogiske skjematiske figurer for Modell-delen av sec05
==========================================================

Genererer:
  mlvrp_attention_schematic.png  -- skjema av encoder (felles MLP paa alle
                                    noder) og decoder som peker via
                                    attention paa remaining kunder.
  mlvrp_pointer_decoder.png      -- ett enkelt decoder-steg: kontekst
                                    (graph-embed + last node + capacity)
                                    -> query -> attention-score per node
                                    -> mask -> softmax -> ny aksjon.
  mlvrp_method.png               -- ML-pipeline: datainnsamling -> feature
                                    engineering -> arkitektur -> trening
                                    -> evaluering -> sammenligning.

Lagrer direkte i latex-figurmappen for sec05.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyArrowPatch


# Farger fra theme.tex
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
            / "ch04-nettverksdesign" / "figures")


def _fancy_box(ax, x, y, w, h, text, fill, edge, fontsize=10,
               text_color=None):
    box = patches.FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                 boxstyle="round,pad=0.04,rounding_size=0.12",
                                 linewidth=1.3, edgecolor=edge,
                                 facecolor=fill, zorder=3)
    ax.add_patch(box)
    ax.text(x, y, text, ha="center", va="center", fontsize=fontsize,
            color=text_color or INK, zorder=4)


def _arrow(ax, p, q, color=INKMUTED, style="-|>", lw=1.2, ls="-"):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, color=color,
                                  mutation_scale=12, linewidth=lw,
                                  linestyle=ls, zorder=2))


# ---------------------------------------------------------------
# 1) Attention-skjema: encoder + pointer-decoder
# ---------------------------------------------------------------
def fig_attention_schematic(out: Path):
    fig, ax = plt.subplots(figsize=(12, 6.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 8)
    ax.axis("off")

    # -- Input-sektion: 5 noder (1 depot + 4 kunder) --
    ax.text(1.1, 7.5, "Input: node-features $x_i$",
            fontsize=11, fontweight="bold", color=INK)
    nodes = [
        (1.1, 6.3, "depot\n$(0{,}5,0{,}5,0,1)$", S5),
        (1.1, 5.3, "kunde 1\n$(x_1,y_1,d_1/Q,0)$", S1),
        (1.1, 4.3, "kunde 2\n$(x_2,y_2,d_2/Q,0)$", S1),
        (1.1, 3.3, "kunde 3\n$(x_3,y_3,d_3/Q,0)$", S1),
        (1.1, 2.3, "kunde 4\n$(x_4,y_4,d_4/Q,0)$", S1),
    ]
    for (x, y, t, c) in nodes:
        _fancy_box(ax, x, y, 2.1, 0.75, t, c, S1D, fontsize=8.5)

    # -- Encoder-boks --
    enc_x, enc_y = 4.5, 4.3
    _fancy_box(ax, enc_x, enc_y, 2.1, 3.6,
               "Encoder:\nfelles MLP\n(3 lag, $d=64$)",
               S2, S2D, fontsize=10)

    # Piler fra noder til encoder
    for (_, y, _, _) in nodes:
        _arrow(ax, (2.2, y), (enc_x - 1.05, y), color=INKMUTED)

    # -- Embeddings h_i --
    emb_x = 7.1
    ax.text(emb_x, 7.5, "Embeddings $h_i \\in \\mathbb{R}^d$",
            fontsize=11, fontweight="bold", color=INK)
    for (x, y, _, c) in nodes:
        _fancy_box(ax, emb_x, y, 1.4, 0.7, "$h_i$",
                   c, S1D, fontsize=11)
        _arrow(ax, (enc_x + 1.05, y), (emb_x - 0.7, y), color=INKMUTED)

    # -- Decoder-kontekst --
    ctx_x = 10.2
    ctx_y_top = 6.0
    _fancy_box(ax, ctx_x, ctx_y_top + 0.6, 2.2, 0.7,
               "graph-embed\n$\\bar h = \\frac{1}{N}\\sum_i h_i$",
               S4, S4D, fontsize=8.5)
    _fancy_box(ax, ctx_x, ctx_y_top - 0.3, 2.2, 0.7,
               "last-node embed\n$h_{\\text{last}}$",
               S4, S4D, fontsize=8.5)
    _fancy_box(ax, ctx_x, ctx_y_top - 1.2, 2.2, 0.7,
               "remaining cap\n$c_t / Q$",
               S4, S4D, fontsize=8.5)

    # Samle kontekst
    qbox_x, qbox_y = ctx_x, 3.6
    _fancy_box(ax, qbox_x, qbox_y, 2.2, 0.9,
               "context proj $\\to q_t$", S3, S3D, fontsize=10)
    _arrow(ax, (ctx_x, ctx_y_top + 0.25), (qbox_x, qbox_y + 0.45))
    _arrow(ax, (ctx_x, ctx_y_top - 0.65), (qbox_x, qbox_y + 0.45))
    _arrow(ax, (ctx_x, ctx_y_top - 1.55), (qbox_x, qbox_y + 0.45))

    # -- Attention-score -> softmax -> pointer --
    att_x = 13.1
    _fancy_box(ax, att_x, 4.3, 1.7, 4.6,
               "Attention\n $s_i = C\\tanh((Wq_t+Wh_i)\\cdot v)$\n\nmaske\n(besoekte + kapasitet)\n\nsoftmax\n\n$p(a_t=i)$",
               S1, S1D, fontsize=9)

    # Query-flyten
    _arrow(ax, (qbox_x + 1.1, qbox_y), (att_x - 0.85, 4.3))
    # Embeddings-flyten (fra alle h_i sammen)
    _arrow(ax, (emb_x + 0.7, 4.3), (att_x - 0.85, 4.3), color=S1D)

    ax.text(7.0, 0.7,
            "Samme encoder-vekter deles mellom alle noder. Decoderen "
            "setter sammen konteksten paa hvert steg og peker paa en "
            "gjenvaerende, kapasitet-tillatt node.",
            ha="center", va="center",
            fontsize=9.5, color=INKMUTED, style="italic")

    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {out}")


# ---------------------------------------------------------------
# 2) Pointer-decoder: ett decoder-steg
# ---------------------------------------------------------------
def fig_pointer_decoder(out: Path):
    fig, (ax_left, ax_right) = plt.subplots(1, 2, figsize=(13, 5.6),
                                             gridspec_kw={"width_ratios": [1, 1]})
    # -- Venstre: raa logitter
    ax_left.set_xlim(0, 10)
    ax_left.set_ylim(0, 6)
    ax_left.axis("off")
    ax_left.set_title("(a) Raw attention-scores $s_i$",
                      fontsize=11, fontweight="bold", color=INK, loc="left")

    node_labels = ["depot", "1", "2", "3", "4", "5", "6"]
    raw_scores = np.array([1.2, 2.1, -0.3, 1.7, 0.5, 2.5, -1.0])
    mask = np.array([True, False, True, True, True, True, True])  # 1 er besoekt

    # Tegn sooyler
    xs = np.linspace(1.0, 9.0, len(node_labels))
    bar_max_h = 3.0
    for x, s, m, lbl in zip(xs, raw_scores, mask, node_labels):
        height = 0.5 + 0.5 * (s + 2)  # skaler
        color = S1 if m else "#CBD5E1"
        ax_left.add_patch(patches.Rectangle(
            (x - 0.35, 1.2), 0.7, height, facecolor=color, edgecolor=S1D,
            linewidth=1.1))
        ax_left.text(x, 1.0, lbl, ha="center", va="top",
                     fontsize=10, color=INK)
        ax_left.text(x, 1.25 + height, f"{s:+.1f}", ha="center",
                     va="bottom", fontsize=9, color=INKMUTED)
    ax_left.text(5.0, 0.3,
                 "Rad attention gir en verdi per node, ogsaa de som "
                 "allerede er besoekt.",
                 ha="center", va="center", fontsize=9.5,
                 color=INKMUTED, style="italic")

    # -- Hoyre: etter mask + softmax
    ax_right.set_xlim(0, 10)
    ax_right.set_ylim(0, 6)
    ax_right.axis("off")
    ax_right.set_title("(b) Etter kapasitet- og besoek-maske + softmax",
                       fontsize=11, fontweight="bold", color=INK, loc="left")
    # Mask ut kunde 1 og la kunde 4 vaere kapasitet-fortrengt
    mask_soft = np.array([True, False, True, True, False, True, True])
    # Masked logits
    masked = np.where(mask_soft, raw_scores, -1e9)
    # Softmax
    exps = np.exp(masked - masked.max())
    probs = exps / exps.sum()
    for x, p, m, lbl in zip(xs, probs, mask_soft, node_labels):
        if m:
            height = 3.5 * p
            ax_right.add_patch(patches.Rectangle(
                (x - 0.35, 1.2), 0.7, height, facecolor=S3, edgecolor=S3D,
                linewidth=1.1))
            ax_right.text(x, 1.3 + height, f"{p:.2f}", ha="center",
                          va="bottom", fontsize=9, color=INKMUTED)
        else:
            # Krysset rektangel
            ax_right.add_patch(patches.Rectangle(
                (x - 0.35, 1.2), 0.7, 0.1, facecolor="#CBD5E1",
                edgecolor=INKMUTED, hatch="////"))
        ax_right.text(x, 1.0, lbl, ha="center", va="top",
                      fontsize=10, color=INK)
    # Marker argmax
    best = int(np.argmax(probs))
    ax_right.annotate("valgt: argmax",
                      xy=(xs[best], 1.3 + 3.5 * probs[best]),
                      xytext=(xs[best] + 1.0, 4.9),
                      arrowprops=dict(arrowstyle="->", color=S5D),
                      fontsize=10, color=S5D)
    ax_right.text(5.0, 0.3,
                  "Etter masking gjoeres softmax over de gyldige nodene "
                  "og decoderen peker paa den mest sannsynlige.",
                  ha="center", va="center", fontsize=9.5,
                  color=INKMUTED, style="italic")

    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {out}")


# ---------------------------------------------------------------
# 3) Method-diagram
# ---------------------------------------------------------------
def fig_method(out: Path):
    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.axis("off")

    steps = [
        (1, "Datainnsamling\n(eksakt solver genererer\n$1\\,200$ instanser)", S1, S1D),
        (2, "Feature engineering\n(koord + demand/$Q$ +\n depot-flag)", S1, S1D),
        (3, "Arkitektur\n(encoder-MLP + pointer-\n decoder med attention)", S2, S2D),
        (4, "Trening\n(supervised teacher\n forcing, 40 epoker)", S2, S2D),
        (5, "Evaluering\n(greedy decoding,\n gap til optimum)", S3, S3D),
        (6, "Sammenligning\n(Clarke-Wright / eksakt\n paa ulike n)", S3, S3D),
    ]
    xs = [2.0, 5.0, 8.0, 2.0, 5.0, 8.0]
    ys = [6.0, 6.0, 6.0, 2.5, 2.5, 2.5]
    for (n, text, fill, edge), x, y in zip(steps, xs, ys):
        _fancy_box(ax, x, y, 2.6, 1.35, f"Steg {n}\n\n{text}",
                   fill, edge, fontsize=9)

    # Piler
    order = [(0, 1), (1, 2), (2, 5), (5, 4), (4, 3)]
    for a, b in order:
        xa, ya = xs[a], ys[a]
        xb, yb = xs[b], ys[b]
        # Hoptt rundt boksene
        if ya == yb:
            _arrow(ax, (xa + 1.3, ya), (xb - 1.3, yb))
        else:
            # Hjoerne
            _arrow(ax, (xa, ya - 0.72), (xb, yb + 0.72))

    ax.text(5.0, 0.7,
            "Pipeline fra data -> modell -> maaling mot klassiske baselines.",
            ha="center", va="center",
            fontsize=10, color=INKMUTED, style="italic")

    plt.tight_layout()
    plt.savefig(out, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {out}")


def main():
    out = _latex_fig_dir()
    out.mkdir(parents=True, exist_ok=True)
    fig_attention_schematic(out / "mlvrp_attention_schematic.png")
    fig_pointer_decoder(out / "mlvrp_pointer_decoder.png")
    fig_method(out / "mlvrp_method.png")


if __name__ == "__main__":
    main()
