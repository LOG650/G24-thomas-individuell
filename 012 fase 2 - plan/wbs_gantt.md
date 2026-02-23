# WBS & GANTT-PLAN FOR MS PROJECT

**LOG650 – Bacheloroppgave i logistikk**  
*AI-basert beslutningsstøtte for klassifisering av medisinsk forbruksmateriell*

**Thomas Ekrem Jensen**  
Høgskolen i Molde – Vår 2025  
Dato: Mars 2025 – Versjon 1.2 (CPM-verifisert)

---

## Steg 1 – Arbeidsnedbrytningsstruktur (WBS)

WBS-strukturen er brutt ned fra leveransenivå (prosjektstyringsplanen seksjon 2.5) til konkrete arbeidsoppgaver med estimert varighet. Strukturen følger de fire prosjektfasene definert i LOG650.

### 1.1 Nedbrytningsprinsipper

Hver leveranse fra prosjektplanen er konvertert til én eller flere aktiviteter som kan tilordnes ressurs, estimeres og spores. Nedbrytningen følger disse reglene:

- Aktiviteter på laveste nivå har varighet 1–12 arbeidsdager
- Milepæler har varighet 0 dager og representerer formelle godkjenningspunkt
- Avhengigheter er primært Finish-to-Start (FS)
- Sammendragsoppgaver (summary tasks) grupperer relaterte aktiviteter
- Kritisk sti er markert og utgjør den lengste avhengighetskjeden

### 1.2 Fasestruktur

**Fase 1 – Initiering:** Ferdigstilt. Inkluderer proposal og samarbeidsavtale. Disse oppgavene legges inn med faktiske datoer.

**Fase 2 – Planlegging:** Prosjektstyringsplan, SAP-dataspesifikasjon, litteratursøk, MS Project og GitHub. Flere aktiviteter kjører parallelt etter M1.

**Fase 3 – Gjennomføring:** Tre parallelle arbeidsløp: forskning/teori (3.1), dataanalyse (3.2) og rapportskriving (3.3). Dataanalysen er sekvensiell og utgjør kjernen av kritisk sti.

**Fase 4 – Avslutning:** Fagfellevurdering, revisjon, GitHub-opprydding og endelig innlevering. Inneholder eksplisitt buffer.

---

## Steg 2 – MS Project-tabell

Tabellen nedenfor er klar for direkte innlegging i MS Project. Kolonnene tilsvarer standardfeltene Task Name, Duration og Predecessors. Innrykk indikerer WBS-nivå.

**Forklaring:** Var. = Varighet, Pred. = Forgjenger (Finish-to-Start), MS = Milepæl (★), KS = Kritisk sti (★).  
Farger: **Blå** = sammendrag, **Gul** = milepæl, **Rød** = kritisk sti.

| **WBS** | **Oppgavenavn (Task Name)** | **Var.** | **Pred.** | **MS** | **KS** |
|---|---|---|---|---|---|
| **1** | **FASE 1 – INITIERING** | | | | |
| 1.1 | Utarbeide prosjektforslag (proposal) | 5d | | | ★ |
| 1.2 | Innhente og signere samarbeidsavtale | 3d | 1.1 | | ★ |
| 1.3 | **M1: Proposal godkjent** | 0d | 1.2 | ★ | ★ |
| **2** | **FASE 2 – PLANLEGGING** | | | | |
| 2.1 | Utarbeide prosjektstyringsplan | 10d | 1.3 | | ★ |
| 2.2 | Etablere GitHub-repository med prosjektstruktur | 1d | 1.3 | | |
| 2.3 | Utarbeide SAP-dataspesifikasjon (Vedlegg A) | 5d | 1.3 | | |
| 2.4 | Gjennomføre litteratursøk og etablere referanseliste | 7d | 1.3 | | |
| 2.5 | Opprette detaljert tidsplan i MS Project | 2d | 2.1 | | ★ |
| 2.6 | **M2: Prosjektstyringsplan godkjent av veileder** | 0d | 2.5 | ★ | ★ |
| **3** | **FASE 3 – GJENNOMFØRING** | | | | |
| **3.1** | **FORSKNING OG TEORI** | | | | |
| 3.1.1 | Litteraturgjennomgang (23 kilder) | 12d | 2.6 | | |
| 3.1.2 | Skrive teorikapittel med konseptuelt rammeverk | 5d | 3.1.1 | | |
| **3.2** | **DATA OG ANALYSE** | | | | |
| 3.2.1 | Datautrekk fra SAP iht. spesifikasjon (11 filer) | 3d | 2.6 | | ★ |
| 3.2.2 | Dataforbehandling og kvalitetssikring (7 kontroller) | 4d | 3.2.1 | | ★ |
| 3.2.3 | ABC-analyse med Pareto-diagram | 3d | 3.2.2 | | ★ |
| 3.2.4 | XYZ-klassifisering med CV-beregning og SAP-validering | 3d | 3.2.3 | | ★ |
| 3.2.5 | EOQ-avviksanalyse | 3d | 3.2.3 | | |
| 3.2.6 | K-means klyngeanalyse | 4d | 3.2.4 | | ★ |
| 3.2.7 | Regelmotor og HVFS-anbefalinger | 4d | 3.2.5, 3.2.6 | | ★ |
| 3.2.8 | Besparelsesberegning og sensitivitetsanalyse | 2d | 3.2.7 | | ★ |
| 3.2.9 | **M3: Dataanalyse og Python-verktøy ferdigstilt** | 0d | 3.2.8 | ★ | ★ |
| **3.3** | **RAPPORTSKRIVING** | | | | |
| 3.3.1 | Skrive metodekapittel | 4d | 3.1.2 | | |
| 3.3.2 | Skrive resultatkapittel med visualiseringer | 6d | 3.2.9 | | ★ |
| 3.3.3 | Skrive diskusjonskapittel | 4d | 3.3.2 | | ★ |
| 3.3.4 | Skrive innledning og konklusjon | 3d | 3.3.3 | | ★ |
| 3.3.5 | **M4: Komplett rapportutkast ferdig for review** | 0d | 3.3.1, 3.3.4 | ★ | ★ |
| **4** | **FASE 4 – AVSLUTNING** | | | | |
| 4.1 | Fagfellevurdering av komplett utkast | 5d | 3.3.5 | | ★ |
| 4.2 | Revisjon basert på tilbakemeldinger | 5d | 4.1 | | ★ |
| 4.3 | Buffer / uforutsette oppgaver | 3d | 4.2 | | ★ |
| 4.4 | Sluttkorrektur, APA 7-sjekk og formatering | 3d | 4.3 | | ★ |
| 4.5 | Ferdigstille kode og dokumentasjon på GitHub | 2d | 4.2 | | |
| 4.6 | **M5: Endelig rapport innlevert** | 0d | 4.4, 4.5 | ★ | ★ |

Totalt 37 oppgaver inkludert 5 milepæler og 5 sammendragsoppgaver.

### 2.1 Importinstruksjon for MS Project

1. Åpne MS Project og opprett nytt prosjekt. Sett prosjektstartdato til 6. januar 2025.
2. Legg inn oppgavene fra tabellen over i Task Name-kolonnen.
3. Bruk Indent (Tab-tast) for å opprette sammendragsoppgaver basert på WBS-nivå.
4. Fyll inn Duration og Predecessors fra tabellen. Milepæler settes automatisk med 0d.
5. Fase 1-oppgaver: Sett faktiske datoer (Actual Start / Actual Finish) og marker som 100 % ferdig.
6. Tilordne ressurs «Thomas» til alle oppgaver (Resource Sheet → Resource Name).
7. Kjør Format → Critical Path for å visualisere kritisk linje i rødt.

---

## Steg 3 – Gantt-logikk og kritisk sti

### 3.1 Gjennomføringsrekkefølge

Prosjektet har tre hovedsekvenser som konvergerer mot sluttleveransen:

**Hovedsekvens (kritisk sti):** Proposal (1.1) → Avtale (1.2) → M1 → Prosjektplan (2.1) → MS Project (2.5) → M2 → SAP-utrekk (3.2.1) → Datavask (3.2.2) → ABC (3.2.3) → XYZ (3.2.4) → K-means (3.2.6) → Regelmotor (3.2.7) → Besparelse (3.2.8) → M3 → Resultat (3.3.2) → Diskusjon (3.3.3) → Innledning/konklusjon (3.3.4) → M4 → Review (4.1) → Revisjon (4.2) → Buffer (4.3) → Korrektur (4.4) → M5

**Parallell sekvens A (teori):** M2 → Litteraturgjennomgang (3.1.1) → Teorikapittel (3.1.2) → Metodekapittel (3.3.1). Har 15 dagers slakk da den konvergerer først ved M4.

**Parallell sekvens B (EOQ):** ABC (3.2.3) → EOQ-analyse (3.2.5). Konvergerer ved regelmotor (3.2.7) med 4 dagers slakk. Near-critical – forsinkelse >4d skyver kritisk sti.

**Parallell sekvens C (GitHub):** Revisjon (4.2) → GitHub-opprydding (4.5). Konvergerer ved M5 med 4 dagers slakk.

### 3.2 Kritisk linje

Den kritiske stien har null total slakk (Total Float = 0). Enhver forsinkelse på disse oppgavene vil forskyde innleveringsdatoen direkte.

| **WBS** | **Oppgave på kritisk sti** | **Varighet** |
|---|---|---|
| 1.1 | Utarbeide prosjektforslag | 5d |
| 1.2 | Signere samarbeidsavtale | 3d |
| 1.3 | M1: Proposal godkjent | 0d |
| 2.1 | Prosjektstyringsplan | 10d |
| 2.5 | Detaljert tidsplan i MS Project | 2d |
| 2.6 | M2: Plan godkjent | 0d |
| 3.2.1 | Datautrekk fra SAP | 3d |
| 3.2.2 | Dataforbehandling | 4d |
| 3.2.3 | ABC-analyse | 3d |
| 3.2.4 | XYZ-klassifisering | 3d |
| 3.2.6 | K-means klyngeanalyse | 4d |
| 3.2.7 | Regelmotor | 4d |
| 3.2.8 | Besparelsesberegning | 2d |
| 3.2.9 | M3: Analyse ferdig | 0d |
| 3.3.2 | Resultatkapittel | 6d |
| 3.3.3 | Diskusjonskapittel | 4d |
| 3.3.4 | Innledning og konklusjon | 3d |
| 3.3.5 | M4: Utkast ferdig | 0d |
| 4.1 | Fagfellevurdering | 5d |
| 4.2 | Revisjon | 5d |
| 4.3 | Buffer | 3d |
| 4.4 | Sluttkorrektur | 3d |
| 4.6 | M5: Innlevering | 0d |

**Kritisk sti: 23 oppgaver, 72 arbeidsdager totalt (inkl. 3d buffer). EOQ (3.2.5) er near-critical med TF = 4d.**

### 3.3 Buffer og slakk

Tidsplanen inneholder følgende buffermekanismer. Merk: Buffer (4.3) ligger på kritisk sti, noe som betyr at buffertid telles inn i total prosjektvarighet – dette er et bevisst valg for å absorbere forsinkelser fra veileder-iterasjoner uten å forskyve korrektur og innlevering.

| **Buffertype** | **Estimat** | **Beskrivelse** |
|---|---|---|
| Planlagt buffer (4.3) | 3 dager | På kritisk sti – absorberer veileder-iterasjoner mellom revisjon og korrektur |
| Fase 4 total margin | 18 dager | 3–5. mai til 20. mai gir rom for én ekstra iterasjon |
| «Bør»-krav slakk | 5–10 dager | FK-09 og AK-07 kan droppes for å frigjøre kapasitet |
| Litteratur parallellitet | 15 dager | 3.1.1–3.1.2–3.3.1 kjører parallelt med dataanalyse (TF=15d) |
| EOQ near-critical | 4 dager | 3.2.5 har TF=4d – forsinkelse >4d skyver kritisk sti |

### 3.4 Risikovurdering av tidsplanen

De største risikoene for tidsplanen (ref. prosjektplanens seksjon 4) er:

**R1 (Datakvalitet, score 12):** Direkte på kritisk sti. Dårlig datakvalitet i SAP-utrekk kan forsinke 3.2.1–3.2.2 med opptil 5 dager. Tiltak: SAP-dataspesifikasjonen (Vedlegg A) er ferdigstilt med 7 kvalitetskontroller.

**R4 (Tidspress, score 12):** Påvirker alle faser. Parallelt arbeid med fulltidsstilling gir begrenset daglig kapasitet. Tiltak: Realistisk estimering, prioritering av kritisk linje, og «bør»-krav som kan nedprioriteres.

**R2 (Forsinket datatilgang, score 10):** Kritisk for oppstart fase 3. Tiltak: Bruk anonymisert testdatasett for parallell utvikling. Ferdig dataspesifikasjon gjør at andre kan utføre uttrekket.

---

## Steg 4 – Baseline-strategi

### 4.1 Når baseline skal settes

Baseline settes ved milepæl M2 (Prosjektstyringsplan godkjent av veileder), planlagt 9. mars 2025. På dette tidspunktet er:

- Alle oppgaver definert med varighet og avhengigheter
- Fase 1 ferdigstilt med faktiske datoer
- Prosjektstyringsplanen godkjent av veileder
- Tidsplanen representerer den formelle «kontrakten» for gjennomføring

### 4.2 Hvordan sette baseline i MS Project

Følg denne prosedyren nøyaktig:

1. Gå til **Project → Set Baseline → Set Baseline...**
2. Velg **Baseline (not Baseline 1–10)**
3. Under «For», velg **Entire project**
4. Klikk **OK**
5. Bekreft at Baseline Start / Baseline Finish-kolonner er fylt ut for alle oppgaver

> **Viktig:** Ikke sett baseline på nytt med mindre det er en formelt godkjent endring. Bruk Baseline 1–10 for eventuelle re-baselines slik at opprinnelig baseline bevares for sammenligning.

### 4.3 Tracking Gantt

For å visualisere fremdrift mot baseline, bytt til Tracking Gantt-visningen:

1. Gå til **View → Tracking Gantt**
2. **Grå linjer** viser baseline-plan (opprinnelig tidslinje)
3. **Fargede linjer** viser faktisk fremdrift (blå = på plan, rød = kritisk)
4. Avvik mellom baseline og faktisk er synlig som forskyvning mellom de to linjene

### 4.4 Lese Variance

Variance-feltene i MS Project gir kvantifisert mål på avvik fra baseline:

| **Felt** | **Tolkning** |
|---|---|
| Start Variance | Differanse mellom Baseline Start og Scheduled Start. Positiv verdi = forsinket oppstart. |
| Finish Variance | Differanse mellom Baseline Finish og Scheduled Finish. Kritisk for milepæler – positiv verdi = forsinket leveranse. |
| Duration Variance | Differanse mellom Baseline Duration og Scheduled Duration. Viser om aktiviteten tar lengre tid enn planlagt. |
| Work Variance | Differanse i estimert arbeidsinnsats. Relevant for å justere fremtidige estimater. |

### 4.5 Anbefalt oppfølgingsrutine

For å holde tidsplanen oppdatert og få mest mulig verdi av baseline-sammenligningen, anbefales følgende ukentlige rutine:

1. Oppdater % Complete for alle aktive oppgaver (Task → Update Tasks)
2. Sett Actual Start-dato når oppgaver starter
3. Sett Actual Finish-dato når oppgaver fullføres
4. Sjekk Tracking Gantt for avvik (spesielt på kritisk sti)
5. Legg inn Finish Variance for milepælene i ukentlig statusrapport til veileder
6. Ved signifikant avvik (≥3 dager): Vurder korrigerende tiltak og dokumenter i prosjektloggen

Denne rutinen tar 10–15 minutter per uke og gir solid grunnlag for veilederrapportering samt dokumentasjon av prosjektstyringskompetanse i LOG650-kontekst.
