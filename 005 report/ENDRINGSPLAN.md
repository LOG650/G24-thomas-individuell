# Endringsplan: Kutt og styrk LOG650-rapporten

**Mål:** Reduser fra ~14 000 til 12 000 ± 500 ord. Styrk faglig kvalitet basert på benchmarkanalyse.
**Kildefil:** `LOG650_Rapport_FINAL_v10 (1).md`
**Arbeidsflyt:** Utfør stegene i rekkefølge. Kjør `py wordcount.py` etter hvert steg for å sjekke fremdrift.

---

## Steg 1 — Kapittel 6: Fjern dupliserte tallresultater (~400 ord kutt)

Kap 6 (Analyse) gjentar tallresultater som allerede presenteres i Kap 7 (Resultater). Fjern tallene fra Kap 6 og la Kap 7 være autoritativ.

### 1a. Seksjon 6.1 (ABC-analyse)
- Fjern setningen som starter «Av de 709 artiklene fikk 704 en ABC-klasse (182 A, 184 B, 338 C)…» — disse tallene står i Tabell 8 (Kap 7.1).
- Erstatt med: «Endelig fordeling mellom A-, B- og C-artikler presenteres i Tabell 8 i kapittel 7.»

### 1b. Seksjon 6.2 (XYZ-klassifisering)
- Fjern «Samsvaret mellom beregnet og systemregistrert klasse ble kvantifisert som andelen…» og hele setningen om «det lave samsvaret som ble observert». Tallet 33 % presenteres i Kap 7.2 Tabell 10.
- Behold setningen som forklarer at kryssvalidering ble gjennomført.

### 1c. Seksjon 6.4 (K-means)
- Fjern gjentatt silhouette-score (0,383/0,368) og differansen (0,015) — allerede i Kap 7.4.
- Fjern klyngestørrelser (281, 175, 31) — allerede i Tabell 12.
- Behold beskrivelse av K-valg-prosedyren og at K=3 ble valgt.

### 1d. Seksjon 6.5 (Regelmotor)
- Fjern regelfordelingen «R1 fanget 143 artikler, R2 fanget 114, R3 fanget 71…» — allerede i Kap 7.5.
- Fjern den lange forklaringen av VURDER NÆRMERE-kategorien som starter «At VURDER_NÆRMERE er den største enkeltgruppen er et bevisst designvalg…» — gjentas i Kap 7.5.
- Behold den korte beskrivelsen av at regelmotoren ble kjørt sekvensielt.

---

## Steg 2 — Kapittel 2: Komprimer litteraturgjennomgang (~500 ord kutt)

### 2a. Seksjon 2.1 (litteraturgjennomgang)
- **Avsnitt 1** (Volland et al.): Behold som innledning.
- **Avsnitt 2** (ABC/Silaen/Gupta): Kutt de siste to setningene om VED-detaljer. Poenget er allerede dekket.
- **Avsnitt 3** (XYZ/Nowotyńska/Suryaputri/Ketkar): Kutt til 2-3 setninger. Detaljer om hvert studie er unødvendig når 2.3 dekker XYZ-metoden.
- **Avsnitt 4** (EDAS/AHP/klynge): Kutt referansen til Partovi & Burton her — den brukes allerede i 2.2. Behold poenget om at K-means + regelmotor er lite dokumentert.
- **Avsnitt 5** (van Kampen): Behold — dette er rammeverkets ankerfeste.
- **Avsnitt 6** (gap-identifikasjon/Saha & Ray): Behold — dette er kjerneargumentet.

### 2b. Tabell 1 (litteraturoversikt)
- **Behold** «Relevans for oppgaven»-kolonnen — den viser sensor at du har tenkt gjennom hvorfor hver kilde er med.
- Fjern 5–6 verktøy-/programvarereferanser fra tabellen: McKinney, Pedregosa, Partovi & Burton, Kumar & Kumar, Sirisawat. Disse er sitert i tekst og referanseliste, det holder.

### 2c. Seksjon 2.6 (lagerstyring i helse)
- Kutt avsnitt 1 fra «Kumar og Kumar (2015) identifiserer…» til slutten av setningen om Sirisawat. Disse poengene er allerede dekket i 2.1.
- Behold avsnittet om Saha & Ray og Fragapane.

### 2d. Tabell 2 (sammenligning av metoder)
- Behold — dette er en nyttig oppsummeringstabell.

---

## Steg 3 — Kapittel 4: Stram metode og data (~300 ord kutt)

### 3a. Seksjon 4.1 (forskningsdesign)
- Kutt setningene «Et casestudiedesign egner seg særlig når forskningsspørsmålet handler om *hvordan* og *hva*…» og «Sistnevnte kjennetegn er tydelig til stede her…». Erstatt med: «Casestudiedesignet egner seg fordi problemstillingen er avgrenset til én operativ kontekst.»
- **Behold** avgrensningen mot kvalitativ metode, men stram: «Studien er rent kvantitativ — det benyttes ingen spørreundersøkelser, intervjuer eller deltakerobservasjon. Alle analyser er basert på operasjonelle ERP-data, som er automatisk registrert og ikke gjenstand for selvrapporteringsfeil (Saha & Ray, 2019).»
- Kutt siste avsnitt i 4.1 som starter «Studien er deskriptiv…» — erstatt med: «Studien er deskriptiv-analytisk: den klassifiserer eksisterende artikler og kombinerer resultatene i en regelbasert beslutningsmodell (van Kampen et al., 2012).»

### 3b. Seksjon 4.3 (dataforbehandling)
- Fjern avsnittet «De viktigste beslutningene utdypes kort: D-03 benytter…» (3 setninger). Tabell 5 inneholder allerede denne informasjonen.

### 3c. Seksjon 4.4 (etiske betraktninger)
- Kutt avsnittet «To sentrale parametere er antagelser…» (hele avsnittet om S og h). Dette gjentar Kap 1.4 (Antagelser). Erstatt med: «Parametervalgene S og h er begrunnet i avsnitt 1.4 og testes i sensitivitetsanalysen (kap. 7.6).»

---

## Steg 4 — Kapittel 5: Fjern gjentatt parametervurdering (~250 ord kutt)

### 4a. Seksjon 5.3 (EOQ — parametervurdering)
- Fjern avsnittet «**Parametervurdering.** Parametervalgene S = 750 kr og h = 20 %…» (hele avsnittet fra «Parametervurdering» til «…eksplisitt gjennom scenariomodellen.»).
- Erstatt med: «Parametervalgene er begrunnet i avsnitt 1.4. Sensitivitetsanalysen i kapittel 7.6 tester robustheten ved systematisk variasjon i S og h.»

### 4b. Seksjon 5.4 (K-means — treningsprosedyre)
- Kutt setningen «dette forhindrer datalekkasje fra testsettet til skaleringen» — begrepet er selvforklarende for målgruppen.
- Kutt «det vil si at testpunktenes tildeling…» — erstatt med «Testsettet evaluerer klyngestrukturens generaliserbarhet.»

---

## Steg 5 — Kapittel 8: Kutt geopolitikk, legg til svakheter (~net −90 ord)

### 5a. Kutt — Seksjon 8.3 (geopolitikk-avsnittet)
- Fjern hele avsnittet som starter «Den geopolitiske situasjonen i Midtøsten…» til «…ytre forstyrrelser.» (~120 ord).

### 5b. Kutt — Seksjon 8.3 (generaliserbarhet til andre varegrupper)
- Fjern avsnittet «Metoderammeverket er utviklet for medisinsk forbruksmateriell…» til slutten av 8.3 (~90 ord). Poenget er allerede dekket i 8.2 siste avsnitt.

### 5c. Legg til — Seksjon 8.4 (VED/kritikalitet, F3 fra benchmark)
Legg til nytt avsnitt i 8.4 etter eksisterende tekst:

> Modellen inkluderer ikke en eksplisitt kritikalitetsdimensjon som VED (Vital, Essential, Desirable). VED fanger forsyningskritikalitet for pasientbehandling som ikke fremgår av kvantitative ERP-metrikker alene. En forenklet binær kritikalitetsvurdering basert på varegruppe ville styrket modellens kliniske relevans, men krever fagkompetanse utenfor denne studiens rammeverk.

### 5d. Legg til — Seksjon 8.4 (enkelt klyngealgoritme, F5)
Legg til etter VED-avsnittet:

> Studien benytter kun K-means som klyngealgoritme. En sammenligning med hierarkisk klynging eller DBSCAN ville styrket tilliten til klyngeresultatene, særlig gitt at silhouette-scoren (0,383) indikerer moderat separasjon.

### 5e. Legg til — Seksjon 8.4 (simuleringsvalidering, F6)
Legg til etter klyngeavsnittet:

> Besparelsesestimatet er beregnet analytisk. En Monte Carlo-simulering av bestillingsfrekvensendringer for de største overføringskandidatene ville gitt et dynamisk estimat som fanger samspillet mellom ordrefrekvens, lagernivå og servicenivå over tid.

### 5f. ~~Styrk — Seksjon 8.2 (EOQ-stasjonaritet, F4)~~ ALLEREDE DEKKET
Formuleringen «augmented Dickey–Fuller» står eksplisitt i 8.2. Ingen handling nødvendig.

---

## Steg 6 — Kapittel 1 og 3: Mindre stramming (~250 ord kutt)

### 6a. Seksjon 1.3 (avgrensninger — metodevalg)
- Kutt «Metodevalg»-avsnittet fra 4 setninger til 1: «ROP-modulen er identifisert som en naturlig forlengelse, men utelatt da leveringstidsdata kun dekker 6 % av artiklene.»

### 6b. Seksjon 1.4 (antagelser — leveringstid)
- Kutt utdypningen «Denne parameteren påvirker ikke EOQ-…». Behold bare verdien og fallback-begrunnelsen.

### 6c. Seksjon 3.2 (HVFS og LIBRA)
- Kutt detaljbeskrivelsen av APL. Erstatt med: «APL innebærer ferdigpakkede leveranser direkte til avdeling uten mellomlagring, og forutsetter stabil og forutsigbar etterspørsel.»
- Kutt siste halvdel av LIBRA-avsnittet fra «I forlengelsen av LIBRA-prosjektet…» — poenget er gjort.

### 6d. Seksjon 3.3 (problemkontekst)
- Kutt setningene om de Vries og Volland som gjentar 1.1. Behold bare den SAP-spesifikke problemstillingen.

---

## Steg 7 — Vedlegg A: Fjern duplikattabell (~200 ord kutt)

- Vedlegg A inneholder en SAP-tabelloversikt som er nesten identisk med Tabell 4 i Kap 4.2.
- Erstatt innholdet i Vedlegg A med: «Se Tabell 4 i avsnitt 4.2 for fullstendig oversikt over de 14 SAP S/4HANA-tabellene.» Behold eventuelt kun nøkkelfelter-kolonnen som tilleggsinformasjon.

---

## Steg 8 — Verifisering

1. Kjør `cd "005 report" && py wordcount.py` — sjekk at totalt er innenfor 12 000 ± 500.
2. Sjekk at alle referanser i referanselisten fortsatt har minst én in-text-sitering (søk etter forfatternavn).
3. Kjør `cd "005 report" && py build_word.py` for oppdatert DOCX.
4. Les gjennom Kap 6 og 7 for å verifisere at ingen tallresultater mangler i Kap 7 etter fjerning fra Kap 6.

---

## Estimert ordbudsjett

| Steg | Handling | Ordendring |
|------|----------|------------|
| 1 | Kap 6: fjern dupliserte tall | −400 |
| 2 | Kap 2: komprimer litteratur | −500 |
| 3 | Kap 4: stram metode | −300 |
| 4 | Kap 5: fjern gjentakelser | −250 |
| 5 | Kap 8: kutt geopolitikk + legg til svakheter (VED, klynge, simulering) | +10 |
| 6 | Kap 1 + 3: stramming | −250 |
| 7 | Vedlegg A: fjern duplikat | −200 |
| **Totalt** | | **−1 890** |

Forventet sluttresultat: ~12 100 ord.
