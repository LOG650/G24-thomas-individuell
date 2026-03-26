# Komparativ referanseanalyse: Benchmarking av LOG650-oppgaven mot 18 bachelor- og masteroppgaver (2013–2025)

**Forfatter:** Thomas Ekrem Jensen
**Dato:** Mars 2026
**Tilknytning:** LOG650, Høgskolen i Molde

---

## 1. Metodisk tilnærming

Denne analysen gjennomfører en systematisk sammenligning av LOG650-oppgaven mot 18 norske bachelor- og masteroppgaver publisert i perioden 2013–2025. Formålet er å identifisere styrker, svakheter og konkret forbedringspotensial ved å posisjonere oppgaven i et bredere faglig landskap.

**Utvalgskriterier.** Oppgavene er valgt basert på tre kriterier: (1) metodisk relevans — bruk av klassifiseringsmetoder (ABC, XYZ, VED), optimaliseringsmodeller (EOQ, simulering, klyngeanalyse) eller beslutningsstøttesystemer; (2) domenenærhet — helselogistikk, lagerstyring eller forsyningskjede; (3) institusjonsspredning — representasjon fra NTNU, HiMolde, NMBU, HVL og BI. Utvalget er inndelt i tre relevansnivåer: direkte sammenlignbare (5), metodisk overlappende (8) og kontekstuell kontrast (5).

**Analysedimensjoner.** Sammenligningen gjennomføres langs seks dimensjoner:

1. **Forskningsdesign** — kvantitativ, kvalitativ eller blandet metode
2. **Datagrunnlag** — datakilde (ERP, intervju, simulering), utvalgsstørrelse og analyseperiode
3. **Klassifiseringsmetoder** — ABC, XYZ, VED, SDE og andre klassifiseringsskjemaer
4. **Optimeringsmodeller** — EOQ, simulering, klyngeanalyse, lineær programmering, maskinlæring
5. **Beslutningsstøtte** — type beslutningsmekanisme (regelmotor, rammeverk, DSS, Lean-verktøy)
6. **Kostnadskvantifisering** — besparelsesestimat og sensitivitetsanalyse

**Begrensning.** Sammenligningen er basert på publisert tekst. Implementasjonskvalitet er ikke uavhengig verifisert. Fire oppgaver er ekskludert grunnet lav relevans (offshore ruting, rent kvalitativ PDCA, ulesbar filformat og duplikat).

---

## 2. Hovedsammenligningstabell

Tabell 1 gir en samlet oversikt over alle 19 oppgaver (18 referanseoppgaver + LOG650) på tvers av metadata, klassifisering, analytiske metoder og beslutningsstøtte.

### Tabell 1a — Metadata og datagrunnlag

| # | Forfatter(e) | År | Inst. | Nivå | Sektor | Design | Datakilde | n | Periode |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Rydock | 2023 | NTNU | Master | Sykehus | Blandet | ERP + intervju | ~1 400 | 12 mnd |
| 2 | Nilssen | 2021 | NTNU | Master | Bygg/industri | Blandet | ERP + intervju | ~200 | 12 mnd |
| 3 | Berg et al. | 2025 | NTNU | Bachelor | Sykehus | Blandet | Bestillingsdata + observasjon | ~300 | 12 mnd |
| 4 | Hauge et al. | 2024 | NTNU | Bachelor | Sykehus | Blandet | Bestillingsdata + intervju | ~10 | 6 mnd |
| 5 | Gundersen | 2023 | HVL | Bachelor | Olje/gass | Kvalitativ | Intervju + dokumenter | Ikke oppgitt | — |
| 6 | Hosana | 2023 | HiMolde | Master | Offentlig | Kvantitativ | Spørreundersøkelse | ~100 org. | Tverrsnitt |
| 7 | Bakken & Solli | 2019 | BI | Master | Sykehus | Kvalitativ | Intervju + observasjon | — | — |
| 8 | Dybwad & Larsen | 2020 | NMBU | Master | Handel | Kvantitativ | CRM (Visma) | 3 prod. | 36 mnd |
| 9 | Cunin | 2025 | NTNU | Master | Industri | Blandet | Litteratur + case | — | — |
| 10 | Risholm | 2013 | NTNU | Master | Offshore | Blandet | Teknisk dokumentasjon | 1 kran | — |
| 11 | Skogli et al. | 2013 | NTNU | Bachelor | Treindustri | Blandet | Lagerstatus + forbruk | ~50 | 12 mnd |
| 12 | Langelo | 2018 | HiMolde | Master | Teori | Kvantitativ | Matematisk modell | — | — |
| 13 | Halvorsen | 2019 | NTNU | Master | Bygg/avfall | Kvantitativ | Prosjektdata | 15 mill. m³ | 5 år |
| 14 | Redzic & Olesen | 2025 | NMBU | Master | Energi | Blandet | ESG-data + intervju | ~200 lev. | Tverrsnitt |
| 15 | Birkedal et al. | 2023 | HiMolde | Bachelor | Industri | Kvalitativ | Litteraturstudie | — | — |
| 16 | Romsdal | 2014 | NTNU | PhD | Mat | Blandet | Produksjonsdata (TINE) | ~500 | 24 mnd |
| 17 | Grimstad et al. | 2022 | NTNU | Bachelor | Industri | Kvalitativ | Intervju + observasjon | — | — |
| 18 | Centonze et al. | 2025 | NTNU | Bachelor | Sykehus | Kvantitativ | Bemanningsdata | — | 12 mnd |
| **19** | **Jensen (LOG650)** | **2026** | **HiMolde** | **Bachelor** | **Sykehus** | **Kvantitativ** | **SAP S/4HANA (14 tab.)** | **709** | **24 mnd** |

### Tabell 1b — Metoder og beslutningsstøtte

| # | Forfatter(e) | ABC | XYZ | Andre klass. | EOQ | Simulering | Klynge | LP/MILP | Beslutningsstøtte | Kostn.est. | Sensitivitet |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Rydock | Ja (verdi) | Nei | VED, etterspørsel | Ja | anyLogistix | Nei | Nei | Rammeverk | Nei | Nei |
| 2 | Nilssen | Ja (verdi) | Ja (CV) | SDE, FSN, HML | Nei | Monte Carlo | Nei | Nei | SAW-rammeverk | Nei | Nei |
| 3 | Berg et al. | Ja (frekvens + volum) | Nei | — | Nei | Nei | Nei | Nei | Lean (kanban, 5S) | Nei | Nei |
| 4 | Hauge et al. | Ja | Nei | — | Nei | Monte Carlo | Nei | Nei | RFID to-kasse | Nei | Nei |
| 5 | Gundersen | Ja | Nei | Kraljic | Nei | Nei | Nei | Nei | Kvalitativ anbefaling | Nei | Nei |
| 6 | Hosana | Nei | Nei | — | Nei | Nei | K-means | Nei | Klyngeanalyse | Nei | Nei |
| 7 | Bakken & Solli | Nei | Nei | — | Nei | Nei | Nei | Nei | Lean (VSM, 5S) | Nei | Nei |
| 8 | Dybwad & Larsen | Ja | Nei | — | Ja | Nei | Nei | Nei | ML-prediksjon | kr 125 K | Nei |
| 9 | Cunin | Nei | Nei | Kritikalitet | Nei | Nei | Nei | Nei | DSS (beslutningstre) | Nei | Nei |
| 10 | Risholm | Nei | Nei | RCM/RBI | Ja | Nei | Nei | Nei | Beslutningsverktøy | Nei | Nei |
| 11 | Skogli et al. | Ja | Nei | — | Nei | Nei | Nei | Nei | Layout-anbefaling | Nei | Nei |
| 12 | Langelo | Nei | Nei | — | Relatert | Nei | Nei | Nei | Matematisk modell | Nei | Nei |
| 13 | Halvorsen | Nei | Nei | — | Nei | Nei | Nei | MILP | Optimeringsmodell | Ja (scenarier) | Ja (kooperasjon) |
| 14 | Redzic & Olesen | Nei | Nei | ESG-score | Nei | Nei | Ja (K-means) | Nei | Random Forest + ESG | Nei | Nei |
| 15 | Birkedal et al. | Nei | Nei | — | Nei | Nei | Nei | Nei | Ingen formell | Nei | Nei |
| 16 | Romsdal | Nei | Nei | PPC-differensiering | Nei | Nei | Nei | Nei | Rammeverk | Nei | Nei |
| 17 | Grimstad et al. | Nei | Nei | — | Nei | Nei | Nei | Nei | Lean (prosessforslag) | Nei | Nei |
| 18 | Centonze et al. | Nei | Nei | — | Nei | Nei | Nei | LP/ILP | Optimeringsmodell | Ja | Ja (stokastisk) |
| **19** | **Jensen (LOG650)** | **Ja (80/95 %)** | **Ja (CV)** | **—** | **Ja** | **Nei** | **K-means (K=3)** | **Nei** | **Regelmotor R1–R8** | **kr 452 K/år** | **Ja (27 scenarier)** |

---

## 3. Dimensjonsanalyse

### 3.1 Forskningsdesign

Av de 18 referanseoppgavene er 4 rent kvantitative (Hosana, Dybwad & Larsen, Langelo, Centonze et al.), 4 rent kvalitative (Gundersen, Bakken & Solli, Birkedal et al., Grimstad et al.) og 10 bruker blandet metode. LOG650-oppgaven er rent kvantitativ med formalisert modellspesifikasjon i et eget kapittel (kap. 5).

Blant bacheloroppgavene skiller LOG650 seg markant ut. De øvrige bachelorene (Berg et al., Hauge et al., Skogli et al., Birkedal et al., Grimstad et al.) er enten kvalitative casestudier eller kombinerer enkel kvantitativ analyse med intervjuer. Centonze et al. (2025) er den eneste andre bacheloroppgaven med rent kvantitativ tilnærming, men bruker lineær programmering for et helt annet formål (bemanning).

Sammenlignet med masteroppgavene er LOG650 på linje med Hosana (klyngeanalyse med silhouettevalidering) og Dybwad & Larsen (prediktiv analyse med maskinlæring), men under Rydock (som supplerer kvantitativ analyse med simuleringsstudie i anyLogistix) og Nilssen (som kombinerer fem klassifikasjonsanalyser med Monte Carlo-simulering).

### 3.2 Datagrunnlag

LOG650-oppgavens datagrunnlag er unikt i sammenligningssettet. Med 709 aktive artikler fra 14 SAP S/4HANA-tabeller over en 24-månedersperiode overgår den samtlige referanseoppgaver i datadybde og -bredde.

De nærmeste sammenlignbare er Rydock (2023), som bruker ERP-data fra Helse Midt-Norges logistikksenter (~1 400 SKU-er), og Romsdal (2014), som bruker produksjonsdata fra TINE (~500 produkter). Rydock har flere artikler, men LOG650 har mer detaljert artikkel-nivå-analyse med 20+ attributter per artikkel.

Bacheloroppgavene har vesentlig svakere datagrunnlag: Hauge et al. analyserer ~10 artikler med Monte Carlo, Berg et al. bruker bestillingsfrekvens og volumdata uten verdiklassifisering, Skogli et al. analyserer ~50 dimensjoner i et trelager, og Gundersen baserer seg primært på kvalitative intervjuer.

LOG650 er den eneste oppgaven som dokumenterer datakvalitetsbeslutninger systematisk (D-01 til D-08 med begrunnelse og effekt per beslutning). Denne transparensen er ikke representert i noen av referanseoppgavene.

### 3.3 Klassifiseringsmetoder

ABC-analyse er den mest brukte klassifiseringsmetoden og forekommer i 8 av 18 referanseoppgaver. XYZ-klassifisering brukes kun i 2 oppgaver: LOG650 og Nilssen (2021). Tabell 2 oppsummerer klassifiseringsbredden.

**Tabell 2 — Klassifiseringsmetoder per oppgave**

| Oppgave | ABC | XYZ | VED | SDE | FSN | HML | Kraljic | ESG | Antall |
|---|---|---|---|---|---|---|---|---|---|
| Jensen (LOG650) | Ja | Ja | — | — | — | — | — | — | 2 |
| Nilssen (2021) | Ja | Ja | — | Ja | Ja | Ja | — | — | 5 |
| Rydock (2023) | Ja | — | Ja | — | — | — | — | — | 2 |
| Berg et al. (2025) | Ja | — | — | — | — | — | — | — | 1 |
| Hauge et al. (2024) | Ja | — | — | — | — | — | — | — | 1 |
| Gundersen (2023) | Ja | — | — | — | — | — | Ja | — | 2 |
| Dybwad & Larsen (2020) | Ja | — | — | — | — | — | — | — | 1 |
| Skogli et al. (2013) | Ja | — | — | — | — | — | — | — | 1 |
| Redzic & Olesen (2025) | — | — | — | — | — | — | — | Ja | 1 |

Nilssen (2021) har den bredeste klassifiseringsporteføljen med fem skjemaer kombinert via Simple Additive Weighting (SAW). LOG650 bruker to klassifiseringsskjemaer, men integrerer dem med to ytterligere kvantitative metoder (EOQ-avvik og K-means) i en regelmotor. Denne operasjonaliseringen — fra klassifisering til per-artikkel-beslutning — er unik i sammenligningssettet. Nilssens SAW gir en rangert liste, men produserer ikke kategoriske handlingsanbefalinger.

Rydock (2023) bruker ABC og VED (Vital-Essential-Desirable) som grunnlag for bestillingspolitikk. VED-dimensjonen fanger klinisk kritikalitet, noe LOG650 mangler. Dette er et identifisert forbedringsområde.

### 3.4 Optimeringsmodeller og analytiske metoder

**Tabell 3 — Analytiske metoder per oppgave**

| Metode | Oppgaver som bruker den |
|---|---|
| EOQ / partistørrelse | Jensen, Rydock, Dybwad & Larsen, Risholm, Langelo (5) |
| Monte Carlo-simulering | Nilssen, Hauge et al. (2) |
| anyLogistix-simulering | Rydock (1) |
| K-means klyngeanalyse | Jensen, Hosana, Redzic & Olesen (3) |
| LP / MILP | Halvorsen, Centonze et al. (2) |
| Maskinlæring (RF, XGBoost, ARIMA) | Dybwad & Larsen, Redzic & Olesen (2) |
| Poisson / stokastisk modell | Cunin (1) |

LOG650 er den eneste oppgaven som kombinerer klyngeanalyse med tradisjonell lagerklassifisering (ABC/XYZ) og EOQ. Rydock er den eneste som bruker kommersiell simuleringsprogramvare (anyLogistix) for å validere klassifiseringens effekt på bestillingskostnader. Dybwad & Larsen (2020) er de eneste som bruker maskinlæringsalgoritmer for etterspørselsprognoser i en lagerstyrskontekst.

Ingen av referanseoppgavene kombinerer fire kvantitative metoder i en integrert pipeline slik LOG650 gjør. Den nærmeste er Nilssen med fem klassifiseringsanalyser og Monte Carlo-simulering, men uten klyngeanalyse eller regelmotor.

### 3.5 Beslutningsstøtte

Beslutningsstøttemekanismene varierer betydelig. Tabell 4 kategoriserer tilnærmingene.

**Tabell 4 — Beslutningsstøttetype**

| Type | Oppgaver |
|---|---|
| Formell regelmotor | Jensen (R1–R8, sekvensiell prioritet) |
| Rammeverk med handlingsmatrise | Rydock (klassifisering → bestillingspolitikk), Nilssen (SAW → planlegging/etterfylling) |
| DSS / beslutningsverktøy | Cunin (beslutningstre), Risholm (reservedelsverktøy) |
| Optimeringsmodell | Halvorsen (MILP), Centonze et al. (LP/ILP), Langelo (dynamisk programmering) |
| ML-basert prediksjon | Dybwad & Larsen (ARIMA/RF), Redzic & Olesen (Random Forest + ESG) |
| Lean-verktøy | Berg et al. (kanban/5S), Bakken & Solli (VSM/5S), Grimstad et al. (prosessforslag) |
| Klyngeanalyse | Hosana (gruppeidentifikasjon) |
| Kvalitativ anbefaling | Gundersen, Birkedal et al., Skogli et al. |

LOG650s regelmotor R1–R8 er den mest formaliserte beslutningsmekanismen i sammenligningssettet. Den konverterer multikriterieklassifisering til handlingsanbefalinger per artikkel (OVERFØR / BEHOLD / TIL VURDERING / MANGLER DATA). Rydocks rammeverk gir bestillingspolitikkanbefalinger basert på klassifisering, men uten den sekvensielle prioritetslogikken som regelmotor R1–R8 tilbyr. Nilssens SAW gir vektede scorer, men krever manuell tolkning for å omsette til konkrete handlinger.

### 3.6 Kostnadskvantifisering og sensitivitet

De fleste referanseoppgavene kvantifiserer ikke kostnadsbesparelser. Kun tre oppgaver (utenom LOG650) inkluderer estimater:

**Tabell 5 — Kostnadskvantifisering**

| Oppgave | Besparelsesestimat | Sensitivitetsanalyse |
|---|---|---|
| **Jensen (LOG650)** | **kr 452 K/år (base), intervall 176–764 K** | **27 scenarier (S × h × τ_f)** |
| Dybwad & Larsen (2020) | kr 125 K/år | Nei |
| Halvorsen (2019) | 34 % kostnadsreduksjon | Ja (kooperasjonsnivåer) |
| Centonze et al. (2025) | Kostnadsbesparelse (bemanning) | Ja (stokastisk modell) |

LOG650 er den eneste oppgaven som gjennomfører systematisk multiparameter-sensitivitetsanalyse med 27 scenariokombinajoner. Besparelsen forblir positiv i alle scenarier, noe som gir robust beslutningsgrunnlag. Dybwad & Larsen estimerer besparelser på kr 125 K, men anbefaler selv ikke implementering grunnet svakt datagrunnlag og modellusikkerhet.

---

## 4. Syntese

### 4.1 Identifiserte styrker ved LOG650-oppgaven

**S1 — Multimetodeintegrasjon.** Fire kvantitative metoder (ABC, XYZ, EOQ, K-means) integrert via regelmotor R1–R8. Kun Nilssen (2021) har sammenlignbar bredde med fem klassifiseringsskjemaer, men uten klyngeanalyse og uten formalisert beslutningslogikk. LOG650 operasjonaliserer klassifiseringen til per-artikkel-anbefalinger, noe ingen annen oppgave gjør.

**S2 — Reelle operasjonelle data.** n = 709 artikler fra 14 SAP S/4HANA-tabeller med 20+ attributter per artikkel. Ingen annen bacheloroppgave og kun Rydock (master) bruker sammenlignbar ERP-datadybde. Hauge et al. analyserer ~10 artikler, Berg et al. bruker kvalitativ observasjon med frekvensdata, og Gundersen baserer seg på intervjuer.

**S3 — Formell modellspesifikasjon.** Eget modelleringskapittel (kap. 5) med matematiske formuleringer av alle metoder. Verifisert mot implementasjon. Ikke representert i noen referansebacheloroppgave.

**S4 — Reproduserbar analysepipeline.** Deterministisk Python-pipeline med random_state=42, train/test-splitt, StandardScaler fittet kun på treningsdata, og dokumenterte datakvalitetsbeslutninger D-01 til D-08. Unikt i sammenligningssettet.

**S5 — Sensitivitetsanalyse.** 27-scenario rutenett (3 verdier for S, h og τ_f) med reberegning av kandidatsett per scenario. Ingen annen oppgave gjennomfører systematisk multiparameter-sensitivitet.

**S6 — Regelmotor som formalisert beslutningsmekanisme.** Sekvensiell prioritetslogikk R1–R8 som produserer fire kategorier. Mer formalisert enn Rydocks rammeverk (som krever manuell tilpasning) og Nilssens SAW (som gir rangert liste uten handlingskategorier).

**S7 — Kostnadsestimat med intervall.** kr 176 K – 764 K/år (g = 75 %), ikke et enkeltpunktsestimat. Kun Dybwad & Larsen kvantifiserer besparelser blant de øvrige, men uten sensitivitet og med lavere beløp (kr 125 K).

### 4.2 Svakheter og forbedringsområder

**F1 — Manglende ekspertvalidering.** Rydock (2023) validerer klassifisering mot domeneeksperter ved Helse Midt-Norge. Berg et al. (2025) og Hauge et al. (2024) bruker intervjuer med logistikkpersonell og sykepleiere for å kontekstualisere kvantitative funn. LOG650 anerkjenner dette gapet (kap. 8.3), men adresserer det ikke. *Anbefaling:* En strukturert ekspertundersøkelse blant 5–10 innkjøpere som validerer OVERFØR-listen ville styrket praktisk relevans betydelig.

**F2 — Stor TIL VURDERING-kategori (40,1 %).** Kategorien er den største enkeltgruppen. Nilssens SAW-tilnærming tvinger alle artikler inn i en rangert liste uten en tvetydig mellomkategori. Rydocks klassifisering produserer også definitive bestillingspolitikktilordninger for alle artikler. *Anbefaling:* Et sekundært klassifiseringspass — for eksempel Kraljic-matrise (jf. Gundersen, 2023) eller VED-klassifisering (jf. Rydock, 2023) — kunne redusert den tvetydige kategorien.

**F3 — Ingen klinisk kritikalitetsdimensjon.** Rydock inkluderer VED (Vital-Essential-Desirable) som et eget klassifiseringskriterium. VED fanger forsyningskritikalitet for pasientbehandling, noe som er spesielt relevant for sykehusartikler. LOG650 bruker utelukkende kvantitative ERP-metrikker uten klinisk kritikalitet. *Anbefaling:* Et forenklet kritikalitetsmål (binært: kritisk/ikke-kritisk) basert på varegruppe eller klinisk bruk ville styrket modellen.

**F4 — EOQ-stasjonaritet ikke testet.** Wilson-modellen forutsetter stasjonær, deterministisk etterspørsel. LOG650 refererer til Hautaniemi & Pirttilä (1999), men tester ikke stasjonaritet formelt. Dybwad & Larsen (2020) bruker ARIMA som håndterer trend og sesongvariasjon inherent. Nilssens Monte Carlo unngår deterministiske EOQ-forutsetninger helt. *Anbefaling:* En ADF-test eller enkel sesongdekomposisjon for de 20 artiklene med størst ΔTC ville dokumentert forutsetningens holdbarhet.

**F5 — Enkelt klyngealgoritme.** LOG650 bruker kun K-means med silhouettevalidering. Hosana (2023) bruker også K-means med silhouette. Redzic & Olesen (2025) kombinerer klyngeanalyse med Random Forest for klassifisering. *Anbefaling:* En sammenligning med hierarkisk klynging eller DBSCAN ville styrket klyngeresultatene, særlig gitt at silhouettescoren (0,383) indikerer moderat separasjon.

**F6 — Ingen simuleringsvalidering.** Rydock bruker anyLogistix for å simulere effekten av klassifisering på bestillingskostnader. Nilssen og Hauge et al. bruker Monte Carlo. LOG650 estimerer besparelser analytisk, men simulerer ikke den dynamiske effekten av endret bestillingsfrekvens. *Anbefaling:* En forenklet Monte Carlo-simulering av bestillingsfrekvensendringer for de 50 største overføringskandidatene.

**F7 — Begrenset generaliserbarhet.** Resultatene gjelder et enkelt lager (WERKS 3300, LGORT 3001). Rydock dekker hele Helse Midt-Norges logistikksenter. *Anbefaling:* Replikering ved et andre WERKS i Helse Bergen (eller en annen helseregion) ville demonstrert rammeverkets overførbarhet.

### 4.3 Posisjonering i referanselandskapet

LOG650-oppgaven plasserer seg metodisk i den øverste kvartilen av sammenligningssettet. Den overgår alle direkte sammenlignbare bacheloroppgaver uten unntak — dette bekreftes av sensorrapportens uavhengige vurdering. Oppgaven er sammenlignbar med mellomsjiktet av masteroppgavene (Hosana, Cunin) i analytisk dybde, men ligger under de mest metodisk avanserte masteroppgavene (Rydock med simuleringsstudie, Nilssen med fem klassifiseringsskjemaer og Monte Carlo, Dybwad & Larsen med maskinlæring).

Det unike bidraget er kombinasjonen av multikriterieklassifisering med klyngeanalyse og en formell regelmotor i en sykehuskontekst basert på reelle SAP-data. Denne kombinasjonen er ikke representert i noen av de 18 referanseoppgavene.

Sammenlignet med den internasjonale litteraturen som oppgaven selv refererer (van Kampen et al., 2012; Srinivasan & Moon, 1999; Bijvank & Vis, 2012), bekrefter benchmarkanalysen at LOG650 fyller et identifisert forskningsgap: empiriske ERP-baserte casestudier med multikriterieklassifisering i norsk helsesektor.

---

## 5. Oppsummering

Benchmarkanalysen dekker 18 oppgaver fra 5 institusjoner (NTNU, HiMolde, NMBU, HVL, BI) publisert mellom 2013 og 2025. Sammenligningen er gjennomført langs seks dimensjoner: forskningsdesign, datagrunnlag, klassifiseringsmetoder, optimeringsmodeller, beslutningsstøtte og kostnadskvantifisering.

LOG650-oppgaven har komparative fortrinn på datadybde (709 artikler, 14 SAP-tabeller), formell modellspesifikasjon, reproduserbar pipeline, sensitivitetsanalyse (27 scenarier) og formalisert regelmotor (R1–R8). De viktigste forbedringsområdene er ekspertvalidering av anbefalinger, inkludering av klinisk kritikalitet (VED), simuleringsbasert validering av besparelsesestimat og reduksjon av den store TIL VURDERING-kategorien (40 %).

Analysen bekrefter sensorrapportens vurdering om at oppgaven «overgår metodisk alle direkte sammenlignbare bacheloroppgaver» og posisjonerer den i mellomsjiktet av masteroppgavene i analytisk dybde. Det unike bidraget — multikriterieklassifisering kombinert med klyngeanalyse og regelmotor på reelle SAP-data i norsk helsesektor — er ikke representert i noen av referanseoppgavene.
