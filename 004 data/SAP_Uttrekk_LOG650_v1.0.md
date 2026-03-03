# SAP-uttrekk – SE16H
*Helse Bergen forsyningslager · LOG650 · Februar 2026*
*WERKS: 3300 · LGORT: 3000 · v1.0*

---

## Logikk og rekkefølge

**MARD hentes alltid først** – definerer artikkeluniverset på LGORT 3000. **MDMA hentes som nr. 2** – bekrefter hvilke MATNR som er aktive i MRP-område 3000 og gir ABC/XYZ. **Alle tabeller fra nr. 3 og utover filtreres mot MATNR-listen fra MDMA (WERKS=3300, BERID=3000).**

```
MARD   →  artikkelunivers (LGORT 3000)
  └─ MDMA   WERKS=3300, BERID=3000  →  ABC/XYZ + bekreftet MATNR-liste
       └─ MARA   MATNR fra MDMA
       └─ MAKT   MATNR fra MDMA
       └─ MARC   MATNR fra MDMA, WERKS=3300
       └─ MBEW   MATNR fra MDMA
       └─ MSEG   BWART=201  →  FORBRUK UT fra lager til avdeling (XYZ/CV, EOQ etterspørsel D)
       └─ EKKO   datofilter
            └─ EKPO  EBELN fra EKKO + MATNR fra MDMA + LGORT=3000
                 └─ EKBE  →  INNKJØP INN til lager fra leverandør (ABC-verdi, EOQ-avvik)
       └─ EINE   MATNR fra MDMA
       └─ T023T  MATKL fra MARA
```

---

## Uttrekksrekkefølge

| # | Tabell | Filnavn | Primærfilter | Formål |
|---|---|---|---|---|
| 1 | MARD | MARD_3300_3000.xlsx | WERKS=3300, LGORT=3000 | Definerer artikkelunivers |
| 2 | MDMA | MDMA_3300_3000.xlsx | MATNR fra MARD, WERKS=3300, BERID=3000 | ABC- og XYZ-indikator per MRP-område |
| 3 | MARA | MARA_3300.xlsx | MATNR fra MDMA, MTART=[avklar] | Ekskluder feil materialtype |
| 4 | MAKT | MAKT_NO.xlsx | MATNR fra MDMA, SPRAS=NO | Materialebeskrivelser |
| 5 | MARC | MARC_3300.xlsx | MATNR fra MDMA, WERKS=3300 | MRP-parametere |
| 6 | MBEW | MBEW_3300.xlsx | MATNR fra MDMA, BWKEY=3300 | Pris per artikkel |
| 7 | MSEG 2024 | MSEG_3300_3000_2024.xlsx | MATNR fra MDMA, WERKS=3300, LGORT=3000, BWART=201+647, BUDAT=01.01.2024–31.12.2024 | 🔴 FORBRUK UT fra lager → avdeling (~135 000 rader) |
| 8 | MSEG 2025 | MSEG_3300_3000_2025.xlsx | MATNR fra MDMA, WERKS=3300, LGORT=3000, BWART=201+647, BUDAT=01.01.2025–31.12.2025 | 🔴 FORBRUK UT fra lager → avdeling (~135 000 rader) |
| 9 | EKKO | EKKO_2024_2025.xlsx | BSTYP=F, BSART=ZNB, EKGRP=3000+300, BEDAT=01.01.2024–31.12.2025 | Innkjøpsordrehoder |
| 10 | EKPO | EKPO_3300.xlsx | EBELN fra EKKO, MATNR fra MDMA, WERKS=3300, LGORT=3000, LOEKZ=blank | Ordreposisjoner (8 240 rader) |
| 11 | EKBE | EKBE_2024_2025.xlsx | EBELN+EBELP fra EKPO, BEWTP=E, BWART=101, BUDAT=01.01.2024–31.12.2025 | 🔵 INNKJØP INN til lager → fra leverandør (9 004 rader) |
| 12 | EINA | EINA_3300.xlsx | MATNR fra MDMA, WERKS=3300 | Leverandør-artikkel-infopost – kobling MATNR → INFNR |
| 13 | EINE | EINE_3300.xlsx | INFNR fra EINA | Leveringstid (WEBAZ) per infopost |
| 14 | T023T | T023T_NO.xlsx | MATKL fra MARA, SPRAS=NO | Varegruppenavn |

---

## Dataflyt – inn og ut av lager

| Retning | Tabell | Brukes til |
|---|---|---|
| 🔴 **UT fra lager** | MSEG (BWART=201) | Forbruk til avdeling – XYZ/CV, EOQ etterspørsel D |
| 🔵 **INN til lager** | EKKO → EKPO → EKBE | Innkjøp fra leverandør – ABC-verdi, EOQ-avvik |

---

## Feltliste per tabell

### 1. MARD – Lagerbeholdning *(hentes først)*
*Filter: WERKS=3300, LGORT=3000*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Nøkkel – definerer universet | ✓ Kritisk |
| WERKS | Anlegg | Filter = 3300 | ✓ Kritisk |
| LGORT | Lagersted | Filter = 3000 | ✓ Kritisk |
| LABST | Fritt disponibelt lager | Aktivitetskontroll | ✓ Kritisk |
| EINME | Beholdning i kvalitetskontroll | Komplett aktivitetsbilde | Bør ha |
| UMLME | Beholdning i overføring | Komplett aktivitetsbilde | Bør ha |

> Aktiv artikkel = LABST + EINME + UMLME > 0

---

### 2. MDMA – ABC og XYZ per MRP-område *(egendefinert tabell)*
*Filter: MATNR fra MARD, WERKS=3300, BERID=3000*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| WERKS | Anlegg | Filter = 3300 | ✓ Kritisk |
| BERID | MRP-område | Filter = 3000 | ✓ Kritisk |
| ZZABC | ABC-indikator (Helse Bergen) | Validering mot beregnet ABC | ✓ Kritisk |
| ZZXYZ | XYZ-indikator (Helse Bergen) | Validering mot beregnet XYZ | ✓ Kritisk |

> MDMA er strukturert på fabrikk (WERKS) + MRP-område (BERID). MRP-område 3000 tilsvarer lagersted 3000 hos Helse Bergen, men er teknisk sett et eget felt. ABC og XYZ kan valideres direkte mot det som er registrert i systemet.

---

### 3. MARA – Materialmaster
*Filter: MATNR fra MDMA, MTART=[avklar med Helse Bergen]*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| MTART | Materialtype | Ekskluder legemidler/implantater | ✓ Kritisk |
| MATKL | Varegruppe (kode) | Segmentering / kobling T023T | ✓ Kritisk |
| MEINS | Basisenhet | EOQ-beregning | ✓ Kritisk |

---

### 4. MAKT – Materialebeskrivelse
*Filter: MATNR fra MDMA, SPRAS=NO*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| SPRAS | Språk | Filter = NO | ✓ Kritisk |
| MAKTX | Beskrivelse (klartekst) | Lesbar output | ✓ Kritisk |

---

### 5. MARC – Materialdata per anlegg
*Filter: MATNR fra MDMA, WERKS=3300*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| WERKS | Anlegg | Filter = 3300 | ✓ Kritisk |
| MTVFP | XYZ-indikator (SAP standard) | Kontekst – erstattes av MDMA.ZZXYZ | Bør ha |
| DISMM | Disponeringspolicy (MRP-type) | Kontekst bestillingspolicy | Bør ha |
| EISBE | Sikkerhetslager | EOQ / ROP | Bør ha |
| MINBE | Bestillingspunkt | EOQ / ROP | Bør ha |
| MABST | Lottstørrelse / avrunding | EOQ-validering | Bør ha |

---

### 6. MBEW – Materialvurdering (pris)
*Filter: MATNR fra MDMA, BWKEY=3300*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| BWKEY | Vurderingsområde | Filter = 3300 | ✓ Kritisk |
| STPRS | Standardpris | ABC-verdi, EOQ holdekostnad H | ✓ Kritisk |
| VERPR | Glidende gjennomsnittspris | Alternativ til STPRS | ✓ Kritisk |
| PEINH | Prisenhet | Korreksjonsfaktor | ✓ Kritisk |
| VPRSV | Priskontrollindikator (S/V) | Avgjør hvilken pris som er aktiv | ✓ Kritisk |

> Prislogikk: VPRSV='S' → pris = STPRS ÷ PEINH · VPRSV='V' → pris = VERPR ÷ PEINH
> PEINH er ofte 10 eller 100 – ikke 1. Hyppig årsak til feil ABC-beregning.

---

### 7–8. MSEG – Faktisk forbruk ut fra lager *(primærkilde for forbruksdata)*
*Filter: MATNR fra MDMA, WERKS=3300, LGORT=3000, BWART=201+647 – kjør 2024 og 2025 som separate uttrekk*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| WERKS | Anlegg | Filter = 3300 | ✓ Kritisk |
| LGORT | Lagersted | Filter = 3000 | ✓ Kritisk |
| BWART | Bevegelsestype | Filter = 201 (vareuttak til kostnadssted) og 647 (levering til transittbeholdning) | ✓ Kritisk |
| BUDAT | Bokføringsdato | Datofilter 2024–2025 | ✓ Kritisk |
| MENGE | Forbruksmengde | Faktisk forbruk ut fra lager | ✓ Kritisk |
| MEINS | Enhet | Kontroll mot MARA.MEINS | Bør ha |
| KOSTL | Kostnadssted | Kontekst – hvilken avdeling | Bør ha |

> 🔴 **FORBRUK UT fra lager til avdeling** – BWART=201 = vareuttak til kostnadssted.
> To filer – én per år (~135 000 rader hver). Slås sammen i Python med pd.concat() før aggregering.
> Aggreger MENGE per MATNR per måned (BUDAT) → 24 måneder for CV/XYZ-beregning.
> Totalforbruk per MATNR per år = etterspørsel D i EOQ-formelen.

---

### 8. EKKO – Innkjøpsordrehode
*Filter: BSTYP=F, BSART=ZNB, EKGRP=3000 og 300, BEDAT=01.01.2024–31.12.2025*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| EBELN | Ordrenummer | Nøkkel → EKPO | ✓ Kritisk |
| BEDAT | Ordredato | Datofilter 2024–2025 | ✓ Kritisk |
| EKORG | Innkjøpsorganisasjon | Filter Helse Bergen | ✓ Kritisk |
| BSTYP | Ordrekategori | Filter = F (bestilling) | ✓ Kritisk |
| BSART | Bestillingstype | Filter = ZNB (Helse Bergen) | ✓ Kritisk |
| EKGRP | Innkjøpsgruppe | Filter = 3000 og 300 (forsyningslager) | ✓ Kritisk |
| LIFNR | Leverandørnummer | Kontekst / rapportering | Bør ha |
| FRGKE | Frigivelsesstatus | Ekskluder ufrigitte ordrer | Bør ha |

> Med filtrene BSTYP=F, BSART=ZNB og EKGRP=3000+300 gir dette 13 154 rader for 2024–2025 – godt innenfor SE16H-grensen på 50 000.

---

### 9. EKPO – Innkjøpsordreposisjon
*Filter: EBELN fra EKKO, MATNR fra MDMA, WERKS=3300, LGORT=3000, LOEKZ=blank*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| EBELN | Ordrenummer | Kobling EKKO | ✓ Kritisk |
| EBELP | Posisjonsnummer | Nøkkel → EKBE | ✓ Kritisk |
| MATNR | Artikkelnummer | Kobling masterdata | ✓ Kritisk |
| WERKS | Anlegg | Filter = 3300 | ✓ Kritisk |
| MENGE | Bestilt kvantum | EOQ-avvik, ordrefrekvens | ✓ Kritisk |
| NETPR | Nettopris | ABC-verdiberegning | ✓ Kritisk |
| PEINH | Prisenhet | Korreksjon av NETPR | ✓ Kritisk |
| NETWR | Nettoordre­verdi | ABC direkte | ✓ Kritisk |
| LOEKZ | Sletteflagg | Filter = blank | ✓ Kritisk |
| ELIKZ | Leveringsavsluttet-flagg | Identifiser ufullstendige leveranser | Bør ha |
| PSTYP | Posisjonstype | Ekskluder avropspos. (PSTYP=5) | Bør ha |

> Forventet antall rader: **8 240** med filter EBELN fra EKKO + LGORT=3000.

---

### 10. EKBE – Varemottak per ordreposisjon
*Filter: EBELN+EBELP fra EKPO, BEWTP=E, BWART=101, BUDAT=01.01.2024–31.12.2025 – forventet 9 004 rader*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| EBELN | Ordrenummer | Kobling | ✓ Kritisk |
| EBELP | Posisjonsnummer | Kobling | ✓ Kritisk |
| MATNR | Artikkelnummer | Kobling | ✓ Kritisk |
| BEWTP | Bevegelseskategori | Filter = E (varemottak) | ✓ Kritisk |
| BWART | Bevegelsestype | Filter = 101 (ekskluder 102 reverseringer) | ✓ Kritisk |
| BUDAT | Bokføringsdato | Datofilter 2024–2025 | ✓ Kritisk |
| MENGE | Mottatt kvantum | Varemottak fra leverandør – EOQ-avvik (bestilt vs mottatt) | ✓ Kritisk |
| WRBTR | Verdi NOK | ABC-kontroll | ✓ Kritisk |
| SHKZG | Debet/kreditindikator (S/H) | Netto mottatt kvantum | ✓ Kritisk |

> 🔵 **INNKJØP INN til lager fra leverandør** – ikke forbruk.
> BWART=101 = faktisk varemottak. BWART=102 = reversering – ekskludert.
> Brukes til EOQ-avvik: sammenlign bestilt (EKPO.MENGE) mot faktisk mottatt (EKBE.MENGE).
> Netto per MATNR: sum(MENGE der SHKZG='S') − sum(MENGE der SHKZG='H')

---

### 11. EINA – Leverandør-artikkel-infopost
*Filter: MATNR fra MDMA, WERKS=3300*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATNR | Artikkelnummer | Kobling | Bør ha |
| WERKS | Anlegg | Filter = 3300 | Bør ha |
| LIFNR | Leverandørnummer | Identifisere primærleverandør | Bør ha |
| INFNR | Infopostnummer | Nøkkel → EINE for leveringstid | Bør ha |
| MINBM | Minimumsbestilling | EOQ-validering | Bør ha |

> Artikler med flere leverandører gir multiple rader. Bruk leverandøren med høyest EKBE-volum som primærleverandør.

---

### 12. EINE – Leveringstid per infopost
*Filter: INFNR fra EINA*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| INFNR | Infopostnummer | Kobling fra EINA | Bør ha |
| WEBAZ | Leveringstid (dager) | EOQ / ROP | Bør ha |
| EKORG | Innkjøpsorganisasjon | Kontekst | Bør ha |

> EINE inneholder ingen MATNR – kobles alltid via EINA.INFNR → EINE.INFNR.

---

### 13. T023T – Varegruppenavn
*Filter: MATKL fra MARA, SPRAS=NO*

| Felt | Beskrivelse | Brukes til | Status |
|---|---|---|---|
| MATKL | Varegruppe (kode) | Kobling fra MARA | Bør ha |
| SPRAS | Språk | Filter = NO | Bør ha |
| WGBEZ | Varegruppenavn | Lesbar gruppering | Bør ha |

---

## Koblingsnøkler – masterfil

| Fra | Via felt | Til | Formål |
|---|---|---|---|
| MARD | MATNR | Alle tabeller | Basis for alle koblinger |
| EINA | INFNR | EINE | Leveringstid per artikkel |
| MDMA | MATNR | Masterfile | ABC og XYZ per lagersted |
| MARA | MATKL | T023T | Varegruppenavn |
| EKKO | EBELN | EKPO | Ordrehode → posisjon |
| EKPO | EBELN + EBELP | EKBE | Posisjon → faktiske mottak |
| MSEG | MATNR (aggregert per måned) | Masterfile | Månedlig forbruk, CV, EOQ etterspørsel D |
| EKPO + EKBE | MATNR | Masterfile | Ordrefrekvens, EOQ-avvik |

---

## Datakvalitetskontroller

| Kontroll | Hva du sjekker | Tiltak |
|---|---|---|
| MATNR-telling | Unike MATNR per tabell vs. MARD | Avvik > 10 % krever undersøkelse |
| MDMA dekningsgrad | Andel MATNR uten ZZABC / ZZXYZ | Rapporter – beregn selv som fallback |
| Pris = 0 | MBEW.STPRS = 0 eller null | Ekskluder fra ABC |
| Nullforbruk | MSEG sum MENGE = 0 for alle måneder | Ekskluder – inaktiv artikkel |
| Prisenhet ≠ 1 | MBEW.PEINH ≠ 1 | Korriger: pris = STPRS ÷ PEINH |
| EKBE returer | SHKZG = 'H' > 20 % | Summer netto S minus H |
| Nullbeholdning | LABST + EINME + UMLME = 0 | Vurder eksklusjon |
| Innfasingsartikler | Første BUDAT i MSEG | Start CV fra første aktive måned |

---

*LOG650 – Helse Bergen · WERKS 3300 · LGORT 3000 · Februar 2026 · v1.0*
