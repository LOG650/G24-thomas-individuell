"""
Steg 2: Basismodell for 4-trinns forsyningskjede med (s,S)-politikk
===================================================================
Definerer simulatoren. Hvert trinn k = 1..4 (detaljist, grossist,
distributor, fabrikk) bruker en (s,S)-politikk med periodisk
gjennomgang (review period R = 1 uke) og leveringstid L = 2 uker.

For hver uke t:
    1. Motta leveranser som ankommer i uke t.
    2. Lever ut ordren fra trinnet under (eller D_t for detaljisten).
    3. Oppdater etterspoerselsprognose via eksponentiell glatting:
           mu_hat_k(t) = alpha * signal_k(t) + (1 - alpha) * mu_hat_k(t-1)
       der signal_k er trinnets *egen* ordre-inngang (desentralisert)
       eller sluttkundeettersporselen D_t (delt informasjon).
    4. Beregn dynamisk (s, S):
           s_k = mu_hat * (L + R) + z * sigma_hat * sqrt(L + R)
           S_k = s_k + mu_hat * R
    5. Hvis IP_k(t) = lager_k + utestaaende_ordrer <= s_k, bestill
       O_k(t) = S_k - IP_k(t). Ellers O_k(t) = 0.
    6. Logg alle ordrer og lagernivaaer.

Funksjoner
----------
simulate_chain(...) : hovedsimulator
bullwhip_ratios(result, warmup) : Var(O_k) / Var(D) per trinn

Output:
    - output/basismodell.json  (spesifikasjon)
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

OUTPUT_DIR = Path(__file__).parent.parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True)


@dataclass
class Tier:
    """Ett trinn i forsyningskjeden."""
    name: str
    lead_time: int = 2              # L_k (uker)
    review_period: int = 1          # R_k (uker)
    service_z: float = 1.65         # z-verdi (95% servicenivaa)
    initial_inventory: int = 300
    initial_forecast_mean: float = 100.0
    initial_forecast_std: float = 15.0
    smoothing_alpha: float = 0.3    # eksponentiell glatting


def _compute_sS(mu_hat: float, sigma_hat: float, L: int, R: int, z: float) -> tuple[float, float]:
    """Beregn dynamiske (s, S) fra glidende prognose.

    s_k = mu_hat * (L + R) + z * sigma_hat * sqrt(L + R)
    S_k = s_k + mu_hat * R
    """
    s = mu_hat * (L + R) + z * sigma_hat * np.sqrt(L + R)
    S = s + mu_hat * R
    return float(s), float(S)


def simulate_chain(
    demand: np.ndarray,
    tiers: Optional[list[Tier]] = None,
    shared_information: bool = False,
    seed: int = 0,
) -> dict:
    """Simuler en 4-trinns forsyningskjede og returner ordreserier per trinn.

    Parametre
    ---------
    demand : np.ndarray
        Ukentlig sluttkundeettersporsel, lengde T.
    tiers : list[Tier] | None
        Fire Tier-objekter i rekkefolgen detaljist, grossist, distributor,
        fabrikk. Hvis None brukes standardverdier.
    shared_information : bool
        True  -> alle trinn ser D_t og oppdaterer prognosen pa D_t.
        False -> hvert trinn ser kun ordre-inngangen fra trinnet under.
    seed : int
        Reservert (simuleringen er deterministisk gitt demand).
    """
    _ = seed
    T = len(demand)

    if tiers is None:
        tiers = [
            Tier(name='Detaljist'),
            Tier(name='Grossist'),
            Tier(name='Distributor'),
            Tier(name='Fabrikk'),
        ]
    K = len(tiers)

    inv = np.array([float(t.initial_inventory) for t in tiers])
    mu_hat = np.array([t.initial_forecast_mean for t in tiers])
    sigma_hat = np.array([t.initial_forecast_std for t in tiers])

    # Pipeline[k]: liste av (ankomst_uke, kvantum) for trinn k
    pipeline: list[list[tuple[int, float]]] = [[] for _ in range(K)]

    orders_placed = np.zeros((K, T))
    orders_received_from_below = np.zeros((K, T))
    inventory_log = np.zeros((K, T))

    for t in range(T):
        # 1) Motta leveranser som ankommer i uke t
        for k in range(K):
            arrivals = [q for (a, q) in pipeline[k] if a == t]
            inv[k] += sum(arrivals)
            pipeline[k] = [(a, q) for (a, q) in pipeline[k] if a > t]

        d_t = float(demand[t])
        orders_received_from_below[0, t] = d_t

        for k in range(K):
            # Innkommende ordre til trinn k
            if k == 0:
                incoming = d_t
            else:
                incoming = float(orders_placed[k - 1, t])
                orders_received_from_below[k, t] = incoming

            # Lever ut til trinnet under (detaljist -> kunde faller bort,
            # fordi sluttleveransen er direkte)
            delivered = min(inv[k], incoming)
            inv[k] -= delivered
            if k > 0:
                L_below = tiers[k - 1].lead_time
                pipeline[k - 1].append((t + L_below, delivered))

            # Oppdater prognose
            signal = d_t if shared_information else incoming
            mu_new = (
                tiers[k].smoothing_alpha * signal
                + (1 - tiers[k].smoothing_alpha) * mu_hat[k]
            )
            dev = abs(signal - mu_new)
            sigma_hat[k] = (
                tiers[k].smoothing_alpha * dev
                + (1 - tiers[k].smoothing_alpha) * sigma_hat[k]
            )
            sigma_hat[k] = max(sigma_hat[k], 1.0)
            mu_hat[k] = mu_new

            # (s, S)-politikk med periodisk gjennomgang
            s_k, S_k = _compute_sS(
                mu_hat[k], sigma_hat[k],
                tiers[k].lead_time, tiers[k].review_period, tiers[k].service_z,
            )
            outstanding = sum(q for (a, q) in pipeline[k] if a > t)
            IP = inv[k] + outstanding
            if (t % tiers[k].review_period == 0) and IP <= s_k:
                order_qty = max(0.0, S_k - IP)
            else:
                order_qty = 0.0
            orders_placed[k, t] = order_qty

            # Fabrikken produserer selv
            if k == K - 1 and order_qty > 0:
                pipeline[k].append((t + tiers[k].lead_time, order_qty))

            inventory_log[k, t] = inv[k]

    return {
        'T': T,
        'K': K,
        'tier_names': [t.name for t in tiers],
        'orders_placed': orders_placed,
        'orders_received_from_below': orders_received_from_below,
        'inventory': inventory_log,
        'demand': demand.copy(),
        'shared_information': shared_information,
    }


def bullwhip_ratios(result: dict, warmup: int = 10) -> list[float]:
    """Bullwhip-ratio per trinn: Var(O_k) / Var(D) fra uke `warmup` og utover."""
    K = result['K']
    D = result['demand'][warmup:]
    var_d = float(np.var(D, ddof=1))
    ratios = []
    for k in range(K):
        O = result['orders_placed'][k, warmup:]
        var_o = float(np.var(O, ddof=1))
        ratios.append(var_o / var_d if var_d > 0 else float('nan'))
    return ratios


def main() -> None:
    print('\n' + '=' * 60)
    print('STEG 2: BASISMODELL (spesifikasjon)')
    print('=' * 60)

    default_tiers = [Tier(name='Detaljist'), Tier(name='Grossist'),
                     Tier(name='Distributor'), Tier(name='Fabrikk')]

    spec = {
        'antall_trinn': 4,
        'leveringstid_L': default_tiers[0].lead_time,
        'gjennomgangsperiode_R': default_tiers[0].review_period,
        'servicenivaa_z': default_tiers[0].service_z,
        'servicenivaa_prosent': 95,
        'startlager': default_tiers[0].initial_inventory,
        'glatting_alpha': default_tiers[0].smoothing_alpha,
        'trinn': [t.name for t in default_tiers],
    }
    print(json.dumps(spec, indent=2, ensure_ascii=False))

    json_path = OUTPUT_DIR / 'basismodell.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f'\nSpesifikasjon lagret: {json_path}')


if __name__ == '__main__':
    main()
