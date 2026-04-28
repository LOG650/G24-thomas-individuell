"""
Steg 1: Datainnsamling for Weibull-returanalyse
================================================
Genererer syntetisk salgs- og returdatasett for en norsk elektronikk-forhandler
(forbrukerelektronikk, f.eks. en ruter/modell-serie) over 48 månader (4 år).

Hvert solgt produkt får trukket en levetid fra en Weibull(beta, eta)-fordeling.
Produkter med levetid innenfor garantiperioden (24 mnd) gir en retur i
måneden salgstidspunkt + levetid. Produkter med levetid utover garantien
antas ikke å returneres (censurert).

Skriver tre CSV-filer til data/:
  - sales.csv             : månedlig salg S_s for s = 1..48
  - returns_units.csv     : logg av alle enhetsretur (salgsmåned, levetid, returmåned)
  - returns_monthly.csv   : aggregert antall returer R_t per måned t
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
FIG_DIR = OUTPUT_DIR  # figurer lagres i output/ og kopieres til LaTeX senere

# ---------------------------------------------------------------------------
# Parametre
# ---------------------------------------------------------------------------
N_MONTHS = 48               # 4 år salgshistorikk
START_DATE = "2021-01-01"    # Januar 2021

# Weibull levetidsfordeling (sanne verdier) --------------------------------
# beta (form) > 1 gir økende hazard: barnedødelighet er lav, problem oppstaar
# etter noe tid. Typisk for elektronikk der komponenter slites.
TRUE_BETA = 2.2
TRUE_ETA = 18.0   # måneder; karakteristisk levetid (63.2-prosentil)

# Garantivindu (returer utenfor ignoreres) ----------------------------------
WARRANTY_MONTHS = 24

# Salgsprofil: trend + sesong (produktet lanseres, tar av, flater ut) -------
BASE_LEVEL = 900
TREND = 15.0           # enheter per måned
SEASON_AMP = 180.0     # sesongamplitude
NOISE_SD = 60.0


def generate_sales(seed: int = 2026) -> pd.DataFrame:
    """Syntetisk månedlig salg over N_MONTHS måneder."""
    rng = np.random.default_rng(seed)
    t = np.arange(1, N_MONTHS + 1)
    dates = pd.date_range(START_DATE, periods=N_MONTHS, freq="MS")
    month = dates.month.values

    # Trend + demping (lanseringseffekt) + sesong + støy
    ramp = np.minimum(t / 10.0, 1.0)
    trend = BASE_LEVEL + TREND * t
    season = SEASON_AMP * np.sin(2 * np.pi * (month - 4) / 12.0)
    noise = rng.normal(0.0, NOISE_SD, N_MONTHS)
    sales = np.round(ramp * (trend + season) + noise).astype(int)
    sales = np.maximum(sales, 0)

    return pd.DataFrame({
        "t": t,
        "dato": dates,
        "salg": sales,
    })


def generate_returns(sales: pd.DataFrame, seed: int = 7) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Generer levetider per solgt enhet, beregn retur innenfor garantivindu."""
    rng = np.random.default_rng(seed)

    unit_records = []
    for _, row in sales.iterrows():
        s = int(row["t"])
        n = int(row["salg"])
        if n == 0:
            continue
        # Weibull-levetider (scipy: shape=beta, scale=eta)
        lifetimes = rng.weibull(TRUE_BETA, size=n) * TRUE_ETA
        # Kun enheter som feiler innen garantiperioden registreres som retur
        returned = lifetimes <= WARRANTY_MONTHS
        for lt, ret in zip(lifetimes, returned):
            unit_records.append({
                "salgsmaaned": s,
                "levetid": float(lt),
                "returnert": bool(ret),
                "returmaaned": int(np.ceil(s + lt)) if ret else np.nan,
            })

    units = pd.DataFrame(unit_records)

    # Vi observerer kun returer opp til siste måned i datasettet (N_MONTHS)
    observed = units["returnert"] & (units["returmaaned"] <= N_MONTHS)
    monthly = (
        units.loc[observed]
        .groupby("returmaaned")
        .size()
        .reindex(range(1, N_MONTHS + 1), fill_value=0)
        .rename("returer")
        .reset_index()
        .rename(columns={"returmaaned": "t"})
    )
    # La ogsaa returmaaned staar for de som faktisk er registrert (levetid <= 24 og
    # returmaaned <= N_MONTHS). For andre sette nan tilbake i units:
    units.loc[~observed, "returmaaned"] = np.nan
    units.loc[~observed, "returnert"] = False

    return units, monthly


def plot_sales(sales: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(sales["t"], sales["salg"], color="#8CC8E5", edgecolor="#1F6587", linewidth=0.6)
    ax.set_xlabel("$s$ (salgsmåned)", fontsize=14)
    ax.set_ylabel("$S_s$", fontsize=14, rotation=0, labelpad=20)
    ax.set_title("Månedlig salg av elektronikkmodellen", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def plot_returns(monthly: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.bar(monthly["t"], monthly["returer"], color="#ED9F9E", edgecolor="#961D1C", linewidth=0.6)
    ax.set_xlabel("$t$ (returmåned)", fontsize=14)
    ax.set_ylabel("$R_t$", fontsize=14, rotation=0, labelpad=20)
    ax.set_title("Månedlig antall observerte returer", fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.tick_params(axis="both", labelsize=10)
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {path}")


def main() -> None:
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    sales = generate_sales()
    units, monthly = generate_returns(sales)

    sales.to_csv(DATA_DIR / "sales.csv", index=False)
    units.to_csv(DATA_DIR / "returns_units.csv", index=False)
    monthly.to_csv(DATA_DIR / "returns_monthly.csv", index=False)
    print(f"Data lagret til {DATA_DIR}")

    # Figurer
    plot_sales(sales, FIG_DIR / "weib_sales.png")
    plot_returns(monthly, FIG_DIR / "weib_returns_monthly.png")

    # Summary JSON
    total_sold = int(sales["salg"].sum())
    total_returned = int(monthly["returer"].sum())
    observed_mask = units["returnert"].astype(bool)
    n_observed_units = int(observed_mask.sum())
    total_units = len(units)
    avg_lifetime_obs = float(units.loc[observed_mask, "levetid"].mean()) if n_observed_units else 0.0

    results = {
        "n_months": int(N_MONTHS),
        "start_date": START_DATE,
        "warranty_months": int(WARRANTY_MONTHS),
        "true_beta": float(TRUE_BETA),
        "true_eta": float(TRUE_ETA),
        "total_sold": total_sold,
        "total_units_tracked": total_units,
        "total_returned_observed": total_returned,
        "return_rate_pct": round(100.0 * total_returned / max(total_sold, 1), 2),
        "avg_lifetime_observed_months": round(avg_lifetime_obs, 3),
        "sales_min": int(sales["salg"].min()),
        "sales_max": int(sales["salg"].max()),
        "sales_mean": round(float(sales["salg"].mean()), 1),
        "sales_std": round(float(sales["salg"].std(ddof=1)), 1),
    }
    with open(OUTPUT_DIR / "step01_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print()
    print("KONKLUSJON")
    print("-" * 60)
    print(f"Solgte enheter totalt (4 år):  {total_sold:,}")
    print(f"Observerte returer:            {total_returned:,}  ({results['return_rate_pct']} %)")
    print(f"Gjennomsnittlig observert levetid: {avg_lifetime_obs:.2f} mnd")
    print(f"Salg per måned: min={results['sales_min']}, max={results['sales_max']},"
          f" snitt={results['sales_mean']}, std={results['sales_std']}")


if __name__ == "__main__":
    main()
