# sec04 -- M/M/c Erlang-C kapasitetsdimensjonering

Python-prosjekt for eksempelet om kapasitetsdimensjonering av containerterminalkraner
ved Oslo Havn. Eksempelet implementerer Erlang-C-formelen og losser et
kostnadsoptimeringsproblem for a finne optimalt antall kraner.

## Stegstruktur

| Steg  | Script                              | Beskrivelse                                   |
|-------|-------------------------------------|-----------------------------------------------|
| 1     | `step01_datainnsamling.py`          | Ankomst- og betjeningsdata fra containerterminalen |
| 2     | `step02_erlang_c.py`                | Implementer Erlang-C-formelen og sveip over $c$      |
| 3     | `step03_servicedimensjonering.py`   | Minimal $c$ som moter servicekrav                    |
| 4     | `step04_kostnadsoptimering.py`      | Kostnadsoptimal $c$ (kapasitetskost + ventetidskost) |
| 5     | `step05_sensitivitet.py`            | Sensitivitet for ankomstrate (sesongtopper)   |
| 6     | `step06_anbefaling.py`              | Samlet anbefaling og Gantt-plan                      |

## Kjoring

```
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_erlang_c.py
uv run python src/step03_servicedimensjonering.py
uv run python src/step04_kostnadsoptimering.py
uv run python src/step05_sensitivitet.py
uv run python src/step06_anbefaling.py
```
