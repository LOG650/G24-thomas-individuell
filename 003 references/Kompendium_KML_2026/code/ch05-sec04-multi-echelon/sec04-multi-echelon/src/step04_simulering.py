"""
Steg 4: Monte Carlo-simulering av begge politikker
==================================================
Simulerer systemet dag for dag over T_DAGER perioder og N_REP replikasjoner,
for baade uavhengig (s,S) og Clark-Scarf echelon base-stock. Registrerer:
- Realisert type-1 servicenivaa per region (fraksjon dager uten backorder)
- Realisert fill rate (type-2) per region
- Forventet holdekostnad
- Forventet backorder-kostnad
- Total systemkostnad

Systemlogikk (periodisk gjennomgang, dagens rytme):
  1. Send transitt-ankomster til mottakerne (sentral og regioner).
  2. Regionene moter kundeetterspørsel; eventuell mangel gaar til backorder.
  3. Hver node ser lagerposisjon = installasjonslager + transit - backorder.
  4. Policy bestemmer bestilling:
     - base-stock: order-up-to S_install.
     - For sentrallageret er ordren "all pass-through" i UAVH-politikk
       (bestiller S_0_install - IP_0 fra leverandør).
     - For region i: bestiller S_i_install - IP_i fra sentrallager.
  5. Bestillinger lagt inn ved sentrallageret tas kun til fysisk
     allokering saa lenge sentrallageret har varer (allocation rule:
     pro-rata naar vi ikke har nok).
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / "output"

T_DAGER = 730  # 2 aar daglig simulering
N_REP = 40
SEED = 17

S_FILLS = ["#8CC8E5", "#97D4B7", "#F6BA7C", "#BD94D7", "#ED9F9E"]
S_DARKS = ["#1F6587", "#307453", "#9C540B", "#5A2C77", "#961D1C"]
PRIMARY = "#1F6587"
INKMUTED = "#556270"
INK = "#1F2933"


def load_all() -> dict:
    with open(OUTPUT_DIR / "step01_parameters.json", "r", encoding="utf-8") as f:
        p = json.load(f)
    with open(OUTPUT_DIR / "step02_uavhengig_ss.json", "r", encoding="utf-8") as f:
        uav = json.load(f)
    with open(OUTPUT_DIR / "step03_clark_scarf.json", "r", encoding="utf-8") as f:
        cs = json.load(f)
    return {"params": p, "uav": uav, "cs": cs}


def simulate_system(
    params: dict,
    S_install_0: float,
    S_install_region: np.ndarray,
    T: int = T_DAGER,
    rng: np.random.Generator | None = None,
) -> dict:
    """Simulerer systemet over T dager for gitte installasjons-base-stock.

    Returnerer per-dag-serie for statistikk.
    """
    if rng is None:
        rng = np.random.default_rng(SEED)

    N = params["N"]
    mu_d = np.array(params["mu_d"])
    sigma_d = np.array(params["sigma_d"])
    L_reg = np.array(params["L_reg"], dtype=int)
    L0 = int(params["L_sentral"])
    R = int(params["R"])

    # Startlagre: start ved base-stock (warmup kaster vi uansett)
    I_0 = S_install_0
    I_reg = S_install_region.copy()

    # Transit-kø: pipeline[node][k] = enheter som ankommer om (k+1) dager
    pipe_0 = [0.0] * L0
    pipe_reg = [[0.0] * int(L_reg[i]) for i in range(N)]

    backorder_reg = np.zeros(N)  # backordre hos regionene
    backorder_0 = 0.0            # backorder fra region (= varer de venter)

    # Logger
    demand_log = np.zeros((T, N))
    served_log = np.zeros((T, N))
    stockout_days = np.zeros(N, dtype=int)  # dager med manko i region
    hold_reg_log = np.zeros((T, N))
    hold_0_log = np.zeros(T)
    back_reg_log = np.zeros((T, N))

    for t in range(T):
        # 1a. Ankomster i transit (stepp ett dag)
        if L0 > 0:
            arrival_0 = pipe_0[0]
            pipe_0 = pipe_0[1:] + [0.0]
        else:
            arrival_0 = 0.0
        I_0 += arrival_0

        for i in range(N):
            if L_reg[i] > 0:
                arrive_i = pipe_reg[i][0]
                pipe_reg[i] = pipe_reg[i][1:] + [0.0]
            else:
                arrive_i = 0.0
            I_reg[i] += arrive_i
            # Dekk eventuelle backordre forst
            if backorder_reg[i] > 0 and I_reg[i] > 0:
                s = min(backorder_reg[i], I_reg[i])
                backorder_reg[i] -= s
                I_reg[i] -= s

        # 2. Etterspørsel hos hver region
        D = rng.normal(mu_d, sigma_d)
        D = np.maximum(D, 0.0)  # trunker negative
        demand_log[t] = D

        for i in range(N):
            if I_reg[i] >= D[i]:
                I_reg[i] -= D[i]
                served_log[t, i] = D[i]
            else:
                served_log[t, i] = I_reg[i]
                unmet = D[i] - I_reg[i]
                I_reg[i] = 0.0
                backorder_reg[i] += unmet
                stockout_days[i] += 1

        hold_0_log[t] = I_0
        hold_reg_log[t] = I_reg
        back_reg_log[t] = backorder_reg

        # 3. Bestillingsbeslutning (periodisk gjennomgang hver dag)
        # Regionene: IP_i = I_i - backorder_i + sum(pipe_reg[i])
        orders_region = np.zeros(N)
        for i in range(N):
            IP_i = I_reg[i] - backorder_reg[i] + sum(pipe_reg[i])
            target = S_install_region[i]
            if IP_i < target:
                orders_region[i] = target - IP_i

        # Alloker fra sentrallager
        total_order = orders_region.sum()
        if I_0 >= total_order:
            allokert = orders_region.copy()
            I_0 -= total_order
        else:
            # pro-rata allokering
            if total_order > 1e-9:
                allokert = orders_region * (I_0 / total_order)
            else:
                allokert = np.zeros(N)
            I_0 = 0.0

        # Ikke-allokert andel blir regionalt backorder ved sentrallageret
        # (saa ordren blir "prioritert" neste dag). Enkelhet:
        # gjenvaerende ordre fra regionene tapes fra sentralbestillingen,
        # men sentrallageret har ansvar for aa fylle opp i neste periode.
        for i in range(N):
            # Legg det allokerte kvantumet i regionens pipeline
            if L_reg[i] > 0:
                pipe_reg[i][-1] += allokert[i]
            else:
                I_reg[i] += allokert[i]

        # Sentrallager bestiller fra leverandoren
        IP_0 = I_0 - backorder_0 + sum(pipe_0)
        if IP_0 < S_install_0:
            order_0 = S_install_0 - IP_0
            if L0 > 0:
                pipe_0[-1] += order_0
            else:
                I_0 += order_0

    # Warmup (hopp over forste 30 dager i statistikk)
    W = 30
    d = demand_log[W:]
    s = served_log[W:]
    hreg = hold_reg_log[W:]
    h0 = hold_0_log[W:]
    breg = back_reg_log[W:]

    type1 = np.zeros(N)
    fill_rate = np.zeros(N)
    for i in range(N):
        # type1: fraksjon dager uten backorder ved sluttet periode
        type1[i] = float(np.mean(breg[:, i] <= 1e-6))
        fill_rate[i] = float(np.sum(s[:, i]) / max(np.sum(d[:, i]), 1e-9))

    # Kostnader
    h_inst = np.array(params["h_install"])
    holding_reg_daily = hreg.mean(axis=0) * h_inst[1:]
    holding_0_daily = float(h0.mean() * h_inst[0])
    holding_daily = float(holding_0_daily + holding_reg_daily.sum())
    holding_annual = holding_daily * 365

    b = params["b_region"]
    backorder_daily = float(breg.mean() * b * N)  # mean er allerede per node
    # Riktig sum:
    backorder_daily = float(breg.mean(axis=0).sum() * b)
    backorder_annual = backorder_daily * 365

    total_annual = holding_annual + backorder_annual

    return {
        "type1_per_region": type1.tolist(),
        "fill_rate_per_region": fill_rate.tolist(),
        "stockout_days": stockout_days.tolist(),
        "holding_per_node_NOK_per_aar": [
            holding_0_daily * 365,
            *(holding_reg_daily * 365).tolist(),
        ],
        "total_holding_NOK_per_aar": holding_annual,
        "total_backorder_NOK_per_aar": backorder_annual,
        "total_NOK_per_aar": total_annual,
        "mean_inv_per_node": [
            float(h0.mean()),
            *hreg.mean(axis=0).tolist(),
        ],
        "mean_backorder_per_region": breg.mean(axis=0).tolist(),
    }


def replicate(policy_label: str, params: dict, S_install_0: float,
              S_install_region: np.ndarray, n_rep: int) -> dict:
    """Kjor n_rep replikasjoner og aggreger."""
    rows = []
    for rep in range(n_rep):
        rng = np.random.default_rng(SEED + rep * 101)
        out = simulate_system(params, S_install_0, S_install_region,
                              T=T_DAGER, rng=rng)
        rows.append(out)

    # Aggregat
    def agg(key):
        return np.mean([r[key] for r in rows], axis=0)

    N = params["N"]
    type1 = agg("type1_per_region")
    fillrate = agg("fill_rate_per_region")
    holding_per_node = agg("holding_per_node_NOK_per_aar")
    total_h = float(np.mean([r["total_holding_NOK_per_aar"] for r in rows]))
    total_b = float(np.mean([r["total_backorder_NOK_per_aar"] for r in rows]))
    total = float(np.mean([r["total_NOK_per_aar"] for r in rows]))
    se_total = float(np.std([r["total_NOK_per_aar"] for r in rows], ddof=1) /
                     np.sqrt(len(rows)))
    mean_inv_per_node = agg("mean_inv_per_node")

    return {
        "policy": policy_label,
        "n_rep": n_rep,
        "type1_per_region": [float(x) for x in type1],
        "fill_rate_per_region": [float(x) for x in fillrate],
        "holding_per_node_NOK_per_aar": [float(x) for x in holding_per_node],
        "total_holding_NOK_per_aar": total_h,
        "total_backorder_NOK_per_aar": total_b,
        "total_NOK_per_aar": total,
        "se_total_NOK_per_aar": se_total,
        "mean_inv_per_node": [float(x) for x in mean_inv_per_node],
    }


def plot_service_compare(
    params: dict, res_uav: dict, res_cs: dict, output_path: Path
) -> None:
    """Søylediagram: realisert type-1 service per region for begge politikker."""
    regioner = params["regioner"]
    N = len(regioner)
    x = np.arange(N)
    width = 0.36

    fig, ax = plt.subplots(figsize=(8, 4.2))
    bars_uav = ax.bar(x - width / 2, res_uav["type1_per_region"], width,
                      color=S_FILLS[0], edgecolor=S_DARKS[0],
                      label="Uavhengig (s,S)")
    bars_cs = ax.bar(x + width / 2, res_cs["type1_per_region"], width,
                     color=S_FILLS[1], edgecolor=S_DARKS[1],
                     label="Clark-Scarf")

    ax.axhline(0.95, color=INKMUTED, linestyle="--", lw=1.2,
               label=r"M\aa l $\alpha = 0{,}95$")
    ax.set_xticks(x)
    ax.set_xticklabels(regioner, fontsize=10)
    ax.set_ylabel("Realisert type-1 servicenivaa", fontsize=11)
    ax.set_ylim(0.75, 1.01)
    ax.set_title("Realisert servicenivaa per region (Monte Carlo)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(fontsize=9, loc="lower right")

    for bars in (bars_uav, bars_cs):
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.005,
                    f"{b.get_height():.3f}", ha="center", va="bottom",
                    fontsize=8, color=INK)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_cost_compare(
    params: dict, res_uav: dict, res_cs: dict, output_path: Path
) -> None:
    """Stablet bar: holdekostnad + backorder-kostnad per politikk."""
    labels = ["Uavhengig (s,S)", "Clark-Scarf"]
    hold = [res_uav["total_holding_NOK_per_aar"] / 1000,
            res_cs["total_holding_NOK_per_aar"] / 1000]
    back = [res_uav["total_backorder_NOK_per_aar"] / 1000,
            res_cs["total_backorder_NOK_per_aar"] / 1000]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    x = np.arange(len(labels))
    w = 0.55

    bars1 = ax.bar(x, hold, w, color=S_FILLS[0], edgecolor=S_DARKS[0],
                   label="Holdekostnad")
    bars2 = ax.bar(x, back, w, bottom=hold, color=S_FILLS[4],
                   edgecolor=S_DARKS[4], label="Backorder-kostnad")

    tot = [h + b for h, b in zip(hold, back)]
    for xi, t in zip(x, tot):
        ax.text(xi, t + max(tot) * 0.02, f"{t:,.0f} kNOK",
                ha="center", va="bottom", fontsize=10,
                fontweight="bold", color=INK)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Kostnad (kNOK/aar)", fontsize=11)
    ax.set_title("Arlig totalkostnad per politikk",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(fontsize=9, loc="upper right")
    ax.set_ylim(0, max(tot) * 1.15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def plot_policy_compare(
    params: dict, res_uav: dict, res_cs: dict, output_path: Path
) -> None:
    """Visualiser gjennomsnittlig lagernivaa per node per politikk."""
    labels = ["Sentrallager", *params["regioner"]]
    x = np.arange(len(labels))
    width = 0.36

    fig, ax = plt.subplots(figsize=(9, 4.2))
    uav_inv = res_uav["mean_inv_per_node"]
    cs_inv = res_cs["mean_inv_per_node"]

    ax.bar(x - width / 2, uav_inv, width, color=S_FILLS[0],
           edgecolor=S_DARKS[0], label="Uavhengig (s,S)")
    ax.bar(x + width / 2, cs_inv, width, color=S_FILLS[1],
           edgecolor=S_DARKS[1], label="Clark-Scarf")

    for i, (u, c) in enumerate(zip(uav_inv, cs_inv)):
        ax.text(i - width / 2, u + max(max(uav_inv), max(cs_inv)) * 0.02,
                f"{u:.0f}", ha="center", va="bottom", fontsize=8)
        ax.text(i + width / 2, c + max(max(uav_inv), max(cs_inv)) * 0.02,
                f"{c:.0f}", ha="center", va="bottom", fontsize=8)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylabel("Gj.snitt installasjonslager (enheter)", fontsize=11)
    ax.set_title("Gjennomsnittlig lagernivaa per node",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 4: MONTE CARLO-SIMULERING")
    print("=" * 60)

    d = load_all()
    params = d["params"]
    uav = d["uav"]
    cs = d["cs"]

    # Uavhengig policy: installasjons-S = de isolerte beregnede base-stock.
    S0_uav = uav["S_0"]
    Sreg_uav = np.array(uav["S_region"])

    # Clark-Scarf policy: installasjons-S_0 = S^e_0 - sum S^e_reg.
    S0_cs = cs["S_install_0"]
    # Hvis denne er negativ (irrealistisk) sett til liten positiv buffer
    S0_cs_use = max(S0_cs, 0.0)
    Sreg_cs = np.array(cs["S_install_region"])

    print(f"\nPolicy UAV: S_0 = {S0_uav:.1f}, S_reg = "
          f"{[float(f'{x:.1f}') for x in Sreg_uav]}")
    print(f"Policy CS : S_0 = {S0_cs_use:.1f}, S_reg = "
          f"{[float(f'{x:.1f}') for x in Sreg_cs]}")

    print(f"\nKjorer {N_REP} replikasjoner x {T_DAGER} dager...")

    res_uav = replicate("uavhengig", params, S0_uav, Sreg_uav, N_REP)
    res_cs = replicate("clark_scarf", params, S0_cs_use, Sreg_cs, N_REP)

    for res in (res_uav, res_cs):
        print(f"\n--- {res['policy']} ---")
        print(f"  type1 per region: "
              f"{[f'{x:.3f}' for x in res['type1_per_region']]}")
        print(f"  fill rate:        "
              f"{[f'{x:.3f}' for x in res['fill_rate_per_region']]}")
        print(f"  holdekostnad/aar: {res['total_holding_NOK_per_aar']:,.0f} NOK")
        print(f"  backorder/aar:    {res['total_backorder_NOK_per_aar']:,.0f} NOK")
        print(f"  TOTAL/aar:        {res['total_NOK_per_aar']:,.0f} NOK "
              f"(SE = {res['se_total_NOK_per_aar']:,.0f})")

    diff = res_uav["total_NOK_per_aar"] - res_cs["total_NOK_per_aar"]
    rel = diff / res_uav["total_NOK_per_aar"] * 100
    print(f"\nBesparelse Clark-Scarf vs. uavhengig: "
          f"{diff:,.0f} NOK/aar ({rel:.1f} %)")

    # Figurer
    plot_service_compare(params, res_uav, res_cs,
                         OUTPUT_DIR / "echelon_service_compare.png")
    plot_cost_compare(params, res_uav, res_cs,
                      OUTPUT_DIR / "echelon_cost_compare.png")
    plot_policy_compare(params, res_uav, res_cs,
                        OUTPUT_DIR / "echelon_policy_compare.png")

    # Lagre
    out = {
        "T_dager": T_DAGER,
        "n_rep": N_REP,
        "res_uav": res_uav,
        "res_cs": res_cs,
        "S0_uav": float(S0_uav),
        "S_reg_uav": [float(x) for x in Sreg_uav],
        "S0_cs_install": float(S0_cs),
        "S_reg_cs": [float(x) for x in Sreg_cs],
    }
    path = OUTPUT_DIR / "step04_simulering.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {path}")
    print("\nFerdig med steg 4.\n")


if __name__ == "__main__":
    main()
