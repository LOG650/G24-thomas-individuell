"""
Steg 6: Sensitivitetsanalyse og Pareto-front
============================================
For et spekter av servicenivaa alpha i {0.80, 0.85, ..., 0.99} løser vi
shared-capacity problemet og plotter:

1. Pareto-front: total aarlig kostnad vs servicenivaa
2. Sammenligning mot uavhengig (Q,R) uten skranker

Hvis uavhengig losning bryter skrankene, viser vi en \"infeasible\"-merket
linje for a demonstrere at det ikke er et reelt alternativ.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import norm

from step01_datainnsamling import (
    DATA_DIR, OUTPUT_DIR, S_FILLS, S_DARKS, PRIMARY, INKMUTED,
)
from step02_uavhengig_qr import (
    WEEKS_PER_YEAR, independent_qr, loss_function,
)
from step03_modell_formulering import V_MAX_M3, B_MAX_NOK
from step04_optimering import (
    solve_shared_capacity, build_arrays, total_cost, resource_usage,
)


SERVICE_LEVELS = np.array([0.80, 0.85, 0.90, 0.92, 0.94, 0.95, 0.96, 0.97, 0.98, 0.99])


def run_sweep(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    arrs = build_arrays(df)
    for alpha in SERVICE_LEVELS:
        # Uavhengig
        indep = independent_qr(df, alpha=alpha)
        tc_indep = float(indep["total_cost"].sum())
        V_indep = float((df["v"] * (indep["Q_star"] / 2 + indep["SS"])).sum())
        B_indep = float((df["c"] * (indep["Q_star"] / 2 + indep["SS"])).sum())
        volume_feasible = V_indep <= V_MAX_M3
        budget_feasible = B_indep <= B_MAX_NOK

        # Shared capacity
        sol = solve_shared_capacity(df, alpha=alpha, V_max=V_MAX_M3, B_max=B_MAX_NOK)

        rows.append(
            {
                "alpha": round(float(alpha), 3),
                "z": round(float(norm.ppf(alpha)), 3),
                "TC_uavhengig": round(tc_indep, 0),
                "V_uavhengig": round(V_indep, 3),
                "B_uavhengig": round(B_indep, 0),
                "volume_feasible_uavhengig": bool(volume_feasible),
                "budget_feasible_uavhengig": bool(budget_feasible),
                "feasible_uavhengig": bool(volume_feasible and budget_feasible),
                "TC_delt": round(sol["total_cost"], 0),
                "lambda_V": round(sol["lambda_V"], 5),
                "lambda_B": round(sol["lambda_B"], 7),
                "V_delt": round(sol["V_used"], 3),
                "B_delt": round(sol["B_used"], 0),
            }
        )
    return pd.DataFrame(rows)


def plot_pareto(sweep: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.8))

    # Delt kapasitet -- alltid feasible (koordinert)
    ax.plot(
        sweep["alpha"], sweep["TC_delt"] / 1000,
        "-o", color=S_DARKS[0], markersize=6, markerfacecolor=S_FILLS[0],
        label="Delt kapasitet (koordinert)",
    )

    # Uavhengig -- marker feasible vs infeasible
    feasible_mask = sweep["feasible_uavhengig"].values
    ax.plot(
        sweep["alpha"], sweep["TC_uavhengig"] / 1000,
        "--", color=S_DARKS[2], alpha=0.6, label="Uavhengig (uten skranker)",
    )
    if (~feasible_mask).any():
        ax.scatter(
            sweep["alpha"][~feasible_mask], sweep["TC_uavhengig"][~feasible_mask] / 1000,
            color=S_DARKS[4], marker="x", s=70, linewidth=2,
            label="Uavhengig -- bryter skranker",
        )
    if feasible_mask.any():
        ax.scatter(
            sweep["alpha"][feasible_mask], sweep["TC_uavhengig"][feasible_mask] / 1000,
            color=S_DARKS[2], marker="o", s=60, facecolors="none", linewidths=1.8,
            label="Uavhengig -- feasible",
        )

    ax.set_xlabel(r"Type-1 servicenivaa $\alpha$", fontsize=12)
    ax.set_ylabel("Total aarlig kostnad (kNOK)", fontsize=11)
    ax.set_title(
        "Pareto-front: servicenivaa vs. totalkostnad",
        fontsize=12, fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_shadow_vs_alpha(sweep: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))

    ax2 = ax.twinx()
    ax.plot(
        sweep["alpha"], sweep["lambda_V"],
        "-o", color=S_DARKS[0], markerfacecolor=S_FILLS[0],
        label=r"$\lambda_V$ (volum-skyggepris)",
    )
    ax2.plot(
        sweep["alpha"], sweep["lambda_B"] * 1000,
        "-s", color=S_DARKS[2], markerfacecolor=S_FILLS[2],
        label=r"$\lambda_B \cdot 10^{3}$ (kapital)",
    )
    ax.set_xlabel(r"Type-1 servicenivaa $\alpha$", fontsize=12)
    ax.set_ylabel(r"$\lambda_V$", fontsize=12, color=S_DARKS[0])
    ax2.set_ylabel(r"$\lambda_B \cdot 10^{3}$", fontsize=12, color=S_DARKS[2])
    ax.grid(True, alpha=0.3)
    ax.set_title(
        "Skyggepriser som funksjon av servicenivaa",
        fontsize=12, fontweight="bold",
    )
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 6: SENSITIVITETSANALYSE")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "produkter.csv")
    sweep = run_sweep(df)

    print("\nServicenivaa-sweep:")
    print(sweep.to_string(index=False))

    sweep.to_csv(OUTPUT_DIR / "step06_sweep.csv", index=False)
    summary = {
        "alpha_min": float(sweep["alpha"].min()),
        "alpha_max": float(sweep["alpha"].max()),
        "TC_delt_ved_0.95": float(
            sweep.loc[sweep["alpha"] == 0.95, "TC_delt"].iloc[0]
        ),
        "TC_uavhengig_ved_0.95": float(
            sweep.loc[sweep["alpha"] == 0.95, "TC_uavhengig"].iloc[0]
        ),
        "alpha_feasible_uavhengig_max": float(
            sweep.loc[sweep["feasible_uavhengig"], "alpha"].max()
            if sweep["feasible_uavhengig"].any() else -1
        ),
    }
    with open(OUTPUT_DIR / "step06_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_pareto(sweep, OUTPUT_DIR / "multiqr_cost_service_pareto.png")
    plot_shadow_vs_alpha(sweep, OUTPUT_DIR / "multiqr_shadow_vs_alpha.png")


if __name__ == "__main__":
    main()
