"""
Steg 1: Datainnsamling og etterspoerselsfordeling
=================================================
Genererer syntetisk etterspoersel for et sesongprodukt (norsk motebutikk som
bestiller en vinterjakkekolleksjon fra en leverandoer i utlandet) og
karakteriserer fordelingen. Plotter PDF og visualiserer kritisk-forhold-intuisjonen.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


# -- Problem parametere ----------------------------------------------------
# Vinterjakker - sesongprodukt som bestilles en gang foer sesongen og ikke
# kan etterbestilles. Etterspoersel modelleres som normalfordelt.
MU_DEMAND = 1000          # forventet etterspoersel (enheter)
SIGMA_DEMAND = 250        # standardavvik (enheter)

# Oekonomiske parametere (NOK per enhet)
PRICE_RETAIL = 1500       # p: utsalgspris (detaljist til sluttkunde)
COST_SUPPLIER = 400       # c: produksjonskostnad hos leverandoer
WHOLESALE_PRICE = 900     # w: ordinaer engrospris (leverandoer -> detaljist)
SALVAGE_VALUE = 200       # s: restverdi (slik salg etter sesong)


def demand_pdf(x: np.ndarray) -> np.ndarray:
    return stats.norm.pdf(x, loc=MU_DEMAND, scale=SIGMA_DEMAND)


def critical_ratio(p: float, c: float, s: float) -> float:
    """Kritisk forhold for klassisk newsvendor (integrert kjede)."""
    return (p - c) / (p - s)


def plot_demand_distribution(output_path: Path) -> None:
    """PDF for etterspoersel med kritisk-forhold-kvantil markert."""
    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.linspace(MU_DEMAND - 4 * SIGMA_DEMAND, MU_DEMAND + 4 * SIGMA_DEMAND, 500)
    f = demand_pdf(x)

    ax.plot(x, f, color='#1F6587', linewidth=2, label=r'$f_D(d)$ (normal)')
    ax.fill_between(x, 0, f, color='#8CC8E5', alpha=0.4)

    # Kritisk forhold for den integrerte kjeden
    cr = critical_ratio(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE)
    q_star = stats.norm.ppf(cr, loc=MU_DEMAND, scale=SIGMA_DEMAND)

    # Markere kvantilet
    ax.axvline(q_star, color='#961D1C', linestyle='--', linewidth=1.8,
               label=f'$Q^*_{{kjede}} = F^{{-1}}({cr:.2f}) = {q_star:.0f}$')
    ax.axvline(MU_DEMAND, color='#307453', linestyle=':', linewidth=1.5,
               label=fr'$\mu = {MU_DEMAND}$')

    # Skrav kritisk-forhold-arealet
    mask = x <= q_star
    ax.fill_between(x[mask], 0, f[mask], color='#97D4B7', alpha=0.6,
                    label=fr'$P(D \leq Q^*) = {cr:.2f}$')

    ax.set_xlabel('$d$ (enheter etterspurt)', fontsize=12)
    ax.set_ylabel('$f_D(d)$', fontsize=12)
    ax.set_title('Etterspoerselsfordeling for vinterjakker',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper right', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(x[0], x[-1])
    ax.set_ylim(0, max(f) * 1.15)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f'Figur lagret: {output_path}')


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    print('\n' + '=' * 60)
    print('STEG 1: DATAINNSAMLING')
    print('=' * 60)

    cr = critical_ratio(PRICE_RETAIL, COST_SUPPLIER, SALVAGE_VALUE)
    q_star = stats.norm.ppf(cr, loc=MU_DEMAND, scale=SIGMA_DEMAND)
    safety_stock = q_star - MU_DEMAND

    summary = {
        'mu': MU_DEMAND,
        'sigma': SIGMA_DEMAND,
        'p_retail': PRICE_RETAIL,
        'c_supplier': COST_SUPPLIER,
        'w_wholesale': WHOLESALE_PRICE,
        's_salvage': SALVAGE_VALUE,
        'kritisk_forhold_kjede': round(cr, 4),
        'q_star_kjede': round(float(q_star), 1),
        'sikkerhetslager_kjede': round(float(safety_stock), 1),
    }

    print('\nFordelingsparametere:')
    print(f'  mu (forventet etterspoersel) : {MU_DEMAND}')
    print(f'  sigma (standardavvik)        : {SIGMA_DEMAND}')
    print('\nOekonomiske parametere (NOK):')
    print(f'  p (utsalgspris)              : {PRICE_RETAIL}')
    print(f'  c (produksjonskostnad)       : {COST_SUPPLIER}')
    print(f'  w (engrospris)               : {WHOLESALE_PRICE}')
    print(f'  s (restverdi)                : {SALVAGE_VALUE}')
    print('\nSentraliserte beregninger (som referanse):')
    print(f"  kritisk forhold (p-c)/(p-s)  : {cr:.4f}")
    print(f'  Q* for kjeden                : {q_star:.1f}')
    print(f'  Sikkerhetslager ift mu       : {safety_stock:.1f}')

    # Lagre data
    with open(OUTPUT_DIR / 'step01_results.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {OUTPUT_DIR / 'step01_results.json'}")

    plot_demand_distribution(OUTPUT_DIR / 'nv_demand_dist.png')


if __name__ == '__main__':
    main()
