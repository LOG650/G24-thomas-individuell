# Kvantitative metoder i logistikk – Kompendium 2026

> Kilde: <https://kml-site-production.up.railway.app/>
> Forfattere: Per Kristian Rekdal og Bård-Inge Pettersen
> Kurs: LOG 650 – Forskningsprosjekt: Logistikk og kunstig intelligens
> Utgivelsesår: MMXXVI (2026), Høgskolen i Molde
> Sammendrag: Thomas Ekrem Jensen, april 2026

---

## Forord og overordnet filosofi

Kompendiet retter seg mot studenter i sluttfasen av et logistikkstudium som gjennomfører selvstendige forskningsprosjekter der kvantitative metoder kombineres med anvendelser av kunstig intelligens (KI).

**Forutsetninger:** grunnleggende erfaring med Python og statistikk. Vekten ligger på modellering og analytisk dømmekraft fremfor verktøyopplæring.

**Filosofi:** *«KI brukes eksplisitt som støtte i utvikling og implementering av kvantitative modeller — ikke som en erstatning for faglig vurdering.»* Målet er å utvikle analytisk skjerpede logistikkstudenter som kan integrere fagkunnskap, kvantitative metoder og samtidens KI-anvendelser.

**Struktur:** Kompendiet er delt i tre deler:

- **Del I (Innledning):** etablerer fem grunnbegreper – område, problemstilling, modell, prosess og metode – og hvordan KI integreres i arbeidsflyten.
- **Del II (Områder):** anvender rammeverket på elleve logistikkområder, med 33 gjennomarbeidede eksempler.
- **Del III (Vedlegg):** Python-kodebibliotek og sjekklister.

---

# Del I – Innledning

## Kapittel I: De fem begrepene

Hierarki: **Område → Problemstilling → Modell → Prosess (med Metoder)**. Hvert steg bygger på det forrige; mangler ett steg, smuldrer hele kjeden.

### 1. Område

Et område angir fagfeltet eller sektoren prosjektet fokuserer på, og setter grenselinjer for problemomfanget. Kompendiet dekker 11 områder:

| # | Område | Kjerne |
|---|--------|--------|
| 1 | Etterspørselsprognoser | Predikere fremtidig salg fra historiske mønstre |
| 2 | Lagerstyring | Bestillingsmengder og bestillingstidspunkt |
| 3 | Produksjonsplanlegging | Kapasitetsallokering og sekvensering |
| 4 | Nettverksdesign | Lokalisering av distribusjonssentre og lagre |
| 5 | Forsyningskjedeanalyse | Integrering av leverandører, produksjon, distribusjon |
| 6 | Kø-teori | Dimensjonering av tjenestepunkter, ventetider |
| 7 | Lagerdrift | Plukkprosesser og lageroppstilling |
| 8 | Bærekraftig logistikk | Reduksjon av miljøpåvirkning |
| 9 | Returlogistikk | Returer og sirkulær økonomi |
| 10 | Innkjøpsoptimalisering | Leverandørvalg og avtaleforhandlinger |
| 11 | Risikostyring | Sikkerhetslager og leverandørrobusthet |

### 2. Problemstilling

Formulerer i prosa hvilket konkret utfall prosjektet skal oppnå.

**Kjennetegn på en god problemstilling:**

- **Spesifikk** – nøyaktig avgrenset
- **Målbar** – kan kvantifiseres eller verifiseres empirisk
- **Relevant** – har praktisk betydning
- **Forståelig** – kan formidles uten matematisk språk

**Eksempler:**

| Område | Typisk problemstilling |
|--------|------------------------|
| Etterspørsel | Hva blir forventet salg av produkt X neste måned? |
| Lager | Hvor mye bør vi bestille, og når skal bestilling skje? |
| Produksjon | Hva er optimal produksjonsmengde for kostnadsminimering? |
| Nettverk | Hvor lokaliseres nytt distribusjonssenter for laveste transportkostnad? |
| Kapasitet | Hvor mange servere må være operative for ventetid under 5 minutter? |
| Bærekraft | Hvordan reduseres CO₂-utslipp med 20 % uten kostnadsøkning? |
| Innkjøp | Hvilken leverandør velges på basis av pris, kvalitet og leveringssikkerhet? |

### 3. Modell

En modell representerer problemstillingen i matematisk språk. Fire komponenter:

| Komponent | Spørsmål | Eksempel (EOQ) |
|-----------|----------|----------------|
| Parametre | Hva vet vi på forhånd? | D, K, h |
| Variabler | Hva kan vi velge? | Q |
| Målfunksjon | Hva ønsker vi å oppnå? | Min TC(Q) = (D/Q)·K + (Q/2)·h |
| Føringer | Hvilke regler gjelder? | Q > 0 |

EOQ-modellen forutsetter konstant etterspørsel, ingen leveringstid og ingen volumrabatter.

### 4. Prosess

Den systematiske fremgangsmåten i fem steg:

1. **Datainnsamling** – historiske, operasjonelle, markeds- og finansielle data. Kritisk: kvalitet, fullstendighet, relevans, aktualitet.
2. **Sjekk av antagelser** – statistiske hypotesetester, grafisk visualisering, fagvurdering, sensitivitetsanalyse.
3. **Løsning** – analytisk, numerisk, simulering eller heuristikk.
4. **Sjekk av løsning** – realitetssjekk, benchmarking, sensitivitet, pilottesting.
5. **Anvendelse** – implementering, vedvarende oppdatering, overvåking, dokumentasjon.

Prosessen er syklisk: læring kan kreve tilbakegang til tidligere steg.

### 5. Metoder

Metoder definerer *hvordan*, mens prosessen definerer *hva*.

| Forkortelse | Metode |
|-------------|--------|
| LP | Lineær programmering (Simplex, indre-punkt) |
| HP | Heltallsprogrammering (branch-and-bound, branch-and-cut) |
| DP | Dynamisk programmering (Bellman, verdiiterasjon) |
| Sim | Simulering (Monte Carlo, diskret hendelse, agentbasert) |
| Kø | Køteori (M/M/1, M/M/c, kønettverk) |
| Net | Nettverksoptimering (korteste sti, min-cost flow) |
| Heu | Heuristikker (genetiske algoritmer, tabu, simulert gløding) |
| Tid | Tidsrekkeanalyse (ARIMA, eksponentiell glatting) |
| Lag | Lagerstyringsmodeller (EOQ, bestillingspunkt, newsvendor) |
| Mul | Multikriterie (AHP, TOPSIS, ELECTRE, PROMETHEE) |
| ML | Maskinlæring (nevronnett, random forest, gradient boosting) |
| ABC | Klassifisering (Pareto, XYZ, kombinert) |

---

## Kapittel II: Arbeidsflyt og KI

De fem begrepene henger sammen i en kjede der hvert steg bygger på det forrige. Uten klart definert område er presis problemformulering umulig; uten problemstilling kan man ikke utvikle relevant modell; uten modell mangler prosess og metoder strukturelt fundament.

**Praktisk eksempel – lagerstyring:**

| Begrep | Anvendelse |
|--------|------------|
| Område | Lagerstyring |
| Problem | Optimal bestillingsmengde og tidspunkt for produkt X |
| Modell | EOQ med etterspørsels- og kostnadsparametre |
| Prosess | Fem steg fra datainnsamling til implementering |
| Metoder | ERP-eksport, statistisk testing, analytisk løsning, sensitivitet, dashboarding |

**KI sin rolle:** Tradisjonelt krevdes dyp matematisk kunnskap og programmeringsferdigheter. KI endrer kravsbildet ved å muliggjøre kompleks problemløsning uten mestring av alle tekniske detaljer. Brukeren må utvikle høy-nivå styringskompetanse:

- forstå hvilke metoder som passer til hvilke problemer,
- formulere problemstillinger klart nok for KI-assistanse,
- vurdere om KI-genererte resultater er rimelige,
- styre KI-prosesser uavhengig av full teknisk innsikt,
- brainstorme sammen med KI for å utforske nye løsninger.

---

## Kapittel III: Prosjektgjennomføring med KI

### Rollefordeling

| Studenten har ansvar for | KI bidrar med |
|--------------------------|---------------|
| Valg av område og problemstilling | Foreslår metoder og tilnærminger |
| Skaffe og evaluere data | Behandler og analyserer data |
| Velge metode og validere resultater | Bygger modeller, koder og løser |
| Kvalitetssikring og presentasjon | Genererer rapporter og visualiseringer |

> «Du har ansvar for de faglige valgene og kvalitetssikringen, mens KI fungerer som et kraftig verktøy for analyse, koding og dokumentasjon.»

### Fire prosjektfaser

| Fase | Innhold | Leveranse |
|------|---------|-----------|
| 1 – Initiering | Område, problemstilling, metode | Godkjent prosjektbeskrivelse med KI-integrasjonsplan |
| 2 – Planlegging | Kravspesifikasjon, oppgavelisten, datakilder, etikk, risiko | Godkjent prosjektplan med metodevalg |
| 3 – Gjennomføring | Datainnsamling → modell → Python-kode (KI-assistert) → validering | Godkjent rapportutkast |
| 4 – Avslutning | Rapportskriving, visualisering, kvalitetsgjennomgang, presentasjon | Endelig rapport og fremlegg |

---

# Del II – Områder

## Kapittel 1: Etterspørselsprognoser

**Område:** Forutsi fremtidig etterspørsel på kortsiktig (dager–uker), mellomlang (måneder) og langsiktig (år) horisont, som grunnlag for lager-, produksjons- og transportplanlegging.

**Fem hovedutfordringer:**

1. Trend og sesong – klassiske mønstre via SARIMA
2. Eksterne faktorer – kampanjer via ARIMAX
3. Mange variabler – ikke-lineære sammenhenger via LightGBM
4. Sporadisk etterspørsel – uregelmessige serier
5. Komplekse sekvenser – LSTM/Transformer

### Modell – SARIMA

φ_p(B)·Φ_P(B^m)·∇^d·∇_m^D Y_t = θ_q(B)·Θ_Q(B^m)·ε_t

Box-Jenkins-prosess: data → ADF-stasjonaritetstest → ACF/PACF → MLE → Ljung-Box → prognose. Eksempel: traktorsalg modelleres som SARIMA(1,1,1)(0,1,1)₁₂.

### Modell – ARIMAX

φ_p(B)·Φ_P(B^m)·∇^d·∇_m^D (Y_t − β'X_t) = θ_q(B)·Θ_Q(B^m)·ε_t

Feature engineering konstruerer syv variabler for kampanje, rabatt, pre-buying og post-campaign-dipper. NordMat-eksempel: MAPE faller fra 7,2 % til 3,0 %.

### Modell – LightGBM

Ensemble av 1 781 beslutningstrær på ~90 features tvers 50 SKU-er. MAPE 25,7 % på testsett mot 67 % for SARIMA. SHAP-verdier dekomponerer hver prediksjon; «SKU-spesifikk ukedag-gjennomsnitt» og «salg samme dag forrige uke» dominerer.

**Praktisk valg:** SARIMA for enkle stasjonære serier, ARIMAX for planlagte interventioner, gradient boosting for komplekse paneler.

---

## Kapittel 2: Lagerstyring

**Område:** Balansere produkttilgjengelighet mot lagerholdkostnad. Strategiske, taktiske og operative beslutninger om bestillingspolitikk og sikkerhetslager.

### Problemstilling 1 – Multi-produkt (Q,R) med felles ressurser

Optimalt bestillingskvantum med Lagrange-multiplikatorer (skyggeprisen for volum og kapital):

$$Q_i^* = \sqrt{\frac{2D_i(K_i + π_i σ_{DL,i} L(k_i))}{h_i c_i + λ_V v_i + λ_B c_i}}$$

**Resultat:** +17,8 % kostnad mot ubegrenset uavhengig løsning, men 95 % servicenivå oppnås innenfor volum- og budsjettrammer.

### Problemstilling 2 – Multi-lokasjon med lateral transshipment

To-trinns stokastisk lineært program: stage 1 bestiller før etterspørsel, stage 2 omfordeler etter realisert etterspørsel. **Resultat:** 68 % kostnadsreduksjon, fyllingsgrad 77 % → 99 %.

### Problemstilling 3 – Datadrevet klassifisering

LightGBM på 36 features (volum, variabilitet, pris, ledetid, holdbarhet, kampanjefrekvens) erstatter manuell ABC-XYZ for 2500 SKU-er. **Macro-F1: 0,92 mot 0,54;** simulert besparelse 12,6 MNOK/år (21 %).

| Problemstilling | Modell | Resultat |
|---|---|---|
| Multi-produkt | (Q,R) + Lagrange | Servicenivå 95 % oppnådd |
| Multi-lokasjon | To-trinns stokastisk LP | −68 % kostnad |
| Klassifisering | LightGBM | F1 0,92, −21 % kostnad |

---

## Kapittel 3: Produksjonsplanlegging og -styring

**Definisjon:** Bestemme hva som skal produseres, i hvilken mengde, når og med hvilke ressurser for å dekke etterspørsel til lavest totalkostnad under kapasitets- og materialskranker.

**Tre planleggingshorisonter:** aggregert (måneder), master (uker, MPS), detalj (dager/timer).

### Problemstilling 1 – Aggregert planlegging via LP

Båtprodusent med sesongtopper. Beslutningsvariabler: regulær produksjon Pₜ, overtid Oₜ, lager Iₜ, ansettelser Hₜ, oppsigelser Fₜ.

$$\min \sum_t (c^P P_t + c^O O_t + c^I I_t + c^H H_t + c^F F_t)$$

**Resultat:** Bygger lager (49 båter april–mai), bruker overtid kun i topp (8 båter august), konstant arbeidsstyrke. Totalkostnad 11,4 MNOK/år. Chase-strategi koster 46 % mer. Skyggepris: 11 000 NOK per ekstra båt i sesong.

### Problemstilling 2 – Sekvensering (1|s_ij|ΣwⱼTⱼ)

CNC-maskin, 6–50 ordre med vekt, frist og oppsettstider. Binærvariabler y_ij angir at jobb j følger jobb i.

| N | Metode | Vektet forsinkelse |
|---|--------|--------------------|
| 6 | MIP (CBC) | 7,97 (optimal) |
| 6 | ATC | 28 % gap |
| 50 | ATC | 329 |
| 50 | ATC + Simulert gløding | 86 (–73,9 %, 23 s) |

Dispatch-regler: SPT, EDD, ATC (dynamisk balanse av vekt, behandlingstid, slack).

### Problemstilling 3 – MRP med lot-sizing

Sykkelprodusent, 12-ukers plan, BOM-eksplosjon. Sammenligning av politikker:

| Policy | Ordre | Oppsett | Holdkostnad | Total |
|--------|-------|---------|-------------|-------|
| Lot-for-lot | 64 | 7 070 kr | 0 | 7 070 kr |
| EOQ | 33 | 3 690 kr | 2 357 kr | 6 047 kr |
| **Silver-Meal** | 30 | 3 340 kr | 772 kr | **4 112 kr** |

Silver-Meal forlenger dekningsperioden mens gjennomsnittskostnad faller. Sparer 42 % vs. lot-for-lot.

---

## Kapittel 4: Nettverksdesign og optimering

**Område:** Strategiske 5–10-årsbeslutninger om plassering av fasiliteter, kundetildelinger og transportmodus. Tre nivåer: strategisk struktur, taktisk allokering, operativ ruteplanlegging.

### Problemstilling 1 – UFLP (ukapasitert fasilitetslokalisering)

Binærvariabler y_i (åpne lager), kontinuerlige x_ij (kundeallokering). Min: faste åpningskostnader + variable transportkostnader.

**Eksempel:** Skandinavisk netthandler, 3 av 15 DC-kandidater. Optimal løsning: Bergen, Örebro, Umeå. Totalkostnad 20,4 MNOK/år. Robust ±50–100 % i faste kostnader.

### Problemstilling 2 – CVRP (kapasitert ruteplanlegging)

MTZ-formulering: binære x_ij + kumulativ last u_i for å eliminere subsykler.

| Metode | Gap til optimum |
|--------|-----------------|
| Nærmeste-nabo | ~39 % |
| Clarke–Wright | <1 % på små instanser |
| 2-opt forbedring | – |
| Eksakt MIP | 0 % (N ≤ 20–25) |

Oslo hjemlevering, 15–40 kunder: Clarke–Wright reduserer distansen 28–30 % vs. nærmeste-nabo.

### Problemstilling 3 – ML-basert ruteoptimering

Attention-basert pointer-nettverk (~25 000 parametere) trent på 1 200 løste CVRP-instanser. Encoder lager node-embeddings, decoder konstruerer rute autoregressivt.

**Resultater:** 5,7 % gap til optimum in-distribution (N=5–7), eksakt optimum i 31 % av tilfellene. Generaliserer dårlig (gap 20 % på N=20). Hybrid anbefales når optimalitetsgaranti kreves.

---

## Kapittel 5: Forsyningskjedeanalyse og -optimering

**Område:** Verdikjeden som ett integrert system der beslutninger forplanter seg. Dekker bullwhip-effekten, sentralisering, koordineringsmekanismer og multi-echelon lagerstyring.

### Problemstilling 1 – Bullwhip-effekten

4-trinns dagligvarekjede simulert med (s,S)-policy + eksponentiell glatting.

| Tilstand | Bullwhip-ratio | Sparing |
|----------|----------------|---------|
| Desentralisert | 437,5 | – |
| Med informasjonsdeling | 59,6 | 86 % redusert |
| Totalkostnad-effekt | – | −56,7 % |

**Hovedfunn:** Informasjonsdeling bryter amplifikasjonen mer enn kort ledetid alene.

### Problemstilling 2 – Multi-echelon (Clark–Scarf)

Farmasidistributor, 1 sentrallager + 4 regionale hub-er. Echelon base-stock: hver node løser uavhengig newsvendor med inkrementell holdkostnad.

| Indikator | Uavhengig | Clark–Scarf |
|-----------|-----------|-------------|
| Installasjonslager | 2 735 enh | 1 010 enh |
| Årskostnad | 3 408 kNOK | 982 kNOK (−71 %) |
| Servicenivå | ~99,9 % | ~99,9 % |

**Hovedfunn:** Clark–Scarf er bemerkelsesverdig flat i ledetid; uavhengig eksploderer.

### Problemstilling 3 – Newsvendor og revenue-sharing

Motekjede, vinterjakker. Kritisk forhold α = (p−c)/(p−s) = 0,846. Engrospris gir double marginalization. Kontrakt (φ=0,5, w′=200): detaljisten beholder φ av omsetning, betaler redusert pris w′ = φ·c.

| Metric | Engrospris | Revenue-sharing |
|--------|-----------|-----------------|
| Bestilling | 976 | 1 255 (+28 %) |
| Detaljist | baseline | +8,6 % |
| Leverandør | baseline | +4,8 % |
| Kjede | baseline | +6,7 % |

Pareto-intervall: φ ∈ [0,47; 0,52]. Begge parter tjener mer.

---

## Kapittel 6: Kø-teori og kapasitetsplanlegging

**Kendall-notasjon:** A/S/c/K/N/D – ankomst, servicetid, antall servere, kapasitet, populasjon, disiplin.

### M/M/1 – analytiske formler (ρ = λ/μ < 1)

| Størrelse | Formel |
|-----------|--------|
| L (i system) | ρ/(1−ρ) |
| Wq (ventetid) | ρ/(μ−λ) |
| Lq (i kø) | ρ²/(1−ρ) |

**Kritisk:** Ventetiden eksploderer hyperbolsk når ρ → 1. Wq ved ρ=0,90 er 9× verdien ved ρ=0,50.

### M/M/c og Erlang-C

C(c, a) = sannsynlighet for at ankomstende kunde treffer alle servere opptatte. Halefordelingen P(Wq > t) løses for minste c som oppfyller P(Wq > t*) < α.

**Avveining:** c_serv (servicekrav) vs. c_kost (driftskostnad). Velg max(c_serv, c_kost).

### Komplekse nettverk (SimPy)

Prosess: data → grunnmodell → basissimulering (5000+ enheter) → flaskehalsanalyse → what-if → KPI-sammenligning.

**Eksempelresultater:**

- Tollstasjon (M/M/1): krav W ≤ 5 min krever ρ ≤ 0,50; dagens 0,67 bryter krav.
- Containerterminal (M/M/c): P(Wq > 10 min) < 5 % krever c=3 kraner.
- E-handelssentral: pakking er flaskehals (54 % av gjennomløpstid); en tredje pakker halverer ventetid.

**Hovedfunn:** Reduksjon av variabilitet ved ikke-flaskehals kan forverre total gjennomløpstid; tiltak må rettes mot flaskehalsen.

---

## Kapittel 7: Lagerdrift og ordreplukk

**Område:** Vareflyt fra mottak til utsending. Plukking utgjør typisk 50–60 % av driftskostnadene i manuelle lagre.

### Problemstilling 1 – Slotting (class-based storage)

70/20/10-regelen: 70 % hyppigste varer i nærsone, 20 % i midtsone, 10 % i fjernsone. Forventet reisedistanse: E[d|σ] = (Σf_i d_σ(i))/(Σf_i).

**FreshFlow:** 400 lokasjoner. Forventet plukkdistanse fra 51,0 m (tilfeldig) til 26,1 m (klassebasert) – 48 % reduksjon, 805 t spart per plukker årlig.

### Problemstilling 2 – Plukkruteoptimering

| Heuristikk | Snitt (m) | Gap til optimum |
|------------|-----------|-----------------|
| S-shape | 275,52 | 17,84 % |
| Largest-gap | 249,26 | 5,92 % |
| Return | 329,91 | 40,36 % |
| Ratliff–Rosenthal DP | 235,08 | 0 % |

Largest-gap unngår største tomme segment i hver gang. NordDel: 9,5 % kortere distanse vs. S-shape; 1–2 km spart per plukker per skift.

### Problemstilling 3 – Integrert bølge-, batch- og ruteplanlegging

Hierarkisk dekomponering:

1. **Bølge-MIP:** tidsindeksert heltallsprogram, fordeler ordre på bølger med deadline og pakkekapasitet.
2. **Batching (k-medoids):** klyngedanning på plukklokasjonsnærhet.
3. **Ruting (largest-gap):** rute per batch.

| Tilnærming | Deadline-overholdelse |
|------------|----------------------|
| FIFO baseline | 81,6 % |
| Bølge-MIP | 92,4 % |
| Full integrasjon | 94,8 % |

Pakkekølengde redusert fra 1,45 til 0,34 batcher.

---

## Kapittel 8: Bærekraftig logistikk

**Område:** Måle, modellere og redusere CO₂-utslipp, energiforbruk og avfall. Transportsektoren står for ~25 % av globale CO₂. Drivere: EU-regulering (CSRD, ETS), kundeforventninger, karbonprising.

**Rammeverk:**

- **GHG Scope 1/2/3** (direkte / innkjøpt energi / verdikjede)
- **Livssyklusanalyse (LCA)** fra råvare til avhending

### Problemstilling 1 – Green VRP

Lasteavhengig utslippsfunksjon e(w) = α + βw. EcoTrans Oslo, 25 leveranser. Modifisert Clarke–Wright på CO₂ + 2-opt + Pareto. **Resultat: 3,8 % CO₂-reduksjon uten kostnadsøkning.**

### Problemstilling 2 – Bin packing

NordPakk, 80 produkter daglig, 72 l / 25 kg-esker.

| Metode | Esker brukt |
|--------|-------------|
| Naiv First-Fit | 24 |
| First-Fit Decreasing | 23 |
| Best-Fit Decreasing | 23 |

En spart eske daglig = 250 esker årlig = 32,5 t CO₂e og 350 000 NOK.

### Problemstilling 3 – Stokastisk flermål-MIP

NorDistrib AS, 6 DC-kandidater, 3 transportmoduser, 50 kunder. To-trinns SP, scenario-reduksjon (300→10) via Kantorovich, epsilon-constraint Pareto-front.

| Løsning | Kostnad | CO₂ |
|---------|---------|-----|
| Min-kostnad | 1,21 MEUR | 200 t/år (2 DC) |
| Min-utslipp | 3,37 MEUR | 24 t/år (6 DC) |
| **Knee-point** | **1,62 MEUR** | **95 t/år (3 DC)** |

Knee-løsning: 53 % utslippsreduksjon for 34 % kostnadsøkning. **Tipping-punkt:** mellom 125 og 150 EUR/tonn karbonpris skifter optimal modus fra 100 % lastebil til 93 % jernbane.

---

## Kapittel 9: Returlogistikk og sirkulære kjeder

**Område:** Bakovergående vareflyt: garanti, e-handelsreturer, ende-av-liv, emballasje, refurbishment. Sluttede sløyfer der brukte produkter gjenvinnes.

### Problemstilling 1 – Reverse network design (MIP)

EE-avfall i Norge: 40 kundegrupper → samlesentre → 3 gjenvinningsanlegg. Flertrinns kapasitert facilitetslokalisering, binære + kontinuerlige variabler.

**Resultat:** Åpne 5 samlesentre (Drammen, Kristiansand, Stavanger, Hamar, Bodø) + 2 gjenvinningsanlegg (Grenland, Mo i Rana). Totalkostnad 53,8 MNOK/år. Behandling dominerer (39,4 %), ikke transport (12,2 %).

### Problemstilling 2 – Returprognose med Weibull

Ruterleverandør, 48 mnd salgs- og returhistorie. Weibull W(β, η) estimert via MLE med høyrecensurering, konvolvert med salgshistorie.

**Estimert:** β̂ = 2,20 (økende hazard, slitasje), η̂ = 18,07 mnd. 84,5 % feiler innen 24-mnd-garanti. 12-mnd prognose: ~15 445 returer (95 % CI: 15 375–15 514). Backtest MAPE 1,0 %.

### Problemstilling 3 – Disposisjonsbeslutning

EV(a|x) = p_a(x)·r_a(x) − k_a − (1−p_a(x))·ℓ_a. CART-tre lært på oracle-optimale beslutninger.

| Strategi | Verdi vs. oracle |
|----------|------------------|
| Alltid resirkuler | baseline |
| Cut-off på tilstandsskår | 98,4 % av oracle |
| Lært tre | 99,3 % |

Refurbish blir dominerende handling for ~49 % av enheter; +351 % verdi vs. baseline.

---

## Kapittel 10: Innkjøpsoptimalisering og leverandørstyring

**Område:** Innkjøp utgjør 50–80 % av omsetningen. Strategisk (segmentering, sourcing), taktisk (kontrakter, TCO), operativt (mengder, rabatter), auksjoner (kombinatoriske bud).

### Problemstilling 1 – Leverandørvalg (AHP + TOPSIS)

**AHP** etablerer vekter fra parvise sammenligninger; konsistensforhold CR < 0,10.
**TOPSIS** rangerer på geometrisk avstand til ideell og anti-ideell løsning.

Prosess: data → AHP-vekter → TOPSIS → rangering via C_i ∈ [0,1] → sensitivitet (vekter ±20 %) → anbefaling.

**Eksempel:** Nordvik Industri, 6 leverandører. Epsilon vinner (C_i = 0,712), så Gamma (0,700), Alfa (0,649). Robust under vektvariasjoner.

### Problemstilling 2 – Kvantumsrabatt (utvidet EOQ)

$$TC(Q) = c·D + (D/Q)·K + (Q/2)·h, \quad Q^* = \sqrt{2DK/h}$$

To rabattformer:

- **All-units:** hele ordren får intervallpris
- **Incremental:** kun enheter over grensen får rabatt

Beregn EOQ per intervall, klassifiser indre/hjørne/ugyldig, velg lavest TC.

**NordTek Engros:** Q* = 500 (mot klassisk EOQ ≈ 104) på elektroverktøy → 8,1 % besparelse. Fire produkter samlet: 359 100 NOK/år (9,82 %).

### Problemstilling 3 – Innkjøpsauksjon (Winner Determination)

Binært heltallsprogram:

$$\min \sum_{b} p_b x_b \quad \text{s.t.} \quad \sum_{b: k \in K(b)} x_b = 1 \forall k$$

Diversifisering: Σ p_b x_b ≤ α_max · C_øvre per leverandør.

**Nordbygg Entreprenør:** 8 kategorier, 4 leverandører, 24 bud (18 enkle + 6 bundles).

| Tilnærming | Kostnad |
|------------|---------|
| Naiv (laveste pris per kategori) | 13,353 MNOK |
| **MIP-optimal** | **12,789 MNOK (−4,2 %)** |
| MIP m/diversifisering α_max=0,50 | 12,835 MNOK (+0,36 %) |

Robust mot leverandørbortfall (+0,78 %); aggressiv ny bundle kan redusere −1,94 %.

---

## Kapittel 11: Risikostyring og robusthet

**Definisjon:** Identifisere, kvantifisere og håndtere hendelser som kan forstyrre flyt. To kategorier:

- **Forstyrrelsesrisiko** – sjeldne, høy-impact (konkurs, havneblokade)
- **Operasjonell risiko** – hyppige variasjoner (etterspørsel, ledetid)

### Problemstilling 1 – Monte Carlo, VaR/CVaR

Norsk importør, asiatisk leverandør:

- D ~ N(12 000, 2 000²)
- L ~ LogN(ln 35, 0,30²)
- F ~ Bernoulli(0,08)

N=10 000 kjøringer:

| Mål | Verdi (NOK) |
|-----|-------------|
| Forventet kostnad | 268 353 |
| 95 %-VaR | 693 609 |
| 95 %-CVaR | 840 718 |

**Tornado-analyse:** dual sourcing reduserer CVaR med 36 %; økt sikkerhetslager bare 8 %. Strukturelle tiltak slår operasjonelle buffere.

### Problemstilling 2 – Robust nettverksdesign

Nordic Seafood, 4 hubs, ±41 % etterspørselsuusikkerhet på 25 markeder. To-trinns LP:

- Stage 1: kapasitet z (here-and-now)
- Stage 2: ruting + spot (wait-and-see)

| Beslutningskriterium | Kapasitet (t) | Worst-case |
|---------------------|---------------|------------|
| Deterministisk | 8 200 | 1,8 MNOK overskridelse |
| Stokastisk (50 scenarier) | 8 667 | moderat |
| **Robust minimax regret** | **9 126** | **−16 % worst-case (5,9 % premium)** |

Robust løsning allokerer overraskende mye til billige Tromsø (2 376 t) som hedge.

### Problemstilling 3 – Stresstesting (NordMed)

3-trinns nettverk, 5 scenarier:

| Scenario | Servicenivå | Kostnadsøkning |
|----------|-------------|----------------|
| Pandemi | 55 % | +184 MNOK |
| Havneblokade | 76 % | +84 MNOK |
| Leverandørkonkurs | 54 % | +140 MNOK |
| Naturkatastrofe | 83 % | +63 MNOK |
| Cyberangrep | 59 % | +118 MNOK |

Forventet årskostnad: 74,8 MNOK (12× baseline).

**Tiltak rangert:**

| Tiltak | Netto-gevinst |
|--------|---------------|
| M₂ Alternativ leverandør | +28,8 MNOK (CB-ratio 25) |
| M₃ Nearshoring (60 % volum) | +9,2 MNOK |
| M₄ Dual sourcing 50/50 | +7,7 MNOK |
| M₁ +50 % sikkerhetslager | −2,4 MNOK (kontraproduktivt) |
| M₅ +25 % fleksibel kapasitet | −0,8 MNOK |

**Hovedfunn:** «Diversifiser mot din største strukturelle avhengighet» – kildeendring slår lagerbuffere.

---

# Del III – Vedlegg

## A.1 Python-kodebibliotek (33 eksempler)

Hver eksempel-pakke inneholder typisk seks Python-filer (`step01_datainnsamling.py` … `step06_prognose.py`/`anbefaling.py`) og bruker UV som dependency manager (Python ≥ 3.12).

| Kapittel | Eksempler |
|----------|-----------|
| 1 Etterspørsel | SARIMA, ARIMAX, LightGBM (m/SHAP) |
| 2 Lager | Multi-produkt (Q,R) m/Lagrange, multi-lokasjon to-trinns SP, ML-klassifikasjon |
| 3 Produksjon | Aggregert LP, sekvensering MIP/SA, MRP m/lot-sizing |
| 4 Nettverk | UFLP, CVRP, ML-pointer-nettverk |
| 5 SC-analyse | Bullwhip 4-trinn, Clark–Scarf, newsvendor + revenue-sharing |
| 6 Kø | M/M/1, M/M/c (Erlang-C), SimPy-nettverk |
| 7 Lagerdrift | Class-based slotting, plukkruter (5 metoder), bølge-batch-ruting |
| 8 Bærekraft | Green VRP, bin packing (FFD/BFD/2D), flermål-stokastisk MIP |
| 9 Retur | Reverse network MIP, Weibull-prognose, disposisjon m/CART |
| 10 Innkjøp | AHP+TOPSIS, EOQ m/rabatt, WDP-auksjon |
| 11 Risiko | Monte Carlo VaR/CVaR, robust LP, stresstesting |

> NB: Lenker til appendiks A.1 *Sjekklister* og A.2 *Typer av oppgaver* var utilgjengelige (404) ved opphenting; disse delene mangler i sammendraget.

---

# Oppsummering – metode-til-område-matrise

| Metode | Bruk i kompendiet |
|--------|-------------------|
| LP / MIP | Kap. 3 (aggregert), 4 (UFLP, CVRP), 7 (bølge), 8 (flermål), 9 (reverse), 10 (WDP), 11 (robust) |
| Tidsrekker (SARIMA, ARIMAX) | Kap. 1 |
| Gradient boosting / SHAP | Kap. 1 (LightGBM), 2 (klassifikasjon) |
| Stokastisk programmering | Kap. 2 (multi-lokasjon), 8 (grønn SC), 11 (robust) |
| Diskret hendelsessimulering | Kap. 5 (bullwhip), 6 (SimPy), 11 (Monte Carlo) |
| Heuristikker (CW, 2-opt, SA, ATC, Silver-Meal) | Kap. 3, 4, 7, 8 |
| Lagerstyringsmodeller (EOQ, Q,R, newsvendor, Clark–Scarf) | Kap. 2, 5, 10 |
| Multikriterieanalyse (AHP, TOPSIS, epsilon-constraint) | Kap. 8, 10 |
| Maskinlæring (CART, attention, LightGBM) | Kap. 1, 2, 4, 9 |
| Køteori (M/M/1, M/M/c, Erlang-C) | Kap. 6 |
| Risikomål (VaR, CVaR, minimax regret) | Kap. 11 |

---

*Sammendraget følger strukturen og terminologien i originalkompendiet. Ved bruk i LOG650-rapport bør sentrale figurer, formler og tall verifiseres direkte mot kildeteksten.*
