"""
Steg 6: Anbefaling
==================
Sammenstiller naekeltall fra steg 4 og 5 til en konkret anbefaling for det
reverse nettverket: hvilke innsamlingssentre og gjenvinningsanlegg som bor
aapnes, hvilke volumer og avstander som kreves, og hvor robust loesningen
er for vekst og parameterusikkerhet.
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
    df_flow2 = pd.read_csv(OUTPUT_DIR / 'step04_flow_l2.csv')

    # Gruppere tildeling per innsamlingssenter
    grp_is = df_assign.groupby('IS_navn').agg(
        antall_kunder=('kunde', 'count'),
        returvolum_tonn=('returvolum_tonn', 'sum'),
        snittavstand_km=('avstand_km', 'mean'),
        maks_avstand_km=('avstand_km', 'max'),
    ).round(1)
    grp_is['returvolum_tonn'] = grp_is['returvolum_tonn'].astype(int)
    grp_is.to_csv(OUTPUT_DIR / 'step06_is_loadings.csv')
    print(f"\nIS-belastninger:\n{grp_is}")

    # Gruppere flyt per gjenvinningsanlegg
    if not df_flow2.empty:
        grp_gv = df_flow2.groupby('GV_navn').agg(
            antall_IS=('IS_id', 'nunique'),
            volum_tonn=('volum_tonn', 'sum'),
            snittavstand_km=('avstand_km', 'mean'),
        ).round(1)
        grp_gv['volum_tonn'] = grp_gv['volum_tonn'].round(1)
        grp_gv.to_csv(OUTPUT_DIR / 'step06_gv_loadings.csv')
        print(f"\nGV-belastninger:\n{grp_gv}")

    # Anbefaling som dict
    def _lookup(seq_values, seq_targets, target):
        idx = seq_values.index(target)
        return seq_targets[idx]

    anbefaling = {
        'totalkostnad_MNOK': s04['obj_MNOK'],
        'antall_IS_aapnes': s04['antall_aapne_IS'],
        'aapne_IS_navn': s04['aapne_IS_navn'],
        'antall_GV_aapnes': s04['antall_aapne_GV'],
        'aapne_GV_navn': s04['aapne_GV_navn'],
        'snitt_avstand_l1_km': s04['snitt_avstand_l1_km'],
        'maks_avstand_l1_km': s04['maks_avstand_l1_km'],
        'snitt_avstand_l2_km': s04['snitt_avstand_l2_km'],
        'total_retur_tonn': s04['total_retur_tonn'],
        'sensitivitet': {
            'rho_0_50_IS_aapne': _lookup(s05['rho_values'], s05['rho_num_open_is'], 0.50),
            'rho_1_00_IS_aapne': _lookup(s05['rho_values'], s05['rho_num_open_is'], 1.00),
            'rho_1_50_IS_aapne': _lookup(s05['rho_values'], s05['rho_num_open_is'], 1.50),
            'rho_1_75_IS_aapne': _lookup(s05['rho_values'], s05['rho_num_open_is'], 1.75),
            'rho_1_75_GV_aapne': _lookup(s05['rho_values'], s05['rho_num_open_gv'], 1.75),
            'beta_0_50_IS_aapne': _lookup(s05['beta_values'], s05['beta_num_open_is'], 0.50),
            'beta_2_00_IS_aapne': _lookup(s05['beta_values'], s05['beta_num_open_is'], 2.00),
            'beta_3_00_IS_aapne': _lookup(s05['beta_values'], s05['beta_num_open_is'], 3.00),
        },
    }
    with open(OUTPUT_DIR / 'step06_anbefaling.json', 'w', encoding='utf-8') as f:
        json.dump(anbefaling, f, indent=2, ensure_ascii=False)

    rapport = [
        "ANBEFALING: reverst nettverk for EE-avfall i Norge",
        "=" * 56,
        f"  Totalkostnad:       {s04['obj_MNOK']:.3f} MNOK/aar",
        f"   - fast innsamling: {s04['fixed_is_MNOK']:.3f} MNOK",
        f"   - fast gjenvinning: {s04['fixed_gv_MNOK']:.3f} MNOK",
        f"   - transport ledd 1: {s04['trans_l1_MNOK']:.3f} MNOK",
        f"   - transport ledd 2: {s04['trans_l2_MNOK']:.3f} MNOK",
        f"   - prosesseringskost: {s04['proc_MNOK']:.3f} MNOK",
        f"  Innsamlingssentre:  {s04['antall_aapne_IS']} ({', '.join(s04['aapne_IS_navn'])})",
        f"  Gjenvinningsanlegg: {s04['antall_aapne_GV']} ({', '.join(s04['aapne_GV_navn'])})",
        f"  Snitt-/maks-avstand ledd 1: {s04['snitt_avstand_l1_km']:.1f} / {s04['maks_avstand_l1_km']:.1f} km",
        f"  Snitt-avstand ledd 2: {s04['snitt_avstand_l2_km']:.1f} km",
        f"  Total retur:        {s04['total_retur_tonn']} tonn/aar",
        "",
        "Sensitivitet (antall aapne innsamlingssentre):",
        f"  rho=0.50 (halvert volum)     -> {anbefaling['sensitivitet']['rho_0_50_IS_aapne']}",
        f"  rho=1.00 (baseline)          -> {anbefaling['sensitivitet']['rho_1_00_IS_aapne']}",
        f"  rho=1.50 (+50 % volum)       -> {anbefaling['sensitivitet']['rho_1_50_IS_aapne']}",
        f"  rho=1.75 (+75 % volum)       -> {anbefaling['sensitivitet']['rho_1_75_IS_aapne']}",
        f"  beta=0.50 (halvert fastkost) -> {anbefaling['sensitivitet']['beta_0_50_IS_aapne']}",
        f"  beta=2.00 (doblet fastkost)  -> {anbefaling['sensitivitet']['beta_2_00_IS_aapne']}",
        f"  beta=3.00 (tredoblet)        -> {anbefaling['sensitivitet']['beta_3_00_IS_aapne']}",
    ]
    print('\n' + '\n'.join(rapport))
    with open(OUTPUT_DIR / 'step06_rapport.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(rapport))


if __name__ == '__main__':
    main()
