# Flerlokasjon stokastisk programmering (sec04)

Python-kode for eksempel: "Periodisk gjennomgang (R,S,s) med flerlokasjon,
lateral transshipment og to-trinns stokastisk programmering".

## Kjøring

```bash
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_uavhengig_rss.py
uv run python src/step03_scenariogenerering.py
uv run python src/step04_to_trinns_LP.py
uv run python src/step05_rullerende_horisont.py
uv run python src/step06_sammenligning.py
```

## Struktur

- `data/` genereres i `step01` (syntetisk korrelert etterspørsel)
- `output/` inneholder figurer (`mlstok_*.png`) og JSON-resultater

## Modell

To-trinns stokastisk lineært program:

- Stage 1 (her-og-nå): bestillingsmengde $x_\ell$ per lokasjon
- Stage 2 (etter realisering av etterspørsel $\xi^s$): laterale
  transshipments $y^s_{\ell m}$ mellom lokasjoner, pluss restordre og
  overskuddslager

Scenario-reduksjon (Kantorovich-heuristikk) velger 60 representative
scenariør fra 10 000 genererte.
