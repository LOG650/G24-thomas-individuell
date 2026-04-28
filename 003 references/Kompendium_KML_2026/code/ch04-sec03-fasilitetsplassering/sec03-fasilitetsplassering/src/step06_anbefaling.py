"""
Steg 6: Anbefaling
==================
Samler naekeltall fra steg 4-5 og lagrer en sluttrapport med konkret
anbefaling, inkludert hvilke DC-er aapnes, forventet servicegrad
(snittavstand) og robusthet.
"""

import json
from pathlib import Path

import pandas as pd

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
DATA_DIR = Path(__file__).parent.parent / 'data'


def main() -> None:
    print("\n" + "=" * 60)
    print("STEG 6: ANBEFALING")
    print("=" * 60)

    with open(OUTPUT_DIR / 'step04_summary.json', 'r', encoding='utf-8') as f:
        s04 = json.load(f)
    with open(OUTPUT_DIR / 'step05_summary.json', 'r', encoding='utf-8') as f:
        s05 = json.load(f)

    df_assign = pd.read_csv(OUTPUT_DIR / 'step04_assignment.csv')
    df_dc = pd.read_csv(DATA_DIR / 'kandidater.csv')
    df_cust = pd.read_csv(DATA_DIR / 'kunder.csv')

    # Gruppere tildeling per DC
    grp = df_assign.groupby('DC_navn').agg(
        antall_kunder=('kunde', 'count'),
        etterspoersel=('etterspoersel', 'sum'),
        snittavstand_km=('avstand_km', 'mean'),
        maks_avstand_km=('avstand_km', 'max'),
    ).round(1)
    grp['etterspoersel'] = grp['etterspoersel'].astype(int)
    grp.to_csv(OUTPUT_DIR / 'step06_dc_loadings.csv')
    print(f"\nDC-belastninger:\n{grp}")

    # Anbefaling som dict
    anbefaling = {
        'totalkostnad_MNOK': s04['obj_MNOK'],
        'antall_DC_aapnes': s04['antall_aapne_DC'],
        'aapne_DC_navn': s04['aapne_DC_navn'],
        'andel_fast_pct': s04['andel_fast'],
        'andel_transport_pct': s04['andel_transport'],
        'snittavstand_km': s04['snitt_avstand_km'],
        'maks_avstand_km': s04['maks_avstand_km'],
        'p_star_fra_p_median_sveip': s05['p_star'],
        'sensitivitet': {
            'beta_0_5_n_open': s05['beta_num_open'][s05['beta_values'].index(0.5)],
            'beta_1_0_n_open': s05['beta_num_open'][s05['beta_values'].index(1.0)],
            'beta_2_0_n_open': s05['beta_num_open'][s05['beta_values'].index(2.0)],
            'beta_3_0_n_open': s05['beta_num_open'][s05['beta_values'].index(3.0)],
        },
    }
    with open(OUTPUT_DIR / 'step06_anbefaling.json', 'w', encoding='utf-8') as f:
        json.dump(anbefaling, f, indent=2, ensure_ascii=False)

    # Tekstrapport
    rapport = [
        "ANBEFALING: UFLP for skandinavisk distribusjonsnettverk",
        "=" * 56,
        f"  Totalkostnad:       {s04['obj_MNOK']:.3f} MNOK/aar",
        f"   - faste kostnader: {s04['fixed_cost_NOK']/1e6:.3f} MNOK ({s04['andel_fast']:.1f}%)",
        f"   - transport:       {s04['transport_cost_NOK']/1e6:.3f} MNOK ({s04['andel_transport']:.1f}%)",
        f"  Antall DC aapnes:   {s04['antall_aapne_DC']}",
        f"  DC-lokasjoner:      {', '.join(s04['aapne_DC_navn'])}",
        f"  Snittavstand:       {s04['snitt_avstand_km']:.1f} km",
        f"  Maks avstand:       {s04['maks_avstand_km']:.1f} km",
        "",
        "Sensitivitet - faste kostnader skaleres:",
        f"  beta=0.5  ->  {anbefaling['sensitivitet']['beta_0_5_n_open']} aapne DC-er",
        f"  beta=1.0  ->  {anbefaling['sensitivitet']['beta_1_0_n_open']} aapne DC-er (basis)",
        f"  beta=2.0  ->  {anbefaling['sensitivitet']['beta_2_0_n_open']} aapne DC-er",
        f"  beta=3.0  ->  {anbefaling['sensitivitet']['beta_3_0_n_open']} aapne DC-er",
    ]
    print('\n' + '\n'.join(rapport))
    with open(OUTPUT_DIR / 'step06_rapport.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(rapport))


if __name__ == '__main__':
    main()
