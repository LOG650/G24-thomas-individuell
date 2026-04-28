"""
Steg 4: Scenario-reduksjon (Kantorovich fast-forward)
=====================================================
Reduserer et stort scenariosett til et mindre representativt sett
via Kantorovich fast-forward-heuristikken. Kantorovich-avstanden
mellom to diskrete fordelinger minimeres ved å iterativt legge
til det scenariet som gir størst reduksjon i avstand.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from solver import Instance, build_and_solve, load_instance

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def generate_large_scenarios(
    customers: pd.DataFrame, n: int, seed: int
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    for s in range(n):
        for _, c in customers.iterrows():
            d = max(0, int(round(rng.normal(c["mu"], c["sigma"]))))
            records.append({"scenario": s, "customer": c["customer"], "demand": d})
    return pd.DataFrame(records)


def fast_forward_reduction(
    scenarios_mat: np.ndarray, n_keep: int, p_full: np.ndarray | None = None
) -> tuple[list[int], np.ndarray]:
    """Kantorovich fast-forward-heuristikk.

    Parameters
    ----------
    scenarios_mat : (N, D)-matrise der rad s er scenario s sin vektor.
    n_keep : antall scenarier å beholde.
    p_full : lik sannsynligheter for originale scenarier (uniform hvis None).
    """
    N = scenarios_mat.shape[0]
    if p_full is None:
        p_full = np.full(N, 1.0 / N)

    # Alle parvise avstander
    # Euklidisk avstand
    diffs = scenarios_mat[:, None, :] - scenarios_mat[None, :, :]
    D = np.sqrt(np.sum(diffs ** 2, axis=-1))

    remaining = list(range(N))
    selected: list[int] = []

    for _ in range(n_keep):
        # For hvert scenario u ikke valgt: beregn "kostnad" hvis vi legger
        # det til S. Kostnaden er sum_{u' remaining} p_full[u'] *
        # min(D[u', v]) for v i S u {u}. Vi velger u som minimerer dette.
        best = None
        best_cost = np.inf
        if not selected:
            # Første iterasjon: velg scenariet som minimerer total
            # avstand til alle andre (vektet med p_full)
            for u in remaining:
                cost = float(np.sum(p_full * D[:, u]))
                if cost < best_cost:
                    best_cost = cost
                    best = u
        else:
            current_min = np.min(D[:, selected], axis=1)
            for u in remaining:
                new_min = np.minimum(current_min, D[:, u])
                cost = float(np.sum(p_full * new_min))
                if cost < best_cost:
                    best_cost = cost
                    best = u

        selected.append(best)
        remaining.remove(best)

    # Tilordne sannsynligheter: hvert originalscenario tildeles nærmeste
    # av de valgte, og vektene summeres.
    nearest = np.argmin(D[:, selected], axis=1)
    p_red = np.zeros(n_keep)
    for s_idx, nearest_idx in enumerate(nearest):
        p_red[nearest_idx] += p_full[s_idx]
    return selected, p_red


def plot_reduction(
    full_mat: np.ndarray,
    selected_idx: list[int],
    p_red: np.ndarray,
    output_path: Path,
) -> None:
    """Projeksjon til 2D (første 2 kundevariabler) av full vs redusert."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    axes[0].scatter(
        full_mat[:, 0],
        full_mat[:, 1],
        s=18,
        c="#8CC8E5",
        alpha=0.5,
        edgecolors="#1F6587",
        linewidths=0.4,
    )
    axes[0].set_title(
        f"Alle {full_mat.shape[0]} originale scenarier",
        fontsize=11,
        fontweight="bold",
    )
    axes[0].set_xlabel(r"Etterspørsel C01", fontsize=10)
    axes[0].set_ylabel(r"Etterspørsel C02", fontsize=10)
    axes[0].grid(True, alpha=0.3)

    # Redusert sett -- boblestørrelse proporsjonal med p_red
    sizes = 40 + 500 * p_red / p_red.max()
    axes[1].scatter(
        full_mat[selected_idx, 0],
        full_mat[selected_idx, 1],
        s=sizes,
        c="#F6BA7C",
        alpha=0.75,
        edgecolors="#9C540B",
        linewidths=1.0,
    )
    axes[1].set_title(
        f"Reduserte {len(selected_idx)} representative scenarier",
        fontsize=11,
        fontweight="bold",
    )
    axes[1].set_xlabel(r"Etterspørsel C01", fontsize=10)
    axes[1].set_ylabel(r"Etterspørsel C02", fontsize=10)
    axes[1].grid(True, alpha=0.3)

    # Samme aksegrenser
    xmin = min(axes[0].get_xlim()[0], axes[1].get_xlim()[0])
    xmax = max(axes[0].get_xlim()[1], axes[1].get_xlim()[1])
    ymin = min(axes[0].get_ylim()[0], axes[1].get_ylim()[0])
    ymax = max(axes[0].get_ylim()[1], axes[1].get_ylim()[1])
    for ax in axes:
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

    fig.suptitle(
        "Kantorovich fast-forward scenario-reduksjon",
        fontsize=12,
        fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("=" * 60)
    print("STEG 4: Scenario-reduksjon")
    print("=" * 60)

    inst = load_instance(DATA_DIR)
    customers = inst.customers

    # Generer et stort scenariosett
    # Pedagogisk demo: vi trenger nok scenarier til at reduksjonen blir
    # meningsfull, men ikke sa mange at MIP-en blir upraktisk. N_FULL=300
    # og N_KEEP=10 holder: reduksjonsraten er 30x, og begge MIP-er kjorer
    # pa rimelig tid (<60s per call).
    N_FULL = 300
    N_KEEP = 10
    print(f"\nGenererer {N_FULL} full-scenarier fra normalfordeling...")
    full_scen_df = generate_large_scenarios(customers, N_FULL, seed=42)

    # Bygg matrise (N_FULL x N_customers)
    mat = full_scen_df.pivot(
        index="scenario", columns="customer", values="demand"
    ).loc[:, customers["customer"].tolist()].to_numpy(dtype=float)

    print(f"Scenario-matrise: {mat.shape}")
    print(f"Kjorer fast-forward-reduksjon til {N_KEEP} scenarier...")
    selected, p_red = fast_forward_reduction(mat, N_KEEP)
    print(f"  Valgte scenario-indekser: {selected}")
    print(f"  Vekter: {np.round(p_red, 4)}")
    print(f"  Total vekt: {p_red.sum():.6f}")

    # Bygg redusert Instance
    red_rows = []
    for new_s, old_s in enumerate(selected):
        for _, c in customers.iterrows():
            demand = int(mat[old_s, customers.index[customers["customer"] == c["customer"]][0]])
            red_rows.append({"scenario": new_s, "customer": c["customer"], "demand": demand})
    red_scenarios_df = pd.DataFrame(red_rows)

    red_inst = Instance(
        dcs=inst.dcs,
        customers=inst.customers,
        modes=inst.modes,
        edges=inst.edges,
        scenarios=red_scenarios_df,
        scenario_probs={s: float(p_red[s]) for s in range(N_KEEP)},
    )

    # Kjor min-cost MIP pa redusert sett og sammenlign med full (pa
    # en delmengde pga tid)
    print(f"\nLoser MIP pa redusert scenariosett ({N_KEEP} scenarier)...")
    r_red = build_and_solve(red_inst, objective="cost", time_limit=45)
    print(f"  Redusert: cost={r_red['total_cost']:,.0f} EUR, emis={r_red['emission_kg']/1000:.1f} tonn, tid={r_red['solve_time_s']:.1f}s")

    # Sammenlign med full: for tidsbegrensning reduserer vi den "fulle"
    # baseline til et middels sett (N_BASE_FULL). 15 scenarier er nok til
    # aa vise kvalitets-konsistens samtidig som det kjorer raskt.
    N_BASE_FULL = 15
    print(f"\nLoser MIP pa middelstort scenariosett ({N_BASE_FULL} scenarier som 'full' baseline)...")
    base_rows = []
    for new_s, old_s in enumerate(range(N_BASE_FULL)):
        for _, c in customers.iterrows():
            demand = int(mat[old_s, customers.index[customers["customer"] == c["customer"]][0]])
            base_rows.append({"scenario": new_s, "customer": c["customer"], "demand": demand})
    base_df = pd.DataFrame(base_rows)

    base_inst = Instance(
        dcs=inst.dcs,
        customers=inst.customers,
        modes=inst.modes,
        edges=inst.edges,
        scenarios=base_df,
    )
    r_base = build_and_solve(base_inst, objective="cost", time_limit=60)
    print(f"  Baseline: cost={r_base['total_cost']:,.0f} EUR, emis={r_base['emission_kg']/1000:.1f} tonn, tid={r_base['solve_time_s']:.1f}s")

    # Gap
    cost_gap = 100 * (r_red["total_cost"] - r_base["total_cost"]) / r_base["total_cost"]
    emis_gap = 100 * (r_red["emission_kg"] - r_base["emission_kg"]) / r_base["emission_kg"]
    speedup = r_base["solve_time_s"] / max(1e-3, r_red["solve_time_s"])
    print(f"\n GAP: cost {cost_gap:+.2f}%, emis {emis_gap:+.2f}%, speedup x{speedup:.1f}")

    result = {
        "n_full": N_BASE_FULL,
        "n_reduced": N_KEEP,
        "reduced": {
            "total_cost": r_red["total_cost"],
            "emission_kg": r_red["emission_kg"],
            "service": r_red["service"],
            "opened": r_red["opened"],
            "solve_time_s": r_red["solve_time_s"],
        },
        "baseline": {
            "total_cost": r_base["total_cost"],
            "emission_kg": r_base["emission_kg"],
            "service": r_base["service"],
            "opened": r_base["opened"],
            "solve_time_s": r_base["solve_time_s"],
        },
        "gap_cost_pct": cost_gap,
        "gap_emission_pct": emis_gap,
        "speedup": speedup,
    }
    with open(OUTPUT_DIR / "step04_reduction.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    plot_reduction(mat, selected, p_red, OUTPUT_DIR / "gronnsc_scenario_reduction.png")


if __name__ == "__main__":
    main()
