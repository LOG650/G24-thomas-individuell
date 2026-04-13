# Sensorsimulering – LOG650 Bacheloroppgave

**Kandidat:** Thomas Ekrem Jensen
**Emne:** LOG650 Forskningsprosjekt: Logistikk og kunstig intelligens
**Institusjon:** Hogskolen i Molde, varen 2026
**Veileder:** Bard Inge Austigard Pettersen
**Dato for simulering:** 13. april 2026

> **Merknad:** Denne simuleringen er gjennomfort uten tilgang til offisiell sensorveiledning. Vurderingen baseres pa vanlig akademisk sensurlogikk for bacheloroppgaver, ECTS-skalaen (A-F) og kryssjekk av rapportens pastander mot implementert kode.

---

## 1. Totalvurdering

Oppgaven presenterer en strukturert, reproduserbar analysemodell for klassifisering av medisinsk forbruksmateriell ved Helse Bergens forsyningslager. Problemstillingen er klart formulert, praktisk relevant og godt forankret i en reell organisatorisk kontekst (HVFS-etableringen og LIBRA-prosjektet). Metoderammeverket -- som kombinerer fire komplementaere analysemetoder med en regelbasert beslutningsmodell -- demonstrerer ambisjon utover det som er vanlig pa bachelorniva.

Oppgavens storste styrke er den systematiske transparensen: alle datavalgsbeslutninger (D-01 til D-08) er eksplisitt dokumentert, koden er deterministisk og reproduserbar, og parametervalgene testes gjennom en 27-scenariosensitivitetsanalyse. Diskusjonskapittelet viser moden selvkritikk -- kandidaten identifiserer de fleste svakhetene selv, inkludert K-means' begrensede uavhengige bidrag og fravaeret av VED-dimensjonen.

Hovedsvakhetene er (a) en noe smal referansebase (22 kilder), (b) at K-means i praksis fungerer som et bekreftende stottefilter snarere enn et uavhengig analysesignal, (c) at sentrale kostnadsparametere (S, h, g) ikke er kalibrert mot lokale data, og (d) at ekstern validering av regelmotoranbefalingene mangler. Disse svakhetene er imidlertid delvis kompensert av at kandidaten selv erkjenner dem eksplisitt og tilbyr sensitivitetsanalyse som risikodekning.

---

## 2. Forelopig karakterforslag

### Hovedforslag: **B**

**Spenn:** B (solid) -- mulig A dersom sensor vekter metodisk ambisjon og praktisk relevans hoyt, mulig C dersom sensor vekter referansebredde og ekstern validering tungt.

**Begrunnelse:** Oppgaven er klart over gjennomsnittet for en bacheloroppgave i logistikk. Den demonstrerer selvstendig problemlosning, metodisk bevissthet og evne til a koble teori med praksis. Manglene er reelle, men kandidaten kompenserer gjennom transparens og selvkritikk. Oppgaven tilfredsstiller kravene til B-niva pa ECTS-skalaen: "meget god prestasjon som klart overstiger gjennomsnittet."

---

## 3. Vurdering per kriterium

### 3.1 Problemstilling og relevans

**Styrker:**
- Problemstillingen er presis, todelt (identifikasjon + kvantifisering) og operasjonaliserbar
- Direkte forankret i en pagaende organisatorisk endring (HVFS/LIBRA)
- Tydelig avgrenset: beslutningsstotte, ikke implementering
- Avgrensningene (kap. 1.3) er eksplisitt begrunnet, ikke bare listet
- Antagelsene (kap. 1.4) er formalisert med formelnotasjon

**Svakheter:**
- Proposalet nevner "kritikalitet" i forskningssporsmaleet, men VED-dimensjonen er utelatt i analysen. Rapporten diskuterer dette som begrensning (8.4), men det representerer et uinnfridd element i den opprinnelige problemformuleringen
- LGORT endret fra 3000 (proposal) til 3001 (rapport) -- en liten inkonsistens som er rettet i koden

**Alvorlighetsgrad:** Lav. Kjerneproblematikken er innfridd; VED-fravseret er adekvat handtert gjennom diskusjonen.

**Sensorsprak:** *Problemstillingen er presis og praktisk relevant. Avgrensningene er godt begrunnet. Kritikalitetsdimensjonen (VED) nevnes i proposalet men gjennomfores ikke -- dette diskuteres aerlig som en begrensning.*

---

### 3.2 Litteratur og teoretisk forankring

**Styrker:**
- 22 referanser med klar relevans for oppgavens metoder
- Tabell 1 gir god oversikt med kopling til egen oppgave
- Tabell 2 sammenligner metodenes styrker/svakheter systematisk
- Konseptuelt rammeverk (2.7) viser at kandidaten forstar helheten
- Identifiserer et konkret gap i litteraturen (empiriske SAP-casestudier i sykehuskontekst)

**Svakheter:**
- 22 kilder er i nedre sjikt for en bacheloroppgave. Flere sentrale omrader har bare en eller to kilder (f.eks. K-means i sykehuslogistikk: kun Gurumurthy et al.)
- Noe smal bredde: mangler kilder pa ABC-analyse som ikke er sykehus-spesifikke, general klyngeanalyseteori utover Srinivasan & Moon, og nyere reviewartikler
- Klassikeren Silver, Pyke & Thomas (eller tilsvarende laerebok) mangler som grunnreferanse for EOQ
- Partovi & Burton (1993) nevnes i teksten men er knapt integrert i analysen

**Alvorlighetsgrad:** Moderat. Referansedekningen er funksjonell men ikke imponerende. Sensor vil typisk forvente 25-35 kilder pa dette nivaet.

**Sensorsprak:** *Litteraturgjennomgangen er fokusert og relevant, med god kopling mellom kilder og eget arbeid (jf. Tabell 1). Referanselisten er noe smal (22 kilder) -- bredere dekning innen generell lagerstyringsteori og klyngeanalyse ville styrket den teoretiske forankringen.*

---

### 3.3 Metodevalg og forskningsdesign

**Styrker:**
- Tydelig design: kvantitativ casestudie med deskriptiv, eksplorativ og normativ komponent
- Begrunnelse for hvert metodevalg med referanse til litteraturen
- Eksplisitt argumentasjon for hvorfor flerkriterietilnaerming (ABC+XYZ+EOQ+K-means) fremfor EDAS/MCDM
- Etisk betraktning (4.4) er inkludert og relevant
- KI-bruk i metodekapittelet (4.5) er adekvat

**Svakheter:**
- Forskningsdesignet beskrives som "rent kvantitativt", men en kort bekreftende samtale med innkjopsfaglig personale ville styrket den eksterne validiteten vesentlig -- dette diskuteres som begrensning, men det er en reell metodisk svakhet
- Ingen formal stasjonaritetstest for EOQ-forutsetningene

**Alvorlighetsgrad:** Lav til moderat. Designet er velvalgt og godt begrunnet for problemstillingen.

**Sensorsprak:** *Forskningsdesignet er passende for problemstillingen og godt begrunnet. Valget av fire komplementaere metoder er ambisiost for en bacheloroppgave. Fravseret av kvalitativ validering (ekspertvurdering) er en anerkjent begrensning.*

---

### 3.4 Datagrunnlag og etterprovebarhet

**Styrker:**
- 14 SAP-tabeller systematisk dokumentert (Tabell 4)
- 8 datavalgsbeslutninger (D-01 til D-08) er eksemplarisk transparent -- dette er uvanlig grundig for bachelorniva
- Populasjonsavgrensning (1006 -> 709) er logisk begrunnet
- Figur 3/4 gir god oversikt over datapipeline og variabelfordelinger
- PEINH-korrigering (D-02) viser SAP-domenekunnskap
- Koden er deterministisk (random_state=42) og reproduserbar

**Svakheter:**
- 204 av 709 artikler (29 %) mangler EKPO-data og far beregnet ABC-verdi. Rapporten diskuterer dette, men andelen er hoy nok til a pavirke tillit til rangeringen
- Leveringstid dekker kun 6 % -- dette begrenser fremtidig ROP-analyse vesentlig
- MSEG-data fanger ikke nod-uttak utenfor SAP

**Alvorlighetsgrad:** Lav. Datakvalitetsbegrensningene er apenbart kommunisert.

**Sensorsprak:** *Datagrunnlaget er godt dokumentert med eksemplarisk transparens i datavalgsbeslutningene (D-01 til D-08). At 29 % av artiklene mangler innkjopsdata er en reell begrensning, men den er adekvat handtert med alternativ verdiberegning og diskutert i kapittel 8.*

---

### 3.5 Analysegjennomforing og modellbruk

**Styrker:**
- Formell matematisk spesifikasjon av alle modeller i kapittel 5
- Klar separasjon mellom modellering (kap. 5) og analyse (kap. 6) -- i trad med kompendiet
- K-means: korrekt train/test-split for skalering forhindrer datalekkasje
- Silhouette-basert K-valg med automatisert soek (K=2-7)
- Regelmotor med sekvensiell prioritet er logisk konsistent og deterministisk
- Besparelsesmodell endret fra v2.6 til v2.7 (fra r-basert til DeltaTC-basert) -- dette er en forbedring

**Kryssjekk kode vs. rapport (alle bekreftet konsistente):**
- ABC-grenser: 80/95 % (kode linje 99-100, rapport Tabell 6)
- XYZ-grenser: CV 0.5/1.0 (kode linje 103-104, rapport Tabell 6)
- EOQ: S=750, H=20 %, tau_f=1.5 (kode linje 91-92, 266-273, rapport avsnitt 5.3)
- K-means: K=3, 3 features, train/test 80/20, n_init=50 (kode linje 321-344, rapport avsnitt 5.4)
- Regelmotor: 8 regler, sekvensiell, Z-override forst (kode linje 423-469, rapport Tabell 7)
- Besparelse: B_HVFS = Sum DeltaTCi * g, g in {0.50, 0.75, 1.00} (kode linje 501-540, rapport avsnitt 5.3)
- Sensitivitet: 27 scenarier, 3x3x3 (kode linje 574-576, rapport avsnitt 7.6)

**Svakheter:**
- K-means' uavhengige bidrag er begrenset: K_OVERFOR-klyngen overlapper i stor grad med ABC/XYZ-identifiserte artikler (kandidaten erkjenner dette selv i 8.4)
- Kun en klyngealgoritme testet (ingen DBSCAN/hierarkisk sammenligning)
- Ingen formal stasjonaritetstest for EOQ-forutsetningene

**Alvorlighetsgrad:** Moderat for K-means-redundans. Analysens kjerne (ABC+XYZ+EOQ+regelmotor) er solid.

**Sensorsprak:** *Analysegjennomforingen er grundig og metodisk korrekt. Alle parametere i rapporten samsvarer med implementert kode -- etterprovebarhet er pa et hoyt niva. K-means' merverdi er begrenset og primert bekreftende, noe kandidaten selv reflekterer over. Sensitivitetsanalysen (27 scenarier) er en styrke.*

---

### 3.6 Resultater og tolkning

**Styrker:**
- Resultater presentert systematisk i tabeller (Tabell 8-14) med tydelig struktur
- 145 artikler identifisert som overforingskandidater -- et konkret, operasjonaliserbart resultat
- Besparelsesestimat presentert som scenariointervall (301-602 TNOK/ar), ikke som punktestimat
- Sensitivitetsanalyse viser robusthet (positivt over alle 27 scenarier)
- ZZXYZ-validering (33 % samsvar) er et genuint og verdifullt funn

**Svakheter:**
- VURDER NAERMERE-gruppen (284 artikler, 40.1 %) er stor -- dette reflekterer en bevisst konservativ strategi, men det betyr ogsa at modellen er usikker for nesten halvparten av artiklene
- Klyngeprofilene i Tabell 12 har verdier som er noe vanskelige a tolke direkte for en leser uten kontekst (f.eks. "Verdi snitt kr 150" for klynge 1 vs "kr 167 267" for klynge 3 -- stor spennvidde)

**Alvorlighetsgrad:** Lav. Resultatpresentasjonen er oversiktlig og vel underbygd.

**Sensorsprak:** *Resultatene er klart presentert og knyttet tilbake til problemstillingen. Besparelseestimatet som scenariointervall er metodisk korrekt. At 40 % sendes til manuell vurdering kan sees som en svakhet i modellens dekningsgrad, men ogsa som en styrke i dens forsiktighet.*

---

### 3.7 Diskusjon, begrensninger og refleksjon

**Styrker:**
- Tabell 15 (funn vs. litteratur) er en uvanlig systematisk og transparent sammenstilling for bachelorniva
- Metodekritikk (8.2) er grundig og identifiserer de fleste reelle svakhetene
- Svakheter og begrensninger (8.4) er aerlig -- 8 konkrete punkter inkludert K-means' begrensede merverdi
- Praktisk betydning (8.3) kobler funnene direkte til SAP MM-endringer og LIBRA-prosjektet
- Kandidaten peker pa bekreftelsestendens i K-means-bruken -- dette er modent

**Svakheter:**
- Diskusjonen kunne vaert sterkere pa validitetsdrofting (intern, ekstern, begrep, statistisk konklusjon). Begrepene nevnes, men rammeverket er ikke eksplisitt brukt
- Mangler refleksjon over generaliserbarhetens grenser utover "andre WERKS i Helse Vest"

**Alvorlighetsgrad:** Lav. Diskusjonen er pa et hoyt niva for en bacheloroppgave.

**Sensorsprak:** *Diskusjonskapittelet er oppgavens sterkeste del. Selvkritikken er aerlig og konkret, og kandidaten demonstrerer evne til a vurdere egne funn kritisk. Tabell 15 (funn vs. litteratur) er eksemplarisk.*

---

### 3.8 Konklusjon og anbefalinger

**Styrker:**
- Konklusjonen besvarer begge deler av problemstillingen eksplisitt (hvilke artikler + besparelse)
- Fire prioriterte anbefalinger til Helse Bergen er konkrete og gjennomforbare
- Anbefaling om pilotfase og klinisk kritikalitetsvurdering viser praktisk modenhet
- Forslag til videre forskning (ROP, leverandorkonsolidering, replikering) er realistiske

**Svakheter:**
- Konklusjonen er noe lang og gjentar deler av resultatkapittelet
- Konklusjonsstyrken kunne vaert tydeligere kalibrert: "strukturert beslutningsgrunnlag" er passende, men grensen mellom dette og en sterkere anbefaling er noe uklar

**Alvorlighetsgrad:** Lav.

**Sensorsprak:** *Konklusjonen besvarer problemstillingen direkte og gir konkrete, gjennomforbare anbefalinger. Forslagene til videre forskning er realistiske og viser at kandidaten forstar metoderammeverkets potensial og begrensninger.*

---

### 3.9 Akademisk framstilling, struktur og KI-transparens

**Styrker:**
- Klar struktur med logisk progresjon fra innledning til konklusjon
- Separasjon mellom modellering (kap. 5) og analyse (kap. 6) folger kompendiet
- Figurliste, tabelliste og innholdsfortegnelse er komplett
- 15 tabeller og 12 figurer -- god bruk av visuell framstilling
- KI-erklaering (Vedlegg C) er grundig og tilfredsstiller alle krav i retningslinjene:
  - Verktoy oppgitt (Claude)
  - Formal beskrevet (kode, figurer, tekst)
  - Bearbeiding beskrevet
  - Refleksjon over pavirkning inkludert
  - Avgrensning mot radata presisert
  - Signaturskjema inkludert
- APA 7 norsk stil -- konsistent gjennom referanselisten
- Ordtelling: ca. 12 600 ord brodtekst (kap. 1-9), ca. 14 800 totalt -- rimelig omfang

**Svakheter:**
- Noen steder er teksten noe repetitiv -- samme poeng gjentas i sammendrag, analyse, resultater og diskusjon (f.eks. "145 artikler anbefales overfert")
- Figurnummerering i MD-kilden (Fig00-Fig11) matcher ikke alltid tabellreferansene (Figur 1-12) -- dette skyldes at figurlisten bruker logisk nummerering mens filnavnene er tekniske

**Alvorlighetsgrad:** Lav. Framstillingen er god og KI-transparensen er pa et hoyt niva.

**Sensorsprak:** *Oppgaven er velskrevet med klar struktur. KI-erklaering er grundig og tilfredsstiller alle institusjonelle krav. APA 7-referering er konsistent. Noe repetisjon mellom kapitler.*

---

## 4. Viktigste mangler som trekker ned (5 stk)

1. **Referansebredde (22 kilder):** I nedre sjikt. Mangler generelle laerebokreferanser for EOQ og klyngeanalyse, og har kun en kilde for K-means i sykehuskontekst.

2. **K-means' begrensede uavhengige bidrag:** Klyngeanalysen bekrefter i stor grad det ABC/XYZ allerede identifiserer. Kandidaten erkjenner dette, men det svekker den metodiske begrunnelsen for a inkludere en fjerde analysedimensjon.

3. **Ikke-kalibrerte parametere:** S=750 NOK og h=20 % er hentet fra internasjonal litteratur, ikke empirisk estimert for Helse Bergen. g=75 % er en ren ekspertantagelse. Sensitivitetsanalysen kompenserer delvis, men et ABC-kostnadsestimat ville styrket troverdigheten.

4. **Ingen ekstern validering:** Regelmotoranbefalingene er ikke sjekket mot innkjopsfaglig skjonn. Modellens presisjon og recall er dermed ukjente. Kandidaten diskuterer dette aerlig, men det forblir en vesentlig begrensning.

5. **Stor VURDER-gruppe (40.1 %):** Nesten halvparten av artiklene far ikke en automatisert anbefaling. Dette er en bevisst konservativ strategi, men det begrenser verktoyets umiddelbare operasjonelle verdi.

---

## 5. Sterkeste sider (5 stk)

1. **Datavalgsbeslutninger D-01 til D-08:** Eksemplarisk transparens i dataforbehandlingen. Uvanlig grundig for bachelorniva og styrker etterprovebarhet og tillit til resultatene.

2. **Sensitivitetsanalyse (27 scenarier):** Systematisk variasjon av tre parametere viser robusthet og demonstrerer at kandidaten forstar modellens usikkerhetsdrivere.

3. **Diskusjon og selvkritikk (kap. 8):** Tabell 15 (funn vs. litteratur), identifikasjon av K-means' bekreftelsestendens, og 8 eksplisitte begrensninger viser moden akademisk refleksjon.

4. **Kodekvalitet og reproduserbarhet:** Determinitisk script med random_state=42, train/test-split for datalekkasje, og full konsistens mellom rapportparametere og implementert kode.

5. **Praktisk relevans og gjennomforbarhet:** Oppgaven lander ikke bare i akademisk teori, men gir fire konkrete, prioriterte anbefalinger til Helse Bergen med direkte kopling til SAP MM-parametere og LIBRA-prosjektet.

---

## 6. Hva bor forbedres mest for innlevering

Gitt at oppgaven er naer innleveringsklar, er folgende de mest realistiske forbedringene innenfor tilgjengelig tid:

### Prioritet 1: Referanselisten (moderat innsats)
Utvid med 3-5 kilder:
- En grunnlagsreferanse for EOQ (f.eks. Silver, Pyke & Thomas eller Axsater)
- En generell klyngeanalysekilde (f.eks. Jain, 2010 eller Xu & Tian, 2015)
- En nyere review pa ABC/XYZ (dersom tilgjengelig)
- Integrer disse i teorikapittelet med 2-3 setninger hver

### Prioritet 2: Stram inn repetisjon (liten innsats)
- Sammendrag, kap. 6.5 og kap. 7.5-7.6 gjentar noen av de samme formuleringene. En runde med stramming gir bedre lesbarhet.

### Prioritet 3: Validitetsrammeverk i diskusjonen (liten til moderat innsats)
- Bruk begrepene intern validitet, ekstern validitet, begrepsvaliditet og statistisk konklusjonsvaliditet mer eksplisitt som organiseringsprinsipp i avsnitt 8.2. Innholdet er der allerede -- det trenger bare en tydeligere ramme.

### Ikke anbefalt a endre:
- Analysen og resultatene er solide og konsistente med koden. Det er ikke behov for a endre metodikk, regelmotor eller besparelsesmodell pa dette stadiet.
- KI-erkleringen er komplett og trenger ikke utvidelse.

---

## 7. Kryssjekk: KI-erklering mot retningslinjer

| Krav i retningslinjene | Oppfylt? | Kommentar |
|---|---|---|
| Oppgi verktoy | Ja | Claude |
| Beskriv formal | Ja | Kode, figurer, tekst |
| Beskriv bearbeiding | Ja | "Gjennomgatt, testet og modifisert" |
| Refleksjon over pavirkning | Ja | Punkt 4 i Vedlegg C |
| Signert erklering | Ja | Signaturskjema inkludert |
| Radata ikke delt med KI | Ja | Eksplisitt avgrensning |
| KI ikke brukt som fagkilde | Ja | Presisert i avsnitt 4.5 og Vedlegg C |

**Vurdering:** KI-erkleringen tilfredsstiller alle krav i HiMoldes retningslinjer for KI pa hjemmeeksamen.

---

## 8. Kryssjekk: Proposal-scope vs. rapport

| Element i proposalet | Innfridd? | Kommentar |
|---|---|---|
| ABC-analyse | Ja | Kap. 5.1, 6.1, 7.1 |
| Beregnet XYZ-klassifisering | Ja | Kap. 5.2, 6.2, 7.2 |
| EOQ-avviksanalyse | Ja | Kap. 5.3, 6.3, 7.3 |
| K-means klyngeanalyse | Ja | Kap. 5.4, 6.4, 7.4 |
| Regelmotor med HVFS-anbefaling | Ja | Kap. 5.5, 6.5, 7.5 |
| Besparelsesestimat | Ja | Kap. 5.3 (formel), 7.6 |
| "Kritikalitet" i forskningsspm. | Delvis | VED ikke implementert, diskutert som begrensning |
| LGORT 3000 | Rettet | Endret til LGORT 3001 i rapport og kode |

---

*Denne sensorsimuleringen er generert som intern kvalitetskontroll for innlevering. Den erstatter ikke offisiell sensur.*
