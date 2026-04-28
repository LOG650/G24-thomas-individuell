"""
Steg 1: Datainnsamling -- baseline-forsyningskjede
==================================================
Definerer en komplett flerniva forsyningskjede for en norsk distributor av
kritiske forsyninger (legemidler, verneutstyr):

  - 2 leverandorer (L1 i Kina, L2 i Polen) med ulik ledetid og palitelighet
  - 1 fabrikk / sentrallager i Oslo
  - 3 regionallager (Nord, Midt, Sor)
  - 5 kunderegioner med stokastisk etterspurselsprofil

Hver node har kapasitet, sikkerhetslager og kostnadsparametre. Denne modulen
brukes av steg 2-6.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

import matplotlib.pyplot as plt
import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


# ============================================================
# Dataklasser for forsyningskjeden
# ============================================================

@dataclass
class Supplier:
    name: str
    lead_time_mean: float    # dager
    lead_time_sd: float      # dager
    reliability: float       # sannsynlighet for levering (per ordre)
    capacity: float          # enheter / uke
    unit_cost: float         # NOK / enhet


@dataclass
class Factory:
    name: str
    throughput: float        # enheter / uke
    safety_stock: float      # enheter
    holding_cost: float      # NOK / enhet / uke


@dataclass
class Warehouse:
    name: str
    region: str
    capacity: float          # enheter
    safety_stock: float      # enheter
    holding_cost: float      # NOK / enhet / uke


@dataclass
class CustomerRegion:
    name: str
    demand_mean: float       # enheter / uke
    demand_sd: float         # enheter / uke
    warehouse: str           # primaerlager


@dataclass
class CostParams:
    lost_sale_cost: float = 1200.0   # NOK per manglende enhet
    expedite_cost: float = 650.0     # NOK per haste-enhet
    setup_cost: float = 3500.0       # NOK per bestilling


@dataclass
class SupplyChain:
    suppliers: list[Supplier]
    factory: Factory
    warehouses: list[Warehouse]
    customers: list[CustomerRegion]
    costs: CostParams = field(default_factory=CostParams)
    weeks: int = 52
    seed: int = 2025


# ============================================================
# Baseline-definisjon
# ============================================================

def baseline_supply_chain() -> SupplyChain:
    """Full baseline-beskrivelse av forsyningskjeden (Norsk distributor)."""
    suppliers = [
        Supplier(
            name='L1-Kina',
            lead_time_mean=35.0, lead_time_sd=6.0,
            reliability=0.97, capacity=3200.0, unit_cost=45.0,
        ),
        Supplier(
            name='L2-Polen',
            lead_time_mean=14.0, lead_time_sd=3.0,
            reliability=0.99, capacity=1500.0, unit_cost=62.0,
        ),
    ]
    factory = Factory(
        name='F-Oslo',
        throughput=4200.0, safety_stock=3500.0, holding_cost=4.0,
    )
    warehouses = [
        Warehouse(name='W-Nord', region='Nord', capacity=5500.0,
                  safety_stock=2100.0, holding_cost=5.0),
        Warehouse(name='W-Midt', region='Midt', capacity=5500.0,
                  safety_stock=1500.0, holding_cost=5.0),
        Warehouse(name='W-Sor', region='Sor', capacity=8500.0,
                  safety_stock=4300.0, holding_cost=5.0),
    ]
    customers = [
        CustomerRegion('Troms',    demand_mean=480.0, demand_sd=110.0, warehouse='W-Nord'),
        CustomerRegion('Nordland', demand_mean=560.0, demand_sd=130.0, warehouse='W-Nord'),
        CustomerRegion('Trondelag', demand_mean=720.0, demand_sd=150.0, warehouse='W-Midt'),
        CustomerRegion('Vestland', demand_mean=900.0, demand_sd=180.0, warehouse='W-Sor'),
        CustomerRegion('Oslo-Viken', demand_mean=1250.0, demand_sd=220.0, warehouse='W-Sor'),
    ]
    return SupplyChain(
        suppliers=suppliers, factory=factory,
        warehouses=warehouses, customers=customers,
    )


# ============================================================
# Visualisering av nettverket
# ============================================================

# Farger fra bokens temapalette (fylling / strek)
FILLS = ['#8CC8E5', '#97D4B7', '#F6BA7C', '#BD94D7', '#ED9F9E']
STROKES = ['#1F6587', '#307453', '#9C540B', '#5A2C77', '#961D1C']


def plot_network(sc: SupplyChain, output_path: Path) -> None:
    """Tegn forsyningskjedenettverket som en sjiktsvis graf."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Fire kolonner (sjikt): leverandor, fabrikk, lager, kunder
    x_sup, x_fac, x_wh, x_cu = 0.5, 3.0, 5.5, 8.0

    # Leverandorer
    n_sup = len(sc.suppliers)
    sup_y = np.linspace(0.8, 4.2, n_sup)
    for i, s in enumerate(sc.suppliers):
        _draw_node(ax, x_sup, sup_y[i], 1.6, 0.7,
                   s.name, FILLS[0], STROKES[0],
                   sub=f'LT={s.lead_time_mean:.0f}d, rel={s.reliability:.2f}')

    # Fabrikk
    _draw_node(ax, x_fac, 2.5, 1.6, 0.8,
               sc.factory.name, FILLS[2], STROKES[2],
               sub=f'SS={sc.factory.safety_stock:.0f}')

    # Lagre
    n_wh = len(sc.warehouses)
    wh_y = np.linspace(0.8, 4.2, n_wh)
    for i, w in enumerate(sc.warehouses):
        _draw_node(ax, x_wh, wh_y[i], 1.6, 0.7,
                   w.name, FILLS[1], STROKES[1],
                   sub=f'cap={w.capacity:.0f}')

    # Kunder
    n_cu = len(sc.customers)
    cu_y = np.linspace(0.4, 4.6, n_cu)
    for i, c in enumerate(sc.customers):
        _draw_node(ax, x_cu, cu_y[i], 1.6, 0.6,
                   c.name, FILLS[3], STROKES[3],
                   sub=f'D={c.demand_mean:.0f}/u')

    # Piler: leverandor -> fabrikk
    for y in sup_y:
        _draw_arrow(ax, x_sup + 0.8, y, x_fac - 0.8, 2.5)
    # fabrikk -> lager
    for y in wh_y:
        _draw_arrow(ax, x_fac + 0.8, 2.5, x_wh - 0.8, y)
    # lager -> kunder
    for i, c in enumerate(sc.customers):
        # finn y-koordinat til tilhorende lager
        wh_idx = [w.name for w in sc.warehouses].index(c.warehouse)
        _draw_arrow(ax, x_wh + 0.8, wh_y[wh_idx], x_cu - 0.8, cu_y[i])

    # Sjiktsetiketter
    for x, label in [(x_sup, 'Leverandorer'), (x_fac, 'Fabrikk'),
                     (x_wh, 'Regionlagre'), (x_cu, 'Kunderegioner')]:
        ax.text(x, 5.2, label, ha='center', va='bottom', fontsize=11,
                fontweight='bold', color='#1F2933')

    ax.set_xlim(-0.5, 9.5)
    ax.set_ylim(-0.2, 5.7)
    ax.axis('off')
    ax.set_title('Baseline-forsyningskjede: 2 leverandorer, 1 fabrikk, 3 lagre, 5 regioner',
                 fontsize=12, fontweight='bold')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def _draw_node(ax, x, y, w, h, label, fill, stroke, sub=None):
    rect = plt.Rectangle((x - w / 2, y - h / 2), w, h,
                         facecolor=fill, edgecolor=stroke, linewidth=1.8, zorder=3)
    ax.add_patch(rect)
    ax.text(x, y + (0.08 if sub else 0.0), label, ha='center', va='center',
            fontsize=10, color=stroke, fontweight='bold', zorder=4)
    if sub:
        ax.text(x, y - 0.18, sub, ha='center', va='center',
                fontsize=8, color='#556270', zorder=4)


def _draw_arrow(ax, x1, y1, x2, y2):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#556270',
                                lw=1.1, alpha=0.65), zorder=1)


def plot_method(output_path: Path) -> None:
    """Seks-stegs prosessdiagram for stresstest."""
    fig, ax = plt.subplots(figsize=(13, 3.6))
    steps = [
        ('1. Datainnsamling',       '#8CC8E5', '#1F6587'),
        ('2. Baseline-\nsimulering', '#97D4B7', '#307453'),
        ('3. Scenarier',            '#F6BA7C', '#9C540B'),
        ('4. Evaluering',           '#BD94D7', '#5A2C77'),
        ('5. Mitigasjoner',         '#ED9F9E', '#961D1C'),
        ('6. Beredskapsplan',       '#8CC8E5', '#1F6587'),
    ]
    n = len(steps)
    xs = np.linspace(0.8, 12.2, n)
    y = 1.5
    w, h = 1.5, 1.2
    for x, (label, fill, stroke) in zip(xs, steps):
        rect = plt.Rectangle((x - w / 2, y - h / 2), w, h,
                             facecolor=fill, edgecolor=stroke, linewidth=1.8)
        ax.add_patch(rect)
        ax.text(x, y, label, ha='center', va='center',
                fontsize=10, color=stroke, fontweight='bold')
    for i in range(n - 1):
        ax.annotate('', xy=(xs[i + 1] - w / 2, y), xytext=(xs[i] + w / 2, y),
                    arrowprops=dict(arrowstyle='->', color='#556270', lw=1.6))
    # Loop-pil bakover (iterativ prosess)
    ax.annotate('', xy=(xs[0], y - h / 2 - 0.15),
                xytext=(xs[-1], y - h / 2 - 0.15),
                arrowprops=dict(arrowstyle='->', color='#1F6587', lw=1.2,
                                connectionstyle='arc3,rad=-0.2', alpha=0.7))
    ax.text((xs[0] + xs[-1]) / 2, y - h / 2 - 0.85,
            'Iterasjon: ny informasjon leder til oppdaterte scenarier og tiltak',
            ha='center', va='center', fontsize=9, color='#1F6587', style='italic')

    ax.set_xlim(0, 13)
    ax.set_ylim(-0.3, 2.6)
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


# ============================================================
# Hovedfunksjon
# ============================================================

def _sc_to_dict(sc: SupplyChain) -> dict:
    return {
        'suppliers': [asdict(s) for s in sc.suppliers],
        'factory': asdict(sc.factory),
        'warehouses': [asdict(w) for w in sc.warehouses],
        'customers': [asdict(c) for c in sc.customers],
        'costs': asdict(sc.costs),
        'weeks': sc.weeks, 'seed': sc.seed,
    }


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 1: DATAINNSAMLING")
    print("=" * 60)

    sc = baseline_supply_chain()

    total_demand = sum(c.demand_mean for c in sc.customers)
    total_capacity = sum(s.capacity for s in sc.suppliers)
    total_wh_cap = sum(w.capacity for w in sc.warehouses)

    print(f"Leverandorer:     {len(sc.suppliers)}")
    print(f"Fabrikker:        1")
    print(f"Regionlagre:      {len(sc.warehouses)}")
    print(f"Kunderegioner:    {len(sc.customers)}")
    print(f"Total etterspursel (snitt): {total_demand:.0f} enh/uke")
    print(f"Total leverandorkapasitet:  {total_capacity:.0f} enh/uke")
    print(f"Total lagerkapasitet:       {total_wh_cap:.0f} enh")
    print(f"Fabrikkapasitet:            {sc.factory.throughput:.0f} enh/uke")

    # Lagre som JSON
    path_json = OUTPUT_DIR / 'step01_supply_chain.json'
    with open(path_json, 'w', encoding='utf-8') as f:
        json.dump(_sc_to_dict(sc), f, indent=2, ensure_ascii=False)
    print(f"Baseline-data lagret: {path_json}")

    plot_network(sc, OUTPUT_DIR / 'st_network.png')
    plot_method(OUTPUT_DIR / 'st_method.png')


if __name__ == '__main__':
    main()
