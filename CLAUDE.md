# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LOG650 bachelor thesis project** (Høgskolen i Molde, spring 2025) by Thomas Ekrem Jensen. The project develops a Python-based decision support tool for classifying medical consumables at Helse Bergen's supply warehouse, identifying candidates for transfer to the regional supply centre (HVFS).

**Research question:** Which articles should be transferred to HVFS based on value, criticality, and consumption pattern, and what is the expected annual savings?

**Partner organisation:** Helse Vest IKT / Helse Bergen Forsyningssenter (HVFS), operated by NorEngros.

## Repository Structure

```
000 templates/     – Report templates (Word), reference style guide (APA 7 Norwegian)
001 info/          – (empty – organisational info)
002 meetings/      – Meeting notes, one subfolder per meeting (dd.mm.2026)
003 references/    – Academic PDFs and the APA 7 reference list (Kildeliste_LOG650_APA7.md)
004 data/          – SAP data exports (not yet populated; data extraction pending)
011 fase 1 - proposal/  – Approved project proposal (proposal.md)
012 fase 2 - plan/      – Project management plan, WBS/Gantt (wbs_gantt.md), HTML diagrams
013 fase 3 - review/    – (empty – execution phase)
014 fase 4 - report/    – (empty – final report)
```

## The Python Tool (to be built)

The analysis tool will be written in Python and should implement the following pipeline:

1. **Data ingestion** – SAP exports (~800–1 200 active articles, period 2024–2025): transaction data (POs, goods movements), master data, and monthly consumption history.
2. **ABC analysis** – Classify articles by cumulative purchase value (A/B/C) with Pareto diagram.
3. **XYZ classification** – Compute coefficient of variation (CV) on monthly demand; validate against SAP-provided XYZ indicator. Report coverage gaps.
4. **EOQ deviation analysis** – Identify articles ordered more frequently than economically optimal (high transaction cost → HVFS candidate).
5. **K-means clustering** – Group articles by value, variability, and order frequency. Clusters with high transaction value and low variability are natural HVFS candidates.
6. **Rule engine** – Combine ABC, XYZ, EOQ deviation, and cluster profile → recommendation: *overfør til HVFS* / *behold lokalt* / *krever nærmere vurdering*.
7. **Savings calculation & sensitivity analysis** – Estimated annual transaction cost savings (NOK 500–1 000 per order) with sensitivity ranges.

**Key libraries:** pandas (data structures), scikit-learn (K-means), matplotlib/seaborn (visualisations).

## Writing Conventions

- **Language:** Norwegian (Bokmål) throughout – all document text, comments in code, and commit messages.
- **References:** APA 7th edition, Norwegian style (see `000 templates/Referansestiler/APA 7th norsk v1.12.pdf` and `003 references/Kildeliste_LOG650_APA7.md`).
- **Report template:** Use `000 templates/Mal prosjekt LOG650 v2.docx` as the base.
- **Excluded scope:** Pharmaceuticals, implants, and expensive equipment are out of scope. Only medical consumables at Helse Bergen.

## Project Phases & Status

| Phase | Status | Key deliverable |
|-------|--------|-----------------|
| Fase 1 – Initiering | ✅ Complete | Approved proposal (`011 fase 1 - proposal/proposal.md`) |
| Fase 2 – Planlegging | In progress | Project management plan; WBS/Gantt in `012 fase 2 - plan/` |
| Fase 3 – Gjennomføring | Pending M2 | SAP data extraction, Python tool, theory chapters |
| Fase 4 – Avslutning | Pending | Peer review, final corrections, submission |

Critical path goes through SAP data extraction → preprocessing → ABC → XYZ → K-means → rule engine → results chapter → final submission.

## Critical Constraints

- The tool provides **decision support only** – it does not implement any warehouse changes.
- XYZ classification uses SAP data where available; missing coverage must be reported explicitly.
- Data quality is validated through 7 checks defined in the SAP data specification (Vedlegg A in project management plan).
- Anonymised test data should be used for parallel development while waiting for SAP extraction.
