# M/M/1-kømodell

Kode som genererer figurer og resultater for sec03-mm1-model i Ch06.
Kjoer stegene 01-06 i rekkefolge.

```
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_analytisk.py
uv run python src/step03_simulering.py
uv run python src/step04_utnyttelse.py
uv run python src/step05_sensitivitet.py
uv run python src/step06_anbefaling.py
```

Utdata legges i `output/`. Figurer med prefiks `mm1_` kopieres til
`latex/200-bodymatter/part02-omrader/ch06-ko-teori/figures/`.
