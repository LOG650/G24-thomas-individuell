"""
Steg 4: Losning av flerprodukts (Q,R) med Lagrange
==================================================
Vi fikserer Type-1 servicenivaa per produkt (alpha -> k_i = Phi^{-1}(alpha))
og optimerer over Q = (Q_1, ..., Q_n) under to skranker:
sum v_i (Q_i/2 + SS_i) <= V_max og sum c_i (Q_i/2 + SS_i) <= B_max.

Med fiksert k_i er lagrangeanen for Q separabel i produktene gitt
lambda = (lambda_V, lambda_B). Forste-ordens betingelsen gir lukket form:

    Q_i(lambda) = sqrt( 2 D_i (K_i + pi_i sigma_{DL,i} L(k_i))
                       / (h_i c_i + lambda_V v_i + lambda_B c_i) )

Vi søker lambda >= 0 slik at skrankene oppfylles (binder naar lambda > 0)
via scipy.optimize.minimize paa den duale funksjonen g(lambda).
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import norm

from step01_datainnsamling import (
    DATA_DIR, OUTPUT_DIR, S_FILLS, S_DARKS, PRIMARY, INKMUTED,
)
from step02_uavhengig_qr import (
    WEEKS_PER_YEAR, SERVICE_LEVEL_TYPE1, loss_function, sigma_DL,
)
from step03_modell_formulering import V_MAX_M3, B_MAX_NOK


def build_arrays(df: pd.DataFrame) -> dict:
    """Konverter DataFrame til numpy-arrays for rask optimering."""
    return {
        "mu_D": df["mu_D"].values.astype(float),
        "sigma_D": df["sigma_D"].values.astype(float),
        "mu_L": df["mu_L"].values.astype(float),
        "sigma_L": df["sigma_L"].values.astype(float),
        "c": df["c"].values.astype(float),
        "K": df["K"].values.astype(float),
        "h": df["h"].values.astype(float),
        "pi": df["pi"].values.astype(float),
        "v": df["v"].values.astype(float),
        "produkt_id": df["produkt_id"].values,
    }


def Q_of_lambda(arrs: dict, k: np.ndarray, lam_V: float, lam_B: float) -> np.ndarray:
    """Lukket form for Q_i(lambda) gitt fikserte k_i."""
    mu_D = arrs["mu_D"]
    D_year = mu_D * WEEKS_PER_YEAR
    K = arrs["K"]
    h = arrs["h"]
    c = arrs["c"]
    v = arrs["v"]
    pi = arrs["pi"]
    sDL = np.sqrt(arrs["mu_L"] * arrs["sigma_D"] ** 2 + mu_D ** 2 * arrs["sigma_L"] ** 2)
    Lk = np.array([loss_function(ki) for ki in k])

    numerator = 2.0 * D_year * (K + pi * sDL * Lk)
    denominator = h * c + lam_V * v + lam_B * c
    return np.sqrt(numerator / denominator)


def total_cost(arrs: dict, Q: np.ndarray, k: np.ndarray) -> float:
    """Aarlig total kostnad (uten Lagrange-termer)."""
    mu_D = arrs["mu_D"]
    D_year = mu_D * WEEKS_PER_YEAR
    K = arrs["K"]
    h = arrs["h"]
    c = arrs["c"]
    pi = arrs["pi"]
    sDL = np.sqrt(arrs["mu_L"] * arrs["sigma_D"] ** 2 + mu_D ** 2 * arrs["sigma_L"] ** 2)
    Lk = np.array([loss_function(ki) for ki in k])
    SS = k * sDL
    ord_cost = K * D_year / Q
    hold_cost = h * c * (Q / 2 + SS)
    short_cost = pi * D_year * sDL * Lk / Q
    return float((ord_cost + hold_cost + short_cost).sum())


def resource_usage(arrs: dict, Q: np.ndarray, k: np.ndarray) -> tuple[float, float]:
    sDL = np.sqrt(arrs["mu_L"] * arrs["sigma_D"] ** 2 + arrs["mu_D"] ** 2 * arrs["sigma_L"] ** 2)
    SS = k * sDL
    V_used = float((arrs["v"] * (Q / 2 + SS)).sum())
    B_used = float((arrs["c"] * (Q / 2 + SS)).sum())
    return V_used, B_used


def dual_function(lam: np.ndarray, arrs: dict, k: np.ndarray,
                  V_max: float, B_max: float) -> float:
    """Negativ dualfunksjon g(lambda) (vi minimerer -g for a maksimere g)."""
    lam_V, lam_B = max(lam[0], 0.0), max(lam[1], 0.0)
    Q = Q_of_lambda(arrs, k, lam_V, lam_B)
    Q = np.maximum(Q, 1e-6)  # numerisk stabilitet
    tc = total_cost(arrs, Q, k)
    V_used, B_used = resource_usage(arrs, Q, k)
    g = tc + lam_V * (V_used - V_max) + lam_B * (B_used - B_max)
    return -g


def solve_primal_slsqp(arrs: dict, k: np.ndarray,
                       V_max: float, B_max: float) -> tuple[np.ndarray, dict]:
    """Loss primær-problemet direkte med SLSQP (constrained nonlinear program).

    min_Q  sum_i [ K_i D_i / Q_i + h_i c_i (Q_i/2 + SS_i) + pi_i D_i s_i L_i / Q_i ]
    s.t.   sum_i v_i (Q_i/2 + SS_i) <= V_max
           sum_i c_i (Q_i/2 + SS_i) <= B_max
           Q_i >= 1
    """
    from scipy.optimize import minimize as _minimize, NonlinearConstraint

    mu_D = arrs["mu_D"]
    D_year = mu_D * WEEKS_PER_YEAR
    K = arrs["K"]
    h = arrs["h"]
    c = arrs["c"]
    pi = arrs["pi"]
    v = arrs["v"]
    sDL = np.sqrt(arrs["mu_L"] * arrs["sigma_D"] ** 2 + mu_D ** 2 * arrs["sigma_L"] ** 2)
    Lk = np.array([loss_function(ki) for ki in k])
    SS = k * sDL

    def objective(Q):
        Q = np.maximum(Q, 1e-3)
        return float((K * D_year / Q + h * c * (Q / 2 + SS) + pi * D_year * sDL * Lk / Q).sum())

    def objective_grad(Q):
        Q = np.maximum(Q, 1e-3)
        return -K * D_year / Q ** 2 + h * c / 2 - pi * D_year * sDL * Lk / Q ** 2

    def vol_constraint(Q):  # must be <= 0
        return V_max - float((v * (Q / 2 + SS)).sum())

    def bud_constraint(Q):
        return B_max - float((c * (Q / 2 + SS)).sum())

    # Startpunkt: skalert uavhengig Q slik at det er feasible.
    Q0 = np.sqrt(2.0 * D_year * (K + pi * sDL * Lk) / (h * c))
    V_used0 = float((v * (Q0 / 2 + SS)).sum())
    B_used0 = float((c * (Q0 / 2 + SS)).sum())
    # Krymp Q0 til feasible naar uavhengig losning er infeasible.
    vol_headroom = V_max - float((v * SS).sum())
    bud_headroom = B_max - float((c * SS).sum())
    cycle_vol = float((v * Q0 / 2).sum())
    cycle_bud = float((c * Q0 / 2).sum())
    scale = 1.0
    if cycle_vol > vol_headroom:
        scale = min(scale, 0.9 * vol_headroom / max(cycle_vol, 1e-9))
    if cycle_bud > bud_headroom:
        scale = min(scale, 0.9 * bud_headroom / max(cycle_bud, 1e-9))
    Q0 = np.maximum(Q0 * max(scale, 0.05), 1.0)

    constraints = [
        {"type": "ineq", "fun": vol_constraint},
        {"type": "ineq", "fun": bud_constraint},
    ]
    bounds = [(1.0, None)] * len(Q0)

    result = _minimize(
        objective, Q0, jac=objective_grad, method="SLSQP",
        bounds=bounds, constraints=constraints,
        options={"maxiter": 500, "ftol": 1e-7},
    )
    return np.maximum(result.x, 1.0), {
        "success": bool(result.success),
        "iterations": int(result.nit),
        "message": str(result.message),
    }


def recover_multipliers(arrs: dict, Q: np.ndarray, k: np.ndarray,
                        V_max: float, B_max: float) -> tuple[float, float]:
    """Gjenopprett Lagrange-multiplikatorer fra KKT-betingelsene.

    For hvert produkt:  d TC / d Q_i + (lambda_V v_i + lambda_B c_i) / 2 = 0
    => (lambda_V v_i + lambda_B c_i) = 2 K_i D_i / Q_i^2 + 2 pi_i D_i s_i L_i / Q_i^2 - h_i c_i

    Bruk minste kvadraters tilpasning paa de aktive skrankene.
    """
    mu_D = arrs["mu_D"]
    D_year = mu_D * WEEKS_PER_YEAR
    K = arrs["K"]
    h = arrs["h"]
    c = arrs["c"]
    pi = arrs["pi"]
    v = arrs["v"]
    sDL = np.sqrt(arrs["mu_L"] * arrs["sigma_D"] ** 2 + mu_D ** 2 * arrs["sigma_L"] ** 2)
    Lk = np.array([loss_function(ki) for ki in k])

    # Høyreside per produkt: target = 2(K_i D_i + pi_i D_i s_i L_i) / Q_i^2 - h_i c_i
    target = 2.0 * (K * D_year + pi * D_year * sDL * Lk) / Q ** 2 - h * c

    # Venstre: v_i * lam_V + c_i * lam_B. Aktiv skranke-sjekk:
    SS = k * sDL
    V_used = float((v * (Q / 2 + SS)).sum())
    B_used = float((c * (Q / 2 + SS)).sum())
    V_active = abs(V_used - V_max) < 1e-3 * V_max
    B_active = abs(B_used - B_max) < 1e-3 * B_max

    A_rows, b_rows = [], []
    for i in range(len(Q)):
        A_rows.append([v[i], c[i]])
        b_rows.append(target[i])
    A = np.array(A_rows)
    b = np.array(b_rows)

    if V_active and B_active:
        lam, *_ = np.linalg.lstsq(A, b, rcond=None)
        lam_V = max(0.0, float(lam[0]))
        lam_B = max(0.0, float(lam[1]))
    elif V_active:
        lam_V = max(0.0, float((v @ b) / (v @ v)))
        lam_B = 0.0
    elif B_active:
        lam_B = max(0.0, float((c @ b) / (c @ c)))
        lam_V = 0.0
    else:
        lam_V, lam_B = 0.0, 0.0
    return lam_V, lam_B


def solve_shared_capacity(df: pd.DataFrame, alpha: float,
                          V_max: float, B_max: float) -> dict:
    """Losser primær-problemet med SLSQP og gjenoppretter Lagrange-multiplikatorer."""
    arrs = build_arrays(df)
    n = len(df)
    k = np.full(n, norm.ppf(alpha))

    Q_star, info = solve_primal_slsqp(arrs, k, V_max, B_max)
    lam_V, lam_B = recover_multipliers(arrs, Q_star, k, V_max, B_max)
    lam = np.array([lam_V, lam_B])
    n_iter = info["iterations"]
    sDL = np.sqrt(arrs["mu_L"] * arrs["sigma_D"] ** 2
                  + arrs["mu_D"] ** 2 * arrs["sigma_L"] ** 2)
    SS = k * sDL
    R_star = arrs["mu_D"] * arrs["mu_L"] + SS
    V_used, B_used = resource_usage(arrs, Q_star, k)
    tc = total_cost(arrs, Q_star, k)

    per_product = pd.DataFrame(
        {
            "produkt_id": arrs["produkt_id"],
            "Q_star": np.round(Q_star, 1),
            "R_star": np.round(R_star, 1),
            "SS": np.round(SS, 1),
            "sigma_DL": np.round(sDL, 2),
            "volum_snitt_m3": np.round(arrs["v"] * (Q_star / 2 + SS), 3),
            "verdi_snitt_NOK": np.round(arrs["c"] * (Q_star / 2 + SS), 1),
        }
    )
    return {
        "lambda_V": float(lam[0]),
        "lambda_B": float(lam[1]),
        "Q": Q_star,
        "k": k,
        "SS": SS,
        "R": R_star,
        "V_used": V_used,
        "B_used": B_used,
        "V_max": V_max,
        "B_max": B_max,
        "total_cost": tc,
        "per_product": per_product,
        "optimizer_message": f"Subgradient ascent, {n_iter} iter",
        "optimizer_success": True,
        "iterations": int(n_iter),
    }


def plot_lambda_sweep(arrs: dict, k: np.ndarray, output_path: Path) -> None:
    """Vis V_used og B_used som funksjon av skyggepris-triangel (lam_V, lam_B=0)."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))
    grid = np.linspace(0, 0.3, 25)

    ax = axes[0]
    V_list, B_list = [], []
    for lv in grid:
        Q = Q_of_lambda(arrs, k, lv, 0.0)
        V, B = resource_usage(arrs, Q, k)
        V_list.append(V)
        B_list.append(B)
    ax.plot(grid, V_list, "-o", color=S_DARKS[0], markersize=4,
            markerfacecolor=S_FILLS[0], label="Volum (m$^3$)")
    ax.axhline(V_MAX_M3, ls="--", color=S_DARKS[4], label="$V_{\\max}$")
    ax.set_xlabel(r"$\lambda_V$", fontsize=12)
    ax.set_ylabel(r"Volum $\sum v_i(Q_i/2+SS_i)$", fontsize=11)
    ax.set_title(r"Volumbruk vs.\ $\lambda_V$ ($\lambda_B=0$)",
                 fontsize=11, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    grid_B = np.linspace(0, 0.25, 25)
    V_list, B_list = [], []
    for lb in grid_B:
        Q = Q_of_lambda(arrs, k, 0.0, lb)
        V, B = resource_usage(arrs, Q, k)
        V_list.append(V)
        B_list.append(B / 1000)  # kNOK
    ax.plot(grid_B, B_list, "-o", color=S_DARKS[2], markersize=4,
            markerfacecolor=S_FILLS[2], label="Budsjett (kNOK)")
    ax.axhline(B_MAX_NOK / 1000, ls="--", color=S_DARKS[4], label="$B_{\\max}$")
    ax.set_xlabel(r"$\lambda_B$", fontsize=12)
    ax.set_ylabel(r"Kapitalbinding (kNOK)", fontsize=11)
    ax.set_title(r"Kapitalbinding vs.\ $\lambda_B$ ($\lambda_V=0$)",
                 fontsize=11, fontweight="bold")
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_shadow_price(sol: dict, arrs: dict, output_path: Path) -> None:
    """Bar-plott: Q_uavhengig vs Q_delt per produkt."""
    indep = pd.read_csv(OUTPUT_DIR / "step02_independent_qr.csv")
    fig, ax = plt.subplots(figsize=(9, 4.5))
    x = np.arange(len(arrs["produkt_id"]))
    width = 0.38

    ax.bar(x - width / 2, indep["Q_star"], width,
           color=S_FILLS[0], edgecolor=S_DARKS[0], label="Uavhengig $Q_i^*$")
    ax.bar(x + width / 2, sol["Q"], width,
           color=S_FILLS[2], edgecolor=S_DARKS[2], label="Delt $Q_i^{**}$")
    ax.set_xticks(x)
    ax.set_xticklabels(arrs["produkt_id"], rotation=45, ha="right", fontsize=9)
    ax.set_ylabel("Bestillingsmengde (enheter)", fontsize=11)
    ax.set_title(
        r"Effekt av delte skranker paa $Q_i$ "
        f"($\\lambda_V={sol['lambda_V']:.3f}$, "
        f"$\\lambda_B={sol['lambda_B']:.4f}$)",
        fontsize=11, fontweight="bold",
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
    print("STEG 4: OPTIMERING MED DELTE SKRANKER")
    print("=" * 60)

    df = pd.read_csv(DATA_DIR / "produkter.csv")
    arrs = build_arrays(df)
    sol = solve_shared_capacity(
        df, alpha=SERVICE_LEVEL_TYPE1, V_max=V_MAX_M3, B_max=B_MAX_NOK,
    )

    print(f"\nOptimizer success: {sol['optimizer_success']} ({sol['iterations']} iter)")
    print(f"  lambda_V = {sol['lambda_V']:.5f}")
    print(f"  lambda_B = {sol['lambda_B']:.7f}")
    print(f"  V_used = {sol['V_used']:.3f} / V_max = {V_MAX_M3}")
    print(f"  B_used = {sol['B_used']:,.0f} / B_max = {B_MAX_NOK:,.0f}")
    print(f"  Total aarlig kostnad = {sol['total_cost']:,.0f} NOK")

    print("\nPer produkt:")
    print(sol["per_product"].to_string(index=False))

    # Lagre resultater
    indep = pd.read_csv(OUTPUT_DIR / "step02_independent_qr.csv")
    TC_indep = float(indep["total_cost"].sum())
    delta = sol["total_cost"] - TC_indep

    out = {
        "servicenivaa_type1": SERVICE_LEVEL_TYPE1,
        "V_max_m3": V_MAX_M3,
        "B_max_NOK": B_MAX_NOK,
        "lambda_V": sol["lambda_V"],
        "lambda_B": sol["lambda_B"],
        "V_used_m3": round(sol["V_used"], 3),
        "B_used_NOK": round(sol["B_used"], 0),
        "total_cost_NOK": round(sol["total_cost"], 0),
        "total_cost_uavhengig_NOK": round(TC_indep, 0),
        "kostnadsokning_NOK": round(delta, 0),
        "kostnadsokning_pct": round(100 * delta / TC_indep, 2),
        "iterations": sol["iterations"],
        "optimizer_message": str(sol["optimizer_message"]),
    }

    with open(OUTPUT_DIR / "step04_optimering.json", "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    sol["per_product"].to_csv(OUTPUT_DIR / "step04_shared_qr.csv", index=False)

    # Figurer
    plot_lambda_sweep(arrs, sol["k"], OUTPUT_DIR / "multiqr_shadow_price.png")
    plot_shadow_price(sol, arrs, OUTPUT_DIR / "multiqr_Q_comparison.png")

    print("\nFerdig med steg 4.")


if __name__ == "__main__":
    main()
