"""
Steg 6: Anbefaling
==================
Kvantifiserer kost/nytte av mitigasjonstiltakene. Vi legger til
tiltakskostnader (dobbel sourcing = 150 000 NOK/aar i administrasjon,
hoyere sikkerhetslager = 400 ekstra enheter * holding_cost_rate *
cost_unit = 24 000 NOK/aar) og trekker dem fra risikoreduksjonen
(redusert CVaR).

Output:
  - output/mcr_anbefaling.json  : tabell med netto nytte
"""

import json
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / 'output'


# Aarlige administrasjons-/kapitalkostnader ved hvert tiltak
TILTAKSKOSTNAD = {
    'Baseline': 0,
    'Hoyere sikkerhetslager': 24_000,      # 400 ekstra enh * 0.20 * 300
    'Dobbel sourcing': 150_000,            # ekstra admin, revisjon, kontrakt
    'Kombinert tiltak': 24_000 + 150_000,
}


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 6: ANBEFALING MED KOST/NYTTE')
    print('=' * 60)

    with open(OUTPUT_DIR / 'mcr_mitigation.json', 'r', encoding='utf-8') as f:
        mit = json.load(f)

    base = next(s for s in mit['strategies'] if s['name'] == 'Baseline')
    base_cvar = base['metrics']['CVaR_0_95']
    base_mean = base['metrics']['mean']

    rows = []
    for s in mit['strategies']:
        name = s['name']
        mean = s['metrics']['mean']
        var_ = s['metrics']['VaR_0_95']
        cvar = s['metrics']['CVaR_0_95']
        tiltakskost = TILTAKSKOSTNAD[name]
        # Risikoreduksjon: vi bruker CVaR-differanse mot baseline
        risk_reduction = base_cvar - cvar
        mean_reduction = base_mean - mean
        net_benefit = risk_reduction - tiltakskost
        rows.append({
            'name': name,
            'E_C': mean,
            'VaR_0_95': var_,
            'CVaR_0_95': cvar,
            'tiltakskostnad': tiltakskost,
            'CVaR_reduksjon': risk_reduction,
            'E_C_reduksjon': mean_reduction,
            'netto_nytte_CVaR': net_benefit,
            'netto_nytte_EC': mean_reduction - tiltakskost,
        })

    print('\n--- Kost/nytte-tabell ---')
    for r in rows:
        print(f'  {r["name"]:28s}  E[C]={r["E_C"]:>10,.0f}  '
              f'CVaR={r["CVaR_0_95"]:>10,.0f}  '
              f'Red(CVaR)={r["CVaR_reduksjon"]:>+10,.0f}  '
              f'Tiltak={r["tiltakskostnad"]:>7,.0f}  '
              f'Netto={r["netto_nytte_CVaR"]:>+10,.0f}'
              .replace(',', ' '))

    recommendation = max(rows, key=lambda r: r['netto_nytte_CVaR'])
    print(f'\nANBEFALING: {recommendation["name"]}')
    print(f'  Reduserer CVaR med {recommendation["CVaR_reduksjon"]:,.0f} NOK/aar'
          .replace(',', ' '))
    print(f'  Til en aarlig kostnad av {recommendation["tiltakskostnad"]:,.0f} NOK'
          .replace(',', ' '))
    print(f'  Netto nytte (CVaR basert): {recommendation["netto_nytte_CVaR"]:+,.0f} NOK'
          .replace(',', ' '))

    out = {'rows': rows, 'recommendation': recommendation['name']}
    json_path = OUTPUT_DIR / 'mcr_anbefaling.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f'\nResultater lagret: {json_path}')


if __name__ == '__main__':
    main()
