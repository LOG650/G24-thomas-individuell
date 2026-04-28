# Multi-produkt (Q,R) med delt kapasitet

Python-prosjekt for eksempel: Flerprodukts lagerstyring med felles kapasitets- og
budsjettbegrensning, lost via Lagrange-multiplikatorer.

## Oppsett

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_uavhengig_qr.py
uv run python src/step03_modell_formulering.py
uv run python src/step04_optimering.py
uv run python src/step05_validering.py
uv run python src/step06_sensitivitet.py
```

Figurene lagres som `output/multiqr_*.png` og kopieres til
`latex/200-bodymatter/part02-omrader/ch02-lagerstyring/figures/`.
