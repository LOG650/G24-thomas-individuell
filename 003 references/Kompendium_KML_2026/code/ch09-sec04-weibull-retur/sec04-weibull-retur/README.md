# Weibull-retur: Returprognoser med levetidsanalyse

Kode for eksempel i kapittel 9 (Returlogistikk), seksjon 4.

## Kjøring

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_eksplorering.py
uv run python src/step03_mle_weibull.py
uv run python src/step04_hazard_analyse.py
uv run python src/step05_prognose.py
uv run python src/step06_validering.py
```

## Innhold

- `data/` syntetisk salgs- og returdata for elektronikkprodukt (Weibull-fordelt levetid)
- `output/` figurer, JSON-resultater og CSV-filer
- `src/` Python-skript for hvert steg i analysen
