# Prosjektstyringsplan 1.0

**Fra lokalt forsyningslager til regional sentralforsyning:**
Multikriterieklassifisering og klyngeanalyse for identifisering av overføringskandidater ved Helse Bergen.

| | |
|---|---|
| **Emne:** | LOG650 Forskningsprosjekt: Logistikk og KI |
| **Institusjon:** | Høgskolen i Molde |
| **Utarbeidet av:** | Thomas Ekrem Jensen (prosjektleder) |
| **Veileder:** | Bård Inge Austigard Pettersen |
| **Bedrift:** | Helse Vest IKT |
| **Dato:** | 2025-03-09 |
| **Versjon:** | 1.0 |

*Autorisert av: [Veileder] – Dato: ____.____.2025*

---

## 1 Sammendrag

Denne prosjektstyringsplanen dokumenterer planbaselines for omfang, tidsplan, risiko, ressurser, kommunikasjon og kvalitet for Forskningsprosjekt: Logistikk og KI i LOG650 ved Høgskolen i Molde, vårsemesteret 2026.

### 1.1 Bakgrunn

Helse Vest Forsyningssenter (HVFS) er under etablering som regionalt sentrallager for medisinsk forbruksmateriell, med NorEngros som operatør. Frem mot 2029 skal sortimentet utvides og avdelingspakkede leveranser (APL) innføres. Helse Bergens lokale forsyningslager håndterer i dag 800–1 200 aktive artikler, og det mangler et systematisk, datadrevet grunnlag for å avgjøre hvilke artikler som bør overføres til HVFS.

### 1.2 Problemstilling

Prosjektet besvarer følgende forskningsspørsmål: Hvilke artikler bør overføres til HVFS basert på verdi, kritikalitet og forbruksmønster, og hva er forventet årlig besparelse?

### 1.3 Forskningsdesign

Prosjektet er designet som en kvantitativ deskriptiv casestudie med Helse Bergen forsyningslager som analyseenhet. Tilnærmingen kombinerer velprøvde klassifiseringsmetoder fra lagerstyringslitteraturen (ABC, XYZ, EOQ) med eksplorativ klyngeanalyse (K-means) for å utvikle et datadrevet beslutningsstøtteverktøy. Datagrunnlaget er transaksjon- og masterdata fra SAP S/4HANA for perioden 2024–2025.

### 1.4 Prosjektmål

Å utvikle et Python-basert beslutningsstøtteverktøy som kombinerer ABC-analyse, beregnet XYZ-klassifisering, EOQ-avviksanalyse og K-means klyngeanalyse for å identifisere HVFS-kandidater blant medisinsk forbruksmateriell ved Helse Bergen, med estimert årlig transaksjonskostnadsbesparelse.

### 1.5 Forretningscase

Transaksjonskostnad per ordre estimeres til 500–1 000 kroner. Ved overføring av et signifikant antall artikler til HVFS reduseres antall lokale bestillingstransaksjoner, noe som gir målbare besparelser årlig. Prosjektets kost–nytte-analyse baseres på beregnet transaksjonskostnadsreduksjon som valideres gjennom sensitivitetsanalyse.

### 1.6 Vedleggsoversikt

Prosjektstyringsplanen suppleres av følgende vedlegg som utdyper datamessig og akademisk forankring:

- **Vedlegg A – SAP-dataspesifikasjon:** Komplett tabelloversikt, feltliste, seleksjonskriterier, koblingskart og datakvalitetskontroller for SE16H-uttrekk fra Helse Bergen (WERKS 3300, LGORT 3000).
- **Vedlegg B – Referanseliste:** 23 kilder strukturert i Tier 1 (metodisk kjerne, 10 referanser), Tier 2 (kontekst og metode, 11 referanser) og Programvare (2 referanser), formatert etter APA 7th edition.

---

## 2 Omfang (Scope)

Denne seksjonen definerer prosjektomfanget, inkludert mål, krav, avgrensninger, løsningsbeskrivelse, arbeidsnedbrytningsstruktur og omfangsverifikasjon. Planlegging av tidsplan, risiko og ressurser er basert på denne omfangsdefinisjonen.

### 2.1 Mål og forutsetninger

**Prosjektmål:** Levere en akademisk rapport med tilhørende Python-verktøy som gir datadrevne anbefalinger for artikkeloverføring til HVFS, dokumentert i henhold til LOG650-krav.

**Forutsetninger:**

- Tilgang til anonymiserte SAP-data fra Helse Bergen for perioden 2024–2025 via SE16H. Dataspesifikasjonen i Vedlegg A definerer 10 tabeller med 55+ felt.
- Veileder er tilgjengelig for minimum to veiledningsmøter i perioden.
- Python-miljø med nødvendige biblioteker (pandas, scikit-learn, matplotlib) er tilgjengelig.
- Prosjektet gjennomføres som individuelt arbeid.
- Litteratursøk er gjennomført med 23 identifiserte kilder (Vedlegg B). 6 artikler venter på Molde bibliotek.
- EOQ-holdekostnadssats estimeres til 20 % av enhetspris (bransjetypisk for helsesektor, 15–25 %). Satsen inngår i sensitivitetsanalysen.
- Data inneholder ikke personidentifiserbar informasjon; analysen utføres på artikkelnivå (materialnummer), ikke pasient- eller ansattnivå. Separat NSD-melding er derfor ikke påkrevd.

### 2.2 Krav

#### Funksjonelle krav

| **ID** | **Krav** | **Prioritet** |
|--------|----------|---------------|
| FK-01 | ABC-klassifisering basert på kumulativ innkjøpsverdi (Pareto 80/20) | Må |
| FK-02 | Beregnet XYZ-klassifisering basert på variasjonskoeffisient (CV) | Må |
| FK-03 | EOQ-avviksanalyse som identifiserer artikler med høye transaksjonskostnader | Må |
| FK-04 | K-means klyngeanalyse på normaliserte variabler | Må |
| FK-05 | Regelmotor som kombinerer ABC, XYZ, EOQ og klyngeprofil til HVFS-anbefaling | Må |
| FK-06 | Estimert årlig transaksjonskostnadsbesparelse | Må |
| FK-07 | Sensitivitetsanalyse med variasjon av nøkkelparametere | Må |
| FK-08 | Validering: samsvar mellom SAP-XYZ (MARC.MTVFP) og beregnet XYZ | Må |
| FK-09 | Visualiseringer (Pareto-diagram, klyngeplot og ABC/XYZ-matrise) | Bør |

#### Akademiske krav

| **ID** | **Krav** | **Prioritet** |
|--------|----------|---------------|
| AK-01 | Litteraturgjennomgang med minimum 15 fagfellevurderte kilder (23 identifisert, jf. Vedlegg B) | Må |
| AK-02 | Metodebeskrivelse med begrunnelse for valg av analysemetoder | Må |
| AK-03 | Diskusjon av resultater i lys av teori og praksis | Må |
| AK-04 | Konklusjon med svar på forskningsspørsmålet | Må |
| AK-05 | Formatering i henhold til Høgskolen i Moldes retningslinjer | Må |
| AK-06 | Kildehåndtering med APA 7th edition | Må |
| AK-07 | Reproduserbar kode på GitHub med README | Bør |

### 2.3 Avgrensninger

- Kun medisinsk forbruksmateriell ved Helse Bergen (WERKS 3300, LGORT 3000). Legemidler, implantater og kostbart utstyr ekskluderes via MTART-filter.
- Analyseperiode begrenset til 2024–2025 (MVER.LFGJA, EKKO.BEDAT).
- Verktøyet gir beslutningsstøtte (anbefalinger), ikke implementering av faktisk overføring.
- XYZ-kritikalitet hentes fra SAP (MARC.MTVFP) der tilgjengelig; manglende dekning rapporteres som datakvalitetsmål.
- Prosjektet er et akademisk analyseprosjekt, ikke et IT-implementeringsprosjekt.

### 2.4 Løsningsbeskrivelse

Løsningen består av et Python-basert analyseverktøy med følgende moduler. Datagrunnlaget er spesifisert i Vedlegg A med 10 SAP-tabeller, koblingsnøkler og datakvalitetskontroller.

- **Datainnhenting og forbehandling:** Import av 11 Excel-filer fra SE16H-uttrekk (jf. Vedlegg A, seksjon A.5). Kobling på MATNR som primærnøkkel. Datavask inkluderer PEINH-korreksjon, håndtering av null-priser og negative forbrukstall.
- **ABC-analysemodul:** Klassifisering basert på kumulativ innkjøpsverdi fra EKPO.NETWR, med Pareto-fordeling (A: 80 %, B: 15 %, C: 5 %).
- **XYZ-klassifiseringsmodul:** Beregning av variasjonskoeffisient (CV) på månedlig forbruk fra MVER.VER01–VER12, med terskler X < 0,5, Y: 0,5–1,0, Z > 1,0. Validering mot MARC.MTVFP.
- **EOQ-avviksmodul:** Beregning av Wilson EOQ med årlig etterspørsel (D) fra MVER, bestillingskostnad (S) = 500–1 000 kr, og holdekostnad (H) = enhetspris (MBEW.STPRS/PEINH) × holdekostnadssats (20 %, sensitivitet 15–25 %). Identifisering av artikler med signifikant avvik mellom faktisk og optimal bestillingsfrekvens.
- **Klyngeanalysemodul:** K-means clustering på normaliserte variabler (verdi, variabilitet, ordrefrekvens) med elbow-metoden for optimalt antall klynger.
- **Regelmotor:** Kombinerer ABC, XYZ, EOQ-avvik og klyngeprofil for å gi trevalgs-anbefaling: overfør til HVFS, behold lokalt, eller krever nærmere vurdering.
- **Besparelsesmodul:** Estimerer årlig transaksjonskostnadsreduksjon med sensitivitetsanalyse.

### 2.5 Arbeidsnedbrytningsstruktur (WBS)

WBS er definert på leveransenivå i henhold til prosjektets fire faser. Detaljerte aktiviteter spesifiseres og struktureres i MS Project. Referanser til vedlegg er vist der relevant.

| **WBS-ID** | **Leveranse** | **Fase** | **Vedlegg** |
|------------|---------------|----------|-------------|
| 1.x | Prosjektinitiering | Fase 1 | |
| 1.x | Godkjent prosjektforslag (proposal) | Fase 1 | |
| 1.x | Signert samarbeidsavtale med Helse Vest IKT | Fase 1 | |
| 2.x | Prosjektplanlegging | Fase 2 | |
| 2.x | Prosjektstyringsplan (dette dokumentet) | Fase 2 | |
| 2.x | Detaljert tidsplan i MS Project | Fase 2 | |
| 2.x | Etablert GitHub-repository med prosjektstruktur | Fase 2 | |
| 2.x | SAP-dataspesifikasjon ferdigstilt | Fase 2 | Vedlegg A |
| 2.x | Litteratursøk gjennomført og referanseliste etablert | Fase 2 | Vedlegg B |
| 3.1x | Gjennomføring – Forskning | Fase 3 | |
| 3.1x | Litteraturgjennomgang (23 kilder, jf. Vedlegg B) | Fase 3 | Vedlegg B |
| 3.1x | Teorikapittel med konseptuelt rammeverk | Fase 3 | |
| 3.2x | Gjennomføring – Data og analyse | Fase 3 | |
| 3.2x | Datautrekk fra SAP iht. spesifikasjon (11 filer) | Fase 3 | Vedlegg A |
| 3.2x | Dataforbehandling og kvalitetssikring (7 kontroller) | Fase 3 | Vedlegg A |
| 3.2x | ABC-analyse med Pareto-diagram | Fase 3 | |
| 3.2x | XYZ-klassifisering med CV-beregning og SAP-validering | Fase 3 | |
| 3.2x | EOQ-avviksanalyse | Fase 3 | |
| 3.2x | K-means klyngeanalyse | Fase 3 | |
| 3.2x | Regelmotor og HVFS-anbefalinger | Fase 3 | |
| 3.2x | Besparelsesberegning og sensitivitetsanalyse | Fase 3 | |
| 3.3x | Gjennomføring – Rapportskriving | Fase 3 | |
| 3.3x | Metodekapittel | Fase 3 | |
| 3.3x | Resultatkapittel med visualiseringer | Fase 3 | |
| 3.3x | Diskusjonskapittel | Fase 3 | |
| 3.3x | Innledning og konklusjon | Fase 3 | |
| 4.x | Avslutning | Fase 4 | |
| 4.x | Komplett utkast for fagfellevurdering | Fase 4 | |
| 4.x | Revidert sluttrapport | Fase 4 | |
| 4.x | Kode og dokumentasjon på GitHub | Fase 4 | |
| 4.x | Innlevering og eventuell presentasjon | Fase 4 | |

### 2.6 Omfangsverifikasjon

Leveranser verifiseres og godkjennes gjennom følgende prosess, tilpasset et individuelt akademisk prosjekt:

- **Milepælgodkjenning:** Veileder gjennomgår og godkjenner leveranser ved milepælene M2 (prosjektplan), M4 (rapportutkast) og M5 (endelig rapport). Godkjenning dokumenteres skriftlig.
- **Akseptkriterier for dataanalyse:** (1) Minimum 80 % av aktive artikler skal være klassifisert i alle fire dimensjoner (ABC, XYZ, EOQ, klynge). (2) XYZ-dekningsgrad fra SAP (MARC.MTVFP) skal rapporteres eksplisitt. (3) K-means skal gi meningsfulle klynger validert med silhouette-score > 0,3.
- **Akseptkriterier for rapport:** (1) Forskningsspørsmålet skal være besvart med kvantifisert besparelsesestimat. (2) Alle «må»-krav (FK-01 til FK-08, AK-01 til AK-06) skal være oppfylt. (3) APA 7-formatering bekreftet gjennom korrekturlesning.
- **Selvreview:** Før leveranser sendes til veileder, gjennomfører Thomas en strukturert selvreview mot kravlisten i seksjon 2.2.
- **Avviksrapportering:** Dersom akseptkriterier ikke oppfylles, dokumenteres avviket i ukentlig statusrapport med årsak, konsekvens og korrigerende tiltak.

---

## 3 Tidsplan (Schedule)

Tidsplanen er strukturert i fire faser med definerte milepæler. Detaljert Gantt-plan utarbeides i MS Project basert på WBS-aktivitetene.

### 3.1 Faseoversikt

| **Fase** | **Periode** | **Nøkkelleveranser** | **Milepæl** |
|----------|-------------|----------------------|-------------|
| Fase 1: Initiering | Jan 2025 (ferdig) | Proposal, samarbeidsavtale | M1: Proposal godkjent |
| Fase 2: Planlegging | Feb – 9. mars 2025 | Prosjektstyringsplan, SAP-spesifikasjon, referanseliste, MS Project, GitHub | M2: Plan godkjent (9. mars) |
| Fase 3: Gjennomføring | 10. mars – 2. mai 2025 | Litteratur, datautrekk (11 filer), Python-verktøy, rapportutkast | M3: Analyse ferdig · M4: Utkast ferdig |
| Fase 4: Avslutning | 3. mai – 20. mai 2025 | Fagfellevurdering, revisjon, innlevering | M5: Innlevering |

### 3.2 Detaljert milepælsplan

| **ID** | **Milepæl** | **Planlagt dato** | **Status** |
|--------|-------------|-------------------|------------|
| M1 | Prosjektforslag (proposal) godkjent | Januar 2025 | Ferdig |
| M2 | Prosjektstyringsplan godkjent av veileder | 9. mars 2025 | Under arbeid |
| M2a | SAP-dataspesifikasjon ferdigstilt (Vedlegg A) | Mars 2025 | Ferdig |
| M2b | Referanseliste etablert (Vedlegg B) | Mars 2025 | Ferdig (6 kilder venter) |
| M3 | Dataanalyse og Python-verktøy ferdigstilt | 10. april 2025 | Planlagt |
| M4 | Komplett rapportutkast ferdig for review | 2. mai 2025 | Planlagt |
| M5 | Endelig rapport innlevert | 20. mai 2025 | Planlagt |

### 3.3 Kritisk linje og buffer

Den kritiske linjen for prosjektet går gjennom følgende sekvens: Datautrekk fra SAP (4.1) → Dataforbehandling (4.2) → ABC-analyse (4.3) → XYZ-klassifisering (4.4) → Klyngeanalyse (4.6) → Regelmotor (4.7) → Resultatkapittel (5.2) → Diskusjon (5.3) → Revisjon (6.2) → Innlevering (6.4). Forsinkelse i noen av disse leveransene vil direkte påvirke sluttdatoen.

Litteraturgjennomgang (3.1) og EOQ-analyse (4.5) ligger parallelt og har noe slakk, men bør ferdigstilles før rapportskrivingen starter for å sikre konsistens. Ferdigstillelse av SAP-dataspesifikasjonen (Vedlegg A) i fase 2 reduserer risikoen på den kritiske linjen ved å muliggjøre raskt datautrekk ved oppstart av fase 3.

**Buffer:** Tidsplanen inneholder følgende buffermekanismer: (1) Én ukes buffer mellom M3 og M4 (10.–18. april) for å absorbere forsinkelser på kritisk linje. (2) «Bør»-krav FK-09 og AK-07 kan nedprioriteres og gir ytterligere 1–2 uker kapasitet dersom kritisk-linje-aktiviteter krever mer tid. (3) Fase 4 har 18 dager for review og revisjon, som gir rom for én ekstra iterasjon med veileder.

---

## 4 Risiko

Risikoregisteret er utarbeidet gjennom systematisk gjennomgang av prosjektets avhengigheter, datakvalitet, teknisk kompleksitet og akademiske krav. Risikoene er kvantifisert med sannsynlighet (1–5) og konsekvens (1–5), og risikoscore beregnes som produkt av disse.

*Versjon 1.2: Risikoscore for R1 og R2 er justert ned som følge av at SAP-dataspesifikasjonen (Vedlegg A) er ferdigstilt. R8 lagt til for bibliotektilgang.*

### 4.1 Prosess for risikostyring

Risikoregisteret gjennomgås ukentlig i forbindelse med statusoppdatering. Risikoeier (Thomas) overvåker utløsere og iverksetter tiltak proaktivt. Ved risikomaterialisering aktiveres beredskapsplanen. Veileder konsulteres ved kritiske risikoer.

### 4.2 Risikoregister

| **ID** | **Risiko** | **S** | **K** | **Score** | **Tiltak** | **Beredskap** |
|--------|-----------|-------|-------|-----------|------------|---------------|
| R1 | Mangelfull datakvalitet i SAP-uttrekk (manglende XYZ, ufullstendig forbrukshistorikk) | 3 | 4 | 12 | SAP-dataspesifikasjon ferdigstilt (Vedlegg A) med 7 definerte kvalitetskontroller. Tidlig uttrekk i uke 11. Minimum dekningsgrad for XYZ definert. | Beregn XYZ fra MVER-forbruksdata. Dokumenter dekningsgrad som datakvalitetsmål. Bruk EKBE som alternativ kilde ved MVER-avvik. |
| R2 | Forsinket datatilgang fra Helse Bergen / SAP-autorisasjon | 2 | 5 | 10 | Konkret dataspesifikasjon (Vedlegg A) med tabellnavn, felt og filtre klart til oversendelse. Avklar tilgang med LIBRA-prosjektet før fase 3. | Bruk anonymisert testdatasett for utvikling. Bytt til reelle data når tilgjengelig. Spesifikasjonen muliggjør at andre kan gjøre uttrekket. |
| R3 | Teknisk kompleksitet i K-means (skaleringsproblemer, optimalt K) | 3 | 3 | 9 | Bruk etablerte biblioteker (scikit-learn). Test elbow-metoden tidlig. | Forenkling til ABC/XYZ-matrise uten klyngeanalyse dersom K-means ikke gir meningsfulle resultater. |
| R4 | Tidspress på grunn av parallelt arbeid (jobb + studier) | 4 | 3 | 12 | Realistisk tidsplan med eksplisitt buffer (jf. seksjon 3.3). Prioriter kritisk-linje-aktiviteter. Jobbfri tid i intensive perioder. | Reduser omfang på «bør»-krav (FK-09, AK-07). Fokuser på «må»-krav. |
| R5 | Resultater gir ikke tydelige HVFS-anbefalinger | 2 | 4 | 8 | Definer klare beslutningsregler i regelmotoren. Forankre regler i teori (Vedlegg B, Tier 1-kilder). | Presenter funn som bidrag til videre vurdering. Juster forskningsspørsmål i diskusjonen. |
| R6 | Tap av arbeid (kode, rapport) | 2 | 5 | 10 | Daglig commit til GitHub. Automatisk skylagring av rapport. | Rekonstruksjon fra siste backup. Estimer 2–3 dager tapt arbeid maksimalt. |
| R7 | Veileder utilgjengelig i kritiske perioder | 2 | 3 | 6 | Avtal faste veiledningstidspunkter tidlig. Send statusoppdatering ukentlig. | Bruk skriftlig tilbakemelding via e-post. Utsett veiledningsavhengige beslutninger. |
| R8 | Manglende bibliotektilgang til 6 ventende artikler | 3 | 2 | 6 | Bestilling allerede sendt til Molde bibliotek. Følg opp ukentlig. Prioriter Tier 1-artikler. | Eksisterende 17 tilgjengelige kilder dekker alle analysemetoder. Ventende artikler supplerer, men er ikke kritiske. |

*S = Sannsynlighet (1–5), K = Konsekvens (1–5), Score = S × K. Risikoer med score ≥ 12 krever aktiv oppfølging.*

#### Endringslogg risikoregister

| **Versjon** | **Risiko** | **Endring** | **Begrunnelse** |
|-------------|-----------|-------------|-----------------|
| 1.0 → 1.1 | R1 | S: 4→3, Score: 16→12 | SAP-dataspesifikasjon (Vedlegg A) konkretiserer datakrav og definerer 7 kvalitetskontroller |
| 1.0 → 1.1 | R2 | S: 3→2, Score: 15→10 | Ferdig dataspesifikasjon med tabellnavn og felt reduserer tvetydighet i datatilgangsforespørsel |
| 1.1 | R8 | Ny risiko (score 6) | Identifisert ved etablering av referanseliste – 6 artikler venter på Molde bibliotek |
| 1.1 → 1.2 | R4 | Tiltak oppdatert | Referanse til eksplisitt bufferdokumentasjon i seksjon 3.3 |

---

## 5 Interessenter

Denne seksjonen beskriver de viktigste interessentene for prosjektet, deres rolle og behov.

| **Interessent** | **Rolle** | **Hovedbehov** | **Kommunikasjon** |
|-----------------|-----------|----------------|-------------------|
| Veileder, Høgskolen i Molde | Sponsor / faglig veileder | Akademisk kvalitet, metodisk stringens, overholdelse av tidsplan | Veiledningsmøte annenhver uke, ukentlig statusrapport, review ved milepæler |
| Helse Vest IKT / LIBRA-prosjektet | Bedriftspartner / dataeier | Praktisk anvendbarhet av resultatene, korrekt bruk av SAP-data, konfidensialitet | Møter ved behov (min. 2), validering av anbefalinger |
| HVFS / NorEngros | Potensiell fremtidig bruker | Beslutningsgrunnlag for sortimentsutvidelse, artikkeloverføring | Indirekte via sluttrapport og Helse Vest IKT |
| Høgskolen i Molde, LOG650 | Akademisk institusjon | Innlevering iht. retningslinjer, APA 7, akademisk integritet | Formell innlevering ved M5, eventuell presentasjon |
| Thomas Ekrem Jensen | Prosjektleder / student | Godkjent bacheloroppgave, faglig utvikling og praktisk nytteverdi | Selvstyrt med veiledningsstøtte |

---

## 6 Ressurser

### 6.1 Prosjektteam og roller

| **Rolle** | **Person** | **Ansvar** |
|-----------|-----------|------------|
| Prosjektleder / Utvikler / Forfatter | Thomas Ekrem Jensen | Alt prosjektarbeid: planlegging, dataanalyse, utvikling, rapportskriving og kvalitetssikring. |
| Veileder (sponsor) | [Veileders navn] | Faglig veiledning, godkjenning av prosjektplan og endringer. Gir tilbakemelding på rapportutkast. |
| Kontaktperson bedrift | [Kontakt, Helse Vest IKT] | Tilrettelegging for datatilgang fra SAP. Faglig sparringspartner for forretningslogikk. |

### 6.2 Verktøy og infrastruktur

| **Ressurs** | **Formål** | **Tilgjengelighet** |
|-------------|-----------|---------------------|
| Python 3.x (pandas, scikit-learn, matplotlib, numpy) | Dataanalyse, klyngeanalyse, visualisering | Installert lokalt |
| SAP S/4HANA – Helse Bergen (SE16H) | Datakilde: 10 tabeller iht. Vedlegg A | Via Helse Vest IKT-tilgang |
| GitHub (privat repository) | Versjonskontroll for kode og dokumentasjon | Opprettet i fase 2 |
| Microsoft Word / LaTeX | Rapportskriving | Tilgjengelig |
| Microsoft Project | Detaljert tidsplan og Gantt-diagram | Via studentlisens |
| Microsoft Teams | Kommunikasjon med veileder og bedriftskontakt | Tilgjengelig |

### 6.3 Kritiske ressurser

Den mest kritiske ressursen er tilgang til SAP-data fra Helse Bergen. Ferdigstillelsen av SAP-dataspesifikasjonen (Vedlegg A) reduserer denne risikoen betydelig ved å gi en konkret bestilling som kan oversendes direkte til datatilgangsteamet. Spesifikasjonen muliggjør også at en kollega kan utføre uttrekket dersom Thomas ikke har direkte tilgang.

Thomas' tid er også en kritisk ressurs, gitt parallelt arbeid med fulltidsstilling ved Helse Vest IKT. Tidsplanen tar høyde for dette gjennom realistisk estimering, eksplisitt buffer (seksjon 3.3) og prioritering av kritisk-linje-aktiviteter.

---

## 7 Kommunikasjon

Kommunikasjonsplanen sikrer at alle interessenter holdes informert gjennom strukturerte kanaler tilpasset et individuelt bachelorprosjekt.

### 7.1 Kommunikasjonsoversikt

| **Kommunikasjonsform** | **Frekvens** | **Deltakere** | **Kanal** | **Formål** |
|------------------------|-------------|---------------|-----------|-----------|
| Veiledningsmøte | Annenhver uke / ved behov | Thomas, veileder | Teams / fysisk | Faglig veiledning, fremdriftsvurdering, godkjenning av milepæler |
| Statusoppdatering til veileder | Ukentlig | Thomas → veileder | E-post | Kort skriftlig oppsummering av ukens fremdrift, blokkere og neste steg |
| Bedriftskontakt-møte | Ved behov (minimum 2 ganger) | Thomas, kontaktperson | Teams | Avklaring av dataspørsmål, forretningslogikk, validering av anbefalinger |
| GitHub-oppdateringer | Løpende (daglig commit) | Thomas (tilgjengelig for veileder) | GitHub | Versjonskontroll, dokumentasjon av fremgang i kode |

### 7.2 Rapportering

Status kan følges gjennom MS Project som viser: ferdigstilte leveranser siste uke, planlagte aktiviteter neste uke, identifiserte blokkere eller risikoer, og eventuelle avvik fra tidsplanen. Ved milepæler (M2–M5) sendes leveransen til veileder for formell gjennomgang.

### 7.3 Endringskontroll

Endringer i prosjektomfang, tidsplan eller analysemetodikk etter godkjenning av denne planen skal dokumenteres skriftlig og godkjennes av veileder før implementering. Mindre justeringer (f.eks. optimalisering av parametervalg) dokumenteres i prosjektloggen og informeres om i ukentlig statusrapport.

---

## 8 Kvalitet

Kvalitetsstyring i dette prosjektet bygger på fire prinsipper: reproduserbarhet, validering, fagfellevurdering og akademisk integritet. Disse prinsippene sikrer både teknisk og akademisk kvalitet på sluttresultatet.

### 8.1 Reproduserbarhet

- All Python-kode lagres i et strukturert GitHub-repository med README, kravfil (requirements.txt) og dokumentasjon av kjøreinstruksjoner.
- Datapipelinen er fullt automatisert fra rådata (11 SE16H-filer iht. Vedlegg A) til sluttresultat, slik at analysen kan reproduseres på nytt med oppdatert data.
- Alle parametervalg (ABC-terskler, XYZ-grenseverdier, EOQ-kostnadsparametere inkl. holdekostnadssats, antall klynger) er eksplisitt dokumentert i kode og rapport.
- Seed-verdier settes for alle stokastiske prosesser (K-means initialisering) for å sikre deterministiske resultater.

### 8.2 Sensitivitetsanalyse

Robustheten i resultatene valideres gjennom systematisk sensitivitetsanalyse på følgende nøkkelparametere:

- **Transaksjonskostnad per ordre (S):** variasjon innenfor intervallet 500–1 000 kroner.
- **Holdekostnadssats:** variasjon 15–25 % av enhetspris (base case 20 %).
- **ABC-terskler:** justering av grenseverdier for A/B/C-kategorisering (± 5 prosentpoeng).
- **XYZ-grenseverdier:** variasjon av CV-terskler for X/Y/Z-klassifisering.
- **Antall klynger (K):** evaluering med elbow-metode og silhouette-score for K = 2–8.

Resultater presenteres som område (best case / base case / worst case) for årlig besparelse.

### 8.3 XYZ-validering

En sentral kvalitetsindikator er samsvar mellom SAP-lagret XYZ-klassifisering (MARC.MTVFP) og prosjektets beregnede XYZ fra MVER-forbruksdata. Dette måles gjennom:

- **XYZ-dekningsgrad:** andel artikler med MARC.MTVFP tilgjengelig (ikke-blank).
- **Samsvarsprosent:** andel artikler der beregnet XYZ stemmer overens med SAP-XYZ.
- **Avviksanalyse:** identifisering og forklaring av systematiske avvik mellom de to klassifiseringene.

Lav dekningsgrad eller lavt samsvar dokumenteres åpent som datakvalitetsrisiko og diskuteres i rapporten.

### 8.4 Fagfellevurdering (Peer Review)

Følgende kvalitetsreviews gjennomføres:

| **Review-type** | **Tidspunkt** | **Reviewer** | **Fokus** |
|-----------------|--------------|-------------|-----------|
| Veiledningsreview 1 | Etter fase 2 (M2) | Veileder | Prosjektplan, forskningsdesign, metodisk tilnærming |
| Kode-review | Etter WBS 4.7 (regelmotor ferdig) | Selvreview + eventuell medstudent | Kodekvalitet, logikk i regelmotor, håndtering av edge cases |
| Utkast-review | Etter M4 (komplett utkast) | Veileder | Akademisk kvalitet, struktur, argumentasjon og konklusjoner |
| Sluttreview | Før M5 (innlevering) | Veileder + eventuell medstudent | Ferdigstillelse, korrektur, formatering, APA 7-referanser |

### 8.5 Akademisk integritet

- Alle 23 kilder i Vedlegg B refereres i henhold til APA 7th edition med DOI der tilgjengelig.
- Bruk av AI-verktøy (Claude, ChatGPT) for kodestøtte og tekstarbeid dokumenteres transparent i metodekapittelet.
- Rapporten sjekkes mot plagiat før innlevering.
- Data behandles i tråd med Helse Vest IKTs retningslinjer for informasjonssikkerhet. Analysen utføres på artikkelnivå (materialnummer) og inneholder ikke personidentifiserbar informasjon knyttet til pasienter eller ansatte. Separat NSD-melding er derfor ikke nødvendig.

---

## Vedlegg A – SAP-dataspesifikasjon

Komplett dataspesifikasjon for SE16H-uttrekk fra Helse Bergen forsyningslager. Fabrikk (WERKS): 3300, Lagersted (LGORT): 3000. Utarbeidet februar 2025.

### A.1 Tabelloversikt

Følgende 10 SAP-tabeller dekker alle beslutningsvariabler i prosjektet.

| **Tabell** | **Innhold** | **Brukes til** | **Status** |
|-----------|-------------|----------------|------------|
| MAKT | Materialebeskrivelse (klartekst) | Lesbar output – uten denne er rapport uleselig | ✓ Kritisk |
| MARA | Materialtype, varegruppe, basisenhet | Filtrere forbruksmateriell, ekskludere legemidler | ✓ Kritisk |
| MARC | SAP XYZ-indikator, disponering, sikkerhetslager | XYZ-validering mot beregnet CV | ✓ Kritisk |
| MBEW | Enhetspris (standard / glidende) | ABC-verdi og EOQ holdekostnad (H = pris × sats) | ✓ Kritisk |
| MARD | Lagerbeholdning per lagersted | Identifisere aktive artikler på LGORT 3000 | ✓ Kritisk |
| MVER | Månedlig forbruk 2024–2025 | XYZ-klassifisering (CV), EOQ etterspørsel (D) | ✓ Kritisk |
| EKKO | Innkjøpsordrehode – dato, type | Datofiltere EKPO korrekt på 2024–2025 | ✓ Kritisk |
| EKPO | Innkjøpsordreposisjon – kvantum og pris | ABC-verdi, ordrefrekvens, EOQ-avvik | ✓ Kritisk |
| EKBE | Faktiske varemottak per ordre | Skille bestilt fra mottatt – datakvalitet | ✓ Kritisk |
| EINE | Leveringstid og minimumskvantum | EOQ restordreperiode (ROP) | Bør ha |
| T023T | Varegruppenavn (klartekst) | Lesbar gruppering i output | Bør ha |

### A.2 Seleksjonskriterier i SE16H

| **Parameter** | **Verdi** | **SAP-felt** | **Merknad** |
|--------------|----------|-------------|-------------|
| Anlegg | 3300 | WERKS | Gjelder MARC, MBEW, MARD, MVER, EKPO, EINE |
| Lagersted | 3000 | LGORT | Kun i MARD – dette spesifikke lageret |
| Vurderingsområde | 3300 | BWKEY | MBEW – samme som anlegg |
| Forbruksår | 2024–2025 | LFGJA | MVER – analyseperiode |
| Språk | NO (evt. EN) | SPRAS | MAKT og T023T – norsk tekst |
| Ordrekategori | F | BSTYP | EKKO – kun innkjøpsordrer, ikke forespørsler |
| Bevegelseskategori | E | BEWTP | EKBE – kun faktiske varemottak |
| Sletteflagg | tomt (blank) | LOEKZ | EKPO – ekskluder slettede posisjoner |
| Materialetype | Avklar med HB | MTART | MARA – kode for medisinsk forbruksmateriell |

### A.3 Koblingsnøkler

Alle tabeller kobles på MATNR (artikkelnummer) som primærnøkkel gjennom hele datasettet.

| **Fra tabell** | **Via felt** | **Til tabell** | **Formål** |
|---------------|-------------|---------------|-----------|
| EKKO | EBELN | EKPO | Koble ordrehode til ordreposisjoner |
| EKPO | EBELN + EBELP | EKBE | Koble ordreposisjon til faktiske mottak |
| EKPO | MATNR | MBEW | Hente pris per artikkel til ABC-beregning |
| EKPO | MATNR | MVER | Koble ordrehistorikk til forbrukshistorikk |
| MARA | MATNR | MARC | Legge til SAP XYZ-indikator og disponering |
| MARA | MATNR | MAKT | Legge til materialebeskrivelse (klartekst) |
| MARA | MATKL | T023T | Legge til varegruppenavn |
| MARC | MATNR | MARD | Verifisere aktiv beholdning på LGORT 3000 |
| EKPO | MATNR | EINE | Legge til leveringstid for EOQ/ROP |

### A.4 Datakvalitetskontroller

Følgende 7 kontroller skal utføres før analyse iht. WBS 4.2:

| **Kontroll** | **Hva sjekkes** | **Korrigerende tiltak** |
|-------------|----------------|------------------------|
| Artikler uten pris | MBEW.STPRS = 0 eller null | Ekskluder fra ABC – kan ikke verdsettes |
| Artikler uten forbruk | MVER alle måneder = 0 | Ekskluder – inaktive artikler |
| MVER vs EKBE avvik | Totalforbruk MVER ≠ sum EKBE.MENGE | Bruk EKBE som primærkilde – flagg avvik |
| SAP XYZ mangler (MTVFP) | MARC.MTVFP = blank for > X artikler | Rapporter dekningsgrad – beregn XYZ fra MVER |
| Duplikate artikkelnummer | Samme MATNR i MBEW med ulik BWKEY | Filtrer på BWKEY = 3300 strengt |
| Negative forbrukstall | VER01–VER12 < 0 i MVER | Kontroller returer – ekskluder eller sett til 0 |
| Prisenhet ≠ 1 | MBEW.PEINH = 10 eller 100 | Korriger: pris per stk = STPRS ÷ PEINH |

> **Viktig:** Prisenhet (PEINH) i MBEW er ofte 10 eller 100 – ikke 1. Pris per stykk beregnes som STPRS ÷ PEINH. Denne feilen er hyppig årsak til feil ABC-beregning.

### A.5 Anbefalt uttrekksrekkefølge

| **#** | **Tabell** | **Filnavn** | **Kommentar** |
|-------|-----------|-------------|---------------|
| 1 | MARA | MARA_3300.xlsx | Basis for all filtrering – hent først |
| 2 | MAKT | MAKT_NO.xlsx | Språk = NO, kobles på MATNR |
| 3 | MARC | MARC_3300.xlsx | WERKS = 3300 – SAP XYZ-indikator |
| 4 | MBEW | MBEW_3300.xlsx | BWKEY = 3300 – pris per artikkel |
| 5 | MARD | MARD_3300_3000.xlsx | WERKS = 3300, LGORT = 3000 |
| 6 | MVER | MVER_3300_2024_2025.xlsx | WERKS = 3300, LFGJA = 2024–2025 |
| 7 | EKKO | EKKO_2024_2025.xlsx | BEDAT = 01.01.2024–31.12.2025, BSTYP = F |
| 8 | EKPO | EKPO_3300.xlsx | WERKS = 3300, filtrer på EBELN fra EKKO |
| 9 | EKBE | EKBE_2024_2025.xlsx | BEWTP = E, BUDAT = 2024–2025 |
| 10 | EINE | EINE_3300.xlsx | WERKS = 3300 – leveringstider |
| 11 | T023T | T023T_NO.xlsx | SPRAS = NO – varegruppenavn |

---

## Vedlegg B – Referanseliste

23 kilder strukturert etter APA 7th edition. Oppdatert mars 2025. Artikler merket [⏳] venter på Molde bibliotek.

### B.1 Tier 1 – Metodisk kjerne (10 referanser)

#### Vareklassifisering og SKU

van Kampen, T. J., Akkerman, R., & Pieter van Donk, D. (2012). SKU classification: A literature review and conceptual framework. *International Journal of Operations & Production Management*, *32*(7), 850–876. https://doi.org/10.1108/01443571211250112

Gurumurthy, A., Nair, V. K., & Vinodh, S. (2020). Application of a hybrid selective inventory control technique in a hospital. *The TQM Journal*, *33*(3), 568–595. https://doi.org/10.1108/TQM-06-2020-0123 [⏳]

Ketkar, M., & Vaidya, O. S. (2014). Developing ordering policy based on multiple inventory classification schemes. *Procedia – Social and Behavioral Sciences*, *133*, 180–188. https://doi.org/10.1016/j.sbspro.2014.04.183

Silaen, R., Sihombing, H., Sembiring, A. C., & Sinulingga, S. (2024). Implementation of the ABC analysis to the inventory management. *International Journal of Science, Technology & Management*, *5*(4), 816–825. https://doi.org/10.46729/ijstm.v5i4.1144

Suryaputri, R. S., Siagian, Y., & Rahmawati, D. (2022). Integration of ABC-XYZ analysis in inventory management optimization: A case study in the health industry. *Proceedings of IEOM*, 1–10. https://doi.org/10.46254/AF03.20220070

#### Sykehuslogistikk og sentralisering

Bijvank, M., & Vis, I. F. A. (2012). Inventory control for point-of-use locations in hospitals. *Journal of the Operational Research Society*, *63*(4), 497–510. https://doi.org/10.1057/jors.2011.52

Saha, E., & Ray, P. K. (2019). Modelling and analysis of inventory management systems in healthcare: A review and reflections. *Computers & Industrial Engineering*, *137*, 106051. https://doi.org/10.1016/j.cie.2019.106051

Volland, J., Fügener, A., Schoenfelder, J., & Brunner, J. O. (2017). Material logistics in hospitals: A literature review. *Omega*, *69*, 82–101. https://doi.org/10.1016/j.omega.2016.08.004 [⏳]

Moons, K., Waeyenbergh, G., & Pintelon, L. (2019). Measuring the logistics performance of internal hospital supply chains. *Omega*, *82*, 205–217. https://doi.org/10.1016/j.omega.2018.01.007

De Vries, J. (2011). The shaping of inventory systems in health services: A stakeholder analysis. *International Journal of Production Economics*, *133*(1), 60–69. https://doi.org/10.1016/j.ijpe.2009.10.029 [⏳]

### B.2 Tier 2 – Kontekst, modell og metode (11 referanser)

#### EOQ og bestillingspolitikk

Hautaniemi, P., & Pirttilä, T. (1999). The choice of replenishment policies in an MRP environment. *International Journal of Production Economics*, *59*(1–3), 85–92. https://doi.org/10.1016/S0925-5273(98)00026-7 [⏳]

Nyoman Pujawan, I. (2004). The effect of lot sizing rules on order variability. *European Journal of Operational Research*, *159*(3), 617–635. https://doi.org/10.1016/S0377-2217(03)00419-3

#### Klassifiseringsmetoder og MCDM

Partovi, F. Y., & Burton, J. (1993). Using the analytic hierarchy process for ABC analysis. *International Journal of Operations & Production Management*, *13*(9), 29–44. https://doi.org/10.1108/01443579310043619 [⏳]

Keshavarz Ghorabaee, M., Amiri, M., Olfat, L., & Khatami Firouzabadi, S. M. A. (2015). Multi-criteria inventory classification using EDAS. *Informatica*, *26*(3), 435–451. https://doi.org/10.15388/Informatica.2015.57

Kolińska, K., & Cudziło, M. (2016). The use of XYZ analysis in the stock management. *LogForum*, *12*(4), 295–304. https://doi.org/10.17270/J.LOG.2016.4.7

Srinivasan, M. M., & Moon, Y. B. (1999). A comprehensive clustering algorithm for strategic analysis of supply chain networks. *Computers & Industrial Engineering*, *36*(3), 615–633. https://doi.org/10.1016/S0360-8352(99)00155-2

#### Sykehus – internlogistikk og ytelse

Fragapane, G. I., Ivanov, D., Sgarbossa, F., & Strandhagen, J. O. (2019). Medical supplies to the point-of-use in hospitals. *IFIP Advances in ICT*, 248–255. https://doi.org/10.1007/978-3-030-29996-5_29

Gupta, R., Gupta, K., Jain, B., & Garg, R. (2007). ABC and VED analysis in medical stores inventory control. *Medical Journal Armed Forces India*, *63*(4), 325–327. https://doi.org/10.1016/S0377-1237(07)80006-2

Kumar, D., & Kumar, D. (2015). Modelling hospital inventory management using ISM approach. *International Journal of Logistics Systems and Management*, *21*(3), 319–335. https://doi.org/10.1504/IJLSM.2015.069730

Sirisawat, P., Hasachoo, N., & Kaewket, T. (2019). Investigation and prioritization of performance indicators for inventory management. *Proceedings IEEE IEEM*, 691–695. https://doi.org/10.1109/IEEM44572.2019.8978700 [⏳]

Kelle, P., Woosley, J., & Schneider, H. (2012). Pharmaceutical supply chain specifics and inventory solutions for a hospital case. *Operations Research for Health Care*, *1*(2–3), 54–63. https://doi.org/10.1016/j.orhc.2012.07.001

### B.3 Programvareverktøy (2 referanser)

McKinney, W. (2010). Data structures for statistical computing in Python. I S. van der Walt & J. Millman (Red.), *Proceedings of the 9th Python in Science Conference* (s. 56–61). https://doi.org/10.25080/Majora-92bf1922-00a

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., ... & Duchesnay, É. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, *12*, 2825–2830. http://jmlr.org/papers/v12/pedregosa11a.html

*Status: 17 artikler tilgjengelig, 6 venter på Molde bibliotek (merket [⏳]). Kompendiumkilder legges til når utgivelse foreligger. Alle DOI-er er bekreftet.*
