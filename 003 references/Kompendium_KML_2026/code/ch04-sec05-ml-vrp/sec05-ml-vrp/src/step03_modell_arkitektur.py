"""
Steg 3: Modell-arkitektur (forenklet pointer network med attention)
===================================================================

Inspirert av Kool et al. (2019) "Attention, Learn to Solve Routing Problems!",
men kraftig forenklet slik at treningen gaar paa en CPU i minutter:

  1) En liten 'encoder' (to-lags MLP) tar node-featurene x_i in R^4 og
     produserer embeddings h_i in R^D for i=0..n. Alle nodene (depot +
     kunder) deler samme MLP-vekter.

  2) Decoderen besoeker noder iterativt. Ved hvert steg t holder den paa
     en 'kontekst' c_t basert paa: gjennomsnittet av alle embeddings
     (graph embedding), gjeldende gjenvaerende kapasitet, og embeddingen
     til forrige besoek. En enkelt-hode attention-enhet ser paa alle
     embeddings og gir en logit per node.

  3) En mask fjerner noder som allerede er besoekte og noder hvis demand
     overskrider den gjenvaerende kapasiteten paa kjoerretoyet. Depot er
     altid tillatt (bortsett fra umiddelbart etter et depot-besoek).

Tap = kryss-entropi mot den ekspertdemonstrerte aksjonen i hvert steg
(supervised imitation av den eksakte loesningen).
"""

from __future__ import annotations

import math
from typing import Tuple

import torch
import torch.nn as nn
import torch.nn.functional as F


# ---------------------------------------------------------------
# Encoder
# ---------------------------------------------------------------
class NodeEncoder(nn.Module):
    """Per-node MLP-encoder. Deler vekter mellom alle nodene i grafen."""

    def __init__(self, d_in: int = 4, d_model: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(d_in, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model),
        )

    def forward(self, X: torch.Tensor) -> torch.Tensor:
        """X: (B, N, d_in)  -->  H: (B, N, d_model)"""
        return self.net(X)


# ---------------------------------------------------------------
# Enkel attention-basert pointer decoder
# ---------------------------------------------------------------
class PointerDecoder(nn.Module):
    """Enkelthode attention som peker paa naeste node.

    For hver decoder-steg:
      context_t = [graph_embed ; last_node_embed ; remaining_capacity] -> projiseres til d_model.
      scores_i  = C * tanh((W_q context_t + W_k h_i) . v)   (forenklet)
      scores blir maskerte og gir en kategorisk fordeling over noder.
    """

    def __init__(self, d_model: int = 64, clip: float = 10.0):
        super().__init__()
        self.d_model = d_model
        self.clip = clip
        # Kontekstprojeksjon: input = graph_embed (d) + last_node (d) + capacity (1)
        self.context_proj = nn.Linear(2 * d_model + 1, d_model)
        # Attention-parametre
        self.W_q = nn.Linear(d_model, d_model, bias=False)
        self.W_k = nn.Linear(d_model, d_model, bias=False)
        self.v = nn.Parameter(torch.empty(d_model))
        nn.init.uniform_(self.v, -1.0 / math.sqrt(d_model), 1.0 / math.sqrt(d_model))

    def forward(self, H: torch.Tensor, last_emb: torch.Tensor,
                remaining_cap: torch.Tensor,
                mask: torch.Tensor) -> torch.Tensor:
        """
        H            : (B, N, d_model) node-embeddings
        last_emb     : (B, d_model)    embedding av forrige node
        remaining_cap: (B, 1)          gjenvaerende kapasitet (normalisert)
        mask         : (B, N)          True for tillatte noder, False ellers

        Returnerer log-sannsynligheter: (B, N)
        """
        graph_emb = H.mean(dim=1)  # (B, d)
        context_in = torch.cat([graph_emb, last_emb, remaining_cap], dim=-1)
        q = self.context_proj(context_in)          # (B, d)
        Q = self.W_q(q).unsqueeze(1)               # (B, 1, d)
        K = self.W_k(H)                            # (B, N, d)
        # Enkelthode additiv attention + clipping (Bahdanau-lik)
        scores = self.clip * torch.tanh(
            torch.einsum("bnd,d->bn", torch.tanh(Q + K), self.v)
        )
        scores = scores.masked_fill(~mask, -1e9)
        return F.log_softmax(scores, dim=-1)       # (B, N)


# ---------------------------------------------------------------
# Full pointer network
# ---------------------------------------------------------------
class PointerVRP(nn.Module):
    """End-to-end pointer network for CVRP med supervised aksjonssekvens."""

    def __init__(self, d_in: int = 4, d_model: int = 64):
        super().__init__()
        self.encoder = NodeEncoder(d_in=d_in, d_model=d_model)
        self.decoder = PointerDecoder(d_model=d_model)
        self.d_model = d_model

    def encode(self, X: torch.Tensor) -> torch.Tensor:
        """X: (B, N, d_in)  -->  H: (B, N, d_model)"""
        return self.encoder(X)

    def step_logp(self, H: torch.Tensor, last_idx: torch.Tensor,
                  remaining_cap: torch.Tensor,
                  mask: torch.Tensor) -> torch.Tensor:
        """Ett decoder-steg.

        last_idx: (B,) heltallsindeks for forrige besoek
        """
        B, N, d = H.shape
        last_emb = H[torch.arange(B, device=H.device), last_idx]  # (B, d)
        return self.decoder(H, last_emb, remaining_cap, mask)


# ---------------------------------------------------------------
# Mask-util
# ---------------------------------------------------------------
def build_mask(visited: torch.Tensor, demand: torch.Tensor,
               remaining_cap: torch.Tensor,
               last_was_depot: torch.Tensor) -> torch.Tensor:
    """Beregn gyldighetsmaske for neste aksjon.

    visited         : (B, N) bool (True = allerede besoekt; depot teller
                                     ikke som "oppbrukt")
    demand          : (B, N) int   (depot har demand 0)
    remaining_cap   : (B, 1) float (demand/capacity-enhet)
    last_was_depot  : (B,)  bool

    Returnerer en (B, N) bool-maske: True = tillatt.
    """
    # En kunde er tillatt hvis IKKE besoekt og dens normaliserte demand
    # er <= gjenvaerende kapasitet.
    allowed = (~visited) & (demand <= remaining_cap + 1e-6)
    # Depot er altid tillatt bortsett fra naar vi nettopp returnerte til depot.
    depot_idx = 0
    allowed[:, depot_idx] = True
    # Hvis alle kunder er besoekt, ma vi fortsatt velge depot for aa
    # avslutte -- det er allerede sant over.
    # Dersom siste aksjon var depot OG minst en kunde gjenstaar, skal vi
    # ikke faa lov til aa velge depot paa rad (aksjonen ville da vaere
    # ineffektiv).
    any_customer_left = (~visited[:, 1:]).any(dim=1)  # (B,)
    disallow_depot = last_was_depot & any_customer_left
    allowed[disallow_depot, depot_idx] = False
    return allowed


def compute_tour_distance(coords: torch.Tensor, tour: torch.Tensor) -> torch.Tensor:
    """Totaldistanse for en tour som starter og slutter ved depot.

    coords: (B, N, 2)
    tour:   (B, T)   sekvens av indekser (0 = depot). Vi antar at tour
                     starter naar vi forlater depot og at 0 angir retur.
    Full cykel = depot -> tour[0] -> tour[1] -> ... -> tour[-1].
    Hvis tour[-1] != 0, legges en siste retur til depot.
    """
    B, T = tour.shape
    device = tour.device
    coord_prev = coords[torch.arange(B, device=device)[:, None].expand(-1, 1),
                        torch.zeros(B, 1, dtype=torch.long, device=device)]
    total = torch.zeros(B, device=device)
    for t in range(T):
        idx_t = tour[:, t]
        c_t = coords[torch.arange(B, device=device), idx_t].unsqueeze(1)
        total = total + torch.linalg.norm(coord_prev - c_t, dim=-1).squeeze(1)
        coord_prev = c_t
    # Hvis siste ikke er depot, legg til retur
    last = tour[:, -1]
    coord0 = coords[torch.arange(B, device=device), torch.zeros(B, dtype=torch.long, device=device)]
    diff = torch.linalg.norm(
        coords[torch.arange(B, device=device), last] - coord0, dim=-1)
    # Hvis siste er depot blir diff 0, saa vi kan alltid legge til.
    # For enkelhets skyld gjoer vi det betinget (skip hvis last==0).
    mask_last_not_depot = (last != 0).float()
    total = total + diff * mask_last_not_depot
    return total


if __name__ == "__main__":
    # Selvtest: byg et enkelt tilfelle og verifiser at forward loeper.
    torch.manual_seed(0)
    B, N = 4, 8
    X = torch.rand(B, N, 4)
    X[:, 0, 3] = 1.0  # depot-flag
    model = PointerVRP(d_in=4, d_model=64)
    H = model.encode(X)
    print("H shape:", tuple(H.shape))
    last = torch.zeros(B, dtype=torch.long)
    remaining = torch.ones(B, 1)
    visited = torch.zeros(B, N, dtype=torch.bool)
    visited[:, 0] = True
    demand = torch.rand(B, N) * 0.3
    demand[:, 0] = 0.0
    last_was_depot = torch.ones(B, dtype=torch.bool)
    mask = build_mask(visited, demand, remaining, last_was_depot)
    logp = model.step_logp(H, last, remaining, mask)
    print("logp shape:", tuple(logp.shape))
    print("logp sample:", logp[0].tolist())
    print("number of parameters:",
          sum(p.numel() for p in model.parameters() if p.requires_grad))
