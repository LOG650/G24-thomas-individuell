# Integrert grønn forsyningskjede

To-trinns stokastisk flermål MIP med epsilon-constraint og scenario-reduksjon.

Kjør stegene:

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_enkeltmal_baselines.py
uv run python src/step03_epsilon_constraint.py
uv run python src/step04_scenario_redusering.py
uv run python src/step05_karbonpris_tipping.py
uv run python src/step06_anbefaling.py
```
