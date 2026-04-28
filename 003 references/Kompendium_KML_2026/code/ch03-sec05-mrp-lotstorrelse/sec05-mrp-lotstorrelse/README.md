# MRP med lotstorrelse

Eksempel for kap. 3, seksjon 5: Materialbehovsplanlegging (MRP) med lotstorrelse.

## Modeller

- Materialbehovsplanlegging (MRP): BOM-eksplosjon, nettbehov og tidsforskyvning
- Lotstorrelsesmetoder: lot-for-lot (LFL), EOQ, Silver-Meal

## Kjoring

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_mrp_eksplosjon.py
uv run python src/step03_lfl.py
uv run python src/step04_eoq_lotsizing.py
uv run python src/step05_silver_meal.py
uv run python src/step06_sammenligning.py
```
