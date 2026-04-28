"""
Steg 2: Uavhengig (Q,R) per produkt -- baseline
==============================================
Beregner klassisk (Q,R)-politikk per produkt uten a ta hensyn til
delte kapasitets- eller budsjettskranker. Formelverket er:

    Q_i^EOQ = sqrt(2 K_i D_i / (h_i c_i))
    R_i     = mu_{DL,i} + k_i * sigma_{DL,i}

der sigma_{DL,i}^2 = mu_{L,i} * sigma_{D,i}^2 + mu_{D,i}^2 * sigma_{L,i}^2
er variansen til etterspørsel under leveringstid (stokastisk L).

Kostnadsmodellen (aarlig) for hvert produkt er:

    TC_i(Q,R) = (K_i D_i / Q_i) + h_i c_i * (Q_i / 2 + SS_i) + pi_i D_i n(R_i)/Q_i

der SS_i = k_i sigma_{DL,i} og n(R) er forventet manko per syklus
(loss function for normalfordeling).
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

WEEKS_PER_YEAR = 52
SERVICE_LEVEL_TYPE1 = 0.95  # fell-rate (kritisk: P(ingen mangel pr syklus))


def load_products() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "produkter.csv")


def loss_function(k: float) -> float:
    """Standardisert normaltaps-funksjon L(k) = phi(k) - k (1 - Phi(k))."""
    return float(norm.pdf(k) - k * (1.0 - norm.cdf(k)))


def eoq(K: float, D_year: float, h: float, c: float) -> float:
    """Klassisk EOQ (harmonisk) -- kun bestillings- og lagerkostnad."""
    return float(np.sqrt(2.0 * K * D_year / (h * c)))


def eoq_with_shortage(K: float, D_year: float, h: float, c: float,
                      pi: float, sDL: float, Lk: float) -> float:
    """Optimal Q naar ogsaa forventet mangelkostnad inngaar i TC.

    Q* = sqrt( 2 D (K + pi sigma_{DL} L(k)) / (h c) )
    """
    return float(np.sqrt(2.0 * D_year * (K + pi * sDL * Lk) / (h * c)))


def sigma_DL(mu_D: float, sigma_D: float, mu_L: float, sigma_L: float) -> float:
    """Standardavvik for etterspørsel under leveringstid (Hadley-Whitin)."""
    var = mu_L * sigma_D ** 2 + mu_D ** 2 * sigma_L ** 2
    return float(np.sqrt(var))


def independent_qr(df: pd.DataFrame, alpha: float = SERVICE_LEVEL_TYPE1) -> pd.DataFrame:
    """Beregn uavhengig (Q,R) for hvert produkt gitt type-1 servicenivaa alpha.

    Benytter den utvidede EOQ-formelen som minimerer hele TC(Q,R) = ordering +
    holding + stockout, slik at sammenligningen mot den delte losningen er fair.
    """
    z = float(norm.ppf(alpha))
    Lk = loss_function(z)
    rows = []
    for _, row in df.iterrows():
        D_year = row["mu_D"] * WEEKS_PER_YEAR
        sDL = sigma_DL(row["mu_D"], row["sigma_D"], row["mu_L"], row["sigma_L"])
        Q = eoq_with_shortage(
            row["K"], D_year, row["h"], row["c"], row["pi"], sDL, Lk,
        )
        mu_DL = row["mu_D"] * row["mu_L"]
        SS = z * sDL
        R = mu_DL + SS
        # Forventet manko per syklus
        ESC = sDL * Lk
        n_orders = D_year / Q
        # Arlig kostnad
        ordering_cost = row["K"] * n_orders
        holding_cost = row["h"] * row["c"] * (Q / 2 + SS)
        stockout_cost = row["pi"] * ESC * n_orders
        total = ordering_cost + holding_cost + stockout_cost
        rows.append(
            {
                "produkt_id": row["produkt_id"],
                "D_year": round(D_year, 1),
                "Q_star": round(Q, 1),
                "R_star": round(R, 1),
                "SS": round(SS, 1),
                "sigma_DL": round(sDL, 2),
                "syklus_lager_verdi": round(row["c"] * Q / 2, 1),
                "sikkerhets_lager_verdi": round(row["c"] * SS, 1),
                "volum_syklus_m3": round(row["v"] * Q / 2, 3),
                "volum_ss_m3": round(row["v"] * SS, 3),
                "ordering_cost": round(ordering_cost, 1),
                "holding_cost": round(holding_cost, 1),
                "stockout_cost": round(stockout_cost, 1),
                "total_cost": round(total, 1),
                "z": round(z, 3),
                "service_type1": alpha,
            }
        )
    return pd.DataFrame(rows)


def plot_independent_costs(result: pd.DataFrame, output_path: Path) -> None:
    """Stablet soylediagram av kostnadene per produkt (uavhengig losning)."""
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(result))

    bottom = np.zeros(len(result))
    colors = [S_FILLS[0], S_FILLS[2], S_FILLS[4]]
    darks = [S_DARKS[0], S_DARKS[2], S_DARKS[4]]
    labels = ["Bestilling", "Lagerhold", "Mangel"]
    for col, color, dark, label in zip(
        ["ordering_cost", "holding_cost", "stockout_cost"], colors, darks, labels,
    ):
        vals = result[col].values / 1000.0  # kNOK
        ax.bar(x, vals, bottom=bottom, color=color, edgecolor=dark, label=label)
        bottom = bottom + vals

    ax.set_xticks(x)
    ax.set_xticklabels(result["produkt_id"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Arlig kostnad (kNOK)", fontsize=11)
    ax.set_title(
        "Uavhengig (Q,R): kostnadsstruktur per produkt",
        fontsize=12, fontweight="bold",
    )
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: UAVHENGIG (Q,R) PER PRODUKT")
    print("=" * 60)

    df = load_products()
    result = independent_qr(df, alpha=SERVICE_LEVEL_TYPE1)

    print(
        f"\nUavhengig (Q,R) med servicenivaa alpha = {SERVICE_LEVEL_TYPE1:.2f}"
    )
    print(result.to_string(index=False))

    # Oppsummering
    total_volume_cycle = float((df["v"] * result["Q_star"] / 2).sum())
    total_volume_ss = float((df["v"] * result["SS"]).sum())
    total_value_cycle = float((df["c"] * result["Q_star"] / 2).sum())
    total_value_ss = float((df["c"] * result["SS"]).sum())
    total_annual_cost = float(result["total_cost"].sum())

    summary = {
        "servicenivaa_type1": SERVICE_LEVEL_TYPE1,
        "volum_syklus_m3": round(total_volume_cycle, 2),
        "volum_sikkerhet_m3": round(total_volume_ss, 2),
        "volum_totalt_m3": round(total_volume_cycle + total_volume_ss, 2),
        "verdi_syklus_NOK": round(total_value_cycle, 0),
        "verdi_sikkerhet_NOK": round(total_value_ss, 0),
        "verdi_totalt_NOK": round(total_value_cycle + total_value_ss, 0),
        "total_aarlig_kostnad_NOK": round(total_annual_cost, 0),
    }
    print("\nPortefølje-sammendrag (uavhengig losning):")
    for key, value in summary.items():
        print(f"  {key}: {value}")

    result.to_csv(OUTPUT_DIR / "step02_independent_qr.csv", index=False)
    with open(OUTPUT_DIR / "step02_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_independent_costs(result, OUTPUT_DIR / "multiqr_independent_costs.png")


if __name__ == "__main__":
    main()
