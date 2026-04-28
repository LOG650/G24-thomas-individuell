"""
Steg 6: Prognose og scenarioanalyse
===================================
Bruker den tilpassede ARIMAX-modellen til å:

  1. Lage baseline-prognose (X_kampanje = 0) for de neste 14 dagene
  2. Lage kampanjeprognose for en planlagt 5-dagers kampanje med 20 % rabatt
  3. Beregne kampanjeløft: (kampanje - baseline) / baseline
  4. Scenarioanalyse: rabatt = 10, 15, 20, 25, 30 %
  5. Plott baseline vs. kampanjeprognose med 95 % konfidensintervall
"""

import json
import pickle
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from step01_datainnsamling import generate_raw_data
from step02_feature_engineering import EXOG_COLS, build_features
from step04_modell_estimering import ORDER, SEASONAL_ORDER

warnings.filterwarnings("ignore")

HORIZON = 14                  # totalt antall dager i prognosen
CAMPAIGN_START_OFFSET = 5     # kampanjen starter dag 5 i horisonten
CAMPAIGN_LENGTH = 5           # 5 dager lang kampanje
BASE_DISCOUNT = 20            # 20 % rabatt i hovedscenarioet


def load_arimax(output_dir: Path) -> dict:
    with open(output_dir / "arimax_model.pkl", "rb") as f:
        return pickle.load(f)


def build_future_exog(
    horizon: int = HORIZON,
    campaign_start: int = CAMPAIGN_START_OFFSET,
    campaign_length: int = CAMPAIGN_LENGTH,
    discount: float = BASE_DISCOUNT,
    include_campaign: bool = True,
) -> pd.DataFrame:
    """Bygg en exog-matrise for prognosehorisonten."""
    data = np.zeros((horizon, len(EXOG_COLS)))
    col_idx = {c: i for i, c in enumerate(EXOG_COLS)}

    if include_campaign:
        c_end = campaign_start + campaign_length - 1
        for k in range(campaign_start, c_end + 1):
            if 0 <= k < horizon:
                data[k, col_idx["x_kampanje"]] = 1
                data[k, col_idx["x_rabatt"]] = discount
        # Pre-buying og post-campaign
        if campaign_start - 1 >= 0:
            data[campaign_start - 1, col_idx["x_foer_1"]] = 1
        if campaign_start - 2 >= 0:
            data[campaign_start - 2, col_idx["x_foer_2"]] = 1
        if c_end + 1 < horizon:
            data[c_end + 1, col_idx["x_etter_1"]] = 1
        if c_end + 2 < horizon:
            data[c_end + 2, col_idx["x_etter_2"]] = 1
        if c_end + 3 < horizon:
            data[c_end + 3, col_idx["x_etter_3"]] = 1
    return pd.DataFrame(data, columns=EXOG_COLS)


def forecast_with_exog(res, exog_future: pd.DataFrame) -> dict:
    """Kjør prognose gitt en exog-matrise."""
    fc = res.get_forecast(steps=len(exog_future), exog=exog_future.values)
    mean = np.asarray(fc.predicted_mean)
    ci = fc.conf_int(alpha=0.05)
    if hasattr(ci, "iloc"):
        lower = ci.iloc[:, 0].values
        upper = ci.iloc[:, 1].values
    else:
        lower = np.asarray(ci)[:, 0]
        upper = np.asarray(ci)[:, 1]
    return {
        "mean": mean,
        "lower": np.asarray(lower),
        "upper": np.asarray(upper),
    }


def run_scenario_analysis(res, discounts=(0, 10, 15, 20, 25, 30)) -> list[dict]:
    """Kjør prognose for flere rabattnivåer og samle totale salgstall."""
    scenarios = []
    baseline = forecast_with_exog(
        res, build_future_exog(include_campaign=False)
    )
    baseline_total = float(np.sum(baseline["mean"]))
    # Totalt baseline-volum over hele 14-dagershorisonten
    # (vi sammenligner mot dette for å få netto kampanjeløft).

    for d in discounts:
        if d == 0:
            fc = baseline
        else:
            fc = forecast_with_exog(
                res,
                build_future_exog(discount=d, include_campaign=True),
            )
        total = float(np.sum(fc["mean"]))
        # Kampanjeløft over hele horisonten (inkl. pre/post-effekter)
        lift_pct = (total / baseline_total - 1) * 100
        # Kampanjeløft bare for selve kampanjedagene
        start = CAMPAIGN_START_OFFSET
        end = start + CAMPAIGN_LENGTH
        camp_sum = float(np.sum(fc["mean"][start:end]))
        base_camp_sum = float(np.sum(baseline["mean"][start:end]))
        camp_lift_pct = (camp_sum / base_camp_sum - 1) * 100
        scenarios.append(
            {
                "rabatt_pct": d,
                "total_14d": round(total, 1),
                "total_loeft_pct": round(lift_pct, 1),
                "kampanjedager_sum": round(camp_sum, 1),
                "kampanjedager_baseline": round(base_camp_sum, 1),
                "kampanje_loeft_pct": round(camp_lift_pct, 1),
                "ekstra_enheter": round(camp_sum - base_camp_sum, 1),
            }
        )
    return scenarios


def plot_baseline_vs_campaign(
    hist_t: np.ndarray,
    hist_y: np.ndarray,
    fc_baseline: dict,
    fc_campaign: dict,
    output_path: Path,
    campaign_start: int = CAMPAIGN_START_OFFSET,
    campaign_length: int = CAMPAIGN_LENGTH,
) -> None:
    """Plott siste 30 dager historikk + 14 dagers prognose i to varianter."""
    fig, ax = plt.subplots(figsize=(11, 5.3))

    n_hist = len(hist_t)
    ax.plot(hist_t, hist_y, "o-", color="#1F6587", linewidth=1.2, markersize=3.5,
            label="Historikk")

    fc_t = np.arange(hist_t[-1] + 1, hist_t[-1] + 1 + len(fc_baseline["mean"]))

    # Baseline (ingen kampanje)
    ax.plot(fc_t, fc_baseline["mean"], "--", color="#307453", linewidth=1.6,
            marker="o", markersize=4, label="Baseline-prognose $\\hat Y_t^{(0)}$")
    ax.fill_between(fc_t, fc_baseline["lower"], fc_baseline["upper"],
                    color="#97D4B7", alpha=0.35)

    # Kampanjeprognose
    ax.plot(fc_t, fc_campaign["mean"], "-", color="#9C540B", linewidth=1.8,
            marker="s", markersize=4.5, label="Med kampanje $\\hat Y_t^{(X)}$")
    ax.fill_between(fc_t, fc_campaign["lower"], fc_campaign["upper"],
                    color="#F6BA7C", alpha=0.30)

    # Marker kampanjedager
    c_start_t = fc_t[campaign_start]
    c_end_t = fc_t[campaign_start + campaign_length - 1]
    ax.axvspan(c_start_t - 0.5, c_end_t + 0.5, color="#F6BA7C", alpha=0.20,
               label="Kampanje (rabatt 20 %)")

    # Skillelinje mellom historikk og prognose
    ax.axvline(hist_t[-1] + 0.5, color="#556270", linestyle=":", linewidth=1.2)

    ax.set_xlabel("$t$ (dag)", fontsize=12)
    ax.set_ylabel("$Y_t$", fontsize=13, rotation=0, labelpad=15)
    ax.set_title("ARIMAX-prognose: baseline vs. kampanje (5 dager, 20 % rabatt)",
                 fontsize=12, fontweight="bold")
    ax.legend(loc="upper left", fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_scenarios(scenarios: list[dict], output_path: Path) -> None:
    """Stolpediagram av kampanjeløft for ulike rabattnivåer."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    rabatter = [s["rabatt_pct"] for s in scenarios]
    loft = [s["kampanje_loeft_pct"] for s in scenarios]
    colors = ["#8CC8E5" if d == 0 else "#F6BA7C" for d in rabatter]
    edge = ["#1F6587" if d == 0 else "#9C540B" for d in rabatter]

    bars = ax.bar(rabatter, loft, width=3.5, color=colors, edgecolor=edge,
                  linewidth=1.0)
    for b, s in zip(bars, scenarios):
        ax.text(b.get_x() + b.get_width() / 2,
                b.get_height() + 2,
                f"+{s['kampanje_loeft_pct']:.0f}%",
                ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Rabatt (%)", fontsize=12)
    ax.set_ylabel("Kampanjeløft (%)", fontsize=12)
    ax.set_title("Scenarioanalyse: kampanjeløft som funksjon av rabatt",
                 fontsize=12, fontweight="bold")
    ax.set_xticks(rabatter)
    ax.set_ylim(0, max(loft) * 1.2 + 10)
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 6: PROGNOSE OG SCENARIOANALYSE")
    print(f"{'=' * 60}")

    arimax = load_arimax(output_dir)
    res = arimax["results"]
    df = generate_raw_data()
    df_feat = build_features(df)

    # --- Prognose: baseline og kampanje ---
    print(f"\nPrognose for de neste {HORIZON} dagene "
          f"(kampanje dag {CAMPAIGN_START_OFFSET + 1}--"
          f"{CAMPAIGN_START_OFFSET + CAMPAIGN_LENGTH}, "
          f"rabatt {BASE_DISCOUNT} %):")

    exog_base = build_future_exog(include_campaign=False)
    exog_camp = build_future_exog(discount=BASE_DISCOUNT, include_campaign=True)

    fc_base = forecast_with_exog(res, exog_base)
    fc_camp = forecast_with_exog(res, exog_camp)

    print("\n  Dag  Baseline  Kampanje  Løft %   95%-int (kampanje)")
    print("  " + "-" * 58)
    for k in range(HORIZON):
        lift = (fc_camp["mean"][k] / fc_base["mean"][k] - 1) * 100
        print(f"  {k + 1:>3d}  {fc_base['mean'][k]:>7.1f}   "
              f"{fc_camp['mean'][k]:>7.1f}  {lift:>+6.1f}   "
              f"[{fc_camp['lower'][k]:.0f}, {fc_camp['upper'][k]:.0f}]")

    base_total = float(np.sum(fc_base["mean"]))
    camp_total = float(np.sum(fc_camp["mean"]))
    print(f"\n  Totalt baseline  : {base_total:.0f} enheter")
    print(f"  Totalt kampanje  : {camp_total:.0f} enheter")
    print(f"  Ekstra solgt     : {camp_total - base_total:+.0f} enheter")
    print(f"  Netto løft       : {(camp_total / base_total - 1) * 100:+.1f} %")

    # Plott
    hist_window = 28
    hist_df = df_feat.iloc[-hist_window:]
    plot_baseline_vs_campaign(
        hist_df["t"].values,
        hist_df["salg"].values.astype(float),
        fc_base,
        fc_camp,
        output_dir / "arimax_forecast.png",
    )

    # --- Scenarioanalyse ---
    print("\n--- Scenarioanalyse over rabattnivåer ---")
    scenarios = run_scenario_analysis(res,
                                       discounts=(0, 10, 15, 20, 25, 30))
    for s in scenarios:
        print(
            f"  Rabatt {s['rabatt_pct']:>2d} %: "
            f"kampanjedager-sum = {s['kampanjedager_sum']:>6.1f}, "
            f"løft = {s['kampanje_loeft_pct']:>+6.1f} %, "
            f"ekstra enheter = {s['ekstra_enheter']:+.0f}"
        )
    plot_scenarios([s for s in scenarios if s["rabatt_pct"] > 0],
                   output_dir / "arimax_scenarios.png")

    # --- Priselastisitet (marginal effekt) ---
    # Vi estimerer elastisiteten som (d Y / d rabatt) ved å sammenligne
    # rabatt 10 -> 30 med samme kampanjestruktur.
    s10 = next(s for s in scenarios if s["rabatt_pct"] == 10)
    s30 = next(s for s in scenarios if s["rabatt_pct"] == 30)
    d_ekstra = (s30["ekstra_enheter"] - s10["ekstra_enheter"]) / (30 - 10)
    # beta_rabatt direkte fra modellen
    beta_rabatt = float(res.params["x_rabatt"])
    print(f"\n  Priselastisitet (modell):     beta_rabatt = {beta_rabatt:.2f} "
          f"enheter per % rabatt per kampanjedag")
    print(f"  Priselastisitet (scenario):   "
          f"delta(ekstra enheter) / delta(rabatt) = {d_ekstra:.2f} "
          f"enheter per prosentpoeng over hele kampanjen")

    # --- Lagre alt ---
    prognose_records = []
    for k in range(HORIZON):
        prognose_records.append(
            {
                "dag": k + 1,
                "baseline": round(float(fc_base["mean"][k]), 1),
                "kampanje": round(float(fc_camp["mean"][k]), 1),
                "kampanje_nedre": round(float(fc_camp["lower"][k]), 1),
                "kampanje_ovre": round(float(fc_camp["upper"][k]), 1),
                "loeft_pct": round(
                    (float(fc_camp["mean"][k]) / float(fc_base["mean"][k]) - 1)
                    * 100, 1
                ),
            }
        )

    results = {
        "horisont_dager": HORIZON,
        "kampanje_start": CAMPAIGN_START_OFFSET + 1,
        "kampanje_lengde": CAMPAIGN_LENGTH,
        "base_rabatt_pct": BASE_DISCOUNT,
        "prognose": prognose_records,
        "oppsummering": {
            "baseline_total": round(base_total, 1),
            "kampanje_total": round(camp_total, 1),
            "ekstra_enheter": round(camp_total - base_total, 1),
            "netto_loft_pct": round((camp_total / base_total - 1) * 100, 1),
        },
        "scenarioer": scenarios,
        "priselastisitet": {
            "beta_rabatt": round(beta_rabatt, 3),
            "scenario_delta": round(d_ekstra, 3),
        },
    }
    with open(output_dir / "forecast_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: forecast_results.json")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(
        f"  ARIMAX-prognosen forutsier at en 5-dagers kampanje med 20 % rabatt\n"
        f"  vil selge {camp_total - base_total:+.0f} ekstra enheter over 14-"
        f"dagershorisonten\n"
        f"  (netto løft {(camp_total / base_total - 1) * 100:+.1f} %). "
        f"Rabattelastisiteten er {beta_rabatt:.2f} enheter per prosentpoeng."
    )


if __name__ == "__main__":
    main()
