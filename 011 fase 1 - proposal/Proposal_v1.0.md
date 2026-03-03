# LOG650 – Bacheloroppgave: Prosjektforslag

| | |
|---|---|
| **Gruppemedlemmer** | Thomas Ekrem Jensen |
| **Område** | Lagerstyring og innkjøpsoptimalisering |
| **Bedrift** | Helse Vest IKT |
| **Versjon** | 1.0 |

---

## Problemstilling

Helse Vest Forsyningssenter (HVFS) styrer sortiment og lageroppbygging for medisinsk forbruksmateriell i regionen, med NorEngros som operatør. Frem mot 2029 skal sortimentet utvides og avdelingspakkede leveranser (APL) innføres – ferdigpakkede leveranser direkte til avdeling uten mellomlagring.

Prosjektet utvikler et Python-verktøy som klassifiserer artikler ved Helse Bergen forsyningslager og identifiserer kandidater for HVFS-overføring. Verktøyet kombinerer ABC-analyse, beregnet XYZ-klassifisering, EOQ-analyse og klyngeanalyse – velprøvde metoder innen lagerstyring.

**Forskningsspørsmål:** Hvilke artikler bør overføres til HVFS basert på verdi, kritikalitet og forbruksmønster, og hva er forventet årlig besparelse?

---

## Data

Data hentes fra SAP S/4HANA ved Helse Bergen for perioden 2024–2025 via SE16H (WERKS 3300, LGORT 3000). Dataspesifikasjonen er definert i 14 tabeller fordelt på fire kategorier:

- **Masterdata:** MARD, MDMA, MARA, MAKT, MARC, MBEW – artikkelunivers, ABC/XYZ-indikatorer, pris og beskrivelse.
- **Forbruksdata:** MSEG (BWART=201+647) – faktisk forbruk ut fra lager til avdeling, månedlig aggregert for CV-beregning.
- **Innkjøpsdata:** EKKO, EKPO, EKBE – innkjøpsordrer og varemottak fra leverandør, brukt til ABC-verdi og EOQ-avvik.
- **Supplerende:** EINA, EINE, T023T – leveringstider og varegruppenavn.

**Viktig distinksjon:**
- MSEG = forbruk **ut** fra lager → XYZ/CV og EOQ etterspørsel D
- EKKO/EKPO/EKBE = innkjøp **inn** til lager → ABC-verdi og EOQ-avvik

**Estimert datavolum:** 800–1 200 aktive artikler.

---

## Beslutningsvariabler

For hver artikkel skal følgende bestemmes:

| Variabel | Beskrivelse |
|---|---|
| **ABC-klasse** | Klassifisering basert på kumulativ innkjøpsverdi fra EKPO.NETWR (A, B eller C). |
| **Beregnet XYZ-klasse** | Klassifisering basert på variasjonskoeffisient (CV = σ/μ) på månedlig forbruk fra MSEG. Valideres mot SAP-XYZ i MDMA.ZZXYZ. |
| **EOQ-avvik** | Artikler som bestilles oftere enn økonomisk gunstig har høye transaksjonskostnader og er kandidater for HVFS-overføring. |
| **Klyngetilhørighet** | Datadrevet gruppering basert på verdi, variabilitet og ordrefrekvens. Klyngeanalysen identifiserer grupper med høy transaksjonsverdi og lav variabilitet som naturlige HVFS-kandidater. |
| **HVFS-anbefaling** | En regelmotor kombinerer ABC, XYZ, EOQ-avvik og klyngeprofil for å gi anbefaling: *overfør til HVFS*, *behold lokalt*, eller *krever nærmere vurdering*. |

---

## Målfunksjon

Estimert årlig transaksjonskostnadsbesparelse ved HVFS-overføring.

- **Transaksjonskostnad per ordre:** 500–1 000 kroner. Besparelse oppstår ved redusert antall transaksjoner lokalt.
- **Datakvalitet** måles gjennom XYZ-dekningsgrad (MDMA.ZZXYZ) og samsvar mellom SAP-XYZ og beregnet XYZ fra MSEG.
- **Robusthet** valideres gjennom sensitivitetsanalyse.

---

## Avgrensninger

- Gjelder medisinsk forbruksmateriell ved Helse Bergen (WERKS 3300, LGORT 3000). Legemidler, implantater og kostbart utstyr ekskluderes via MTART-filter.
- Analyseperiode: 2024–2025.
- Forbruksdata baseres på MSEG (BWART=201+647) – kun forbruk ut fra LGORT 3000, ikke aggregert anleggsnivå.
- Verktøyet er beslutningsstøtte, ikke implementering – det gir anbefalinger.
- XYZ hentes fra MDMA.ZZXYZ der tilgjengelig. Manglende XYZ-dekning rapporteres.

---

*LOG650 · Helse Bergen · WERKS 3300 · LGORT 3000 · v1.0 · Februar 2026*
