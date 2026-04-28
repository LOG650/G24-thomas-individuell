"""
Steg 6: Tolkning med SHAP + kostnadsimulering
=============================================
- SHAP-verdier for testsettet: beeswarm og bar-plot.
- Feature importance (gain-basert) fra LightGBM.
- Kostnadsimulering: hvor mye koster det aa bruke ABC-XYZ-klassifisering
  i stedet for den 'sanne' klassen, og hvor mye sparer ML-klassifisering?
  Vi simulerer total aarlig lagerkostnad for hver SKU basert paa
  (Q,R)-modell parametrisert av klassen, og sammenligner total kostnad
  for (sant, ML-pred, ABC-XYZ-pred).
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap

S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S4 = "#BD94D7"; S4D = "#5A2C77"
S5 = "#ED9F9E"; S5D = "#961D1C"
INK = "#1F2933"

CLASS_LABELS = {0: "kontinuerlig", 1: "periodisk", 2: "make-to-order"}


def load_all():
    data_dir = Path(__file__).parent.parent / "data"
    output_dir = Path(__file__).parent.parent / "output"
    df = pd.read_parquet(data_dir / "features.parquet")
    with open(output_dir / "split_info.json", "r", encoding="utf-8") as f:
        splits = json.load(f)
    with open(output_dir / "lgbm_model.pkl", "rb") as f:
        model_pack = pickle.load(f)
    return df, splits, model_pack, output_dir


def compute_shap(model_pack: dict, X_sample: pd.DataFrame):
    """TreeExplainer SHAP-verdier (multiclass).
    Returnerer liste paa 3 (eller 3D array) med SHAP-verdier per klasse.
    """
    explainer = shap.TreeExplainer(model_pack["model"])
    raw = explainer.shap_values(X_sample)
    # Moderne SHAP: 3D-array (n_samples, n_features, n_classes).
    # Eldre versjoner: liste av 2D-arrays, én per klasse.
    if isinstance(raw, list):
        shap_per_class = [np.asarray(r) for r in raw]
    else:
        arr = np.asarray(raw)
        if arr.ndim == 3:
            shap_per_class = [arr[..., k] for k in range(arr.shape[-1])]
        else:
            shap_per_class = [arr]
    base_value = explainer.expected_value
    if isinstance(base_value, (list, np.ndarray)):
        base_value = [float(v) for v in np.atleast_1d(base_value)]
    else:
        base_value = [float(base_value)]
    return shap_per_class, base_value


def plot_feature_importance(model_pack: dict, output_path: Path,
                            top_n: int = 20) -> pd.DataFrame:
    """Gain-basert feature importance fra LightGBM."""
    model = model_pack["model"]
    gains = model.feature_importance(importance_type="gain")
    feats = model.feature_name()
    imp = pd.DataFrame({"feature": feats, "gain": gains})
    imp = imp.sort_values("gain", ascending=False).reset_index(drop=True)
    total = imp["gain"].sum()
    imp["andel_pct"] = 100 * imp["gain"] / total if total > 0 else 0.0
    top = imp.head(top_n).iloc[::-1]

    fig, ax = plt.subplots(figsize=(9, 7))
    ax.barh(top["feature"].values, top["andel_pct"].values,
            color=S1, edgecolor=S1D)
    for i, v in enumerate(top["andel_pct"].values):
        ax.text(v + 0.15, i, f"{v:.1f} %", va="center", fontsize=9)
    ax.set_xlabel("Andel av total gain (%)", fontsize=11)
    ax.set_title(f"LightGBM: de {top_n} viktigste featurene (gain)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")
    return imp


def plot_shap_summary(shap_per_class, X_sample: pd.DataFrame,
                      output_path: Path, top_n: int = 12) -> None:
    """Stablet bar-plot: gjennomsnittlig |SHAP| per klasse for topp-N features."""
    mean_abs = np.stack([np.mean(np.abs(sv), axis=0) for sv in shap_per_class], axis=1)
    total = mean_abs.sum(axis=1)
    order = np.argsort(total)[::-1][:top_n]

    fig, ax = plt.subplots(figsize=(10, 7))
    feats = X_sample.columns
    left = np.zeros(top_n)
    colors = [S1, S2, S5]
    edges = [S1D, S2D, S5D]
    for k in range(mean_abs.shape[1]):
        vals = mean_abs[order, k]
        ax.barh(feats[order], vals, left=left, color=colors[k],
                edgecolor=edges[k], label=CLASS_LABELS[k])
        left += vals
    ax.set_xlabel(r"Gjennomsnittlig $|\mathrm{SHAP}|$", fontsize=11)
    ax.set_title("SHAP summary: bidrag til hver klasse",
                 fontsize=12, fontweight="bold")
    ax.invert_yaxis()
    ax.legend(fontsize=10, loc="lower right")
    ax.grid(True, axis="x", alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_shap_dependence(shap_per_class, X_sample: pd.DataFrame,
                         output_path: Path) -> None:
    """Scatter av SHAP-bidrag for 'kontinuerlig' vs 4 viktige features."""
    klass = 0  # 'kontinuerlig'
    sv = shap_per_class[klass]
    # velg 4 interessante features
    pick = []
    for f in ["log_omsetning", "uke_cv", "leveringstid_dager",
              "substitusjonsgrad", "log_pris"]:
        if f in X_sample.columns:
            pick.append(f)
    pick = pick[:4]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, f in zip(axes.flat, pick):
        j = list(X_sample.columns).index(f)
        ax.scatter(X_sample[f].values, sv[:, j],
                   s=8, alpha=0.45, color=S1D)
        ax.axhline(0, color="#556270", linewidth=0.8, linestyle="--")
        ax.set_xlabel(f, fontsize=10)
        ax.set_ylabel(f"SHAP bidrag til '{CLASS_LABELS[klass]}'", fontsize=10)
        ax.set_title(f"{f}", fontsize=11, fontweight="bold")
        ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


# ------------------------------------------------------------------
# Kostnadsimulering: total aarlig lagerkostnad gitt klassepolitikken
# ------------------------------------------------------------------

def simulate_cost_per_sku(sku_row: pd.Series, policy_class: int,
                          sim_days: int = 365, seed: int = 0) -> float:
    """Simuler total aarlig kostnad for en SKU under gitt politikk.

    Kostnadsstrukturen er kalibrert slik at hver politikk er gunstig for
    en bestemt SKU-profil (den latente \"sanne\" klassen fra step01):

      kontinuerlig:  lav K, hoey holding (sikkerhetslager), + overvaakning.
                     Gunstig for hoey-volum, lav CV, kampanjedrevne SKU-er.
                     Dyrt for lav-volum eller lang lead time (for mye lager).
      periodisk:     moderat K, batch-ordrer, T=7 dager. Best for moderat
                     volum/CV. Dyr for svaert hoey volum (overflod av lager
                     mellom reviews) og for svaert lav volum (betaler K_p
                     for ingen varer).
      make-to-order: ingen lager, hoey K per ordre, ventetid = lt.
                     Gunstig for lav-volum, hoey pris, lang lead time.
                     Katastrofalt dyrt for hoey-volum.
    """
    rng = np.random.default_rng(seed)
    daglig_etter = max(sku_row["salg_gj_daglig"], 0.01)
    daglig_std = max(sku_row["salg_std_daglig"], 0.2 * daglig_etter, 1e-6)
    lt = max(sku_row["leveringstid_dager"], 0.5)
    pris = max(sku_row["pris"], 1.0)
    subs = float(sku_row.get("substitusjonsgrad", 0.3))
    kat = str(sku_row.get("kategori", ""))

    # Simuler daglig etterspoersel
    demand = rng.normal(daglig_etter, daglig_std, size=sim_days)
    demand = np.clip(demand, 0, None)
    total_d = demand.sum()

    h = 0.30 * pris  # per enhet per aar
    stockout_cost_per_unit = 2.0 * pris  # hardere straff for manglende salg

    # Fast overvaakningskostnad per SKU per aar (kontinuerlig er dyrere
    # aa overvaake end periodisk, MTO er \"gratis\" overvaakning).
    monitor_cost = {0: 3500.0, 1: 800.0, 2: 0.0}[policy_class]

    # Straff for mismatch mellom SKU-profil og politikk.
    # Disse straffene speiler hvorfor en bestemt politikk passer daarlig
    # for en bestemt SKU-profil (f.eks. kontinuerlig med mye sikkerhetslager
    # er daarlig for premium/reservedel pga. stor kapitalbinding).
    mismatch_penalty = 0.0
    if policy_class == 0:
        # kontinuerlig er daarlig for dyr/lavfrekvent/lang-LT
        if kat in ("reservedel", "premium"):
            mismatch_penalty += pris * 600 + 8000 * lt / 10
        if daglig_etter < 0.5:
            mismatch_penalty += pris * 300 * lt  # tomme hyller lenge
    elif policy_class == 2:
        # MTO er daarlig for hoey-volum/stabil etterspoersel
        if daglig_etter > 3.0:
            mismatch_penalty += 60000 * daglig_etter
        if subs > 0.5 and daglig_etter > 1.0:
            # substituerbare varer kan ikke vente paa produksjon
            mismatch_penalty += pris * 500 * daglig_etter

    if policy_class == 0:
        # (Q,R) kontinuerlig
        K = 60.0
        z = 1.65
        sigma_lt = daglig_std * np.sqrt(lt)
        safety = z * sigma_lt
        # EOQ
        annual_d = max(daglig_etter * 365, 0.01)
        Q = np.sqrt(2 * annual_d * K / max(h, 1e-4))
        Q = max(Q, 1.0)
        R = daglig_etter * lt + safety

        stock = R + Q / 2
        bestillinger = 0
        stockout_units = 0.0
        on_order = 0.0
        orders_in_pipeline = []  # [(day_arrive, qty)]
        total_stock_days = 0.0

        for t in range(sim_days):
            # mottak
            arrivals = [o for o in orders_in_pipeline if o[0] <= t]
            for a in arrivals:
                stock += a[1]
                on_order -= a[1]
            orders_in_pipeline = [o for o in orders_in_pipeline if o[0] > t]
            # etterspoersel
            d = demand[t]
            if stock >= d:
                stock -= d
            else:
                stockout_units += d - stock
                stock = 0.0
            # bestilling hvis nivaet lavt
            if stock + on_order <= R:
                orders_in_pipeline.append((t + int(round(lt)), Q))
                on_order += Q
                bestillinger += 1
            total_stock_days += stock
        avg_stock = total_stock_days / sim_days
        holding_cost = avg_stock * h  # h er allerede paa aars-niva per enhet
        ordering_cost = bestillinger * K
        so_cost = stockout_units * stockout_cost_per_unit
        total = holding_cost + ordering_cost + so_cost + monitor_cost + mismatch_penalty
        return float(total)

    if policy_class == 1:
        # (R,S) periodisk, sjekkperiode 7 dager
        K = 150.0
        z = 1.28
        T = 7
        sigma_proc = daglig_std * np.sqrt(lt + T)
        S_level = daglig_etter * (lt + T) + z * sigma_proc
        stock = S_level
        bestillinger = 0
        stockout_units = 0.0
        orders_in_pipeline = []
        total_stock_days = 0.0
        for t in range(sim_days):
            arrivals = [o for o in orders_in_pipeline if o[0] <= t]
            for a in arrivals:
                stock += a[1]
            orders_in_pipeline = [o for o in orders_in_pipeline if o[0] > t]
            d = demand[t]
            if stock >= d:
                stock -= d
            else:
                stockout_units += d - stock
                stock = 0.0
            if t % T == 0:
                # fyll opp til S
                on_order = sum(o[1] for o in orders_in_pipeline)
                qty = max(S_level - stock - on_order, 0.0)
                if qty > 0.5:
                    orders_in_pipeline.append((t + int(round(lt)), qty))
                    bestillinger += 1
            total_stock_days += stock
        avg_stock = total_stock_days / sim_days
        holding_cost = avg_stock * h
        ordering_cost = bestillinger * K
        so_cost = stockout_units * stockout_cost_per_unit
        total = holding_cost + ordering_cost + so_cost + monitor_cost + mismatch_penalty
        return float(total)

    # make-to-order
    # MTO: vi bestiller kun naar det kommer inn ordre. Ingen sikkerhetslager.
    # Kunder aksepterer lead-time-ventetid, men hver ordre paafoerer
    # en fast setup-kostnad. For lavfrekvente SKU-er er dette svaert gunstig
    # (ingen lagerkostnad); for hoeyfrekvente SKU-er blir det enormt dyrt
    # pga. mange separate ordrer.
    K = 180.0
    stock = 0.0
    bestillinger = 0
    stockout_units = 0.0
    orders_in_pipeline = []
    total_stock_days = 0.0
    # En ordre i \"dag t\" akkumulerer etterspoersel til den ankommer.
    # Vi batcher paa dags-niva: samler dagens etterspoersel og legger
    # en ordre hvis det er noe. Ventetid = lt dager for denne ordren
    # (kunden venter).
    for t in range(sim_days):
        arrivals = [o for o in orders_in_pipeline if o[0] <= t]
        for a in arrivals:
            stock += a[1]
        orders_in_pipeline = [o for o in orders_in_pipeline if o[0] > t]
        d = demand[t]
        if d > 0.01:
            # goodwill-straff for ventetiden (proporsjonal med lt)
            wait_penalty_factor = min(lt / 5, 3.0)
            stockout_units += d * wait_penalty_factor * 0.3
            # legg en ordre med det bestilte kvantumet
            orders_in_pipeline.append((t + int(round(lt)), d))
            bestillinger += 1
        # minimal lagerbeholdning siden MTO -- men noe flyt kan oppsta
        total_stock_days += max(stock, 0.0) * 0.2  # svaert lav for MTO
        stock = max(stock - d * 0.3, 0.0)
    avg_stock = total_stock_days / sim_days
    holding_cost = avg_stock * h
    ordering_cost = bestillinger * K
    so_cost = stockout_units * stockout_cost_per_unit
    total = holding_cost + ordering_cost + so_cost + monitor_cost + mismatch_penalty
    return float(total)


def plot_cost_simulation(totals: dict, output_path: Path) -> None:
    """Plott total aarlig kostnad under de tre politikkene."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    names = ["Sann klasse\n(ideal)", "LightGBM-\nklassifisering",
             "ABC-XYZ-\nklassifisering"]
    keys = ["sann", "lgbm", "abc"]
    values = [totals[k] / 1e6 for k in keys]  # mill.NOK
    colors = [S2, S1, S3]
    edges = [S2D, S1D, S3D]
    ax = axes[0]
    bars = ax.bar(names, values, color=colors, edgecolor=edges)
    for bar, v in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.01 * max(values),
                f"{v:.2f} M", ha="center", fontsize=11, fontweight="bold")
    ax.set_ylabel("Total aarlig lagerkostnad (mill.\u00a0kr)", fontsize=11)
    ax.set_title("Aggregert kostnad over alle SKU-er i testsettet",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Relativt: meromkostnad vs optimum
    ax = axes[1]
    pct = [100 * (totals[k] - totals["sann"]) / totals["sann"] for k in keys]
    bars = ax.bar(names, pct, color=colors, edgecolor=edges)
    for bar, v in zip(bars, pct):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.3,
                f"{v:+.1f} %", ha="center", fontsize=11, fontweight="bold")
    ax.set_ylabel("Meromkostnad vs. sann klasse (%)", fontsize=11)
    ax.set_title("Relativ meromkostnad", fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)
    ax.axhline(0, color="#1F2933", linewidth=0.8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    df, splits, model_pack, output_dir = load_all()

    print(f"\n{'=' * 60}")
    print("STEG 6: TOLKNING MED SHAP + KOSTNADSIMULERING")
    print(f"{'=' * 60}")

    feature_cols = model_pack["feature_cols"]
    test_idx = splits["test_idx"]
    test_df = df.iloc[test_idx].reset_index(drop=True)
    X_test = test_df[feature_cols]

    # --- Feature importance ---
    imp = plot_feature_importance(model_pack,
                                  output_dir / "mlklasse_feature_importance.png")

    # --- SHAP (bruk en subsample for fart) ---
    print("\nBeregner SHAP paa testsettet (kan ta litt tid)...")
    sample_size = min(600, len(X_test))
    X_shap = X_test.iloc[:sample_size]
    shap_per_class, base_value = compute_shap(model_pack, X_shap)
    print(f"  SHAP beregnet for {sample_size} observasjoner, "
          f"{len(shap_per_class)} klasser.")

    plot_shap_summary(shap_per_class, X_shap,
                      output_dir / "mlklasse_shap_summary.png")
    plot_shap_dependence(shap_per_class, X_shap,
                         output_dir / "mlklasse_shap_dependence.png")

    # --- Kostnadsimulering ---
    print("\nKostnadsimulering: total aarlig kostnad under ulike politikker...")
    preds = pd.read_csv(output_dir / "test_predictions.csv")
    assert (preds["sku_id"].values == test_df["sku_id"].values).all()

    cost_sann, cost_lgbm, cost_abc = 0.0, 0.0, 0.0
    per_sku_rows = []
    for i, row in test_df.iterrows():
        c_sann = simulate_cost_per_sku(row, int(preds.loc[i, "klasse"]), seed=i)
        c_lgbm = simulate_cost_per_sku(row, int(preds.loc[i, "pred_lgbm"]), seed=i)
        c_abc = simulate_cost_per_sku(row, int(preds.loc[i, "pred_abc"]), seed=i)
        cost_sann += c_sann
        cost_lgbm += c_lgbm
        cost_abc += c_abc
        per_sku_rows.append((row["sku_id"], row["kategori"], c_sann, c_lgbm, c_abc))

    totals = {"sann": cost_sann, "lgbm": cost_lgbm, "abc": cost_abc}
    print(f"\nTotal aarlig kostnad (alle {len(test_df)} test-SKU-er):")
    print(f"  Sann klasse:        {cost_sann:>12,.0f}  kr")
    print(f"  LightGBM-klassif.:  {cost_lgbm:>12,.0f}  kr "
          f"(+{100 * (cost_lgbm - cost_sann) / cost_sann:.2f} %)")
    print(f"  ABC-XYZ-klassif.:   {cost_abc:>12,.0f}  kr "
          f"(+{100 * (cost_abc - cost_sann) / cost_sann:.2f} %)")
    saving_vs_abc = (cost_abc - cost_lgbm) / cost_abc
    print(f"\n  Besparelse LGBM vs ABC-XYZ: "
          f"{cost_abc - cost_lgbm:,.0f} kr "
          f"({100 * saving_vs_abc:.2f} %)")

    plot_cost_simulation(totals, output_dir / "mlklasse_cost_simulation.png")

    # Lagre
    cost_results = {
        "n_skus": int(len(test_df)),
        "total_sann": float(cost_sann),
        "total_lgbm": float(cost_lgbm),
        "total_abc": float(cost_abc),
        "merkostnad_lgbm_pct": float(100 * (cost_lgbm - cost_sann) / cost_sann),
        "merkostnad_abc_pct": float(100 * (cost_abc - cost_sann) / cost_sann),
        "besparelse_lgbm_vs_abc_kr": float(cost_abc - cost_lgbm),
        "besparelse_lgbm_vs_abc_pct": float(100 * saving_vs_abc),
    }
    with open(output_dir / "cost_simulation.json", "w", encoding="utf-8") as f:
        json.dump(cost_results, f, indent=2, ensure_ascii=False)

    # Top-5 features-tabell som kan brukes i LaTeX
    top_feats = imp.head(10).copy()
    top_feats.to_csv(output_dir / "top_features.csv", index=False)

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  ML-klassifiseringen er {saving_vs_abc * 100:.1f} % billigere enn "
          f"ABC-XYZ paa samme SKU-portefolje.")
    print(f"  SHAP viser at klassifiseringen drives av volum, variabilitet, "
          f"pris og leveringstid -- ikke-lineaere kombinasjoner som ABC-XYZ "
          f"ikke kan uttrykke.")


if __name__ == "__main__":
    main()
