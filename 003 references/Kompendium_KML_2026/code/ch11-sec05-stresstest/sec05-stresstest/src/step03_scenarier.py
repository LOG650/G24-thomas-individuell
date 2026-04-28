"""
Steg 3: Scenariokatalog
=======================
Definerer fem forhandsbestemte forstyrrelsesscenarier som alle bruker
ScenarioOverrides-strukturen:

  S1: Pandemi        -- lavere leverandorpalitelighet + demand shock (+30 %)
  S2: Havneblokkade  -- doblet ledetid for Kina-leverandoren, -50 % kapasitet
  S3: Leverandorkonkurs -- L1 (Kina) helt ute + demand flat
  S4: Naturkatastrofe -- fabrikk -40 % throughput i 10 uker (modellert som
                         hel-ars gjennomsnitt) + transport +2 uker
  S5: Cyberangrep    -- alle leverandorer -70 % palitelighet + oppsettskostn. hoy

Verktoyene her gjenbrukes av steg 4-5.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import baseline_supply_chain, OUTPUT_DIR
from step02_baseline_simulering import ScenarioOverrides


# ============================================================
# Scenariodefinisjoner
# ============================================================

def scenario_pandemi() -> ScenarioOverrides:
    """Global pandemi: hamstring (+30 % demand) og svikt hos leverandorer."""
    return ScenarioOverrides(
        name='S1-Pandemi',
        supplier_overrides={
            'L1-Kina': (1.4, 0.75, 0.6),      # ledetid +40 %, rel -25 %, kapasitet -40 %
            'L2-Polen': (1.2, 0.90, 0.8),
        },
        demand_mult={
            'Troms': 1.30, 'Nordland': 1.30, 'Trondelag': 1.30,
            'Vestland': 1.30, 'Oslo-Viken': 1.30,
        },
    )


def scenario_havneblokkade() -> ScenarioOverrides:
    """Blokkade av Suez/Asia-ruten: kun L1 rammes hardt."""
    return ScenarioOverrides(
        name='S2-Havneblokkade',
        supplier_overrides={
            'L1-Kina': (2.0, 0.85, 0.5),      # ledetid x2, kapasitet -50 %
        },
        transport_delay_weeks=1,
    )


def scenario_leverandorkonkurs() -> ScenarioOverrides:
    """L1 (Kina) konkurs -- fullt utslag pa sannsynlighet for levering."""
    return ScenarioOverrides(
        name='S3-Leverandorkonkurs',
        supplier_outage_prob={'L1-Kina': 1.0},   # L1 er helt ute av drift
    )


def scenario_naturkatastrofe() -> ScenarioOverrides:
    """Flom/brann i Oslo-fabrikken + regionale transportproblemer."""
    return ScenarioOverrides(
        name='S4-Naturkatastrofe',
        factory_throughput_mult=0.7,
        transport_delay_weeks=2,
    )


def scenario_cyberangrep() -> ScenarioOverrides:
    """IT-angrep forstyrrer bestillings-/kommunikasjonssystemer."""
    return ScenarioOverrides(
        name='S5-Cyberangrep',
        supplier_overrides={
            'L1-Kina': (1.1, 0.40, 1.0),      # palitelighet -60 %
            'L2-Polen': (1.1, 0.40, 1.0),
        },
    )


def all_scenarios() -> list[ScenarioOverrides]:
    return [
        scenario_pandemi(),
        scenario_havneblokkade(),
        scenario_leverandorkonkurs(),
        scenario_naturkatastrofe(),
        scenario_cyberangrep(),
    ]


# ============================================================
# Visualisering
# ============================================================

def plot_scenario_signatures(scenarios: list[ScenarioOverrides], output_path: Path) -> None:
    """Radarlignende oversikt over hvilke dimensjoner hvert scenario pavirker."""
    # Fem dimensjoner: Leverandor-LT, Leverandor-rel, Leverandor-kapasitet,
    # Fabrikk-kapasitet, Etterspursel, Transport-forsinkelse
    dims = ['Leverandor\nledetid', 'Leverandor\npalitelighet',
            'Leverandor\nkapasitet', 'Fabrikk\nkapasitet',
            'Etterspursel\nsjokk', 'Transport\nforsinkelse']

    def score(ov: ScenarioOverrides) -> list[float]:
        # normaliser alle til 0-1 skala (0 = ingen effekt, 1 = stor stressor)
        lt_mults = [m for (m, _, _) in ov.supplier_overrides.values()]
        rel_mults = [m for (_, m, _) in ov.supplier_overrides.values()]
        cap_mults = [m for (_, _, m) in ov.supplier_overrides.values()]
        lt_score = max([max(0.0, m - 1.0) / 1.5 for m in lt_mults] + [0.0])
        rel_score = max([max(0.0, 1.0 - m) for m in rel_mults] + [0.0])
        if ov.supplier_outage_prob:
            rel_score = max(rel_score, max(ov.supplier_outage_prob.values()))
        cap_score = max([max(0.0, 1.0 - m) for m in cap_mults] + [0.0])
        fac_score = max(0.0, 1.0 - ov.factory_throughput_mult)
        dem_mults = list(ov.demand_mult.values())
        dem_score = max([max(0.0, m - 1.0) / 1.0 for m in dem_mults] + [0.0])
        trans_score = min(1.0, ov.transport_delay_weeks / 3.0)
        return [lt_score, rel_score, cap_score, fac_score, dem_score, trans_score]

    fills = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']
    strokes = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']

    fig, ax = plt.subplots(figsize=(11, 5))
    width = 0.14
    x = np.arange(len(dims))
    for i, sc in enumerate(scenarios):
        scores = score(sc)
        offset = (i - 2) * width
        ax.bar(x + offset, scores, width=width,
               color=fills[i % len(fills)], edgecolor=strokes[i % len(strokes)],
               linewidth=1.2, label=sc.name, alpha=0.9)

    ax.set_xticks(x)
    ax.set_xticklabels(dims, fontsize=9)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel('Stress-intensitet (0-1)', fontsize=11)
    ax.set_title('Scenariosignaturer: hvilke dimensjoner rammes?',
                 fontsize=12, fontweight='bold')
    ax.legend(fontsize=9, loc='upper right', ncol=5)
    ax.grid(True, axis='y', alpha=0.3)
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
    print("STEG 3: SCENARIER")
    print("=" * 60)

    scens = all_scenarios()
    print(f"Antall scenarier definert: {len(scens)}\n")

    signatures = {}
    for sc in scens:
        print(f"  {sc.name}:")
        print(f"    supplier_overrides   = {sc.supplier_overrides}")
        print(f"    demand_mult          = {sc.demand_mult}")
        print(f"    factory_tp_mult      = {sc.factory_throughput_mult}")
        print(f"    transport_delay      = {sc.transport_delay_weeks} uker")
        print(f"    supplier_outage_prob = {sc.supplier_outage_prob}")
        signatures[sc.name] = {
            'supplier_overrides': sc.supplier_overrides,
            'demand_mult': sc.demand_mult,
            'factory_throughput_mult': sc.factory_throughput_mult,
            'transport_delay_weeks': sc.transport_delay_weeks,
            'supplier_outage_prob': sc.supplier_outage_prob,
        }

    with open(OUTPUT_DIR / 'step03_scenarios.json', 'w', encoding='utf-8') as f:
        json.dump(signatures, f, indent=2, ensure_ascii=False)
    print(f"\nScenariokatalog lagret: {OUTPUT_DIR / 'step03_scenarios.json'}")

    plot_scenario_signatures(scens, OUTPUT_DIR / 'st_scenario_signatures.png')


if __name__ == '__main__':
    main()
