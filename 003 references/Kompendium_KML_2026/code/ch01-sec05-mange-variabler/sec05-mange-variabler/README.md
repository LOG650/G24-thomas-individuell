# LightGBM: Etterspørselsprognoser med mange variabler

Python-prosjektet for kapittel 1, seksjon 5 i "Kvantitative metoder i logistikk".

## Formål

Demonstrere hvordan en gradient boosting-modell (LightGBM) kan utnytte
hundrevis av variabler og ikke-lineære sammenhenger som SARIMA/ARIMAX
ikke kan fange opp. Sammenligner mot naiv baseline, glidende gjennomsnitt
og SARIMA, og bruker SHAP-verdier for tolkning.

## Struktur

- `src/step01_datainnsamling.py`      -- genererer SKU-panel med pris, vær, kampanje osv.
- `src/step02_feature_engineering.py` -- bygger 100+ features (lag, rulleande, kalender, produkt, vær)
- `src/step03_datasplitting.py`       -- tidsseriebasert train/val/test-splitt
- `src/step04_modell_estimering.py`   -- LightGBM + hyperparametertuning
- `src/step05_validering.py`          -- evaluering mot baseline, MA og SARIMA
- `src/step06_tolkning.py`            -- SHAP-analyse og prognoseplot

## Kjøring

```
uv sync
cd src
python step01_datainnsamling.py
python step02_feature_engineering.py
python step03_datasplitting.py
python step04_modell_estimering.py
python step05_validering.py
python step06_tolkning.py
```
