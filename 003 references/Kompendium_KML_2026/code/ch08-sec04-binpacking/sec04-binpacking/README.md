# Bin Packing (emballasjeoptimering)

Kode for Ch08 sec04 - eksempel pa 1D/2D bin packing med FFD og BFD heuristikker.

## Struktur

- `src/step01_datainnsamling.py`  - genererer 80 produkter med realistiske dimensjoner og vekt
- `src/step02_naiv_pakking.py`    - first-fit i ankomstrekkefolge (baseline)
- `src/step03_ffd.py`             - First-Fit Decreasing (etter volum)
- `src/step04_bfd.py`             - Best-Fit Decreasing
- `src/step05_2d_shelves.py`      - 2D shelf-packing for visualisering
- `src/step06_sammenligning.py`   - kontinuerlig nedre grense, gap, transportbesparelse

## Kjoring

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_naiv_pakking.py
uv run python src/step03_ffd.py
uv run python src/step04_bfd.py
uv run python src/step05_2d_shelves.py
uv run python src/step06_sammenligning.py
```
