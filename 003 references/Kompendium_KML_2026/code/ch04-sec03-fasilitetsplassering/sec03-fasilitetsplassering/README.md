# UFLP: Fasilitetsplassering

Python-prosjekt for kapittel 4, seksjon 3: Ukapasitert fasilitetslokalisering
(Uncapacitated Facility Location Problem, UFLP) loest som MIP med PuLP/CBC.

## Kjoring

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_avstandsmatrise.py
uv run python src/step03_mip_formulering.py
uv run python src/step04_mip_losning.py
uv run python src/step05_sensitivitet.py
uv run python src/step06_anbefaling.py
```
