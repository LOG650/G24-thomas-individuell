"""
Steg 5: Mitigasjoner -- rangering av tiltak
===========================================
For hvert tiltak endrer vi baseline-nettverket og re-simulerer de verste
scenariene. Vi beregner:

  - Implementasjonskostnad (arlig, MNOK) -- estimert
  - Forventet kostnad under hele scenariokatalogen (MNOK)
  - Netto risikoreduksjon (MNOK) = kostnad(baseline) - kostnad(med tiltak)
  - Kost-nytte-forhold:  Nytte / Kostnad

Tiltak som vurderes:
  M1: Ekstra sikkerhetslager (+50 % pa alle lagre)
  M2: Alternativ leverandor (tredje leverandor fra Tyrkia)
  M3: Nearshoring (flytt 60 % av L1 til L2/Polen)
  M4: Dual sourcing (50/50 splitt istedenfor 70/30)
  M5: Fleksibel fabrikkapasitet (+25 % throughput pa kort varsel)
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    baseline_supply_chain, Supplier, OUTPUT_DIR,
)
from step02_baseline_simulering import ScenarioOverrides, run_simulation
from step03_scenarier import all_scenarios


# ============================================================
# Mitigasjonsstrategier
# ============================================================

# Hver mitigasjon er en funksjon (SupplyChain, ScenarioOverrides)
#   -> (modified_sc, modified_overrides, annual_cost_nok)
# annual_cost representerer tiltakets direkte implementasjonskostnad pr ar
# (lon, kontraktspremie, kapitalkostnad ekstra lager, osv.)


def m1_extra_safety_stock(sc, ov):
    """+50 % sikkerhetslager og +50 % fabrikk-SS. Holding-kostnaden er allerede
    fanget i simuleringens lagerhold-ledd, men vi legger til en arlig
    kapitalkostnad for det oppbundne lageret (eksplisitt)."""
    sc2 = replace(sc,
                  warehouses=[replace(w, safety_stock=w.safety_stock * 1.5)
                              for w in sc.warehouses],
                  factory=replace(sc.factory, safety_stock=sc.factory.safety_stock * 1.5))
    # Ekstra kapitalkostnad: 500 NOK/enh for ekstra SS over et ar
    extra_ss = 0.5 * (sum(w.safety_stock for w in sc.warehouses)
                      + sc.factory.safety_stock)
    annual = 500.0 * extra_ss  # kapitalbinding + ekstra lagerhold
    return sc2, ov, annual


def m2_alternativ_leverandor(sc, ov):
    """Ny leverandor L3-Tyrkia: kort ledetid, hoy palitelighet, hoy pris."""
    l3 = Supplier(
        name='L3-Tyrkia',
        lead_time_mean=20.0, lead_time_sd=4.0,
        reliability=0.98, capacity=700.0, unit_cost=58.0,
    )
    sc2 = replace(sc, suppliers=sc.suppliers + [l3])
    # 20 % av bestillingene rutes via L3 (splittene justeres i run_simulation
    # ved at vi gir en manuell override: vi simulerer L3 implicit via Polen).
    # Her modellerer vi dette som en hoyere gjennomsnittlig palitelighet +
    # ekstra kontraktskostnad pr ar.
    new_overrides = ScenarioOverrides(
        name=ov.name,
        supplier_overrides={k: (v[0], min(1.0, v[1] * 1.1), v[2])
                            for k, v in ov.supplier_overrides.items()},
        demand_mult=ov.demand_mult,
        factory_throughput_mult=ov.factory_throughput_mult,
        transport_delay_weeks=ov.transport_delay_weeks,
        supplier_outage_prob={k: v * 0.6 for k, v in ov.supplier_outage_prob.items()},
    )
    # Ekstra kontraktskostnad: 1,2 MNOK/ar (ready-to-go-kontrakt)
    return sc2, new_overrides, 1.2e6


def m3_nearshoring(sc, ov):
    """Flytt 60 % av L1 (Kina) til Polen-volum: reduser outage + LT eksponering."""
    # Modelleres ved a halvere leverandor-ledetid effekten og
    # halvere outage_prob pa L1
    new_overrides = ScenarioOverrides(
        name=ov.name,
        supplier_overrides={
            k: ((1 + (v[0] - 1) * 0.5) if k == 'L1-Kina' else v[0],
                v[1],
                v[2])
            for k, v in ov.supplier_overrides.items()
        },
        demand_mult=ov.demand_mult,
        factory_throughput_mult=ov.factory_throughput_mult,
        transport_delay_weeks=ov.transport_delay_weeks,
        supplier_outage_prob={k: (v * 0.4 if k == 'L1-Kina' else v)
                              for k, v in ov.supplier_outage_prob.items()},
    )
    # Ekstra arlig kostnad: hoyere enhetspris pa 60 % av Kina-volumet
    # (~17 NOK prisforskjell x ca. 2700 enh/uke x 60 % x 52 uker)
    annual = 17.0 * 0.60 * 2700.0 * 52.0   # ~ 1,43 MNOK
    return sc, new_overrides, annual


def m4_dual_sourcing(sc, ov):
    """Splitt 50/50 istedenfor 70/30 -- gir mer redundans, men hoyere pris."""
    # Implementeres via redusert avhengighet av L1: halverer outage_prob og
    # gir et marginalt lyft pa palitelighet
    new_overrides = ScenarioOverrides(
        name=ov.name,
        supplier_overrides={k: (v[0], min(1.0, v[1] * 1.03), v[2])
                            for k, v in ov.supplier_overrides.items()},
        demand_mult=ov.demand_mult,
        factory_throughput_mult=ov.factory_throughput_mult,
        transport_delay_weeks=ov.transport_delay_weeks,
        supplier_outage_prob={k: v * 0.5 for k, v in ov.supplier_outage_prob.items()},
    )
    # Ekstra kostnad: 20 % flyttes fra billig L1 til dyr L2
    # (0.20 x (62-45) x 4000 enh/uke x 52 uker)
    annual = 0.20 * (62.0 - 45.0) * 4000.0 * 52.0   # ~ 707 kNOK
    return sc, new_overrides, annual


def m5_fleksibel_fabrikk(sc, ov):
    """+25 % fabrikkapasitet pa kort varsel (overtidsavtale)."""
    # Overstyrer factory_throughput_mult oppover (men ikke over 1.0 hvis det
    # er lavere enn det). I baseline-modellen gir dette ingen ekstra effekt;
    # i scenarier der fabrikken er stressor (f.eks. S4) er det viktig.
    new_overrides = ScenarioOverrides(
        name=ov.name,
        supplier_overrides=ov.supplier_overrides,
        demand_mult=ov.demand_mult,
        factory_throughput_mult=min(1.25, ov.factory_throughput_mult * 1.25),
        transport_delay_weeks=ov.transport_delay_weeks,
        supplier_outage_prob=ov.supplier_outage_prob,
    )
    # Arlig beredskapskost: 2 MNOK
    return sc, new_overrides, 2.0e6


MITIGATIONS = [
    ('M1-Sikkerhetslager+50%', m1_extra_safety_stock),
    ('M2-Alternativ-leverandor', m2_alternativ_leverandor),
    ('M3-Nearshoring', m3_nearshoring),
    ('M4-Dual-sourcing', m4_dual_sourcing),
    ('M5-Fleksibel-fabrikk', m5_fleksibel_fabrikk),
]


# ============================================================
# Simulering pr mitigasjon
# ============================================================

def evaluate_mitigation(mit_fn, scenarios: list[ScenarioOverrides],
                        n_reps: int = 15) -> dict:
    """Kjor baseline + alle scenarier med mitigasjonen pa plass."""
    sc_base = baseline_supply_chain()

    # 1. Baseline drift (ingen forstyrrelse) med tiltaket
    sc_mit, _, annual_cost = mit_fn(sc_base, ScenarioOverrides(name='baseline'))
    baseline_costs = []
    for rep in range(n_reps):
        res = run_simulation(sc_mit, overrides=ScenarioOverrides(name='baseline'),
                             seed=3000 + rep)
        baseline_costs.append(res['total_cost'])

    # 2. Hver forstyrrelse med tiltaket
    scen_results = {}
    for ov in scenarios:
        sc_mit, ov_mit, _ = mit_fn(sc_base, ov)
        costs = []
        sls = []
        for rep in range(n_reps):
            res = run_simulation(sc_mit, overrides=ov_mit, seed=3000 + rep)
            costs.append(res['total_cost'])
            sls.append(res['service_level'])
        scen_results[ov.name] = {
            'cost_mean': float(np.mean(costs)),
            'service_level_mean': float(np.mean(sls)),
        }

    return {
        'annual_cost': annual_cost,
        'baseline_cost_mean': float(np.mean(baseline_costs)),
        'scenario_results': scen_results,
    }


def run_all_mitigations(n_reps: int = 15) -> dict:
    scens = all_scenarios()
    out = {}

    # Forst: baseline (ingen tiltak)
    print("  Evaluerer status quo ...")
    sc = baseline_supply_chain()
    base_rows = {}
    base_base = []
    for rep in range(n_reps):
        res = run_simulation(sc, overrides=ScenarioOverrides(name='baseline'),
                             seed=3000 + rep)
        base_base.append(res['total_cost'])
    for ov in scens:
        costs = []
        sls = []
        for rep in range(n_reps):
            res = run_simulation(sc, overrides=ov, seed=3000 + rep)
            costs.append(res['total_cost'])
            sls.append(res['service_level'])
        base_rows[ov.name] = {
            'cost_mean': float(np.mean(costs)),
            'service_level_mean': float(np.mean(sls)),
        }
    out['Status-quo'] = {
        'annual_cost': 0.0,
        'baseline_cost_mean': float(np.mean(base_base)),
        'scenario_results': base_rows,
    }

    # Hver mitigasjon
    for name, fn in MITIGATIONS:
        print(f"  Evaluerer {name} ...")
        out[name] = evaluate_mitigation(fn, scens, n_reps)

    return out


# ============================================================
# Analyse av risikonytte
# ============================================================

def analyze_cost_benefit(mit_results: dict,
                         scenario_probs: dict[str, float] | None = None) -> list[dict]:
    """Beregn forventet arlig risikokostnad per tiltak.
    scenario_probs = arlig sannsynlighet for at hvert scenario intreffer.
    """
    if scenario_probs is None:
        # Default: sjeldne store hendelser, men ikke forsvinnende sma
        scenario_probs = {
            'S1-Pandemi': 0.10,
            'S2-Havneblokkade': 0.15,
            'S3-Leverandorkonkurs': 0.08,
            'S4-Naturkatastrofe': 0.05,
            'S5-Cyberangrep': 0.20,
        }
    p_normal = max(0.0, 1.0 - sum(scenario_probs.values()))

    status_quo = mit_results['Status-quo']
    sq_expected = (p_normal * status_quo['baseline_cost_mean']
                   + sum(scenario_probs[s] * status_quo['scenario_results'][s]['cost_mean']
                         for s in scenario_probs))

    rows = []
    for name, m in mit_results.items():
        expected_disruption_cost = (
            p_normal * m['baseline_cost_mean']
            + sum(scenario_probs[s] * m['scenario_results'][s]['cost_mean']
                  for s in scenario_probs)
        )
        risk_reduction = sq_expected - expected_disruption_cost
        annual_cost = m['annual_cost']
        net_benefit = risk_reduction - annual_cost
        ratio = (risk_reduction / annual_cost) if annual_cost > 0 else float('inf')
        rows.append({
            'mitigation': name,
            'annual_impl_cost': annual_cost,
            'expected_total_cost': expected_disruption_cost,
            'risk_reduction': risk_reduction,
            'net_benefit': net_benefit,
            'cost_benefit_ratio': ratio,
        })

    return rows


# ============================================================
# Visualisering
# ============================================================

FILLS = ['#CBD5E1', '#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']
STROKES = ['#556270', '#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']


def plot_mitigation_benefit(cb: list[dict], output_path: Path) -> None:
    """To panels: (a) forventet kostnad pr tiltak, (b) netto nytte."""
    names = [r['mitigation'].replace('-', '\n', 1) for r in cb]
    exp_cost = [r['expected_total_cost'] / 1e6 for r in cb]
    impl_cost = [r['annual_impl_cost'] / 1e6 for r in cb]
    net_benefit = [r['net_benefit'] / 1e6 for r in cb]
    risk_red = [r['risk_reduction'] / 1e6 for r in cb]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    x = np.arange(len(cb))
    width = 0.4
    ax.bar(x - width / 2, exp_cost, width, label='Forventet total kostnad',
           color=FILLS, edgecolor=STROKES, linewidth=1.4, alpha=0.9)
    ax.bar(x + width / 2, impl_cost, width, label='Implementasjonskostnad',
           color='#F4F7FB', edgecolor='#556270', linewidth=1.2, alpha=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel('MNOK / ar', fontsize=11)
    ax.set_title('(a) Forventet kostnad vs implementasjonskostnad',
                 fontsize=11, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, axis='y', alpha=0.3)

    ax = axes[1]
    colors = ['#307453' if nb > 0 else '#961D1C' for nb in net_benefit]
    bars = ax.bar(names, net_benefit, color=colors, edgecolor='#1F2933',
                  linewidth=1.4, alpha=0.9)
    for bar, v, rr in zip(bars, net_benefit, risk_red):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + (0.3 if v >= 0 else -0.6),
                f'{v:+.1f}', ha='center',
                va='bottom' if v >= 0 else 'top',
                fontsize=9, fontweight='bold')
    ax.axhline(0, color='#1F2933', lw=1.0)
    ax.set_ylabel('Netto arlig nytte (MNOK)', fontsize=11)
    ax.set_title('(b) Netto nytte = risikoreduksjon $-$ implementasjonskostnad',
                 fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    plt.setp(ax.get_xticklabels(), fontsize=8)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


# ============================================================
# Hovedfunksjon
# ============================================================

def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 5: MITIGASJONER")
    print("=" * 60)

    n_reps = 15
    results = run_all_mitigations(n_reps=n_reps)
    cb = analyze_cost_benefit(results)

    print(f"\n{'Tiltak':28s} {'ImplC (MNOK)':>13s} {'ExpC (MNOK)':>13s} "
          f"{'RR (MNOK)':>11s} {'NB (MNOK)':>11s} {'B/C':>7s}")
    for r in cb:
        ratio = r['cost_benefit_ratio']
        ratio_str = 'inf' if not np.isfinite(ratio) else f'{ratio:.2f}'
        print(f"{r['mitigation']:28s} "
              f"{r['annual_impl_cost']/1e6:>13.2f} "
              f"{r['expected_total_cost']/1e6:>13.2f} "
              f"{r['risk_reduction']/1e6:>11.2f} "
              f"{r['net_benefit']/1e6:>11.2f} "
              f"{ratio_str:>7s}")

    with open(OUTPUT_DIR / 'step05_mitigations.json', 'w', encoding='utf-8') as f:
        json.dump({
            'simulation_results': results,
            'cost_benefit': cb,
        }, f, indent=2, ensure_ascii=False, default=float)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step05_mitigations.json'}")

    plot_mitigation_benefit(cb, OUTPUT_DIR / 'st_mitigation_benefit.png')


if __name__ == '__main__':
    main()
