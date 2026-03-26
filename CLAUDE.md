# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LOG650 bachelor thesis project** (Høgskolen i Molde, spring 2026) by Thomas Ekrem Jensen. The project develops a Python-based decision support tool for classifying medical consumables at Helse Bergen's supply warehouse (WERKS 3300 / LGORT 3001), identifying candidates for transfer to the regional supply centre (HVFS).

**Research question:** Which articles should be transferred to HVFS based on value, criticality, and consumption pattern, and what is the expected annual savings?

**Partner organisation:** Helse Vest IKT / Helse Bergen Forsyningssenter (HVFS), operated by NorEngros.

## Repository Structure

```
000 templates/          – Report templates (Word), reference style guide (APA 7 Norwegian)
003 references/         – Academic PDFs (23 stk) with per-source .md summaries and OVERSIKT.md
004 data/               – SAP data exports (original MASTERFILE)
005 report/             – Final report source (MD) and Word output
  LOG650_Rapport_FINAL.md          – Master source (Markdown), includes reference list
  LOG650_Rapport.docx              – Final Word document (generated from template)
  build_word.py                    – Script: builds DOCX from template + MD
  wordcount.py                     – Script: counts words in report
  retningslinjer-ki-hjemmeeksamen.md – HiMolde KI guidelines
006 Analyse/            – Python analysis scripts, MASTERFILE, and generated figures
  LOG650_analyse_v2_7.py – Main analysis script (ABC, XYZ, EOQ, K-means, regelmotor)
  plot_*.py             – 12 figure-generating scripts (Fig00–Fig11)
  plots/                – Generated PNG figures (300 dpi)
  MASTERFILE V1.xlsx    – Working data file (709 articles, sheet MASTERFILE, header row 9)
  LOG650_Resultater.xlsx – Generated results (ABC, XYZ, K-means, regelmotor, besparelse)
  LOG650_kmeans_train.csv / _test.csv – Train/test split for K-means
011 fase 1 - proposal/  – Approved project proposal (proposal.md)
012 fase 2 - plan/      – Project management plan, WBS/Gantt
013 fase 3 - review/    – Execution phase
```

## Data

- **MASTERFILE V1.xlsx** – Main data source in `006 Analyse/`. Read with `pd.read_excel(..., sheet_name="MASTERFILE", header=9)`. Contains 709 active articles with columns: MATNR, MAKTX, MTART, MATKL, WGBEZ, MEINS, ZZABC, ZZXYZ, MARC_ABC, UNIT_PRICE, TOTAL_STOCK, D_ANNUAL, ACTIVE_MONTHS, CV, MSEG_STATUS, TOTAL_NETWR, ORDER_COUNT, AVG_ORDER_QTY, NET_RECEIVED, LEAD_TIME_DAYS, SUPPLIER_COUNT.
- **K-means CSV files** – Pre-split train (389) / test (98) sets with computed features: LN_CV, LN_V, LN_DTCABS.

## Analysis Pipeline (implemented)

1. **ABC analysis** – Cumulative purchase value (80/95 % thresholds). A: 182, B: 184, C: 338 articles.
2. **XYZ classification** – CV-based: X (CV < 0.5), Y (0.5–1.0), Z (> 1.0). Computed from D_ANNUAL history.
3. **EOQ deviation** – S = 750 NOK, H = 20 % of unit price, 2-year period (ORDER_COUNT / 2). Threshold ±50 %.
4. **K-means clustering** – K = 3, features: z(ln(CV)), z(ln(v+1)), z(ln(|ΔTC|+1)). Silhouette: 0.383 train / 0.368 test.
5. **Rule engine** – 8 rules (R1–R8): 145 OVERFØR, 257 BEHOLD, 284 TIL VURDERING, 23 MANGLER DATA.
6. **Savings** – Base case kr 452 T/year (g = 75 %), worst kr 301 T, best kr 602 T.

## Figures (12 scripts in `006 Analyse/`)

All scripts use the same style: serif font (DejaVu Serif), `font.size: 10`, title color `#1A2A44`, 300 dpi export.

| Script | Output | Content |
|--------|--------|---------|
| `plot_rammeverk.py` | Fig00_Konseptuelt_Rammeverk.png | Conceptual framework diagram |
| `plot_lagerstruktur.py` | Fig01_Lagerstruktur.png | Warehouse hierarchy diagram |
| `plot_analysepipeline.py` | Fig02_Analysepipeline.png | Analysis pipeline diagram |
| `plot_regelmotor.py` | Fig03_Regelmotor.png | Rule engine flowchart (R1–R8) |
| `plot_dataoversikt.py` | Fig04_Dataoversikt.png | Data overview diagram |
| `plot_abc_pareto.py` | Fig05_ABC_Pareto.png | ABC Pareto diagram |
| `plot_abc_xyz_matrise.py` | Fig06_ABC_XYZ_Matrise.png | ABC/XYZ 3×3 classification matrix |
| `plot_eoq_avvik.py` | Fig07_EOQ_Avvik.png | EOQ deviation scatter + bar |
| `plot_silhouette.py` | Fig08_Silhouette.png | Silhouette score K=2–7 |
| `plot_kmeans_klynger.py` | Fig09_Kmeans_Klynger.png | K-means scatter (2 panels) |
| `plot_kmeans_profil.py` | Fig10_Kmeans_Profil.png | Cluster profile line chart |
| `plot_regelmotor_besparelse.py` | Fig11_Regelmotor_Besparelse.png | Rule engine results + savings |

**Colour palette (consistent across all figures):**
- Green `#1E7D45` – positive / HVFS candidate / optimal
- Orange `#D68910` – review / neutral
- Red `#B03A2E` – negative / keep local / problem
- Blue `#0B3D8C` – analysis / data visualization
- Grey `#888888` – reference lines, secondary elements
- Title `#1A2A44` – all titles and dark text

## Python Environment

- Python 3.13 via `py` launcher (not `python` or `python3` on this machine)
- Key libraries: pandas, numpy, scikit-learn, matplotlib, openpyxl

## Writing Conventions

- **Language:** Norwegian (Bokmål) throughout – all document text, comments in code, and commit messages. Do NOT use nynorsk forms (e.g. "ikkje", "fordelingar", "variablar") — use bokmål consistently ("ikke", "fordelinger", "variabler").
- **References:** APA 7th edition, Norwegian style.
- **Excluded scope:** Pharmaceuticals, implants, and expensive equipment are out of scope. Only medical consumables at Helse Bergen.

## Project Phases & Status

| Phase | Status | Key deliverable |
|-------|--------|-----------------|
| Fase 1 – Initiering | ✅ Complete | Approved proposal |
| Fase 2 – Planlegging | ✅ Complete | Project management plan |
| Fase 3 – Gjennomføring | ✅ Complete | Analysis pipeline, all figures, results |
| Fase 4 – Avslutning | In progress | Final report editing, submission |

## Report Structure

- **Forord** – kort og konsist, ingen detaljert prosjektbeskrivelse
- **Sammendrag** – forkortet, 5 avsnitt, fokus på metode, resultater og konklusjon
- **Abstract** – SLETTET, brukes ikke
- **Kapittel 1–9** – hovedinnhold (se MD-fil for full struktur)
- **Referanseliste** – APA 7, norsk stil
- **Vedlegg A–C** – SAP-dataspesifikasjon, Python-verktøy, KI-erklæring

## Word Document Generation

`005 report/build_word.py` generates the final DOCX from the HiMolde template:
- **Base:** `000 templates/Mal prosjekt LOG650 v2.docx` (cover pages, declarations, privacy, publishing agreement)
- **Content:** Parsed from `LOG650_Rapport_FINAL.md`
- **Math:** LaTeX → MathML (`latex2mathml`) → OMML (`MML2OMML.XSL`) → Word equations
- **Tables:** Three-line format (booktabs): top border, header-bottom border, table-bottom border, no vertical lines
- **Table captions:** Italic, placed UNDER tables (per kompendiet kap. 3.5)
- **Figures:** 12 PNGs from `006 Analyse/plots/` (Fig00–Fig11), caption under (italic)
- **Run:** `cd "005 report" && py build_word.py`
- **Workflow:** MD-filen er kilden. Ved endringer: oppdater MD først, kjør `build_word.py` etterpå.

## Critical Constraints

- The tool provides **decision support only** – it does not implement any warehouse changes.
- XYZ classification uses SAP data where available; missing coverage must be reported explicitly.
- Data quality is validated through 8 checks (D-01 to D-08) documented in the report.
