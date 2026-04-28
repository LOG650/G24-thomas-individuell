# Integrert lagerplanlegging

Eksempelkode for ch07 sec05: Integrert bolgeplanlegging, batching og ruteoptimering.

## Modell

- **Bolgeplanlegging**: Tidsindeksert MIP (PuLP/CBC) som tildeler ordrer til bolger under deadline- og pakkekapasitetskrav.
- **Batching**: k-medoids-klynging av ordrer innenfor hver bolge etter plukklokasjoners x-koordinat.
- **Ruter**: Largest-gap-heuristikk for parallell-gang-lager.
- **Evaluering**: SimPy-simulering av en hel dag med 4 planstrategier.

## Kjoring

```
uv sync
uv run python src/step01_datainnsamling.py
uv run python src/step02_bolgeplanlegging_mip.py
uv run python src/step03_batching_kmedoids.py
uv run python src/step04_ruting_largestgap.py
uv run python src/step05_simpy_simulering.py
uv run python src/step06_sammenligning.py
```

## Figurer (prefix intlag_)

- `intlag_orders_timeline.png` --- ordreankomster over dagen
- `intlag_waves.png` --- bolgeinndeling fra MIP
- `intlag_batches_clusters.png` --- k-medoids-batcher i en bolge
- `intlag_pack_queue.png` --- kolengde ved pakkestasjon (SimPy)
- `intlag_simpy_kpi.png` --- KPI-sammenligning: integrert vs 3 baselines
- `intlag_method.png` --- prosessdiagram (AI-generert)
