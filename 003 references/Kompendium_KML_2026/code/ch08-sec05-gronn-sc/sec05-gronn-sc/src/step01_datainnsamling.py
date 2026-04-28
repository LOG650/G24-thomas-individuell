"""
Steg 1: Datainnsamling
======================
Genererer et skandinavisk distribusjonsnett med 6 DC-kandidater,
50 kunder, 3 transportmoduser (lastebil, tog, skip), og scenario-basert
etterspørsel. Utslippsfaktorer er basert på DEFRA (2023).

Kjøring lagrer:
- data/dc_candidates.csv
- data/customers.csv
- data/modes.csv
- data/edges.csv      (fra DC til kunde pr modus med kost/utslipp/service)
- data/scenarios.csv  (etterspørselsrealiseringer pr kunde/scenario)
- output/gronnsc_network.png
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"

SEED = 20260420

# DC-kandidater: (navn, lat, lon, kapasitet, fast kost EUR/år)
DC_CANDIDATES = [
    ("Oslo",       59.91, 10.75, 4000, 520_000),
    ("Goteborg",   57.71, 11.97, 5000, 600_000),
    ("Stockholm",  59.33, 18.07, 4500, 580_000),
    ("Malmo",      55.60, 13.00, 3800, 480_000),
    ("Trondheim",  63.43, 10.39, 3000, 420_000),
    ("Kobenhavn",  55.68, 12.57, 4200, 560_000),
]

# Transportmoduser med kost og utslipp pr tonnkm (DEFRA-basert).
# Kost pr tkm gjort litt nærmere enn ren spot-pris, slik at moderate
# karbonpriser (EU ETS-niva 50-150 EUR/tonn) kan snu balansen. Terminal-
# kost for rail/ship paa korte strekninger modelleres i build_edges.
MODES = [
    # navn, kost EUR/tkm, utslipp kg CO2/tkm, relativ service-penalitet
    ("truck", 0.11, 0.095, 1.0),   # rask, billig pr tkm, hoy utslipp
    ("rail",  0.12, 0.024, 1.3),   # litt dyrere pr tkm, lav utslipp
    ("ship",  0.13, 0.016, 1.8),   # dyrest pr tkm, laveste utslipp
]

N_CUSTOMERS = 50
N_SCENARIOS = 20  # vi starter med moderat scenariosett; step04 reduserer videre


def haversine(lat1, lon1, lat2, lon2) -> float:
    """Tilnærmet avstand i km mellom to punkt (Haversine)."""
    R = 6371.0
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dp = np.radians(lat2 - lat1)
    dl = np.radians(lon2 - lon1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))


def generate_customers(rng: np.random.Generator) -> pd.DataFrame:
    """Genererer kunder i skandinavisk bounding box."""
    # Skandinavia bounding box (grovt): lat 55-65, lon 5-20
    lats = rng.uniform(55.0, 64.5, size=N_CUSTOMERS)
    lons = rng.uniform(5.0, 19.5, size=N_CUSTOMERS)
    # Etterspørselsparametere: gj.snitt 80-200, std 15-40
    mu = rng.uniform(80, 200, size=N_CUSTOMERS)
    sigma = rng.uniform(15, 40, size=N_CUSTOMERS)
    names = [f"C{i:02d}" for i in range(1, N_CUSTOMERS + 1)]
    return pd.DataFrame(
        {
            "customer": names,
            "lat": np.round(lats, 3),
            "lon": np.round(lons, 3),
            "mu": np.round(mu, 1),
            "sigma": np.round(sigma, 1),
        }
    )


def build_edges(dcs: pd.DataFrame, customers: pd.DataFrame, modes: pd.DataFrame) -> pd.DataFrame:
    """Bygger alle (DC, kunde, modus)-kanter med avstand, kost og utslipp."""
    rows = []
    for _, d in dcs.iterrows():
        for _, c in customers.iterrows():
            dist = haversine(d["lat"], d["lon"], c["lat"], c["lon"])
            for _, m in modes.iterrows():
                # Kost og utslipp skaleres med avstand. Tog og skip har store
                # geografiske begrensninger, modellert via en
                # 'tilgjengelighets-boost': om avstanden er under 150 km,
                # dominerer lastebil naturlig (ingen togtransport for korte
                # distanser). Vi setter likevel alle modi tilgjengelig for
                # enkelhet, men øker rail/ship-kost for veldig korte
                # distanser slik at MIP-en selv velger bort.
                base_cost = m["cost_per_tkm"] * dist
                base_emis = m["emis_per_tkm"] * dist
                # service-penalitet: avstand x relativ faktor (proxy for tid)
                service = dist * m["service_factor"]
                if dist < 150 and m["mode"] in ("rail", "ship"):
                    base_cost *= 2.0  # fast terminalkost gjør korte transport tunge
                rows.append(
                    {
                        "dc": d["dc"],
                        "customer": c["customer"],
                        "mode": m["mode"],
                        "dist_km": round(dist, 1),
                        "cost_per_unit": round(base_cost, 3),
                        "emis_per_unit": round(base_emis, 4),  # kg CO2 pr enhet
                        "service_cost": round(service, 2),
                    }
                )
    return pd.DataFrame(rows)


def generate_scenarios(customers: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    """Genererer N_SCENARIOS etterspørselsrealiseringer per kunde."""
    records = []
    for s in range(N_SCENARIOS):
        for _, c in customers.iterrows():
            demand = max(0, int(round(rng.normal(c["mu"], c["sigma"]))))
            records.append({"scenario": s, "customer": c["customer"], "demand": demand})
    return pd.DataFrame(records)


def plot_network(dcs: pd.DataFrame, customers: pd.DataFrame, output_path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 7))

    # Kunder som små mintpunkter
    ax.scatter(
        customers["lon"],
        customers["lat"],
        s=45,
        c="#97D4B7",
        edgecolors="#307453",
        linewidths=0.8,
        label="Kunde",
        zorder=2,
    )

    # DC-kandidater som store pastellblå punkter
    ax.scatter(
        dcs["lon"],
        dcs["lat"],
        s=350,
        c="#8CC8E5",
        edgecolors="#1F6587",
        linewidths=1.8,
        marker="s",
        label="DC-kandidat",
        zorder=3,
    )
    for _, d in dcs.iterrows():
        ax.annotate(
            d["dc"],
            (d["lon"], d["lat"]),
            xytext=(6, 6),
            textcoords="offset points",
            fontsize=10,
            fontweight="bold",
            color="#1F6587",
        )

    ax.set_xlabel("Lengdegrad", fontsize=11)
    ax.set_ylabel("Breddegrad", fontsize=11)
    ax.set_title(
        "Skandinavisk distribusjonsnett: 6 DC-kandidater og 50 kunder",
        fontsize=12,
        fontweight="bold",
    )
    ax.grid(True, alpha=0.3)
    ax.legend(loc="lower right", fontsize=10, frameon=True)
    ax.set_aspect("auto")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)
    rng = np.random.default_rng(SEED)

    print("=" * 60)
    print("STEG 1: Datainnsamling")
    print("=" * 60)

    dcs = pd.DataFrame(
        DC_CANDIDATES, columns=["dc", "lat", "lon", "capacity", "fixed_cost"]
    )
    modes = pd.DataFrame(
        MODES, columns=["mode", "cost_per_tkm", "emis_per_tkm", "service_factor"]
    )
    customers = generate_customers(rng)
    edges = build_edges(dcs, customers, modes)
    scenarios = generate_scenarios(customers, rng)

    dcs.to_csv(DATA_DIR / "dc_candidates.csv", index=False)
    modes.to_csv(DATA_DIR / "modes.csv", index=False)
    customers.to_csv(DATA_DIR / "customers.csv", index=False)
    edges.to_csv(DATA_DIR / "edges.csv", index=False)
    scenarios.to_csv(DATA_DIR / "scenarios.csv", index=False)

    print(f"\n DC-kandidater: {len(dcs)}")
    print(f" Kunder:        {len(customers)}")
    print(f" Moduser:       {len(modes)}")
    print(f" Kanter:        {len(edges)} (= 6 x 50 x 3)")
    print(f" Scenarioer:    {scenarios['scenario'].nunique()}")
    print(f" Tot. ettersp. (gj.sn. over sc.): {scenarios.groupby('scenario')['demand'].sum().mean():.0f}")

    # Oppsummerende statistikk
    stats = {
        "n_dc": len(dcs),
        "n_customers": len(customers),
        "n_modes": len(modes),
        "n_scenarios": int(scenarios["scenario"].nunique()),
        "mean_demand_per_sc": float(
            scenarios.groupby("scenario")["demand"].sum().mean()
        ),
        "std_demand_per_sc": float(
            scenarios.groupby("scenario")["demand"].sum().std()
        ),
        "avg_dist_km": float(edges["dist_km"].mean()),
    }
    with open(OUTPUT_DIR / "step01_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    plot_network(dcs, customers, OUTPUT_DIR / "gronnsc_network.png")
    print(f"\nStatistikk: {stats}")


if __name__ == "__main__":
    main()
