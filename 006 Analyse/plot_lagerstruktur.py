"""
Genererer Fig01_Lagerstruktur.png
Organisering av regionalt lager – Helse Vest forsyningskjede (forenklet)

Horisontal materialflyt: Leverandører → Regionalt lager → Sykehus → Avdelinger
Nedre del: rollefordeling (Helse Vest RHF, Driftsoperatør, Sykehusene)
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from fig_style import apply_style, fig_title, COLORS, HIER_COLORS, draw_box, draw_arrow_h

apply_style()

fig, ax = plt.subplots(figsize=(14, 7))
ax.set_xlim(0, 14)
ax.set_ylim(0, 7)
ax.axis("off")

# ── Flytboksar (øvre del) ──────────────────────────────────────
bh = 0.85
y_flow = 5.8

lev = draw_box(ax, 1.5, y_flow, 2.0, bh,
               "Leverandører", HIER_COLORS["mid_side"], fontsize=10)

reg = draw_box(ax, 5.2, y_flow, 2.8, bh,
               "Regionalt lager\nHVFS", HIER_COLORS["top"],
               textcolor="white", fontsize=10)

syk = draw_box(ax, 9.2, y_flow, 2.0, bh,
               "Sykehus", HIER_COLORS["mid_main"],
               textcolor="white", fontsize=10)

# «Sentrallager»-etikett under Sykehus
ax.text(9.2, y_flow - bh / 2 - 0.12, "Sentrallager",
        ha="center", va="top", fontsize=8, color=COLORS["label"],
        fontstyle="italic")

avd = draw_box(ax, 12.5, y_flow, 2.0, bh,
               "Avdelinger", HIER_COLORS["mid_side"], fontsize=10)

# ── Pilar mellom flytboksar ─────────────────────────────────────
draw_arrow_h(ax, lev[0] + lev[2] / 2, y_flow,
             reg[0] - reg[2] / 2, y_flow, label="Transport")

draw_arrow_h(ax, reg[0] + reg[2] / 2, y_flow,
             syk[0] - syk[2] / 2, y_flow, label="Transport")

draw_arrow_h(ax, syk[0] + syk[2] / 2, y_flow,
             avd[0] - avd[2] / 2, y_flow, label="Forsyning")

# ── Grøn materialflytpil ────────────────────────────────────────
bar_y = y_flow - 0.85
ax.annotate("", xy=(13.3, bar_y), xytext=(0.5, bar_y),
            arrowprops=dict(arrowstyle="-|>", color=COLORS["green"],
                            lw=4, mutation_scale=20, zorder=2))

# ── Rolleboksar (nedre del) ─────────────────────────────────────
role_y = 2.3
role_h = 2.6
role_w = 4.0
role_xs = [2.3, 7.0, 11.7]

# Bakgrunnar
for rx in role_xs:
    bg = mpatches.FancyBboxPatch(
        (rx - role_w / 2, role_y - role_h / 2), role_w, role_h,
        boxstyle="round,pad=0.15",
        facecolor="#F5F8FB", edgecolor="#D0DCE8",
        linewidth=0.8, zorder=1)
    ax.add_patch(bg)

# Hjelpar: tittel + kulepunkt, venstrejustert inne i boks
def _role_text(ax, cx, y_top, title, lines, w):
    """Skriv rolletittel + kulepunkt venstrejustert i rolleboks."""
    ax.text(cx, y_top, title,
            ha="center", va="top",
            fontsize=9.5, fontweight="bold", color=COLORS["title"])
    txt = "\n".join(f"•  {l}" for l in lines)
    ax.text(cx - w / 2 + 0.35, y_top - 0.30, txt,
            ha="left", va="top",
            fontsize=7.5, color=COLORS["label"], linespacing=1.6)

y_title = role_y + role_h / 2 - 0.25

# ── Helse Vest RHF ──────────────────────────────────────────────
_role_text(ax, 2.3, y_title, "Helse Vest RHF", [
    "Bestilling fra avtaleleverandører",
    "Min/maks lagernivå og bestillingspunkt",
    "Fakturamottak og avstemming",
    "Forvaltning av prediksjonsmodell",
    "Lagerbeholdning i Power BI",
], role_w)

# ── Driftsoperatør ──────────────────────────────────────────────
_role_text(ax, 7.0, y_title, "Driftsoperatør (NorEngros)", [
    "Mottak fra leverandører",
    "Lagerstyring og lagerføring",
    "Plukk, pakking og distribusjon",
    "Kommunisere lagerbeholdning",
    "Mottaks- og salgsrapporter",
], role_w)

# ── Sykehusene ──────────────────────────────────────────────────
_role_text(ax, 11.7, y_title, "Sykehusene", [
    "Mottak av varer",
    "Forsyning til avdelinger",
    "Aktiv forsyning (plassering)",
    "Bestilling og retur av varer",
], role_w)

# ── Eksporter ───────────────────────────────────────────────────
plt.tight_layout()
fig_title(fig, "Lagerstruktur",
          "Organisering av regionalt lager – Helse Vest forsyningskjede (forenklet)")
out = r"C:\G24\G24-thomas-individuell\006 analyse\plots\Fig01_Lagerstruktur.png"
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
plt.close()
print(f"Lagret: {out}")
