# Multi-echelon lagerstyring (Clark-Scarf)

Kode for eksempel i Ch05 sec04: Clark-Scarf echelon base-stock for et to-trinns
distribusjonsnettverk (1 sentrallager + 4 regionlagre) med stokastisk
etterspørsel per region.

## Struktur

```
src/
  step01_datainnsamling.py     # Parametere, nettverksdiagram
  step02_uavhengig_ss.py       # Uavhengig (s,S) per lager (baseline)
  step03_clark_scarf.py        # Echelon base-stock (analytisk Clark-Scarf)
  step04_simulering.py         # Monte Carlo validering begge politikker
  step05_sensitivitet.py       # Sensitivitet vs ledetid og variabilitet
  step06_sammenligning.py      # Total kostnad og service-sammenligning
output/                        # Figurer og JSON-resultater
```

## Kjøre

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_uavhengig_ss.py
uv run python src/step03_clark_scarf.py
uv run python src/step04_simulering.py
uv run python src/step05_sensitivitet.py
uv run python src/step06_sammenligning.py
```
