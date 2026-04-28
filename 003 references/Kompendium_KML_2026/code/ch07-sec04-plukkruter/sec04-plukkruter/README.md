# Plukkruteoptimering (TSP-heuristikker + Ratliff-Rosenthal)

Python-kode for eksempelet i `ch07-lagerdrift/sec04-plukkruter.tex`.

## Struktur

- `step01_datainnsamling.py` - Genererer syntetisk parallell-gang-lager og 500 plukklister
- `step02_s_shape.py` - S-shape (traversal) heuristikk
- `step03_largest_gap.py` - Largest-gap heuristikk
- `step04_return_midpoint.py` - Return + midpoint heuristikker
- `step05_ratliff_rosenthal.py` - Eksakt dynamisk programmering (Ratliff-Rosenthal 1983)
- `step06_sammenligning.py` - Statistisk sammenligning over alle plukklister

Kjør:

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_s_shape.py
uv run python src/step03_largest_gap.py
uv run python src/step04_return_midpoint.py
uv run python src/step05_ratliff_rosenthal.py
uv run python src/step06_sammenligning.py
```
