# Aggregert produksjonsplanlegging via lineær programmering

Pythonkode for eksempelet i `sec03-aggregert-lp.tex` (Ch03, Produksjonsplanlegging).

## Struktur

- `data/` -- inndata (genereres av `step01`).
- `src/step01_datainnsamling.py` -- syntetisk 12-måneders etterspørsel og parametere.
- `src/step02_modell_formulering.py` -- formell LP-formulering med parametertabell.
- `src/step03_lp_losning.py` -- løsning med PuLP (CBC) og `scipy.linprog`.
- `src/step04_sensitivitet.py` -- skyggepriser og sensitivitetsanalyse.
- `src/step05_validering.py` -- stresstest under etterspørsels- og kapasitetssjokk.
- `src/step06_anbefaling.py` -- endelig anbefaling og kostnadssammendrag.

## Kjør

```
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_modell_formulering.py
uv run python src/step03_lp_losning.py
uv run python src/step04_sensitivitet.py
uv run python src/step05_validering.py
uv run python src/step06_anbefaling.py
```
