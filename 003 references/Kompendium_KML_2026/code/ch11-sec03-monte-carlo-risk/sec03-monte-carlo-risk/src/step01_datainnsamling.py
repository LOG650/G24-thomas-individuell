"""
Steg 1: Datainnsamling
======================
Definerer parametrene i forsyningskjedemodellen for NordImport AS --
en norsk importor som henter et enkelt produkt fra en leverandor i Asia.
Etterspoersel, leveringstid og leverandorsvikt modelleres som
sannsynlighetsfordelinger med realistiske parametre.

Output:
  - output/mcr_parameters.json     : alle modellparametre som JSON
  - output/mcr_cost_dist.png       : (fyllist her, figur lages i step03)
  - output/mcr_distributions.png   : tre underplott med fordelingene
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)

# Farger fra bokens palett (pastell-infografikk)
COLOR_S1 = '#8CC8E5'
COLOR_S1_DARK = '#1F6587'
COLOR_S2 = '#97D4B7'
COLOR_S2_DARK = '#307453'
COLOR_S3 = '#F6BA7C'
COLOR_S3_DARK = '#9C540B'
COLOR_S4 = '#BD94D7'
COLOR_S4_DARK = '#5A2C77'
COLOR_S5 = '#ED9F9E'
COLOR_S5_DARK = '#961D1C'
COLOR_INK = '#1F2933'


def get_parameters() -> dict:
    """Returner alle modellparametre for NordImport AS.

    Etterspoersel: normalfordelt aarlig (enheter/aar).
    Leveringstid: lognormalfordelt (dager).
    Leverandorsvikt: Bernoulli pr bestillingssyklus.
    Kostnader: deterministiske satser.
    """
    return {
        # Etterspoersel (aarlig, normalfordelt)
        'demand_mean': 12_000,           # enheter per aar
        'demand_std': 2_000,             # standardavvik
        # Leveringstid (lognormal pr bestilling, dager)
        'lead_time_meanlog': np.log(35), # median 35 dager
        'lead_time_sdlog': 0.30,         # CV ~ 30 %
        # Leverandorsvikt (Bernoulli pr bestilling)
        'supplier_fail_prob': 0.08,      # 8 % per bestilling
        # Bestillingssyklus
        'n_orders_per_year': 6,          # 6 bestillinger/aar (ca. annenhver maaned)
        # Kostnader (NOK per enhet eller NOK pr aar)
        'price': 600.0,                  # salgspris
        'cost_unit': 300.0,              # normal innkjopskostnad
        'cost_expedite': 550.0,          # hasteinnkjop (dobbel margintap)
        'cost_lost_sale': 450.0,         # tapt dekningsbidrag pr enhet
        'holding_cost_rate': 0.20,       # 20 % av enhetspris pr aar
        'safety_stock_units': 400,       # baseline sikkerhetslager
        # Simuleringsoppsett
        'n_runs': 10_000,
        'seed': 2026,
    }


def _lead_time_stats(meanlog: float, sdlog: float) -> dict:
    """Beregn forventning, median, 95 %-kvantil for lognormalfordelingen."""
    mean = float(np.exp(meanlog + 0.5 * sdlog ** 2))
    median = float(np.exp(meanlog))
    q95 = float(stats.lognorm(sdlog, scale=np.exp(meanlog)).ppf(0.95))
    return {'mean': round(mean, 2), 'median': round(median, 2), 'q95': round(q95, 2)}


def plot_distributions(params: dict, output_path: Path) -> None:
    """Plott de tre stokastiske innputene i tre underpaneler."""
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))

    # 1. Etterspoersel (normal)
    mu_d = params['demand_mean']
    sd_d = params['demand_std']
    x_d = np.linspace(mu_d - 4 * sd_d, mu_d + 4 * sd_d, 500)
    y_d = stats.norm.pdf(x_d, mu_d, sd_d)
    axes[0].plot(x_d, y_d, color=COLOR_S1_DARK, linewidth=2)
    axes[0].fill_between(x_d, 0, y_d, color=COLOR_S1, alpha=0.6)
    axes[0].axvline(mu_d, color=COLOR_INK, linestyle='--', linewidth=1)
    axes[0].set_title(r'Etterspoersel $D \sim \mathcal{N}(12\,000, 2\,000^2)$',
                      fontsize=11, fontweight='bold')
    axes[0].set_xlabel('Enheter per aar', fontsize=11)
    axes[0].set_ylabel('Tetthet', fontsize=11)
    axes[0].grid(True, alpha=0.3)

    # 2. Leveringstid (lognormal)
    meanlog = params['lead_time_meanlog']
    sdlog = params['lead_time_sdlog']
    x_l = np.linspace(10, 90, 500)
    y_l = stats.lognorm.pdf(x_l, sdlog, scale=np.exp(meanlog))
    axes[1].plot(x_l, y_l, color=COLOR_S2_DARK, linewidth=2)
    axes[1].fill_between(x_l, 0, y_l, color=COLOR_S2, alpha=0.6)
    axes[1].axvline(np.exp(meanlog), color=COLOR_INK, linestyle='--', linewidth=1)
    axes[1].set_title(r'Leveringstid $L \sim \mathrm{LogN}(\ln 35, 0{,}30^2)$',
                      fontsize=11, fontweight='bold')
    axes[1].set_xlabel('Dager', fontsize=11)
    axes[1].set_ylabel('Tetthet', fontsize=11)
    axes[1].grid(True, alpha=0.3)

    # 3. Leverandorsvikt (Bernoulli) -- vis som stolpediagram
    p = params['supplier_fail_prob']
    axes[2].bar([0, 1], [1 - p, p],
                color=[COLOR_S5, COLOR_S5_DARK], alpha=0.85, edgecolor=COLOR_INK)
    axes[2].set_xticks([0, 1])
    axes[2].set_xticklabels(['Leverer (0)', 'Svikt (1)'], fontsize=11)
    axes[2].set_ylim(0, 1.05)
    axes[2].set_title(r'Leverandorsvikt $F \sim \mathrm{Bern}(0{,}08)$',
                      fontsize=11, fontweight='bold')
    axes[2].set_ylabel('Sannsynlighet', fontsize=11)
    axes[2].grid(True, alpha=0.3, axis='y')
    for i, v in enumerate([1 - p, p]):
        axes[2].text(i, v + 0.02, f'{v:.2f}', ha='center', fontsize=10, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING')
    print('=' * 60)

    params = get_parameters()

    print('\n--- Parametre ---')
    for key, value in params.items():
        print(f'  {key}: {value}')

    ls = _lead_time_stats(params['lead_time_meanlog'], params['lead_time_sdlog'])
    print(f'\n--- Leveringstid (avledet) ---')
    print(f'  E[L] = {ls["mean"]} dager')
    print(f'  Median = {ls["median"]} dager')
    print(f'  95 %-kvantil = {ls["q95"]} dager')

    # Lagre som JSON
    params_out = {k: (v if not isinstance(v, float) else round(v, 6))
                  for k, v in params.items()}
    params_out['lead_time_stats'] = ls
    json_path = OUTPUT_DIR / 'mcr_parameters.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(params_out, f, indent=2, ensure_ascii=False)
    print(f'\nParametre lagret: {json_path}')

    plot_distributions(params, OUTPUT_DIR / 'mcr_distributions.png')


if __name__ == '__main__':
    main()
