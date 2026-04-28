"""
Steg 6: Anbefaling og konklusjon
================================
Formulerer konkrete anbefalinger for tollstasjonen og belyser
naar rho > 0.85 blir uholdbart.
"""

import json
from pathlib import Path

from step01_datainnsamling import LAMBDA_TRUE, MU_TRUE
from step02_analytisk import mm1_formler

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

# Servicemaal -- maksimal aksepterbar ventetid ved tollstasjonen
WQ_MAKS_MIN = 5.0


def finn_kritisk_rho(mu: float, wq_maks_min: float) -> float:
    """Finn hoyeste rho slik at Wq <= wq_maks_min minutter."""
    wq_maks_timer = wq_maks_min / 60.0
    # Wq = rho / (my - lambda) = rho / (my (1 - rho))  slik at
    # Wq * my * (1 - rho) = rho  =>  Wq*my = rho (1 + Wq*my)
    # => rho = (Wq*my) / (1 + Wq*my)
    rho_krit = (wq_maks_timer * mu) / (1.0 + wq_maks_timer * mu)
    return rho_krit


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    print("\n" + "=" * 60)
    print("STEG 6: ANBEFALING")
    print("=" * 60)

    baseline = mm1_formler(LAMBDA_TRUE, MU_TRUE)
    Wq_min = baseline['Wq'] * 60.0

    rho_krit = finn_kritisk_rho(MU_TRUE, WQ_MAKS_MIN)
    lambda_maks = rho_krit * MU_TRUE

    # Hva skjer om ankomstraten oker med 20 % (hoysesong)?
    lam_ny = LAMBDA_TRUE * 1.20
    scen = mm1_formler(lam_ny, MU_TRUE)

    # Hva trengs i my for aa holde Wq <= 5 min ved lambda = 12 (+20 %)?
    wq_maks_timer = WQ_MAKS_MIN / 60.0
    # Wq = 1 / (my - lambda) * rho = (lambda/my) / (my - lambda)
    # Krav: rho / (my - lambda) <= wq_maks -> my >= lambda + rho/wq_maks
    # Enklere: los for my direkte. La x = my. Wq = lambda / (x (x - lambda)) = wq_maks
    # -> lambda / (x (x - lambda)) = wq_maks -> x^2 - lambda x - lambda/wq_maks = 0
    a = 1.0
    b = -lam_ny
    c = -lam_ny / wq_maks_timer
    my_kreves = (-b + (b ** 2 - 4 * a * c) ** 0.5) / (2.0 * a)

    anbefalinger = {
        'baseline': {
            'lambda': LAMBDA_TRUE,
            'mu': MU_TRUE,
            'rho': round(baseline['rho'], 4),
            'Wq_min': round(Wq_min, 2),
        },
        'servicemaal': {
            'Wq_maks_min': WQ_MAKS_MIN,
            'rho_kritisk': round(rho_krit, 4),
            'lambda_maks': round(lambda_maks, 3),
            'kommentar': (
                f'Ved my = {MU_TRUE}/time kan ankomstraten maksimalt vaere '
                f'{lambda_maks:.2f}/time for aa holde Wq <= {WQ_MAKS_MIN:.0f} min'
            ),
        },
        'scenario_hoysesong': {
            'lambda_ny': round(lam_ny, 3),
            'rho_ny': round(scen['rho'], 4),
            'Wq_min_uten_tiltak': round(scen['Wq'] * 60.0, 2),
            'my_kreves': round(my_kreves, 3),
            'kommentar': (
                f'Om lambda oker fra {LAMBDA_TRUE} til {lam_ny:.1f}/time, '
                f'maa my okes fra {MU_TRUE} til minst {my_kreves:.2f}/time '
                f'for aa holde servicemaalet (dvs. raskere betjening eller '
                f'mer erfaren tollbetjent).'
            ),
        },
        'generell_regel': (
            'For M/M/1: utnyttelse rho > 0,85 gir eksponentielt voksende '
            'ventetid. For rho = 0,90 er Wq = 45 min (my=12); for rho = 0,95 '
            'er Wq = 95 min. Operativt maal bor vaere rho <= 0,8-0,85 '
            'for aa sikre robusthet mot tilfeldig variasjon.'
        ),
    }

    for k, v in anbefalinger.items():
        print(f"\n{k}:")
        print(json.dumps(v, indent=2, ensure_ascii=False))

    path = OUTPUT_DIR / 'step06_results.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(anbefalinger, f, indent=2, ensure_ascii=False)
    print(f"\nResultater lagret: {path}")


if __name__ == '__main__':
    main()
