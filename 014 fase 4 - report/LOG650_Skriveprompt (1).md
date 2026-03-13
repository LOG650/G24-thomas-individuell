# LOG650 – Masterprompt: Skriv rapporten steg for steg
### 9 kapitler | 40 sider | 18 000 ord | Times New Roman 12pt | 1,5 linjeavstand

> **Alle data fra:** `LOG650/data/MASTERFILE_V1.xlsx` og `LOG650/plots/` og `LOG650/LOG650_Resultater.xlsx`
> **Python-script:** `LOG650/LOG650_analyse_v2_6.py`
> **Outputfil:** `LOG650/rapport/LOG650_Rapport_FINAL.docx`
> **LGORT:** 3001 (ikke 3000 — sjekk dette i hvert steg)

---

## KAPITELSTRUKTUR OG ORDFORDELING

| Del | Kapittel | Sider | Ord |
|---|---|---|---|
| Frontmatter | Forord | 1 | 300 |
| Frontmatter | Sammendrag | 1 | 350 |
| **Kap 1** | Innledning | 2 | 900 |
| **Kap 2** | Litteratur og teori | 8 | 3 600 |
| **Kap 3** | Casebeskrivelse | 3 | 1 350 |
| **Kap 4** | Metode og data | 4 | 1 800 |
| **Kap 5** | Modellering | 4 | 1 800 |
| **Kap 6** | Analyse | 5 | 2 250 |
| **Kap 7** | Resultater | 4 | 1 800 |
| **Kap 8** | Diskusjon | 5 | 2 250 |
| **Kap 9** | Konklusjon | 2 | 900 |
| Backmatter | Bibliografi | 2 | 900 |
| Backmatter | Vedlegg | — | — |
| **TOTALT** | | **41 sider** | **≈ 18 200 ord** |

### Hva skiller de tre midtre kapitlene?

| Kapittel | Spørsmål det svarer på |
|---|---|
| **Kap 4 – Metode og data** | *Hvordan ble dataene samlet inn og klargjort?* |
| **Kap 5 – Modellering** | *Hvilke modeller brukes, og hvorfor? Hvordan er de satt opp?* |
| **Kap 6 – Analyse** | *Hva skjer når modellene kjøres på datasettet?* |
| **Kap 7 – Resultater** | *Hva kom ut? Tabeller, figurer, tall — presentert objektivt.* |

---

## MAPPESTRUKTUR

```
LOG650/
├── data/
│   └── MASTERFILE_V1.xlsx
├── plots/
│   ├── 01_ABC_Pareto.png
│   ├── 02_ABC_XYZ_Matrise.png
│   ├── 03_EOQ_Avvik.png
│   ├── 04_Kmeans_Klynger.png
│   └── 05_HVFS_Besparelse.png
├── rapport/
│   ├── FASIT_TALL.txt          <- genereres i STEG 0
│   └── LOG650_Rapport_FINAL.docx
├── LOG650_Resultater.xlsx
└── LOG650_analyse_v2_6.py
```

---

## FASTE PARAMETRE (bruk disse i alle steg — ikke estimer)

| Parameter | Verdi |
|---|---|
| WERKS | 3300 |
| LGORT | **3001** |
| Analyseperiode | 24 måneder (2024–2025) |
| Rådata -> aktive artikler | 1006 -> 709 |
| ABC A-grense | 80 % kumulativ verdi |
| ABC B-grense | 95 % kumulativ verdi |
| XYZ X-grense | CV < 0,5 |
| XYZ Y-grense | CV <= 1,0 |
| K-means features | z(ln(CV)), z(ln(v+1)), z(ln(|DTC|+1)) |
| K-valg | Automatisk — høyeste silhouette K = 2..7 |
| Train/test-split | 80/20, random_state = 42 |
| S (ordrekostnad) | 750 NOK |
| h (holdekostand) | 20 % av enhetspris/år |
| EOQ-terskel | 1,5 (avvik > 50 % -> FOR_MANGE_ORDRER) |
| LEAD_TIME fallback | 14 dager |
| Besparelsesformel | **Bi = fi,obs x S x r** |
| r worst / base / best | 6 % / 12 % / 20 % |
| Hva r maler | Transaksjonskostreduks. — IKKE holdekostnad |

---

---

# STEG 0 – Kjor Python-analysen

```
Role: Du er Python-utvikler og dataanalytiker.

Kjor:
  cd LOG650
  python LOG650_analyse_v2_6.py

Etter kjoring — les og lagre folgende i LOG650/rapport/FASIT_TALL.txt:

  ARTIKLER_TOTALT      = [tall]
  ABC_A_ANTALL         = [tall]
  ABC_A_VERDI_PCT      = [tall] %
  ABC_B_ANTALL         = [tall]
  ABC_B_VERDI_PCT      = [tall] %
  ABC_C_ANTALL         = [tall]
  ABC_C_VERDI_PCT      = [tall] %
  XYZ_X_ANTALL         = [tall]
  XYZ_Y_ANTALL         = [tall]
  XYZ_Z_ANTALL         = [tall]
  KMEANS_K             = [tall]
  KMEANS_SIL_TREN      = [tall]
  KMEANS_SIL_TEST      = [tall]
  HVFS_OVERFØR         = [tall]
  HVFS_BEHOLD          = [tall]
  HVFS_VURDER          = [tall]
  BESPARELSE_WORST     = [tall] kr/år
  BESPARELSE_BASE      = [tall] kr/år
  BESPARELSE_BEST      = [tall] kr/år
  SENS_SCENARIER       = [tall]
```

### Selvsjekk STEG 0

```
[ ] plots/01_ABC_Pareto.png finnes
[ ] plots/02_ABC_XYZ_Matrise.png finnes
[ ] plots/03_EOQ_Avvik.png finnes
[ ] plots/04_Kmeans_Klynger.png finnes
[ ] plots/05_HVFS_Besparelse.png finnes
[ ] LOG650_Resultater.xlsx finnes med 8 ark
[ ] FASIT_TALL.txt skrevet og komplett (20 nokkeltall)
[ ] Ingen NaN eller apenbart feil 0-verdier

STOPP og fiks eventuelle feil FOR du gar videre.
```

---

---

# STEG 1 – Forord (~300 ord)

```
Role: Du er Thomas Ekrem Jensen, SAP MM-konsulent ved Helse Vest IKT
og bachelorstudent ved Hogskolen i Molde.

Skriv Forordet. Mal: 300 ord. Ingen overskrifter. Ingen referanser.

Innhold:
- Takk til veileder Bård Inge Austigard Pettersen (fullt navn)
- Takk til Helse Bergen for datatilgang
- Kort om temaet og motivasjon (SAP-bakgrunn, LIBRA-prosjektet)
- Sted og dato: Stavanger, mai 2026
```

### Selvsjekk STEG 1
```
[ ] 280–320 ord
[ ] Veileder nevnt med fullt navn
[ ] Helse Bergen nevnt
[ ] Stavanger, mai 2026
[ ] Ingen referanser, ingen overskrifter
```

---

---

# STEG 2 – Sammendrag (~350 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Sammendraget. Mal: 350 ord. Ingen overskrifter. Ingen referanser.
Bruk KUN tall fra FASIT_TALL.txt.

Struktur (ett avsnitt per punkt):
1. Problemstilling og formal
2. Datagrunnlag: FASIT_TALL.ARTIKLER_TOTALT aktive artikler,
   SAP S/4HANA, WERKS 3300, LGORT 3001
3. Metode: ABC, XYZ, EOQ, K-means (K=FASIT_TALL.KMEANS_K),
   regelmotor med 8 regler
4. Nokkelfunn (bruk FASIT-tall):
   - ABC A: [tall] artikler = [tall]% av verdi
   - K-means silhouette tren=[tall] / test=[tall]
   - HVFS-kandidater: [tall] artikler
   - Besparelse base case: kr [tall]/år
     (Bi = fi,obs x S x r, S=750 kr, r=12 %)
5. Konklusjon: sentralisering til HVFS anbefales, med reservasjoner
```

### Selvsjekk STEG 2
```
[ ] 330–370 ord
[ ] Alle tall hentet fra FASIT_TALL.txt
[ ] Besparelsesformel korrekt: Bi = fi,obs x S x r
[ ] LGORT 3001 (ikke 3000)
[ ] Ingen referanser
```

---

---

# STEG 3 – Kapittel 1: Innledning (~900 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 1 – Innledning. Mal: 900 ord.

Underkapitler:
  1.1 Bakgrunn og aktualisering    300 ord
  1.2 Problemstilling              150 ord
  1.3 Avgrensninger                250 ord
  1.4 Antagelser                   200 ord

Krav:
- 1.1: Aktualiser lagerbinding i norske helseforetak med referanse.
       Kontekst: WERKS 3300, LGORT 3001 ved Helse Bergen.
- 1.2: Problemstillingen som "Hvordan..."-sporsmal.
- 1.3: Alle avgrensninger begrunnet faglig — aldri "mangel på tid".
       Avgrensning til LGORT 3001 skal begrunnes (transaksjonsdata).
- 1.4: Definer eksplisitt:
       S = 750 NOK (ordrekostnad — antagelse, ikke observert)
       h = 20 % (holdekostnad — antagelse)
       Analyseperiode = 24 måneder
       LEAD_TIME fallback = 14 dager
       Besparelsesformel: Bi = fi,obs x S x r
       (transaksjonskostnad — ikke holdekostnad)
- Avslutt med: "Rapporten er strukturert som folger: ..."
  og list alle 9 kapitler.
- Minst 3 referanser i kapitlet.
```

### Selvsjekk STEG 3
```
[ ] 850–950 ord
[ ] 1.2 er "Hvordan..."-sporsmal
[ ] LGORT 3001 — ikke 3000
[ ] S=750, h=20%, periode=24 mnd, LEAD_TIME=14 dager nevnt
[ ] Besparelsesformelen Bi = fi,obs x S x r introdusert
[ ] Rapportstruktur med alle 9 kapitler listet
[ ] Minst 3 referanser
```

---

---

# STEG 4 – Kapittel 2: Litteratur og teori (~3 600 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 2 – Litteratur og teori. Mal: 3 600 ord.

Underkapitler:
  2.1 Litteraturgjennomgang              800 ord
  2.2 ABC-analyse                        550 ord
  2.3 XYZ-klassifisering                 500 ord
  2.4 Economic Order Quantity (EOQ)      550 ord
  2.5 K-means klyngeanalyse              500 ord
  2.6 Lagerstyring i helsesektoren       500 ord
  2.7 Konseptuelt rammeverk              200 ord

Krav:
  2.1: Hva er gjort, hvem er uenige, hva er gapet.
       Minst 8 referanser. Argumentasjon — ikke mekanisk listing.
  2.2: ABC-definisjoner, Pareto-prinsipp, grenser 80%/95%,
       styrker og svakheter. Referanse.
  2.3: CV = sigma/mu, grenser 0,5/1,0. ABC/XYZ-kombinasjon. Referanse.
  2.4: EOQ = sqrt(2DS/H), definer D, S, H, forutsetninger, sensitivitet.
       Referanse.
  2.5: K-means algoritme, elbow, silhouette,
       begrunnelse for log-transformasjon og z-score. Referanse.
  2.6: Saertrekk helsesektor, forsyningssikkerhet, SAP. Referanse.
  2.7: Pipeline SAP-data -> ABC -> XYZ -> EOQ -> K-means -> Regelmotor -> HVFS.
       Henvis til Figur 0. Presiser at detaljert modellbeskrivelse er i Kap 5.
```

### Selvsjekk STEG 4
```
[ ] 3 400–3 800 ord
[ ] 2.1: Minst 8 referanser, gap identifisert
[ ] 2.2–2.5: Formler gjengitt, referanser
[ ] 2.6: Minst 2 referanser helsesektor
[ ] 2.7: Figur 0 referert, peker til Kap 5
```

---

---

# STEG 5 – Kapittel 3: Casebeskrivelse (~1 350 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 3 – Casebeskrivelse. Mal: 1 350 ord.
Ingen analyseresultater i dette kapitlet.

Underkapitler:
  3.1 Helse Bergen og Helse Vest          450 ord
  3.2 HVFS og LIBRA-prosjektet            450 ord
  3.3 Problemkontekst og datagrunnlag     450 ord

Krav:
  3.1: Helse Bergen, størrelse, rolle, SAP S/4HANA (WERKS 3300, LGORT 3001).
  3.2: HVFS, APL-prosjektet, LIBRA-prosjektet, sentrallagermodellen.
  3.3: Problemet (lagerbinding, suboptimal sortering, manglende sentralisering).
       Hva virksomheten mener — ikke egne funn.
       14 SAP-tabeller. Henvis til Tabell 3 og Figur 1.
       Minst 3 referanser i kapitlet.
```

### Selvsjekk STEG 5
```
[ ] 1 250–1 450 ord
[ ] LGORT 3001 — ingen forekomst av 3000
[ ] Ingen analyseresultater
[ ] Tabell 3 og Figur 1 referert
[ ] Minst 3 referanser
```

---

---

# STEG 6 – Kapittel 4: Metode og data (~1 800 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 4 – Metode og data. Mal: 1 800 ord.
Dette kapitlet handler om datainnsamling og klargjoring.
Modellenes matematikk beskrives i Kap 5.

Underkapitler:
  4.1 Forskningsdesign          350 ord
  4.2 Datainnsamling            500 ord
  4.3 Dataforbehandling         750 ord
  4.4 Etikk og begrensninger    200 ord

Krav:
  4.1: Kvantitativ casestudie. Henvis til [Yin, 2018] e.l.
       Begrunn SAP-data (operasjonelle ERP-data, ikke selvrapportert).
       Avgrensning til WERKS 3300, LGORT 3001.
  4.2: 14 SAP-tabeller (Tabell 4). 24 mnd. WERKS=3300, LGORT=3001.
       Fra 1006 rader -> 709 aktive artikler.
  4.3: Alle 8 datavalgsbeslutninger med faglig begrunnelse:
       D-01: Aktiv = D_ANNUAL>0 ELLER TOTAL_STOCK>0 -> 709 av 1006
       D-02: UNIT_PRICE = STPRS / PEINH
       D-03: ABC_VALUE = D_ANNUAL x UNIT_PRICE der TOTAL_NETWR mangler
       D-04: XYZ fra CV — ZZXYZ kun validering
       D-05: LEAD_TIME fallback = 14 dager (6 % fra EINA/EINE)
       D-06: MSEG_STATUS blank -> AKTIV
       D-07: ABC_VALUE_SOURCE: TOTAL_NETWR>0 kreves for EKPO
       D-08: ACTUAL_FREQ = ORDER_COUNT x (12/24)
       Henvis til Tabell 5.
  4.4: Ingen personopplysninger. S=750 og h=20% er antagelser.
       LEAD_TIME fallback dekker 94% uten observert data.

VIKTIG: Ikke beskriv ABC/XYZ/EOQ/K-means matematisk her.
Si kun at modellene beskrives i Kap 5.
```

### Selvsjekk STEG 6
```
[ ] 1 700–1 900 ord
[ ] LGORT 3001 — ikke 3000
[ ] Ingen modellmatematikk (det er Kap 5)
[ ] Alle 8 beslutninger D-01–D-08 dekket
[ ] S og h eksplisitt kalt "antagelser"
[ ] Tabell 4, Tabell 5 referert
[ ] Minst 4 referanser
```

---

---

# STEG 7 – Kapittel 5: Modellering (~1 800 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 5 – Modellering. Mal: 1 800 ord.
Beskriv modellenes matematiske oppbygging og parametersetting.
Ingen kjoresultater fra datasettet — det er Kap 6.

Underkapitler:
  5.1 ABC-modellen                      300 ord
  5.2 XYZ-modellen                      300 ord
  5.3 EOQ-modellen og besparelsesformel 450 ord
  5.4 K-means klyngemodellen            450 ord
  5.5 Regelmotor                        300 ord

Krav:
  5.1: Kumulativ verdiandel. Grenser A=80%, B=95%. Parametersetting.
  5.2: CV = sigma/mu (manedlig forbruk 24 mnd).
       X: CV<0,5 / Y: 0,5<=CV<1,0 / Z: CV>=1,0.
       Validering mot ZZXYZ.
  5.3: EOQ = sqrt(2DS/H). D=ars. forbruk, S=750 NOK, H=h x UNIT_PRICE.
       Avviksformel: FREQ_AVVIK = (ACTUAL_FREQ - EOQ_FREQ) / EOQ_FREQ.
       Terskel: 1,5 -> FOR_MANGE_ORDRER.
       Besparelsesformel SEPARAT:
         Bi = fi,obs x S x r
         r: worst=6%, base=12%, best=20%
         PRESISER: dette er transaksjonskostnad — IKKE holdekostnad.
         fi,obs = ACTUAL_FREQ (annualisert fra EKBE via D-08).
  5.4: Featurevektor: [z(ln(CV)), z(ln(v+1)), z(ln(|DTC|+1))]
       Begrunn log-transformasjon (hoyreskjevhet).
       Begrunn |DTC| (avviksstorrelse, ikke retning).
       Train/test 80/20 (random_state=42).
       StandardScaler fittes KUN pa treningsdata.
       KMeans fittes KUN pa treningsdata.
       K: automatisk via hoyeste silhouette K=2..7.
       Silhouette separat for tren og test.
  5.5: 8 regler i prioritert rekkefolge:
       1. Z-override -> BEHOLD_LOKALT (alltid)
       2. C+Y -> BEHOLD_LOKALT
       3. A/B + X + FOR_MANGE_ORDRER -> OVERFØR_HVFS
       4. A/B + X + K_OVERFØR -> OVERFØR_HVFS
       5. A/B + Y + K_OVERFØR -> OVERFØR_HVFS
       6. A/B + X (ikke K_OVERFØR) -> VURDER_NÆRMERE
       7. A/B + Y (ikke K_OVERFØR) -> VURDER_NÆRMERE
       8. C+X -> VURDER_NÆRMERE
       Forklar sekvenslogikken.

VIKTIG: Ingen tall fra det faktiske datasettet her.
Parametere (S=750, h=20%) er OK — de er modellinnstillinger.
```

### Selvsjekk STEG 7
```
[ ] 1 700–1 900 ord
[ ] EOQ = sqrt(2DS/H) korrekt
[ ] Bi = fi,obs x S x r — presisert som transaksjonskostnad
[ ] h brukt BARE i H=h x UNIT_PRICE — IKKE i besparelsesformelen
[ ] Train/test: fit kun pa treningsdata, korrekt gjengitt
[ ] Alle 8 regler listet og forklart
[ ] Ingen resultater fra datasettet
[ ] Minst 4 referanser
```

---

---

# STEG 8 – Kapittel 6: Analyse (~2 250 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 6 – Analyse. Mal: 2 250 ord.
Beskriv hva som skjer nar modellene kj?res pa datasettet.
Prosessorientert — ikke presentasjon av sluttresultater (det er Kap 7).

Underkapitler:
  6.1 ABC-analyse av 709 artikler         400 ord
  6.2 XYZ-klassifisering                  400 ord
  6.3 EOQ-avviksberegning                 450 ord
  6.4 K-means klyngeanalyse               600 ord
  6.5 Regelmotor og HVFS-scoring          400 ord

Krav:
  6.1: Sorteringsprosessen (rangering, kumulativ sum), grenser 80%/95%.
       Henvis til Figur 3 (Pareto). Beskriv prosessen, referer Kap 7 for tall.
  6.2: CV beregnet per artikkel (EKBE-data 24 mnd). Grenser anvendt.
       ZZXYZ som valideringssjekk. Krysstabulering mot ABC.
       Henvis til Figur 5.
  6.3: EOQ_FREQ beregnet. ACTUAL_FREQ annualisert (D-08).
       Avvik og terskel 1,5 anvendt. DTC beregnet.
       Henvis til Figur 3 (EOQ-avvik) og Tabell 9.
  6.4: Featurevektor konstruert. Log-transformasjon utfort.
       80/20-split gjennomfort (n_tren=[FASIT], n_test=[FASIT]).
       Scaler fittet pa treningsdata. Elbow K=2..7 (Figur 8).
       Beste K valgt: K=[FASIT_TALL.KMEANS_K].
       KMeans fittet og predikert separat pa tren og test.
       K_OVERFØR-klynge identifisert (lav CV, hoy verdi, hoy |DTC|).
       Henvis til Figur 9.
  6.5: Regelmotor kjort pa alle 709 artikler, sekvensiell prioritet.
       Bi = fi,obs x S x r for alle OVERFØR_HVFS.
       Sensitivitetsanalyse: [FASIT.SENS_SCENARIER] scenarier.
       Henvis til Tabell 11 og Figur 5.

VIKTIG: Analyseprocessen — ikke sluttresultater.
Sluttresultater i Kap 7.
```

### Selvsjekk STEG 8
```
[ ] 2 100–2 400 ord
[ ] Prosessbeskrivelse — ikke sluttresultater
[ ] n_tren og n_test fra FASIT_TALL.txt
[ ] K=[FASIT] nevnt
[ ] Bi = fi,obs x S x r korrekt
[ ] LGORT 3001 der aktuelt
[ ] Minst 3 referanser
```

---

---

# STEG 9 – Kapittel 7: Resultater (~1 800 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 7 – Resultater. Mal: 1 800 ord.
Presenter funnene objektivt. INGEN tolkning — det er Kap 8.
Bruk KUN tall fra FASIT_TALL.txt.

Underkapitler:
  7.1 ABC-resultater                    300 ord
  7.2 XYZ-resultater                    300 ord
  7.3 EOQ-avviksresultater              300 ord
  7.4 K-means klyngeresultater          350 ord
  7.5 Regelmotor og HVFS-anbefalinger   350 ord
  7.6 Besparelse og sensitivitet        200 ord

Krav:
  7.1: Tabell 6 (ABC). Figur 3 (Pareto) og Figur 4 (soyle).
       A=[tall] art ([tall]%), B=[tall] ([tall]%), C=[tall] ([tall]%).
  7.2: Tabell 7 (XYZ) og Tabell 8 (kryssmatrise). Figur 5 og 6.
  7.3: DTC total. FOR_MANGE/OPTIMAL/FOR_FÅ. Tabell 9. Figur 3 (EOQ).
  7.4: K=[tall], sil tren=[tall], test=[tall].
       Klyngeprofiler. K_OVERFØR antall og profil. Tabell 10. Figur 4.
  7.5: OVERFØR=[tall], BEHOLD=[tall], VURDER=[tall].
       Tabell 11. Figur 5 (kakediagram).
  7.6: Worst=[tall], base=[tall], best=[tall] kr/ar.
       Bi = fi,obs x S x r (S=750). Tabell 12. Figur 5.

ABSOLUTTE KRAV:
- Alle tall fra FASIT_TALL.txt
- Figurtekster under figuren
- Tabelltitler over tabellen
- INGEN tolkninger
```

### Selvsjekk STEG 9
```
[ ] 1 700–1 900 ord
[ ] Alle tall fra FASIT_TALL.txt
[ ] Bi = fi,obs x S x r — h ikke nevnt i besparelsen
[ ] Tabell 6–12 referert
[ ] Ingen tolkninger
[ ] LGORT 3001 der aktuelt
```

---

---

# STEG 10 – Kapittel 8: Diskusjon (~2 250 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 8 – Diskusjon. Mal: 2 250 ord.
Ingen nye data. Minst 8 referanser aktivt brukt.

Underkapitler:
  8.1 Funn opp mot litteraturen            600 ord
  8.2 Metodekritikk                        600 ord
  8.3 Praktisk betydning for Helse Bergen  600 ord
  8.4 Svakheter og begrensninger           450 ord

Krav:
  8.1: ABC A-andel vs. Pareto-prinsippet i litteraturen. Referanse.
       Silhouette [tall] — hva er akseptabelt? Referanse.
       Besparelsesestimat vs. tilsvarende studier.
  8.2: Reliabilitet (SAP-data = operasjonelle).
       Validitet (maler ABC det den hevder for LGORT 3001?).
       Generaliserbarhet (andre WERKS i Helse Vest?) — var edruelig.
  8.3: Hva betyr [tall] artikler overfort i praksis?
       Neste steg for Helse Bergen. SAP-endringer (MRP-type, ordrekvantumspar.).
       VURDER_NÆRMERE ([tall] art) bor gjennomgas manuelt.
  8.4: r er IKKE empirisk — det er et scenarioparameter.
       LEAD_TIME fallback 14 dager for 94% av artikler.
       24 mnd pavirket av COVID-ettervirkninger.
       K-means sensitiv for K-valg — automatisk valg minimerer bias.
       D-03: ABC-verdier for noen artikler estimert — konsekvenser.
```

### Selvsjekk STEG 10
```
[ ] 2 100–2 400 ord
[ ] Ingen nye data
[ ] r kalt scenarioparameter — ikke empirisk
[ ] LEAD_TIME-begrensning nevnt
[ ] LGORT 3001 der aktuelt
[ ] Minst 8 referanser
```

---

---

# STEG 11 – Kapittel 9: Konklusjon (~900 ord)

```
Role: Du er Thomas Ekrem Jensen.

Skriv Kapittel 9 – Konklusjon. Mal: 900 ord.
Ingen nye referanser. Ingen nye data.

Underkapitler:
  9.1 Svar pa problemstillingen         350 ord
  9.2 Anbefalinger til Helse Bergen     300 ord
  9.3 Forslag til videre forskning      250 ord

Krav:
  9.1: Gjenta problemstillingen fra 1.2 ordrett.
       Svar direkte med FASIT-tall.
       [tall] artikler anbefalt -> besparelse kr [tall]/ar (r=12%).
  9.2: Minst 4 konkrete, nummererte anbefalinger:
       1. Pilotoverforing: klynge K_OVERFØR + AX/BX-artikler
       2. Gjennomga VURDER_NÆRMERE ([tall]) manuelt
       3. Oppdater SAP MM MRP-type og ordrekvantumspar.
       4. Evaluer gevinstrealisering etter 12 mnd
  9.3: Minst 3 forslag til videre forskning:
       - ROP-modul (ikke implementert i v2.6)
       - Leverandorkonsolidering
       - Replikering til andre WERKS i Helse Vest
```

### Selvsjekk STEG 11
```
[ ] 850–950 ord
[ ] Problemstillingen gjentatt ordrett fra 1.2
[ ] FASIT-tall brukt
[ ] Minst 4 anbefalinger
[ ] Minst 3 forslag til videre forskning
[ ] Ingen nye referanser eller data
```

---

---

# STEG 12 – Bibliografi

```
Skriv Bibliografien. Alle 23 kilder i APA 7, alfabetisk.

Sjekk:
- Alle in-text-referanser fra Kap 1–9 finnes i listen
- Alle kilder i listen er sitert i teksten
- DOI eller URL inkludert der tilgjengelig

[Lim inn dine 23 kilder her]
```

### Selvsjekk STEG 12
```
[ ] Noyaktig 23 kilder
[ ] Alle i APA 7-format
[ ] Alle sitert i teksten — ingen "spokelsesreferanser"
[ ] DOI/URL der tilgjengelig
[ ] Alfabetisk rekkefølge
```

---

---

# STEG 13 – Total sluttsjekk

```
Role: Du er kvalitetskontrollos.

Gjennomfor total sluttsjekk FOR Word-generering.

--- ORDTELLING ---
Forord:       ___ ord  (mal 300)
Sammendrag:   ___ ord  (mal 350)
Kap 1:        ___ ord  (mal 900)
Kap 2:        ___ ord  (mal 3 600)
Kap 3:        ___ ord  (mal 1 350)
Kap 4:        ___ ord  (mal 1 800)
Kap 5:        ___ ord  (mal 1 800)
Kap 6:        ___ ord  (mal 2 250)
Kap 7:        ___ ord  (mal 1 800)
Kap 8:        ___ ord  (mal 2 250)
Kap 9:        ___ ord  (mal 900)
Bibliografi:  ___ ord  (mal 900)
TOTALT:       ___ ord  (mal 18 200)

--- LGORT-SJEKK ---
Sok etter "LGORT 3000" i hele dokumentet:
[ ] Null treff — alle er rettet til 3001

--- FORMELSJEKK ---
[ ] EOQ = sqrt(2DS/H) — kun der EOQ beregnes
[ ] Bi = fi,obs x S x r — brukt i Kap 5.3, 6.5, 7.6, 9.1
[ ] h brukt i H=h x UNIT_PRICE — ALDRI i besparelsesformelen
[ ] S = 750 NOK konsistent (ikke 250)

--- KAPITTELGRENSER ---
[ ] Kap 4: Kun datainnsamling og klargjoring — ingen modellmatematikk
[ ] Kap 5: Kun modelloppbygging — ingen datasett-resultater
[ ] Kap 6: Kun analytisk prosess — ingen sluttresultater
[ ] Kap 7: Kun sluttresultater — ingen tolkninger
[ ] Kap 8: Kun tolkning — ingen nye data

--- REFERANSESJEKK ---
[ ] Alle in-text-referanser finnes i bibliografien
[ ] Alle bibliografi-kilder er sitert
[ ] Ingen synsing uten referanse i Kap 2, 8

--- TALLSJEKK ---
[ ] Alle tall i Kap 7 og 9 matcher FASIT_TALL.txt

--- FIGURER ---
[ ] Figur 0 – Konseptuelt rammeverk (Kap 2)
[ ] Figur 1 – Lagerstruktur (Kap 3)
[ ] Figur 2 – Analysepipeline (Kap 4)
[ ] Figur 3 – ABC Pareto + EOQ-avvik
[ ] Figur 4 – K-means klynger
[ ] Figur 5 – Besparelse/HVFS-anbefaling
[ ] Figur 6 – ABC/XYZ-matrise

SKRIV: GODKJENT eller IKKE GODKJENT [hva som mangler]
```

---

---

# STEG 14 – Generer Word-dokument

```
Role: Du er dokumentprodusent. Les SKILL.md (docx) FOR du starter.

Generer: LOG650/rapport/LOG650_Rapport_FINAL.docx

--- SIDEFORMAT ---
Papir:        A4 (11906 x 16838 DXA)
Marger:       2,54 cm alle kanter (1440 DXA)
Font:         Times New Roman 12pt
Linjeavstand: 1,5 (360 DXA)
Avsnitt:      spacing before=0, after=120

--- STILER ---
Heading 1: Times New Roman 14pt bold
Heading 2: Times New Roman 13pt bold
Heading 3: Times New Roman 12pt bold italic
Normal:    Times New Roman 12pt, 1,5 linjeavstand

--- REKKEFØLGE ---
1.  Forside
2.  Forord
3.  Sammendrag
4.  Innholdsfortegnelse (automatisk)
5.  Liste over figurer
6.  Liste over tabeller
7.  Kap 1 Innledning
8.  Kap 2 Litteratur og teori
9.  Kap 3 Casebeskrivelse
10. Kap 4 Metode og data
11. Kap 5 Modellering
12. Kap 6 Analyse
13. Kap 7 Resultater
14. Kap 8 Diskusjon
15. Kap 9 Konklusjon
16. Bibliografi
17. Vedlegg A: Python-script (LOG650_analyse_v2_6.py)
18. Vedlegg B: Datakvalitetsbeslutninger D-01–D-08

--- FORSIDE ---
Logo:       Hogskolen i Molde
Tittel:     Lageroptimalisering ved Helse Bergen
Undertittel: En analyse av 709 artikler for mulig sentralisering til HVFS
Forfatter:  Thomas Ekrem Jensen
Veileder:   Bård Inge Austigard Pettersen
Emne:       LOG650 – Bacheloroppgave i logistikk og supply chain management
Dato:       Mai 2026

--- SIDETALL ---
Forord/sammendrag/innholdsfortegnelse: romertall (i, ii, iii)
Fra Kap 1: arabiske tall (1, 2, 3...)

--- FIGURER ---
PNG-filer fra LOG650/plots/ settes inn pa korrekte steder.
Figurtekst: under figuren, kursiv.
Tabelltittel: over tabellen, fet.
Maks 80% av sidebredde. Sentrert.

--- VALIDERING ---
Kjor validate.py. Bekreft gront svar.
```

### Selvsjekk STEG 14
```
[ ] LOG650/rapport/LOG650_Rapport_FINAL.docx finnes
[ ] validate.py: ingen feil
[ ] Forside korrekt
[ ] Innholdsfortegnelse med alle 9 kapitler
[ ] Sidetall: romertall -> arabiske fra Kap 1
[ ] Alle figurer satt inn
[ ] Times New Roman 12pt gjennomgaende
[ ] 1,5 linjeavstand gjennomgaende
[ ] 38–42 sider

FERDIG — klar for innlevering
```

---

## HURTIGREFERANSE

| Fil | Path |
|---|---|
| Kildedata | `LOG650/data/MASTERFILE_V1.xlsx` |
| Python-script | `LOG650/LOG650_analyse_v2_6.py` |
| Analyseresultater | `LOG650/LOG650_Resultater.xlsx` |
| Plots | `LOG650/plots/*.png` |
| Fasit-tall | `LOG650/rapport/FASIT_TALL.txt` |
| Ferdig rapport | `LOG650/rapport/LOG650_Rapport_FINAL.docx` |
