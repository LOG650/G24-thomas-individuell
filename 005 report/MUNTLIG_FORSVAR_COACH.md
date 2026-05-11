# Muntlig forsvar-coach for LOG650-bacheloren

**Eier:** Thomas Ekrem Jensen
**Formål:** Lære deg rapporten i dybden — ikke oppsummere den — slik at du kan forklare og forsvare hele innholdet muntlig med full forståelse.
**Bruksområde:** Muntlig presentasjon, eksaminasjon, sensorforsvar.
**Komplementær til:**
- `SENSORGUIDE_metodikk.md` — kompakt høynivå metodikk (les den først som rask oppfriskning)
- `SENSORSIMULERING.md` — simulert sensorvurdering med karakter B og kriterieskåre
- `LOG650_Rapport_FINAL.md` — selve rapporten (primærkilde)

---

## 0. Hvordan bruke denne filen

### Lesemetode

1. **Først:** Les `SENSORGUIDE_metodikk.md` (15 min) for å få overblikk og "rød tråd".
2. **Deretter:** Les denne filen kapittel for kapittel. Ikke prøv å lese alt på én økt — del opp i 2–4 økter à 60–90 min.
3. **Per kapittel:**
   - Les "Hva står her" → lukk fil → forklar muntlig for deg selv før du leser videre.
   - Gå gjennom "Hvorfor det står her", "Nøkkelbegreper", "Formler".
   - Gå gjennom "Antagelser", "Styrker", "Svakheter".
   - Test deg selv på Q&A-bolken nederst i hvert kapittel.
   - Memorer **forsvarsformularet** — den ene setningen du alltid kan falle tilbake på.
4. **Til slutt:** Pugg drillings-pakken i kapittel 15 (25 vanligste sensorspørsmål) og elevator-pitchen (kap. 18).

### Hva du *ikke* skal gjøre

- Ikke memorer rapporten ord for ord. Sensor straffer parrotering.
- Ikke unngå svakhetene. Erkjenn dem og vis at du har tenkt gjennom dem — det er den modne akademiske holdningen.
- Ikke spar med tallene. Hovedtallene (709, 145, 117, 257, 284, 23, 451 515, 176 374–763 903, 33 %, 0,383/0,368, $\tau_f = 1{,}5$, $g \in \{50, 75, 100\,\%\}$) må sitte. Resten kan du si "det står i Tabell X i rapporten".

### Q&A-konvensjon

Q&A er skrevet slik:

> **Sensor:** [spørsmål formulert slik en HiMolde-sensor faktisk vil stille det].
> **Du:** [modellsvar 2–4 setninger som du parafraserer, ikke memorerer].
> **Coach-kommentar:** [hva som er fellen, eller hva som er nøkkelen i svaret — denne sier du ikke høyt].

---

## 1. Den røde tråden (40-sekunders versjon du må kunne fra hodet)

Dette er åpningssvaret hvis sensor spør "kan du fortelle kort om oppgaven din":

> «Oppgaven utvikler et reproduserbart, datadrevet beslutningsgrunnlag for å identifisere hvilke artikler ved Helse Bergens forsyningslager — WERKS 3300, LGORT 3001 — som bør overføres til det regionale sentrallageret HVFS. Jeg trekker ut 14 SAP-tabeller via SE16H for perioden 2024–2025, filtrerer til 709 aktive artikler gjennom åtte dokumenterte datavalg, og kjører fire komplementære analyser: ABC for verdi, XYZ for forbruksstabilitet, EOQ-avvik for bestillingseffektivitet og K-means klyngeanalyse for datadrevet validering. En regelmotor med åtte prioriterte regler aggregerer signalene og gir 145 OVERFØR-kandidater, 257 BEHOLD-LOKALT, 284 VURDER og 23 MANGLER DATA. Besparelsesestimatet er kr 451 515/år i base case (g = 75 %), med et sensitivitetsintervall på kr 176 000 – 764 000/år. Et empirisk bifunn er at SAPs eget ZZXYZ-felt bare samsvarer med beregnet CV-klasse i 33 % av tilfellene — et resultat som har umiddelbar operasjonell konsekvens for LIBRA-prosjektet.»

### Hvorfor denne åpningen er sterk

- Du gir **navn** på alt sentralt (WERKS, LGORT, HVFS, SE16H, ABC/XYZ/EOQ/K-means, regelmotor).
- Du gir **fire nøkkeltall**: 145, kr 451 515, 33 %, intervall 176k–764k.
- Du erkjenner usikkerheten (sensitivitetsintervall) før sensor får spurt.
- Du nevner **bifunnet** (ZZXYZ 33 %) — sensor vil spørre, så ta det først.

### Den korte versjonen (10 sekunder, hvis du bare har én setning)

> «Jeg har bygd et SAP-datadrevet rammeverk som identifiserer 145 av 709 artikler ved Helse Bergen som overføringskandidater til HVFS, med estimert besparelse kr 451 515/år base case og intervall kr 176k–764k.»

---

## 2. Sammendrag (s. 184–195 i rapporten)

### 2.1 Hva står her

Sammendraget er fem avsnitt: (1) tema og forankring i LIBRA, (2) datagrunnlag og metode, (3) hovedresultat — 145/257/284/23-fordelingen, (4) besparelse med scenarier og sensitivitet, (5) implementeringsforutsetninger og ZZXYZ-bifunnet. Det er den **kompakte versjonen av hele oppgaven** — under 350 ord.

### 2.2 Hvorfor det står her

Sammendraget gir leseren — sensor inkludert — anledning til å vite hva oppgaven konkluderer med før de leser detaljene. Det er ofte det første og siste sensor leser. Hvis sensor finner motsetninger mellom sammendrag og kapittel 7/9, er det rødt flagg.

### 2.3 Nøkkeltall du må kunne forklare

| Tall | Betydning | Kilde |
|---|---|---|
| **709 aktive artikler** | Etter D-01-filter (1 006 → 709). Ikke totalsortiment. | Tabell 13 |
| **145 OVERFØR (20,5 %)** | Hovedresultatet. Sum av R3 + R4 + R5 = 71 + 18 + 56. | Tabell 14 |
| **257 BEHOLD (36,2 %)** | R1 (143 Z-artikler) + R2 (114 CY-artikler). | Tabell 14 |
| **284 VURDER (40,1 %)** | R6 (160) + R7 (23) + R8 (101). Bevisst stor for presisjon. | Tabell 14 |
| **23 MANGLER DATA** | Manglende CV-historikk eller verdidata. | Tabell 13 |
| **117 i besparelsesgrunnlag** | Av 145 OVERFØR; 28 mangler FOR_MANGE_ORDRER-status. | Avsnitt 7.5 |
| **kr 451 515/år** | Base case ved g = 75 %. | Tabell 15 |
| **kr 176 374 – 763 903/år** | Sensitivitetsintervall over 27 (S, h, $\tau_f$)-kombinasjoner. | Avsnitt 7.6 |
| **33 % samsvar ZZXYZ** | 125 av 375 stemmer mellom SAP-felt og beregnet CV. | Tabell 10 |
| **0,383 / 0,368** | K-means silhouette trening/test. Begge > 0,3-terskel. | Avsnitt 7.4 |

### 2.4 Sensor-Q&A for sammendraget

> **Sensor:** Du nevner 145 artikler i sammendraget. Hvorfor er det 117 i besparelsen?
> **Du:** Besparelsesformelen summerer $\Delta TC_i$ for artikler som *både* er anbefalt OVERFØR *og* har EOQ-status FOR_MANGE_ORDRER. R3-artikler oppfyller begge per definisjon (71 stk). I R4 og R5 (totalt 18 + 56 = 74) ble klyngesignalet (K_OVERFØR) brukt som tilstrekkelig grunnlag for OVERFØR-anbefaling uten at FOR_MANGE_ORDRER var aktivert. De 28 differanseartiklene (74 − 46 R4/R5-treff på FMO = 28) anbefales overført, men har ikke et målbart EOQ-kostnadsavvik å summere — derfor utelates de fra besparelsen, ikke fra OVERFØR.
> **Coach-kommentar:** Ikke kall det "avrundingsfeil" eller "data-rusk". Det er en bevisst konservativ konstruksjon. Bruk ordet "konservativt" — det er metodisk korrekt.

> **Sensor:** Hvorfor presenterer du tre scenarier *og* sensitivitetsanalyse? Er ikke det dobbelt?
> **Du:** De svarer på to forskjellige spørsmål. De tre scenariene varierer kun gevinstrealiseringsgraden $g$ (50/75/100 %), som er en *implementeringsantagelse*. Sensitivitetsanalysen varierer $S$, $h$ og $\tau_f$, som er *modellantagelser*. Tre scenarier viser hvor mye den fysiske gjennomføringen kan koste oss; sensitivitet viser hvor mye modellen selv kan ta feil. Sammen utgjør de en fullstendig usikkerhetsbeskrivelse.
> **Coach-kommentar:** Dette er et klassisk forsvar-spørsmål. Bruk distinksjonen "implementeringsantagelse vs. modellantagelse" — det signaliserer at du forstår skillet.

> **Sensor:** Du fremhever 33 %-funnet om ZZXYZ. Er ikke det egentlig irrelevant for hovedproblemstillingen?
> **Du:** Det er et empirisk bifunn, ikke svar på problemstillingen, og det presenteres som sådan. Men det har direkte operasjonell relevans for LIBRA: hvis ZZXYZ-feltet er systematisk feil, så er all MRP-logikk som hviler på det også upålitelig — og MRP-kjøringer driver bestillingsforslag i SAP. Funnet styrker dermed *motivasjonen* for oppgavens kjernearbeid: man kan ikke stole på systemets egen klassifisering.
> **Coach-kommentar:** Sensor vil teste om du forstår at "selvstendig empirisk funn" og "svar på problemstillingen" er to forskjellige bidrag. Begge er gyldige, og du har erkjent skillet i kap. 9.1.

### 2.5 Forsvarsformular

> "Sammendraget viser hovedresultatet — 145 OVERFØR-kandidater og kr 451 515 base case — men understreker bevisst usikkerheten gjennom sensitivitetsintervallet. Det er ikke et punktestimat, og det er ikke ment som det."

---

## 3. Forord (s. 166–181 i rapporten)

### 3.1 Hva står her

Fire korte avsnitt: takk til veileder Bård Inge Pettersen, takk til Helse Bergen / Helse Vest IKT for datatilgang, en personlig motivasjon (rollen som SAP MM-konsulent og det "underutnyttede datagrunnlaget"), takk til samboer Hilde, signert Stavanger mai 2026.

### 3.2 Hvorfor det står her

Forordet er ikke faglig substans — det er en sjangerregel. Men det forteller sensor:

1. Du har tilgang til faktiske SAP-data fra en reell case (ikke synteseksempel).
2. Du har en rolle/erfaring som forklarer hvorfor du kan tolke SAP MM korrekt (legitimt domeneautoritet).
3. Du har samarbeid med veileder og partnerorganisasjon (legitim institusjonell forankring).

### 3.3 Hva som *ikke* står der — og hvorfor det er bevisst

- Ingen detaljert prosjektbeskrivelse (det er i kap. 1 og 3).
- Ingen forhåndsoppsummering av funn (det er i sammendraget).
- Ingen "denne oppgaven er viktig fordi…"-retorikk. HiMolde sin malstil ber om korte forord.

### 3.4 Sensor-Q&A for forordet

> **Sensor:** Du jobber som SAP MM-konsulent ved Helse Vest IKT. Har du sett denne studiens funn i din profesjonelle rolle?
> **Du:** Ikke som strukturert analyse — det er nettopp gapet jeg adresserer. I rollen min ser jeg at SAP MM brukes til drift, men ikke til datadrevet styringsbeslutninger. Studien er et systematisert forsøk på å lukke det gapet og er ikke knyttet til konkrete operative beslutninger jeg har deltatt i. Det er heller ingen interessekonflikt — datatilgangen er gitt for forskningsformål, ikke for å understøtte en bestemt konklusjon.
> **Coach-kommentar:** Sensor kan teste rollekonflikt-tematikken. Vær åpen og presis: dataeier er institusjonen, ikke deg personlig.

> **Sensor:** Hvor mye av oppgaven har du gjort selv?
> **Du:** Hele den faglige retningen — metodevalg, regelutforming, tolkning av resultater og konklusjon — er mitt eget arbeid. Veileder har gitt kritisk feedback. KI-verktøy (Claude) er brukt til kodestøtte, layout av figurer og språkbearbeiding, og dette er deklarert eksplisitt i Vedlegg C i tre kategorier. Rådata fra SAP er aldri lagt inn i KI-verktøyet, og alle resultater er reproduserbare ved at `random_state=42` brukes gjennom hele pipelinen.
> **Coach-kommentar:** Dette er det viktigste enkeltspørsmålet om akademisk integritet i en post-KI-verden. Tre setninger som dekker: eget arbeid, deklarert KI-bruk, dataverning.

### 3.5 Forsvarsformular

> "Forordet er kort fordi alt substansielt hører hjemme i kapittel 1 og videre. Det dokumenterer institusjonell forankring og datatilgang."

---

## 4. Kapittel 1 – Innledning

### 4.1 Avsnitt 1.1 — Bakgrunn og aktualisering

#### Hva står her

Tre lag av kontekst: (1) sykehuslogistikk er ressurskrevende — 30–40 % av driftskostnader (Volland et al., 2017); (2) HVFS etableres regionalt med NorEngros som operatør og APL-leveranser frem mot 2029; (3) LIBRA-prosjektet ruller ut SAP S/4HANA regionalt, som teknisk gjør tverr-foretak-analyser mulig. Avsnittet avsluttes med tre bidragstyper — metodisk, praktisk, empirisk — og målgruppe.

#### Hvorfor det står her

1.1 plasserer studien både i et **faglig** rom (sykehuslogistikk-litteratur) og i et **institusjonelt** rom (HVFS + LIBRA). Sensor vil bedømme om problemstillingen er faglig forankret *og* praktisk relevant — 1.1 dekker begge.

#### Nøkkelbegreper

- **APL (avdelingspakkede leveranser):** ferdigpakkede leveranser direkte fra HVFS til avdeling, uten mellomlagring ved Helse Bergen. Forutsetter stabil etterspørsel — derfor er XYZ (variabilitet) en kritisk klassifiseringsdimensjon for APL-egnethet.
- **HVFS:** Helse Vest Forsyningssenter. Regionalt sentrallager, driftet av NorEngros. Erstatter (delvis) lokale forsyningslagre.
- **LIBRA:** Helse Vest IKTs SAP S/4HANA-utrullingsprogram. Gir datamessig harmonisering på tvers av foretak.
- **30–40 % driftskostnader (Volland):** ikke "logistikk er dyrt", men "sykehuslogistikk er en *strategisk* kostnadsdriver". Denne andelen rettferdiggjør oppgavens omfang.

#### Antagelser og beslutninger

- Avgrensning til medisinsk forbruksmateriell — legemidler, implantater og dyrt utstyr er eksplisitt utenfor scope.
- Implisitt: 24 mnd. transaksjonsperiode (2024–2025) er tilstrekkelig for både XYZ-CV og EOQ-avvik.

#### Styrker sensor vil rose

- Tre uavhengige kilder for relevans (Volland-tall, HVFS-prosjekt, LIBRA-prosjekt).
- Eksplisitt navngitt målgruppe (innkjøpsfaglig + Helse Vest IKT + forskere).
- Bidragsstrukturen "metodisk / praktisk / empirisk" gir sensor en sjekkliste for vurderingen.

#### Svakheter sensor kan utfordre

- 30–40 %-tallet er fra én review-studie. Sensor kan be om kryssreferanse.
  - **Forsvar:** "Volland et al. (2017) er en systematisk gjennomgang av 145 publikasjoner og er den dominerende sekundærkilden på dette området. Tallet brukes i konteksten av at logistikk er en *vesentlig* kostnadsdriver, ikke som presist estimat."
- "30–40 %" kan virke vidt. Det er ikke et tall fra Helse Bergen.
  - **Forsvar:** "Korrekt — det er et bransjeestimat, ikke et lokalt estimat. Helse Bergen har ikke offentliggjort tilsvarende ABC-kalkyle av logistikkostnader. Det er begrunnelse for at studien er aktuell, ikke en lokal baseline."

#### Sensor-Q&A

> **Sensor:** Du sier oppgaven plasserer seg "i skjæringspunktet mellom lagerstyring og innkjøpsoptimalisering". Kan du utdype hva som ligger i den distinksjonen?
> **Du:** Lagerstyring handler om klassifisering og *plasseringsbeslutninger* — hvilken artikkel hører hjemme hvor og under hvilket regime. Innkjøpsoptimalisering handler om *bestillingseffektivitet* — frekvens, batch-størrelse og kostnadsavvik mot EOQ. Mitt rammeverk gjør begge: ABC + XYZ + K-means er lagerstyringsverktøy, mens EOQ-avviksanalysen er innkjøpsoptimalisering. Regelmotoren binder dem sammen ved å bruke EOQ-signalet som ett av flere beslutningskriterier for overføringsanbefalingen.
> **Coach-kommentar:** Distinksjonen viser at du forstår den faglige posisjoneringen — ikke bare anvender metodene.

> **Sensor:** Hva mener du egentlig med "datadrevet beslutningsgrunnlag"? Er det ikke bare en buzzword?
> **Du:** Konkret betyr det her tre ting: (1) alle klassifiseringer er beregnet fra rådata, ikke hentet fra SAP-felter som kan være utdaterte; (2) hele pipelinen er deterministisk og reproduserbar med `random_state=42`, slik at samme input gir samme output; og (3) anbefalingen per artikkel kan spores tilbake til de fire underliggende signalene (ABC, XYZ, EOQ, K-means) og den spesifikke regelen som ble utløst. Det er motsatsen til skjønnsbaserte beslutninger som ikke er etterprøvbare.
> **Coach-kommentar:** "Datadrevet" er buzzword, men i din kontekst har det tre operasjonaliserte krav. List dem opp.

### 4.2 Avsnitt 1.2 — Problemstilling

#### Hva står her

Den overordnede problemstillingen formuleres først som praktisk spørsmål (hvilke artikler bør sentraliseres, hva er verdt det), og operasjonaliseres deretter som forskningsspørsmål:

> Hvordan kan multidimensjonal klassifisering og klyngeanalyse av SAP-transaksjonsdata identifisere hvilke artikler ved Helse Bergens forsyningslager (WERKS 3300, LGORT 3001) som er kandidater for overføring til HVFS, og hva er det estimerte besparelsespotensialet?

To eksplisitte avgrensninger: (a) identifikasjon, ikke gjennomføring; (b) anbefaling, ikke autoritativ beslutning.

#### Hvorfor det står her

Forskningsspørsmålet er **kontrakten** mellom deg og sensor. Alle senere kapitler skal bidra til å besvare dette spesifikke spørsmålet. Sensor vil teste i kap. 9 om du faktisk har svart på det du sa du skulle svare på.

#### Antagelser og beslutninger

- **Todelt:** "hvilke artikler" *og* "hva er besparelsespotensialet". Sensor kan teste begge separat.
- "Multidimensjonal" — ikke bare ABC, ikke bare EOQ. Hele oppgaven står og faller på trianguleringsargumentet.
- "Estimert" — du har sagt eksplisitt at det er et estimat, ikke en presis prediksjon. Sensor kan ikke holde deg ansvarlig for at base case ikke er presist.

#### Styrker

- Presis, todelt, operasjonaliserbar.
- Forankret i konkret SAP-data (ikke generisk).
- Avgrenset på flere nivåer (WERKS, LGORT, sortiment, periode).

#### Svakheter

- Ordet "kritikalitet" var med i proposalen (VED-dimensjonen), men er strøket i rapportens forskningsspørsmål.
  - **Forsvar:** "VED-dimensjonen kunne ikke operasjonaliseres maskinlesbart fra SAP MARA/MARC. Konsekvensen er eksplisitt diskutert i kap. 4.4 og 8.4, og inkludert som anbefaling 1 i kap. 9.2 (klinisk pilot før implementering). Jeg har valgt å være ærlig om hva analysen *kan* og *ikke kan*, fremfor å late som om en proxy var dekkende."
- LGORT er endret fra 3000 (proposal) til 3001 (rapport).
  - **Forsvar:** "Ja — 3001 er det operative forsyningslageret ved WERKS 3300; 3000 var en feilskrivning i proposalen som er rettet i koden og dokumentet. Det påvirker ikke metoden, kun nomenklaturen."

#### Sensor-Q&A

> **Sensor:** Problemstillingen din er todelt: "hvilke artikler" og "hva er besparelsen". Hvilken del er sterkest besvart?
> **Du:** Identifikasjonsdelen er kvalitativt sterkt besvart — 145 artikler med eksplisitt regelsporing per artikkel. Besparelsesdelen er svakere fordi den hviler på litteraturparametre ($S$, $h$, $g$) som ikke er lokalt kalibrert. Det er erkjent eksplisitt: derfor presenterer jeg et *intervall* (kr 176k–764k), ikke et punktestimat. Sensitivitetsanalysen viser at konklusjonen om at det *finnes* en positiv besparelse, holder over alle 27 scenarier — men den eksakte verdien er ikke fastslått.
> **Coach-kommentar:** Du må eie svakheten her. Sensor vil teste om du forstår skillet mellom "robust kvalitativt funn" og "presist kvantitativt estimat".

> **Sensor:** Hvorfor ikke bare bruke SAP sine egne ABC/XYZ-felt? Hvorfor hele dette rammeverket?
> **Du:** To grunner. For det første viser kap. 7.2 at samsvaret mellom SAP-feltet ZZXYZ og beregnet CV-klasse bare er 33 %, så feltet er ikke pålitelig. For det andre er problemstillingen *bredere* enn ABC/XYZ alene — jeg trenger også EOQ-avvik (for å kvantifisere besparelse) og en regelmotor (for å aggregere signaler til én anbefaling per artikkel). SAP-feltet hadde gitt meg en klassifisering, men ikke et beslutningsgrunnlag.
> **Coach-kommentar:** ZZXYZ-funnet er ditt eget arbeid, ikke en gitt premiss. Bruk det aktivt for å begrunne metodevalget.

### 4.3 Avsnitt 1.3 — Avgrensninger

#### Hva står her

Seks avgrensninger med eksplisitt begrunnelse: sortiment (forbruksmateriell), lagersted (LGORT 3001), artikkelstatus (D-01), analyseperiode (24 mnd.), metodevalg (ROP utenfor scope), generaliserbarhet (kun WERKS 3300, men metoderammeverk er overførbart).

#### Hvorfor det står her

Hver avgrensning eliminerer en sensor-innvending. Hvis du *ikke* avgrenset til medisinsk forbruksmateriell, ville sensor spurt "hvorfor analyserer du legemidler med samme regelmotor?". Hvis du *ikke* avgrenset til 24 mnd., ville sensor spurt "hvorfor stoppet du der?".

#### Nøkkelbegreper

- **WERKS:** SAP-anleggskode. 3300 = Helse Bergen.
- **LGORT:** SAP-lagerstedskode under WERKS. 3001 = forsyningslager.
- **MTART:** SAP-materialtypekode. Brukes for å skille forbruksmateriell fra implantater/legemidler/utstyr.
- **Aktiv status (D-01):** D_ANNUAL > 0 ELLER TOTAL_STOCK > 0. Filteret er inklusivt (OR), ikke eksklusivt (AND).

#### Antagelser og beslutninger

- Avgrensningen til ett lagersted er **metodisk nødvendig**, ikke vilkårlig: 3001 er det eneste med 24 mnd. komplett transaksjonshistorikk for forbruksmateriell. Inkludering av andre lagre ville innført datakvalitetsforskjeller som ikke kan kontrolleres.
- ROP (reorder point) utelates fordi EINE PLIFZ dekker kun 6 % — datagrunnlaget er for tynt.

#### Styrker

- Avgrensningene er **begrunnet**, ikke bare listet (sensor sjekker det).
- Generaliserbarhet er eksplisitt nedjustert: studien gjelder Helse Bergen, men metoden er overførbar.

#### Svakheter

- Bare 24 mnd. forbruksdata kan være kort for noen artikkeltyper (sesong, sjeldne hendelser).
  - **Forsvar:** "Korrekt — lengre periode ville styrket XYZ-robustheten. Men data utover 24 mnd. var ikke tilgjengelig med tilstrekkelig kvalitet, og COVID-aftermath kan forvrenge eldre data. Konsekvensen er erkjent i kap. 8.4."

#### Sensor-Q&A

> **Sensor:** Hvorfor inkluderte du ikke implantater og dyrt utstyr? De er da også relevante for HVFS?
> **Du:** Implantater og dyrt utstyr styres gjennom egne SAP-objekter — andre WERKS/LGORT eller andre MTART-koder — og har en helt annen forsyningslogikk. Implantater er ofte case-bestilte og lagres ikke; dyrt utstyr har egne anskaffelsesprosesser. Å inkludere dem i samme regelmotor ville krevd ulik parametrisering per kategori, og fellesgrunnlaget for terskelverdier ville falt bort. Det er en metodisk grunn til avgrensningen, ikke en utelatelse.
> **Coach-kommentar:** Avgrensninger er ikke "ting du droppet". De er metodiske beslutninger med faglig begrunnelse.

> **Sensor:** Kan resultatene overføres til de andre helseforetakene i Helse Vest?
> **Du:** Metoderammeverket — kombinasjonen ABC + XYZ + EOQ + K-means + regelmotor — er fullt overførbart, ettersom LIBRA gir samme SAP S/4HANA-datastruktur på tvers. Men tallresultatene gjelder kun Helse Bergen: sortimentet, leverandøravtaler og driftsmodell vil variere mellom foretakene. Anbefaling 4 i kap. 9.3 foreslår eksplisitt replikering til Stavanger, Fonna og Førde som videre forskning.
> **Coach-kommentar:** Skill mellom *metode* og *tallresultat*. Sensor straffer hvis du overgenerelaliserer tallene.

### 4.4 Avsnitt 1.4 — Antagelser

#### Hva står her

Fem antagelser med begrunnelse: $S = 750$ NOK, $h = 20\,\%$, 24 mnd. analyseperiode, LEAD_TIME = 14 dager, besparelsesformelen $B_{HVFS} = \sum \Delta TC_i \cdot g$.

#### Hvorfor det står her

Antagelsene er det sensoren vil angripe hardest. Ved å formalisere dem i 1.4 — *før* metoden presenteres — viser du at du er åpen om grunnlagsforutsetningene. Hver antagelse er en eksplisitt forhandlingsbar premiss.

#### Formelutdrag

$$B_{\text{HVFS}} = \sum_{i \in \text{OVERFØR}} \Delta TC_i \cdot g$$

Der $\Delta TC_i = TC_{\text{actual},i} - TC_{\text{optimal},i}$ og $g \in \{0{,}50, 0{,}75, 1{,}00\}$.

#### Antagelser i detalj

| Antagelse | Verdi | Begrunnelse | Sensitivitet testet |
|---|---|---|---|
| Ordrekostnad S | 750 NOK | Bijvank & Vis (2012), Kelle et al. (2012) | Ja: {500, 750, 1000} |
| Holdekostnad h | 20 % av UNIT_PRICE | Ketkar & Vaidya (2014) | Ja: {15, 20, 25 %} |
| LEAD_TIME | 14 dager | Bransjepraksis (dekker 94 %) | Nei (ikke brukt i EOQ-frekvensanalyse) |
| Gevinstrealisering g | 50 / 75 / 100 % | Worst/Base/Best — implementeringsfriksjon | Implicit i 3 scenarier |
| Analyseperiode | 24 mnd. | SAP-tilgjengelighet, sesongdekking | Implicit i datavalg |

#### Sensor-Q&A

> **Sensor:** Hvor kommer 750 NOK fra? Har du estimert den selv?
> **Du:** Nei. 750 NOK er en bransjestandard fra to refererte studier — Bijvank & Vis (2012) og Kelle et al. (2012) — som dekker administrative kostnader for å opprette, godkjenne og følge opp en innkjøpsordre i SAP. Lokal kalibrering ville krevd egen aktivitetsbasert kostnadsanalyse av innkjøpsprosessen, som ligger utenfor bachelorscopen. Sensitivitetsanalysen tester verdien over {500, 750, 1000} NOK og viser at konklusjonen — at besparelsen er positiv — holder over hele intervallet.
> **Coach-kommentar:** Erkjenn at det ikke er lokalt kalibrert, men understrek at sensitivitetsanalysen kompenserer.

> **Sensor:** Hvor pålitelig er gevinstrealiseringsgraden g = 75 %?
> **Du:** Den er en ekspertantagelse uten direkte empirisk belegg fra Helse Bergen. Verdien reflekterer en realistisk forventning om at implementeringsfriksjon — SAP MM-justering, leverandørforhandlinger, prosessomstilling — absorberer ca. 25 % av det teoretiske potensialet. Intervallet 50 % (worst) til 100 % (best) er valgt for å fange spennvidden av mulig realiseringskvalitet. Det er den enkeltparameteren som har størst kvalitetsavhengighet, og det er nettopp derfor jeg presenterer tre scenarier i stedet for ett.
> **Coach-kommentar:** Sensor leter etter at du ikke later som g er empirisk. Si "ekspertantagelse" — det er nøyaktig hva det er.

> **Sensor:** Hvorfor er LEAD_TIME satt til 14 dager når dataen er dårlig?
> **Du:** LEAD_TIME inngår *ikke* i EOQ-avviksanalysen min — den er basert på ordrefrekvens, ikke bestillingspunkt. 14-dagers standardverdien er en plassholder for en fremtidig ROP-modul (anbefaling 1 i kap. 9.3), der EINE må berikes med faktiske leveringstider. I dagens analyse har den ingen materiell effekt.
> **Coach-kommentar:** Dette er en felle. Sensor tester om du vet hvilke parametre som faktisk *brukes*. LEAD_TIME er deklarert men ikke aktiv.

#### Forsvarsformular for kap. 1

> "Innledningen forankrer studien i tre samtidige initiativer — HVFS, NorEngros-APL og LIBRA — og avgrenser problemstillingen til identifikasjon og kvantifisering, ikke implementering. Antagelsene er eksplisitt formalisert *før* metoden presenteres, slik at sensitivitetsanalysen kan teste dem direkte."

---

## 5. Kapittel 2 – Litteratur og teori

### 5.1 Avsnitt 2.1 — Litteraturgjennomgang

#### Hva står her

En narrativ gjennomgang av 22 sentrale kilder organisert tematisk: (1) ABC-tradisjonen (Silaen, Gupta), (2) XYZ som komplement (Nowotyńska, Suryaputri), (3) flerkriterietilnærminger og EDAS (Keshavarz Ghorabaee), (4) klyngeanalyse i SCM (Srinivasan & Moon), (5) tre-dimensjonsrammeverket til van Kampen, (6) gap-identifikasjonen (Saha & Ray). Avsluttes med Tabell 1 som matriserer alle 22 kilder med tema og relevans.

#### Hvorfor det står her

Litteraturgjennomgangen har tre funksjoner: (a) demonstrere fagforankring, (b) plassere oppgaven i et eksisterende forskningsfelt, (c) identifisere det konkrete gapet som studien fyller. Det er en *kontrakt* med sensor: "her er konteksten, og her er hvor mitt bidrag passer inn".

#### Nøkkelbegreper

- **Gap-identifikasjon:** Saha & Ray (2019) — review av 137 artikler — konstaterer at *empiriske casestudier som kombinerer ABC + XYZ + EOQ + K-means på faktiske ERP-data* er underrepresentert. Det er gapet studien adresserer.
- **Volland-tallet (30–40 %):** systematisk gjennomgang av 145 publikasjoner. Bekrefter at lagerstyring er det dominerende forskningsområdet innen sykehuslogistikk.

#### Styrker sensor vil rose

- 22 referanser med tematisk struktur (ikke alfabetisk liste).
- Tabell 1 gir én rad per kilde med eksplisitt relevans for *denne* oppgaven.
- Eksplisitt gap-identifikasjon (ikke bare "lite forsket på").

#### Svakheter sensor vil utfordre

- 22 kilder er **i nedre sjikt** for bacheloroppgaver (sensor forventer 25–35).
  - **Forsvar:** "Antall referanser er ikke et selvstendig kvalitetsmål — det avgjørende er at hver kilde brukes aktivt i argumentasjonen. Av de 22 er alle sitert i metodologisk eller empirisk argumentasjon, ingen er pyntereferanser. Bredere referansebase ville styrket litteraturgjennomgangen, og det er erkjent i SENSORSIMULERING-vurderingen som en svakhet."
- **Manglende lærebok-referanse for EOQ** (Silver, Pyke & Thomas eller tilsvarende).
  - **Forsvar:** "Ja, lærebok-referansen kunne vært inkludert som grunnreferanse. Hautaniemi & Pirttilä (1999) og Ketkar & Vaidya (2014) dekker det teoretiske grunnlaget for EOQ-anvendelsen, men en kanonisk lærebok ville ha gitt bredere forankring. Det er en svakhet jeg ville rettet i en revidert versjon."
- **K-means i sykehus har bare én kjernekilde** (Gurumurthy et al., 2021).
  - **Forsvar:** "Korrekt — K-means i sykehuslogistikk er et lite litteraturområde. Srinivasan & Moon (1999) er den generelle SCM-referansen, mens Gurumurthy et al. (2021) er den sykehusspesifikke. At feltet er smalt er nettopp en del av gap-argumentet."

#### Sensor-Q&A

> **Sensor:** Hva er gapet i litteraturen, helt konkret?
> **Du:** Saha & Ray (2019), som er en systematisk review av 137 artikler, konstaterer at det mangler empiriske casestudier som anvender flere klassifiseringsmetoder samlet på faktiske ERP-data i sykehuskontekst — og som leverer et eksplisitt besparelsesestimat som output. Min studie fyller dette ved å kombinere ABC, XYZ, EOQ-avvik og K-means på 14 SAP-tabeller fra Helse Bergen, med en regelmotor som aggregerer signalene og en besparelsesformel som kvantifiserer effekten. Det er ikke metodisk nyhet i hvert enkelt verktøy, men kombinasjonen og operasjonaliseringen.
> **Coach-kommentar:** "Saha & Ray" er navnet du må ha klart. Det er din kjernereferanse for gap-argumentet.

> **Sensor:** Du nevner Partovi & Burton (1993) i teksten, men de er knapt integrert i analysen?
> **Du:** Partovi & Burton brukes som grunnreferanse for å begrunne *at* ABC er utilstrekkelig alene — de viser at single-criterion ABC ignorerer kritikalitet og variabilitet. Denne argumentasjonen rettferdiggjør hvorfor jeg utvider til ABC+XYZ+EOQ+K-means. Deres AHP-baserte multikriterietilnærming er ikke implementert i mitt rammeverk fordi AHP krever subjektiv vekting, noe jeg eksplisitt vil unngå for å sikre etterprøvbarhet. Bruken er teoretisk, ikke metodisk overtatt.
> **Coach-kommentar:** Hvis sensor griper én underutnyttet referanse, snu det til "den er teoretisk fundament for et metodisk valg" — det er gyldig.

### 5.2 Avsnitt 2.2–2.5 — De fire kjernemetodene

#### Hva står her

Fire korte avsnitt (2.2 ABC, 2.3 XYZ, 2.4 EOQ, 2.5 K-means). Hvert avsnitt presenterer metoden konseptuelt med én eller to nøkkelreferanser og henviser til kapittel 5 for matematisk spesifikasjon.

#### Hvorfor det står her

Avsnittene har én funksjon hver: forklare *hvorfor metoden er valgt* og *hvilken dimensjon den dekker*. Den matematiske formuleringen kommer i kap. 5 — duplisering er bevisst unngått.

#### De fire dimensjonene

| Metode | Dimensjon | Blindsone | Komplement |
|---|---|---|---|
| ABC | Verdi (kapitalbinding) | Ignorerer variabilitet, kritikalitet | XYZ + VED |
| XYZ | Forbruksstabilitet (CV) | Sier ingenting om verdi eller bestillingsmønster | EOQ |
| EOQ | Bestillingseffektivitet (frekvensavvik) | Forutsetter stasjonær etterspørsel; univariat | K-means |
| K-means | Multivariat mønster (CV + verdi + \|ΔTC\|) | Ingen kausal tolkning; sensitiv for K | Regelmotor (transparens) |

Dette er **trianguleringslogikken**. Hver metode har en blindsone som motiverer neste metode. Sensor vil teste om du kan resitere denne kjeden.

#### Hvorfor disse fire og ikke andre?

- **EDAS** (Keshavarz Ghorabaee et al., 2015): krever subjektiv vekting → utelukker reproduserbarhet → dropped.
- **AHP/TOPSIS**: samme problem som EDAS + tyngre å forsvare → dropped, men foreslått i kap. 9.3.
- **DBSCAN / hierarkisk klynging**: alternativer til K-means; ikke testet i denne oppgaven, men foreslått i kap. 8.4 som videreutvikling.
- **Veiledet ML**: forutsetter merkede fasitklasser for HVFS-egnethet, som ikke eksisterer. Dropped, men foreslått i kap. 9.3 (etter pilotfasen).

#### Sensor-Q&A

> **Sensor:** Hvorfor valgte du K-means og ikke DBSCAN eller hierarkisk klynging?
> **Du:** K-means ble valgt fordi den er den dominerende klyngealgoritmen i SCM-litteraturen (Srinivasan & Moon, 1999) og fordi den gir tolkbar partisjonering der hvert datapunkt har én klyngetilhørighet — noe regelmotoren krever som input. DBSCAN ville gitt støy-deteksjon (outliers), men ikke nødvendigvis bedre separasjon for klassifiseringsformål. Hierarkisk klynging ville gitt et dendrogram, men krever subjektivt valg av kuttenivå — et K-valg er mer reproduserbart via silhouette-optimering. Sammenligning med alternative algoritmer er foreslått som videre forskning i kap. 8.4.
> **Coach-kommentar:** Erkjenn at alternativene finnes; begrunn hvorfor K-means passer dette formålet. Det er ikke "K-means er best", det er "K-means er passende for denne kombinasjonen av krav".

> **Sensor:** EOQ forutsetter stasjonær etterspørsel. Har du testet det?
> **Du:** Nei, jeg har ikke gjennomført formell stasjonaritetstest (f.eks. augmented Dickey–Fuller). Begrensningen er erkjent i kap. 8.2. Men EOQ anvendes primært på X-artikler (CV < 0,5), som per definisjon har lav relativ variabilitet — Wilson-forutsetningen er dermed *relativt godt oppfylt der EOQ faktisk brukes operativt*. EOQ-avviksanalysens primære formål er dessuten relativ rangering av artikler etter kostnadsavvik, ikke eksakt kostnadsestimering. Hvis etterspørselen har sesongkomponent, vil den typisk skalere $f^*$ proporsjonalt på tvers av sammenlignbare artikler, slik at rangordenen bevares.
> **Coach-kommentar:** Dette er en av sensorens favorittfeller. Du må kunne svare på (a) hva forutsetningen er, (b) at den ikke er testet, (c) hvorfor det ikke ødelegger analysen — *rangering vs. absoluttverdi*.

### 5.3 Avsnitt 2.6 — Lagerstyring i helsesektoren og VED

#### Hva står her

Sykehuslogistikk skiller seg fra industri ved at forsyningssvikt har direkte kliniske konsekvenser (Bijvank & Vis modelleres som lost-sales). Saha & Ray dokumenterer at ERP-baserte casestudier mangler. Fragapane er nøkkelreferansen for APL-leveranser. de Vries advarer om organisatoriske barrierer. VED-dimensjonen (Vital/Essential/Desirable) presenteres konseptuelt — og det er deklarert eksplisitt at den **ikke** operasjonaliseres fordi SAP MARA/MARC ikke inneholder VED-felter.

#### Hvorfor det står her

VED-diskusjonen i 2.6 er bevisst plassert *i litteraturkapitlet* (ikke gjemt bort senere) for å vise at du *kjenner* dimensjonen og har truffet et **bevisst valg** om ikke å operasjonalisere den. Sensor vil straffe hvis VED ikke nevnes; du tar brodden av kritikken ved å adressere det tidlig.

#### Nøkkelbegreper

- **VED:** Vital (livsviktig — leveransesvikt kan true pasientliv), Essential (vesentlig — leveransesvikt kan forsinke behandling), Desirable (ønskelig — leveransesvikt har begrenset klinisk konsekvens). Gupta et al. (2007) er originalreferanse.
- **Lost-sales-modell:** I sykehus betyr stockout at pasienten ikke får behandling — det er ikke som butikk-stockout der kunden venter. Bijvank & Vis modellerer dette eksplisitt.
- **R1-regelen som proxy:** Siden VED ikke kan operasjonaliseres, brukes XYZ = Z (uregelmessig forbruk) som *proxy* for klinisk kritikalitet — antagelsen er at kritiske artikler ofte har uregelmessig forbruk (akutt-bruk). Ikke perfekt, men forsiktig.

#### Antagelser og beslutninger

- VED kan **ikke** utledes fra SAP-data og er erkjent som svakhet.
- Anbefaling 1 i kap. 9.2 (klinisk pilotvalidering) er **mitigasjonsstrategien** — du sier at før noe faktisk overføres, må VED-vurderingen gjøres manuelt av klinisk personell.

#### Styrker

- VED-diskusjonen plasseres tidlig (kap. 2.6, ikke gjemt i diskusjonen).
- Mitigeringen (klinisk pilot) er innebygd i anbefalingen.

#### Svakheter

- VED-proxy via XYZ = Z er ikke validert empirisk.
  - **Forsvar:** "Korrekt — proxy-antagelsen 'høy CV korrelerer med klinisk kritikalitet' er ikke empirisk testet. Det er en hypotese basert på at akutt-brukte artikler ofte har sporadisk forbruksmønster. En pilotvalidering med kliniske VED-vurderinger som referanse vil teste hvor god proxien faktisk er — dette er innbakt i anbefaling 1."

#### Sensor-Q&A

> **Sensor:** Hvis VED er så viktig i sykehuslogistikk, hvorfor utelot du den helt?
> **Du:** Jeg utelot den ikke — jeg erkjente den eksplisitt og kompenserte. VED er en klinisk vurdering som ikke er maskinlesbar i SAP MARA/MARC. Operasjonalisering ville krevd manuell innhenting fra kliniske avdelinger, som ligger utenfor bachelorscopen for en kvantitativ casestudie. Regelmotorens R1-regel — XYZ = Z fører til BEHOLD_LOKALT — fungerer som en delvis proxy: høy variabilitet er ofte assosiert med akutt klinisk bruk. Anbefaling 1 i kap. 9.2 sier eksplisitt at klinisk VED-vurdering må gjennomføres før noen artikkel faktisk overføres. Jeg gir altså et beslutningsgrunnlag, ikke en autoritativ beslutning.
> **Coach-kommentar:** Ikke unnskyld utelatelsen. Forklar den som metodisk avgrensning + mitigasjon. Det er en moden akademisk holdning.

### 5.4 Avsnitt 2.7 — Konseptuelt rammeverk (Figur 1)

#### Hva står her

Et konseptuelt rammeverk presentert tekstlig og visuelt (Figur 1: `Fig00_Konseptuelt_Rammeverk.png`). Modellen viser **sekvensiell analyse** fra rådata til beslutningsanbefaling: ABC + XYZ + EOQ + K-means → regelmotor → besparelse.

#### Hvorfor det står her

Sensoren leser figuren før hen leser detaljene. Den må derfor være selvforklarende. Rammeverket er din **mentale modell** av hele oppgaven, og det er det første du peker på i muntlig presentasjon.

#### Figur 1 — lesetolkning

Figuren skal vise (fra venstre/topp):
- **SAP-rådata** (14 tabeller via SE16H)
- **D-01 → D-08 datavalg** (1 006 → 709)
- **Fire parallelle analyser**: ABC, XYZ, EOQ, K-means
- **Regelmotor** (R1–R8) aggregerer signalene
- **Output**: OVERFØR / BEHOLD / VURDER / MANGLER DATA
- **Besparelse**: $\Delta TC \cdot g$ for de 117

Fargepalett (konsistent gjennom hele rapporten):
- Grønn `#1E7D45` — positiv / HVFS-kandidat / optimal
- Oransje `#D68910` — vurdering / nøytral
- Rød `#B03A2E` — negativ / behold lokalt / problem
- Blå `#0B3D8C` — analyse / datavisualisering
- Grå `#888888` — referanselinjer
- Tittel-mørkblå `#1A2A44` — overskrifter og dark text

#### Sensor-Q&A

> **Sensor:** Kan du tegne meg din analysepipeline på et stykke papir?
> **Du:** [Tegn:] SAP via SE16H → 14 tabeller → D-01–D-08 datavalg → 709 aktive artikler → fire parallelle analyser (ABC verdi, XYZ stabilitet, EOQ-avvik, K-means klynge) → regelmotor med 8 prioriterte regler R1–R8 → fire output-kategorier (OVERFØR 145, BEHOLD 257, VURDER 284, MANGLER 23) → besparelse $\sum \Delta TC_i \cdot g$ for de 117 i skjæringspunkt OVERFØR ∩ FOR_MANGE_ORDRER → kr 451 515 base case.
> **Coach-kommentar:** Forsvarsmanualens viktigste øvelse: kunne tegne hele pipelinen fra hodet på 60 sekunder.

> **Sensor:** Hvorfor er regelmotoren sentral i rammeverket?
> **Du:** Fordi de fire analysene gir hver sin dimensjon av signalstyrke, men sensor og innkjøper trenger én anbefaling per artikkel. Regelmotoren er aggregeringslaget — den oversetter multivariate signaler til diskret beslutningsstøtte med transparent sporbarhet (hver artikkel kan spores til én konkret regel). Uten den ville analysen produsert fire klassifiseringer som sensor måtte aggregere subjektivt; med den får sensor en revisjonbar regelkjede.
> **Coach-kommentar:** Nøkkelordet er **transparens** — sensor vil rose at regelen kan auditeres per artikkel.

#### Forsvarsformular for kap. 2

> "Kapittel 2 plasserer studien i et eksisterende felt og identifiserer Saha & Rays gap — empiriske ERP-baserte casestudier. De fire metodene er valgt fordi de dekker komplementære dimensjoner (verdi, stabilitet, bestillingseffektivitet, multivariat mønster), og rammeverket i Figur 1 viser hvordan de aggregeres til én anbefaling per artikkel."

---

## 6. Kapittel 3 – Casebeskrivelse

### 6.1 Avsnitt 3.1 — Helse Bergen og Helse Vest (Tabell 3, Figur 2)

#### Hva står her

Helse Bergen er det største foretaket i Helse Vest (Haukeland Universitetssykehus, ~500 000 innbyggere opptaksområde). SAP-strukturen: WERKS 3300, LGORT 3001, EKGRP 300/3000, bestillingstype ZNB. Bevegelsestyper: BWART 201 (standard forbruk) og BWART 647 (lokal forbruksvariant). Tabell 3 oppsummerer nøkkeltall.

#### Hvorfor det står her

Casebeskrivelsen gir sensor det operasjonelle vokabularet hen trenger for å forstå datakildene i kap. 4. Uten 3.1 ville "WERKS 3300" og "BWART 647" være ren forkortelses-tåke.

#### Nøkkelbegreper

- **BWART 201:** SAP standard bevegelsestype for vareforbruk til kostnadssted (uttak fra ubegrenset beholdning). Universell.
- **BWART 647:** SAP standard er "GI for stock transport order, one-step" — men ved Helse Bergen brukes 647 *kundespesifikt* for forbruk innenfor samme anlegg. Du må kunne forklare dette skillet hvis sensor er SAP-kyndig.
- **BWART 101:** Varemottak fra leverandør. Ikke brukt direkte i XYZ (det er innkjøp, ikke forbruk), men relevant for EKBE-data.
- **ZNB:** Helse Bergens lokale bestillingstype.

#### Sensor-Q&A

> **Sensor:** Hvorfor inkluderer du BWART 647 når SAP-standarden tilsier at det er en cross-plant-bevegelse?
> **Du:** Ved Helse Bergen er BWART 647 anvendt kundespesifikt for forbruk til avdeling/kostnadssted innenfor samme anlegg, ikke som cross-plant-overføring. Dette er bekreftet med innkjøpsmiljøet ved Helse Bergen og er en lokal SAP-tilpasning. Å utelate 647 ville underestimert det reelle forbruket. Kombinasjonen 201 + 647 fanger det reelle uttaket ut av lager og utelukker interne overføringer og returer som ville forvrengt etterspørselsestimatet.
> **Coach-kommentar:** Dette er et SAP-domeneeksperten-spørsmål. Vis at du har sjekket lokal bruk, ikke bare standardlitteratur.

> **Sensor:** Hvor representativt er WERKS 3300 for andre helseforetak i Helse Vest?
> **Du:** WERKS 3300 er det største forsyningslageret i regionen og har det rikeste datagrunnlaget — 24 mnd. komplett transaksjonshistorikk for forbruksmateriell. Strukturelt er andre WERKS sammenlignbare (samme SAP-struktur etter LIBRA), men sortimentet vil variere. Replikering til Stavanger, Fonna og Førde er foreslått som videre forskning. Metoderammeverket er overførbart; tallresultatene er ikke.
> **Coach-kommentar:** Konsekvent skille mellom metode og tall (du sa det samme i kap. 1.3 — sensor liker konsistens).

### 6.2 Avsnitt 3.2 — HVFS og LIBRA-prosjektet

#### Hva står her

HVFS er under etablering som regionalt sentrallager med NorEngros som operatør. APL frem mot 2029. LIBRA er Helse Vest IKTs SAP S/4HANA-utrullingsprogram som gjør tverr-foretak-analyser teknisk mulig.

#### Hvorfor det står her

Du må kunne forklare hvorfor *denne* studien er aktuell *nå*. Svaret er at HVFS + LIBRA er to samtidige initiativer som gjør spørsmålet "hvilke artikler skal sentraliseres" både operasjonelt presserende og teknisk besvarbart.

#### Nøkkelbegreper

- **APL (Avdelingspakkede leveranser):** ferdigpakkede leveranser direkte til avdeling, uten mellomlagring ved Helse Bergens forsyningslager. Krever stabil forbruk for å fungere — det er derfor XYZ er en kritisk klassifiseringsdimensjon.
- **NorEngros:** vant offentlig anbudskonkurranse som HVFS-operatør. Du driver ikke analysen for NorEngros — du analyserer på vegne av Helse Bergen / Helse Vest IKT.
- **Stordriftsfordeler:** HVFS samler innkjøp på tvers av foretak → bedre forhandlingsmakt mot leverandører + redusert administrativ overhead per ordre.

#### Sensor-Q&A

> **Sensor:** Hvordan vil APL endre forsyningskjeden konkret?
> **Du:** I dag bestiller Helse Bergens forsyningslager fra leverandør, lagrer bulk lokalt i LGORT 3001 og pakker om/distribuerer til avdeling. Med APL via HVFS bestiller NorEngros fra leverandør, plukker per avdeling, og leverer ferdigpakket direkte. Mellomledd-lagringen forsvinner. Operasjonell konsekvens for klassifiseringen: artikler med stabilt forbruk egner seg fordi NorEngros kan planlegge plukk-rytmen; artikler med uregelmessig forbruk (Z) krever lokal beredskap fordi APL-syklusen ikke håndterer akutt-uttak godt.
> **Coach-kommentar:** Du knytter teknologien (APL) direkte til klassifiseringskriteriet (XYZ). Det er essensen i hvorfor X/Y/Z er valgt som dimensjon.

### 6.3 Avsnitt 3.3 — Problemkontekst og datagrunnlag

#### Hva står her

Bro til kapittel 4: 14 SAP-tabeller via SE16H, fire funksjonelle kategorier (masterdata, forbruksdata, innkjøpsdata, supplerende). Eksempler på datakvalitetsutfordringer (PEINH, manglende EKPO for 204 artikler).

#### Hvorfor det står her

Avsnittet er en forhåndsannonsering av kap. 4. Det forteller sensor "vi har data, men det er ikke trivielt — her er teaseren, full detalj kommer".

#### Forsvarsformular for kap. 3

> "Casebeskrivelsen plasserer analysen i en konkret operasjonell kontekst: WERKS 3300 / LGORT 3001 ved Helse Bergen, med SE16H-uttrekk av 14 SAP-tabeller, mens HVFS og LIBRA er de samtidige initiativene som gjør problemstillingen aktuell."

---

## 7. Kapittel 4 – Metode og data

### 7.1 Avsnitt 4.1 — Forskningsdesign

#### Hva står her

Kvantitativ casestudie med tre komponenter:
- **Deskriptiv** — ABC/XYZ-klassifisering av eksisterende mønstre
- **Eksplorativ** — K-means klyngeanalyse for mønstergjenkjenning
- **Normativ** — regelmotor og besparelsesformel for handlingsanbefalinger

Ingen spørreundersøkelser, intervjuer eller deltakerobservasjon. Datauttrekk i januar 2026 av forfatteren. Analyseenhet = enkeltartikkel (SKU). Populasjon = 709 aktive artikler i LGORT 3001 for 2024–2025.

#### Hvorfor det står her

Forskningsdesign er sensorens første verktøy for vurdering: er metoden konsistent med spørsmålet? Beskrivelsen *deskriptiv + eksplorativ + normativ* viser at du forstår at oppgaven har tre faglige modi — det forutser sensor-spørsmål om hvorfor metodene har ulik epistemisk status.

#### Nøkkelbegreper

- **Casestudie:** én operasjonell kontekst (Helse Bergen) studeres i dybden. Ikke generalisering på tvers; metoderammeverket er overførbart, ikke tallene.
- **Analyseenhet:** SKU = Stock Keeping Unit = artikkelnummer (MATNR). Alle klassifiseringer er per artikkel, ikke per varegruppe eller per leverandør.
- **Reliabilitet:** SAP-transaksjonsdata er automatisk registrert → ikke utsatt for selvrapporterings- eller hukommelsesfeil. Høyere enn intervjudata.
- **Validitet:** intern (måler vi det vi tror?) vs. ekstern (gjelder dette for andre kontekster?). Studien har høy intern validitet, lav ekstern (begrenset til WERKS 3300).

#### Antagelser

- ERP-data er fri for selvrapporteringsfeil. Saha & Ray (2019) støtter dette.
- Forfatteren har lesetilgang som SAP MM-konsulent — datatilgangen er gitt for forskning, ikke for å understøtte en bestemt konklusjon.

#### Sensor-Q&A

> **Sensor:** Hvorfor casestudie og ikke en bredere komparativ studie?
> **Du:** Tre grunner: (1) bare WERKS 3300 har 24 mnd. komplett transaksjonshistorikk for forbruksmateriell — andre lagre mangler dybde i MSEG/EKBE; (2) en komparativ studie ville krevd standardisering av data på tvers, noe LIBRA først nå begynner å gi; (3) bachelorscopen tilsier dybde fremfor bredde. Casestudien gir høy intern validitet for Helse Bergen og et reproduserbart rammeverk for senere replikering.
> **Coach-kommentar:** "Dybde fremfor bredde" er den klassiske casestudie-begrunnelsen. Bruk den, men koble til datatilgjengeligheten.

> **Sensor:** Studien er rent kvantitativ. Mangler du ikke en kvalitativ dimensjon?
> **Du:** Studien har bevisst valgt kvantitativt fokus for å maksimere reproduserbarhet og fjerne subjektivt skjønn fra klassifiseringen. Den kvalitative dimensjonen — innkjøpsfaglig og klinisk vurdering — er ikke utelatt, men plassert i implementeringsfasen via anbefaling 1 og 2 i kap. 9.2. Det er en bevisst arbeidsdeling: jeg leverer det kvantitative beslutningsgrunnlaget, og det kvalitative skjønnet legges på som valideringslag.
> **Coach-kommentar:** "Arbeidsdeling kvantitativ analyse + kvalitativ validering" er en moden formulering. Sensor straffer hvis du later som om alt skal være kvantitativt.

### 7.2 Avsnitt 4.2 — Datainnsamling (Tabell 4, Figur 3)

#### Hva står her

14 SAP-tabeller hentet via SE16H. Tabell 4 lister dem med beskrivelse og kategori (masterdata / forbruksdata / innkjøpsdata / supplerende). Råuttrekket = 1 006 artikler, redusert til 709 i 4.3. BWART 201 og 647 spesifisert. EINE PLIFZ dekker bare 6 % → D-05.

#### Hvorfor det står her

Tabell 4 er **revisjons-referansen**. Hvis en annen analytiker vil etterprøve studien, må de vite nøyaktig hvilke tabeller som er hentet og fra hvilken kategori. Sensor kan teste om du kan navngi tabellene.

#### De fire kategoriene — pugg disse

| Kategori | Tabeller | Brukes til |
|---|---|---|
| **Masterdata** | MARA, MAKT, MARC, MARD, MBEW, MDMA | Identifikasjon, pris, ABC/XYZ-validering |
| **Forbruksdata** | MSEG (BWART 201/647) | XYZ-CV, D (årsforbruk) for EOQ |
| **Innkjøpsdata** | EKKO, EKPO, EKBE | ABC-verdi (EKPO NETWR), ordrefrekvens (EKBE) |
| **Supplerende** | EINA, EINE, T023T, T024 | Leveringstid (EINE PLIFZ), varegruppenavn |

#### Sensor-Q&A

> **Sensor:** Kan du nevne de viktigste SAP-tabellene dine og hva de gir deg?
> **Du:** MARA + MAKT gir artikkelnummer og tekst. MBEW gir standardpris (STPRS) og prisenhet (PEINH) — UNIT_PRICE = STPRS / PEINH. MSEG gir forbrukstransaksjoner med BWART 201 og 647 — grunnlag for CV-beregning. EKPO gir faktisk innkjøpsverdi (NETWR) — grunnlag for ABC når data finnes. EKBE gir ordrefrekvens — grunnlag for EOQ-avvik. MDMA gir SAPs egne ZZABC og ZZXYZ — brukt kun til kryssvalidering, ikke som primær klassifisering. Disse seks er kjernen; de resterende åtte er enten støtte (T023T, T024) eller dekker for marginale tilfeller (EINA, EINE, MARC, MARD).
> **Coach-kommentar:** Forsøk å huske rekkefølgen MARA → MBEW → MSEG → EKPO → EKBE → MDMA. Det er den narrative kjeden fra masterdata til validering.

> **Sensor:** Hva er SE16H, og hvorfor brukte du den?
> **Du:** SE16H er SAPs transaksjon for direkte lesetilgang til databasetabeller med utvidet filtrering. Den gir read-only-tilgang — ingen endringer i systemet — og er den standardiserte måten å hente strukturerte uttak på for analyseformål. Alternativene ville vært BW/BO-rapporter (krever forhåndsbygde kuber) eller direkte SQL (ikke standard tilgangsvei i SAP S/4HANA). SE16H ga meg fleksibiliteten til å hente eksakt de feltene jeg trengte for hver tabell.
> **Coach-kommentar:** Detalj som viser SAP-fagkunnskap. Hvis sensor er ikke-SAP, vil ordet "read-only" være tilstrekkelig forsikring.

### 7.3 Avsnitt 4.3 — Dataforbehandling (Tabell 5, D-01–D-08, Figur 4)

#### Hva står her

Åtte eksplisitte datavalgsbeslutninger D-01 til D-08 dokumentert i Tabell 5. Hver representerer et punkt der analytikeren måtte velge mellom alternative behandlingsmåter.

#### Hvorfor det står her

D-01–D-08 er **transparensens hjerte** i hele oppgaven. De gjør at en hvilken som helst annen analytiker kan reprodusere studien. Sensor vil rose dette eksplisitt.

#### De åtte datavalgsbeslutningene — fullstendig

| ID | Beslutning | Effekt | Hvorfor det er nødvendig |
|---|---|---|---|
| **D-01** | Populasjonsavgrensning: D_ANNUAL > 0 OR TOTAL_STOCK > 0 | 1 006 → 709 | Inaktive artikler (ingen forbruk + ingen beholdning) er irrelevante for HVFS-vurdering |
| **D-02** | PEINH-korrigering: UNIT_PRICE = STPRS / PEINH | Korrigerer prisenhet | STPRS er pris per PEINH-enheter; uten korrigering ville priser være feilskalert med faktor 10 eller 100 |
| **D-03** | Beregnet ABC-verdi for 204 artikler uten EKPO | Bruker D_ANNUAL × UNIT_PRICE | Manglende EKPO innebærer ikke at artikkelen er irrelevant — standardpris × forbruk er rimelig estimat |
| **D-04** | CV-basert XYZ erstatter ZZXYZ | Beregnet klasse foretrukket | 33 % samsvar gjør ZZXYZ upålitelig som primær |
| **D-05** | LEAD_TIME = 14 dager standard | Dekker 94 % | EINE PLIFZ dekker bare 6 %; standardverdien er plassholder for fremtidig ROP |
| **D-06** | MSEG_STATUS blank → AKTIV | Antar normal drift | Manglende statusverdi tolkes som default-aktiv |
| **D-07** | EKPO-verdi prioriteres over beregnet | TOTAL_NETWR > 0 kreves for EKPO-kilde | Faktiske innkjøpsverdier er mer presise enn standardpris × forbruk |
| **D-08** | Annualisering: ACTUAL_FREQ = ORDER_COUNT × 12/24 | 24 mnd → år | EOQ-avvik må sammenlignes på årsbasis |

#### Pugg-trick

Hvis sensor spør om en spesifikk beslutning, husk denne mnemoteknikken:
- **D-01** = "filter" (populasjon)
- **D-02** = "pris" (PEINH)
- **D-03** = "beregnet pris" (manglende EKPO)
- **D-04** = "XYZ-valg" (CV over ZZXYZ)
- **D-05** = "leveringstid" (14 dager)
- **D-06** = "status-default"
- **D-07** = "EKPO-prioritet"
- **D-08** = "annualisering"

#### Sensor-Q&A

> **Sensor:** D-02 — kan du forklare PEINH-korrigeringen?
> **Du:** STPRS i MBEW er ikke pris per stykk, men pris per PEINH-enheter. For mange medisinske forbruksartikler er PEINH = 10 eller 100. Hvis en hanske har STPRS = 150 NOK og PEINH = 100, så er enhetsprisen 1,50 NOK/stk, ikke 150. Uten korrigeringen ville verdiberegningen blitt overestimert med faktor 100 for slike artikler — og hele ABC-rangeringen ville falt sammen. UNIT_PRICE = STPRS / PEINH er derfor en helt nødvendig korreksjon, ikke en preferanse.
> **Coach-kommentar:** Bruk konkret eksempel (hanske, 150/100 = 1,50). Sensor husker eksempler bedre enn formler.

> **Sensor:** D-03 — er det metodisk forsvarlig å bruke beregnet verdi for 204 artikler?
> **Du:** Det er en *kjent svakhet* som er eksplisitt dokumentert i kap. 8.2. Antagelsen er at STPRS i MBEW er en rimelig tilnærming til faktisk innkjøpspris. Av de 204 havner 98 i A-klassen og 63 i B-klassen, så feilen ville hatt størst effekt der den potensielt er mest skadelig. Risikoen dempes imidlertid av at regelmotoren krever *flere* sammenfallende signaler for OVERFØR-anbefaling — en isolert ABC-feil vil sjelden alene utløse feilklassifisering. Anbefaling i kap. 9.3 er å verifisere prisavviket for disse 204 artiklene i en oppfølgingsstudie.
> **Coach-kommentar:** "Kjent svakhet" + "redundans gjennom triangulering" + "anbefalt videreundersøkelse" = full forsvarsstrategi.

> **Sensor:** Hvorfor er D-01 et OR-filter og ikke AND?
> **Du:** OR-logikken — D_ANNUAL > 0 ELLER TOTAL_STOCK > 0 — er inklusiv. En artikkel kan ha aktiv beholdning uten å ha hatt forbruk i analyseperioden (f.eks. nylig anskaffet og ennå ikke brukt) eller motsatt (forbrukt fra varemottak uten å bli liggende på lager). Begge tilstander indikerer at artikkelen er operasjonelt relevant. AND-filteret ville ekskludert begge disse tilstandene og redusert populasjonen vesentlig — antakelig fjernet legitimt aktive artikler.
> **Coach-kommentar:** OR/AND-logikk er enkel, men sensor kan spørre for å sjekke om du har tenkt over det. Svaret er at OR er metodisk bredere og forsvarlig.

### 7.4 Avsnitt 4.4 — Etiske betraktninger og begrensninger

#### Hva står her

Tre ting: (1) ingen personopplysninger (kun artikkelnivå), (2) parametervalg er begrunnet og testet i sensitivitet, (3) eksplisitt erkjennelse av at VED-dimensjonen mangler.

#### Hvorfor det står her

Etisk avsnitt er forventet sjangerregel. Det viktige er at du adresserer VED-mangelen *her*, ikke senere — det viser at du har tenkt på de kliniske konsekvensene før implementering.

#### Sensor-Q&A

> **Sensor:** Hvilke etiske risikoer ser du i å bruke verktøyet?
> **Du:** Primært én: at en klinisk kritisk artikkel anbefales overført, og at HVFS-leveransesvikten påvirker pasientbehandling. Mitigasjonen er todelt: R1-regelen i regelmotoren holder Z-artikler (uregelmessig forbruk) lokalt som proxy, og anbefaling 1 i kap. 9.2 krever klinisk VED-vurdering før noen artikkel faktisk overføres. Studien produserer beslutningsstøtte, ikke autoriserte beslutninger — den endelige overføringen er en klinisk validert prosess.
> **Coach-kommentar:** Skill mellom "verktøyet kan ta feil" (akseptert) og "verktøyet kan brukes feil" (ansvar). Anbefaling 1 fanger det siste.

### 7.5 Avsnitt 4.5 — Bruk av kunstig intelligens

#### Hva står her

Claude er brukt til kodestøtte, figurgenerering og språkbearbeiding. Tre eksplisitte kategorier (kode / figurer / tekst). Rådata aldri lagt inn i KI-verktøy. Vedlegg C har full deklarasjon.

#### Hvorfor det står her

HiMolde-retningslinjer krever eksplisitt KI-deklarasjon. Plasseringen i metodekapitlet er bevisst — det er en *metodisk* opplysning, ikke en etterord-erklæring.

#### Sensor-Q&A

> **Sensor:** Hvilken del av rapporten ville ikke vært laget hvis du ikke hadde brukt KI?
> **Du:** Den faglige retningen ville vært den samme — metodevalg, regelutforming, tolkning av resultater og konklusjon er mitt eget arbeid. Det KI bidro mest til er (a) iterasjonshastigheten i Python-utviklingen, slik at jeg kunne kjøre flere eksperimentelle parametervariasjoner, og (b) språklig bearbeiding for å gjøre lange faglige resonnementer mer konsise. Uten KI ville rapporten vært skrevet, men antakelig med færre sensitivitetsscenarier (27 stk krevde mange parametriserte kjøringer) og lengre prosatekst.
> **Coach-kommentar:** Vær konkret om hva KI gjorde og hva du gjorde. Vag om bidrag er rødt flagg; konkret deklarasjon er respektert.

#### Forsvarsformular for kap. 4

> "Metodekapitlet etablerer reproduserbarhet på tre nivåer: SE16H gir read-only-tilgang til 14 SAP-tabeller, åtte eksplisitte datavalgsbeslutninger D-01–D-08 dokumenterer hver transformasjon, og `random_state=42` sikrer deterministisk output. KI-bruk er deklarert i tre kategorier, og VED-mangelen er erkjent med klinisk pilot som mitigasjon."

---

## 8. Kapittel 5 – Modellering (kjernen i oppgaven)

Dette er det **viktigste kapitlet for sensor**. Hvis du må prioritere én del å pugge i dybden, er det denne. Forvent at sensor vil be deg utlede minst én formel for hånd.

### 8.1 Avsnitt 5.1 — ABC-modellen (Tabell 6)

#### Hva står her

ABC-analyse er en klassifiseringsregel basert på Pareto. Formel: $v_i = D_i \times \text{UNIT\_PRICE}_i$ (årsverdi per artikkel). Artikler sorteres synkende, kumulativ verdiandel $C_i$ beregnes, og grensene 80 % og 95 % anvendes. Tabell 6 oppsummerer alle parameterne.

#### Hvorfor det står her

ABC er den enkleste metoden men også den med flest blindsoner. Sensor vil teste om du forstår at **enkelhet ikke er svakhet** — Pareto er bredt akseptert og direkte koblet til kapitalbinding.

#### Formler — utled disse for hånd

**Årsverdi per artikkel:**

$$v_i = D_i \times \text{UNIT\_PRICE}_i$$

der $D_i$ = annualisert forbruk (enheter/år) og $\text{UNIT\_PRICE}_i$ = STPRS / PEINH (NOK/enhet).

**Kumulativ verdiandel:**

$$C_i = \frac{\sum_{j=1}^{i} v_j}{V_{\text{tot}}}, \quad V_{\text{tot}} = \sum_{j=1}^{N} v_j$$

**Klassifiseringsregel:**
- A hvis $C_i \leq 0{,}80$
- B hvis $0{,}80 < C_i \leq 0{,}95$
- C hvis $C_i > 0{,}95$

#### Tallregneeksempel (oppdiktet for illustrasjon)

| MATNR | $D_i$ | UNIT_PRICE | $v_i$ |
|---|---|---|---|
| Hanske A | 50 000 | 1,50 | 75 000 |
| Suturer B | 800 | 120 | 96 000 |
| Bandasje C | 30 000 | 2,80 | 84 000 |

Sortert synkende etter $v_i$: Suturer B (96 000), Bandasje C (84 000), Hanske A (75 000).
Total $V_{\text{tot}} = 255\,000$. Kumulativt:
- Suturer B: $C_1 = 96\,000/255\,000 = 0{,}376$ → A
- Bandasje C: $C_2 = 180\,000/255\,000 = 0{,}706$ → A
- Hanske A: $C_3 = 255\,000/255\,000 = 1{,}000$ → C (siden $C_3 > 0{,}95$)

Hvis sensor ber deg vise en utregning på papir, dette er strukturen.

#### Antagelser og beslutninger

- Grenser 80/95 % er **standardverdier** fra Silaen et al. (2023). Du har *ikke* selv kalibrert dem.
- 25,7 % av artiklene blir A-klasse (vs. kanonisk 20 %) — konsistent med Gupta et al. (2007) for sykehusspesifikt sortiment.

#### Styrker

- Enkel, transparent, bred litteraturstøtte.
- Direkte tolkbart (verdiandel).
- Robust mot småfeil i enkeltartikler (én feil artikkel påvirker bare lokalt).

#### Svakheter

- Univariat — ignorerer variabilitet og kritikalitet.
- Avhengig av prisens nøyaktighet (D-02, D-03).
- 80/95 % er litteraturkonvensjon, ikke empirisk kalibrert for sykehussortiment.

#### Sensor-Q&A

> **Sensor:** Hvorfor 80 og 95 og ikke 70 og 90?
> **Du:** 80/95 er den klassiske Pareto-grensen fra Silaen et al. (2023), van Kampen et al. (2012) og bred ABC-litteratur. Sykehussortiment har en bredere "verdi-topp" enn industri på grunn av mange høyverdige spesialartikler — 25,7 % A-andel i mine data bekrefter dette og er konsistent med Gupta et al. (2007). Strengere grenser (70/90) ville gitt en smalere A-klasse som ikke fanget bredden i sortimentet; løsere grenser (90/99) ville utvannet styringssignalet. 80/95 er en *fortolket konvensjon*, ikke optimal terskel.
> **Coach-kommentar:** "Fortolket konvensjon" er det riktige uttrykket — ikke "feiltakelse" og ikke "presist kalibrert".

> **Sensor:** Hvis et fåtall artikler dominerer verdien, kunne du ikke bare brukt en top-N-cut?
> **Du:** Top-N (f.eks. "topp 100 artikler") er forutsetning på antall, mens Pareto er forutsetning på *kumulativ verdiandel*. ABC er normativt mer meningsfullt fordi det binder klassifiseringen til *hvor mye verdi som styres*, ikke til artikkelantall. To sortimenter med samme N kan ha helt forskjellig verdikonsentrasjon. Pareto-tilnærmingen er også koblet til den klassiske 80/20-regelen i lagerstyringslitteraturen.
> **Coach-kommentar:** Sensoren tester om du forstår *kvalitativ forskjell* mellom kvantil-cut og kumulativ-andel.

### 8.2 Avsnitt 5.2 — XYZ-modellen

#### Hva står her

XYZ-klassifisering basert på variasjonskoeffisient $\text{CV} = \sigma / \mu$ av månedlige forbruksverdier fra MSEG (BWART 201 + 647). Grenser: X < 0,5, Y i [0,5; 1,0), Z ≥ 1,0.

#### Hvorfor det står her

XYZ er det "andre øyet" på sortimentet. ABC sier *hvor mye* verdi, XYZ sier *hvor stabilt*. Kombinasjonen er det som muliggjør 9-felts kryssmatrise (AX, AY, AZ, BX, BY, BZ, CX, CY, CZ).

#### Formler

$$\text{CV}_i = \frac{\sigma_i}{\mu_i}$$

der $\sigma_i$ og $\mu_i$ beregnes over de 24 månedlige forbruksverdiene per artikkel. Nullmåneder inkluderes for artikler som tilfredsstiller minimumskravet ≥ 3 mnd. forbruk (ellers ekskluderes som MANGLER_DATA).

**Klassifiseringsregel:**
- X (stabilt) hvis $\text{CV} < 0{,}5$
- Y (moderat) hvis $0{,}5 \leq \text{CV} < 1{,}0$
- Z (uregelmessig) hvis $\text{CV} \geq 1{,}0$

#### Hvorfor MSEG (forbruk) og ikke EKPO (innkjøp)?

HVFS skal levere etter *forbruksbehov* via APL. Bestillinger kan klumpe seg administrativt uten at forbruket gjør det (f.eks. periodisk batch-innkjøp av stabilt brukt artikkel). CV på forbruk fanger den underliggende etterspørselsstabiliteten — som er det APL-modellen krever.

#### Hvorfor 3 mnd. minimumskrav?

Færre enn 3 observasjoner gir misvisende standardavvik (degenerate fordelinger der enkeltobservasjoner dominerer). 22 artikler ekskluderes som MANGLER_DATA.

#### Hvorfor inkludere nullmåneder?

Hvis en artikkel har forbruk i bare 3 av 24 måneder, vil eksklusjon av nullmåneder gi CV basert på 3 ikke-null observasjoner — det skjuler at artikkelen *ikke ble brukt* i de øvrige 21. Ved å inkludere nullmåneder fanger CV at slik sporadisk bruk gir høyere variabilitet enn jevnt forbruk over samme volum — en ønsket egenskap.

#### Sensor-Q&A

> **Sensor:** CV har en kjent svakhet ved lavt forbruksvolum. Hvordan adresserer du det?
> **Du:** Ja — for artikler med svært lavt forbruk kan enkeltutleveringer gi kunstig høy CV. Det er erkjent i kap. 8.4 som en svakhet ved metoden. Mitigeringen er todelt: (1) minimumskravet om forbruk i ≥ 3 av 24 måneder eliminerer de aller mest sporadiske, og (2) regelmotoren krever *flere* sammenfallende signaler for OVERFØR-anbefaling — en isolert CV-feil utløser sjelden alene en feilklassifisering. CV-grensene 0,5 og 1,0 er også standardverdier som er testet på industrielle sortimenter (Nowotyńska, 2013) og bekreftet i sykehuskontekst (Suryaputri et al., 2022).
> **Coach-kommentar:** "Standardverdier + redundans gjennom triangulering" er igjen riktig forsvarsstruktur.

> **Sensor:** Hva med sesongvariasjon? Vil ikke det blåse opp CV for artikler som faktisk er forutsigbare?
> **Du:** Sesongvariasjon er en kjent kilde til CV-inflasjon. For X-artikler (CV < 0,5) er sesongkomponenten typisk for liten til å bryte klassifiseringen. For grenseartikler nær X/Y- eller Y/Z-overgangen kan sesong tippe klassifiseringen. En sesongjustert CV ville krevd dekomponering (f.eks. STL-dekomponering), som ligger utenfor scopen. En 24-mnd. periode dekker imidlertid to fulle sesongsykluser, slik at sesongkomponenten ikke skaper et systematisk skjevbilde i én retning. Kap. 8.4 nevner dette i diskusjonen av COVID-aftermath som potensiell kilde til CV-forvrengning.
> **Coach-kommentar:** Sesong er et legitimt poeng — vis at du har tenkt på det og kjenner STL-dekomponering som teoretisk løsning.

### 8.3 Avsnitt 5.3 — EOQ-modellen og besparelsesformelen

#### Hva står her

EOQ er **den eneste klassiske optimeringsmodellen** i oppgaven. Wilson-formelen gir optimalt ordrekvantum $Q^*$ og optimal ordrefrekvens $f^*$. Avviksanalysen kvantifiserer $\Delta TC$ — kostnadsdifferansen mellom faktisk og optimal drift. Besparelsesformelen summerer signed $\Delta TC$ med gevinstrealiseringsfaktor $g$.

#### Hvorfor det står her

EOQ er **kvantifikasjonsmotoren**. Uten EOQ-avvik ville besparelsesestimatet vært umulig å lage. Sensor vil teste hele formelsystemet.

#### Formler — du må kunne disse fra hodet

**Wilson EOQ (optimalt ordrekvantum):**

$$Q^* = \sqrt{\frac{2 D S}{H}}$$

der $D$ = årsforbruk (enheter/år), $S = 750$ NOK = ordrekostnad per bestilling, $H = h \times \text{UNIT\_PRICE}$ = holdekostnad per enhet per år, med $h = 20\,\%$.

**Optimal ordrefrekvens:**

$$f^* = \frac{D}{Q^*} = \sqrt{\frac{D H}{2 S}}$$

**Totalkostnad ved gitt frekvens:**

$$TC(f) = f \cdot S + \frac{D}{2f} \cdot H$$

der $f \cdot S$ er årlig ordrekostnad og $D \cdot H / (2f)$ er årlig holdekostnad (lagernivå i snitt $= Q/2 = D/(2f)$).

**Relativt frekvensavvik:**

$$\text{FREQ\_AVVIK}_i = \frac{f_{\text{obs},i} - f^*_i}{f^*_i}$$

**Totalkostnadsavvik:**

$$\Delta TC_i = TC(f_{\text{obs},i}) - TC(f^*_i)$$

**Klassifisering:**
- FOR_MANGE_ORDRER hvis FREQ_AVVIK > 0,5 (dvs. $f_{\text{obs}} > 1{,}5 \cdot f^*$)
- OK hvis $-0{,}5 \leq$ FREQ_AVVIK $\leq 0{,}5$
- FOR_FÅ_ORDRER hvis FREQ_AVVIK < −0,5

**Besparelsesformel:**

$$B_{\text{HVFS}} = \sum_{i \in \text{OVERFØR} \cap \text{FOR\_MANGE\_ORDRER}} \Delta TC_i \cdot g$$

med $g \in \{0{,}50, 0{,}75, 1{,}00\}$.

#### Utledning av $f^*$ for sensor

Hvis sensor sier "vis meg at $f^* = \sqrt{DH/(2S)}$":

1. Start med $TC(f) = fS + DH/(2f)$.
2. Deriver med hensyn til $f$: $\frac{dTC}{df} = S - \frac{DH}{2f^2}$.
3. Sett lik null for minimum: $S = \frac{DH}{2f^{*2}} \Rightarrow f^{*2} = \frac{DH}{2S}$.
4. Trekk kvadratrot: $f^* = \sqrt{\frac{DH}{2S}}$. **QED.**

Pugg disse fire trinnene. Det er den eneste utledningen sensor sannsynligvis ber om.

#### Hvorfor frekvens fremfor partistørrelse?

Ved overføring til HVFS er det **bestillingsfrekvensen** som endres operasjonelt. NorEngros planlegger plukk- og leveringsrytmer per uke/måned. Partistørrelsen ($Q$) er en *konsekvens* av frekvensen, ikke en handlingsvariabel. Derfor er FREQ_AVVIK den operasjonelt relevante metrikken.

#### Hvorfor terskel $\tau_f = 1{,}5$ (= 50 % avvik)?

EOQ-kostnadskurven er **flat nær optimum** — små avvik gir små besparelser. $\tau_f = 1{,}5$ skiller *operasjonelt vesentlige* avvik fra *statistisk merkbare*. Verdien er forfatterens skjønnsbeslutning, eksplisitt testet i sensitivitetsanalysen ($\tau_f \in \{1{,}25; 1{,}50; 2{,}00\}$).

#### Hvorfor $g$ (gevinstrealiseringsgrad)?

$g$ skiller **teoretisk optimum** fra **forventet realisering**. Implementeringsfriksjon, leverandørforhandlinger og SAP MM-omkalibrering absorberer en andel av den teoretiske besparelsen. Tre scenarier (50/75/100 %) gjør usikkerheten eksplisitt fremfor å skjule den i et punktestimat.

#### Sensor-Q&A

> **Sensor:** Hvordan finner du $f^*$ matematisk?
> **Du:** Jeg starter med totalkostnaden $TC(f) = fS + DH/(2f)$. Den deriveres med hensyn til $f$: $dTC/df = S - DH/(2f^2)$. Sett deriverte lik null: $S = DH/(2f^{*2})$, som gir $f^{*2} = DH/(2S)$ og dermed $f^* = \sqrt{DH/(2S)}$. Den andre deriverte er positiv, så det er et minimum. Den optimale frekvensen er altså den der marginal ordrekostnad er lik marginal holdekostnad.
> **Coach-kommentar:** Sensor straffer hvis du sier "Wilson-formel" uten å vise utledningen. Pugg de fire trinnene.

> **Sensor:** Er ikke EOQ-modellen utdatert i moderne JIT-miljøer?
> **Du:** EOQ er en stilisert modell — den forutsetter konstant etterspørsel og ignorerer JIT, kvantumsrabatter og leveringsvariabilitet. Den brukes her ikke som *bestillingsoptimerer*, men som *avviksindikator*: forholdet mellom faktisk og optimal frekvens fungerer som signal for ineffektiv bestillingspraksis. Selv om absoluttverdien av $f^*$ er en forenkling, gir rangeringen av artikler etter $\Delta TC$ et reproduserbart styringssignal. Hautaniemi & Pirttilä (1999) påpeker at EOQ er mest pålitelig for artikler med lav variabilitet, noe som understøtter valget om å bruke X-artikler som primær EOQ-populasjon.
> **Coach-kommentar:** Du bruker EOQ som *signal*, ikke som *resept*. Det er nøkkeldistinksjonen.

> **Sensor:** Hvorfor er $\tau_f = 1{,}5$ og ikke 1,0 (perfekt optimum)?
> **Du:** Fordi EOQ-kostnadskurven er flat nær optimum — frekvensavvik på 10–20 % gir tilnærmet null kostnadsdifferanse. $\tau_f = 1{,}5$ er en operasjonell skjønnsbeslutning: artiklene med $f_{\text{obs}} > 1{,}5 \cdot f^*$ representerer der overbestillingen er vesentlig nok til at sentralisering kan gi reell gevinst. Verdien er testet i sensitivitetsanalysen over {1,25, 1,50, 2,00}, og konklusjonen er robust over alle tre.
> **Coach-kommentar:** Sensor liker "kostnadskurven er flat nær optimum" — det viser at du forstår funksjonens form.

> **Sensor:** Hvorfor symmetrisk $\pm 50\,\%$? Underbestilling er en helt annen risiko enn overbestilling.
> **Du:** Korrekt — FOR_FÅ_ORDRER (FREQ_AVVIK < −0,5) og FOR_MANGE_ORDRER (FREQ_AVVIK > 0,5) representerer asymmetriske risikoer. FOR_FÅ_ORDRER signaliserer potensielle stockout-problemer, mens FOR_MANGE_ORDRER er overbestilling. Symmetrien i terskelen er for *deteksjon*, ikke for *risikovurdering*. I besparelsesformelen brukes kun FOR_MANGE_ORDRER fordi HVFS-overføring adresserer overbestilling spesifikt. FOR_FÅ_ORDRER-artiklene (31 stk) flagges for separat vurdering — disse kan ha forsyningsproblemer som krever annen handling enn sentralisering.
> **Coach-kommentar:** Sensor tester om du har tenkt på symmetri-implikasjonen. Du har det.

### 8.4 Avsnitt 5.4 — K-means klyngemodellen

#### Hva står her

K-means partisjoneringsalgoritme med tredimensjonal featurevektor:

$$\mathbf{x}_i = [z(\ln \text{CV}_i),\; z(\ln(v_i + 1)),\; z(\ln(|\Delta TC_i| + 1))]$$

K-valg via silhouette-søk i K ∈ {2..7}. K = 3 valgt. Trening/test 80/20, `random_state=42`, `n_init=50`, `max_iter=300`. K_OVERFØR identifiseres deterministisk via dobbelranking.

#### Hvorfor det står her

K-means er **trianguleringsbjelken**. Uten den ville hele oppgaven hvile på regelbaserte terskler (80/95, 0,5/1,0, $\tau_f$). K-means er datadrevet og fri for forhåndsterskler. Når regelbaserte og datadrevne signaler konvergerer (R3, R4, R5), styrkes anbefalingen.

#### Designvalg som må forsvares

| Valg | Begrunnelse |
|---|---|
| Log-transformasjon | CV, $v$ og \|ΔTC\| er høyreskjeve — uten log dominerer ekstremverdier |
| Konstantledd +1 | Hindrer $\ln(0)$ for artikler med $\Delta TC = 0$ |
| Z-score | Likestiller features med ulike enheter (CV er dimensjonsløst, $v$ i NOK, \|ΔTC\| i NOK) |
| Train/test 80/20 | Standard split; testsett evaluerer generaliserbarhet |
| `random_state=42` | Reproduserbarhet |
| Silhouette-søk K ∈ [2,7] | Datadrevet K-valg, ikke forhåndsbestemt |
| `n_init=50` | Robust mot uheldig initialisering |
| Dobbelranking K_OVERFØR | Deterministisk identifikasjon av "overføringsklyngen" |

#### Silhouette-formel

$$s_i = \frac{b_i - a_i}{\max(a_i, b_i)}$$

der $a_i$ = gjennomsnittlig intra-klyngeavstand for punkt $i$, $b_i$ = gjennomsnittlig avstand til nærmeste naboklynge. Tolkning:
- $s_i \to 1$: tydelig klyngetilhørighet
- $s_i \to 0$: overlapp mellom klynger
- $s_i < 0$: punktet ligger feil

> 0,3 = eksplorativt akseptabelt (Ketkar & Vaidya, 2014). Mine resultater: 0,383 trening, 0,368 test.

#### K_OVERFØR — deterministisk identifikasjon

$$k^* = \arg\min_k \left[ \text{rang}(\overline{\text{CV}}_k \uparrow) + \text{rang}(\overline{v}_k \downarrow) \right]$$

Klyngen med lavest gjennomsnittlig CV (stigende rang) og høyest gjennomsnittlig verdi (synkende rang) får lavest rangsum. I mine data: klynge 3 (281 artikler), CV-snitt 0,47, verdi-snitt kr 167 267.

#### Sensor-Q&A

> **Sensor:** Hvorfor log-transformerer du før z-score?
> **Du:** Rekkefølgen er kritisk. De underliggende variablene — CV, $v$ og \|ΔTC\| — er alle høyreskjeve, med lange høyre haler. Uten log-transformasjon ville K-means dominert av ekstremverdier: én artikkel med ekstremt høy verdi ville dratt klyngesenteret mot seg. Log-transformasjonen komprimerer halene og normaliserer fordelingsformen tilnærmet log-normal. Z-score etter log standardiserer skala slik at de tre features bidrar likeverdig til euklidsk distanse. Hadde jeg z-score-standardisert *uten* log, ville utliggere fortsatt dratt klyngesenteret skjevt.
> **Coach-kommentar:** "Rekkefølgen er kritisk" — start svaret med dette. Det viser at du har tenkt på operasjonsrekkefølgen, ikke bare verktøyene.

> **Sensor:** Hvor robust er K = 3-valget?
> **Du:** Silhouette-scoren for K = 2 var lavere, og for K = 4 og oppover monotont synkende. K = 3 var dermed et tydelig optimum, ikke en lokal topp. Differansen mellom trenings- og testsilhouette var bare 0,015 (0,383 vs. 0,368), som indikerer at klyngestrukturen generaliserer. Hvis silhouette hadde toppet seg ved K = 4 også, ville jeg testet begge i parallelle regelmotorer. Det gjorde det ikke — K = 3 var det entydige valget.
> **Coach-kommentar:** Sensor tester om K-valg er gjennomtenkt. "Tydelig optimum, ikke lokal topp" er nøkkeluttrykket.

> **Sensor:** Du bruker \|ΔTC\| som feature *og* i besparelsesformelen. Er ikke det sirkulært?
> **Du:** Det er en *mild* metodisk sirkularitet, og den er eksplisitt erkjent i kap. 8.2. Men matematisk er det ikke samme variabel: K-means bruker absoluttverdien $|\Delta TC|$ (signalstyrke, retning-agnostisk), mens besparelsesformelen summerer kun signed $\Delta TC$ for FOR_MANGE_ORDRER-artikler. K-means klynger på "har stort kostnadsavvik" (verdi for sentralisering); besparelsen summerer "har positivt kostnadsavvik fra overbestilling" (selve gevinsten). Konsekvensen er at K_OVERFØR-klyngen tenderer å inneholde artikler med høyt $|\Delta TC|$, men disse artiklene må *uavhengig* tilfredsstille FOR_MANGE_ORDRER for å havne i besparelsen. Sirkulariteten er begrenset, men leseren bør være oppmerksom.
> **Coach-kommentar:** Sirkularitet er den mest sofistikerte kritikken som kan komme. Du eier den ved å forklare nøyaktig hvor liten den er.

> **Sensor:** Hva er det K-means egentlig tilfører som ABC + XYZ ikke gir?
> **Du:** To ting. (1) **Frihet fra forhåndsterskler:** ABC-grensene 80/95 og XYZ-grensene 0,5/1,0 er litteraturkonvensjoner. K-means lar dataene selv definere gruppestrukturen. Hvis K-means hadde konvergert til vilt andre grupper enn ABC/XYZ, ville det utfordret litteraturtersklene. (2) **Multivariat fanger samspill** som univariate analyser ikke ser — kombinasjonen høy verdi + lav CV + høyt avvik kan ikke leses ut av separate ABC- og XYZ-resultater. At K-means og ABC/XYZ konvergerer er en *validering*, ikke en *redundans*. Sensor-simuleringen (i SENSORSIMULERING.md) merker at K-means' uavhengige bidrag er begrenset — det er en gyldig kritikk, og kompensasjonen er at konvergensen styrker tilliten til tersklene.
> **Coach-kommentar:** Eier kritikken. K-means' uavhengige bidrag er begrenset, men metodens *rolle* er triangulering — og det er metodisk gyldig.

### 8.5 Avsnitt 5.5 — Regelmotor (Tabell 7, Figur 5)

#### Hva står her

Åtte sekvensielt prioriterte regler R1–R8. Hver artikkel evalueres i nummerert rekkefølge; første regel som matcher bestemmer utfallet. Tabell 7 viser betingelse, anbefaling og logikk per regel.

#### Hvorfor det står her

Regelmotoren er **transparenslaget**. Hver anbefaling kan spores til én konkret regel og ett spesifikt signalmønster. Dette er kritisk for tillit i kliniske beslutninger — innkjøper kan auditere hvorfor en bestemt artikkel ble anbefalt overført.

#### De åtte reglene

| Regel | Betingelse | Anbefaling | Logikk | Antall |
|---|---|---|---|---|
| **R1** | XYZ = Z | BEHOLD_LOKALT | Uforutsigbart forbruk → uegnet APL | 143 |
| **R2** | ABC = C ∧ XYZ = Y | BEHOLD_LOKALT | Lav verdi + moderat variasjon → ingen sentraliseringsverdi | 114 |
| **R3** | A/B ∧ X ∧ FOR_MANGE_ORDRER | **OVERFØR_HVFS** | Sterkeste signal: høy verdi, stabilt, overbestilt | 71 |
| **R4** | A/B ∧ X ∧ K_OVERFØR | **OVERFØR_HVFS** | Høy verdi, stabilt, klyngeprofil bekrefter | 18 |
| **R5** | A/B ∧ Y ∧ K_OVERFØR | **OVERFØR_HVFS** | Høy verdi, moderat variasjon, klyngeprofil bekrefter | 56 |
| **R6** | A/B ∧ X (ellers) | VURDER_NÆRMERE | Høy verdi, stabilt, men intet ekstra signal | 160 |
| **R7** | A/B ∧ Y (ellers) | VURDER_NÆRMERE | Høy verdi, moderat variasjon, intet ekstra signal | 23 |
| **R8** | Øvrige (inkl. CX) | VURDER_NÆRMERE | Uklart signalmønster eller lav verdi | 101 |
| (MANGLER) | ABC eller XYZ mangler | MANGLER_DATA | Utilstrekkelig data | 23 |

**Totalt:** 143 + 114 + 71 + 18 + 56 + 160 + 23 + 101 + 23 = 709 ✓

**OVERFØR_HVFS:** R3 + R4 + R5 = 71 + 18 + 56 = **145**

#### Hvorfor sekvensiell prioritet?

To grunner:
1. **Strengeste-passende-regel:** En artikkel havner i kategorien som er minst aggressiv. R1 (BEHOLD) overstyrer R3 (OVERFØR) hvis begge passer — beskytter mot at høyvariable kritiske artikler havner i OVERFØR.
2. **Transparent rangering:** Sensor kan se eksakt *hvilken* regel som utløste anbefalingen. Ingen aggregert score som er ugjennomtrengelig.

#### Hvorfor R1 først?

XYZ = Z er en **frastøtingsregel**. Uforutsigbart forbruk er den sterkeste kontraindikasjonen mot sentralisering — APL-modellen forutsetter planbar etterspørsel. R1 har derfor *override*-prioritet over alt annet.

#### Hvorfor R3 er det sterkeste signalet

R3 har tre uavhengige bekreftende signaler:
- Høy verdi (ABC A/B)
- Stabilt forbruk (XYZ X)
- Dokumentert overbestilling (FOR_MANGE_ORDRER)

R3-artikler er de eneste med direkte målbart EOQ-besparelsespotensial — derfor utgjør de hoveddelen av besparelsesgrunnlaget (71 av 117).

#### Hvorfor R4/R5 svakere enn R3?

R4/R5 har **to regelbaserte signaler + ett klyngebasert**. K_OVERFØR bekrefter mønsteret datadrevet, men gir ikke et direkte EOQ-kostnadsavvik å summere. Derfor er 18 + 56 = 74 R4/R5-artikler i OVERFØR, men kun 46 av dem er i besparelsen (28 mangler FOR_MANGE_ORDRER).

#### Hvorfor 145 er konservativt

Sekvensiell logikk betyr at en artikkel havner i den **strengeste passende kategorien**. Hvis du tvilte mellom OVERFØR og VURDER, ble svaret VURDER (R6/R7). Resultat: **høy presisjon** (få falske positive), **lavere recall** (noen reelle kandidater i VURDER-bunken).

#### Sensor-Q&A

> **Sensor:** Hvorfor regelmotor og ikke en ren K-means-klassifisering?
> **Du:** Tre grunner. (1) **Triangulering:** regelbaserte og datadrevne metoder validerer hverandre. (2) **Transparens:** hver anbefaling kan spores til én spesifikk regel — kritisk for tillit i kliniske beslutninger. (3) **Reviderbarhet:** terskler i regelmotoren kan justeres uten å trene K-means på nytt. Hvis Helse Bergen ønsker strengere OVERFØR-kriterium, kan de endre regelen — modellen er ikke en black box.
> **Coach-kommentar:** Triangulering + transparens + reviderbarhet = tre nøkkelord. Pugg dem.

> **Sensor:** Er R1 for streng? Holder du ikke kandidater unna OVERFØR som kanskje burde vært der?
> **Du:** Trolig ja — R1 prioriterer presisjon over recall. Det er en bevisst konservativ design. I HVFS-kontekst er kostnaden ved feilaktig OVERFØR (forsyningssvikt for klinisk kritisk artikkel) vesentlig høyere enn kostnaden ved feilaktig BEHOLD (ingen besparelse, men ingen pasientrisiko). Hvis Helse Bergen senere ønsker å justere balansen, kan R1 modifiseres til f.eks. "XYZ = Z OG kritikalitet = Vital" når VED er operasjonalisert — men dagens design beskytter forsyningssikkerheten.
> **Coach-kommentar:** "Presisjon over recall i asymmetrisk risiko" er nøkkelfrasen. Sensor vil rose den.

> **Sensor:** Hvorfor er VURDER så stor (40 %)?
> **Du:** Det er en designkonsekvens av presisjonsprioriteten. R3 krever tre samsvarende signaler; R4/R5 krever to + klynge. Hvis bare to av tre primærsignaler matcher (A/B + X uten K_OVERFØR), sendes artikkelen til VURDER (R6) fremfor OVERFØR. Den store VURDER-kategorien er pris for høy konfidens i OVERFØR. Anbefaling 2 i kap. 9.2 spesifiserer at VURDER-gruppen må gjennomgås manuelt med innkjøpsfaglig kompetanse — det er ikke et endepunkt, det er et triage-output.
> **Coach-kommentar:** Eier de 284. De er ikke "feil" — de er en planlagt manuell triage.

> **Sensor:** Kunne du ikke heller brukt en ML-klassifikator (random forest, gradient boosting)?
> **Du:** Veiledet ML krever merkede fasitklasser — i mitt tilfelle "denne artikkelen skal til HVFS / skal beholdes lokalt". Slike merkede data finnes ikke ved Helse Bergen i dag; det er nettopp gapet jeg adresserer. Etter en pilotfase med faglige overføringsbeslutninger kan datasettet brukes som treningsdata for veiledet ML — det er foreslått som videre forskning i kap. 9.3. I dag gir regelmotoren transparent beslutningsstøtte uten å forutsette data som ikke eksisterer.
> **Coach-kommentar:** Veiledet ML-spørsmålet er klassisk. Svaret er at fasit ikke finnes — pilotfasen genererer fasiten.

#### Forsvarsformular for kap. 5

> "Modelleringen er en stafett: ABC kvantifiserer verdi, XYZ kvantifiserer stabilitet, EOQ kvantifiserer bestillingsavvik, K-means trianguler multivariat, og regelmotoren aggregerer signalene til én transparent anbefaling per artikkel. Hver formel og hvert terskelvalg er enten litteraturbasert eller eksplisitt testet i sensitivitet."

---

## 9. Kapittel 6 – Analyse (Figur 6–8, Figur 10–12)

### 9.1 Avsnitt 6.1 — ABC-analyse av 709 artikler (Figur 6)

#### Hva står her

ABC-analysen kjørt på 709 artikler. 505 har $v_i$ basert på faktisk EKPO (ABC_VALUE_SOURCE = EKPO); 204 har beregnet verdi (BEREGNET). Samlet årsverdi ~34 millioner NOK. Resultatfordelingen er presentert i Tabell 8 (kap. 7).

#### Hvorfor det står her

Kap. 6 er **utførelsesloggen**. Den dokumenterer at modellene fra kap. 5 faktisk ble kjørt, med hvilke filtre og hvilket grunnlag. Figur 6 viser Pareto-kurven visuelt.

#### Figur 6 — lesetolkning

Pareto-kurven viser artikler langs x-aksen sortert synkende etter $v_i$, og kumulativ verdiandel på y-aksen. Grenselinjene ved 80 % og 95 % danner A/B- og B/C-overgangene. Kurvens karakteristiske form — bratt stigning tidlig, lang flat hale — bekrefter Pareto-mønsteret.

#### Sensor-Q&A

> **Sensor:** Du sier samlet årsverdi er ~34 millioner. Hvordan har du beregnet det?
> **Du:** Summen er $V_{\text{tot}} = \sum_{i=1}^{709} v_i$, der hver $v_i = D_i \times \text{UNIT\_PRICE}_i$. For 505 artikler er $v_i$ direkte fra EKPO NETWR aggregert over 24 mnd. og annualisert; for 204 er det beregnet fra MSEG-forbruksvolum × STPRS/PEINH. Tallet 34 millioner er det operative aktivitetsvolumet ved LGORT 3001 — det er den totale årlige verdistrømmen lageret håndterer, ikke balanseverdien av beholdningen.
> **Coach-kommentar:** "Aktivitetsvolum, ikke balanseverdi" — den distinksjonen viser at du forstår ABC-grunnlaget.

### 9.2 Avsnitt 6.2 — XYZ-klassifisering (Figur 7)

#### Hva står her

CV beregnet for 687 av 709 artikler (22 ekskludert som MANGLER_DATA pga. < 3 mnd. forbruk). CV-grenser anvendt: X < 0,5, Y i [0,5; 1,0), Z ≥ 1,0. Resultater i Tabell 9. ABC/XYZ-kryssvalidering visualisert i Figur 7.

#### Figur 7 — lesetolkning

9-felts ABC/XYZ-matrise med antall artikler per celle. A og B er konsentrert i X-kolonnen (stabilt forbruk), mens Z-kolonnen er dominert av C-artikler. AZ- og BZ-cellene er små.

#### Hvorfor er denne matrisen sentral?

Den er **inngangsdataene til regelmotoren**. R1 (Z = BEHOLD) tar Z-kolonnen ut. R2 (CY = BEHOLD) tar CY-cellen. R3 (A/B + X) ser på AX, BX-cellene. R4/R5 (A/B + X eller Y med K_OVERFØR) ser på AX, BX, AY, BY.

#### Sensor-Q&A

> **Sensor:** Hvor mange artikler havner i hver celle?
> **Du:** Det vises i Figur 7 (kryssmatrisen). Du har Tabell 9 (univariat XYZ) og Tabell 14 (per regel). Konkret antall per celle hentes fra figuren — jeg har ikke memorert hver celle, men hovedkonsentrasjonen er A/B i X-kolonnen og C-overrepresentasjon i Z. Den faktiske AX-cellen ligger rundt 130 artikler (estimat fra figur).
> **Coach-kommentar:** Hvis du ikke husker eksakte tall per celle: si "det vises i Figur 7". Sensor godtar henvisning til figuren.

> **Sensor:** Hvorfor er det 22 MANGLER_DATA i XYZ men 23 i regelmotoren?
> **Du:** XYZ ekskluderer 22 artikler pga. for kort forbrukshistorikk (< 3 mnd.). Regelmotoren ekskluderer 23 totalt — én ekstra artikkel manglet ABC-klassifisering pga. manglende verdidata (de 5 ikke-klassifiserte i ABC ble fanget av andre regler eller hadde XYZ-klasse). De to tallene gjelder forskjellige punkter i pipelinen, og 22 + 1 = 23 er det totale antallet artikler som regelmotoren ikke kan klassifisere fra rådata.
> **Coach-kommentar:** Detaljforskjell som sensor kan teste. Forklar at det er kumulativ effekt av to filtre på forskjellige nivåer.

### 9.3 Avsnitt 6.3 — EOQ-avviksberegning (Figur 8)

#### Hva står her

EOQ-avviksanalysen kjørt på 487 artikler (de med $D > 0$, UNIT_PRICE > 0 og tilgjengelig LEAD_TIME). $f^*$ beregnet med $S = 750$, $H = 0{,}20 \times \text{UNIT\_PRICE}$. $f_{\text{obs}}$ fra EKBE annualisert via D-08. FREQ_AVVIK og $\Delta TC$ beregnet per artikkel. Resultater i Tabell 11.

#### Figur 8 — lesetolkning

Histogram av FREQ_AVVIK med vertikal terskellinje ved 0,5 (= $\tau_f = 1{,}5$). Fordelingen er sterkt høyreskjev — majoriteten av artiklene har FREQ_AVVIK > 0,5 (FOR_MANGE_ORDRER).

#### Sensor-Q&A

> **Sensor:** Hvorfor 487 og ikke 709?
> **Du:** EOQ-formelen krever positiv etterspørsel $D$ og positiv enhetspris UNIT_PRICE. Artikler uten registrert forbruk eller uten standardpris kan ikke beregnes. I tillegg krever splittinga til train/test for K-means at $\Delta TC$ er definert, og artikler med $\Delta TC = 0$ (perfekt EOQ-samsvar) er sjeldne men gir teknisk degenerate features. 487 er det filtrerte settet som har komplett data for både EOQ og K-means. De resterende 222 (709 − 487) inngår i ABC/XYZ men ikke i EOQ-avviksanalysen.
> **Coach-kommentar:** Sensor tester filterforståelse. 709 → 487 er ikke vilkårlig — det er datakrav.

### 9.4 Avsnitt 6.4 — K-means klyngeanalyse (Figur 9–11)

#### Hva står her

Featurevektor konstruert for 487 artikler. Train/test 80/20 → 389/98. StandardScaler tilpasset *kun* til trening. KMeans trent for K ∈ {2..7} med `n_init=50`. Silhouette beregnet. K = 3 valgt. Klyngeprofiler beregnet og K_OVERFØR identifisert.

#### Figur 9 — Silhouette over K

Silhouette-score plot for K = 2, 3, 4, 5, 6, 7. K = 3 ga høyest score (0,383). For K ≥ 4 monotont synkende. Indikerer at tre klynger er den naturlige strukturen i featurerommet.

#### Figur 10 — Klyngeplot

Scatter-plot av artikler langs z(ln CV) og z(ln verdi), fargelagt etter klynge. K_OVERFØR-klyngen markert med stjerne (★). Klyngene er rimelig separert; K_OVERFØR (grønn) er den øverste-venstre-klyngen i diagrammet (høy verdi, lav CV).

#### Figur 11 — Klyngeprofiler (line chart)

Gjennomsnittlig z-score per feature per klynge. K_OVERFØR-klyngen kjennetegnes av lav CV-z, høy verdi-z, høy \|ΔTC\|-z. De øvrige klyngene har komplementære profiler.

#### Sensor-Q&A

> **Sensor:** Hvorfor 80/20-split?
> **Du:** 80/20 er standardpraksis for å balansere treningsmengde og holdout-evaluering. For K-means uten formell prediksjon (det er uovervåket læring) tjener splittet primært som *generaliseringsevaluering* via silhouette på testsett. Differansen mellom trenings- og testsilhouette (0,015) viser at klyngestrukturen er stabil og ikke overtilpasset.
> **Coach-kommentar:** "Generaliseringsevaluering, ikke prediksjon" — viktig for K-means siden det er unsupervised.

> **Sensor:** Hvorfor `n_init=50`?
> **Du:** K-means er sensitiv mot initialisering — ulike startposisjoner for sentroidene kan gi forskjellige lokale minima. `n_init=50` kjører algoritmen 50 ganger med forskjellige random seeds og returnerer beste løsning (lavest inertia). Det reduserer risikoen for at resultatet er en uheldig lokal minimum. Default i scikit-learn er 10; jeg valgte 50 for ekstra robusthet i lys av at klyngestrukturen er moderat (silhouette 0,38).
> **Coach-kommentar:** Sensor liker at du forstår at `n_init` er om initialiseringsrobusthet, ikke om hyperparameter-tuning.

### 9.5 Avsnitt 6.5 — Regelmotor og HVFS-scoring (Figur 12)

#### Hva står her

Regelmotoren kjørt sekvensielt på alle 709 artikler. Hver artikkel evaluert mot R1–R8 i rekkefølge; første treff bestemmer utfall. For OVERFØR-artikler er $\Delta TC_i \cdot g$ beregnet for $g \in \{0{,}5; 0{,}75; 1{,}0\}$. 27-scenarios sensitivitet kjørt med variasjon i $S$, $h$, $\tau_f$.

#### Figur 12 — Regelmotor + Besparelse

To-panels figur: venstre viser fordeling av anbefalinger (145/257/284/23), høyre viser estimert besparelse for de tre scenariene (kr 301k/452k/602k).

#### Forsvarsformular for kap. 6

> "Kap. 6 er utførelsesloggen: 709 artikler kjørt gjennom ABC, 687 gjennom XYZ, 487 gjennom EOQ og K-means, alle 709 gjennom regelmotoren. Hver figur viser ett konkret analysetrinn med dokumenterbare data."

---

## 10. Kapittel 7 – Resultater (Tabell 8–15)

### 10.1 Avsnitt 7.1 — ABC-resultater (Tabell 8)

#### Tabell 8 — A: 182 (25,7 %), B: 184 (26,0 %), C: 338 (47,7 %), ikke klassifisert: 5

**Hovedfunn:** A- og B-klassene utgjør 51,6 % av artiklene og ~95 % av verdien. A-klassens 25,7 % er noe høyere enn kanonisk 20 %, konsistent med sykehussortiment (Gupta et al., 2007).

#### Sensor-Q&A

> **Sensor:** Du sier A-klassen er "noe høyere enn kanonisk 20 %". Er ikke det et brudd på Pareto?
> **Du:** Nei — Pareto-prinsippet sier at *en liten andel artikler står for stor andel verdi*, ikke at andelen er eksakt 20 %. 25,7 % er fortsatt langt under 50 %, og det er gyldig Pareto-konsentrasjon. Gupta et al. (2007) dokumenterer i militærmedisinsk sykehuskontekst at A-andelen typisk er bredere (25–30 %) fordi sykehus har mange høyverdige spesialartikler — kirurgisk forbruksmateriell, kateteriseringsutstyr, etc. Mitt funn er konsistent med deres.
> **Coach-kommentar:** "Pareto er ikke 80/20-loven, det er konsentrasjonsobservasjon" — pugg den distinksjonen.

> **Sensor:** Hvorfor 5 ikke klassifisert?
> **Du:** Disse 5 artiklene mangler enten UNIT_PRICE eller D_ANNUAL i kildedata — uten begge kan ikke $v_i$ beregnes, og dermed ikke kumulativ andel. Å inkludere dem ville krevd antagelser om manglende verdier som ville forvrengt rangeringen for de øvrige 704. Eksklusjonen er pragmatisk og dokumentert; de 5 inngår i MANGLER_DATA-kategorien i regelmotoren.
> **Coach-kommentar:** Konsistens er nøkkelen — 5 ikke klassifisert i ABC + 22 i XYZ → 23 (med overlapp på 4) i regelmotor MANGLER.

### 10.2 Avsnitt 7.2 — XYZ-resultater (Tabell 9, 10)

#### Tabell 9 — X: 350 (50,9 %), Y: 193 (28,1 %), Z: 144 (20,9 %), ikke klassifisert: 22

#### Tabell 10 — ZZXYZ-kryssvalidering

| SAP \ Beregnet | X | Y | Z | Sum |
|---|---|---|---|---|
| SAP X | **94** | 65 | 59 | 218 |
| SAP Y | 99 | **31** | 20 | 150 |
| SAP Z | 6 | 1 | **0** | 7 |
| **Total samsvar** | | | | **125 / 375 (33 %)** |

**Hovedfunn:** SAP klassifiserer kun 7 artikler som Z, mens analysen finner 79. ZZXYZ er systematisk underrapportert.

#### Hvorfor 33 % samsvar?

Tre forklaringer (rapporten gir alle tre):
1. ZZXYZ oppdateres via MRP-kjøring som kan bruke andre CV-terskler.
2. Beregningsperioden for ZZXYZ samsvarer ikke nødvendigvis med 2024–2025.
3. ZZXYZ oppdateres kun for artikler med aktiv MRP-kjøring.

Det rå 33 %-tallet overestimerer SAPs reelle nytte fordi SAP tildeler X til 218 av 375 (58 %). En sjanse-justert Cohen's kappa ville gitt enda lavere reell enighet.

#### Sensor-Q&A

> **Sensor:** Hvor stort er 33 %-funnet egentlig? Kunne SAP-feltet ikke bare være nyttig som "ja, dette har vært sjekket"?
> **Du:** Nei — funnet er at SAP-feltet er *systematisk feil*, ikke bare "noe utdatert". Kjernen er Z-kolonnen: 6 artikler stemmer X-X-X i en triviell trygg sone, men *ingen* Z-Z-stemming. SAP fanger ikke en eneste av de 79 reelt uregelmessige artiklene. Det er kritisk fordi disse er nettopp artiklene som *ikke* skal sentraliseres. Hvis Helse Bergen brukte ZZXYZ til å avgjøre HVFS-overføring, ville de overført artikler med uforutsigbart forbruk og potensielt klinisk kritikalitet. Funnet er ikke "datafelt er litt rustent" — det er "datafelt er upålitelig for beslutningsbruk".
> **Coach-kommentar:** "0 av 79 Z-Z-treff" er det enkelttallet sensor vil huske. Bruk det.

> **Sensor:** Burde Helse Bergen ikke heller fikse ZZXYZ-feltet enn å bygge ny analyse?
> **Du:** Begge deler trengs. Mitt funn motiverer at ZZXYZ-feltet må rekalkuleres og oppdateres regelmessig — det er anbefaling 3 i kap. 9.2. Men selv et rett ZZXYZ-felt ville ikke besvare HVFS-spørsmålet alene, fordi XYZ bare er én dimensjon. Studien gir både *diagnose* (ZZXYZ er ødelagt) og *behandling* (et multimetode-rammeverk). De er komplementære: kort sikt = bruk rammeverket, lang sikt = fiks SAP-vedlikeholdet.
> **Coach-kommentar:** "Diagnose + behandling" — fin metafor for to bidragstyper.

### 10.3 Avsnitt 7.3 — EOQ-avviksresultater (Tabell 11)

#### Tabell 11

| Status | Betingelse | Antall | Andel |
|---|---|---|---|
| FOR_MANGE_ORDRER | FREQ_AVVIK > 0,5 | 356 | 73,1 % |
| OK | $-0{,}5 \leq$ FREQ_AVVIK $\leq 0{,}5$ | 100 | 20,5 % |
| FOR_FÅ_ORDRER | FREQ_AVVIK < $-0{,}5$ | 31 | 6,4 % |
| **Totalt** | | **487** | **100 %** |
| **Samlet $\sum \Delta TC$ (alle 487)** | | **kr 2 333 441/år** | |

**Hovedfunn:** 73,1 % av artiklene bestilles vesentlig oftere enn EOQ tilsier.

#### Hvorfor er 73 % FOR_MANGE_ORDRER ikke "feil"?

Det kan reflektere:
- Lagringsbegrensninger (manglende plass for store batch)
- Forsyningssikkerhetspolitikk (foretrekker mange små leveranser)
- Leverandørrutiner (faste ukentlige leveringer uavhengig av behov)

Men det indikerer **strukturell overbestilling** som HVFS-sentralisering via APL kan adressere.

#### Sensor-Q&A

> **Sensor:** Hvis 73 % bestilles for ofte, hvorfor er bare 145 anbefalt OVERFØR?
> **Du:** FOR_MANGE_ORDRER er nødvendig men ikke tilstrekkelig for OVERFØR. Av de 356 FOR_MANGE_ORDRER-artiklene må de også oppfylle ABC = A/B og XYZ = X (for R3) — eller A/B + X/Y + K_OVERFØR (for R4/R5). Mange FOR_MANGE-artikler er C-klasse (lav verdi) eller Z-klasse (uforutsigbart), og de havner i BEHOLD eller VURDER selv om de er overbestilt. Regelmotoren krever konvergens av flere signaler, ikke bare ett.
> **Coach-kommentar:** Sensor tester triangulering. Svaret er "et signal er ikke nok".

> **Sensor:** $\sum \Delta TC = 2{,}3$ millioner — er ikke det det egentlige besparelsespotensialet?
> **Du:** Nei. $\sum \Delta TC = 2{,}3$ millioner er det **totale teoretiske kostnadsoverskuddet** for alle 487 EOQ-analyserte artikler. Besparelsen er begrenset til de artiklene som faktisk *overføres* — 117 i skjæringspunktet OVERFØR ∩ FOR_MANGE_ORDRER. Disse 117 utgjør kr 602 020 ($g = 100\,\%$). Resten av de 487 artiklene har avvik som *ikke adresseres* av HVFS-overføring fordi de tilhører BEHOLD eller VURDER. 2,3 millioner er hva det totale ineffektivitetspotensialet i ordrepraksisen er; 0,6 millioner (best case) er hva HVFS-overføringen kan høste.
> **Coach-kommentar:** Sensor leter etter at du forstår skillet teoretisk potensial vs. realiserbar gevinst. 2,3M vs. 0,6M er den nøkkeldistinksjonen.

### 10.4 Avsnitt 7.4 — K-means klyngeresultater (Tabell 12)

#### Tabell 12

| Klynge | n | CV snitt | Verdi snitt (kr) | \|ΔTC\| snitt (kr) | Profil |
|---|---|---|---|---|---|
| 1 | 31 | 1,05 | 150 | 4 999 | Lav verdi, høy variasjon |
| 2 | 175 | 1,59 | 79 658 | 1 199 | Middels verdi, svært variabelt |
| **3 (K_OVERFØR)** | **281** | **0,47** | **167 267** | **7 005** | **Høy verdi, stabilt, høyt avvik** |

**Silhouette:** 0,383 trening / 0,368 test (begge > 0,3-terskel).

#### Hvorfor identifiseres klynge 3 som K_OVERFØR?

Klynge 3 vinner dobbelranking: lavest CV-snitt (0,47, rang 1 stigende) + høyest verdi-snitt (kr 167 267, rang 1 synkende) = rangsum 2. Klynge 1: CV 1,05 (rang 2) + verdi 150 (rang 3) = 5. Klynge 2: CV 1,59 (rang 3) + verdi 79 658 (rang 2) = 5. Klynge 3 har laveste rangsum og er K_OVERFØR.

#### Sensor-Q&A

> **Sensor:** Klynge 3 har 281 artikler, men bare 74 av dem havner i OVERFØR. Hvorfor det avviket?
> **Du:** Av de 281 må artikkelen *også* tilfredsstille R4 (A/B + X + K_OVERFØR) eller R5 (A/B + Y + K_OVERFØR). Mange av de 281 er C-artikler (R1 eller R2 overstyrer) eller Z-klasse (R1 overstyrer). K_OVERFØR-tilhørighet alene utløser ikke OVERFØR — det er et *bekreftende* signal som krever ABC + XYZ-kontekst. Det er konsistent med trianguleringslogikken: K-means alene er ikke nok.
> **Coach-kommentar:** "Bekreftende signal, ikke tilstrekkelig signal" — pugg den frasen.

> **Sensor:** Klynge 2 har 175 artikler med høy CV (1,59) men middels verdi. Hva er de?
> **Du:** Profilen passer artikler med uregelmessig forbruksmønster men ikke ubetydelig verdi — typisk Y- eller Z-klasse med moderat ABC-rangering. Disse er kandidater for BEHOLD_LOKALT pga. R1 (Z-override) eller R2 (CY) eller VURDER (R6/R7/R8). De er en stor gruppe fordi sykehussortiment har mange artikler som er moderat dyre og brukes sporadisk — instrumenter, spesialbandasjer, irregulært prosedyrebehov.
> **Coach-kommentar:** Sensor tester klyngetolkning. Knytt klyngeprofil til klinisk eksempel for å vise domeneforståelse.

### 10.5 Avsnitt 7.5 — Regelmotor og HVFS-anbefalinger (Tabell 13, 14)

#### Tabell 13 — Hovedfordeling

| Kategori | Antall | Andel |
|---|---|---|
| OVERFØR_HVFS | 145 | 20,5 % |
| BEHOLD_LOKALT | 257 | 36,2 % |
| VURDER_NÆRMERE | 284 | 40,1 % |
| MANGLER_DATA | 23 | 3,2 % |
| **Totalt** | **709** | **100 %** |

#### Tabell 14 — Regelfordeling

Allerede gjennomgått i kap. 5. R1: 143, R2: 114, R3: 71, R4: 18, R5: 56, R6: 160, R7: 23, R8: 101, MANGLER: 23.

#### Triage-anbefaling for VURDER-gruppen

Rapportens kap. 7.5 gir en prioritert tilnærming for de 284 VURDER-artiklene:
1. Start med R8 (101 art.) — CX-profil: stabilt forbruk, lav verdi. Disse kan ofte overføres med begrenset risiko.
2. Deretter R6 (160 art.) — A/B + X uten K_OVERFØR.
3. Til slutt R7 (23 art.) — A/B + Y uten K_OVERFØR.

#### Sensor-Q&A

> **Sensor:** R1 fanger 143 Z-artikler. Men du sa det var 144 Z-klassifiserte i Tabell 9. Hvor ble den siste av?
> **Du:** Diskrepansen kommer fra at én Z-klassifisert artikkel mangler tilstrekkelig data til å fanges av R1 (typisk manglende ABC eller fullstendig forbrukshistorikk). Den havner i MANGLER_DATA. Forskjellen mellom 144 (XYZ) og 143 (R1) er den indikatoren.
> **Coach-kommentar:** Sensor tester aritmetisk konsistens. Vær forberedt på at total-tabeller stemmer.

> **Sensor:** Hvorfor sender du 160 artikler til VURDER (R6) i stedet for å overføre dem? De har jo A/B + X.
> **Du:** R6 fanger A/B + X-artikler som *mangler* både FOR_MANGE_ORDRER- og K_OVERFØR-signal. De har høy verdi og stabilt forbruk, men hverken EOQ-avvik eller K-means-bekreftelse. Etter trianguleringslogikken er to av tre primærsignaler ikke tilstrekkelig for automatisk OVERFØR — derfor sendes de til manuell vurdering. Innkjøper kan etter kvalitativ gjennomgang konvertere mange av disse til OVERFØR; men automatisert overføring krever konvergens.
> **Coach-kommentar:** "To av tre signaler er ikke nok" — det er den konservative designen. Eier den.

### 10.6 Avsnitt 7.6 — Besparelse og sensitivitet (Tabell 15)

#### Tabell 15

| Scenario | $g$ | Besparelse (kr/år) |
|---|---|---|
| Worst case | 50 % | 301 010 |
| **Base case** | **75 %** | **451 515** |
| Best case | 100 % | 602 020 |

Beregnet på 117 artikler (OVERFØR ∩ FOR_MANGE_ORDRER), $S = 750$.

#### Sensitivitetsanalyse — 27 scenarier

- $S \in \{500, 750, 1000\}$
- $h \in \{15\,\%, 20\,\%, 25\,\%\}$
- $\tau_f \in \{1{,}25; 1{,}50; 2{,}00\}$
- $3 \times 3 \times 3 = 27$ kombinasjoner

**Total $\sum \Delta TC$ (alle 487):** varierer fra kr 1 602 464 til kr 3 068 757.
**$B_{HVFS}$ ($g = 75\,\%$):** varierer fra **kr 176 374 til kr 763 903 per år**.

#### Dominante usikkerhetsfaktorer

| Parameter | Effekt | Forklaring |
|---|---|---|
| $S$ | **Lineær** (sterkest) | Dobling fra 500 → 1000 nær dobler $\Delta TC$ |
| $h$ | Moderat | Holdekostnad endrer balansen mellom hold og ordre |
| $\tau_f$ | Antallsdrivende | Lavere terskel → flere kandidater, men mindre $\Delta TC$ per |

**Robusthet:** Alle 27 scenarier gir **positiv** besparelse. Konklusjonen om at HVFS-overføring er økonomisk rasjonell holder under all rimelig parameterusikkerhet.

#### Sensor-Q&A

> **Sensor:** Hvilken parameter er viktigst for besparelsen?
> **Du:** Ordrekostnaden $S$ — den inngår lineært i ordrekostnaden $fS$ i totalkostnadsformelen og dermed lineært i $\Delta TC$. En dobling fra 500 til 1000 NOK nær dobler estimert besparelse. Holdesatsen $h$ har moderat effekt. Frekvensterskelen $\tau_f$ påvirker primært *antallet* artikler som klassifiseres som FOR_MANGE_ORDRER, ikke per-artikkel-$\Delta TC$. Lavest besparelse (kr 176k) inntreffer ved $S = 500$, $h = 15\,\%$, $\tau_f = 2{,}00$ (færre artikler kvalifiserer). Høyest (kr 764k) ved $S = 1000$, $h = 25\,\%$, $\tau_f = 1{,}25$ (flere artikler + større $\Delta TC$ per).
> **Coach-kommentar:** Sensitivitets-hierarkiet S → h → $\tau_f$ er det sensor vil ha. Pugg rekkefølgen.

> **Sensor:** Hvis sensitivitetsintervallet er kr 176k–764k, hvor "ekte" er da base case kr 451 515?
> **Du:** Base case er en *strukturert ekspertvurdering*, ikke en empirisk fastslått verdi. Den representerer det mest sannsynlige estimatet gitt midtverdier i alle tre parametre ($S = 750$, $h = 20\,\%$, $\tau_f = 1{,}50$) og en gevinstrealisering på 75 %. Det metodisk korrekte svaret på "hva er besparelsen" er ikke ett tall, men **intervallet** kr 176k–764k med base case 451 515 som forventet midtverdi. Tallet er nyttig som beslutningsstøtte, ikke som prognose.
> **Coach-kommentar:** "Strukturert ekspertvurdering, ikke prognose" — bruk det presise språket. Sensor straffer hvis du selger base case som "svaret".

#### Forsvarsformular for kap. 7

> "Resultatene er det operasjonelle outputet: 145 OVERFØR-kandidater fordelt på R3/R4/R5, 117 i besparelsesgrunnlag, kr 451 515 base case og intervall kr 176k–764k under 27 parametervariasjoner. ZZXYZ-funnet (33 % samsvar) er et selvstendig empirisk bidrag."

---

## 11. Kapittel 8 – Diskusjon (her vinner du eller taper du)

Diskusjonen er **sensorens lakmustest**. Hen leter etter:
- Erkjenner du svakhetene eksplisitt?
- Kobler du funn til litteraturen?
- Forstår du grensene for konklusjonen din?

### 11.1 Avsnitt 8.1 — Funn opp mot litteraturen (Tabell 16)

#### Hva står her

Hvert sentralt funn sammenlignes med forventet litteraturresultat. Tabell 16 lister åtte funn med "Konsistens med litteratur"-status (Ja / Delvis).

#### Tabell 16 — Hovedfunn vs. litteratur

| Funn | Eget | Litteratur | Status |
|---|---|---|---|
| A-klasse andel | 25,7 % | 20–25 % (Gupta) | Ja |
| ZZXYZ-samsvar | 33 % | Statisk klassif. divergerer (van Kampen) | Ja |
| X-andel | 50,9 % | Stabile artikler flertallet (Nowotyńska) | Ja |
| K-means silhouette | 0,38/0,37 | > 0,3 akseptabelt (Ketkar & Vaidya) | Ja |
| Besparelse base | kr 452k/år | Moderate gevinster (Moons) | Ja |
| FOR_MANGE_ORDRER | 73,1 % | Suboptimal bestilling utbredt (Volland) | Ja |
| ABC/XYZ-matrise | 9-felt | Økt segmenteringsverdi (Suryaputri) | Ja |
| K-means merverdi | Bekrefter ABC/XYZ | Klyngeanalyse ofte bekreftende (Srinivasan & Moon) | **Delvis** |

#### Hvorfor "Delvis" på K-means?

K-means' uavhengige bidrag er **moderat**. Den bekrefter ABC/XYZ-aksen fremfor å avdekke et uavhengig mønster. Dette er erkjent eksplisitt og kompenseres av at konvergensen mellom regelbasert og datadrevet metode er et **validitetsargument**, ikke en redundans.

#### Sensor-Q&A

> **Sensor:** Hvor mye nytt bringer K-means egentlig?
> **Du:** Datamessig: lite uavhengig informasjon. K-means konvergerer mot samme akse som ABC/XYZ definerer. Metodisk: tre bidrag. (1) **Validering av terskler** — at K-means finner samme struktur uten forhåndsterskler, bekrefter at 80/95 og 0,5/1,0 ikke er vilkårlige. (2) **Multivariat dekning** — K-means håndterer samspill mellom tre features samtidig. (3) **Eksplorativ åpning** — fremtidige analyser med utvidet featurevektor (VED, leveringstid) vil gi K-means en mer selvstendig rolle. SENSORSIMULERING merker dette som svakhet, og jeg eier den.
> **Coach-kommentar:** Eier kritikken. Kompenser med tre konkrete bidragstyper.

### 11.2 Avsnitt 8.2 — Metodekritikk (kjerneselvkritikk)

#### Hva står her

Seks distinkte metodeproblemer adresseres eksplisitt:
1. SAP-data har høy reliabilitet (auto-registrert), men stamdata (MARA, MBEW) er manuelt vedlikeholdt og kan inneholde feil.
2. For 204 artikler er ABC basert på STPRS × forbruk (D-03) — implisitt antagelse om at standardpris ≈ faktisk pris.
3. **Ingen ekstern validering** mot innkjøpsfaglig skjønn eller historiske beslutninger.
4. EOQ forutsetter stasjonær etterspørsel; ikke testet (men X-artikler har lav variabilitet).
5. **Sirkularitet** ved \|ΔTC\| i både K-means og besparelse — erkjent, men begrenset matematisk.
6. Besparelsesmodellen er **snever** — fanger kun transaksjonskostnader, ikke lagerbinding eller transport.
7. Studien er avgrenset til WERKS 3300 — metoderammeverket overførbart, ikke tallresultater.

#### Hvorfor er ekstern validering den største svakheten?

Uten et "fasit-datasett" (kjente korrekte HVFS-beslutninger) kan vi ikke beregne **presisjon** eller **recall** for regelmotoren. Du kan ikke si "95 % av OVERFØR-anbefalingene er korrekte". Du kan bare si "regelmotoren produserer beslutningsstøtte basert på dokumentert logikk".

#### Den planlagte pilotvalideringen

Anbefaling 1 i kap. 9.2 spesifiserer at pilotfasen genererer det første fasit-datasettet. Etter piloten kan rammeverket kalibreres mot empirisk validerte beslutninger.

#### Sensor-Q&A

> **Sensor:** Hvordan kan du anbefale 145 artikler uten å vite om de er rett?
> **Du:** Anbefalingen er ikke "disse er rett" — det er "disse oppfyller eksplisitte kriterier basert på SAP-data og litteraturbaserte terskler". Det er strukturert beslutningsstøtte, ikke autoriserte beslutninger. Manglende ekstern validering er erkjent som den fremste begrensningen i kap. 8.2, og pilotfasen (anbefaling 1) er nettopp den prosessen som vil generere validerte beslutningsdata. Inntil piloten kan vi karakterisere modellen kun normativt: gitt antagelsene, dette er anbefalingen. Modellen byttes ikke ut med subjektivt skjønn — den supplerer det.
> **Coach-kommentar:** "Strukturert støtte, ikke autorisert beslutning" er kjerneformuleringen. Reciterer du den, signaliserer du at du forstår epistemisk status.

> **Sensor:** Snever besparelsesmodell — hvor mye undervurderer du faktisk?
> **Du:** Modellen fanger kun **transaksjonskostnadsavviket** fra suboptimal ordrefrekvens for 117 artikler. Den utelater tre kostnadselementer: (1) **redusert lokal lagerkapitalbinding** — Kelle et al. (2012) anslår 5–15 % av lagerverdien; (2) **transportkostnader** fra HVFS til avdeling via APL — en motpost som må kartlegges; (3) **engangskostnader** for SAP MM-konfigurering og prosessomstilling. Nettogevinsten ligger sannsynligvis høyere enn base case isolert sett, men intervallet er ikke kvantifisert i denne studien. Estimatet er **konservativt**.
> **Coach-kommentar:** "Konservativt" er nøkkelordet. Sensor vil rose at du underestimerer fremfor å overselge.

> **Sensor:** Du sier studien er reproduserbar. Hvor lett kan jeg faktisk reprodusere den?
> **Du:** Alt nødvendig er dokumentert. `LOG650_analyse_v2_7.py` med `random_state=42` produserer identiske resultater på samme MASTERFILE V1.xlsx. Bibliotekversjoner er spesifisert i Vedlegg B (pandas 2.2.2, scikit-learn 1.4.2 m.fl.). SAP-feltspesifikasjonen i Vedlegg A gjør at en annen SAP MM-konsulent kan kjøre samme SE16H-uttrekk på et hvilket som helst sammenlignbart WERKS. Datavalgsbeslutninger D-01–D-08 er listet med begrunnelse. Den eneste komponenten som ikke kan reproduseres uten Helse Bergens datatilgang, er SAP-uttrekket selv — men det er en organisatorisk tilgangsbegrensning, ikke en metodisk svakhet.
> **Coach-kommentar:** Reproduserbarhet er en av oppgavens største styrker. Vis konkret hva som gjør den reproduserbar.

### 11.3 Avsnitt 8.3 — Praktisk betydning for Helse Bergen

#### Hva står her

145 OVERFØR betyr konkret at bestillingsansvar flyttes fra Helse Bergens innkjøpsenhet til HVFS, med APL-leveranse direkte til avdeling. Dette krever endringer i SAP MM-oppsett: MRP-type, ordrekvantumsparametere, minimum ordrekvantum, avrundingsverdi. 117 FOR_MANGE_ORDRER-artikler er mest presserende.

VURDER (284) krever manuell gjennomgang med innkjøpsfaglig skjønn — de Vries (2011): kostnadsoptimalisering må balanseres mot forsyningssikkerhet.

For LIBRA: regional utrulling som mal for andre helseforetak. Periodisk reklassifisering (årlig) kan kjøres uten metodisk tilpasning.

#### Sensor-Q&A

> **Sensor:** Hva er den største praktiske utfordringen ved å implementere dette?
> **Du:** SAP MM-justering. Selv om HVFS overtar bestillingsansvaret, vil systemet fortsette å generere ordrer med eksisterende frekvens *hvis* MRP-type og kvantumsparametere ikke justeres. Det er ikke en analytisk svakhet — det er en operasjonell forutsetning som ofte undervurderes. Anbefaling 3 i kap. 9.2 adresserer dette eksplisitt. Den andre store utfordringen er klinisk validering: 284 VURDER-artikler kan ikke automatiseres, og det krever koordinert innkjøpsfaglig og klinisk gjennomgang.
> **Coach-kommentar:** SAP MM-detalj signaliserer domeneautoritet. Bruk det.

### 11.4 Avsnitt 8.4 — Svakheter og begrensninger

#### Hva står her

Avsnittet samler de viktigste svakhetene:
- $g$ er scenarioparameter, ikke empirisk prognose
- $S = 750$ ikke lokalt kalibrert
- LEAD_TIME 14 dager dekker 94 %, men ikke brukt i frekvensbasert EOQ
- COVID-aftermath kan forvrenge CV
- K-means er sensitiv mot K-valg
- 204 artikler uten EKPO har beregnet ABC-verdi
- **VED ikke operasjonalisert** — fremstilt som strukturelt valg, ikke metodefeil
- Kun K-means, ikke sammenligning med DBSCAN/hierarkisk
- Analytisk besparelsesestimat — Monte Carlo ville gitt dynamisk simulering

#### Den klassiske diskusjonsmodellen

Hver svakhet får:
1. **Hva den er** (presis beskrivelse)
2. **Hva den betyr for konklusjonen** (effektestimat)
3. **Hvordan den er mitigert** (sensitivitet, anbefaling, alternativ)
4. **Hva som ville styrket det videre** (foreslått videre forskning)

Sensor vil teste om alle fire trinn er dekket per svakhet.

#### Forsvarsformular for kap. 8

> "Diskusjonen erkjenner svakhetene eksplisitt — manglende ekstern validering, sirkularitet via \|ΔTC\|, snever besparelsesmodell, VED-mangel — og kobler hver til mitigasjon eller anbefalt videreundersøkelse. Det er metodisk korrekt og styrker rapportens troverdighet."

---

## 12. Kapittel 9 – Konklusjon

### 12.1 Avsnitt 9.1 — Svar på problemstillingen

#### Hva står her

Forskningsspørsmålet repeteres. Svar i to deler:
- **Kvalitativt:** 145 artikler identifisert, kjennetegnet av A/B + X/Y + FOR_MANGE_ORDRER eller K_OVERFØR
- **Kvantitativt:** Intervall kr 176 374 – 763 903/år, base case kr 451 515

**Selvstendig empirisk funn:** ZZXYZ-samsvar 33 % (125/375). SAP klassifiserer 7 Z, beregnet finner 79.

**Tre hovedbegrensninger eksplisitt** repetert:
1. Ingen ekstern validering
2. S, h, g ikke lokalt kalibrert
3. VED ikke operasjonalisert

#### Hvorfor strukturen "to-delt svar + bifunn + tre begrensninger"?

- Det matcher den **todelte problemstillingen** (hvilke + hva er besparelsen).
- Bifunnet (ZZXYZ) er ærlig markert som *uventet sideresultat*, ikke svar på problemstillingen.
- De tre begrensningene er deklarert *opp foran* slik at sensor ikke trenger å lete etter dem.

#### Sensor-Q&A

> **Sensor:** Du sier 145 artikler. Hva er den ene konkrete egenskapen som gjør disse til kandidater?
> **Du:** Ingen enkelt egenskap. De har alle minimum to av tre primærsignaler aktivert: ABC = A/B, XYZ = X/Y, og enten FOR_MANGE_ORDRER eller K_OVERFØR. R3-artiklene (71) har alle tre — de er de sterkeste kandidatene. R4/R5-artiklene (74) har to regelbaserte signaler + klyngebekreftelse. Det er trianguleringen som definerer kandidaten, ikke en enkelt egenskap.
> **Coach-kommentar:** "Triangulering" er den oppsummerende rammen. Bruk den til å åpne svaret.

> **Sensor:** Hvordan ville du presentert hovedfunnet ditt for ledelsen ved Helse Bergen?
> **Du:** I tre setninger: "Vi har identifisert 145 av 709 forsyningslagerartikler som prioriterte kandidater for overføring til HVFS, fordelt på tre regelkategorier med ulik signalstyrke. Det estimerte besparelsespotensialet ligger mellom kr 176 000 og kr 764 000 per år, med kr 451 515 som beste enkeltestimat. Anbefalingen er pilotvalidering av de 145 mot klinisk kritikalitet før implementering, og parallell oppdatering av SAP MM-parametere for å realisere gevinsten."
> **Coach-kommentar:** Tre setninger = tre nivåer (hva, verdt, neste steg). Pugg strukturen for muntlig presentasjon.

### 12.2 Avsnitt 9.2 — Anbefalinger til Helse Bergen

#### De fire anbefalingene (prioritert)

| # | Anbefaling | Tidsperspektiv |
|---|---|---|
| **1** | Gjennomfør klinisk kritikalitetsvurdering (VED) før pilot. Start med K_OVERFØR ∩ AX/BX som er "Desirable". | Umiddelbart, parallelt |
| **2** | Gjennomgå de 284 VURDER-artiklene manuelt — innkjøpsfaglig + klinisk skjønn. | Mellomfristig |
| **3** | Oppdater SAP MM-parametere (MRP-type, ordrekvantum, ZZXYZ-feltet) for overførte artikler. | Umiddelbart, parallelt |
| **4** | Evaluer gevinstrealisering etter 12 måneder med oppdatert datakjøring. | Langsiktig |

#### Hvorfor er VED-piloten anbefaling 1?

Fordi alle andre handlinger forutsetter klinisk validering. Hvis en Vital-artikkel inngår i de 145 OVERFØR, kan APL-leveransesvikt ha pasientkonsekvenser. Anbefaling 1 er **kvalitetsforsvarsverk** før implementering.

#### Sensor-Q&A

> **Sensor:** Hvis Helse Bergen får velge én anbefaling — hvilken er viktigst?
> **Du:** Anbefaling 1 (klinisk VED-vurdering) — uten den kan ingen artikkel forsvarlig overføres. Anbefaling 3 (SAP MM-justering) er like umiddelbar fordi gevinsten ikke realiseres uten den. De to henger sammen: VED gir *retning* (hvilke artikler), SAP MM gir *gjennomføring* (faktisk endret bestillingspraksis). Anbefaling 2 og 4 kan vente noe lengre.
> **Coach-kommentar:** Sensor tester prioritering. VED + SAP MM = parallelle umiddelbare. Det er den riktige rammen.

### 12.3 Avsnitt 9.3 — Forslag til videre forskning

#### Fire retninger

1. **ROP-modul** med faktiske leveringstider fra EINE
2. **Leverandørkonsolidering** via EKKO/EKPO-analyse
3. **Replikering** til Stavanger, Fonna, Førde
4. **Utvidet metode** — AHP/TOPSIS, kombinatoriske auksjoner, veiledet ML (etter pilotfasen)

#### Sensor-Q&A

> **Sensor:** Hvorfor er veiledet ML på "etter pilot"-listen og ikke i hovedmetoden?
> **Du:** Veiledet ML krever **merkede fasitklasser** — et datasett der HVFS-egnethet er kjent på forhånd per artikkel. Slike merkede data finnes ikke i dag; pilotfasen genererer dem. Etter pilot vil treningsdata være tilgjengelig, og et veiledet maskinlæringsoppsett kan kalibrere regelmotorens parametre eller erstatte deler av den. Det er en logisk neste fase, men forutsetter at pilotfasen genererer fasiten.
> **Coach-kommentar:** "Pilotfasen genererer fasiten" — gjenta dette uttrykket. Det er den enkleste forklaringen på at veiledet ML må komme senere.

#### Forsvarsformular for kap. 9

> "Konklusjonen besvarer problemstillingen todelt: kvalitativt med 145 identifiserte artikler og kvantitativt med kr 451 515 base case innen et sensitivitetsintervall på kr 176k–764k. Tre begrensninger er eksplisitt anerkjent, og fire anbefalinger spesifiserer de praktiske oppfølgingsstegene Helse Bergen må ta for å realisere potensialet."

---

## 12b. Referanseliste (s. 932–976 i rapporten)

### 12b.1 Hva referanselisten er

22 referanser i APA 7 (norsk stil), alfabetisk ordnet etter førsteforfatter. Hver referanse har komplett bibliografisk angivelse med DOI der det finnes. Ingen pyntereferanser — hver kilde er aktivt brukt i metodologisk eller empirisk argumentasjon.

### 12b.2 Kildekartet — de fem rollene

Pugg disse fem gruppene. Sensor vil spørre "hvorfor brukte du akkurat denne kilden", og du må kunne plassere referansen i én av rollene.

#### Gruppe 1: Kjernemetodikk (formelgrunnlaget)

| Referanse | Hva den begrunner |
|---|---|
| **Silaen et al. (2023)** | ABC-grensene 80/95 %, Pareto-prinsippet |
| **Nowotyńska (2013)** | XYZ-grensene 0,5 / 1,0 for CV |
| **Hautaniemi & Pirttilä (1999)** | EOQ-anvendelse, Wilson-modellens forutsetninger |
| **Ketkar & Vaidya (2014)** | Holdesats $h = 20\,\%$, silhouette-terskel > 0,3 |
| **Srinivasan & Moon (1999)** | K-means i SCM, klyngeanalyse for forsyningskjede |
| **Rousseeuw (1987)** | Silhouette-score-definisjonen $s = (b-a)/\max(a,b)$ |

#### Gruppe 2: Sykehuslogistikk-kontekst

| Referanse | Hva den bringer |
|---|---|
| **Bijvank & Vis (2012)** | Lost-sales-modell, $S = 750$ NOK, lager ved brukssted |
| **de Vries (2011)** | Interessentanalyse, organisatoriske barrierer mot sentralisering |
| **Fragapane et al. (2019)** | APL-leveranser, sentraliseringskrav |
| **Gupta et al. (2007)** | ABC + VED, SAP i sykehus, A-andel 25–30 % |
| **Gurumurthy et al. (2021)** | K-means i sykehuslogistikk (eneste direktekilde) |
| **Kelle et al. (2012)** | $S = 750$ NOK, farmasøytisk forsyningskjede, kapitalbinding 5–15 % |
| **Moons et al. (2019)** | Ytelsesmåling i intern sykehusforsyning |

#### Gruppe 3: Reviews / gap-identifikasjon

| Referanse | Hvor mye den dekker | Hva den brukes til |
|---|---|---|
| **Saha & Ray (2019)** | Review av 137 artikler | **Kjernen i gap-argumentet** — ERP-baserte casestudier mangler |
| **Volland et al. (2017)** | Review av 145 publikasjoner | 30–40 %-tallet for sykehuslogistikkens driftskostnadsandel |
| **van Kampen et al. (2012)** | Konseptuelt rammeverk | Tre SKU-dimensjoner: karakteristikker, teknikk, operasjonalisering |

#### Gruppe 4: Komplementær teori

| Referanse | Bidrag |
|---|---|
| **Suryaputri et al. (2022)** | ABC/XYZ-matrisens merverdi i helseindustri |
| **Pujawan (2004)** | Lot-sizing → ordrevariabilitet → bullwhip-relevans |

#### Gruppe 5: Alternativer (sitert, ikke implementert)

| Referanse | Hvorfor utelatt |
|---|---|
| **Keshavarz Ghorabaee et al. (2015)** | EDAS — krever subjektiv vekting → undergraver reproduserbarhet |
| **Partovi & Burton (1993)** | AHP for ABC — krever ekspertintervjuer → utenfor scope |

#### Gruppe 6: Teknisk / programvare

| Referanse | Hva den dokumenterer |
|---|---|
| **Pedregosa et al. (2011)** | scikit-learn (KMeans, StandardScaler, silhouette, train_test_split) |
| **McKinney (2010)** | pandas (datastrukturer) |

### 12b.3 Per-parameter-mapping (kritisk pugg)

Sensor kan stille "hvor kommer X fra?" Du må kunne svare på ett pust:

| Parameter / valg | Kilde |
|---|---|
| ABC 80 % grense | Silaen et al. (2023) |
| ABC 95 % grense | Silaen et al. (2023) |
| XYZ CV < 0,5 | Nowotyńska (2013) |
| XYZ CV ≥ 1,0 | Nowotyńska (2013) |
| $S = 750$ NOK | Bijvank & Vis (2012), Kelle et al. (2012) |
| $h = 20\,\%$ | Ketkar & Vaidya (2014) |
| Silhouette > 0,3 terskel | Ketkar & Vaidya (2014) |
| Silhouette-formelen | Rousseeuw (1987) |
| K-means n_init=50 | scikit-learn (Pedregosa et al., 2011) — egen designbeslutning |
| Wilson EOQ | Hautaniemi & Pirttilä (1999) |
| APL-egnethetskrav (stabilt forbruk) | Fragapane et al. (2019) |
| Lost-sales-modell | Bijvank & Vis (2012) |
| Lagerkapitalbinding 5–15 % | Kelle et al. (2012) |
| 30–40 % driftskostnader | Volland et al. (2017) |
| Gap-argumentet | Saha & Ray (2019) |
| Tre-dimensjonsrammeverket | van Kampen et al. (2012) |
| VED-konseptet | Gupta et al. (2007); Gurumurthy et al. (2021) |
| `random_state=42` | De facto akademisk standard — *ikke* en referanse |

### 12b.4 Sensor-Q&A for referanselisten

> **Sensor:** Kan du nevne dine tre viktigste kilder, og hvorfor de er viktige?
> **Du:** Tre kandidater. (1) **Saha & Ray (2019)** — review av 137 artikler — er kjernen i gap-argumentet: de konstaterer at empiriske ERP-baserte casestudier som kombinerer flere klassifiseringsmetoder mangler. (2) **van Kampen et al. (2012)** gir det konseptuelle SKU-rammeverket med tre dimensjoner (karakteristikker, teknikk, operasjonalisering) som mitt arbeid plasserer seg i krysningen av. (3) **Silaen et al. (2023)** og **Nowotyńska (2013)** sammen er kanonkildene for ABC- og XYZ-tersklene — de er metodologiske ankre uten hvilke jeg ikke kunne forsvart 80/95 og 0,5/1,0 grensene.
> **Coach-kommentar:** Saha & Ray er obligatorisk-svaret. De to andre kan varieres etter spørsmålet.

> **Sensor:** Hvor kommer $S = 750$ NOK fra?
> **Du:** Den er en bransjestandard som hviler på to refererte studier: **Bijvank & Vis (2012)** og **Kelle et al. (2012)**. Begge dokumenterer ordrekostnader i samme størrelsesorden for europeisk sykehuskontekst. Verdien dekker direkte administrative kostnader for å opprette, godkjenne og følge opp en SAP-ordre. Lokal kalibrering ville krevd egen aktivitetsbasert kostnadsanalyse, som ligger utenfor bachelorscopen — derfor er sensitivitetsanalysen testet over $\{500, 750, 1000\}$.
> **Coach-kommentar:** To navn, ikke ett. "Bijvank & Vis + Kelle et al." Det viser at du ikke hviler på én kilde.

> **Sensor:** 22 referanser er i nedre sjikt for bacheloroppgaver. Hvorfor ikke flere?
> **Du:** Korrekt — sensor kan typisk forvente 25–35 kilder, og bredere referansebase ville styrket litteraturgjennomgangen. Det jeg kan forsvare er at hver av de 22 brukes aktivt i argumentasjonen — ingen er pyntereferanser. Tematisk fordeler de seg i seks roller: kjernemetodikk, sykehuslogistikk-kontekst, gap-reviews, komplementær teori, sitert alternativ, og teknisk programvare. SENSORSIMULERING-vurderingen flagger dette eksplisitt som svakhet, og jeg eier den. Områdene som er tynnest dekket er generell lagerstyringsteori og nyere K-means-litteratur.
> **Coach-kommentar:** Eier svakheten + forklarer hvorfor de 22 er kvalitative + indikerer hvor du ville utvidet. Tre-trinns-svar.

> **Sensor:** Hva mangler i referanselisten din?
> **Du:** Tre konkrete hull: (1) en **lærebok-referanse for EOQ** — Silver, Pyke & Thomas eller tilsvarende grunnverk — som ville gitt bredere teoretisk forankring for Wilson-modellen; (2) **generell lagerstyringsteori** utover sykehuskontekst, slik at metodikken er bedre rammet inn i SCM-litteratur; (3) **nyere K-means-litteratur** og sammenligning med alternative klyngealgoritmer (DBSCAN, hierarkisk). Disse er erkjente svakheter, og i en revidert versjon ville referanselisten utvides i disse retningene.
> **Coach-kommentar:** Konkret pugg-svar. Sensor straffer "alt er fint" og roser "her er det jeg ville lagt til".

> **Sensor:** Hva sier Saha & Ray (2019) konkret, og hvorfor er det viktig?
> **Du:** Saha & Ray gjennomfører en systematisk gjennomgang av 137 artikler om lagerstyringsmodeller i helsesektoren publisert frem til 2019. Hovedkonklusjonen er at det er behov for empiriske studier som kobler kvantitative klassifiseringsmodeller til konkrete beslutninger i reelle sykehussystemer — særlig casestudier basert på ERP-data. Min studie adresserer eksakt det gapet: SAP S/4HANA-transaksjonsdata kombinert med fire klassifiseringsmetoder i en regelmotor med eksplisitt besparelsesestimat. Saha & Ray er dermed både motivasjonen for studien og målestokken jeg leverer mot.
> **Coach-kommentar:** "Motivasjon + målestokk" — fin formulering for hva en gap-referanse gjør.

> **Sensor:** Du bruker referanser fra 1987 (Rousseeuw), 1993 (Partovi & Burton) og 1999 (Hautaniemi, Srinivasan & Moon). Er ikke det utdaterte kilder?
> **Du:** De er **klassikere**, ikke utdaterte. Rousseeuw (1987) er originalpapiret for silhouette-score — det er definitionsreferansen, ikke en oppdatering man kan velge bort. Hautaniemi & Pirttilä (1999) er ofte sitert som standardreferanse for EOQ i MRP-miljø; selve Wilson-formelen er fra 1913 og er ikke "utdatert" på samme måte som empiriske studier. Srinivasan & Moon (1999) etablerte K-means' rolle i SCM-litteratur og er fortsatt mye sitert. Partovi & Burton (1993) brukes som teoretisk grunnlag for å begrunne at single-criterion ABC er utilstrekkelig. Alderen er ikke kvalitetsindikator for metodologiske kanoner.
> **Coach-kommentar:** "Klassikere, ikke utdaterte" — pugg den distinksjonen. Alder ≠ relevans for definisjonsreferanser.

> **Sensor:** Hvilken kilde er du mest avhengig av — og hva hvis jeg utfordrer den?
> **Du:** **Saha & Ray (2019)** — fordi den bærer gap-argumentet som rettferdiggjør hele studiens originalitet. Hvis du utfordrer den, ville jeg gjort to ting: (1) Anerkjenne at deres review er fra 2019 og at ny litteratur kan ha lukket gapet delvis — jeg har ikke gjennomført min egen review i 2026. (2) Påpeke at selv om litteraturen har modnet, har det norske / Helse Vest-spesifikke gapet ikke blitt lukket: ingen empirisk SAP-basert sykehuscasestudie publisert i 2024–2025 dekker akkurat Helse Bergen-konteksten. Saha & Rays gap er kvalitativt fortsatt åpent for denne studiens scope.
> **Coach-kommentar:** Når du eier én kilde, må du kunne forsvare den. To-trinns-forsvar: erkjenne aldring + påpeke at lokalt gap fortsatt eksisterer.

> **Sensor:** Hvordan har du sikret at referanselisten følger APA 7 norsk stil?
> **Du:** APA 7 norsk stil følges på alle sentrale punkter: (1) forfatterformat *Etternavn, Initial. Initial.* med komma før *&*; (2) årstall i parentes; (3) tittel uten kursiv, tidsskrift kursiv; (4) volum kursiv, hefte i parentes; (5) sidetall etter komma; (6) DOI som hyperlenke med https://. For konferanseproceedings brukes "I [Redaktører] (Red.)" med kapitler-sidetall. Referansene er manuelt kvalitetssikret mot oppskriften i `000 templates/`. Hvis sensor finner én formateringsfeil, er den et kosmetisk problem som rettes; oppgavens metodiske substans er ikke berørt.
> **Coach-kommentar:** Vis at du kjenner *strukturen*, ikke bare at du har en liste. Hvis sensor stiller spørsmålet, så har de allerede en mening om noe — vær åpen for korreksjon.

### 12b.5 Selvkritisk vurdering — hvor referanselisten er svak

Vær åpen om disse tre områdene hvis sensor presser:

1. **Lærebok-grunnverk for EOQ mangler.** Silver, Pyke & Thomas (eller Nahmias, eller Axsäter) ville gitt bredere teoretisk forankring. Hautaniemi & Pirttilä (1999) og Ketkar & Vaidya (2014) dekker det funksjonelt, men er artikler, ikke kanonisk lærebok.
2. **Generell lagerstyringsteori utenfor sykehuskontekst er smalt dekket.** Studien fokuserer på sykehuslogistikk, og bredere ABC/XYZ-litteratur utenfor helsesektor er underrepresentert.
3. **K-means og klyngeanalyse har bare to direkte kilder** (Srinivasan & Moon 1999 i SCM, Gurumurthy et al. 2021 i sykehus). Sammenligning med DBSCAN, hierarkisk klynging eller nyere klyngealgoritmer mangler litteraturmessig grunnlag i denne studien.

### 12b.6 APA 7 norsk stil — kort sjekkliste

For din egen kvalitetssikring (sensor sjekker sjeldent dette i muntlig, men kan kommentere):

- [ ] Forfatterformat: *Etternavn, A. A., & Etternavn, B. B.*
- [ ] Årstall i parentes etter forfatter: *(2023)*.
- [ ] Tittel på artikkel: ikke kursiv, kun førstebokstav stor.
- [ ] Tidsskrift: *kursiv*, volum *kursiv*, hefte i parentes ikke kursiv.
- [ ] Sidetall: *s. xx–yy* eller `xx–yy` etter komma.
- [ ] DOI: `https://doi.org/...` som hyperlenke der det finnes.
- [ ] Konferanser: "I S. Redaktør (Red.), *Konferansetittel*".
- [ ] Norsk-spesifikt: *&* (et-tegn) brukes, ikke "og".

### 12b.7 Forsvarsformular for referanselisten

> "De 22 referansene er tematisk fordelt på seks roller: kjernemetodikk, sykehuslogistikk-kontekst, gap-reviews, komplementær teori, sitert alternativ og teknisk programvare. Antallet er i nedre sjikt for bacheloroppgaver — det er erkjent — men hver kilde er aktivt brukt i argumentasjonen. Saha & Ray (2019) bærer gap-argumentet; Silaen og Nowotyńska bærer terskelvalgene; van Kampen bærer det konseptuelle rammeverket."

---

## 13. Vedlegg A–C

### 13.1 Vedlegg A — SAP-dataspesifikasjon

#### Hva står her

Henvisning til Tabell 4 (14 tabeller) og Tabell 5 (D-01–D-08). Tabell A1 forklarer alle SAP-feltene som er sitert i hovedteksten — MATNR, MAKTX, MTART, MATKL, WGBEZ, MEINS, WERKS, LGORT, STPRS, PEINH, MARC_ABC, ZZABC, ZZXYZ, EKGRP, BWART, NETWR, PLIFZ, MSEG_STATUS.

#### Hvorfor det står her

Vedlegg A er **etterprøvbarhetsgrunnlaget**. En sensor uten SAP-bakgrunn kan slå opp hver forkortelse og forstå hvilken tabell den hører til.

#### Sensor-Q&A

> **Sensor:** Hva er MSEG_STATUS-feltet?
> **Du:** Det er ikke et standard SAP MSEG-felt — det er et **avledet Z-felt** (egen oppretting) basert på MSEG-bevegelseshistorikk. Det indikerer om artikkelen har vært operativt aktiv i analyseperioden. D-06 sier at blank verdi tolkes som AKTIV (default-antakelse). Det er en dataforbehandlingsbeslutning, ikke et eksisterende SAP-felt. Dette er eksplisitt markert i Tabell A1 som "Avledet".
> **Coach-kommentar:** Z-felt-distinksjonen viser SAP-domeneforståelse. Standard MSEG har ikke STATUS-felt; det er en lokal konstruksjon.

### 13.2 Vedlegg B — Python-analyseverktøy

#### Hva står her

`LOG650_analyse_v2_7.py` er hovedscriptet. 12 figurscripts (`plot_*.py`) genererer Fig00–Fig11. Bibliotekversjoner: pandas 2.2.2, numpy 1.26.4, scikit-learn 1.4.2, matplotlib 3.8.4, openpyxl 3.1.2, xlsxwriter 3.2.0. `random_state=42` overalt for reproduserbarhet.

#### Sensor-Q&A

> **Sensor:** Hvorfor `random_state=42`?
> **Du:** Det er en de facto akademisk standard for reproduserbart pseudo-tilfeldig output. Tallet i seg selv er irrelevant — det er **konsistent valg** på tvers av kjøringer som betyr noe. Andre verdier (0, 7, 123) ville fungert like bra. Det viktige er at to forskjellige analytikere som kjører scriptet med samme inputdata og samme seed får identiske resultater, inkludert train/test-split og K-means-initialisering.
> **Coach-kommentar:** 42 er meme-referansen, men du nevner det ikke. Du nevner heller "konsistent valg, ikke verdien".

### 13.3 Vedlegg C — KI-erklæring

#### Hva står her

Tre kategorier KI-bruk:
1. **Kode og algoritmer** — Claude brukt til kodestøtte og feilsøking i Python-scriptet.
2. **Figurer og tabeller** — Claude bidro til layout, fargepalett, aksetitler. Ingen dataverdier modifisert.
3. **Tekststrukturering** — Disposisjon, formuleringer. Alle faglige påstander forfatterens egne.

Refleksjon over KI-brukens påvirkning. Avgrensning: rådata fra SAP ikke lagt inn i KI-verktøyet; ingen pasientdata.

#### Hvorfor tre kategorier?

HiMolde-retningslinjene krever **eksplisitt deklarasjon per KI-bruk-kategori**. Skille mellom kode (verktøy-bistand) og tekst (innholdsbistand) er metodisk viktig — det signaliserer at KI ikke har påvirket *faglig retning*.

#### Sensor-Q&A

> **Sensor:** Hvor sikker er du på at all KI-generert kode er korrekt?
> **Du:** All KI-generert kode er testet, verifisert mot forventede output, og iterativt revidert. Reproduserbarheten gjennom `random_state=42` betyr at hvis koden ga feil resultat én gang, gir den feil resultat hver gang — feil er deterministiske og oppdagbare. Jeg har manuelt kryssjekket nøkkeltall (709, 145, 117, kr 451 515, 33 %) mot scriptets output og rapportens tabeller. KI har akselerert kodingen, men endelig kvalitetskontroll er mitt ansvar.
> **Coach-kommentar:** "Determinisme + manuell kryssjekk" — to lag av kvalitetssikring. Vis at du har strukturert prosessen.

> **Sensor:** Du sier rådata aldri ble lagt inn i KI-verktøyet. Hvorfor er det viktig?
> **Du:** To grunner: (1) **Personvern** — selv om datasettet ikke inneholder pasientidentifikatorer, er det operative data fra Helse Bergen, og det er prinsipielt riktig å holde sensitive forretningsdata utenfor tredjepartsverktøy. (2) **Reproduserbarhet** — hvis KI-verktøyet hadde hatt rådata-input, ville modellens output kunne påvirket av variasjoner i KI-modellen. Ved å holde KI-verktøyet på kode- og språkrullen, og ikke data-rullen, er pipelinen reproduserbar uten avhengighet av KI-tilstand.
> **Coach-kommentar:** Personvern + reproduserbarhet — to gode grunner. Sensor straffer hvis du svarer bare med personvern.

#### Forsvarsformular for vedleggene

> "Vedlegg A gir SAP-feltspesifikasjon for fagfremmed leser; Vedlegg B dokumenterer Python-pipelinen med bibliotekversjoner og `random_state=42`; Vedlegg C deklarerer KI-bruk i tre kategorier per HiMolde-retningslinjer."

---

## 14. Drilling-pakke: 25 vanligste sensorspørsmål

Pugg disse i den rekkefølgen de er listet. Hver av dem har et 2–4-setningssvar du må kunne parafrasere fra hodet.

### Tema 1: Problemstilling og avgrensning (Q1–Q4)

**Q1: Hva er problemstillingen din?**
"Identifikasjon av artikler ved Helse Bergens forsyningslager (WERKS 3300, LGORT 3001) som er kandidater for HVFS-overføring, kombinert med kvantifisering av besparelsespotensialet."

**Q2: Hvorfor akkurat dette problemet?**
"HVFS er under etablering med APL-leveranser frem mot 2029, og LIBRA gjør SAP S/4HANA-data harmonisert på tvers av Helse Vest. Det skaper en operasjonell beslutningssituasjon som krever datadrevet underlag."

**Q3: Hva avgrenset du bort?**
"Legemidler, implantater, dyrt utstyr, andre lagre enn LGORT 3001, inaktive artikler (D-01), og bestillingspunkt-beregninger (ROP utelatt pga. dårlig leveringstidsdata)."

**Q4: Hvorfor kvantitativ casestudie?**
"Datatilgangen er kvantitativ og automatisk registrert; problemet er operasjonelt definerbart; reproduserbarhet er et primært designkrav; kvalitativt skjønn legges på i implementeringsfasen via pilotvalidering."

### Tema 2: Metode og data (Q5–Q11)

**Q5: Hvor mange SAP-tabeller, og hvilke er kjernen?**
"14 tabeller via SE16H. Kjerne: MARA + MAKT for ID, MBEW for pris (med PEINH-korreksjon), MSEG (BWART 201, 647) for forbruk, EKPO for ABC-verdi, EKBE for ordrefrekvens, MDMA for ZZABC/ZZXYZ til validering."

**Q6: Hva er D-01–D-08?**
"Åtte eksplisitte datavalgsbeslutninger som dokumenterer hvert sted i datapipelinen der analytikeren måtte velge mellom alternative behandlingsmåter. D-01 er populasjonsfilteret som reduserer 1006 → 709, D-02 er PEINH-korreksjonen, D-03 er beregnet ABC-verdi for 204 artikler uten EKPO, osv."

**Q7: Hva er 709, og hvor kommer det fra?**
"709 er antall aktive artikler etter D-01-filteret D_ANNUAL > 0 OR TOTAL_STOCK > 0 anvendt på rå-uttrekkets 1 006. Det er populasjonen som hele studien analyserer."

**Q8: Hva er PEINH-korreksjonen?**
"STPRS i MBEW er ikke pris per stykk, men pris per PEINH-enheter. UNIT_PRICE = STPRS / PEINH. Uten denne ville verdier vært feilskalert med faktor 10 eller 100 for medisinsk forbruksmateriell."

**Q9: Hvorfor 24 mnd. analyseperiode?**
"Lang nok til å fange sesongvariasjon over to fulle sykluser. Kort nok til at COVID-aftermath og dataforringelse i eldre data ikke dominerer. Det er det perioden med best komplett MSEG/EKBE-dekning."

**Q10: Hvorfor `random_state=42`?**
"De facto akademisk standard for reproduserbart pseudo-tilfeldig output. Garantert at to kjøringer med samme inputdata gir samme split og samme K-means-initialisering."

**Q11: Hvordan ville du sjekket at scriptet ditt er riktig?**
"Tre måter: (1) deterministisk output med samme seed; (2) manuell utregning av enkeltartikler mot scriptets verdier; (3) kryssjekk av aggregerte tall mot tabellene i rapporten — 709, 145, 117, 33 %, 0,383."

### Tema 3: Metodikk-kjernen (Q12–Q18)

**Q12: Hvorfor 80/95-grensene i ABC?**
"Standard Pareto-grenser fra Silaen et al. (2023) og bredt akseptert i lagerstyringslitteraturen. Sykehussortiment gir 25,7 % A-andel (noe bredere enn 20 %), konsistent med Gupta et al. (2007)."

**Q13: Hvorfor 0,5 og 1,0 i XYZ?**
"Nowotyńska (2013) — empirisk kalibrert for industrielle og helsesektor-sortimenter. Suryaputri et al. (2022) bekrefter samme grenser i helseindustrien."

**Q14: Hvorfor S = 750 NOK?**
"Bransjestandard fra Bijvank & Vis (2012) og Kelle et al. (2012). Lokal kalibrering ville krevd egen ABC-kalkyle av innkjøpsprosessen. Sensitivitetsanalysen tester {500, 750, 1000} og viser robust konklusjon."

**Q15: Hvorfor $\tau_f = 1{,}5$?**
"Operasjonell skjønnsbeslutning — EOQ-kostnadskurven er flat nær optimum, så små avvik gir små besparelser. 50 % overskridelse skiller operasjonelt vesentlige fra statistisk merkbare avvik. Testet i sensitivitet over {1,25; 1,50; 2,00}."

**Q16: Hvordan finner du $f^*$?**
"Deriver $TC(f) = fS + DH/(2f)$ med hensyn til $f$. Sett deriverte lik null: $S = DH/(2f^{*2})$. Trekk kvadratrot: $f^* = \sqrt{DH/(2S)}$. Andre deriverte er positiv, så minimum."

**Q17: Hva er K-means' featurevektor?**
"$\mathbf{x} = [z(\ln \text{CV}), z(\ln(v+1)), z(\ln(|\Delta TC|+1))]$. Log-transformasjon før z-score for å håndtere høyreskjevhet. Konstantledd +1 hindrer ln(0)."

**Q18: Hvorfor K = 3?**
"Datadrevet via silhouette-søk K ∈ {2..7}. K = 3 ga høyeste score (0,383 trening, 0,368 test). For K ≥ 4 monotont synkende — K = 3 er tydelig optimum, ikke lokal topp."

### Tema 4: Resultater og tolkning (Q19–Q22)

**Q19: Hva er hovedfunnet?**
"145 av 709 artikler (20,5 %) identifisert som HVFS-kandidater, fordelt på tre regelkategorier R3 (71) + R4 (18) + R5 (56). Besparelsesintervall kr 176k–764k/år, base case kr 451 515."

**Q20: Hva er ZZXYZ-funnet?**
"Kun 33 % samsvar mellom SAPs eget ZZXYZ-felt og beregnet CV-klasse. SAP klassifiserer 7 artikler som Z, beregnet finner 79. ZZXYZ er systematisk underrapportert og kan ikke brukes som uavhengig beslutningsgrunnlag uten rekalkulering."

**Q21: Hvor stor er sensitivitetsintervallet?**
"27 scenarier (3 × 3 × 3 av S, h, $\tau_f$) gir kr 176 374 til kr 763 903 per år. Dominant variabel er S (lineær effekt). Alle 27 gir positiv besparelse."

**Q22: Hvorfor 117 og ikke 145 i besparelsen?**
"Besparelsesformelen summerer $\Delta TC$ kun for artikler som *både* er anbefalt OVERFØR (145) *og* har FOR_MANGE_ORDRER (kostnadsavvik kan kvantifiseres). 28 R4/R5-artikler er anbefalt OVERFØR uten FOR_MANGE_ORDRER-status — disse anbefales på K_OVERFØR-signal alene, uten direkte EOQ-besparelse å summere."

### Tema 5: Diskusjon og svakheter (Q23–Q25)

**Q23: Hva er den største svakheten ved studien?**
"Manglende ekstern validering. Det finnes ingen fasit-datasett over korrekte HVFS-beslutninger ved Helse Bergen, så vi kan ikke beregne presisjon eller recall for regelmotoren. Mitigasjon: anbefaling 1 om pilotvalidering vil generere det første empiriske fasit-datasettet."

**Q24: Hvorfor er ikke VED operasjonalisert?**
"VED-kritikalitet er klinisk vurdering, ikke maskinlesbar i SAP MARA/MARC. Operasjonalisering ville krevd manuell innhenting fra kliniske avdelinger utenfor scope. R1 (Z = BEHOLD) brukes som delvis proxy; anbefaling 1 spesifiserer klinisk VED-vurdering før implementering."

**Q25: Hva ville du gjort annerledes?**
"Tre konkrete forbedringer: (1) Lokal kalibrering av S og h gjennom ABC-kalkyle av innkjøpsprosessen, slik at parametere er empirisk fundert; (2) Berikning av EINE med faktiske leveringstider for å aktivere ROP-modulen; (3) Inkludering av VED-data fra klinisk gjennomgang av topp-100 artiklene som tilleggsfeature i K-means."

---

## 15. 10 felletypene — spørsmål som ser snille ut

Disse spørsmålene har en innebygd metodisk felle. Forsvarsstrategien er å gjenkjenne fellen *uten å si "det er en felle"*.

### Felle 1: "Du har funnet kr 451 515 besparelse — er ikke det presist tall?"

**Fellen:** Sensor leter etter om du selger base case som "svaret".
**Riktig svar:** "Nei — kr 451 515 er base case innenfor et sensitivitetsintervall på kr 176k–764k. Det er den forventede midtverdien gitt antagelsen om $g = 75\,\%$, ikke et presist estimat."

### Felle 2: "K-means gir lite uavhengig informasjon — er den da overflødig?"

**Fellen:** Sensor vil at du skal si "ja, jeg burde tatt den ut".
**Riktig svar:** "K-means' rolle er **triangulering**, ikke uavhengig informasjon. At regelbasert og datadrevet metode konvergerer er et validitetsargument for at terskelvalgene 80/95 og 0,5/1,0 ikke er vilkårlige. Den er ikke overflødig — dens funksjon er bekreftende."

### Felle 3: "Hva om du brukte K = 4 i stedet for K = 3?"

**Fellen:** Sensor sjekker om K-valget var begrunnet.
**Riktig svar:** "K = 3 ga høyest silhouette (0,383). For K = 4 og oppover var silhouette monotont synkende. K = 3 var tydelig optimum, ikke en lokal topp. Hadde silhouette toppet seg ved både K = 3 og K = 4, ville jeg testet begge i parallelle regelmotorer."

### Felle 4: "Du har bare brukt KI til kodestøtte og språk, ikke til faglig analyse?"

**Fellen:** Sensor vil at du skal si "vel, kanskje litt på analysen også" og dermed undergrave akademisk integritet.
**Riktig svar:** "Korrekt — KI er brukt til kodestøtte, layout og språk. Den faglige retningen — metodevalg, regelutforming, tolkning av resultater — er mitt eget arbeid. Vedlegg C deklarerer dette eksplisitt i tre kategorier. Rådata fra SAP er aldri lagt inn i KI-verktøyet."

### Felle 5: "ZZXYZ er bare 33 % samsvar — kan det være at *din* CV-beregning er feil?"

**Fellen:** Sensor snur funnet på hodet.
**Riktig svar:** "Min CV-beregning bruker MSEG-data direkte med transparent formel $\sigma/\mu$ over 24 mnd. forbruksverdier. ZZXYZ oppdateres via SAP MRP og kan bruke andre terskler eller perioder. Når SAP klassifiserer kun 7 av 375 som Z mens den uavhengige CV-beregningen finner 79, er det åpenbart at SAPs verdi er underrapportert — ikke at min beregning er overrapportert. Kategoriforskjellen på Z-kolonnen (6 vs. 0 i diagonalen) er for stor til å forklare med terskelforskjeller."

### Felle 6: "Hvorfor ikke bare bruke den anerkjente EDAS-metoden?"

**Fellen:** Sensor tester om du kjenner alternative metoder og kan begrunne valg bort.
**Riktig svar:** "EDAS (Keshavarz Ghorabaee et al., 2015) krever subjektiv vekting av kriterier — for eksempel hvor mye vekt skal verdi ha mot variabilitet. Det undergraver reproduserbarheten. Jeg har valgt objektivt beregnbare kriterier (verdi, CV, EOQ-avvik) for å sikre at en annen analytiker får samme klassifisering. EDAS ville krevd ekspertintervjuer for å fastsette vekter — utenfor scope og potensielt redusert sammenlignbarheten."

### Felle 7: "Du sier 73 % av artiklene er FOR_MANGE_ORDRER. Da er hele bestillingspraksisen feil?"

**Fellen:** Sensor inviterer deg til normativ overkonklusjon.
**Riktig svar:** "Ikke nødvendigvis 'feil' — kan reflektere lagringsbegrensninger, forsyningssikkerhetspolitikk eller leverandørrutiner. Det indikerer **strukturell** overbestilling sammenlignet med Wilson-optimum, som HVFS-sentralisering kan adressere via APL. Men EOQ er en stilisert modell; det er ikke fasit."

### Felle 8: "Ville ikke en Monte Carlo-simulering vært bedre enn analytisk besparelsesestimat?"

**Fellen:** Sensor foreslår avansert metode for å se om du anerkjenner begrensningen.
**Riktig svar:** "Ja — Monte Carlo ville gitt et dynamisk estimat som fanger samspill mellom ordrefrekvens, lagernivå og servicenivå over tid. Det er foreslått som videre forskning i kap. 8.4. Den analytiske tilnærmingen ble valgt fordi den er transparent og reproduserbar, og fordi besparelsesintervallet kr 176k–764k allerede dekker den vesentlige usikkerheten. Monte Carlo ville styrket estimatets dynamikk, ikke nødvendigvis intervallets bredde."

### Felle 9: "Du har bare 22 referanser — er ikke det litt tynt?"

**Fellen:** Sensor utfordrer referansebredden eksplisitt.
**Riktig svar:** "22 referanser er i nedre sjikt for bacheloroppgaver. Hver er aktivt brukt i metodologisk eller empirisk argumentasjon — ingen er pyntereferanser. Bredere base, særlig innen generell lagerstyringsteori og klyngeanalyse, ville styrket litteraturgjennomgangen. SENSORSIMULERING-vurderingen merker dette som svakhet, og jeg eier den."

### Felle 10: "Hvis dette er så enkelt — fire metoder og en regelmotor — hvorfor har ingen gjort det før?"

**Fellen:** Sensor tester originalitetskravet.
**Riktig svar:** "Saha & Ray (2019) sin review av 137 artikler konstaterer at empiriske casestudier som kombinerer ABC, XYZ, EOQ og klyngeanalyse på faktiske ERP-data er underrepresentert. Hver metode er kjent isolert; kombinasjonen og operasjonaliseringen på SAP S/4HANA-data fra et faktisk sykehus med eksplisitt besparelsesestimat er nettopp gapet jeg adresserer. Det er ikke metodisk nyhet — det er empirisk anvendelse i et felt der ERP-datacasestudier mangler."

---

## 16. Hvis sensor presser deg — script for elegant retrett

Av og til presser sensor et spørsmål du ikke har et klart svar på. Her er fire setningstyper du kan bruke uten å miste autoritet.

### Setningstype 1: Erkjenn + henvis

> "Det er en god kritikk. Den dekkes i kapittel 8.4 / SENSORSIMULERING som en kjent svakhet. Min mitigering er X. Jeg ville gjerne ha utforsket det videre, men det lå utenfor bachelorscopen."

### Setningstype 2: Konvertér til "videre forskning"

> "Det er presis det spørsmålet jeg foreslår som videre forskning i kapittel 9.3 / 8.4. Studien gir grunnlag for å stille spørsmålet, men ikke for å besvare det fullt ut innenfor bacheloroppgavens scope."

### Setningstype 3: Skill mellom hva du *kan* si og hva du *ikke* kan si

> "Jeg kan si at [det studien dokumenterer]. Jeg kan ikke si at [det som krever ekstern validering eller utvidet datagrunnlag], og det er nettopp derfor anbefaling 1 / videre forskning er nødvendig."

### Setningstype 4: Tenkepause med begrunnelse

> "Det er et interessant spørsmål. La meg tenke et øyeblikk. Hvis jeg forstår spørsmålet rett, så handler det om [parafrase]. Mitt utgangspunkt ville være [første tilnærming], men det kommer an på [forutsetning]."

### Hva du *ikke* skal gjøre

- Ikke svar "jeg vet ikke" tomt. Si "jeg har ikke vurdert nøyaktig det aspektet, men strukturen ville være X".
- Ikke gå i forsvar. Erkjenn kritikken, deretter forklar mitigasjon.
- Ikke bli på defensiven om hele oppgaven hvis ett spørsmål går skjevt. En enkelt felle felles ikke en god oppgave.
- Ikke si "sensoren har rett" reflektorisk. Vurder først om kritikken faktisk treffer.

---

## 17. 90-sekunders elevator-pitch for åpning av muntlig

Pugg dette ord for ord. Det er åpningen din.

---

> **Oppgaven min utvikler et datadrevet beslutningsgrunnlag for hvilke artikler ved Helse Bergens forsyningslager — WERKS 3300, LGORT 3001 — som bør overføres til det regionale sentrallageret HVFS. Bakteppet er to samtidige initiativer: HVFS-etableringen frem mot 2029 med NorEngros som operatør og avdelingspakkede leveranser direkte til avdeling, og LIBRA-prosjektet som ruller ut SAP S/4HANA harmonisert på tvers av Helse Vest.**

> **Jeg har trukket ut 14 SAP-tabeller via SE16H for perioden 2024–2025, dokumentert åtte datavalgsbeslutninger fra D-01 til D-08 som tar uttrekket fra 1 006 til 709 aktive artikler, og kjørt fire komplementære analyser: ABC for verdi, XYZ for forbruksstabilitet, EOQ for bestillingseffektivitet, og K-means klyngeanalyse for datadrevet validering uten forhåndsterskler.**

> **En regelmotor med åtte prioriterte regler aggregerer signalene til én anbefaling per artikkel. Resultatet er 145 OVERFØR-kandidater, 257 BEHOLD-LOKALT, 284 VURDER og 23 MANGLER DATA. Besparelsesestimatet er kr 451 515 per år i base case, med et sensitivitetsintervall på kr 176 000 til 764 000 over 27 parametervariasjoner. Et selvstendig empirisk bifunn er at SAPs eget ZZXYZ-felt bare samsvarer med beregnet CV-klasse i 33 prosent av tilfellene — et resultat som har umiddelbar operasjonell konsekvens for LIBRA.**

> **Studiens primære bidrag er metodisk transparens og reproduserbarhet: hele pipelinen er deterministisk med `random_state=42`, alle terskler er litteraturbaserte eller eksplisitt testet i sensitivitet, og hver enkelt anbefaling kan spores til én konkret regel og ett spesifikt signalmønster. Begrensningene er erkjent — manglende ekstern validering, ikke-kalibrerte parametre, og VED-dimensjonen som krever klinisk gjennomgang — og dekkes av fire prioriterte anbefalinger som rammeverk for implementering.**

---

**Pugg de fire avsnittene som fire pillarer:** (1) Hva, (2) Hvordan, (3) Resultat, (4) Bidrag og begrensning.

---

## 18. Hovedtall — pugg-kort

Skriv ut og bær med deg på muntlig. Disse må sitte:

| Tall | Hva |
|---|---|
| **709** | aktive artikler etter D-01 |
| **1 006** | rå-uttrekk før D-01 |
| **14** | SAP-tabeller via SE16H |
| **8** | datavalgsbeslutninger D-01 til D-08 |
| **24 mnd.** | analyseperiode 2024–2025 |
| **182 / 184 / 338** | ABC: A / B / C (= 25,7 / 26,0 / 47,7 %) |
| **350 / 193 / 144** | XYZ: X / Y / Z (= 50,9 / 28,1 / 20,9 %) |
| **487** | artikler med komplett EOQ-data |
| **356 / 100 / 31** | EOQ: FOR_MANGE / OK / FOR_FÅ |
| **73,1 %** | FOR_MANGE_ORDRER-andel |
| **389 / 98** | K-means train / test |
| **0,383 / 0,368** | silhouette train / test |
| **K = 3** | optimalt antall klynger |
| **281 / 175 / 31** | K-means klyngestørrelser |
| **CV 0,47 / verdi kr 167 267** | K_OVERFØR-klyngens snitt |
| **143 / 114 / 71 / 18 / 56 / 160 / 23 / 101** | R1–R8 |
| **145** | OVERFØR_HVFS totalt |
| **117** | i besparelsesgrunnlag |
| **257** | BEHOLD_LOKALT |
| **284** | VURDER_NÆRMERE |
| **23** | MANGLER_DATA |
| **kr 301 010 / 451 515 / 602 020** | besparelse worst / base / best |
| **kr 176 374 – 763 903** | sensitivitetsintervall over 27 scenarier |
| **kr 2 333 441** | $\sum \Delta TC$ for alle 487 EOQ-artikler |
| **125 / 375 = 33 %** | ZZXYZ-samsvar |
| **7 vs. 79** | SAP Z vs. beregnet Z |
| **204** | artikler med beregnet ABC-verdi (D-03) |
| **94 %** | LEAD_TIME-dekning (D-05 standardverdi 14 dager) |
| **S = 750, h = 20 %, $\tau_f = 1{,}5$, g = 75 %** | base case-parametre |

---

## 19. Tre-minutters sjekkliste rett før eksamen

Gå gjennom denne sjekklisten 3–5 minutter før du går inn:

- [ ] Jeg kan resitere elevator-pitch fra hodet (kap. 17)
- [ ] Jeg kan tegne analysepipelinen på papir (SAP → D-01–D-08 → fire metoder → regelmotor → output)
- [ ] Jeg vet at hovedtallet er **145 OVERFØR**, base case **kr 451 515**, intervall **kr 176k–764k**, ZZXYZ-samsvar **33 %**
- [ ] Jeg kan utlede $f^* = \sqrt{DH/(2S)}$ (4 trinn)
- [ ] Jeg kan forklare PEINH-korreksjonen med ett eksempel (hanske 150/100 = 1,50)
- [ ] Jeg vet hvorfor 117 ≠ 145 (FOR_MANGE_ORDRER-krav)
- [ ] Jeg vet hvorfor R1 er først (Z-override som beskytter forsyningssikkerhet)
- [ ] Jeg vet hvorfor K-means' bidrag er **triangulering**, ikke uavhengig informasjon
- [ ] Jeg vet at den største svakheten er **ingen ekstern validering** — mitigert av pilot
- [ ] Jeg vet at VED ikke er operasjonalisert — kompensert av R1 og anbefaling 1
- [ ] Jeg har en setning klar hvis jeg blir blank: "La meg tenke et øyeblikk. Hvis jeg forstår spørsmålet rett, så handler det om..."

---

## 20. Avslutning — det ene rådet

Hvis du må huske én ting fra denne filen, så er det dette:

> **Eier svakhetene før sensor får påpekt dem.** Ikke skjul. Ikke unnskyld. Forklar svakheten presist, forklar mitigasjonen, og pek mot videre forskning. Det er den modne akademiske holdningen, og det er den som gir karakteren.

Den nest viktigste tingen:

> **Skill mellom hva oppgaven *kan* og *ikke kan* si.** Du *kan* si at 145 artikler oppfyller eksplisitte kriterier basert på SAP-data. Du *kan ikke* si at de er objektivt korrekte overføringskandidater — det krever pilotvalidering. Skillet mellom **strukturert beslutningsstøtte** og **autorisert beslutning** er der din metodiske selvtillit ligger.

Lykke til. Du har gjort jobben — nå er det bare å fortelle om den.

---

*Slutten på MUNTLIG_FORSVAR_COACH.md.*
