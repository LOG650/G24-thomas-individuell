"""
Steg 1: Datainnsamling for ARIMAX-analyse
=========================================
Genererer (syntetisk) daglig salgsdata for en dagligvarekategori over
ca. 2 år (730 dager) med tydelig ukesesong, svak lineær trend og
15 kampanjer av ulik varighet og rabattnivå.

Genererer også tidsserieplott, rådata-tabell og deskriptiv statistikk.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ----------------------------------------------------------------------------
# Syntetiske data: daglig salg av kategori "kaffe" i en norsk dagligvarekjede
# ----------------------------------------------------------------------------
# 730 dager, starter mandag 2022-01-03.
# Baseline = trend + ukesesong + normalstøy.
# 15 kampanjeperioder (rabatt 10-30 %) gir kraftig løft under kampanjen og
# mildere "dip" dagene rett før og rett etter.

START_DATE = "2022-01-03"  # Mandag
N_DAYS = 730


def generate_raw_data(seed: int = 42) -> pd.DataFrame:
    """Generer daglig salgsdata med kampanjer.

    Returns
    -------
    pd.DataFrame
        Kolonner: dato, t, salg, kampanje (0/1), rabatt (%), kampanje_id.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(1, N_DAYS + 1)
    dates = pd.date_range(start=START_DATE, periods=N_DAYS, freq="D")
    dow = dates.dayofweek.values  # 0=Mandag, 6=Søndag

    # Baseline-komponenter
    baseline_level = 160.0
    trend = 0.12 * t  # oppadgående trend (~88 enheter over 2 år)
    # Ukesesong: høyest fredag/lørdag, lavest søndag/mandag
    weekly_effect = np.array([-15.0, -10.0, -5.0, 0.0, 20.0, 35.0, -25.0])
    season = weekly_effect[dow]

    # AR(1)-støy for realistisk autokorrelasjon
    phi = 0.35
    noise = np.zeros(N_DAYS)
    eps = rng.normal(0, 8.0, N_DAYS)
    for i in range(1, N_DAYS):
        noise[i] = phi * noise[i - 1] + eps[i]

    baseline = baseline_level + trend + season + noise

    # ----------------------------------------------------------
    # Kampanjer: 15 perioder
    # ----------------------------------------------------------
    campaigns = [
        # (start_t, lengde, rabatt_pct)
        (35, 4, 20),
        (80, 3, 15),
        (120, 5, 25),
        (165, 3, 10),
        (210, 4, 20),
        (255, 3, 30),
        (305, 4, 15),
        (355, 5, 25),
        (400, 3, 20),
        (450, 4, 15),
        (500, 3, 30),
        (545, 5, 20),
        (595, 3, 10),
        (640, 4, 25),
        (690, 3, 20),
    ]

    campaign_flag = np.zeros(N_DAYS, dtype=int)
    discount = np.zeros(N_DAYS)
    campaign_id = np.zeros(N_DAYS, dtype=int)

    for cid, (start_t, length, disc_pct) in enumerate(campaigns, start=1):
        for k in range(length):
            idx = start_t - 1 + k
            if idx < N_DAYS:
                campaign_flag[idx] = 1
                discount[idx] = disc_pct
                campaign_id[idx] = cid

    # Kampanjeeffekt på salg: grunnløft 60 enheter + 4 enheter per % rabatt
    base_lift = 60.0
    elasticity = 4.0  # enheter salg per % rabatt
    lift = campaign_flag * (base_lift + elasticity * discount)

    # Pre-buying "dip": 2 dager før kampanjestart (-10 %)
    # Post-campaign "dip": 3 dager etter kampanjeslutt (-8 %)
    pre_dip = np.zeros(N_DAYS)
    post_dip = np.zeros(N_DAYS)
    for (start_t, length, _) in campaigns:
        start_idx = start_t - 1
        end_idx = start_idx + length - 1
        for k in range(1, 3):
            j = start_idx - k
            if 0 <= j < N_DAYS and campaign_flag[j] == 0:
                pre_dip[j] -= 0.10 * baseline[j]
        for k in range(1, 4):
            j = end_idx + k
            if 0 <= j < N_DAYS and campaign_flag[j] == 0:
                post_dip[j] -= 0.08 * baseline[j]

    sales = baseline + lift + pre_dip + post_dip
    sales = np.maximum(sales, 10).round().astype(int)

    df = pd.DataFrame(
        {
            "dato": dates,
            "t": t,
            "salg": sales,
            "kampanje": campaign_flag,
            "rabatt": discount,
            "kampanje_id": campaign_id,
            "ukedag": dow,
        }
    )
    return df


def create_time_series(df: pd.DataFrame | None = None) -> pd.Series:
    """Returner salgsserien som pd.Series med datoindeks."""
    if df is None:
        df = generate_raw_data()
    return pd.Series(df["salg"].values, index=df["dato"], name="Salg")


def calculate_statistics(df: pd.DataFrame) -> dict:
    """Beregn deskriptiv statistikk både totalt og per regime."""
    sales = df["salg"]
    campaign_mask = df["kampanje"] == 1
    baseline_sales = sales[~campaign_mask]
    campaign_sales = sales[campaign_mask]

    stats = {
        "total": {
            "antall": int(sales.count()),
            "gjennomsnitt": round(sales.mean(), 1),
            "standardavvik": round(sales.std(), 1),
            "minimum": int(sales.min()),
            "kvartil_25": round(sales.quantile(0.25), 1),
            "median": round(sales.median(), 1),
            "kvartil_75": round(sales.quantile(0.75), 1),
            "maksimum": int(sales.max()),
        },
        "baseline": {
            "antall": int(baseline_sales.count()),
            "gjennomsnitt": round(baseline_sales.mean(), 1),
            "standardavvik": round(baseline_sales.std(), 1),
        },
        "kampanje": {
            "antall": int(campaign_sales.count()),
            "gjennomsnitt": round(campaign_sales.mean(), 1),
            "standardavvik": round(campaign_sales.std(), 1),
            "antall_kampanjer": int(df["kampanje_id"].max()),
        },
    }
    stats["raa_kampanjeloeft_prosent"] = round(
        (campaign_sales.mean() / baseline_sales.mean() - 1) * 100, 1
    )
    return stats


def plot_time_series(df: pd.DataFrame, output_path: Path) -> None:
    """Plott daglig salg med kampanjeperioder markert."""
    fig, ax = plt.subplots(figsize=(12, 5))

    t = df["t"].values
    sales = df["salg"].values

    ax.plot(t, sales, color="#1F6587", linewidth=0.9, label="Daglig salg $Y_t$")

    # Skygg kampanjeperioder
    campaign_flag = df["kampanje"].values
    in_campaign = False
    start = None
    first_span = True
    for i in range(len(t)):
        if campaign_flag[i] == 1 and not in_campaign:
            in_campaign = True
            start = t[i] - 0.5
        elif campaign_flag[i] == 0 and in_campaign:
            in_campaign = False
            label = "Kampanjeperiode" if first_span else None
            ax.axvspan(start, t[i - 1] + 0.5, color="#F6BA7C", alpha=0.45, label=label)
            first_span = False
    if in_campaign:
        ax.axvspan(start, t[-1] + 0.5, color="#F6BA7C", alpha=0.45)

    # Trendlinje
    z = np.polyfit(t, sales, 1)
    trend = np.poly1d(z)
    ax.plot(t, trend(t), "--", color="#961D1C", linewidth=1.2, alpha=0.8,
            label="Lineær trend")

    ax.set_xlabel("$t$ (dag)", fontsize=14)
    ax.set_ylabel("$Y_t$", fontsize=14, rotation=0, labelpad=18)
    ax.set_xlim(1, N_DAYS)
    ax.set_xticks([1, 100, 200, 300, 400, 500, 600, 730])
    ax.tick_params(axis="both", labelsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_title("Daglig salg med kampanjeperioder (2022-2023)",
                 fontsize=12, fontweight="bold", pad=8)
    ax.legend(loc="upper left", fontsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_week_profile(df: pd.DataFrame, output_path: Path) -> None:
    """Plott gjennomsnittlig salg per ukedag (baseline-dager vs kampanjedager)."""
    fig, ax = plt.subplots(figsize=(9, 4.5))

    dow_names = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
    baseline = df[df["kampanje"] == 0].groupby("ukedag")["salg"].mean()
    campaign = df[df["kampanje"] == 1].groupby("ukedag")["salg"].mean()

    x = np.arange(7)
    w = 0.38
    ax.bar(x - w / 2, baseline.reindex(range(7)).values, width=w,
           label="Baseline-dager", color="#8CC8E5", edgecolor="#1F6587")
    ax.bar(x + w / 2, campaign.reindex(range(7)).values, width=w,
           label="Kampanjedager", color="#F6BA7C", edgecolor="#9C540B")

    ax.set_xticks(x)
    ax.set_xticklabels(dow_names, fontsize=11)
    ax.set_ylabel("Gjennomsnittlig salg", fontsize=11)
    ax.set_title("Ukesesongprofil: baseline vs. kampanje",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 1: DATAINNSAMLING")
    print(f"{'=' * 60}")

    df = generate_raw_data()
    print(f"\nAntall dager: {len(df)}")
    print(f"Periode: {df['dato'].iloc[0].date()} -- {df['dato'].iloc[-1].date()}")
    print(f"Antall kampanjer: {int(df['kampanje_id'].max())}")
    print(f"Kampanjedager:    {int(df['kampanje'].sum())}")

    # Lagre rådata
    csv_path = output_dir / "sales_data.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8")
    print(f"\nRådata lagret: {csv_path}")

    # Statistikk
    stats = calculate_statistics(df)
    print("\n--- Deskriptiv statistikk ---")
    for group, d in stats.items():
        print(f"  {group}: {d}")
    with open(output_dir / "descriptive_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

    # Figurer
    plot_time_series(df, output_dir / "arimax_data_plot.png")
    plot_week_profile(df, output_dir / "arimax_week_profile.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(
        f"  Datasettet har tydelig ukesesong og {int(df['kampanje_id'].max())} "
        "kampanjer som skaper synlige salgstopper. "
        f"\n  Rå kampanjeløft (ukorrigert): "
        f"+{stats['raa_kampanjeloeft_prosent']}% under kampanjedager."
    )


if __name__ == "__main__":
    main()
