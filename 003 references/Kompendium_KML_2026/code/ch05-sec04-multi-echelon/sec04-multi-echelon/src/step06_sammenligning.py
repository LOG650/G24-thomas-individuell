"""
Steg 6: Sammenligning --- kvantifisering av koordineringsverdi
==============================================================
Samler resultater fra steg 2-5 og lager en endelig oppsummeringsfigur
og JSON-oppsummering: forventet service, total aarlig kostnad, og
fordeling av lagernivaa per node.

Figur: echelon_method.png (prosessdiagram for hele eksemplet)
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / "output"

S_FILLS = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
S_DARKS = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]
PRIMARY = "#1F6587"
INKMUTED = "#556270"
INK = "#1F2933"


def load_all() -> dict:
    data = {}
    for name in ("step01_parameters", "step02_uavhengig_ss",
                 "step03_clark_scarf", "step04_simulering",
                 "step05_sensitivitet"):
        path = OUTPUT_DIR / f"{name}.json"
        with open(path, "r", encoding="utf-8") as f:
            data[name] = json.load(f)
    return data


def plot_method_diagram(output_path: Path) -> None:
    """Seks-stegs prosessdiagram for hele analysen."""
    fig, ax = plt.subplots(figsize=(11.5, 3.2))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 3)
    ax.set_aspect("equal")
    ax.axis("off")

    steps = [
        ("Steg 1", "Datainnsamling:\nnettverk,\netterspørsel, LT"),
        ("Steg 2", "Uavhengig\n$(s,S)$ per lager\n(naiv baseline)"),
        ("Steg 3", "Clark-Scarf\nechelon\nbase-stock"),
        ("Steg 4", "Monte Carlo\nsimulering av\nbegge politikker"),
        ("Steg 5", "Sensitivitet\nvs. $L_0$ og\nvariabilitet"),
        ("Steg 6", "Sammenligning\nav kostnad og\nservice"),
    ]
    n = len(steps)
    step_w = 1.55
    gap = 0.35
    total_w = n * step_w + (n - 1) * gap
    x0 = (12 - total_w) / 2

    for i, (hdr, body) in enumerate(steps):
        xi = x0 + i * (step_w + gap)
        fill = S_FILLS[i % 5]
        dark = S_DARKS[i % 5]
        ax.add_patch(
            patches.FancyBboxPatch(
                (xi, 0.45), step_w, 1.85,
                boxstyle="round,pad=0.04", linewidth=1.6,
                edgecolor=dark, facecolor=fill,
            )
        )
        ax.text(xi + step_w / 2, 2.05, hdr, ha="center", va="center",
                fontsize=10.5, fontweight="bold", color=INK)
        ax.text(xi + step_w / 2, 1.25, body, ha="center", va="center",
                fontsize=8.5, color=INK)
        if i < n - 1:
            ax.annotate(
                "",
                xy=(xi + step_w + gap, 1.375),
                xytext=(xi + step_w, 1.375),
                arrowprops=dict(arrowstyle="->", lw=1.4, color=INKMUTED),
            )

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 6: SAMMENLIGNING")
    print("=" * 60)

    d = load_all()
    params = d["step01_parameters"]
    uav = d["step02_uavhengig_ss"]
    cs = d["step03_clark_scarf"]
    sim = d["step04_simulering"]

    # Sammendrag
    print("\n--- Analytisk estimat (steg 2-3) ---")
    print(f"Uavhengig  : forv. holdekostnad = {uav['total_holding_NOK_per_aar']:,.0f} NOK/aar")
    print(f"Clark-Scarf: forv. holdekostnad = {cs['total_holding_NOK_per_aar']:,.0f} NOK/aar")
    saving = uav["total_holding_NOK_per_aar"] - cs["total_holding_NOK_per_aar"]
    rel = saving / uav["total_holding_NOK_per_aar"]
    print(f"Besparelse : {saving:,.0f} NOK/aar ({rel*100:.1f} %)")

    print("\n--- Simulert (steg 4) ---")
    r_uav = sim["res_uav"]
    r_cs = sim["res_cs"]
    print(f"Uavhengig  : total {r_uav['total_NOK_per_aar']:,.0f} NOK/aar "
          f"(hold: {r_uav['total_holding_NOK_per_aar']:,.0f}, "
          f"backorder: {r_uav['total_backorder_NOK_per_aar']:,.0f})")
    print(f"Clark-Scarf: total {r_cs['total_NOK_per_aar']:,.0f} NOK/aar "
          f"(hold: {r_cs['total_holding_NOK_per_aar']:,.0f}, "
          f"backorder: {r_cs['total_backorder_NOK_per_aar']:,.0f})")

    diff = r_uav["total_NOK_per_aar"] - r_cs["total_NOK_per_aar"]
    rel_sim = diff / r_uav["total_NOK_per_aar"]
    print(f"Besparelse : {diff:,.0f} NOK/aar ({rel_sim*100:.1f} %)")

    # Lagre sammendrag
    summary = {
        "analytisk": {
            "H_uav_NOK_per_aar": uav["total_holding_NOK_per_aar"],
            "H_cs_NOK_per_aar": cs["total_holding_NOK_per_aar"],
            "saving_NOK_per_aar": saving,
            "saving_pct": rel * 100,
        },
        "simulert": {
            "total_uav_NOK_per_aar": r_uav["total_NOK_per_aar"],
            "total_cs_NOK_per_aar": r_cs["total_NOK_per_aar"],
            "saving_NOK_per_aar": diff,
            "saving_pct": rel_sim * 100,
            "type1_uav_mean": float(np.mean(r_uav["type1_per_region"])),
            "type1_cs_mean": float(np.mean(r_cs["type1_per_region"])),
        },
        "inventory_total_uav": float(sum(r_uav["mean_inv_per_node"])),
        "inventory_total_cs": float(sum(r_cs["mean_inv_per_node"])),
    }
    path = OUTPUT_DIR / "step06_sammenligning.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nOppsummering lagret: {path}")

    plot_method_diagram(OUTPUT_DIR / "echelon_method.png")

    print("\nFerdig med steg 6.\n")


if __name__ == "__main__":
    main()
