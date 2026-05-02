---
title: "Peer-review av LOG650-rapport – Thomas Ekrem Jensen"
date: "2026-04-28"
---

# Peer-review-rapport — LOG650 våren 2026

## Forsideopplysninger

| Felt | Verdi |
|---|---|
| Vurderende gruppe | [Fyll inn: vurderende gruppe] |
| Gruppe som blir vurdert | Thomas Ekrem Jensen (individuell innlevering) |
| Tittel på rapporten | *Fra lokalt forsyningslager til regional sentralforsyning: Multikriterieklassifisering og klyngeanalyse for identifisering av overføringskandidater ved Helse Bergen* |
| Veileder | Bård Inge Austigard Pettersen |
| Dato | 28. april 2026 |

---

## Helhetsinntrykk

Rapporten leverer et godt strukturert og empirisk forankret bidrag innenfor sykehuslogistikk. Problemstillingen er klart formulert og direkte koblet til en reell beslutningssituasjon i LIBRA-prosjektet, og analysen kombinerer ABC, XYZ, EOQ og K-means i en regelmotor på en troverdig måte. Datagrunnlaget — 709 aktive artikler med 24 måneders SAP-historikk — er solid, og åtte eksplisitte datavalgsbeslutninger (D-01–D-08) styrker etterprøvbarheten. De viktigste utfordringene er at **gevinstrealiseringsgraden $g$ og ordrekostnaden $S$ ikke er empirisk kalibrert** for Helse Bergen, at **K-means bidrar med begrenset selvstendig informasjon** utover ABC/XYZ (forfatteren erkjenner dette), at **kritikalitetsdimensjonen (VED) er fraværende** som strukturert variabel, og at **ekstern validering mot innkjøpsfaglig skjønn ikke er gjennomført**. Ingen av disse rokker ved studiens grunnleggende kvalitet, men de begrenser rekkevidden på besparelsestallene.

---

## Områdevis vurdering

### 1. Innledning

**Styrker.** Bakgrunnen i avsnitt 1.1 forankrer studien i konkrete sektorforhold (HVFS, LIBRA, NorEngros, APL frem mot 2029), og kobler dette til litteraturen via Volland et al. (2017), Bijvank & Vis (2012) og de Vries (2011). Problemstillingen i 1.2 er presist formulert og operasjonaliserer både *identifikasjon* og *kvantifisering*. Avgrensningene i 1.3 og antagelsene i 1.4 er begrunnet, og parameterintervallene for sensitivitetsanalysen (S, h) introduseres allerede her, noe som gir leseren et tidlig riss av usikkerhetshåndteringen.

**Forbedringspunkter.**
- Studiens *teoretiske* betydning kunne fremheves tydeligere ved siden av den praktiske. Avsnitt 1.1 lander hovedsakelig på det operasjonelle gapet ved Helse Bergen; én setning om hvilken litteraturmessig nyhetsverdi metoderammeverket har (kombinasjonen ABC + XYZ + EOQ-avvik + K-means + regelmotor på SAP-data) vil styrke koblingen mellom forskningsmål og betydning.
- Konkret forslag: legg inn en oppsummerende setning sist i 1.1 som eksplisitt sier "Studien bidrar både operasjonelt (et reproduserbart beslutningsverktøy for HVFS-overføring) og litteraturmessig (kvantitativ casestudie som adresserer gapet identifisert av Saha & Ray, 2019)."

### 2. Litteraturgjennomgang og teoretisk forankring

**Styrker.** Tabell 1 i avsnitt 2.1 gir god oversikt over 18 sentrale kilder, og Tabell 2 i 2.6 sammenligner styrker, svakheter og forutsetninger ved de fire metodene — dette gjør det enkelt for leseren å se hvorfor metodekombinasjonen er valgt. Identifikasjonen av et empirisk gap i litteraturen (Saha & Ray, 2019) er konkret og knyttes direkte til oppgavens bidrag. Det konseptuelle rammeverket i 2.7 (Figur 1) binder de fire metodene sammen i ett bilde.

**Forbedringspunkter.**
- Drøftingen av flerkriterietilnærminger (EDAS, AHP/TOPSIS) i avsnitt 2.1 er kort og avslutter med "Denne oppgaven benytter derfor objektivt beregnbare kriterier". Begrunnelsen kunne styrkes ved å vise eksplisitt hvilke vurderinger som taler imot subjektiv vekting i sykehuskontekst (f.eks. konsistens på tvers av artikler, behov for periodisk reklassifisering uten ekspertpanel).
- Klyngeanalysens posisjon i sykehuslogistikk (2.5) støttes hovedsakelig på Gurumurthy et al. (2021). Et par ytterligere referanser, eller en eksplisitt erkjennelse av at empirisk grunnlag er tynt, vil styrke avsnittet.

### 3. Metode

**Styrker.** Forskningsdesignet i 4.1 plasserer studien som kvantitativ casestudie med deskriptiv, eksplorativ og normativ komponent, og knytter hver komponent til en metode. Datainnsamlingen i 4.2 er detaljert (14 SAP-tabeller, BWART 201/647, ZNB-bestillinger), og dataforbehandlingen i 4.3 dokumenterer åtte beslutninger med konkret effekt og begrunnelse. Etiske betraktninger i 4.4 håndterer manglende VED-data åpent og peker frem mot pilotvalidering.

**Forbedringspunkter.**
- *Validitet og reliabilitet* drøftes i kap. 8.2, men en kort egen oppsummering allerede i 4.4 — med eksplisitte underoverskrifter "intern validitet", "ekstern validitet", "reliabilitet" — vil gjøre det lettere for leseren å plassere disse begrepene i metodekapittelet.
- Reproduserbarhetsbeskrivelsen i 4.3 er god, men avhengighetsspesifikasjonen (versjoner) er først i Vedlegg B. En kort henvisning fra 4.3 til Vedlegg B vil være nyttig.
- Konkret forslag: legg inn et avsnitt 4.6 «Validitet og reliabilitet» som speiler de samme tre begrepene før metodekapittelet avsluttes.

### 4. Analyse og resultater

**Styrker.** Kapittel 6 og 7 er konsistent strukturert: hver delanalyse beskriver datagrunnlag, beregning og resultatpresentasjon i samme rekkefølge. Tabellene 8–15 dekker alle modellutfall (ABC, XYZ, ZZXYZ-validering, EOQ-status, K-means-profiler, regelfordeling og besparelsesscenarier), og figurkoplingene (Fig. 5–12) er godt plassert. ZZXYZ-funnet (33 % samsvar; 7 vs. 79 Z-artikler) er et selvstendig empirisk bidrag som er tydelig kvantifisert. Sensitivitetsanalysen over 27 scenarier gir nødvendig robusthet.

**Forbedringspunkter.**
- I avsnitt 7.5 forklares at "De resterende 28 artiklene (18 fra R4 og 10 fra R5) inngår ikke i besparelsesgrunnlaget". At *alle* 18 R4-artikler mangler FOR\_MANGE\_ORDRER-flagget følger logisk av regelrekkefølgen (R3 fanger først), men leseren får ikke denne forklaringen eksplisitt. Én ekstra setning som klargjør dette vil hjelpe.
- Tabell 10 (ZZXYZ-validering): det vil styrke leservennligheten å markere diagonalen tydeligere (eks. fete celler er allerede gjort, men en kort note om at radsum-totalen 218+150+7 også reflekterer at SAP nesten aldri klassifiserer Z, vil hjelpe lesere som bare ser tabellen.)
- Figur 8: terskelen ved $\tau_f = 1{,}5$ ($f_{\text{obs}} > 1{,}5 f^*$) tilsvarer FREQ\_AVVIK > 0,5. Dobbel notasjon ($\tau_f$ vs. avviksgrense 0,5) krever litt sjonglering — en kort fotnote kan avhjelpe.
- ABC-analysen i 6.1 oppgir "i overkant av 34 millioner kroner" som total årsverdi. Et eksakt tall (eller avrundet med 2–3 siffer) vil være mer i tråd med rapportens øvrige tallpresisjon.

### 5. Diskusjon

**Styrker.** Kapittel 8 dekker fire gode delkapitler: funn opp mot litteratur (8.1), metodekritikk (8.2), praktisk betydning (8.3) og svakheter (8.4). Tabell 16 er et effektivt grep — den setter egne resultater opp mot litteraturen i én oversikt og markerer at K-means-merverdien er "delvis", noe som signaliserer faglig modenhet. Drøftingen av besparelsesestimatets begrensninger i 8.2 (utelater kapitalbinding, transport og engangskostnader) er konkret og balansert.

**Forbedringspunkter.**
- 8.1 kunne sterkere drøfte *uventede* funn. ZZXYZ-divergensen (33 %) trekkes frem, men kunne vært løftet til et eget delkapittel siden det er det enkeltfunnet med størst direkte konsekvens for LIBRA. Praktisk: legg inn en kort underseksjon 8.1.1 «ZZXYZ-divergens som operasjonelt funn» som binder funnet til konkret SAP MM-praksis.
- Implikasjoner for *teori* og *policy* (jf. veiledningens kriterieliste) kunne adresseres mer eksplisitt. Avsnitt 8.3 dekker praksis godt, men en setning eller to om hvilken policy-relevans funnene har for Helse Vest IKT (regional reklassifiseringssyklus, governance for ZZXYZ-vedlikehold) ville fullføre triangelen praksis–teori–policy.

### 6. Konklusjon

**Styrker.** Avsnitt 9.1 svarer eksplisitt på problemstillingen, både kvalitativt (145 artikler) og kvantitativt (kr 451 515 base case, intervall kr 176 374 – 763 903). Refleksjonen over at anbefalingene er et «rangert beslutningsunderlag — ikke verifiserte beslutningsregler» er presis og ærlig. De fire anbefalingene i 9.2 er prioriterte, handlingsrettede og adresserer både umiddelbare (klinisk validering, SAP-parameterjustering) og langsiktige tiltak (12 mnd. evaluering). Forslagene til videre forskning i 9.3 er forankret i de identifiserte begrensningene (ROP, leverandørkonsolidering, replikering, MCDM/veiledet ML).

**Forbedringspunkter.**
- *Studiens bidrag til teori* nevnes i forbifarten (metoderammeverket er reproduserbart), men kunne formuleres som en egen setning eller punkt: hva er konkret nytt som denne studien tilbyr lagerstyringslitteraturen? F.eks. dokumentert empirisk anvendelse av kombinasjonen ABC+XYZ+EOQ-avvik+K-means+regelmotor på SAP-data i nordisk sykehuskontekst, og en kvantifisert ZZXYZ-divergensanalyse.
- 9.2 Anbefaling 4 («evaluer etter 12 måneder») nevner ikke hvilke spesifikke KPI-er som bør spores. To-tre konkrete eksempler (faktisk ordrefrekvens vs. EOQ\_optimal, antall stockouts på overførte artikler, andel artikler med oppdatert ZZXYZ) vil gjøre anbefalingen direkte operasjonaliserbar.

### 7. Skriveflyt, formelle aspekter og helhetsvurdering

**Styrker.** Språket er konsist og fagteknisk presist gjennomgående, med konsekvent bruk av bokmål. APA 7-referansene (norsk stil) er korrekt formatert i referanselisten, og kryssreferansene til figurer og tabeller fungerer godt. Tre-linjes tabellformat (booktabs-stil) og ensartet figurpalett (300 dpi, serif, fargepalett angitt i CLAUDE.md) gir profesjonelt visuelt inntrykk. Bruk av matematiske formler er presist og konsekvent. KI-erklæringen i Vedlegg C er detaljert og ærlig.

**Forbedringspunkter.**
- Forkortelser introduseres jevnt over greit (HVFS, APL, LIBRA, MRP, ROP, EOQ, CV, VED), men en samlet **forkortelsesliste** etter Tabelliste vil hjelpe lesere som hopper inn midt i rapporten.
- Enkelte formler bruker `\text{UNIT\_PRICE}` i LaTeX, mens fritekst bruker både UNIT\_PRICE og «enhetspris». Vurder ett konsistent valg.
- I 6.1 brukes "i overkant av 34 millioner kroner"; i øvrige tabeller oppgis presise summer. Konsistent presisjon (eks. "kr 34,3 mill.") anbefales.
- Sammendragets siste avsnitt drar frem ZZXYZ-funnet i ettertid; siden dette er ett av studiens tydeligste empiriske selvstendige bidrag, kan det med fordel løftes opp i andre eller tredje avsnitt slik at funnet får synlighet allerede ved overflatelesning.
- Originalitet: kombinasjonen ABC + XYZ + EOQ-avvik + K-means + regelmotor på SAP-data er reelt original i nordisk sykehuskontekst. Dette kunne fremheves tydeligere som eksplisitt bidrag både i sammendrag og konklusjon.

---

## Oppsummerende anbefalinger til forfatter (prioritert)

1. **Løft ZZXYZ-divergensen** til et eget element i sammendrag og diskusjon — det er studiens sterkeste selvstendige empiriske funn.
2. **Klargjør R3/R4-overlappslogikken** i 7.5 (én setning om hvorfor alle 18 R4-artikler mangler FOR\_MANGE\_ORDRER).
3. **Legg til forkortelsesliste** etter Tabelliste.
4. **Spesifiser KPI-er** for 12-måneders-evalueringen (anbefaling 4 i 9.2).
5. **Strukturer validitet/reliabilitet** med egne underoverskrifter — enten i 4.4 eller i 8.2 — for å speile veiledningskriteriene direkte.

Rapporten er på et sterkt faglig nivå og er klar for innlevering med moderate justeringer på fremstilling og synliggjøring av eksisterende styrker.
