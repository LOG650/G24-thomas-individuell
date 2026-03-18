# SENSORRAPPORT — LOG650 Logistikk og kunstig intelligens

**Oppgave:** Fra lokalt forsyningslager til regional sentralforsyning: Multikriterieklassifisering og klyngeanalyse for identifisering av overføringskandidater ved Helse Bergen
**Kandidat:** Thomas Ekrem Jensen, Høgskolen i Molde, vår 2026
**Sammenligningsgrunnlag:** 11 referanseoppgaver (bachelor og master, NTNU / HiM / HVL / NMBU, 2013–2025)

| | |
|---|---|
| **Nåværende karakter (v5)** | **B+** |
| **Etter alle rettelser** | **A** |

---

## 1. Komparativt overblikk

Rapporten er basert på fullstendig lesning av din oppgave og følgende 11 referanseoppgaver:

| Tittel | Institusjon / År | Nivå | Metode |
|---|---|---|---|
| Hauge et al. – Lagerstyring St. Olav | NTNU 2024 | Bachelor | Intervjuer + Monte Carlo Excel + ABC (10 varer) |
| Centonze et al. – Bemanning St. Olav | NTNU 2025 | Bachelor | LP/ILP-optimering, deterministisk + stokastisk |
| Birkedal et al. – Industri 4.0 lagerstyring | HiM 2023 | Bachelor | Kvalitativ litteraturstudie |
| Gundersen – Anskaffelsesstrategi | HVL | Bachelor | Kvalitative intervjuer |
| Jotvedt & Lisjordet – Lean Mjøsbygg | NTNU 2025 | Bachelor | Kvalitativ casestudie |
| Grimstad et al. – Lean Hunton | NTNU 2022 | Bachelor | Kvalitativ casestudie |
| Skogli et al. – Lagerlogistikk tre | NTNU 2013 | Bachelor | ABC + FIFO, enkel kvantitativ |
| Hosana – Public procurement cluster | HiM 2023 | Master | Klyngeanalyse (silhouette), kvantitativ |
| Risholm – Fleet spare parts | NTNU 2013 | Master | Litteratur + case, kvalitativ |
| Halvorsen – Transport/demolition | NTNU | Master | LP-optimering |
| Cunin – DSS additive manufacturing | NTNU 2025 | Master | DSS + Poisson-modell |

**Konklusjon:** Din oppgave overgår metodisk alle direkte sammenlignbare bacheloroppgaver — uten unntak. Den eneste oppgaven på tilsvarende teknisk nivå er Hosana (HiM 2023), og det er en masteroppgave. Kombinasjonen av fire analysemetoder, 14 SAP-tabeller, formell modellspesifikasjon og reproduserbar Python-pipeline er ikke representert i noen av de andre bacheloroppgavene.

---

## 2. Styrker som holder høyt nivå

| Område | Vurdering |
|---|---|
| **SAP-datadokumentasjon** | 14 tabeller med funksjonell kategorisering, D-01–D-08 med begrunnelse og effekt. PEINH-korreksjon (D-02) og MSEG vs. EKBE-distinksjon er subtile men kritisk korrekte detaljer. Langt over bachelornivå. |
| **Formell modellspesifikasjon** | Alle formler i kap. 5 samsvarer med implementasjonen: f* = √(DH/2S), FREQ_AVVIK, TC(f), besparelsesformelen. Eget modelleringskapittel er metodisk modent. |
| **K-means metodologisk** | Train/test split 80/20, StandardScaler fittet kun på treningsdata, silhouette på begge sett (0,383 vs 0,368, Δ0,015). Datalekkasje-problematikken er eksplisitt adressert. Ikke sett i noen av referansebachelorene. |
| **Sensitivitetsanalyse** | 27 kombinasjoner (S × h × τ_f) med reberegning av kandidatsett per scenario. Besparelse forblir positiv i alle 27 scenarier (kr 176 374–763 903). Solid. |
| **Tabell 15** | Sammenstilling av egne resultater mot litteraturforventninger med referanse er et metodisk modent grep — ikke sett i noen referanseoppgave på bachelornivå. |
| **Teori–modell–kode-konsistens** | Ingen motsetninger mellom kap. 2 (teori), kap. 5 (modell) og kap. 6 (analyse). Regelmotor R1–R8 er logisk konsistent med ABC/XYZ-teorien. |
| **Praktiske anbefalinger** | 4 konkrete, SAP-spesifikke anbefalinger i kap. 9.2 med direkte kobling til MRP-type og ordrekvantumsparametere. Operasjonelt anvendbart. |

---

## 3. Kritiske feil

> Disse to feilene er alvorlighetsgrad 1 — de påvirker karakter direkte og må rettes før innlevering.

### FEIL 1 — Tom Abstract-seksjon

**Plassering:** Etter norsk sammendrag, egen seksjon merket «Abstract».

**Nåværende innhold:** `(Sammendrag på norsk — sjå avsnittet over.)` — dette er ikke et abstract.

**Konsekvens:** Begge NTNU-referanseoppgavene (2024 og 2025) har fullstendig engelsk abstract som eget avsnitt. HiM-sensorer vil se dette umiddelbart. Formalkrav er ikke oppfylt.

**Løsning:** Skriv selvstendig engelsk abstract på ca. 250 ord. Må dekke:
- Bakgrunn og problemstilling
- Metode (ABC/XYZ/EOQ/K-means + regelmotor)
- Nøkkelresultater: 145 artikler, kr 451 515/år, K=3, silhouette 0,383
- Konklusjon og implikasjoner for LIBRA-prosjektet

Må kunne leses fullstendig uavhengig av resten av oppgaven.

---

### FEIL 2 — Tallinkonsistens: FOR_MANGE_ORDRER = 356/487

**Plassering:** Tabell 15 (kap. 8.1) og kap. 6.3.

Logikken bryter matematisk:

| Størrelse | Verdi | Kilde |
|---|---|---|
| Artikler med EOQ-data | 487 | Kap. 6.3 |
| Artikler med null EKBE → klassifisert som OK | 222 | Kap. 6.3 |
| Artikler med positiv ordrefrekvens (mulig FOR_MANGE) | 487 − 222 = **265** | Beregnet |
| Rapportert FOR_MANGE_ORDRER | **356** | Tabell 15 |

**356 > 265 er matematisk umulig** dersom de 222 zero-EKBE-artiklene korrekt klassifiseres som OK (FREQ_AVVIK = −1, ikke > 1,5).

Mulige årsaker i Python-koden:
- Betingelsen er implementert som `abs(FREQ_AVVIK) > τ_f` istedenfor `FREQ_AVVIK > τ_f`
- Nevneren i prosentberegningen er feil (356 er riktig antall, men ikke av 487)
- `ACTUAL_FREQ = 0` behandles ikke riktig — negative FREQ_AVVIK fanges ikke ut

**Krav:** Verifiser kodelinjen som setter FOR_MANGE_ORDRER-flagget. Rett Tabell 15 og kap. 6.3 basert på korrekt tall.

---

## 4. Vesentlige gap

> Påvirker kvalitet og diskusjonsdybde, men ikke karakter direkte dersom de adresseres kort.

### GAP 1 — K_OVERFØR-labeling er ikke formelt reproduserbar

**Plassering:** Avsnitt 5.4.

Nåværende tekst: *«En klynge identifiseres som K_OVERFØR basert på en kombinasjon av lav CV, høy artikkelverdi og høyt positivt ΔTC»*. Ingen deterministisk regel er oppgitt. En annen forsker kan ikke identifisere K_OVERFØR-klyngen uten manuell tolkning — dette svekker reproduserbarheten som ellers er en klar styrke.

**Løsning:** Legg til én eksplisitt setning, f.eks.: *«K_OVERFØR identifiseres programmatisk som klyngen med lavest gjennomsnittlig z(ln CV_i) blant de K klyngene.»* Referer til kodelinjen i Vedlegg B.

---

### GAP 2 — Besparelsesformelens rekkevidde underkommunisert

**Plassering:** Kap. 8.2.

`B_HVFS = ΣΔTCᵢ × g` fanger kun kostnadsavvik fra suboptimal ordrefrekvens for 117 artikler. Tre kostnadselementer er eksplisitt ekskludert men mangler størrelsesorden i diskusjonen:

- Redusert lokal lagerkapitalbinding ved overføring (positiv gevinst)
- Transportkostnad HVFS → avdeling via APL-modellen (motpost)
- Engangskostnader: SAP MM-konfigurasjon, leverandørforhandlinger

**Løsning:** Legg til 3–5 setninger i kap. 8.2 med størrelsesorden på disse elementene, med referanse til Kelle et al. (2012) eller Moons et al. (2019). Tydeliggjør at estimatet er et konservativt transaksjonskostnadsestimat.

---

### GAP 3 — EOQ-antakelsesbrudd ikke eksplisitt testet

**Plassering:** Kap. 6.3 eller 8.2.

Wilson EOQ forutsetter deterministisk/konstant etterspørsel. EOQ anvendes på 350 X-artikler (CV < 0,5), men oppgaven tester ikke om disse faktisk har tilstrekkelig stasjonær og normalfordelt etterspørsel. For artiklene med størst ΔTC — som utgjør grunnlaget for besparelsesestimatet — er dette en relevant intern validitetstrussel.

**Løsning:** Enten (a) legg til en enkel skjevhetssjekk (skewness) for X-artiklene i kap. 6.3, eller (b) nevn dette eksplisitt som en metodisk begrensning i kap. 8.2 med referanse til Hautaniemi & Pirttilä (1999).

---

## 5. Formalfeil

| # | Feil | Plassering | Handling |
|---|---|---|---|
| F1 | Nynorsk i bokmålsoppgave | Vedlegg B og C, figurtekster, regelmotor-tabell | Se fullstendig liste i avsnitt 6 |
| F2 | 
| F3 | `n=n=X`-dobling (8 forekomster) | Kap. 6.4, matematikkfelt | Rett `n=n=389` → `n=389`, osv. for alle 8 |
| F4 | Figurantall inkonsistens | Vedlegg B: Fig00–Fig11 (12 scripts) vs. Vedlegg C: Fig00–Fig10 (11 figurer) | Bestem korrekt antall og rett den andre |
| F5 | 

---

## 6. Fullstendig liste: nynorsk → bokmål

Alle forekomster funnet i dokumentet. Rettes konsekvent gjennom hele oppgaven inkludert vedlegg og figurtekster.

| Nynorsk (rettes) | Bokmål (erstattes med) | Funnet i |
|---|---|---|
| hovudkomponentar | hovedkomponenter | Vedlegg B |
| Hovudscript | Hovedscript | Vedlegg B |
| klassifiseringar | klassifiseringer | Vedlegg B |
| regelmotoranbefalingar | regelmotor-anbefalinger | Vedlegg B |
| separate ark for kvart analysesteg | separate ark for hvert analysetrinn | Vedlegg B |
| genererer figurane Fig00–Fig11 | genererer figurene Fig00–Fig11 | Vedlegg B |
| datastrukturar | datastrukturer | Vedlegg B |
| Reproduserbarheit | Reproduserbarhet | Vedlegg B |
| scripts brukar | scripts bruker | Vedlegg B (2x) |
| same inputdata gir | samme inndata gir | Vedlegg B |
| tilgjengeleg i | tilgjengelig i | Vedlegg B |
| I denne oppgåva | I denne oppgaven | Vedlegg C |
| i tre delar av arbeidet | i tre deler av arbeidet | Vedlegg C |
| Kode og algoritmar | Kode og algoritmer | Vedlegg C |
| Claude vart brukt til | Claude ble brukt til | Vedlegg C (2x) |
| Verktøyet vart brukt til | Verktøyet ble brukt til | Vedlegg C |
| seinare vart tilpassa og integrert | senere ble tilpasset og integrert | Vedlegg C |
| gjennomgått, testa og modifisert av forfattaren | gjennomgått, testet og modifisert av forfatteren | Vedlegg C |
| Den endelege implementasjonen | Den endelige implementasjonen | Vedlegg C |
| tolkinga av resultat | tolkningen av resultater | Vedlegg C |
| numeriske verdiar er forfattarens ansvar | numeriske verdier er forfatterens ansvar | Vedlegg C |
| Figurar og tabellar | Figurer og tabeller | Vedlegg C |
| Figurane er basert på analyseresultat | Figurene er basert på analyseresultater | Vedlegg C |
| frå SAP-kildedata | fra SAP-kildedata | Vedlegg C |
| ikkje produsert eller modifisert nokon dataverdiar | ikke produsert eller modifisert noen dataverdier | Vedlegg C |
| Kvar figur er merka | Hver figur er merket | Vedlegg C |
| Tabellar er formaterte med støtte frå | Tabeller er formatert med støtte fra | Vedlegg C |
| alle verdiar kjem direkte frå | alle verdier kommer direkte fra | Vedlegg C |
| språkleg bearbeiding | språklig bearbeiding | Vedlegg C |
| forbetre språkleg klarheit | forbedre språklig klarhet | Vedlegg C |
| avsnittsinndeling og formuleringar | avsnittsinndeling og formuleringer | Vedlegg C |
| som forfattaren vurderte kritisk | som forfatteren vurderte kritisk | Vedlegg C |
| Alle faglege påstandar, argument og konklusjonar | Alle faglige påstander, argumenter og konklusjoner | Vedlegg C |
| forfattarens eigne | forfatterens egne | Vedlegg C |
| ikkje brukt som fagkjelde og er ikkje sitert | ikke brukt som fagkilde og er ikke sitert | Vedlegg C |
| faglege påstandar | faglige påstander | Vedlegg C |
| Rådata frå SAP vart ikkje lagt inn | Rådata fra SAP ble ikke lagt inn | Vedlegg C |
| Alle datatransformasjonar er dokumenterte | Alle datatransformasjoner er dokumentert | Vedlegg C |
| køyrde lokalt i Python | kjørt lokalt i Python | Vedlegg C |
| personopplysningar er brukte i studien | personopplysninger er brukt i studien | Vedlegg C |
| ikkje K_OVERFØR | ikke K_OVERFØR | Kap. 5.5, Tabell 7 |

---

## 7. Prioritert handlingsplan

| Prioritet | Tidsbruk | Handling |
|---|---|---|
| **P1 ★★★** | 30 min | Konverter alle nynorske ord/fraser til bokmål — bruk listen i avsnitt 6. Inkluder figurtekster, Vedlegg B og C, og regelmotor-tabellen i kap. 5.5. |
| **P2 ★★★** | 45 min | Skriv og lim inn selvstendig engelsk abstract (~250 ord). Må dekke: bakgrunn, metode, nøkkelresultater (145 artikler, kr 451 515/år, K=3), konklusjon. |
| **P3 ★★★** | 30 min | Verifiser FOR_MANGE_ORDRER-betingelsen i Python-scriptet. Sjekk eksakt kodelinje. Rett Tabell 15 og kap. 6.3 dersom tallet er feil. |
|
| **P5 ★★** | 15 min | Rett `n=n=X` → `n=X` for alle 8 forekomster i kap. 6.4 (matematikkfelt). |
| **P6 ★★** | 10 min | Avklar figurtall: 11 (Fig00–Fig10) eller 12 (Fig00–Fig11)? Rett begge vedlegg konsekvent. |
| **P7 ★** | 20 min | Legg til deterministisk K_OVERFØR-labelingsregel i avsnitt 5.4 med referanse til kodelinjen i Vedlegg B. |
| **P8 ★** | 20 min | Legg til 3–5 setninger i kap. 8.2 om ekskluderte kostnadselementer (APL-transport, engangskostnader SAP-konfig) med størrelsesorden. |
| **P9 ★** | 15 min | Nevn eksplisitt i kap. 8.2 at EOQ-antakelsen om konstant etterspørsel ikke er formelt testet for X-artiklene, med referanse til Hautaniemi & Pirttilä (1999). |

**Estimert total tidsbruk:** ca. 3–4 timer for P1–P6 (kritisk). P7–P9 er ønskelig men ikke karakteravgjørende.

---

## 8. Dimensjonsvurdering

| Dimensjon | Nå | Etter rettelser | Kommentar |
|---|---|---|---|
| Problemstilling og avgrensning | A | A | Presis, dobbelt spørsmål, godt besvart |
| Litteraturgjennomgang | A | A | 22 kilder, Tabell 1 og 15 over bachelornivå |
| Teori–modell–kode-konsistens | A | A | Alle formler samsvarer med implementasjon |
| Datagrunnlag og dokumentasjon | A | A | 14 SAP-tabeller, D-01–D-08 eksemplarisk |
| Kvantitativ analyse | A | A | ABC+XYZ+EOQ+K-means+regelmotor |
| Reproduserbarhet | A | A | random_state=42, deterministisk pipeline |
| Sensitivitetsanalyse | A | A | 27 kombinasjoner |
| Diskusjon og metodekritikk | B+ | A- | Svakhet: EOQ-antakelsestest og APL-kostnadskomponent |
| Formalia | C | A | Nynorsk, tomt abstract, n=n=, sidetall |
| **Samlet** | **B+** | **A** | |

---

**Eneste usikkerhetsfaktor:** Dersom FOR_MANGE_ORDRER-tallet (FEIL 2) viser seg å være en reel kalkylefeil i Python-koden, ikke bare en feil nevner i tabellen, vil dette kunne påvirke besparelsesestimatet i kap. 7.6 og konklusjonen. Send kodelinjen, så avgjøres det på sekunder.
