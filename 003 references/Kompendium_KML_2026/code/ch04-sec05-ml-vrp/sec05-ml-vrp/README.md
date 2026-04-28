# ML-VRP (Ch04 sec05)

Attention-based pointer network for CVRP, trained on instances solved by an exact MIP solver (PuLP/CBC). Compared against Clarke-Wright savings heuristic and the exact MIP.

## Steps

- `step01_datainnsamling.py` -- generate 1000+ small-VRP instances and solve each with PuLP (CBC) to produce (instance, tour) labels.
- `step02_feature_engineering.py` -- encoder input features (coordinates + demand + depot flag), normalization.
- `step03_modell_arkitektur.py` -- pointer network / simplified attention model (PyTorch).
- `step04_trening.py` -- supervised training (teacher-forced cross-entropy on next-visit).
- `step05_evaluering.py` -- evaluate on held-out instances: gap vs optimum, runtime.
- `step06_sammenligning.py` -- side-by-side comparison vs Clarke-Wright and exact MIP on small/medium/large instances.
- `fig_model_diagrams.py` -- pedagogical schematics for the Modell subsection (attention schematic, pointer decoder step, method diagram).

All outputs are written to `output/`. Figures used by the LaTeX section are additionally copied to `latex/200-bodymatter/part02-omrader/ch04-nettverksdesign/figures/`.
