"""
Steg 5: What-if-scenarier
=========================
Sammenligner basismodellen med tre tiltak / scenarier:
  A. Utvid flaskehalsen: pakking far c = 3 parallelle servere (fra 2).
  B. Reduser variabilitet i kvalitetskontrollen (kortere halesannsynlighet).
  C. Ankomsttopp: lambda oker fra 40 til 55 ordrer/time (peak-time).
"""

import json
from pathlib import Path

import numpy as np

from step02_grunnmodell import run_simulation

OUTPUT_DIR = Path(__file__).parent.parent / 'output'

N_ORDERS = 5000
SEED = 2025


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("\n" + "=" * 60)
    print("STEG 5: WHAT-IF-SCENARIER")
    print("=" * 60)

    scenarios = {}

    # Baseline
    print("\n[0] Basismodell ...")
    baseline = run_simulation(n_orders=N_ORDERS, seed=SEED)
    scenarios['baseline'] = baseline

    # A: Ekstra server i pakking (flaskehals)
    print("[A] +1 server pa pakking (c=3) ...")
    res_a = run_simulation(
        n_orders=N_ORDERS, seed=SEED,
        station_overrides={'pakking': {'servers': 3}},
    )
    scenarios['A_extra_server'] = res_a

    # B: Redusert variabilitet i kvalitetskontroll -- bytt lognormal mot
    # uniform med samme gjennomsnitt (1.2 min) og lavere CV.
    print("[B] Redusert variabilitet i kvalitetskontroll (uniform [0.8, 1.6]) ...")
    res_b = run_simulation(
        n_orders=N_ORDERS, seed=SEED,
        station_overrides={
            'kvalitetskontroll': {
                'service_dist': 'uniform',
                'service_params': {'low': 0.8, 'high': 1.6},
            },
        },
    )
    scenarios['B_less_var'] = res_b

    # C: Ankomsttopp til 42 ordrer/time (+5% over basismodellen).
    # Viser hvor sensitivt systemet er nar flaskehalsen allerede er hoyt belastet.
    print("[C] Ankomsttopp lambda = 42 ordrer/time ...")
    res_c = run_simulation(
        n_orders=N_ORDERS, seed=SEED,
        arrival_rate_per_hour=42.0,
    )
    scenarios['C_surge'] = res_c

    # Oppsummer
    print("\nSammenligning:")
    print(f"{'Scenario':25s} {'Throughput':>12s} {'E[V]':>8s} {'P95[V]':>9s} "
          f"{'rho(mott)':>10s} {'rho(kval)':>10s} {'rho(pakk)':>10s} {'rho(uts)':>10s}")
    for name, r in scenarios.items():
        rhos = r['stations']
        print(f"{name:25s} {r['throughput_per_hour']:>12.2f} "
              f"{r['mean_sojourn']:>8.2f} {r['p95_sojourn']:>9.2f} "
              f"{rhos['mottak']['utilization']:>10.3f} "
              f"{rhos['kvalitetskontroll']['utilization']:>10.3f} "
              f"{rhos['pakking']['utilization']:>10.3f} "
              f"{rhos['utsending']['utilization']:>10.3f}")

    # Lagre sammendrag
    summary = {}
    for name, r in scenarios.items():
        summary[name] = {
            'n_orders_completed': r['n_orders_completed'],
            'throughput_per_hour': r['throughput_per_hour'],
            'mean_sojourn': r['mean_sojourn'],
            'p95_sojourn': r['p95_sojourn'],
            'stations': {
                sname: {k: v for k, v in s.items() if k not in ('wait_times', 'sojourn_times')}
                for sname, s in r['stations'].items()
            },
        }
    with open(OUTPUT_DIR / 'step05_whatif.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"\nSammendrag lagret: {OUTPUT_DIR / 'step05_whatif.json'}")

    # Lagre sojourn-fordelinger for figur i steg 6
    np.savez_compressed(
        OUTPUT_DIR / 'step05_sojourns.npz',
        baseline=np.array(scenarios['baseline']['order_sojourn']),
        A=np.array(scenarios['A_extra_server']['order_sojourn']),
        B=np.array(scenarios['B_less_var']['order_sojourn']),
        C=np.array(scenarios['C_surge']['order_sojourn']),
    )


if __name__ == '__main__':
    main()
