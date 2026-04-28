# Bullwhip-simulering (Ch05 sec03)

Simulering av bullwhip-effekten i en 4-trinns forsyningskjede
(detaljist -> grossist -> distributor -> fabrikk).

Kjoring:

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_basismodell.py
uv run python src/step03_desentralisert_simulering.py
uv run python src/step04_delt_informasjon.py
uv run python src/step05_sensitivitet.py
uv run python src/step06_kvantifisering.py
```
