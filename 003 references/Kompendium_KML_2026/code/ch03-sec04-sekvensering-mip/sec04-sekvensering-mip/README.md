# Sekvensering med MIP og heuristikker

Kode for eksempel i `latex/200-bodymatter/part02-omrader/ch03-produksjonsplanlegging/sec04-sekvensering-mip.tex`.

## Installasjon

```bash
uv sync
```

## Kjoring

```bash
uv run python src/step01_datainnsamling.py
uv run python src/step02_dispatch_heuristikker.py
uv run python src/step03_mip_formulering.py
uv run python src/step04_mip_losning.py        # ca. 20 s
uv run python src/step05_simulated_annealing.py # ca. 25 s
uv run python src/step06_sammenligning.py
```

## Output

Figurer lagres i `output/seqmip_*.png` og kopieres til
`latex/.../ch03-produksjonsplanlegging/figures/`.

Numeriske resultater lagres som JSON i `output/step*.json`.

## Instanser

- **Liten (N = 6):** Dagsplan. Loses eksakt med CBC, bevist optimum.
- **Stor (N = 50):** Ukesoppdrag. MIP er upraktisk; brukes SA og dispatch-regler.
