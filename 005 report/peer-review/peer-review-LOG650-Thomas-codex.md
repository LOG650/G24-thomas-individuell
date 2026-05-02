---
title: "Peer-review av LOG650-rapport - Thomas Ekrem Jensen"
date: "2026-04-28"
---

# Peer-review-rapport - LOG650 våren 2026

## Forsideopplysninger

- Vurderende gruppe: [Fyll inn: vurderende gruppe]
- Gruppe/person som vurderes: Thomas Ekrem Jensen, individuell innlevering
- Rapport som vurderes: *Fra lokalt forsyningslager til regional sentralforsyning: Multikriterieklassifisering og klyngeanalyse for identifisering av overføringskandidater ved Helse Bergen*
- Grunnlag for vurdering: `LOG650_Rapport.docx`, peer-review-veiledning, side-rendering av DOCX og stikkprøvekontroll mot `LOG650_Resultater.xlsx`
- Dato: 28. april 2026

## Helhetsinntrykk

Rapporten er faglig sterk, empirisk forankret og tydelig relevant for en konkret beslutningssituasjon i Helse Bergen/HVFS. Den kombinerer ABC, XYZ, EOQ, K-means og regelmotor på en strukturert måte, og dokumenterer datagrunnlag, forbehandling og modellvalg langt bedre enn det som ofte sees i praktiske casestudier. De sterkeste bidragene er den reproduserbare SAP-baserte analysepipen, den tydelige regelmotoren og funnet om lavt samsvar mellom SAPs ZZXYZ og beregnet CV-klasse.

Samtidig er rapporten ikke helt leveringsklar. Det er flere formalia- og layoutproblemer i frontstoffet, blant annet manglende innholdsfortegnelse, blankt sidetallfelt og et ikke utfylt engelsk abstract. Viktigere faglig: rapportteksten oppgir at samlet ABC-årsverdi er "i overkant av 34 millioner kroner", mens analysefilen `LOG650_Resultater.xlsx` oppgir kr 123 164 460 for 704 ABC-klassifiserte artikler. Denne tallkollisjonen må avklares for innlevering. Videre bør kostnadsparametere, ekstern validering, klinisk kritikalitet og K-means-rollen presiseres noe skarpere.

## Områdevis vurdering

### 1. Innledning

**Styrker.** Innledningen gir en klar og relevant kontekst: HVFS, LIBRA, SAP S/4HANA, lokalt forsyningslager LGORT 3001 og behovet for datadrevet sentraliseringsbeslutning. Problemstillingen er konkret, empirisk testbar og koblet til både identifikasjon av kandidater og estimering av besparelse. Avgrensningene er ryddige, og antakelsene om kostnadsparametere introduseres tidlig.

**Forbedringspunkter.** Innledningen kan styrkes ved å formulere bidraget mer eksplisitt som to separate bidrag: et praktisk beslutningsgrunnlag for HVFS og et metodisk bidrag til kvantitativ lagerklassifisering i nordisk sykehuskontekst. Problemstillingen er presis, men lang; vurder å dele den opp i to forskningsspørsmål rett etter hovedproblemstillingen: (1) hvilke artikler er kandidater, og (2) hva er estimert besparelse. Tittelsiden må også fylles ut med totalt antall sider.

### 2. Litteratur og teoretisk forankring

**Styrker.** Litteraturkapittelet dekker sentrale metoder og binder dem til problemstillingen. Tabellene som oppsummerer litteratur og analysemetoder er nyttige for leseren. Det er positivt at rapporten ikke bare presenterer ABC/XYZ/EOQ isolert, men forklarer hvordan de kan kombineres i et beslutningsrammeverk.

**Forbedringspunkter.** Begrunnelsen for å velge objektive, databaserte kriterier fremfor MCDM-varianter som AHP/TOPSIS bør utdypes. Dette er særlig relevant fordi sykehuslogistikk har kliniske og organisatoriske hensyn som ikke alltid er godt fanget i transaksjonsdata. Diskuter kort hvorfor subjektiv vekting er valgt bort i denne studien, og hva som tapes ved det. Klyngeanalysekapittelet bør også være tydeligere på at K-means her primært brukes som triangulering, ikke som en uavhengig prediksjonsmodell. Hvis terskelen "silhouette over 0,3" brukes som akseptkriterium, bør kilden for akkurat denne terskelen kontrolleres og forklares.

### 3. Metode

**Styrker.** Metodekapittelet er en av rapportens sterkeste deler. Datainnsamlingen er konkret: 14 SAP-tabeller, avgrensning til WERKS 3300/LGORT 3001, 24 måneders periode og tydelige bevegelsestyper. De åtte datavalgsbeslutningene D-01 til D-08 gir god etterprøvbarhet. Det er også en styrke at rapporten åpent beskriver manglende VED-data, manglende ekstern validering og at verktøyet er beslutningsstøtte, ikke en autorisert beslutningsregel.

**Forbedringspunkter.**

Det bør ryddes i koblingen mellom EOQ og leveringstid. I kapittel 6.3 står det at EOQ-avviksanalysen krever tilgjengelig `LEAD_TIME`, men EOQ-formelen som brukes krever bare `D`, `S`, `H`, faktisk ordrefrekvens og enhetspris. I analysescriptet er `LEAD_TIME_DEFAULT` selv kommentert som reservert for fremtidig ROP-modul. Rapporten bør derfor enten fjerne leveringstid som EOQ-krav eller forklare at leveringstid ikke inngår i denne analysen.

K-means-logikken bør presiseres. Featurevektoren inkluderer `|ΔTC|`, men `K_OVERFØR`-klyngen identifiseres etter lav CV og høy verdi, ikke etter kostnadsavvik. Det er metodisk forsvarlig, men leseren trenger en tydelig forklaring på hvorfor `ΔTC` påvirker klyngestrukturen, men ikke inngår direkte i rangsummen som velger `K_OVERFØR`. Alternativt kan rangsummen utvides med høyt `ΔTC` dersom klyngen faktisk skal representere "høy verdi, stabilt forbruk og høyt avvik".

Kostnadsparametrene `S = 750`, `h = 20 %` og `g = 50/75/100 %` er synliggjort og sensitivitetstestet, men ikke empirisk kalibrert for Helse Bergen. Det bør stå tydeligere i metodekapittelet at besparelsen derfor er et scenarioestimat, og at en lokal ABC-kalkyle av ordrekostnad er neste valideringssteg.

### 4. Analyse og resultater

**Styrker.** Resultatkapittelet er ryddig og konsistent. Det er lett å følge hvordan rapporten går fra ABC/XYZ til EOQ, K-means, regelmotor og besparelsesberegning. Tabell 13 og 14 gir god transparens i regelmotoren, og funnet om ZZXYZ-samsvar på 33 % er et sterkt og handlingsrettet resultat. Sensitivitetsanalysen over 27 scenarier gir rapporten vesentlig mer troverdighet enn et enkelt punktestimat ville gjort.

**Forbedringspunkter.** Det viktigste er å kontrollere tallgrunnlaget for ABC-totalverdien. Rapporten sier i kapittel 6.1 at samlet årsverdi er "i overkant av 34 millioner kroner". Analyseoutputen `LOG650_Resultater.xlsx` viser derimot totalverdi kr 123 164 460 for 704 ABC-klassifiserte artikler. Dette er for stort avvik til å stå ukommentert. Enten er rapportteksten utdatert, eller så er Excel-outputen ikke identisk med rapportgrunnlaget. Uansett må tallet avstemmes for innlevering.

I kapittel 7.5 står det at Z-override (R1) er regelen som "fanger flest artikler i overføringskategorien". R1 gir `BEHOLD_LOKALT`, så formuleringen bør endres til "behold lokalt-kategorien" eller "regelsettet". Dette er en liten tekstfeil, men den kommer i et sentralt resultatavsnitt.

R4/R5-forklaringen kan også styrkes. De 28 `OVERFØR`-artiklene uten `FOR_MANGE_ORDRER` er logisk forklart, men det bør fremgå tydeligere at de ikke bidrar til besparelsesgrunnlaget fordi besparelsesformelen kun fanger EOQ-avvik, ikke andre gevinster ved sentralisering.

### 5. Diskusjon

**Styrker.** Diskusjonen er balansert og moden. Den knytter resultater til litteratur, drøfter metodiske svakheter og er tydelig på at modellen ikke erstatter faglig vurdering. Avsnittene om manglende VED, manglende ekstern validering og ikke-kalibrerte kostnadsparametere er spesielt viktige og viser god faglig selvkritikk.

**Forbedringspunkter.** Diskusjonen bør løfte ZZXYZ-divergensen enda tydeligere som et selvstendig operasjonelt funn. Det er ikke bare en valideringsobservasjon; det har direkte konsekvens for SAP MM-vedlikehold, LIBRA-governance og fremtidig reklassifisering. Legg gjerne inn en egen kort underseksjon om "ZZXYZ som styringsrisiko". I tillegg bør policy-/styringsimplikasjoner tydeliggjøres: hvem bør eie klassifiseringsregimet, hvor ofte bør klassifisering oppdateres, og hvordan skal klinisk kritikalitet integreres i SAP- eller beslutningsprosessen?

### 6. Konklusjon

**Styrker.** Konklusjonen svarer direkte på problemstillingen og oppsummerer de viktigste tallene: 145 kandidater, 117 artikler i besparelsesgrunnlaget, base case kr 451 515 per år og sensitivitetsspenn kr 176 374 til kr 763 903. Anbefalingene til Helse Bergen er konkrete og prioriterte.

**Forbedringspunkter.** Anbefaling 4 om evaluering etter 12 måneder bør operasjonaliseres med KPI-er. Eksempler: faktisk ordrefrekvens mot EOQ-optimal frekvens, antall stockouts/restordre for overførte artikler, andel artikler med oppdatert ZZXYZ, endring i lokal lagerverdi, og realisert administrativ tidsbruk per bestilling. Konklusjonen bør også ha en egen setning om studiens metodiske bidrag, ikke bare praktiske bidrag.

### 7. Skriveflyt, formalia og helhetsvurdering

**Styrker.** Språket er gjennomgående presist og faglig kontrollert. Figurer og tabeller er stort sett informative, og referanselisten ser relevant og konsistent ut. KI-erklæringen er mer konkret enn minimumsnivået og bidrar positivt til transparens.

**Forbedringspunkter.** Frontstoffet må ryddes for innlevering:

- Innholdsfortegnelsen er ikke oppdatert og viser bare "Oppdater felt: Ctrl+A, F9".
- Abstract er ikke et engelsk sammendrag, men en plassholder.
- Tittelsiden mangler totalt antall sider.
- Ja/nei-felter i egenerklæring, personvern, REK/NSD og publiseringsavtale ser ikke utfylt ut.
- Side-rendering viser alvorlige layoutproblemer på enkelte sider, blant annet egenerklæringstabellen og flere sider der tekst rendres som smale vertikale bokstavkolonner. Dette kan være renderer-spesifikt, men må kontrolleres i endelig Word/PDF-eksport.
- Bruk av fulljustert tekst gir tidvis store ordmellomrom og svekker lesbarheten. Vurder orddeling eller venstrejustering.
- Vedlegg B sier at fullstendig kildekode finnes i GitHub-repository, men rapporten bør oppgi lenke, commit eller arkivert versjon dersom dette skal være reproduserbarhetsbelegg.

## Prioriterte anbefalinger for revisjon

1. Avstem ABC-totalverdien mellom rapporten og `LOG650_Resultater.xlsx`. Avviket 34 mill. vs. kr 123 164 460 må forklares eller korrigeres.
2. Eksporter rapporten til endelig PDF og kontroller alle sider visuelt. Rett innholdsfortegnelse, abstract, sidetallfelt, ja/nei-felter og layoutfeil for innlevering.
3. Klargjør metodepunktet om EOQ og leveringstid: leveringstid brukes ikke i EOQ-formelen og bør ikke fremstilles som krav for EOQ-avviksanalysen.
4. Presiser K-means-rollen: triangulering, ikke uavhengig fasit. Forklar hvorfor `ΔTC` inngår i featurevektoren, men ikke direkte i `K_OVERFØR`-rangeringen.
5. Styrk valideringsplanen med lokal kalibrering av `S`, `h` og `g`, samt klinisk VED-gjennomgang av alle `OVERFØR`-kandidater.
6. Legg til konkrete KPI-er for 12-måneders evalueringen.

## Samlet vurdering

Rapporten holder et sterkt faglig nivå og har et tydelig praktisk bidrag. Den metodiske kjernen er solid, og analysen fremstår reproduserbar og relevant. De største svakhetene ligger ikke i selve ideen, men i leveringskvalitet, tallkonsistens og presisering av enkelte metodevalg. Med korrigering av tallavviket, ryddet frontstoff/layout og noe skarpere valideringsargumentasjon vil rapporten fremstå betydelig mer robust.
