# LOG650 – Bacheloroppgave: Prosjektforslag

| | |
|---|---|
| **Gruppemedlemmer** | Thomas Ekrem Jensen |
| **Område** | Lagerstyring og innkjøpsoptimalisering |
| **Bedrift** | Helse Vest IKT |

---

## Problemstilling

Helse Vest Forsyningssenter (HVFS) styrer sortiment og lageroppbygging for medisinsk forbruksmateriell i regionen, med NorEngros som operatør. Frem mot 2029 skal sortimentet utvides og avdelingspakkede leveranser (APL) innføres – ferdigpakkede leveranser direkte til avdeling uten mellomlagring.

Prosjektet utvikler et Python-verktøy som klassifiserer artikler ved Helse Bergen forsynings lager og identifiserer kandidater for HVFS-overføring. Verktøyet kombinerer ABC-analyse, beregnet XYZ-klassifisering, EOQ-analyse og klyngeanalyse – velprøvde metoder innen lagerstyring.

**Forskningsspørsmål:** Hvilke artikler bør overføres til HVFS basert på verdi, kritikalitet og forbruksmønster, og hva er forventet årlig besparelse?

---

## Data

Data hentes fra SAP ved Helse Bergen for perioden 2024–2025:

- **Transaksjonsdata:** Innkjøpsordrer og varebevegelser per artikkel, med dato, mengde og verdi.
- **Masterdata:** Artikkelnummer, varebeskrivelse, varegruppe, enhetspris og XYZ-kritikalitetsindikator.
- **Forbrukshistorikk:** Månedlig forbruk per artikkel for beregning av etterspørselsvariabilitet.
- **Estimert datavolum:** 800–1 200 aktive artikler.

---

## Beslutningsvariabler

For hver artikkel skal følgende bestemmes:

| Variabel | Beskrivelse |
|---|---|
| **ABC-klasse** | Klassifisering basert på kumulativ innkjøpsverdi (A, B eller C). |
| **Beregnet XYZ-klasse** | Klassifisering basert på variasjonskoeffisient i etterspørsel (X, Y eller Z). |
| **EOQ-avvik** | Artikler som bestilles oftere enn økonomisk gunstig har høye transaksjonskostnader og er kandidater for HVFS-overføring. |
| **Klyngetilhørighet** | Datadrevet gruppering basert på verdi, variabilitet og ordrefrekvens. Klyngeanalysen identifiserer grupper med høy transaksjonsverdi og lav variabilitet som naturlige HVFS-kandidater. |
| **HVFS-anbefaling** | En regelmotor kombinerer ABC, XYZ, EOQ-avvik og klyngeprofil for å gi anbefaling: *overfør til HVFS*, *behold lokalt*, eller *krever nærmere vurdering*. |

---

## Målfunksjon

Estimert årlig transaksjonskostnadsbesparelse ved HVFS-overføring.

- **Transaksjonskostnad per ordre:** 500–1 000 kroner. Besparelse oppstår ved redusert antall transaksjoner lokalt.
- **Datakvalitet** måles gjennom XYZ-dekningsgrad og samsvar mellom SAP-XYZ og beregnet XYZ.
- **Robusthet** valideres gjennom sensitivitetsanalyse.

---

## Avgrensninger

- Gjelder medisinsk forbruksmateriell ved Helse Bergen. Legemidler, implantater og kostbart utstyr ekskluderes.
- Analyseperiode: 2024–2025.
- Verktøyet er beslutningsstøtte, ikke implementering – det gir anbefalinger.
- XYZ hentes fra SAP der tilgjengelig. Manglende XYZ-dekning rapporteres.
