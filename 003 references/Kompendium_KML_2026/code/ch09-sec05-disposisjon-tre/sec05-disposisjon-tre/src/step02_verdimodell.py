"""
Steg 2: Verdimodell -- forventet verdi per disposisjonsalternativ
==================================================================
For hver returenhet beregnes forventet netto verdi for fire alternativer:
  a1 = reparere og selge som ny (repair)
  a2 = refurbish og selge brukt med rabatt (refurbish)
  a3 = resirkulere materialene (recycle)
  a4 = deponere som avfall (dispose)

Hver handling gir både en forventet inntekt og en kostnad. Usikkerheten
modelleres ved suksessannsynlighet som avhenger av tilstand.
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from step01_datainnsamling import BRANDS

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'

ACTIONS = ['repair', 'refurbish', 'recycle', 'dispose']

# Suksessannsynlighet P(a | c) -- sannsynlighet for at handling lykkes
# gitt tilstandsscore c in {1,...,5}
P_SUCCESS = {
    'repair':    {1: 0.05, 2: 0.25, 3: 0.55, 4: 0.80, 5: 0.95},
    'refurbish': {1: 0.15, 2: 0.45, 3: 0.75, 4: 0.90, 5: 0.95},
    'recycle':   {1: 0.98, 2: 0.98, 3: 0.98, 4: 0.98, 5: 0.98},
    'dispose':   {1: 1.00, 2: 1.00, 3: 1.00, 4: 1.00, 5: 1.00},
}

# Inntektsfaktorer -- prosent av nypris ved vellykket handling
REVENUE_FACTOR = {
    'repair':    0.85,   # selges som ny, 15 % under nypris
    'refurbish': 0.55,   # brukt med garanti
    'recycle':   0.08,   # materialverdi
    'dispose':   0.00,   # ingen inntekt
}

# Kostnader (flate beløp i NOK) som gjelder uavhengig av suksess
# -- disse dekker inspeksjon, arbeid, logistikk og miljøavgifter.
FIXED_COST = {
    'repair':    750.0,
    'refurbish': 400.0,
    'recycle':   120.0,
    'dispose':   180.0,
}

# Mislykket handling -- enheten må deponeres til miljøavgift
FAILURE_PENALTY = 180.0


def expected_value(row: pd.Series, action: str) -> float:
    """Forventet netto verdi (NOK) for gitt handling på én enhet.

    Suksessannsynligheten justeres ned for eldre enheter og for lav
    funksjonell/kosmetisk grad. Inntekten for reparasjon avhenger også
    av kosmetisk grad (en riper gir redusert pris som ny).
    """
    c = int(row['condition'])
    p_base = P_SUCCESS[action][c]

    # Aldersjustering -- eldre enheter har vanskeligere for å lykkes
    # med repair/refurbish (elektronikk slites, komponenter går ut av produksjon).
    age = int(row['age_months'])
    if action == 'repair':
        age_factor = max(0.55, 1.0 - 0.008 * age)
    elif action == 'refurbish':
        age_factor = max(0.70, 1.0 - 0.005 * age)
    else:
        age_factor = 1.0

    # Funksjonell grad justerer repair (krever fungerende hovedkort)
    func = int(row['functional_grade'])
    if action == 'repair':
        func_factor = {1: 0.30, 2: 0.55, 3: 0.80, 4: 0.95, 5: 1.00}[func]
    elif action == 'refurbish':
        func_factor = {1: 0.65, 2: 0.80, 3: 0.92, 4: 0.98, 5: 1.00}[func]
    else:
        func_factor = 1.0

    p = min(0.98, p_base * age_factor * func_factor)

    # Inntekt avhenger av kosmetisk grad for repair (selges som ny)
    cos = int(row['cosmetic_grade'])
    if action == 'repair':
        cos_factor = {1: 0.70, 2: 0.80, 3: 0.90, 4: 0.97, 5: 1.00}[cos]
    elif action == 'refurbish':
        cos_factor = {1: 0.85, 2: 0.90, 3: 0.95, 4: 0.98, 5: 1.00}[cos]
    else:
        cos_factor = 1.0

    revenue = REVENUE_FACTOR[action] * row['new_price_nok'] * cos_factor
    cost = FIXED_COST[action]

    # Ved mislykket reparasjon/refurbish må enheten deponeres
    if action in ('repair', 'refurbish'):
        failure_cost = FAILURE_PENALTY
    else:
        failure_cost = 0.0
    return p * revenue - cost - (1 - p) * failure_cost


def compute_action_values(df: pd.DataFrame) -> pd.DataFrame:
    """Beregn forventet verdi per handling for hver enhet."""
    result = df.copy()
    for a in ACTIONS:
        result[f'ev_{a}'] = [expected_value(row, a) for _, row in df.iterrows()]
    # Optimal handling = argmax over kolonner
    ev_cols = [f'ev_{a}' for a in ACTIONS]
    result['optimal_action'] = result[ev_cols].idxmax(axis=1).str.replace('ev_', '')
    result['optimal_value'] = result[ev_cols].max(axis=1)
    return result


def plot_value_per_action(df: pd.DataFrame, output_path: Path) -> None:
    """Plot gjennomsnittlig forventet verdi per handling, stratifisert på tilstand."""
    fig, ax = plt.subplots(figsize=(10, 5))

    palette = {
        'repair':    ('#8CC8E5', '#1F6587'),
        'refurbish': ('#97D4B7', '#307453'),
        'recycle':   ('#F6BA7C', '#9C540B'),
        'dispose':   ('#ED9F9E', '#961D1C'),
    }

    width = 0.18
    x = np.arange(1, 6)
    for i, action in enumerate(ACTIONS):
        means = [df.loc[df['condition'] == c, f'ev_{action}'].mean() for c in x]
        offset = (i - 1.5) * width
        fill, edge = palette[action]
        ax.bar(
            x + offset, means, width,
            color=fill, edgecolor=edge, linewidth=1.2,
            label=action,
        )

    ax.axhline(0, color='#556270', linewidth=0.8)
    ax.set_xlabel('Tilstandsscore $c$', fontsize=14)
    ax.set_ylabel('Forventet verdi (NOK)', fontsize=14)
    ax.set_xticks(x)
    ax.set_title('Gjennomsnittlig forventet verdi per handling og tilstand',
                 fontsize=12, fontweight='bold')
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, axis='y', alpha=0.3)
    ax.tick_params(axis='both', labelsize=10)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"Figur lagret: {output_path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print(f"\n{'='*60}")
    print("STEG 2: FORVENTET VERDI PER HANDLING")
    print(f"{'='*60}")

    df = pd.read_csv(DATA_DIR / 'returned_units.csv')
    result = compute_action_values(df)

    # Lagre berikede data
    result.to_csv(OUTPUT_DIR / 'units_with_values.csv', index=False)
    print(f"\nBeriket datasett lagret: {OUTPUT_DIR / 'units_with_values.csv'}")

    # Oppsummering per handling
    summary = {}
    for a in ACTIONS:
        col = f'ev_{a}'
        summary[a] = {
            'mean_ev': round(float(result[col].mean()), 2),
            'median_ev': round(float(result[col].median()), 2),
            'andel_valgt': round(
                float((result['optimal_action'] == a).mean()), 4
            ),
        }
    print("\n--- Gjennomsnittlig EV per handling ---")
    for a, s in summary.items():
        print(f"  {a:>10s}: mean={s['mean_ev']:>9.2f} NOK, andel valgt={s['andel_valgt']:.3f}")

    with open(OUTPUT_DIR / 'step02_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    plot_value_per_action(result, OUTPUT_DIR / 'disp_value_per_action.png')


if __name__ == '__main__':
    main()
