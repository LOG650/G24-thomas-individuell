"""
Steg 2: Feature engineering for ML-VRP
======================================

Konverterer en CVRP-instans til tensorer som encoder-delen av modellen spiser:

  x_i = [coord_x, coord_y, demand_scaled, is_depot]   for i = 0..n

Koordinater ligger allerede i [0,1]^2. Demand normaliseres ved aa dele paa
kapasiteten for aa holde modellen skalafri i kapasitetsendringer.

I tillegg konverteres den optimale ruten (som sekvens av besoek med 0 som
retur-til-depot) til en sekvens av aksjon-tokens:

  a_0 -> a_1 -> ... -> a_T          der a_t in {0, 1, ..., n}

Decoderen skal predikere neste kunde (eller depot) basert paa
(encoder-hidden + state = besoekte kunder + foregaaende aksjon).

Output:
  data/mlvrp_training_tensors.pkl   -- treningsdata som PyTorch-kompatible strukturer
  data/mlvrp_eval_tensors.pkl       -- valideringsdata
  output/step02_results.json        -- oppsummering
"""

from __future__ import annotations

import json
import pickle
from pathlib import Path

import numpy as np

# Viktig: importer dataklassene slik at pickle kan finne dem.
from step01_datainnsamling import VRPInstance, VRPSolution  # noqa: F401

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"


def build_features(instance) -> np.ndarray:
    """Konverter en VRPInstance til en (n+1, 4)-feature-matrise.

    Kolonner: [x, y, demand/capacity, is_depot]
    """
    n = instance.n_customers
    X = np.zeros((n + 1, 4), dtype=np.float32)
    X[:, 0] = instance.coords[:, 0]
    X[:, 1] = instance.coords[:, 1]
    X[:, 2] = instance.demand / instance.capacity
    X[0, 3] = 1.0  # depot
    return X


def tour_to_action_sequence(solution) -> np.ndarray:
    """Gjoer om loesningen til en sekvens av kundeindekser.

    Sluttmarkoeren er depot (0). For en loesning med to ruter [c1,c2] og
    [c3,c4,c5] blir sekvensen [c1, c2, 0, c3, c4, c5, 0].
    """
    return np.array(solution.tour, dtype=np.int64)


def main():
    print("\n" + "=" * 60)
    print("STEG 2: FEATURE ENGINEERING")
    print("=" * 60)

    for split_name, split_file_in, split_file_out in [
        ("trening", "mlvrp_training_instances.pkl", "mlvrp_training_tensors.pkl"),
        ("validering", "mlvrp_eval_instances.pkl", "mlvrp_eval_tensors.pkl"),
    ]:
        with open(DATA_DIR / split_file_in, "rb") as f:
            data = pickle.load(f)

        tensors = []
        for inst, sol in data:
            X = build_features(inst)              # (n+1, 4)
            tour = tour_to_action_sequence(sol)   # (T,)
            tensors.append({
                "X": X,
                "tour": tour,
                "demand": inst.demand.astype(np.int64),
                "capacity": int(inst.capacity),
                "n": int(inst.n_customers),
                "distance": float(sol.distance),
                "coords": inst.coords.astype(np.float32),
            })

        out_path = DATA_DIR / split_file_out
        with open(out_path, "wb") as f:
            pickle.dump(tensors, f)
        print(f"{split_name}: {len(tensors)} instanser  -> {out_path}")

    # Oppsummering
    with open(DATA_DIR / "mlvrp_training_tensors.pkl", "rb") as f:
        train = pickle.load(f)
    tour_lens = [len(t["tour"]) for t in train]
    n_customers = [t["n"] for t in train]

    results = {
        "n_feature_channels": 4,
        "feature_names": ["x", "y", "demand/capacity", "is_depot"],
        "max_tour_length": int(max(tour_lens)),
        "min_tour_length": int(min(tour_lens)),
        "avg_tour_length": round(float(np.mean(tour_lens)), 3),
        "vocab_size": int(max(n_customers) + 1),   # 0..n
    }
    with open(OUTPUT_DIR / "step02_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print("\nOppsummering:")
    for k, v in results.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
