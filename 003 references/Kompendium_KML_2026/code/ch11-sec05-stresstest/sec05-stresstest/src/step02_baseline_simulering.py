"""
Steg 2: Baseline-simulering
===========================
Implementerer en enkel ukesbasert forsyningskjede-simulator med:
  - stokastisk etterspursel pr kunderegion
  - stokastisk ledetid pr leverandor
  - sannsynlighet for leveransesvikt
  - (s, S)-politikk pa hvert regionlager

KPI-er:
  - Service level (Type 2 / fill rate) totalt og pr region
  - Totalkostnad: lagerhold + tapte salg + haste-transport + oppsett
  - Gjennomsnittlig leveringsforsinkelse (uker)

Samme simulator brukes av steg 3-5 via parameter-overrides.
"""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    SupplyChain, baseline_supply_chain, OUTPUT_DIR, _sc_to_dict,
)


# ============================================================
# Parametere som scenarier kan overstyre
# ============================================================

@dataclass
class ScenarioOverrides:
    """Alle felter er valgfrie multiplikatorer eller forskyvninger."""
    name: str = 'baseline'
    # Per leverandor: (lead_time_mult, reliability_mult, capacity_mult)
    supplier_overrides: dict[str, tuple[float, float, float]] = field(default_factory=dict)
    # Per kunderegion: etterspurselsmultiplikator (kan vaere > 1)
    demand_mult: dict[str, float] = field(default_factory=dict)
    # Fabrikkens throughput-multiplikator
    factory_throughput_mult: float = 1.0
    # Transportforsinkelse i uker pa all distribusjon (fabrikk -> lager)
    transport_delay_weeks: int = 0
    # Per leverandor: sannsynlighet for helt "ute av drift" per uke (katastrofe)
    supplier_outage_prob: dict[str, float] = field(default_factory=dict)


# ============================================================
# Selve simulatoren
# ============================================================

def run_simulation(sc: SupplyChain,
                   overrides: ScenarioOverrides | None = None,
                   seed: int | None = None) -> dict:
    """Ukesbasert simulering av forsyningskjeden over sc.weeks uker."""
    overrides = overrides or ScenarioOverrides()
    rng = np.random.default_rng(seed if seed is not None else sc.seed)

    weeks = sc.weeks
    customers = sc.customers
    warehouses = sc.warehouses
    suppliers = sc.suppliers
    factory = sc.factory
    costs = sc.costs

    # Total ukentlig etterspursel -- brukes til fabrikkens (s,S) og initial stock
    total_weekly_demand = sum(c.demand_mean for c in customers)

    # Initialiser tilstandsvariabler (velg generose startverdier slik at
    # baseline er sunn fra dag 1)
    wh_inventory = {w.name: min(2.0 * w.safety_stock, w.capacity * 0.9)
                    for w in warehouses}
    factory_stock = 6 * total_weekly_demand
    # Ordre i transit fra leverandor (liste med (arrival_week, qty, supplier))
    in_transit_sup: list[tuple[int, float, str]] = []
    # Ordre i transit fra fabrikk -> lager (arrival_week, qty, warehouse)
    in_transit_wh: list[tuple[int, float, str]] = []

    # Maal
    demand_log = np.zeros(weeks)
    shortfall_log = np.zeros(weeks)
    shipped_log = np.zeros(weeks)
    delivery_delay_log = []       # forsinkelse (uker) for ordrer som til slutt ble levert
    holding_cost_total = 0.0
    lost_sale_cost_total = 0.0
    expedite_cost_total = 0.0
    setup_cost_total = 0.0

    # Pr-region maal
    per_region_demand = {c.name: 0.0 for c in customers}
    per_region_short = {c.name: 0.0 for c in customers}

    # Bestillingsparametre (enkel (s,S) med S = 2.5 * SS, s = SS)
    s_levels = {w.name: w.safety_stock for w in warehouses}
    S_levels = {w.name: min(2.5 * w.safety_stock, w.capacity * 0.95)
                for w in warehouses}
    # Fabrikkens bestilling fra leverandor: vi tar hoyde for at den totale
    # fyllingen (sum over lagre) skal kunne dekke flere ukers etterspursel
    # under lang ledetid. Setter storre (s,S)-verdier enn for fabrikken.
    s_fac = 4 * total_weekly_demand           # ca 4 ukers etterspursel
    S_fac = 8 * total_weekly_demand           # opptil 8 uker

    # Leverandor-preferanse: rutebytt mellom L1 (billig men treig), L2 (rask, dyr)
    # og eventuelle ekstra leverandorer. Bruker en 70/30-splitt i baseline.
    # Er det flere enn to leverandorer, tar de ekstra en andel av L1.
    if len(suppliers) == 2:
        sup_split = {suppliers[0].name: 0.70, suppliers[1].name: 0.30}
    else:
        # Gi L1 40 %, L2 30 %, og fordel resten likt pa de resterende
        rest = 1.0 - 0.70
        n_extra = len(suppliers) - 1
        sup_split = {suppliers[0].name: 0.70}
        per_rest = rest / n_extra
        for sup in suppliers[1:]:
            sup_split[sup.name] = per_rest

    for t in range(weeks):
        # ---- 1. Ankomster fra leverandor (til fabrikk) ----
        new_in_transit_sup = []
        for arr_w, qty, sname in in_transit_sup:
            if arr_w <= t:
                factory_stock += qty
            else:
                new_in_transit_sup.append((arr_w, qty, sname))
        in_transit_sup = new_in_transit_sup

        # ---- 2. Ankomster til lager (fra fabrikk) ----
        new_in_transit_wh = []
        for arr_w, qty, wname in in_transit_wh:
            if arr_w <= t:
                wh_inventory[wname] += qty
            else:
                new_in_transit_wh.append((arr_w, qty, wname))
        in_transit_wh = new_in_transit_wh

        # ---- 3. Trek etterspursel ----
        region_demands = {}
        for c in customers:
            mult = overrides.demand_mult.get(c.name, 1.0)
            mu = c.demand_mean * mult
            sigma = c.demand_sd * mult
            d = max(0.0, rng.normal(mu, sigma))
            region_demands[c.name] = d
            demand_log[t] += d
            per_region_demand[c.name] += d

        # ---- 4. Oppfyll etterspursel fra regionlager ----
        for c in customers:
            wname = c.warehouse
            d = region_demands[c.name]
            shipped = min(wh_inventory[wname], d)
            wh_inventory[wname] -= shipped
            shipped_log[t] += shipped
            short = d - shipped
            shortfall_log[t] += short
            per_region_short[c.name] += short
            # Tapte salg (Type 2-servicenivaa: backordre antas tapt etter 1 uke)
            if short > 0:
                lost_sale_cost_total += short * costs.lost_sale_cost
                # Bruk haste-levering for ca. halvparten av underskuddet om mulig
                rescue = min(short * 0.5, factory_stock)
                if rescue > 0:
                    factory_stock -= rescue
                    shipped_log[t] += rescue
                    shortfall_log[t] -= rescue
                    per_region_short[c.name] -= rescue
                    lost_sale_cost_total -= rescue * costs.lost_sale_cost
                    expedite_cost_total += rescue * costs.expedite_cost
                    delivery_delay_log.append(1.0)  # en ukes forsinkelse
            # Fyll kapasitet i lager (ikke over)
            wh_inventory[wname] = min(wh_inventory[wname], _wh_cap(warehouses, wname))

        # ---- 5. Lagerhold-kostnader (pa slutten av uken) ----
        for w in warehouses:
            holding_cost_total += max(0.0, wh_inventory[w.name]) * w.holding_cost
        holding_cost_total += max(0.0, factory_stock) * factory.holding_cost

        # ---- 6. Fabrikk forsoker a produsere / skipe til lagrene ----
        factory_tp = factory.throughput * overrides.factory_throughput_mult
        for w in warehouses:
            target = S_levels[w.name]
            if wh_inventory[w.name] < s_levels[w.name]:
                need = target - wh_inventory[w.name]
                take = min(need, factory_stock, factory_tp)
                if take > 0:
                    factory_stock -= take
                    factory_tp -= take
                    delay = 1 + overrides.transport_delay_weeks
                    in_transit_wh.append((t + delay, take, w.name))
                    setup_cost_total += costs.setup_cost * 0.3  # delvis oppsett
            if factory_tp <= 0:
                break

        # ---- 7. Fabrikk bestiller fra leverandor ----
        if factory_stock < s_fac:
            order_qty = S_fac - factory_stock
            for sup in suppliers:
                mult_lt, mult_rel, mult_cap = overrides.supplier_overrides.get(
                    sup.name, (1.0, 1.0, 1.0))
                outage_p = overrides.supplier_outage_prob.get(sup.name, 0.0)
                if rng.random() < outage_p:
                    continue  # leverandor ute av drift denne uken
                if rng.random() > sup.reliability * mult_rel:
                    continue  # ordrefeil
                share = sup_split[sup.name] * order_qty
                cap = sup.capacity * mult_cap
                q = min(share, cap)
                if q <= 0:
                    continue
                lt_mean = sup.lead_time_mean * mult_lt / 7.0  # uker
                lt_sd = sup.lead_time_sd * mult_lt / 7.0
                lt = max(1, int(round(rng.normal(lt_mean, lt_sd))))
                in_transit_sup.append((t + lt, q, sup.name))
                setup_cost_total += costs.setup_cost

    # ---- Summer KPI-er ----
    total_demand = float(demand_log.sum())
    total_short = float(shortfall_log.sum())
    total_shipped = float(shipped_log.sum())
    service_level = 1.0 - (total_short / total_demand) if total_demand > 0 else 1.0
    mean_delay = float(np.mean(delivery_delay_log)) if delivery_delay_log else 0.0
    total_cost = (holding_cost_total + lost_sale_cost_total +
                  expedite_cost_total + setup_cost_total)

    per_region_sl = {
        c.name: 1.0 - (per_region_short[c.name] / per_region_demand[c.name])
        if per_region_demand[c.name] > 0 else 1.0
        for c in customers
    }

    return {
        'scenario': overrides.name,
        'weeks': weeks,
        'total_demand': total_demand,
        'total_shortfall': total_short,
        'total_shipped': total_shipped,
        'service_level': service_level,
        'mean_delivery_delay_weeks': mean_delay,
        'total_cost': total_cost,
        'cost_breakdown': {
            'holding': holding_cost_total,
            'lost_sale': lost_sale_cost_total,
            'expedite': expedite_cost_total,
            'setup': setup_cost_total,
        },
        'per_region_service_level': per_region_sl,
        'per_region_demand': per_region_demand,
        'per_region_shortfall': per_region_short,
        'demand_by_week': demand_log.tolist(),
        'shortfall_by_week': shortfall_log.tolist(),
        'shipped_by_week': shipped_log.tolist(),
    }


def _wh_cap(warehouses, wname) -> float:
    for w in warehouses:
        if w.name == wname:
            return w.capacity
    return 1e9


# ============================================================
# Visualisering av baseline
# ============================================================

def plot_baseline_kpi(res: dict, output_path: Path) -> None:
    """To panels: (a) ukentlig etterspursel og leveranse, (b) KPI-tabell som bar."""
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))

    weeks = res['weeks']
    w = np.arange(1, weeks + 1)
    demand = np.array(res['demand_by_week'])
    shipped = np.array(res['shipped_by_week'])

    ax = axes[0]
    ax.plot(w, demand, color='#1F6587', lw=1.5, label='Etterspursel')
    ax.plot(w, shipped, color='#307453', lw=1.2, alpha=0.85, label='Levert')
    ax.fill_between(w, shipped, demand, where=(demand > shipped),
                    color='#ED9F9E', alpha=0.6, label='Underdekning')
    ax.set_xlabel('Uke $t$', fontsize=11)
    ax.set_ylabel('Enheter / uke', fontsize=11)
    ax.set_title('Ukentlig etterspursel og leveranse (baseline)',
                 fontsize=11, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9, loc='lower right')

    ax = axes[1]
    regions = list(res['per_region_service_level'].keys())
    sl = [res['per_region_service_level'][r] for r in regions]
    fills = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']
    strokes = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']
    bars = ax.bar(regions, sl, color=fills, edgecolor=strokes, linewidth=1.6)
    for bar, v in zip(bars, sl):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.005,
                f'{v*100:.1f}%', ha='center', va='bottom', fontsize=9, fontweight='bold')
    ax.axhline(0.98, color='#961D1C', linestyle='--', lw=1.1, alpha=0.6,
               label='Maal: 98 %')
    ax.set_ylim(0.90, 1.01)
    ax.set_ylabel('Servicenivaa (fill rate)', fontsize=11)
    ax.set_title('Servicenivaa pr kunderegion (baseline)',
                 fontsize=11, fontweight='bold')
    ax.grid(True, axis='y', alpha=0.3)
    ax.legend(fontsize=9, loc='lower right')
    plt.setp(ax.get_xticklabels(), rotation=15, ha='right')

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
    print("STEG 2: BASELINE-SIMULERING")
    print("=" * 60)

    sc = baseline_supply_chain()
    res = run_simulation(sc, overrides=ScenarioOverrides(name='baseline'))

    print(f"Uker simulert:        {res['weeks']}")
    print(f"Total etterspursel:   {res['total_demand']:.0f} enheter")
    print(f"Servicenivaa:         {res['service_level']*100:.2f} %")
    print(f"Snitt-forsinkelse:    {res['mean_delivery_delay_weeks']:.2f} uker")
    print(f"Total kostnad:        {res['total_cost']/1e6:.2f} MNOK")
    print(f"  Lagerhold:          {res['cost_breakdown']['holding']/1e6:.2f} MNOK")
    print(f"  Tapte salg:         {res['cost_breakdown']['lost_sale']/1e6:.2f} MNOK")
    print(f"  Haste-transport:    {res['cost_breakdown']['expedite']/1e6:.2f} MNOK")
    print(f"  Oppsett/bestilling: {res['cost_breakdown']['setup']/1e6:.2f} MNOK")

    # Lagre
    summary = {k: v for k, v in res.items()
               if k not in ('demand_by_week', 'shortfall_by_week', 'shipped_by_week')}
    with open(OUTPUT_DIR / 'step02_baseline.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, default=float)
    print(f"Resultat lagret: {OUTPUT_DIR / 'step02_baseline.json'}")

    plot_baseline_kpi(res, OUTPUT_DIR / 'st_baseline_kpi.png')


if __name__ == '__main__':
    main()
