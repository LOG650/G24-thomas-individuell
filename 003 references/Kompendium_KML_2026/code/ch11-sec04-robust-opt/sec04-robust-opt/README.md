# Robust optimization: Minimax regret for network design under demand uncertainty

This example compares three approaches for a network design problem:

1. Deterministic baseline (uses nominal demand).
2. Robust minimax-regret counterpart (box uncertainty set).
3. Scenario-based stochastic LP (50 scenarios sampled inside the uncertainty set).

Usage:

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_deterministisk.py
uv run python src/step03_robust.py
uv run python src/step04_stokastisk.py
uv run python src/step05_sammenligning.py
uv run python src/step06_tradeoff.py
```
