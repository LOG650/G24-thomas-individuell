"""
Felles modelloppsett for robust optimering under usikker etterspoersel.

Alle formuleringer bygger paa den samme andre-trinns LP-en:

  f(z, d) = min  sum_i sum_j c_{ij} x_{ij} + sum_j p_j u_j
            s.t. sum_i x_{ij} + u_j = d_j        for alle j
                 sum_j x_{ij} <= z_i             for alle i
                 x, u >= 0

Total kostnad ved fast z og realisert d:
  C(z, d) = sum_i k_i z_i + f(z, d)

Perfekt-info optimum for realisering d:
  C*(d) = min_z C(z, d)

I dette biblioteket brukes PuLP + CBC for LP-losninger.
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import pulp

DATA_DIR = Path(__file__).parent.parent / 'data'
OUTPUT_DIR = Path(__file__).parent.parent / 'output'


@dataclass
class Instance:
    """Problemdata for nettverksdesignet."""

    df_w: pd.DataFrame      # kolonner: id, navn, kap_kostnad, maks_kap
    df_c: pd.DataFrame      # kolonner: id, navn, naer_hubb, d_bar, delta
    c: np.ndarray           # (n, m) transportkostnad NOK/enhet
    p: np.ndarray           # (m,) straff for usolgt etterspoersel
    k: np.ndarray           # (n,) kapasitetskostnad NOK/enhet
    z_max: np.ndarray       # (n,) maksimal kapasitet
    d_bar: np.ndarray       # (m,) nominell etterspoersel
    delta: np.ndarray       # (m,) usikkerhetsbredde

    @property
    def n(self) -> int:
        return len(self.df_w)

    @property
    def m(self) -> int:
        return len(self.df_c)


def load_instance() -> Instance:
    df_w = pd.read_csv(DATA_DIR / 'warehouses.csv')
    df_c = pd.read_csv(DATA_DIR / 'markets.csv')
    c = pd.read_csv(DATA_DIR / 'transport_cost.csv', index_col=0).to_numpy()
    p = pd.read_csv(DATA_DIR / 'penalty.csv', index_col=0)['penalty'].to_numpy()
    return Instance(
        df_w=df_w, df_c=df_c, c=c, p=p,
        k=df_w['kap_kostnad'].to_numpy(dtype=float),
        z_max=df_w['maks_kap'].to_numpy(dtype=float),
        d_bar=df_c['d_bar'].to_numpy(dtype=float),
        delta=df_c['delta'].to_numpy(dtype=float),
    )


# ---------------------------------------------------------------------------
#  Deterministisk LP: min_z  k'z + f(z, d) med gitt d
# ---------------------------------------------------------------------------
def solve_deterministic(inst: Instance, d: np.ndarray) -> dict:
    """Loeser deterministisk LP med etterspoersel d (1D-array)."""
    n, m = inst.n, inst.m
    model = pulp.LpProblem('DET', pulp.LpMinimize)

    z = [pulp.LpVariable(f'z_{i}', lowBound=0, upBound=inst.z_max[i])
         for i in range(n)]
    x = [[pulp.LpVariable(f'x_{i}_{j}', lowBound=0) for j in range(m)]
         for i in range(n)]
    u = [pulp.LpVariable(f'u_{j}', lowBound=0) for j in range(m)]

    model += (
        pulp.lpSum(inst.k[i] * z[i] for i in range(n))
        + pulp.lpSum(inst.c[i, j] * x[i][j] for i in range(n) for j in range(m))
        + pulp.lpSum(inst.p[j] * u[j] for j in range(m))
    )
    for j in range(m):
        model += (pulp.lpSum(x[i][j] for i in range(n)) + u[j] == float(d[j])), f'bal_{j}'
    for i in range(n):
        model += (pulp.lpSum(x[i][j] for j in range(m)) <= z[i]), f'cap_{i}'

    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', pulp.LpStatus[status]

    z_val = np.array([float(pulp.value(v)) for v in z])
    x_val = np.array([[float(pulp.value(x[i][j]) or 0.0) for j in range(m)]
                      for i in range(n)])
    u_val = np.array([float(pulp.value(v) or 0.0) for v in u])
    return {
        'obj': float(pulp.value(model.objective)),
        'z': z_val,
        'x': x_val,
        'u': u_val,
    }


def cost_at(inst: Instance, z: np.ndarray, d: np.ndarray) -> dict:
    """Beregner C(z, d) = k'z + f(z, d) ved fastlaast z og realisering d.

    Loeser bare andretrinns LP med z gitt.
    """
    n, m = inst.n, inst.m
    model = pulp.LpProblem('RECOURSE', pulp.LpMinimize)
    x = [[pulp.LpVariable(f'x_{i}_{j}', lowBound=0) for j in range(m)]
         for i in range(n)]
    u = [pulp.LpVariable(f'u_{j}', lowBound=0) for j in range(m)]

    model += (
        pulp.lpSum(inst.c[i, j] * x[i][j] for i in range(n) for j in range(m))
        + pulp.lpSum(inst.p[j] * u[j] for j in range(m))
    )
    for j in range(m):
        model += (pulp.lpSum(x[i][j] for i in range(n)) + u[j] == float(d[j]))
    for i in range(n):
        model += (pulp.lpSum(x[i][j] for j in range(m)) <= float(z[i]))

    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', pulp.LpStatus[status]

    f_val = float(pulp.value(model.objective))
    fixed = float((inst.k * z).sum())
    u_val = np.array([float(pulp.value(v) or 0.0) for v in u])
    x_val = np.array([[float(pulp.value(x[i][j]) or 0.0) for j in range(m)]
                      for i in range(n)])
    return {
        'fixed': fixed,
        'recourse': f_val,
        'total': fixed + f_val,
        'u': u_val,
        'x': x_val,
    }


# ---------------------------------------------------------------------------
#  Stokastisk LP: min_z k'z + (1/S) sum_s f(z, d^s)
# ---------------------------------------------------------------------------
def solve_stochastic(inst: Instance, scenarios: np.ndarray) -> dict:
    """scenarios: (S, m) etterspoerselsmatrise."""
    n, m = inst.n, inst.m
    S = len(scenarios)
    model = pulp.LpProblem('STOCH', pulp.LpMinimize)

    z = [pulp.LpVariable(f'z_{i}', lowBound=0, upBound=inst.z_max[i])
         for i in range(n)]
    # Andretrinns-variabler per scenario
    x = [[[pulp.LpVariable(f'x_{s}_{i}_{j}', lowBound=0)
           for j in range(m)] for i in range(n)] for s in range(S)]
    u = [[pulp.LpVariable(f'u_{s}_{j}', lowBound=0) for j in range(m)]
         for s in range(S)]

    recourse = [
        pulp.lpSum(inst.c[i, j] * x[s][i][j] for i in range(n) for j in range(m))
        + pulp.lpSum(inst.p[j] * u[s][j] for j in range(m))
        for s in range(S)
    ]
    model += (
        pulp.lpSum(inst.k[i] * z[i] for i in range(n))
        + (1.0 / S) * pulp.lpSum(recourse)
    )
    for s in range(S):
        for j in range(m):
            model += (pulp.lpSum(x[s][i][j] for i in range(n)) + u[s][j]
                      == float(scenarios[s, j]))
        for i in range(n):
            model += (pulp.lpSum(x[s][i][j] for j in range(m)) <= z[i])

    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', pulp.LpStatus[status]

    z_val = np.array([float(pulp.value(v)) for v in z])
    return {
        'obj': float(pulp.value(model.objective)),
        'z': z_val,
    }


# ---------------------------------------------------------------------------
#  Minimax-regret LP:
#    min_{z, t} t
#    s.t.  k'z + f(z, d^s) - Cstar(d^s) <= t    for alle s
#          z <= z_max
#  Utvidet: f(z, d^s) representeres med sine LP-variabler x^s, u^s.
# ---------------------------------------------------------------------------
def solve_minimax_regret(inst: Instance, scenarios: np.ndarray,
                          cstar: np.ndarray) -> dict:
    """scenarios: (S, m); cstar: (S,) perfekt-info-kostnad per scenario."""
    n, m = inst.n, inst.m
    S = len(scenarios)
    model = pulp.LpProblem('MINIMAX_REGRET', pulp.LpMinimize)

    z = [pulp.LpVariable(f'z_{i}', lowBound=0, upBound=inst.z_max[i])
         for i in range(n)]
    x = [[[pulp.LpVariable(f'x_{s}_{i}_{j}', lowBound=0)
           for j in range(m)] for i in range(n)] for s in range(S)]
    u = [[pulp.LpVariable(f'u_{s}_{j}', lowBound=0) for j in range(m)]
         for s in range(S)]
    t = pulp.LpVariable('t', lowBound=0)

    model += t

    for s in range(S):
        for j in range(m):
            model += (pulp.lpSum(x[s][i][j] for i in range(n)) + u[s][j]
                      == float(scenarios[s, j]))
        for i in range(n):
            model += (pulp.lpSum(x[s][i][j] for j in range(m)) <= z[i])
        # Kostnad minus perfekt-info optimum <= t
        cost_s = (pulp.lpSum(inst.k[i] * z[i] for i in range(n))
                  + pulp.lpSum(inst.c[i, j] * x[s][i][j]
                               for i in range(n) for j in range(m))
                  + pulp.lpSum(inst.p[j] * u[s][j] for j in range(m)))
        model += (cost_s - float(cstar[s]) <= t), f'regret_{s}'

    solver = pulp.PULP_CBC_CMD(msg=False)
    status = model.solve(solver)
    assert pulp.LpStatus[status] == 'Optimal', pulp.LpStatus[status]

    z_val = np.array([float(pulp.value(v)) for v in z])
    return {
        'max_regret': float(pulp.value(t)),
        'z': z_val,
    }


# ---------------------------------------------------------------------------
#  Scenariotrekking
# ---------------------------------------------------------------------------
def sample_interior_scenarios(inst: Instance, S: int, seed: int) -> np.ndarray:
    """Uniforme trekk fra boks-usikkerhetsomraadet."""
    rng = np.random.default_rng(seed)
    return inst.d_bar + rng.uniform(-1, 1, size=(S, inst.m)) * inst.delta


def sample_vertex_scenarios(inst: Instance, S: int, seed: int) -> np.ndarray:
    """Hjoerner av boksen (d_j enten minimum eller maksimum)."""
    rng = np.random.default_rng(seed)
    signs = rng.choice([-1, 1], size=(S, inst.m))
    return inst.d_bar + signs * inst.delta
