"""
Steg 3: Clark-Scarf echelon base-stock
======================================
Bruker den klassiske Clark-Scarf dekomponeringen for et to-trinns
distribusjonssystem med aggregert behandling av downstream-lagre.

NYAKTIG SETUP:
* Ett produkt, ett sentrallager (node 0) og N regionlagre (node 1..N).
* Etterspørsel per region er iid normal per dag.
* Periodisk gjennomgang R (= 1 dag).
* Ledetider: L_0 fra leverandor til sentrallager; L_i fra sentrallager
  til region i.

ECHELON BEHOLDNING (stasjonær):
  I^e_i = installasjonslager i (og i transport til) i, pluss alt under i.
For region i er I^e_i = I_i (fordi det ikke finnes noder under).
For sentrallageret er I^e_0 = I_0 + sum_j (I_j + transit_j) + transit_0.

NEWSVENDOR PER ECHELON (Clark-Scarf, allokasjonsantakelse):
Regionlager i:
  S^e_i  = mu_{i,L_i+R} + z_i * sigma_{i,L_i+R}
  z_i    = Phi^{-1}(alpha_i)
  der alpha_i = b / (b + h^e_i) (newsvendor critical ratio)

Sentrallager (echelon) - DECOMPOSERING:
  Aggregert etterspørsel D_0 = sum_i D_i.
  Den eksakte Clark-Scarf-dekomponeringen induserer en indusert
  backorder-kostnad beta_0 paa sentralnivaa (penalty for at
  regionlagrene ikke kan bli refylt umiddelbart). For identiske
  produkter i et arborescent distribusjonssystem er det en vanlig
  praktisk approksimasjon aa bruke
        alpha_0 = b_0_eff / (b_0_eff + h^e_0)
  med b_0_eff = b, der b er endeligkonsument-backorderkostnaden.
  Da blir
        S^e_0 = mu_{0,L_0+R} + z_0 * sigma_{0,L_0+R},
  og installasjons-S for sentralen utledes fra at
  S_0^install = S^e_0 - sum_i E[I^e_i]-tilstand i stasjonær drift.
  Siden E[I^e_i] i stasjonær drift er mu_{L_i+R,i} + z_i*sigma_{L_i+R,i}
  er en enkel og sikker regel:
        S_0^install = max(S^e_0 - sum_i S^e_i, 0).

Denne formuleringen gir installasjonslager ved sentralen som bare
kompenserer for den ekstra usikkerheten over L_0 + R dager utover det
som regionlagrene allerede buffrer --- precis poenget i Clark-Scarf.

I denne implementasjonen bruker vi en mer praktisk formulering der
sentralbase-stocken er dimensjonert direkte som en sikkerhetsbuffer
for L_0 dager aggregert etterspørsel --- tilsvarende hva Clark-Scarf
etter allokasjon gir naar regionene har riktige nivaer:
        S_0^install = (L_0 + R) * mu_D0 + z_central * sigma_LR_0
Dette tolkes som at sentrallageret skal kunne dekke alle utgaaende
bestillinger i L_0+R dager pluss en sikkerhetsbuffer.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy.stats import norm

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def load_params() -> dict:
    with open(OUTPUT_DIR / "step01_parameters.json", "r", encoding="utf-8") as f:
        return json.load(f)


def critical_ratio(b: float, h: float) -> float:
    """Newsvendor: alpha = b / (b + h)."""
    return b / (b + h)


def clark_scarf_levels(params: dict) -> dict:
    """Beregn echelon base-stock S^e_i og S^e_0."""
    mu_d = np.array(params["mu_d"])
    sigma_d = np.array(params["sigma_d"])
    L_reg = np.array(params["L_reg"])
    L0 = params["L_sentral"]
    R = params["R"]
    b = params["b_region"]
    h_ech = np.array(params["h_ech"])  # lengde N+1

    N = params["N"]

    # Region-echelon
    alpha_reg = np.array([critical_ratio(b, h_ech[i + 1]) for i in range(N)])
    z_reg = norm.ppf(alpha_reg)
    mu_LR_reg = (L_reg + R) * mu_d
    sigma_LR_reg = np.sqrt((L_reg + R) * sigma_d ** 2)
    S_e_reg = mu_LR_reg + z_reg * sigma_LR_reg

    # Sentrallager-echelon (aggregert)
    # Bruk effektiv "downstream"-backorder-kostnad = b (samme som regionalt).
    # For h^e_0 bruker vi echelon-holdekostnaden for sentralt,
    # som er installasjonsholdekost minus parent (leverandør=0).
    alpha_0 = critical_ratio(b, h_ech[0])
    z_0 = float(norm.ppf(alpha_0))
    mu_D0 = params["mu_D0"]
    sigma_D0 = params["sigma_D0"]
    mu_LR_0 = (L0 + R) * mu_D0
    sigma_LR_0 = np.sqrt((L0 + R) * sigma_D0 ** 2)
    S_e_0 = float(mu_LR_0 + z_0 * sigma_LR_0)

    return {
        "alpha_region": alpha_reg.tolist(),
        "z_region": z_reg.tolist(),
        "mu_LR_region": mu_LR_reg.tolist(),
        "sigma_LR_region": sigma_LR_reg.tolist(),
        "S_e_region": S_e_reg.tolist(),
        "alpha_0": float(alpha_0),
        "z_0": z_0,
        "mu_LR_0": float(mu_LR_0),
        "sigma_LR_0": float(sigma_LR_0),
        "S_e_0": S_e_0,
    }


def implied_installation_basestock(params: dict, cs: dict) -> dict:
    """Konverter echelon S^e_i til installasjons-S_i for
    implementering.

    For region i er S^e_i = S_i (ingen noder under),
    saa S_install_region[i] = S^e_region[i].

    For sentrallageret er det mer subtilt. Installasjonslager ved
    sentralen skal dekke dekke L_0 + R dagers aggregert etterspørsel
    pluss sikkerhetsbuffer for usikkerhet over den samme perioden.
    Vi bruker:
        S_0_install = (L_0 + R) * mu_D0 + z_0 * sigma_LR_0
    som svarer til klassisk base-stock for sentrallagerets EGNE
    usikkerhet, og som er feasible i en daglig
    gjennomgangssimulering.

    Forskjellen mot naive (s,S) ligger i hvordan z_0 bestemmes:
    Clark-Scarf bruker newsvendor-kritisk rate z_0 = Phi^{-1}(b/(b+h_0)),
    mens uavhengig (s,S) bruker et felles flatt servicekrav
    z = Phi^{-1}(alpha).
    """
    S_e_reg = np.array(cs["S_e_region"])
    S_install_region = S_e_reg.copy()
    # Installasjons-S for sentralen basert pa CS z_0
    S_install_0 = cs["mu_LR_0"] + cs["z_0"] * cs["sigma_LR_0"]
    return {
        "S_install_region": S_install_region.tolist(),
        "S_install_0": float(S_install_0),
    }


def expected_holding_cost(params: dict, cs: dict) -> dict:
    """Forventet aarlig holdekostnad i stasjonær drift.

    For Clark-Scarf med S dimensjonert for L_i+R og faktisk pipeline
    bare L_i: E[I_i] = R/2 * mu_d + SS_i.
    Sentralen: E[I_0] = R/2 * mu_D0 + SS_0.
    """
    R = params["R"]
    mu_d = np.array(params["mu_d"])
    SS_reg = np.array(cs["z_region"]) * np.array(cs["sigma_LR_region"])
    exp_inv_reg = 0.5 * R * mu_d + SS_reg
    # Sentralt
    SS0 = cs["z_0"] * cs["sigma_LR_0"]
    exp_inv_0 = 0.5 * R * params["mu_D0"] + SS0

    h_inst = np.array(params["h_install"])
    hc = np.concatenate([[exp_inv_0], exp_inv_reg]) * h_inst * 365
    return {
        "SS_region": SS_reg.tolist(),
        "SS_0": float(SS0),
        "exp_inv_0": float(exp_inv_0),
        "exp_inv_region": exp_inv_reg.tolist(),
        "holding_per_node_NOK_per_aar": hc.tolist(),
        "total_holding_NOK_per_aar": float(hc.sum()),
    }


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 3: CLARK-SCARF ECHELON BASE-STOCK")
    print("=" * 60)

    params = load_params()
    cs = clark_scarf_levels(params)
    iS = implied_installation_basestock(params, cs)
    hc = expected_holding_cost(params, cs)

    print(f"\nBackorder-kostnad b = {params['b_region']:.1f} NOK/enhet")
    print("Echelon holdekostnader h^e_i (NOK/enhet/dag):",
          [f"{h:.3f}" for h in params["h_ech"]])

    print(f"\nSentrallager (echelon):")
    print(f"  alpha_0 = {cs['alpha_0']:.4f},  z_0 = {cs['z_0']:.3f}")
    print(f"  mu_LR_0 = {cs['mu_LR_0']:.1f}, sigma_LR_0 = {cs['sigma_LR_0']:.2f}")
    print(f"  S^e_0 = {cs['S_e_0']:.1f}")
    print(f"  Installasjons-S_0 = {iS['S_install_0']:.1f}")

    print("\nRegionlagre (echelon):")
    for i, region in enumerate(params["regioner"]):
        print(f"  {region:10s}"
              f"  alpha_{i+1} = {cs['alpha_region'][i]:.4f}"
              f"  z_{i+1} = {cs['z_region'][i]:.3f}"
              f"  S^e_{i+1} = {cs['S_e_region'][i]:7.1f}"
              f"  SS_{i+1} = {hc['SS_region'][i]:5.1f}")

    print(f"\nForventet lagernivaa totalt: "
          f"{hc['exp_inv_0'] + sum(hc['exp_inv_region']):.1f} enheter")
    print(f"Forventet aarlig holdekostnad: "
          f"{hc['total_holding_NOK_per_aar']:,.0f} NOK")

    results = {
        "policy_name": "clark_scarf_echelon",
        **cs,
        **iS,
        **hc,
    }
    path = OUTPUT_DIR / "step03_clark_scarf.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"\nResultat lagret: {path}")
    print("\nFerdig med steg 3.\n")


if __name__ == "__main__":
    main()
