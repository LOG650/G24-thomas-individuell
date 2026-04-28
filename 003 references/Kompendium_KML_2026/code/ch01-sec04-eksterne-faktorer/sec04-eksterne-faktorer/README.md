# ARIMAX: Eksterne faktorer og kampanjer

Python-prosjektet for kapittel 1, seksjon 4 i "Kvantitative metoder i logistikk".

## Formål

Demonstrere hvordan ARIMAX (ARIMA med eksogene variabler) kan modellere
kampanjeeffekter i daglig dagligvaresalg som en ren SARIMA-modell ikke fanger opp.

## Struktur

- `src/step01_datainnsamling.py`  -- genererer daglig salgsdata med kampanjer
- `src/step02_feature_engineering.py` -- bygger kampanje-features (binær, rabatt, før/etter)
- `src/step03_stasjonaritet.py`    -- ADF-test og differensiering
- `src/step04_modell_estimering.py` -- MLE-estimering av ARIMAX via statsmodels.SARIMAX(exog=...)
- `src/step05_validering.py`       -- residualanalyse, Ljung-Box, backtest mot SARIMA
- `src/step06_prognose.py`         -- baseline- vs kampanjeprognose, scenarioanalyse, priselastisitet

## Kjøring

```
uv sync
cd src
python step01_datainnsamling.py
python step02_feature_engineering.py
python step03_stasjonaritet.py
python step04_modell_estimering.py
python step05_validering.py
python step06_prognose.py
```
