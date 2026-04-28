"""
Steg 6: Sammenligning og visualisering
======================================
Leser resultatene fra steg 5 (rullerende horisont for uavhengig og
koordinert politikk), produserer kostnads- og servicenivåa-
sammenligningsfigurer, samt en skjematisk metodefigur.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import LOCATIONS

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def plot_cost_comparison(indep: dict, coord: dict, output_path: Path) -> None:
    """Stacked bar chart med kostnadskomponenter."""
    categories = ["Bestilling", "Lagerhold", "Restordre", "Transshipment"]
    keys = ["order", "holding", "backorder", "transship"]
    indep_vals = [indep["total_costs"].get(k, 0.0) for k in keys]
    coord_vals = [coord["total_costs"].get(k, 0.0) for k in keys]

    labels = ["Uavhengig (R,S,s)", "Koordinert\n(to-trinns)"]
    colors = ["#8CC8E5", "#97D4B7", "#ED9F9E", "#F6BA7C"]
    fig, ax = plt.subplots(figsize=(8, 6))

    x = np.arange(len(labels))
    bottom_indep = 0
    bottom_coord = 0
    for i, cat in enumerate(categories):
        vals = [indep_vals[i], coord_vals[i]]
        ax.bar(x, vals, bottom=[bottom_indep, bottom_coord], color=colors[i],
               label=cat, edgecolor="#1F2933", linewidth=0.8, width=0.5)
        bottom_indep += indep_vals[i]
        bottom_coord += coord_vals[i]

    # Totaler over stakkene
    ax.text(0, bottom_indep + bottom_indep * 0.02, f"{bottom_indep:,.0f} kr",
            ha="center", fontsize=10, fontweight="bold")
    ax.text(1, bottom_coord + bottom_coord * 0.02, f"{bottom_coord:,.0f} kr",
            ha="center", fontsize=10, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Totalkostnad over 12 perioder (kr)")
    ax.set_title("Kostnadssammenligning: uavhengig vs koordinert styring",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_service_comparison(indep: dict, coord: dict, output_path: Path) -> None:
    """Servicenivåa-sammenligning (fill rate + restordre)."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    labels = ["Uavhengig", "Koordinert"]
    fills = [indep["service_level_fillrate"] * 100, coord["service_level_fillrate"] * 100]
    backorders = [indep["total_backorder_units"], coord["total_backorder_units"]]

    axes[0].bar(labels, fills, color=["#8CC8E5", "#97D4B7"], edgecolor="#1F2933", width=0.5)
    for i, v in enumerate(fills):
        axes[0].text(i, v + 0.5, f"{v:.2f}%", ha="center", fontsize=11, fontweight="bold")
    axes[0].set_ylabel("Fill-rate (%)")
    axes[0].set_ylim(0, max(fills) * 1.12)
    axes[0].set_title("Fill-rate over 12 perioder", fontsize=12, fontweight="bold")
    axes[0].grid(True, axis="y", alpha=0.3)

    axes[1].bar(labels, backorders, color=["#ED9F9E", "#97D4B7"], edgecolor="#1F2933", width=0.5)
    for i, v in enumerate(backorders):
        axes[1].text(i, v + max(backorders) * 0.02, f"{v:,.1f}", ha="center", fontsize=11, fontweight="bold")
    axes[1].set_ylabel("Totale restordre-enheter")
    axes[1].set_title("Summerte restordre", fontsize=12, fontweight="bold")
    axes[1].grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_period_costs(indep: dict, coord: dict, output_path: Path) -> None:
    """Per-periode kostnader for begge politikker."""
    indep_costs = [h["period_cost"] for h in indep["history"]]
    coord_costs = [h["period_cost"] for h in coord["history"]]
    periods = np.arange(1, len(indep_costs) + 1)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(periods, indep_costs, "o-", color="#1F6587", linewidth=2, markersize=7,
            label="Uavhengig (R,S,s)")
    ax.plot(periods, coord_costs, "s-", color="#307453", linewidth=2, markersize=7,
            label="Koordinert (to-trinns)")

    ax.set_xlabel("Periode (uke $t$)", fontsize=12)
    ax.set_ylabel("Periodekostnad (kr)", fontsize=12)
    ax.set_title("Realisert kostnad per periode - rullerende horisont",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="best", fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xticks(periods)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_method(output_path: Path) -> None:
    """Skjematisk metodefigur: to-trinns + scenario-reduksjon + rullerende."""
    fig, ax = plt.subplots(figsize=(11, 6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 7)
    ax.axis("off")

    boxes = [
        (0.5, 4.0, 2.2, 1.2, "Steg 1\nDatainnsamling", "#8CC8E5", "#1F6587"),
        (3.0, 4.0, 2.2, 1.2, "Steg 2\nUavhengig (R,S,s)\nbasislinje", "#8CC8E5", "#1F6587"),
        (5.5, 4.0, 2.2, 1.2, "Steg 3\nScenario-\nreduksjon", "#97D4B7", "#307453"),
        (8.0, 4.0, 2.5, 1.2, "Steg 4\nTo-trinns LP\n(stage 1 + 2)", "#F6BA7C", "#9C540B"),
        (3.0, 1.5, 2.2, 1.2, "Steg 5\nRullerende\nhorisont", "#BD94D7", "#5A2C77"),
        (6.0, 1.5, 2.5, 1.2, "Steg 6\nSammenligning\n+ fill-rate / kostnad", "#ED9F9E", "#961D1C"),
    ]

    for (x, y, w, h, text, fill, stroke) in boxes:
        ax.add_patch(plt.Rectangle((x, y), w, h, facecolor=fill, edgecolor=stroke, linewidth=1.5))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=10, color="#1F2933")

    # Piler horisontalt
    for x_start, x_end in [(2.7, 3.0), (5.2, 5.5), (7.7, 8.0)]:
        ax.annotate("", xy=(x_end, 4.6), xytext=(x_start, 4.6),
                    arrowprops=dict(arrowstyle="->", color="#1F2933", lw=1.5))

    # Pil nedover fra steg 4 til rullerende
    ax.annotate("", xy=(4.1, 2.7), xytext=(9.25, 3.98),
                arrowprops=dict(arrowstyle="->", color="#1F2933", lw=1.5,
                                connectionstyle="arc3,rad=-0.15"))

    # Pil fra rullerende til sammenligning
    ax.annotate("", xy=(6.0, 2.1), xytext=(5.2, 2.1),
                arrowprops=dict(arrowstyle="->", color="#1F2933", lw=1.5))

    # Tilbake-pil (heuristisk loop: ny periode)
    ax.annotate("", xy=(5.5, 4.0), xytext=(4.1, 2.7),
                arrowprops=dict(arrowstyle="->", color="#556270", lw=1.2, ls="--",
                                connectionstyle="arc3,rad=0.3"))
    ax.text(3.0, 3.3, "Neste periode", fontsize=9, color="#556270", style="italic")

    ax.set_title("Prosess: To-trinns stokastisk programmering med rullerende horisont",
                 fontsize=12, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    with open(OUTPUT_DIR / "step05_rolling_horizon.json", encoding="utf-8") as f:
        data = json.load(f)
    indep = data["independent"]
    coord = data["coordinated"]

    print("=" * 60)
    print("STEG 6: Sammenligning")
    print("=" * 60)

    indep_total = indep["total_cost"]
    coord_total = coord["total_cost"]
    savings = indep_total - coord_total
    pct = savings / indep_total * 100 if indep_total else 0.0

    print(f"Totalkostnad uavhengig : {indep_total:,.2f} kr")
    print(f"Totalkostnad koordinert: {coord_total:,.2f} kr")
    print(f"Besparelse             : {savings:,.2f} kr ({pct:.2f}%)")

    print(f"Fill-rate uavhengig : {indep['service_level_fillrate']:.4f}")
    print(f"Fill-rate koordinert: {coord['service_level_fillrate']:.4f}")

    summary = {
        "independent_total_cost": indep_total,
        "coordinated_total_cost": coord_total,
        "savings_kr": float(round(savings, 2)),
        "savings_pct": float(round(pct, 2)),
        "fill_rate_independent": indep["service_level_fillrate"],
        "fill_rate_coordinated": coord["service_level_fillrate"],
        "backorder_independent": indep["total_backorder_units"],
        "backorder_coordinated": coord["total_backorder_units"],
        "n_periods": len(indep["history"]),
    }

    with open(OUTPUT_DIR / "step06_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_cost_comparison(indep, coord, OUTPUT_DIR / "mlstok_cost_comparison.png")
    plot_service_comparison(indep, coord, OUTPUT_DIR / "mlstok_service_comparison.png")
    plot_period_costs(indep, coord, OUTPUT_DIR / "mlstok_period_costs.png")
    plot_method(OUTPUT_DIR / "mlstok_method.png")


if __name__ == "__main__":
    main()
