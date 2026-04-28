"""
Steg 2: Uavhengig (s,S) per lager - naiv baseline
=================================================
Hvert lager (sentralt + fire regionale) ser kun sin egen lokale etterspørsel
og beregner en base-stock S_i som oppfyller et lokalt servicenivaa alpha.

KONSERVATIV NAIV: Regionlagrene ignorerer at sentrallageret kan vaere tomt.
De antar implisit at etterspørselsprocessen dekker hele forsynings-
kjedens leveringstid L_0 + L_i + R, for aa vaere "paa den sikre siden"
--- en vanlig industrinapraktisk tilnaerming ved planlegging uten
echelon-koordinering. Sentrallageret dimensjoneres ogsaa uavhengig
etter sin egen ledetid L_0 + R og aggregert etterspørsel.

For regionlager i (i=1..N), med daglig etterspørsel
D_{i,t} ~ N(mu_{d_i}, sigma_{d_i}^2) og effektiv ledetid L_0 + L_i + R:
  D_{L_0+L_i+R} ~ N((L_0+L_i+R)*mu_{d_i}, (L_0+L_i+R)*sigma_{d_i}^2)

Base-stock S_i^{uav} = mu + z_alpha * sigma.
Dette resulterer i at HVER region lagrer safety for sin egen andel av
L_0-usikkerheten --- en klassisk double-counting som Clark-Scarf fjerner.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

OUTPUT_DIR = Path(__file__).parent.parent / "output"

ALPHA = 0.95  # lokalt servicenivaa per lager


def load_params() -> dict:
    with open(OUTPUT_DIR / "step01_parameters.json", "r", encoding="utf-8") as f:
        return json.load(f)


def compute_independent_basestock(params: dict, alpha: float = ALPHA) -> dict:
    """Beregn base-stock for hvert lager isolert (konservativ naiv).

    Regionlagrene ser effektiv ledetid L_0 + L_i + R (ingen echelon
    tillit til sentralen). Sentralen ser sin egen L_0 + R.
    """
    z = float(norm.ppf(alpha))

    mu_d = np.array(params["mu_d"])
    sigma_d = np.array(params["sigma_d"])
    L_reg = np.array(params["L_reg"])
    L0 = params["L_sentral"]
    R = params["R"]

    # Regionlagre: "konservativ" naiv --- effektiv ledetid L_0 + L_i + R.
    # Antagelsen er at ved en tom sentrallager maa man vente hele
    # leverandør-ledetiden L_0 i tillegg, saa hele forsyningskjede-
    # ledetiden maa dekkes av lokalt sikkerhetslager.
    L_eff_reg = L0 + L_reg + R
    mu_LR_reg = L_eff_reg * mu_d
    sigma_LR_reg = np.sqrt(L_eff_reg * sigma_d ** 2)
    S_region = mu_LR_reg + z * sigma_LR_reg
    SS_region = z * sigma_LR_reg  # sikkerhetslager

    # Sentrallageret: ser aggregert etterspørsel over L_0 + R.
    # Legger paa sitt eget lag av sikkerhetsbuffer, uten hensyn
    # til regionenes safety (ingen koordinering).
    mu_LR_0 = (L0 + R) * params["mu_D0"]
    sigma_LR_0 = np.sqrt((L0 + R) * params["sigma_D0"] ** 2)
    S_0 = float(mu_LR_0 + z * sigma_LR_0)
    SS_0 = float(z * sigma_LR_0)

    return {
        "alpha": alpha,
        "z": z,
        "S_0": S_0,
        "SS_0": SS_0,
        "L_eff_reg": L_eff_reg.tolist(),
        "S_region": S_region.tolist(),
        "SS_region": SS_region.tolist(),
        "mu_LR_reg": mu_LR_reg.tolist(),
        "sigma_LR_reg": sigma_LR_reg.tolist(),
        "mu_LR_0": mu_LR_0,
        "sigma_LR_0": sigma_LR_0,
    }


def installation_stock_totals(params: dict, uav: dict) -> dict:
    """Forventet installasjonslager i stasjonaer drift.

    Under base-stock med periodisk gjennomgang R og faktisk ledetid
    L_eff_actual (som kan vaere annerledes enn den planlagte L_eff
    som ble brukt til dimensjonering) er:
      E[I_i] = S_i - L_eff_actual * mu_d_i - R * mu_d_i / 2 + SS_i
    Eller alternativt:
      E[I_i] = S_i - mu over faktisk pipeline + halv-syklus.
    For den konservative naive politikken er S_i satt til aa dekke
    L_0 + L_i + R men faktisk pipeline er bare L_i lang (fordi
    sentrallageret vanligvis leverer) --- saa overlapp mellom S_i og
    faktisk pipeline gir et gjennomsnittlig installasjonslager paa
    (L_0 + R/2) * mu_d_i + SS_i = "overstockeringen".
    """
    mu_d = np.array(params["mu_d"])
    mu_D0 = params["mu_D0"]
    R = params["R"]
    L_reg = np.array(params["L_reg"])
    L0 = params["L_sentral"]

    # Region: S_i = (L0+L_i+R)*mu + z*sigma. Faktisk pipeline = L_i*mu.
    # E[I_i] = S_i - L_i*mu_d - R*mu_d/2 = (L0 + R/2)*mu + SS
    SS_reg = np.array(uav["SS_region"])
    exp_inv_reg = (L0 + 0.5 * R) * mu_d + SS_reg

    # Sentralt: S_0 = (L_0+R)*mu_D0 + SS_0. Pipeline ~ L_0*mu_D0.
    # E[I_0] = S_0 - L_0*mu_D0 - R*mu_D0/2 = R*mu_D0/2 + SS_0
    exp_inv_0 = 0.5 * R * mu_D0 + uav["SS_0"]
    total = float(exp_inv_reg.sum() + exp_inv_0)
    return {
        "exp_inv_0": float(exp_inv_0),
        "exp_inv_region": exp_inv_reg.tolist(),
        "total_expected_inventory": total,
    }


def expected_holding_cost(params: dict, inv: dict) -> dict:
    """Forventet aarlig holdekostnad = sum_i h_install_i * E[I_i] * 365."""
    h_inst = np.array(params["h_install"])
    exp = [inv["exp_inv_0"]] + inv["exp_inv_region"]
    holding = np.array(exp) * h_inst * 365
    per_node = holding.tolist()
    total = float(holding.sum())
    return {
        "holding_per_node_NOK_per_aar": per_node,
        "total_holding_NOK_per_aar": total,
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 2: UAVHENGIG (s,S) - NAIV BASELINE")
    print("=" * 60)

    params = load_params()
    uav = compute_independent_basestock(params)
    inv = installation_stock_totals(params, uav)
    hc = expected_holding_cost(params, inv)

    print(f"\nServicenivaa: alpha = {uav['alpha']:.2f} (z = {uav['z']:.3f})")
    print(f"Sentralt   : S_0 = {uav['S_0']:.1f}, SS_0 = {uav['SS_0']:.1f}")
    print("Regioner  :")
    for i, region in enumerate(params["regioner"]):
        print(f"  {region:10s} S_{i+1} = {uav['S_region'][i]:7.1f},"
              f"  SS_{i+1} = {uav['SS_region'][i]:6.1f}")

    print(f"\nForventet lagernivaa totalt: "
          f"{inv['total_expected_inventory']:.1f} enheter")
    print(f"Forventet aarlig holdekostnad: "
          f"{hc['total_holding_NOK_per_aar']:,.0f} NOK")

    results = {
        "policy_name": "uavhengig_base_stock",
        **uav,
        **inv,
        **hc,
    }
    path = OUTPUT_DIR / "step02_uavhengig_ss.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {path}")
    print("\nFerdig med steg 2.\n")


if __name__ == "__main__":
    main()
