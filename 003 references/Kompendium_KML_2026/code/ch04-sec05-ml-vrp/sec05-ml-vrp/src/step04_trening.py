"""
Steg 4: Trening av pointer-modellen med supervised learning
============================================================

Vi leerer modellen aa imitere den eksakt-loesningsmaskinen fra steg 1 via
teacher forcing: paa hvert tidssteg t i tour-sekvensen peker modellen paa
den "riktige" neste node og vi tar kryss-entropi mot det aksjon-labelen.

Det gaar raskt fordi decoder-rullingen er kort (maks ca.\ 10 steg), og
modellen er liten.

Output:
  output/mlvrp_model.pt            -- trente vekter
  output/mlvrp_training_log.json   -- tap per epoke
  output/mlvrp_training_curve.png  -- kurve for trenings- og valideringstap
"""

from __future__ import annotations

import json
import pickle
import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

from step03_modell_arkitektur import PointerVRP, build_mask

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Hyperparametere
D_MODEL = 64
BATCH_SIZE = 64
LR = 1e-3
EPOCHS = 40
SEED = 20260420
DEVICE = torch.device("cpu")


class VRPTensorDataset(Dataset):
    """Paddet dataset: instanser har ulik storrelse, saa vi pader til maks."""

    def __init__(self, tensors, n_max: int, tour_max: int):
        self.items = tensors
        self.n_max = n_max
        self.tour_max = tour_max

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        it = self.items[idx]
        n = it["n"]                      # antall kunder
        N = n + 1                        # noder inkl depot
        # Pad features til (n_max+1, 4). Pad-noder flagges slik at de
        # aldri blir valgt av masken.
        X = np.zeros((self.n_max + 1, 4), dtype=np.float32)
        X[:N] = it["X"]
        demand = np.zeros(self.n_max + 1, dtype=np.int64)
        demand[:N] = it["demand"]
        coords = np.zeros((self.n_max + 1, 2), dtype=np.float32)
        coords[:N] = it["coords"]
        node_mask = np.zeros(self.n_max + 1, dtype=bool)
        node_mask[:N] = True             # True = node finnes
        tour = np.zeros(self.tour_max, dtype=np.int64)
        T = len(it["tour"])
        tour[:T] = it["tour"]
        tour_len = T
        return {
            "X": torch.from_numpy(X),
            "demand": torch.from_numpy(demand),
            "coords": torch.from_numpy(coords),
            "node_mask": torch.from_numpy(node_mask),
            "tour": torch.from_numpy(tour),
            "tour_len": torch.tensor(tour_len, dtype=torch.long),
            "capacity": torch.tensor(float(it["capacity"])),
            "n": torch.tensor(n, dtype=torch.long),
            "distance": torch.tensor(it["distance"], dtype=torch.float32),
        }


def compute_loss(model: PointerVRP, batch) -> torch.Tensor:
    """Teacher-forced kryss-entropi over tour-sekvensen."""
    X = batch["X"].to(DEVICE)
    demand = batch["demand"].to(DEVICE)
    node_mask = batch["node_mask"].to(DEVICE)
    tour = batch["tour"].to(DEVICE)
    tour_len = batch["tour_len"].to(DEVICE)
    capacity = batch["capacity"].to(DEVICE)

    B, N, _ = X.shape
    H = model.encode(X)

    # Normaliser demand per batch basert paa egen kapasitet
    demand_norm = demand.float() / capacity.view(-1, 1)  # (B, N)

    # State
    visited = torch.zeros(B, N, dtype=torch.bool, device=DEVICE)
    visited[:, 0] = True  # depot markert som "besoekt" (men alltid tillatt igjen via build_mask)
    # Reflekter faktisk: for CVRP regnes depot som "ikke oppbrukt". Vi
    # hindrer gjentatte depot-besoek via last_was_depot-sjekken.
    visited[:, 0] = False
    last_idx = torch.zeros(B, dtype=torch.long, device=DEVICE)
    remaining_cap = torch.ones(B, 1, device=DEVICE)
    last_was_depot = torch.ones(B, dtype=torch.bool, device=DEVICE)

    T_max = tour.shape[1]
    total_nll = torch.zeros(B, device=DEVICE)
    steps = torch.zeros(B, device=DEVICE)

    # Maskere ut padded noder alltid
    pad_mask_base = node_mask  # (B, N) True = node finnes

    for t in range(T_max):
        active = (t < tour_len)
        if not active.any():
            break
        action = tour[:, t]             # (B,)
        # Bygg mask for noder som er gyldige ut fra state
        mask_valid = build_mask(visited, demand_norm, remaining_cap,
                                last_was_depot)
        # AND med pad-mask (paddede noder er aldri gyldige)
        mask_valid = mask_valid & pad_mask_base
        # Hvis aksjonen skulle vaere 0 naar alle kunder er besoekt og
        # last_was_depot er True, tillat depot.
        # Edge: hvis mask er all-False for en batch-rad (burde ikke skje),
        # tillat aksjonen slik at log_softmax ikke blir NaN.
        needs_fallback = mask_valid.sum(dim=1) == 0
        if needs_fallback.any():
            mask_valid[needs_fallback, action[needs_fallback]] = True

        logp = model.step_logp(H, last_idx, remaining_cap, mask_valid)  # (B, N)
        nll_step = -logp.gather(1, action.unsqueeze(1)).squeeze(1)      # (B,)
        total_nll = total_nll + nll_step * active.float()
        steps = steps + active.float()

        # Oppdater state etter aksjonen
        is_depot = (action == 0)
        # Trekk demand fra gjenvaerende kapasitet for ikke-depot-besoek
        action_demand = demand_norm.gather(1, action.unsqueeze(1))  # (B,1)
        remaining_cap = torch.where(
            is_depot.unsqueeze(1), torch.ones_like(remaining_cap),
            remaining_cap - action_demand
        )
        # Marker besoekt (depot paavirker ikke visited)
        upd = torch.zeros_like(visited)
        upd.scatter_(1, action.unsqueeze(1), True)
        # Bare for ikke-depot: sett visited=True
        upd[:, 0] = False
        visited = visited | upd
        last_idx = action
        last_was_depot = is_depot

    # Gjennomsnitt per-steg-tap
    return (total_nll / steps.clamp(min=1.0)).mean()


def main():
    print("\n" + "=" * 60)
    print("STEG 4: TRENING AV POINTER-MODELLEN")
    print("=" * 60)

    with open(DATA_DIR / "mlvrp_training_tensors.pkl", "rb") as f:
        train = pickle.load(f)
    with open(DATA_DIR / "mlvrp_eval_tensors.pkl", "rb") as f:
        val = pickle.load(f)

    n_max = max(t["n"] for t in train + val)
    tour_max = max(len(t["tour"]) for t in train + val)
    print(f"n_max={n_max}, tour_max={tour_max}, |train|={len(train)}, |val|={len(val)}")

    torch.manual_seed(SEED)
    np.random.seed(SEED)

    train_ds = VRPTensorDataset(train, n_max, tour_max)
    val_ds = VRPTensorDataset(val, n_max, tour_max)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    model = PointerVRP(d_in=4, d_model=D_MODEL).to(DEVICE)
    opt = torch.optim.Adam(model.parameters(), lr=LR)

    history = {"epoch": [], "train_loss": [], "val_loss": []}
    t0 = time.time()
    best_val = float("inf")
    for epoch in range(1, EPOCHS + 1):
        model.train()
        train_losses = []
        for batch in train_loader:
            opt.zero_grad()
            loss = compute_loss(model, batch)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 2.0)
            opt.step()
            train_losses.append(loss.item())
        model.eval()
        val_losses = []
        with torch.no_grad():
            for batch in val_loader:
                val_losses.append(compute_loss(model, batch).item())
        tr = float(np.mean(train_losses))
        vl = float(np.mean(val_losses))
        history["epoch"].append(epoch)
        history["train_loss"].append(tr)
        history["val_loss"].append(vl)
        improved = vl < best_val
        if improved:
            best_val = vl
            torch.save({
                "model_state": model.state_dict(),
                "d_model": D_MODEL,
                "n_max": n_max,
                "tour_max": tour_max,
            }, OUTPUT_DIR / "mlvrp_model.pt")
        marker = " *" if improved else "  "
        print(f"Epoch {epoch:3d} | train {tr:.4f} | val {vl:.4f}{marker}"
              f" | {time.time()-t0:6.1f}s")

    # Kurver
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    ax.plot(history["epoch"], history["train_loss"], "-o", color="#1F6587",
            label="Trening", markersize=4)
    ax.plot(history["epoch"], history["val_loss"], "-s", color="#9C540B",
            label="Validering", markersize=4)
    ax.set_xlabel("Epoke", fontsize=12)
    ax.set_ylabel("Gjennomsnittlig kryss-entropi per tidssteg", fontsize=11)
    ax.set_title(f"Treningskurve (pointer-modell, {sum(p.numel() for p in model.parameters())} params)",
                 fontsize=12, fontweight="bold")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=10)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "mlvrp_training_curve.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    plt.close()

    with open(OUTPUT_DIR / "mlvrp_training_log.json", "w", encoding="utf-8") as f:
        json.dump({
            "hyperparameters": {
                "d_model": D_MODEL,
                "batch_size": BATCH_SIZE,
                "lr": LR,
                "epochs": EPOCHS,
                "seed": SEED,
            },
            "history": history,
            "best_val_loss": best_val,
            "total_train_time_s": round(time.time() - t0, 2),
            "n_parameters": sum(p.numel() for p in model.parameters()),
        }, f, indent=2, ensure_ascii=False)
    print(f"\nFerdig trening. Beste valideringstap: {best_val:.4f}")
    print(f"Total tid: {time.time() - t0:.1f} s")


if __name__ == "__main__":
    main()
