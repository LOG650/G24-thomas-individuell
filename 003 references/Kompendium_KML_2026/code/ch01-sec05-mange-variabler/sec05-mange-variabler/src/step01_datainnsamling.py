"""
Steg 1: Datainnsamling for LightGBM-analyse
===========================================
Genererer et syntetisk SKU-panel: 50 produkter x 731 dager daglig salg,
med pris, kampanje, vær, produktkategori, merke, butikk og lager. Dette
etterligner et M5/store-item-demand-forecasting-liknende datasett med
rik struktur.

Genererer også tidsserieplot og deskriptiv statistikk.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Konfigurasjon
# -----------------------------------------------------------------------------
START_DATE = "2022-01-03"  # Mandag
N_DAYS = 731               # ca. 2 år
N_SKUS = 50

CATEGORIES = [
    "meieri", "bakevarer", "drikke", "frukt_gronnsaker",
    "kjott", "snacks", "frossen", "husholdning",
]
BRANDS = ["A", "B", "C", "D", "E"]
STORES = ["liten", "middels", "stor"]


def generate_calendar(start: str = START_DATE, n_days: int = N_DAYS) -> pd.DataFrame:
    """Lag kalender med ukedag, måned og helligdagsindikatorer."""
    dates = pd.date_range(start=start, periods=n_days, freq="D")
    cal = pd.DataFrame({
        "dato": dates,
        "t": np.arange(1, n_days + 1),
        "ukedag": dates.dayofweek,
        "uke": dates.isocalendar().week.astype(int).values,
        "maaned": dates.month,
        "aar": dates.year,
        "kvartal": dates.quarter,
        "dag_i_maaned": dates.day,
    })
    cal["helligdag"] = (
        ((cal["maaned"] == 1) & (cal["dag_i_maaned"] == 1))
        | ((cal["maaned"] == 5) & (cal["dag_i_maaned"] == 1))
        | ((cal["maaned"] == 5) & (cal["dag_i_maaned"] == 17))
        | ((cal["maaned"] == 12) & (cal["dag_i_maaned"] == 25))
        | ((cal["maaned"] == 12) & (cal["dag_i_maaned"] == 26))
    ).astype(int)
    # Dager til jul (vektorisert)
    christmas_this = pd.to_datetime(cal["aar"].astype(str) + "-12-24")
    christmas_next = pd.to_datetime((cal["aar"] + 1).astype(str) + "-12-24")
    delta_this = (christmas_this - cal["dato"]).dt.days
    delta_next = (christmas_next - cal["dato"]).dt.days
    cal["dager_til_jul"] = np.where(delta_this >= 0, delta_this, delta_next)
    return cal


def generate_weather(cal: pd.DataFrame, seed: int = 11) -> pd.DataFrame:
    """Syntetisk norsk dagsvær: temperatur, nedbør, solskinn."""
    rng = np.random.default_rng(seed)
    day_of_year = cal["dato"].dt.dayofyear.values
    temp_base = 7.5 + 11.5 * np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
    temp = temp_base + rng.normal(0, 2.5, len(cal))
    rain_rate = 3.0 + 1.5 * np.cos(2 * np.pi * (day_of_year - 80) / 365.25)
    rain = rng.exponential(scale=rain_rate)
    rain = np.where(rng.random(len(cal)) < 0.45, 0.0, rain)
    sun = np.clip(10 - 1.4 * rain + rng.normal(0, 1.5, len(cal)), 0, 14)
    return pd.DataFrame({
        "dato": cal["dato"].values,
        "temperatur": np.round(temp, 1),
        "nedbor": np.round(rain, 1),
        "solskinn": np.round(sun, 1),
    })


def generate_sku_catalog(seed: int = 7) -> pd.DataFrame:
    """Lag katalog med produktattributter for N_SKUS produkter."""
    rng = np.random.default_rng(seed)
    cat_base_price = {
        "meieri": 22, "bakevarer": 35, "drikke": 28,
        "frukt_gronnsaker": 18, "kjott": 120, "snacks": 45,
        "frossen": 55, "husholdning": 65,
    }
    cat_temp_sens = {
        "meieri": -0.3, "bakevarer": -0.1, "drikke": 0.8,
        "frukt_gronnsaker": 0.2, "kjott": -0.2, "snacks": 0.0,
        "frossen": -0.4, "husholdning": 0.0,
    }
    rows = []
    for i in range(N_SKUS):
        cat = CATEGORIES[i % len(CATEGORIES)]
        brand = BRANDS[rng.integers(0, len(BRANDS))]
        store = STORES[rng.integers(0, len(STORES))]
        rows.append({
            "sku_id": f"P{i + 1:03d}",
            "kategori": cat,
            "merke": brand,
            "butikk": store,
            "basispris": round(float(cat_base_price[cat] * rng.uniform(0.85, 1.25)), 2),
            "temp_fol": round(float(cat_temp_sens[cat] + rng.normal(0, 0.15)), 3),
            "priselastisitet": round(float(rng.uniform(-1.8, -0.6)), 2),
            "baseline": round(float(rng.uniform(30, 120)), 2),
            "uke_amp": round(float(rng.uniform(0.10, 0.35)), 3),
        })
    return pd.DataFrame(rows)


def _simulate_inventory(sales: np.ndarray, base: float) -> tuple[np.ndarray, np.ndarray]:
    """Kjør en enkel påfyllssimulering. Returnerer (lager_slutt_dagen, stockout_flag)."""
    n = len(sales)
    refill_interval = 7
    refill_amount = int(max(base * 7.5, 60))
    stock = refill_amount
    inv = np.zeros(n, dtype=np.int32)
    stockout = np.zeros(n, dtype=np.int32)
    for i in range(n):
        if i % refill_interval == 0 and i > 0:
            stock = stock + refill_amount
        if stock < sales[i]:
            sales[i] = stock
            stockout[i] = 1
        stock = max(stock - sales[i], 0)
        inv[i] = stock
    return inv, stockout


def generate_sales_panel(seed: int = 42) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Generer SKU-panel vektorisert og bygg paneldata i kolonner.

    Returns
    -------
    panel, sku_catalog, weather
    """
    rng = np.random.default_rng(seed)
    cal = generate_calendar()
    weather = generate_weather(cal)
    sku = generate_sku_catalog()

    n_days = len(cal)
    n_skus = len(sku)

    # Globale tidsvariabler (1D over dager)
    dow = cal["ukedag"].values
    day_of_year = cal["dato"].dt.dayofyear.values
    month = cal["maaned"].values
    day_of_month = cal["dag_i_maaned"].values
    holiday = cal["helligdag"].values
    days_to_christmas = cal["dager_til_jul"].values
    temp = weather["temperatur"].values
    weekly_shape = np.array([-0.6, -0.4, -0.2, 0.0, 0.6, 1.0, -0.8])
    weekly = weekly_shape[dow]
    trend = 0.0003 * np.arange(n_days)

    # Kategori-sesongmatrise: rad per kategori, kolonne per dag
    cat_season_map = {}
    for cat in CATEGORIES:
        cs = np.zeros(n_days)
        if cat == "drikke":
            cs = 0.25 * np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
        elif cat == "snacks":
            cs = 0.15 * np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
            cs = np.where(month == 12, cs + 0.35, cs)
        elif cat == "meieri":
            cs = np.where(month == 12, 0.22, 0.0)
        elif cat == "frossen":
            cs = -0.15 * np.sin(2 * np.pi * (day_of_year - 80) / 365.25)
        elif cat == "bakevarer":
            cs = np.where((month == 12) & (day_of_month > 10), 0.45, 0.0)
        cat_season_map[cat] = cs

    holiday_effect_base = np.where(holiday == 1, -0.25, 0.0)
    near_christmas = ((days_to_christmas >= 0) & (days_to_christmas <= 3)).astype(float)
    holiday_effect_all = holiday_effect_base + 0.35 * near_christmas

    # Vektoriser per-SKU-generering: bygg 1D-arrays per SKU og stack
    arrays_dato = []
    arrays_t = []
    arrays_sku = []
    arrays_cat = []
    arrays_brand = []
    arrays_store = []
    arrays_pris = []
    arrays_basispris = []
    arrays_rabatt = []
    arrays_kampanje = []
    arrays_lager = []
    arrays_stockout = []
    arrays_salg = []

    dates_vals = cal["dato"].values
    t_vals = cal["t"].values

    for _, row in sku.iterrows():
        base = row["baseline"]
        cat = row["kategori"]
        uke_amp = row["uke_amp"]
        temp_fol = row["temp_fol"]
        price_elastic = row["priselastisitet"]
        base_price = row["basispris"]

        campaign_prob = rng.uniform(0.10, 0.18)
        is_campaign = (rng.random(n_days) < campaign_prob).astype(np.int8)
        discount_pct = np.where(is_campaign == 1,
                                rng.integers(10, 36, size=n_days),
                                0).astype(np.int8)
        daily_price = base_price * (1 - discount_pct / 100.0)

        cat_season = cat_season_map[cat]
        temp_effect = temp_fol * (temp - 7.5) / 10.0
        rel_price_change = (daily_price - base_price) / base_price
        price_effect = price_elastic * rel_price_change
        campaign_bonus = 0.15 * is_campaign

        # Pre/post-flag vektorisert
        # pre: campaign on at t+1 and off at t
        is_c = is_campaign.astype(int)
        shifted_left = np.concatenate([is_c[1:], [0]])
        pre_flag = ((is_c == 0) & (shifted_left == 1)).astype(int)
        # post: campaign off at t and was on at t-1 (up to 2 days)
        shifted_right = np.concatenate([[0], is_c[:-1]])
        shifted_right2 = np.concatenate([[0, 0], is_c[:-2]])
        post_flag = (((is_c == 0) & (shifted_right == 1))
                     | ((is_c == 0) & (shifted_right2 == 1) & (shifted_right == 0))).astype(int)

        interaction = np.zeros(n_days)
        if cat == "drikke":
            high_temp = (temp > 22).astype(float)
            interaction = 0.25 * high_temp * is_campaign

        phi = 0.25
        eps = rng.normal(0, 0.08, n_days)
        noise = np.zeros(n_days)
        # AR(1)-loop (rask for 731 elementer)
        prev = 0.0
        for i in range(n_days):
            prev = phi * prev + eps[i]
            noise[i] = prev

        log_mean = (
            np.log(base)
            + trend
            + uke_amp * weekly
            + cat_season
            + temp_effect
            + price_effect
            + campaign_bonus
            + interaction
            + holiday_effect_all
            + noise
            - 0.08 * pre_flag
            - 0.06 * post_flag
        )
        mean = np.exp(log_mean)
        sales = rng.poisson(np.maximum(mean, 0.1)).astype(np.int32)

        inv, stockout = _simulate_inventory(sales, base)

        arrays_dato.append(dates_vals)
        arrays_t.append(t_vals)
        arrays_sku.append(np.full(n_days, row["sku_id"]))
        arrays_cat.append(np.full(n_days, cat))
        arrays_brand.append(np.full(n_days, row["merke"]))
        arrays_store.append(np.full(n_days, row["butikk"]))
        arrays_pris.append(np.round(daily_price, 2))
        arrays_basispris.append(np.full(n_days, base_price))
        arrays_rabatt.append(discount_pct.astype(np.int32))
        arrays_kampanje.append(is_campaign.astype(np.int32))
        arrays_lager.append(inv)
        arrays_stockout.append(stockout)
        arrays_salg.append(sales)

    panel = pd.DataFrame({
        "dato": np.concatenate(arrays_dato),
        "t": np.concatenate(arrays_t),
        "sku_id": np.concatenate(arrays_sku),
        "kategori": np.concatenate(arrays_cat),
        "merke": np.concatenate(arrays_brand),
        "butikk": np.concatenate(arrays_store),
        "pris": np.concatenate(arrays_pris),
        "basispris": np.concatenate(arrays_basispris),
        "rabatt_pct": np.concatenate(arrays_rabatt),
        "kampanje": np.concatenate(arrays_kampanje),
        "lager": np.concatenate(arrays_lager),
        "stockout": np.concatenate(arrays_stockout),
        "salg": np.concatenate(arrays_salg),
    })
    panel["dato"] = pd.to_datetime(panel["dato"])
    return panel, sku, weather


def calculate_statistics(panel: pd.DataFrame) -> dict:
    """Beregn deskriptiv statistikk for panelet."""
    return {
        "total_rader": int(len(panel)),
        "antall_skuer": int(panel["sku_id"].nunique()),
        "antall_dager": int(panel["dato"].nunique()),
        "antall_kategorier": int(panel["kategori"].nunique()),
        "antall_merker": int(panel["merke"].nunique()),
        "antall_butikker": int(panel["butikk"].nunique()),
        "gj_salg_per_sku_dag": round(float(panel["salg"].mean()), 2),
        "std_salg": round(float(panel["salg"].std()), 2),
        "maks_salg": int(panel["salg"].max()),
        "min_salg": int(panel["salg"].min()),
        "kampanjeandel_pct": round(100 * float(panel["kampanje"].mean()), 1),
        "stockout_andel_pct": round(100 * float(panel["stockout"].mean()), 2),
        "gj_pris": round(float(panel["pris"].mean()), 2),
        "kategori_gj_salg": {
            k: round(float(v), 2)
            for k, v in panel.groupby("kategori")["salg"].mean().items()
        },
    }


def plot_panel_overview(panel: pd.DataFrame, output_path: Path) -> None:
    """Plott: 4 utvalgte SKU-er over tid og total-panelet."""
    sample_skus = ["P001", "P003", "P015", "P032"]
    fig, axes = plt.subplots(2, 1, figsize=(12, 6.8), sharex=True,
                             gridspec_kw={"height_ratios": [2, 1]})
    colors = ["#1F6587", "#307453", "#5A2C77", "#9C540B"]
    for sid, col in zip(sample_skus, colors):
        sub = panel[panel["sku_id"] == sid].sort_values("t")
        axes[0].plot(sub["t"].values, sub["salg"].values, color=col,
                     linewidth=0.8, alpha=0.85, label=f"{sid} ({sub['kategori'].iloc[0]})")
    axes[0].set_ylabel("Daglig salg", fontsize=11)
    axes[0].legend(loc="upper left", fontsize=9, ncol=4)
    axes[0].grid(True, alpha=0.3)
    axes[0].set_title("Daglig salg for fire utvalgte produkter (SKU-er)",
                      fontsize=12, fontweight="bold")

    total = panel.groupby("t")["salg"].sum().reset_index()
    axes[1].plot(total["t"].values, total["salg"].values,
                 color="#1F6587", linewidth=0.9)
    axes[1].fill_between(total["t"].values, 0, total["salg"].values,
                         color="#8CC8E5", alpha=0.35)
    axes[1].set_xlabel("$t$ (dag)", fontsize=12)
    axes[1].set_ylabel("Totalt salg", fontsize=11)
    axes[1].grid(True, alpha=0.3)
    axes[1].set_title("Aggregert salg over alle 50 SKU-er",
                      fontsize=11, fontweight="bold")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_category_profile(panel: pd.DataFrame, output_path: Path) -> None:
    """Plott gjennomsnittlig daglig salg per kategori + ukesesongprofil."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))

    cat_means = panel.groupby("kategori")["salg"].mean().sort_values()
    palette = [
        "#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7",
        "#ED9F9E", "#1F6587", "#307453", "#9C540B",
    ]
    axes[0].barh(cat_means.index, cat_means.values,
                 color=palette[:len(cat_means)], edgecolor="#1F2933")
    axes[0].set_xlabel("Gjennomsnittlig daglig salg", fontsize=11)
    axes[0].set_title("Salg per kategori", fontsize=11, fontweight="bold")
    axes[0].grid(True, axis="x", alpha=0.3)

    dow_labels = ["Man", "Tir", "Ons", "Tor", "Fre", "Lør", "Søn"]
    panel_ = panel.copy()
    panel_["ukedag"] = panel_["dato"].dt.dayofweek
    week_profile = panel_.groupby("ukedag")["salg"].mean()
    axes[1].bar(dow_labels, week_profile.values,
                color="#8CC8E5", edgecolor="#1F6587")
    axes[1].set_ylabel("Gjennomsnittlig daglig salg", fontsize=11)
    axes[1].set_title("Ukesesongprofil (alle SKU-er)", fontsize=11, fontweight="bold")
    axes[1].grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    data_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 1: DATAINNSAMLING")
    print(f"{'=' * 60}")

    panel, sku, weather = generate_sales_panel()
    stats = calculate_statistics(panel)

    print(f"\nDatasett-dimensjoner:")
    print(f"  Rader (sku-dag):         {stats['total_rader']:,}")
    print(f"  Antall SKU-er:           {stats['antall_skuer']}")
    print(f"  Antall dager:            {stats['antall_dager']}")
    print(f"  Antall kategorier:       {stats['antall_kategorier']}")
    print(f"  Kampanjeandel:           {stats['kampanjeandel_pct']} %")
    print(f"  Gjennomsnittlig salg:    {stats['gj_salg_per_sku_dag']}")
    print(f"  Standardavvik:           {stats['std_salg']}")
    print(f"  Maks daglig salg:        {stats['maks_salg']}")

    panel_path = data_dir / "sales_panel.csv"
    panel.to_csv(panel_path, index=False, encoding="utf-8")
    print(f"\nPanel lagret: {panel_path}")

    sku.to_csv(data_dir / "sku_catalog.csv", index=False, encoding="utf-8")
    weather.to_csv(data_dir / "weather.csv", index=False, encoding="utf-8")

    with open(output_dir / "descriptive_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Statistikk lagret: {output_dir / 'descriptive_stats.json'}")

    plot_panel_overview(panel, output_dir / "lgbm_data_plot.png")
    plot_category_profile(panel, output_dir / "lgbm_category_profile.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  Datasettet har {stats['antall_skuer']} SKU-er x "
          f"{stats['antall_dager']} dager = {stats['total_rader']:,} rader.")
    print(f"  Rik struktur: {stats['antall_kategorier']} kategorier, "
          f"{stats['antall_merker']} merker, {stats['antall_butikker']} butikktyper, "
          f"pris, kampanje, vær, lager og stockout.")


if __name__ == "__main__":
    main()
