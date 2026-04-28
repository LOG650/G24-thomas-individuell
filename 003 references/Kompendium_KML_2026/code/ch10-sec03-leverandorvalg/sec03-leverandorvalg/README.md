# AHP + TOPSIS: Leverandørvalg

Python-kode for eksempelet "Leverandørvalg med multikriterieanalyse (AHP + TOPSIS)"
i kapittel 10 av *Kvantitative metoder i logistikk*.

## Struktur

```
src/
  step01_datainnsamling.py     # Definer leverandører, kriterier og ytelsesmatrise
  step02_ahp_vekter.py         # AHP egenvektor-vekter + CI/CR-konsistenssjekk
  step03_topsis.py             # TOPSIS: normalisering, vekting, avstand
  step04_rangering.py          # Endelig rangering og visualisering
  step05_sensitivitet.py       # Sensitivitet på vekter (+/- 20 %)
  step06_anbefaling.py         # Anbefaling under ulike preferanseprofiler
```

## Kjøring

```bash
cd code/ch10-innkjopsoptimalisering/sec03-leverandorvalg
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_ahp_vekter.py
uv run python src/step03_topsis.py
uv run python src/step04_rangering.py
uv run python src/step05_sensitivitet.py
uv run python src/step06_anbefaling.py
```
