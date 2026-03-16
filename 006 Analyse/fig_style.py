"""
Felles stilkonfigurasjon for alle figurar i LOG650-prosjektet.
Importerast av alle plot_*.py-script.

Bruk:
    from fig_style import apply_style, fig_title, COLORS
    apply_style()
    fig, ax = plt.subplots(...)
    ...
    fig_title(fig, "Hovudtittel", "Undertittel med detaljar")

Stil: The Economist / Financial Times editorial dataviz.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.transforms as mtransforms

# ── Signaturlinje ───────────────────────────────────────────────
ACCENT = "#2B5B8A"   # mørk blå – visuell signatur (topplinje)

# ── Fargepalett (semantisk, dempa) ──────────────────────────────
COLORS = {
    "blue":      "#4C72B0",
    "green":     "#55A868",
    "orange":    "#DD8452",
    "red":       "#C44E52",
    "grey":      "#8C8C8C",
    "title":     "#1A1A1A",
    "subtitle":  "#666666",
    "label":     "#555555",
    "line":      "#333333",
    "star":      "#CCAA44",
    "light":     "#D6EAFF",
    "bar_light": "#8FBBD9",
    "edge":      "#4C72B0",
}

BLUE_GRADIENT = [
    "#D6E8F5", "#B8D4ED", "#8FBBD9",
    "#6BA3C8", "#4C89B5", "#3570A0", "#1D5A8C",
]

CLUSTER_COLORS = {
    0: "#4C72B0",
    1: "#DD8452",
    2: "#55A868",
}

PALETTE = [
    COLORS["blue"], COLORS["green"], COLORS["orange"],
    COLORS["red"], COLORS["grey"],
]

DIAGRAM_COLORS = {
    "input":   "#4C72B0",
    "rule":    "#5A7D9A",
    "summary": "#3D5060",
    "zone_1":  "#EDF2F7",
    "zone_2":  "#E2EAF2",
    "zone_3":  "#D6E2ED",
    "zone_edge_1": "#C8D6E5",
    "zone_edge_2": "#B0C4D8",
    "zone_edge_3": "#98B2CB",
    "zone_label":  "#5A7D9A",
}

HIER_COLORS = {
    "top":      "#1D5A8C",
    "mid_main": "#3570A0",
    "mid_side": "#B8D4ED",
    "bottom":   "#D6E8F5",
}


# ── Hovudfunksjon: set stil ─────────────────────────────────────

def apply_style():
    """Set The Economist / FT editorial stil via rcParams."""
    plt.rcParams.update({
        # ── Font (sans-serif, Economist-aktig) ──────────────────
        "font.family":        "sans-serif",
        "font.sans-serif":    ["Segoe UI", "Helvetica Neue", "Arial"],
        "font.size":          10,
        # ── Spines: alle av ─────────────────────────────────────
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.spines.left":   False,
        "axes.spines.bottom": False,
        # ── Grid: berre horisontale, subtile ────────────────────
        "axes.grid":          True,
        "axes.grid.axis":     "y",
        "axes.axisbelow":     True,
        "grid.color":         "#DCDCDC",
        "grid.linewidth":     0.6,
        "grid.linestyle":     "-",
        "grid.alpha":         1.0,
        # ── Tick ────────────────────────────────────────────────
        "xtick.major.size":   0,
        "ytick.major.size":   0,
        "xtick.labelsize":    9,
        "ytick.labelsize":    9,
        "xtick.color":        "#555555",
        "ytick.color":        "#555555",
        # ── Akse-etikettar ──────────────────────────────────────
        "axes.labelsize":     10,
        "axes.labelcolor":    "#555555",
        "axes.titlesize":     12,
        "axes.titleweight":   "bold",
        "axes.titlecolor":    COLORS["title"],
        # ── Bakgrunn: reinhvit ──────────────────────────────────
        "axes.facecolor":     "#FFFFFF",
        "figure.facecolor":   "#FFFFFF",
        # ── Legende: ingen ramme ────────────────────────────────
        "legend.frameon":     False,
        "legend.fontsize":    9,
        "legend.borderpad":   0.4,
        # ── Fargesyklus ─────────────────────────────────────────
        "axes.prop_cycle":    plt.cycler("color", PALETTE),
        # ── Eksport ─────────────────────────────────────────────
        "figure.dpi":         150,
        "savefig.dpi":        300,
        "savefig.bbox":       "tight",
        "savefig.facecolor":  "white",
    })


# ── Tittel i Economist-stil ─────────────────────────────────────

def fig_title(fig, headline, subtitle=None):
    """
    Teikn tittel i The Economist-stil:
      - Blå topplinje (signatur)
      - Hovudtittel i bold
      - Undertittel i regular, grå

    Kall ETTER fig.tight_layout() / plt.tight_layout().
    """
    # Blå topplinje – full breidd, 3pt tjukk
    fig.patches.append(mpatches.FancyBboxPatch(
        (0.0, 0.97), 1.0, 0.03,
        boxstyle="square,pad=0",
        facecolor=ACCENT, edgecolor="none",
        transform=fig.transFigure, figure=fig,
        zorder=10,
    ))

    # Hovudtittel – bold, mørk
    y_headline = 0.94
    fig.text(
        0.02, y_headline, headline,
        fontsize=14, fontweight="bold", color=COLORS["title"],
        ha="left", va="top",
        transform=fig.transFigure, zorder=11,
    )

    # Undertittel – regular, grå
    if subtitle:
        fig.text(
            0.02, y_headline - 0.04, subtitle,
            fontsize=10, fontweight="normal", color=COLORS["subtitle"],
            ha="left", va="top",
            transform=fig.transFigure, zorder=11,
        )


# ── Delte hjelparar for diagramskript ───────────────────────────

def draw_box(ax, cx, cy, w, h, label, facecolor,
             textcolor="#333333", fontsize=9, zorder=2,
             edgecolor=None, linewidth=0.5):
    """Teikn ein boks med avrunda hjørner, sentrert på (cx, cy)."""
    if edgecolor is None:
        edgecolor = "none"
    rect = mpatches.FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.14",
        facecolor=facecolor, edgecolor=edgecolor,
        linewidth=linewidth, zorder=zorder,
    )
    ax.add_patch(rect)
    ax.text(cx, cy, label, ha="center", va="center",
            fontsize=fontsize, fontweight="bold",
            color=textcolor, zorder=zorder + 1,
            linespacing=1.3)
    return cx, cy, w, h


def draw_arrow_v(ax, x1, y1, h1, x2, y2, h2, label=None):
    """Vertikal pil frå botn av boks 1 til topp av boks 2."""
    yf = y1 - h1 / 2
    yt = y2 + h2 / 2
    ax.annotate("", xy=(x2, yt), xytext=(x1, yf),
                arrowprops=dict(
                    arrowstyle="-|>", color="#7A9CB8",
                    lw=1.4, mutation_scale=14, zorder=3,
                ))
    if label:
        mx = (x1 + x2) / 2
        my = (yf + yt) / 2
        ax.text(mx + 0.12, my, label,
                ha="left", va="center",
                fontsize=8, color="#5A7D9A",
                fontstyle="italic", zorder=5)


def draw_arrow_h(ax, x_from, y_from, x_to, y_to, label=None):
    """Horisontal pil mellom to punkt."""
    ax.annotate("", xy=(x_to, y_to), xytext=(x_from, y_from),
                arrowprops=dict(
                    arrowstyle="-|>", color="#7A9CB8",
                    lw=1.4, mutation_scale=14,
                    connectionstyle="arc3,rad=0", zorder=4,
                ))
    if label:
        mx = (x_from + x_to) / 2
        my = y_from + 0.12
        ax.text(mx, my, label,
                ha="center", va="bottom",
                fontsize=8, color="#5A7D9A",
                fontstyle="italic", zorder=5)
