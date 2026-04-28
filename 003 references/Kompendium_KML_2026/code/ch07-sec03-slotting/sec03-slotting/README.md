# Slotting: Class-based storage

Eksempelkode for kapittel 7, seksjon 3: Lagerplassering (slotting) med
class-based storage-heuristikk. Datasettet er syntetisk og genereres i
`step01_datainnsamling.py`: 400 SKU-er i et parallell-gang-lager over 90
dager med Pareto-fordelt plukkfrekvens.

## Steg

1. `step01_datainnsamling.py` -- syntetiske plukkdata + lagerlayout
2. `step02_abc_analyse.py` -- ABC-klassifisering med Pareto-prinsippet
3. `step03_tilfeldig_baseline.py` -- tilfeldig tildeling + Monte Carlo
4. `step04_klassebasert.py` -- frekvensbasert tildeling til soner
5. `step05_soneoptimering.py` -- optimal soneinndeling via grid search
6. `step06_sammenligning.py` -- oppsummeringstabell og tidsbesparelse

## Kjoring

```bash
cd code/ch07-lagerdrift/sec03-slotting
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_abc_analyse.py
uv run python src/step03_tilfeldig_baseline.py
uv run python src/step04_klassebasert.py
uv run python src/step05_soneoptimering.py
uv run python src/step06_sammenligning.py
uv run python src/fig_method.py
```
