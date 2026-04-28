# Ch02 sec05 - Data-driven inventory classification

LightGBM multiclass classifier that assigns SKUs to optimal inventory
management classes (continuous monitoring / periodic / make-to-order)
based on rich product features. Compared against traditional ABC-XYZ.

## Pipeline

- `step01_datainnsamling.py` - synthetic SKU dataset
- `step02_feature_engineering.py` - ABC, XYZ, product-level rolling stats
- `step03_datasplitting.py` - time-based train/val/test split
- `step04_modell_estimering.py` - LightGBM multiclass with grid search
- `step05_validering.py` - confusion matrix, macro-F1, baseline comparison
- `step06_tolkning.py` - SHAP + cost simulation vs ABC-XYZ
- `fig_model_diagrams.py` - schematic figures for \subsection{Modell}

## Run

```
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_feature_engineering.py
uv run python src/step03_datasplitting.py
uv run python src/step04_modell_estimering.py
uv run python src/step05_validering.py
uv run python src/step06_tolkning.py
uv run python src/fig_model_diagrams.py
```
