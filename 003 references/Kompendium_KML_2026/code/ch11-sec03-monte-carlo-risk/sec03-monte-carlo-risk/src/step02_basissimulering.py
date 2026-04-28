"""
Steg 2: Basissimulering (single-run)
====================================
En enkelt simulering av forsyningskjeden for NordImport AS i ett aar.
Viser sammenhengen mellom aarsetterspoersel, lager, leverandorsvikt
og kostnader i en enkelt realisering av de stokastiske stoerelsene.

Output:
  - output/mcr_time_trajectory.png : tre underplott som viser lager,
                                     kumulativ etterspoersel og
                                     kostnadsoppbygging gjennom aaret
  - output/mcr_basis_run.json      : totaltall fra ett enkelt aars-run
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from step01_datainnsamling import (
    COLOR_INK,
    COLOR_S1,
    COLOR_S1_DARK,
    COLOR_S2,
    COLOR_S2_DARK,
    COLOR_S3,
    COLOR_S3_DARK,
    COLOR_S4_DARK,
    COLOR_S5,
    COLOR_S5_DARK,
    get_parameters,
)

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


def simulate_single_run(params: dict, rng: np.random.Generator) -> dict:
    """Simuler ett aar (52 uker) for forsyningskjeden.

    Modell (enkel periodisk bestilling med sikkerhetslager):
      - Samlet aarsetterspoersel D ~ N(mu_D, sigma_D^2) fordelt jevnt paa 52 uker.
      - n_orders bestillinger per aar; hver har en tilfeldig leveringstid L
        (lognormal, dager) og en tilfeldig svikt F ~ Bern(p_fail).
      - Ved svikt forsinkes leveringen med 14 dager ekstra (hastebestilling).
      - Lageret foelges uke for uke; mangel -> tapt salg.

    Returnerer stiene gjennom aaret og totale kostnader.
    """
    # --- Trekk tilfeldige stoerelser ---
    mu_d = params['demand_mean']
    sd_d = params['demand_std']
    demand_annual = max(float(rng.normal(mu_d, sd_d)), 0.0)

    n_orders = params['n_orders_per_year']
    meanlog = params['lead_time_meanlog']
    sdlog = params['lead_time_sdlog']
    lead_times = rng.lognormal(meanlog, sdlog, size=n_orders)
    fails = rng.binomial(1, params['supplier_fail_prob'], size=n_orders)
    # Ved svikt legges 14 dagers hasteforsinkelse til
    lead_times_eff = lead_times + 14.0 * fails

    # --- Simuler uke for uke ---
    weeks = 52
    demand_weekly = np.full(weeks, demand_annual / weeks)
    # Liten ukentlig stoy rundt gjennomsnittet
    demand_weekly = np.maximum(demand_weekly +
                               rng.normal(0, demand_annual / weeks * 0.10, weeks),
                               0)
    # Bestillingsuker (jevnt fordelt) -- start ved uke 0, deretter hver
    # (52 / n_orders)-te uke
    order_weeks = np.arange(n_orders) * (weeks // n_orders)
    order_qty = demand_annual / n_orders

    # Beregn ankomstuker fra leveringstider (dager -> uker)
    arrival_weeks = np.clip(order_weeks + np.round(lead_times_eff / 7).astype(int),
                            0, weeks - 1)

    # Lager og kostnadssporing. Startlager dekker perioden fram til foerste
    # leveranse kommer (ca. 5 uker) pluss sikkerhetslageret.
    avg_weekly_demand = demand_annual / weeks
    initial_lead_weeks = max(int(np.round(np.mean(lead_times_eff) / 7)), 1)
    inventory = np.zeros(weeks + 1)
    inventory[0] = (params['safety_stock_units']
                    + avg_weekly_demand * initial_lead_weeks)
    lost_sales = np.zeros(weeks)
    expedite_units = np.zeros(weeks)  # hastebestillingsvolum ved svikt

    for t in range(weeks):
        # Ankomst denne uken
        incoming = order_qty * np.sum(arrival_weeks == t)
        # Dersom svikt skjer paa en bestilling, er ankomsten forsinket men
        # NordImport dekker deler av gapet med en hastebestilling paa ankomstuka.
        # Vi antar hastebestillingen = halvparten av manglet leveranse.
        swift_incoming = 0.0
        for j, aw in enumerate(arrival_weeks):
            if aw == t and fails[j] == 1:
                # dekk 50 % av ordrekvantumet via ekstra hasteinnkjop
                swift_incoming += 0.5 * order_qty

        available = inventory[t] + incoming + swift_incoming
        if available >= demand_weekly[t]:
            inventory[t + 1] = available - demand_weekly[t]
            lost_sales[t] = 0.0
        else:
            lost_sales[t] = demand_weekly[t] - available
            inventory[t + 1] = 0.0
        expedite_units[t] = swift_incoming

    # --- Kostnader ---
    avg_inventory = float(np.mean(inventory))
    holding_cost = (params['holding_cost_rate'] * params['cost_unit'] *
                    avg_inventory)
    expedite_cost = float(np.sum(expedite_units) *
                          (params['cost_expedite'] - params['cost_unit']))
    lost_sales_total = float(np.sum(lost_sales))
    lost_sales_cost = lost_sales_total * params['cost_lost_sale']

    total_cost = holding_cost + expedite_cost + lost_sales_cost

    return {
        'demand_annual': demand_annual,
        'n_orders': n_orders,
        'lead_times': lead_times,
        'lead_times_eff': lead_times_eff,
        'fails': fails,
        'inventory': inventory,
        'lost_sales': lost_sales,
        'expedite_units': expedite_units,
        'demand_weekly': demand_weekly,
        'order_weeks': order_weeks,
        'arrival_weeks': arrival_weeks,
        'avg_inventory': avg_inventory,
        'holding_cost': holding_cost,
        'expedite_cost': expedite_cost,
        'lost_sales_cost': lost_sales_cost,
        'lost_sales_total_units': lost_sales_total,
        'total_cost': total_cost,
    }


def plot_trajectory(run: dict, output_path: Path) -> None:
    """Plott lagernivaa, kumulativ etterspoersel og kostnadsoppbygging."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 4.2))
    weeks = 52
    t = np.arange(weeks + 1)

    # 1. Lagernivaa
    axes[0].plot(t, run['inventory'], color=COLOR_S1_DARK, linewidth=1.7)
    axes[0].fill_between(t, 0, run['inventory'], color=COLOR_S1, alpha=0.45)
    # Marker ankomster
    for aw, fail in zip(run['arrival_weeks'], run['fails']):
        color = COLOR_S5_DARK if fail == 1 else COLOR_S2_DARK
        axes[0].axvline(aw, color=color, linestyle=':', linewidth=1.2, alpha=0.8)
    axes[0].set_xlabel('Uke $t$', fontsize=11)
    axes[0].set_ylabel('Lagernivaa $I_t$', fontsize=11)
    axes[0].set_title('Lagernivaa gjennom aaret', fontsize=11, fontweight='bold')
    axes[0].set_xlim(0, weeks)
    axes[0].grid(True, alpha=0.3)

    # 2. Kumulativt tapt salg
    cum_lost = np.cumsum(run['lost_sales'])
    axes[1].plot(np.arange(weeks), cum_lost, color=COLOR_S5_DARK, linewidth=1.7)
    axes[1].fill_between(np.arange(weeks), 0, cum_lost,
                         color=COLOR_S5, alpha=0.45)
    axes[1].set_xlabel('Uke $t$', fontsize=11)
    axes[1].set_ylabel('Tapte enheter (kumulativt)', fontsize=11)
    axes[1].set_title('Kumulativt tapt salg', fontsize=11, fontweight='bold')
    axes[1].set_xlim(0, weeks)
    axes[1].grid(True, alpha=0.3)

    # 3. Kostnadsfordeling som sirkel-/stolpediagram
    costs = {
        'Lagerhold': run['holding_cost'],
        'Hastekjoep': run['expedite_cost'],
        'Tapt salg': run['lost_sales_cost'],
    }
    colors = [COLOR_S1_DARK, COLOR_S3_DARK, COLOR_S5_DARK]
    axes[2].bar(list(costs.keys()), list(costs.values()),
                color=colors, alpha=0.85, edgecolor=COLOR_INK)
    axes[2].set_ylabel('Kostnad (NOK)', fontsize=11)
    axes[2].set_title(f'Totalkostnad: {run["total_cost"]:,.0f} NOK'.replace(',', ' '),
                      fontsize=11, fontweight='bold')
    axes[2].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate(costs.values()):
        axes[2].text(i, v * 1.02, f'{v:,.0f}'.replace(',', ' '),
                     ha='center', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 2: BASISSIMULERING')
    print('=' * 60)

    params = get_parameters()
    rng = np.random.default_rng(params['seed'])

    run = simulate_single_run(params, rng)

    print(f'\nAarlig etterspoersel:     {run["demand_annual"]:,.0f} enheter'
          .replace(',', ' '))
    print(f'Gjennomsnittlig lager:    {run["avg_inventory"]:,.0f} enheter'
          .replace(',', ' '))
    print(f'Tapt salg total (enh):    {run["lost_sales_total_units"]:,.0f}'
          .replace(',', ' '))
    print(f'Leverandorsvikt (ant.):   {int(np.sum(run["fails"]))} / '
          f'{run["n_orders"]}')
    print(f'Kostnad - lagerhold:      {run["holding_cost"]:,.0f} NOK'
          .replace(',', ' '))
    print(f'Kostnad - hastekjoep:     {run["expedite_cost"]:,.0f} NOK'
          .replace(',', ' '))
    print(f'Kostnad - tapt salg:      {run["lost_sales_cost"]:,.0f} NOK'
          .replace(',', ' '))
    print(f'TOTALKOSTNAD (denne run): {run["total_cost"]:,.0f} NOK'
          .replace(',', ' '))

    # Lagre JSON (kun skalare totalverdier)
    result = {
        'demand_annual': round(run['demand_annual'], 1),
        'avg_inventory': round(run['avg_inventory'], 1),
        'lost_sales_total_units': round(run['lost_sales_total_units'], 1),
        'n_failures': int(np.sum(run['fails'])),
        'holding_cost': round(run['holding_cost'], 0),
        'expedite_cost': round(run['expedite_cost'], 0),
        'lost_sales_cost': round(run['lost_sales_cost'], 0),
        'total_cost': round(run['total_cost'], 0),
    }
    json_path = OUTPUT_DIR / 'mcr_basis_run.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f'\nResultat lagret: {json_path}')

    plot_trajectory(run, OUTPUT_DIR / 'mcr_time_trajectory.png')


if __name__ == '__main__':
    main()
