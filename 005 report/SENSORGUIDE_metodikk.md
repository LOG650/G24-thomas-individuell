# Sensorguide: metodikk og resonnement i LOG650-rapporten

**Hensikt:** Forklare *hvorfor* analysene er gjort, *hvordan* tallene er beregnet og *hvilken logikk* som binder teori → SAP-data → analyse → regelmotor → besparelse → konklusjon. Dokumentet er en leseveiledning, ikke en omskrivning.

**Forfatter:** Thomas Ekrem Jensen, LOG650, HiMolde, vår 2026.
**Kilde:** `LOG650_Rapport_FINAL.md` (samme innhold som `LOG650_Rapport.docx`).

---

## 0. Lesehensikt og rød tråd gjennom oppgaven

Hele rapporten kan leses som én sammenhengende informasjonskjede:

> **SAP-data (14 tabeller, SE16H)** → **datakvalitetsfilter (D-01 til D-08, 1 006 → 709 artikler)** → **tre uavhengige klassifiseringsanalyser (ABC + XYZ + EOQ)** + **én datadrevet validering (K-means, K=3)** → **regelmotor med 8 prioriterte regler (R1–R8)** → **145 OVERFØR-anbefalinger (20,5 %)** → **117 i besparelsesgrunnlag** → **kr 451 515/år (base case, g = 75 %)** med sensitivitetsintervall **kr 176 374 – kr 763 903/år**.

Tre metodiske grep må sensoren forstå før kapitlene leses:

1. **Triangulering, ikke enkeltmetode.** ABC, XYZ og EOQ er regelbaserte med *forhåndsdefinerte* terskler fra litteraturen. K-means er *datadrevet* uten forhåndsdefinerte terskler. Når regelbaserte og datadrevne signaler konvergerer (R3, R4, R5), styrkes anbefalingen. Når de divergerer, faller artikkelen i VURDER_NÆRMERE — bevisst forsiktighet.

2. **Identifisering, ikke implementering.** Oppgavens mandat er å peke ut artikler som *bør* vurderes for HVFS, ikke å gjennomføre overføringen. Gevinster forutsetter aktiv SAP MM-justering i etterkant.

3. **Intervaller, ikke punktestimater.** Tre parametre (S, h, g) er litteraturbaserte og ikke lokalt kalibrerte. Kompensasjon: 27 sensitivitetsscenarier som spenner kr 176k–764k. Alle gir positiv besparelse → robusthet, ikke presisjon.

---

## 1. Sammendrag og forord — hva sensoren skal feste seg ved

| Tall i sammendraget | Hva det egentlig betyr |
|---|---|
| **709 aktive artikler** | Etter D-01-filter (eks. D_ANNUAL=0 og TOTAL_STOCK=0). Ikke det totale sortimentet på 1 006. |
| **145 OVERFØR (20,5 %)** | Hovedtallet. Antall anbefalte HVFS-kandidater. |
| **257 BEHOLD (36,2 %)** | Kvalifiserte til lokal lagring (Z-artikler eller CY-artikler). |
| **284 VURDER (40,1 %)** | Bevisst stor pga. presisjonsfokus — ambig signalmønster. |
| **23 MANGLER_DATA** | < 3 mnd. forbrukshistorikk eller manglende UNIT_PRICE. |
| **kr 451 515/år** | Kun base case (g = 75 %), basert på 117 av 145 (de med FOR_MANGE_ORDRER). |
| **33 % samsvar ZZXYZ** | Kritisk bifunn — motiverer hele oppgaven. |

**Det sensoren bør lese mellom linjene:**

- 145 ≠ 117 fordi besparelsesformelen kun summerer artikler der EOQ-modellen *kan* dokumentere et kostnadsavvik (FOR_MANGE_ORDRER). De resterende 28 anbefales overført basert på K_OVERFØR-signal alene → ingen direkte EOQ-besparelse å estimere.
- Sammendragets fire-kategori-fordeling reflekterer en bevisst design: når signaler er ambige, er svaret "VURDER" — ikke "ja" eller "nei". Det er metodisk konservativt.

---

## 2. Kapittel 1 — Innledning: fra praksisproblem til kvantitativt forskningsspørsmål

**Problemoperasjonalisering:**

| Praksisnivå | Operasjonalisert som |
|---|---|
| HVFS etableres regionalt | Hvilke artikler ved Helse Bergen er APL-egnet? |
| LIBRA gir felles SAP S/4HANA | Datagrunnlag på tvers er nå mulig |
| Helse Bergen mangler datadrevet beslutningsgrunnlag | Bygg klassifisering fra MARA/MBEW/MSEG/EKPO |
| ZZXYZ vedlikeholdes ikke | Beregn CV fra MSEG-historikk i stedet |

**Avgrensningen til WERKS 3300 / LGORT 3001 er ikke vilkårlig.** Den er metodisk nødvendig fordi det er *det eneste lagerstedet med 24 mnd. komplett transaksjonshistorikk for medisinsk forbruksmateriell*. Inkludering av andre lagre ville innført datakvalitetsforskjeller som ikke kan kontrolleres.

**Hvorfor litteraturparametre (S = 750 NOK, h = 20 %, g = 75 %)?** Lokal kalibrering ville krevd egen aktivitetsbasert kostnadsanalyse — utenfor en bachelorscope. Sensitivitetsanalysen (kap. 7.6) kompenserer ved å vise robusthet over 27 kombinasjoner.

---

## 3. Kapittel 2 — Litteratur og teori: hvorfor hver metode er valgt

Hver metode dekker én dimensjon av problemet og har én blindsone som motiverer neste metode:

| Metode | Dimensjon | Blindsone | Konsekvens |
|---|---|---|---|
| **ABC** | Kapitalbinding (verdi) | Ignorerer variabilitet og kritikalitet | Trenger XYZ |
| **XYZ** | Forbruksstabilitet (CV) | Sier ingenting om verdi eller bestillingsmønster | Trenger EOQ |
| **EOQ** | Bestillingseffektivitet (ordrefrekvens) | Forutsetter stasjonær etterspørsel; ignorerer multivariat sammenheng | Trenger K-means |
| **K-means** | Multivariat mønster (CV + verdi + \|ΔTC\|) | Ingen kausal tolkning; sensitivt for K-valg | Trenger regelmotor (transparens) |
| **VED** | Klinisk kritikalitet | Ikke maskinlesbar i SAP MARA/MARC | R1-regel kompenserer delvis; klinisk pilot kreves |

**Hvor terskelverdiene kommer fra:**

- ABC 80/95 %: standardverdier i Pareto-litteraturen (Silaen et al., 2023), egnet for sykehussortiment der A-andelen typisk er bredere enn 20 %.
- XYZ 0,5 / 1,0: Nowotyńska (2013) — empirisk kalibrert for industrielle forsyningskjeder.
- EOQ S = 750, h = 20 %: Bijvank & Vis (2012), Kelle et al. (2012), Ketkar & Vaidya (2014) — bransjestandarder for sykehus.
- K-means silhouette > 0,3: Ketkar & Vaidya (2014), terskel for *eksplorativ* (ikke konfirmerende) analyse.

**Hvorfor VED ikke operasjonaliseres:** Vital/Essential/Desirable er en *klinisk* vurdering som ikke kan utledes fra transaksjonsdata. Konsekvensen er at R1 (Z = BEHOLD_LOKALT) brukes som proxy: høy variabilitet er *ofte* (ikke alltid) korrelert med klinisk uregelmessig bruk. Dette er en kjent svakhet, dokumentert i kap. 8 og avhjelpt av anbefaling 1 i kap. 9.2 (klinisk pilotvalidering før implementering).

---

## 4. Kapittel 3 — Casebeskrivelse: koblingen mellom SAP-tabeller og analyser

De 14 SAP-tabellene er ikke bare et datavedlegg — hver tabell har én konkret rolle i analysen:

| Tabell | Felt | Brukes til |
|---|---|---|
| MARA / MAKT | MATNR, MAKTX, MTART | Identifikasjon, populasjonsfilter |
| MARC / MARD | WERKS, LGORT, TOTAL_STOCK | Avgrensning til 3300/3001 |
| MBEW | STPRS, PEINH | UNIT_PRICE = STPRS / PEINH (D-02) |
| MSEG | BWART 201, 647 | Månedlig forbruk → CV-beregning (XYZ) |
| EKPO | NETWR | Faktisk innkjøpsverdi → ABC (foretrukket) |
| EKBE | Ordretelling | Faktisk ordrefrekvens → EOQ-avvik |
| EINE | PLIFZ | Leveringstid (dekker kun 6 % → D-05) |
| MDMA | ZZABC, ZZXYZ | Kryssvalidering (33 % samsvar = funn) |
| T023T / T024 | WGBEZ, EKGRP | Varegruppetekst og innkjøpsgruppe |

**To kritiske datavalg sensoren må forstå:**

1. **D-02 (PEINH-korrigering).** Hvis STPRS = 100 NOK og PEINH = 100, så er enhetsprisen 1 NOK/stk, ikke 100. Uten korrigering ville ABC-verdien blitt overestimert med faktor 100 for slike artikler — fullstendig ødelagt klassifisering.

2. **D-03 (beregnet ABC-verdi).** 204 av 709 artikler (28,8 %) mangler EKPO-data. For disse beregnes verdi som D_ANNUAL × UNIT_PRICE i stedet for faktisk NETWR. Antagelsen er at standardpris ≈ faktisk innkjøpspris. Dette er en *kjent svakhet* som diskuteres i kap. 8.2.

---

## 5. Kapittel 4–5 — Metode og modellering: formler i kontekst

### 5.1 ABC: ren rangerings­matematikk

$$v_i = D_i \times \text{UNIT\_PRICE}_i$$

$$C_i = \frac{\sum_{j=1}^{i} v_j}{V_{\text{tot}}}$$

- Sortér N=709 artikler synkende etter $v_i$.
- Klassifiseringsregel: A hvis $C_i \leq 0{,}80$, B hvis $0{,}80 < C_i \leq 0{,}95$, C ellers.

**Hvorfor 80/95 og ikke 70/90?** Sykehussortiment har en bredere "verdi-topp" enn industri pga. mange høyverdige spesialartikler. Empirisk ga 25,7 % A-andel (vs. kanonisk 20 %) — konsistent med Gupta et al. (2007).

### 5.2 XYZ: variasjonskoeffisient over tid

$$\text{CV}_i = \frac{\sigma_i}{\mu_i}$$

- $\sigma$ og $\mu$ beregnes over 24 månedlige forbruksverdier fra MSEG (BWART 201 + 647).
- Klassifiseringsregel: X hvis CV < 0,5, Y hvis $0{,}5 \leq \text{CV} < 1{,}0$, Z ellers.

**Hvorfor MSEG (forbruk) og ikke EKPO (innkjøp)?** HVFS skal levere etter *forbruksbehov* via APL. Bestillinger kan klumpe seg av administrative grunner uten at forbruket gjør det. CV på forbruk fanger den underliggende etterspørselsstabiliteten.

**Hvorfor 3 mnd. minimumskrav?** Mindre enn 3 observasjoner gir misvisende standardavvik (degenerate fordelinger). 22 artikler ekskluderes → MANGLER_DATA.

### 5.3 EOQ-avvik: Wilson-modellen brukt på frekvens, ikke kvantum

$$Q^* = \sqrt{\frac{2 D S}{H}}, \quad H = h \cdot \text{UNIT\_PRICE}$$

$$f^* = \frac{D}{Q^*} = \sqrt{\frac{D H}{2 S}}$$

$$TC(f) = f \cdot S + \frac{D}{2f} \cdot H$$

$$\text{FREQ\_AVVIK}_i = \frac{f_{\text{obs},i} - f^*_i}{f^*_i}$$

$$\Delta TC_i = TC(f_{\text{obs},i}) - TC(f^*_i)$$

**Hvorfor frekvens fremfor partistørrelse?** Ved overføring til HVFS er det *bestillingsfrekvensen* som endres operasjonelt — partistørrelsen er en konsekvens, ikke en handlingsvariabel.

**Hvorfor TC(f)-formelen?** Avledes fra at gjennomsnittlig lagernivå = $Q/2 = D/(2f)$. Holdekostnaden er $H \cdot D/(2f)$, og bestillingskostnaden er $S \cdot f$. Summen minimeres ved $f^*$.

**Hvorfor terskel $\tau_f = 1{,}5$ (= 50 % avvik)?** Skiller *operasjonelt* vesentlige avvik fra *statistisk* merkbare. EOQ-kostnadskurven er flat nær optimum — små avvik gir små besparelser. Terskelen er forfatterens skjønnsbeslutning, eksplisitt testet i sensitivitetsanalysen ($\tau_f \in \{1{,}25; 1{,}50; 2{,}00\}$).

### 5.4 K-means: datadrevet bekreftelse uten forhåndsterskler

$$\mathbf{x}_i = [\, z(\ln \text{CV}_i),\; z(\ln(v_i+1)),\; z(\ln(|\Delta TC_i|+1)) \,]$$

| Designvalg | Begrunnelse |
|---|---|
| Log-transformasjon | CV, $v$ og $\|\Delta TC\|$ er alle høyreskjevt fordelt — uten log dominerer ekstremverdier |
| Konstantledd +1 | Hindrer $\ln(0)$ for artikler med $\Delta TC = 0$ |
| Z-score (z) | Likestiller features med forskjellige enheter |
| Train/test 80/20, random_state=42 | Standardpraksis for reproduserbar generalisering |
| Silhouette-søk K ∈ {2..7} | Datadrevet K-valg; K=3 ga høyest score |
| K_OVERFØR via dobbelranking | $k^* = \arg\min_k[\text{rang}(\overline{\text{CV}}_k\uparrow) + \text{rang}(\overline{v}_k\downarrow)]$ — deterministisk |

**Silhouette: trening 0,383, test 0,368.** Differansen 0,015 er liten → modellen generaliserer akseptabelt. Begge over 0,3-terskelen for eksplorativ gyldighet.

**Hvorfor K-means når ABC/XYZ alt eksisterer?** Tre grunner:
1. Uten forhåndsdefinerte terskler — datapunktene grupperer seg selv.
2. Multivariat — fanger samspill mellom verdi, stabilitet og avvik som univariate analyser ikke ser.
3. Triangulering — når både regelbasert (ABC=A∧XYZ=X) og datadrevet (K_OVERFØR) gir samme signal (R4/R5), styrkes anbefalingen.

### 5.5 Regelmotor: sekvensiell prioritet med transparens

| Regel | Betingelse | Anbefaling | Antall |
|---|---|---|---|
| R1 | XYZ = Z | BEHOLD_LOKALT | 143 |
| R2 | ABC = C ∧ XYZ = Y | BEHOLD_LOKALT | 114 |
| **R3** | **A/B ∧ X ∧ FOR_MANGE_ORDRER** | **OVERFØR_HVFS** | **71** |
| **R4** | **A/B ∧ X ∧ K_OVERFØR** | **OVERFØR_HVFS** | **18** |
| **R5** | **A/B ∧ Y ∧ K_OVERFØR** | **OVERFØR_HVFS** | **56** |
| R6 | A/B ∧ X (ellers) | VURDER_NÆRMERE | 160 |
| R7 | A/B ∧ Y (ellers) | VURDER_NÆRMERE | 23 |
| R8 | Øvrig (inkl. CX) | VURDER_NÆRMERE | 101 |
| — | Manglende ABC/XYZ | MANGLER_DATA | 23 |

**Hvorfor R1 først?** Beskytter mot at høyvariable (ofte kritiske) artikler havner i OVERFØR. Z-override er en *frastøtingsregel* som har prioritet over alt annet.

**Hvorfor R3 sterkest?** Tre uavhengige signaler peker samme vei: høy verdi (ABC), stabilt forbruk (XYZ) og dokumentert overbestilling (EOQ). R3 gir ikke bare en anbefaling — den gir også et estimerbart kostnadsavvik.

**Hvorfor R4/R5 svakere enn R3?** Bare to regelbaserte signaler + ett klyngebasert. K-means bekrefter mønsteret datadrevet, men gir ingen direkte EOQ-kostnad å summere.

**Hvorfor 145 er konservativt?** Sekvensiell logikk betyr at en artikkel havner i den *strengeste* kategorien som passer. Hvis du tvilte mellom OVERFØR og VURDER, ble svaret VURDER. Resultat: høy presisjon (få falske positive), lavere recall (noen reelle kandidater i VURDER-bunken).

### 5.6 Besparelse: snitt mellom OVERFØR og FOR_MANGE_ORDRER

$$B_{\text{HVFS}} = \sum_{i \in \text{OVERFØR} \cap \text{FOR\_MANGE\_ORDRER}} \Delta TC_i \cdot g$$

**Hvorfor snitt og ikke alle 145?** $\Delta TC$ er *kun* definert for artikler med målbart frekvensavvik. R4/R5-artikler uten FOR_MANGE_ORDRER kan ha realisere besparelser via andre mekanismer (lagerbinding, transport), men disse modelleres ikke her. → Konservativt estimat.

**Hvorfor g (gevinstrealiseringsgrad)?** Skiller teoretisk optimum fra forventet realisering. Implementeringsfriksjon, leverandørforhandlinger, SAP MM-omkalibrering — alle absorberer en andel av den teoretiske besparelsen.

**Hvorfor tre scenarier?** Synliggjør usikkerheten eksplisitt i stedet for å skjule den i et punktestimat:

| Scenario | g | $B_{HVFS}$ |
|---|---|---|
| Worst | 50 % | kr 301 010 |
| Base | 75 % | kr 451 515 |
| Best | 100 % | kr 602 020 |

---

## 6. Kapittel 6 — Analyse: trinnvis spor fra rådata til 145

| Trinn | Filter | n |
|---|---|---|
| Rå-SAP (SE16H) | — | 1 006 |
| D-01 | D_ANNUAL > 0 ∨ TOTAL_STOCK > 0 | **709** |
| Klassifiserbare for ABC | UNIT_PRICE og verdigrunnlag | 704 |
| Klassifiserbare for XYZ | ≥ 3 mnd. forbruk | **687** |
| Med EOQ + K-means features | D > 0, UNIT_PRICE > 0, $\Delta TC$ definert | 487 |
| Train/test (80/20) | random_state=42 | 389 / 98 |
| OVERFØR_HVFS (regelmotor) | R3 ∨ R4 ∨ R5 | **145** |
| I besparelsesgrunnlag | + FOR_MANGE_ORDRER | **117** |

Hver overgang er en kontrollerbar filterregel. En sensor som vil etterprøve, kan kjøre `LOG650_analyse_v2_7.py` med samme `random_state=42` og få identiske tall.

---

## 7. Kapittel 7 — Resultater: tabellene som beslutningsgrunnlag

**Tabell 8 (ABC):** Fordelingen 25,7 / 26,0 / 47,7 % avviker bevisst fra Paretos klassiske 20/30/50. A-andelen er bredere fordi sykehussortiment har mange høyverdige spesialartikler (kirurgisk forbruksmateriell). Konsistent med Gupta et al. (2007) for SAP-implementering i sykehus.

**Tabell 9 + 10 (XYZ + kryssvalidering):** Kjernefunn — SAP klassifiserer **7** artikler som Z, mens analysen finner **79**. Samsvar 33 % (125 av 375). ZZXYZ er systematisk *underrapportert* fordi MDMA-feltet ikke oppdateres løpende. Dette er ikke bare en svakhet ved Helse Bergens SAP-vedlikehold — det er en empirisk dokumentasjon på hvorfor reproduserbar reklassifisering trengs.

**Tabell 11 (EOQ-avvik):** 73,1 % FOR_MANGE_ORDRER betyr at majoriteten av artikler bestilles vesentlig oftere enn EOQ tilsier. Dette er ikke nødvendigvis "feil" — det kan reflektere lagringsbegrensninger, forsyningssikkerhetspolitikk eller leverandørrutiner. Men det indikerer *strukturell* overbestilling som HVFS-sentralisering kan adressere via APL.

**Tabell 12 (K-means):**

| Klynge | n | CV | Verdi (kr) | $\|\Delta TC\|$ |
|---|---|---|---|---|
| 1 | 31 | 1,05 | 150 | 4 999 |
| 2 | 175 | 1,59 | 79 658 | 1 199 |
| **3 (K_OVERFØR)** | **281** | **0,47** | **167 267** | **7 005** |

Klynge 3 har lavest CV og høyest verdi → identifiseres deterministisk via dobbelranking som K_OVERFØR. Den datadrevne grupperingen *bekrefter* aksen som ABC og XYZ definerer regelbasert.

**Tabell 13/14 (regelmotor):** 145 = 71 (R3) + 18 (R4) + 56 (R5). Den klart sterkeste anbefalingsgruppen er R3 (71) — de eneste med alle tre signaler aktive.

**Tabell 15 (sensitivitet):** 27 kombinasjoner av (S, h, $\tau_f$) gir intervall kr 176k–764k. Dominante variabler:
- S har lineær effekt (dobling fra 500 → 1 000 nær dobler $\Delta TC$).
- $\tau_f$ påvirker antallet kandidater (lavere terskel → flere artikler, men mindre $\Delta TC$ per artikkel).
- h har moderat effekt.

**Robusthet:** Alle 27 scenarier gir positiv besparelse → konklusjonen om at HVFS-overføring er økonomisk rasjonell, holder under all rimelig parameterusikkerhet.

---

## 8. Kapittel 8 — Diskusjon: erkjente svakheter en sensor vil lete etter

| Svakhet | Hva den betyr | Hvordan den er mitigert |
|---|---|---|
| **Sirkularitet** | $\Delta TC$ inngår i både K-means features og besparelsesformel | K-means bruker $\|\Delta TC\|$ (signalstyrke); besparelse summerer signed $\Delta TC$ → ikke samme variabel matematisk |
| **Ingen ekstern validering** | Det finnes ingen "fasit" på riktig HVFS-portefølje ved Helse Bergen | Kan ikke beregnes presisjon/recall; anbefalt klinisk pilot (anbefaling 1 i kap. 9) |
| **VED ikke operasjonalisert** | Kritikalitet er ikke maskinlesbar i SAP | R1 (Z = BEHOLD) er proxy; klinisk gjennomgang kreves før implementering |
| **Parametre ikke kalibrert** | S, h, g er litteraturbaserte | Sensitivitetsanalyse over 27 scenarier viser robusthet |
| **D-03 (204 art. uten EKPO)** | ABC-verdi for disse er beregnet fra standardpris × forbruk | Antagelse om at STPRS ≈ faktisk innkjøpspris; eksplisitt dokumentert |
| **Wilson EOQ stasjonaritet** | Forutsetter konstant etterspørsel | X-artikler har per definisjon lav variasjon (CV < 0,5) → forutsetning relativt godt oppfylt der EOQ brukes operativt |
| **Snever besparelsesmodell** | Fanger kun transaksjonskostnader fra ordrefrekvens | Estimat er **konservativt** — lagerbinding (5–15 %), transport, engangskostnader er utenfor scope |
| **K-valg sensitivitet** | K=2 eller K=4 ville gitt andre klyngestrukturer | Silhouette-optimering er deterministisk; K=3 valgt empirisk |

**Sensorpoeng:** Forfatteren *erkjenner* svakhetene eksplisitt i stedet for å skjule dem. Dette er metodisk korrekt og styrker rapportens troverdighet.

---

## 9. Kapittel 9 — Konklusjon: hva problemstillingen faktisk besvarer

**Forskningsspørsmålet:**
> *Hvordan kan multidimensjonal klassifisering og klyngeanalyse av SAP-transaksjonsdata identifisere hvilke artikler ved Helse Bergen som er kandidater for overføring til HVFS, og hva er det estimerte besparelsespotensialet?*

**Kvalitativt svar (hvilke artikler):**
- 145 artikler, profilert per regel (R3/R4/R5) med eksplisitt signalmønster.
- Karakteristikk: A/B-verdiklasse, X/Y-stabilitetsklasse, dokumentert overbestilling eller K_OVERFØR-tilhørighet.
- *Rangert* fra SAP-data — reproduserbart med samme script.

**Kvantitativt svar (besparelsespotensiale):**
- *Intervall*, ikke punktestimat: kr 176 374 – kr 763 903/år.
- Base case kr 451 515/år (g = 75 %) er forventet midtverdi, ikke "svaret".
- Hvorfor intervall? Fordi sentrale parametre (S, h, g) er ekspertantagelser, ikke lokalt målt.

**Empirisk bifunn (uventet sideresultat):**
- ZZXYZ-feltet er systematisk feil — kun 33 % samsvar med beregnet CV-klasse.
- Dette har verdi *uavhengig av HVFS-spørsmålet* — det betyr at all SAP MRP-logikk som hviler på ZZXYZ ved Helse Bergen er upålitelig.

**Begrensningens kjerne:**
- *Identifisering* ≠ *implementering*. Uten aktiv SAP MM-justering (MRP-type, ordrekvantum, sikkerhetslager) realiseres ingen av de estimerte gevinstene.
- Klinisk validering (VED) må gjøres før noen artikkel faktisk overføres.

---

## 10. Vedlegg — etterprøvbarhet

**Vedlegg A (SAP-felter):** Spesifikasjonen er nødvendig for at en annen analytiker kan replikere studien på et annet WERKS uten å måtte gjette hvilke felter som ble brukt.

**Vedlegg B (Python):** `random_state=42` er ikke tilfeldig valgt — det er en de facto akademisk standard som sikrer at *enhver* som kjører scriptet får samme tall. Bibliotekversjoner (pandas 2.2.2, scikit-learn 1.4.2 osv.) er dokumentert for dependency-replikering.

**Vedlegg C (KI-erklæring):** Tre nivåer (kode / figurer / tekst) reflekterer HiMolde-retningslinjenes krav om eksplisitt deklarasjon av KI-bruk per kategori. Avgrensningene (rådata aldri lagt inn i KI-verktøy, ingen pasientdata) er kritiske for personvernkonformitet.

---

## 11. Sensorperspektiv: tre spørsmål som sannsynligvis kommer

**Q1: "Hvorfor regelmotor og ikke ren K-means-klassifisering?"**
- Triangulering: regelbaserte og datadrevne metoder validerer hverandre.
- Transparens: hver anbefaling kan spores til én spesifikk regel og ett spesifikt signalmønster — kritisk for tillit i kliniske beslutninger.
- Reviderbarhet: terskler i regelmotor kan justeres uten å trene K-means på nytt.

**Q2: "Hvorfor ikke kalibrere S og h lokalt?"**
- Omfangsbegrensning: lokal kalibrering ville krevd egen ABC-kalkyle av innkjøpsprosessens kostnader — utenfor en bachelorscope.
- Sensitivitetsanalysen kompenserer ved å vise at konklusjonen holder over et bredt parameterintervall.
- Fremtidig arbeid (kap. 9.3): lokal kalibrering anbefales som videre forskning.

**Q3: "Hva er den reelle besparelsen — 301, 452 eller 602 T?"**
- Ingen av dem alene. Det er et *intervall*.
- Base case 452 T er forventet midtverdi *gitt antagelsen* om at g = 75 %.
- Reell verdi vil avhenge av implementeringskvalitet: jo bedre SAP MM-justering og leverandørforhandlinger, desto nærmere best case.
- Det metodisk korrekte svaret er: "kr 451 515/år base case, intervall kr 176k–764k under varierende parametre."

---

## Sammenfattet logisk flyt (oppsummering)

1. **Praksisproblem:** Helse Bergen mangler datadrevet beslutningsgrunnlag for HVFS-overføring.
2. **Datagrunnlag:** 14 SAP-tabeller via SE16H, 24 mnd., 1 006 → 709 artikler etter D-01.
3. **Tre regelbaserte analyser:** ABC (verdi), XYZ (stabilitet), EOQ-avvik (kostnadseffektivitet) — hver dekker én dimensjon med kjente svakheter.
4. **Én datadrevet validering:** K-means (K=3) — bekrefter regelbasert akse uten forhåndsterskler.
5. **Regelmotor (R1–R8):** Sekvensiell prioritet → 145 OVERFØR, 257 BEHOLD, 284 VURDER, 23 MANGLER.
6. **Besparelse:** 117 av 145 har FOR_MANGE_ORDRER → $B_{HVFS}$ = kr 451 515 (base case).
7. **Sensitivitet:** 27 scenarier gir kr 176k–764k — alle positive.
8. **Konklusjon:** Identifisering levert med metodisk transparens; gjennomføring forutsetter klinisk validering og SAP MM-justering.

**Rapportens kjernebudskap:**
> Datadrevet klassifisering kan systematisk identifisere HVFS-kandidater fra SAP-transaksjonsdata, og estimere et robust besparelsespotensiale. Men identifisering er bare første trinn — verdien realiseres først gjennom klinisk validering, SAP-omkalibrering og operasjonell implementering.
