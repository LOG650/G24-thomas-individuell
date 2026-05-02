# Peer review – G22 sin rapport

| Felt | Innhold |
|---|---|
| Vurderende gruppe | G24 – Thomas Ekrem Jensen |
| Vurdert gruppe | G22 – Frida Berge-Robertson, Sebastian Vambheim Thunestvedt |
| Rapporttittel | Datadrevet vurdering av hyllekapasitet vs. etterspørsel (Space Management) i dagligvarebutikk |
| Dato | 2026-05-02 |

## Helhetsinntrykk

Rapporten er et faglig solid og fokusert arbeid med klar problemforankring i en realistisk leverandør–kjede-forhandling hos Coop Extra. LP-formuleringen i §6 er stringent, sensitivitetsanalysen i §7.3 er overbevisende, og §8.2 er ærlig om sju eksplisitte begrensninger (B1–B7). Reproduserbarheten er god, og bokmålet holder høy akademisk standard.

Hovedutfordringene ligger på fire områder: (a) hovedfunnet (+49,8 % marginvektet gevinst i S2) hviler på en lineær plasselastisitet (β=1) som ligger langt over empirisk benchmark — Eisend (2014) sin meta-analyse finner β ≈ 0,17 i snitt, med staples-kategorier i det laveste sjiktet — slik at usikkerhetsbåndet rundt gevinsten blir uklart; (b) datagrunnlaget (1 butikk × 10 uker × 1 kategori) gjør generaliseringspåstanden i §9 noe sterk; (c) en enkel ABC-/heuristikk-baseline kunne vist hvor mye av gevinsten som faktisk krever LP, og publiserte SSAP-case-studier (jf. Hübner et al. 2020) rapporterer typisk profittforbedringer i størrelsesorden 5–15 % — flere ganger lavere enn S2; (d) formaliafelter på forsiden står fortsatt som [TBD]. Ingen av punktene er prinsipielle; alle bør være innenfor rekkevidde før innlevering.

## 1. Innledning

**Styrker.** Problemstillingen er tydelig formulert med to ledd (LP som beslutningsstøtte og dokumenterbart salgspotensial), og er forankret i en reell informasjonsasymmetri mellom leverandør og kjede. Avgrensningen til én butikk og én leverandørs portefølje er klar, og de fire antakelsene i §1.4 gir leseren en god ramme.

**Forbedring.** Forsiden mangler totalt sidetall, veileder og båndleggingsstatus ("[TBD]" på flere felt). Disse feltene er obligatoriske ifølge skriveveiledningens kap. 4.9.1 og bør være ferdig utfylt ved innlevering. Forskningsformålene (i)/(ii) kunne vært koblet enda skarpere til problemstillingens to ledd.

**Forslag.** Fyll inn alle [TBD]-feltene før innlevering. Vurder å nummerere RQ1/RQ2 eksplisitt slik at de speiler analysens to deler.

## 2. Litteratur og teori

**Styrker.** God dekning av SSAP-tradisjonen (Curhan 1972, Hübner et al. 2020, Dösterhöft et al. 2021). Romelastisitet, out-of-stock-litteraturen og kategoristyringsperspektivet (Klement & Hübner 2023) kobles godt til egen problemstilling. Stor andel nyere kilder gir et oppdatert kunnskapsgrunnlag, og synteseavsnittet inn mot problemstillingen er ryddig.

**Forbedring (anbefaling).** To punkter:
- *Category-captain-rollen* er introdusert i §2.3, men bør kobles tydeligere til forhandlingssituasjonen: hvilke beslutninger leverandøren kan påvirke, hvilke data kjeden holder tilbake, og hvor grensen går mellom beslutningsstøtte og partsinnlegg.
- *To referanser bør verifiseres mot kildens metadata før innlevering*:
  - «Dösterhöft, T., Hübner, A. & Schaal, K. (2021). Exact optimization and decomposition approaches for shelf space allocation. *EJOR*»: Tittelen *«Exact optimization and decomposition approaches for shelf space allocation»* (EJOR 299(2), 2022) er av **Çağlar Gençosman & Begen** — ikke Hübner-gruppen. Det finnes derimot en faktisk Hübner-paper fra 2021 av **Hübner, Düsterhöft & Ostermeier**, men den har tittelen *«Shelf space dimensioning and product allocation in retail stores»* (EJOR 292(1), pp. 155–171). To papers ser ut til å ha smeltet sammen i G22s oppføring.
  - «Klement, N. & Hübner, A. (2023). Decision support for managing assortments, shelf space, and replenishment in retail. *FSMJ*»: Det FSMJ-paperet er av **Hübner & Kuhn (2023)**, ikke Klement & Hübner.

**Forslag.** Vurder å utvide §2.3 med 2–4 setninger som kobler category-captain-teorien direkte til leverandørens informasjonsasymmetri og JBP-/hylleforhandling. Sjekk i tillegg de to flaggede referansene mot DOI/publisher-metadata før innlevering, og kjør gjerne hele referanselisten gjennom et lignende verifiseringssjekk.

## 3. Metode

**Styrker.** LP-formuleringen i §6 er presist beskrevet med mengder, parametre, beslutningsvariabler, målfunksjon og restriksjonene R1–R5. Pipelinen (datarensing → deskriptiv/ABC → LP → sensitivitet) er reproduserbar, pseudonymiseringen er ryddig, og datakvaliteten dokumenteres konkret.

**Forbedring.**
- *Lineær plasselastisitet (B2)*: Antakelsen s(f) = λ·f er erkjent som øvre grense, men gevinsten ved en realistisk β<1 kvantifiseres ikke. Eisend (2014, *Journal of Retailing*) sin meta-analyse av 1 268 estimater finner gjennomsnittlig β ≈ 0,17, lavest for commodities, deretter staples, høyest for impulskjøp. Drikkekategorier ligger typisk i staples-sjiktet, altså langt under 1. Lineæritet ligger derfor flere ganger over empirisk benchmark, og dette er trolig antakelsen som styrer hovedfunnet mest.
- *overserve_factor λ=2,0*: Litteraturbegrunnet (Gholami & Bhakoo 2025, range 1,5–3,0), men ikke kategorikalibrert mot drikkekategorien spesifikt. Sensitivitetsanalysen kompenserer delvis, men en setning om hvorfor 2,0 er et rimelig base case for nettopp denne kategorien hadde styrket valget.
- *Notasjon*: x_i og y_i mister subscript i senere avsnitt; i §3.1/§6 brukes både s(f) = λ·f^α og den lineære varianten s(f) = λ·f, noe som kan misforstås.
- *Bruttomargin (B5)*: Brukes som vekt i målfunksjonen. Dekningsbidrag (etter logistikk-, kampanje- og hyllekostnad) ville vært mer økonomisk korrekt, særlig i ytterkant av margindistribusjonen.

**Forslag.** Legg inn et kort regnestykke i §7.3 eller en fotnote: "Hvis β=0,2 (Eisend-snitt for staples) i stedet for 1, ville S2-gevinsten vært ca. X %." Stram også notasjonen rundt x_i, y_i og s(f), og diskuter biasen fra bruttomargin med ett konkret eksempel.

## 4. Analyse og resultater

**Styrker.** De tre scenariene (S1/S2/S3) har tydelig hver sin rolle: øvre grense, hovedanbefaling og konservativ. Sankey-diagrammet (Fig 7.2b) visualiserer omfordelingen godt, og sensitivitetsheatmapet (Fig 7.5) viser at gevinsten er positiv på tvers av det realistiske parameterområdet. Tabell 7.2 er detaljert nok til å være handlingsrettet.

**Forbedring.**
- *A4-anomali*: Reduksjonen fra 168 → 3 facings drives mekanisk av lav utnyttelse i et smalt 10-ukers vindu på et høyvolumprodukt. I en LP er dette korrekt, men 1-kolli-gulv på et volatilt A-produkt er en reell risiko for utsolgtsituasjoner. Bør drøftes med en eksplisitt advarsel om at modellen forutsetter stabilt forbruksmønster.
- *Uke 15 / A2-spike*: Flagget som sannsynlig kampanjeuke (412 mot snitt 191), men beholdt uten å vise eksklusjonens effekt i sensitivitet.
- *Manglende baseline*: LP-resultatet sammenlignes kun med status quo. En enkel "doble alle A, halver alle C"-heuristikk ville vist hvor mye av +49,8 % som faktisk krever LP-presisjon. Til kalibrering: Hübner et al. (2020) sin case-studie med data fra en av Tysklands største dagligvarekjeder rapporterer profittøkning på opp til 15 % — flere ganger lavere enn G22s estimat.
- *Tabell 7.2*: 34 rader gjør at mønstre per ABC-klasse blir krevende å fange. En oppsummerende tabell per klasse kunne supplert.

**Forslag.** Skriv et kort avsnitt om A4-tilfellet som flytter funnet fra "modellen sier" til "modellen + skjønn". Kjør én enkel ABC-heuristikk-baseline og vis kontrasten i Tabell 7.1, slik at leseren ser merverdien av LP framfor en enkel tommelfingerregel.

## 5. Diskusjon

**Styrker.** B1–B7 er ærlige og spesifikke. Skillet mellom funn (butikkspesifikt) og metode (overførbar) er ryddig, og sammenligningen mot empirisk litteratur plasserer funnet i en faglig sammenheng.

**Forbedring.** Begrensningene drøftes likeverdig; det mangler en *prioritering* av hvilken antakelse som styrer hovedfunnet mest. Sannsynligvis B2 (lineæritet) > B3 (overserve) > B6 (kannibalisering). Implikasjonene for praksis kan også strammes med et regneeksempel som gjør funnet håndfast i forhandlingsrommet.

**Forslag.** Lag en kort oversikt over B1–B7 sortert etter hvilken som styrer resultatet mest. Legg til ett avsnitt om hvordan resultatet faktisk brukes i et JBP-møte — hvilke tre tall tar leverandøren med inn i rommet?

## 6. Konklusjon

**Styrker.** Konsis 5-punkts oppsummering som svarer direkte på problemstillingen. Ærlighet om at λ_sec og lineæritet trenger empirisk validering. Forslagene til videre forskning er konkrete.

**Forbedring.** Generaliseringspåstanden ("kan rulles ut på tvers av butikker og kategorier") fremstår noe sterk gitt at antakelsene (lineæritet, λ=2) er kategorispesifikke. Det er den ene formuleringen som bryter med rapportens ellers nøkterne tone. Bidragsformuleringen er tynn på det metodiske: rapporten leverer faktisk noe nytt — en lavterskel pipeline som kun bruker leverandørens egne data — men dette nedtones.

**Forslag.** Stram generaliseringspåstanden, f.eks. "Metoden er overførbar betinget av at antakelsene om elastisitet og overserve gjelder per kategori." Legg til en eksplisitt setning om det metodiske bidraget i siste avsnitt.

## 7. Skriveflyt, formalia og helhetsinntrykk

**Styrker.** Bokmålet holder høy kvalitet, avsnittsstrukturen er god, og APA 7 følges konsekvent. KI-bruken er åpent dokumentert. Sammendrag og abstract er substansielle, og figurene er gjennomgående godt integrert i teksten.

**Forbedring.**
- *Forsiden*: Sidetall, veileder og båndleggingsstatus står fortsatt som [TBD]. Skriveveiledningen (kap. 4.9.1) krever at disse er ferdig utfylt. Dette inkluderer avklaring av taushetserklæringen med Coop, som per dato heller ikke står som bekreftet.
- *Anonymisering og lesbarhet*: Marginanonymisering og pseudonymdekoding (A1–C11) er nødvendig av NDA-hensyn, men gjør sammendraget noe opakt for ekstern leser. Én samlet tabellnote med marginrange og én setning om at pseudonymene dekker «kullsyreholdige drikker, energidrikk, sportsdrikk og vann» ville hjulpet uten å bryte konfidensialitet.
- *Kode-tilgjengelighet*: Vedlegg refererer til Git-repo, men ingen konkret URL eller commit-hash er oppgitt. Dette er ikke et formelt krav, men ville gjort reproduserbarhetspåstanden mer etterprøvbar.

**Forslag.** Siste-runde-formaliasjekk: fyll inn alle forsidefelter, avklar Coop-status formelt, vurder å legge ved repo-URL og commit-hash i Vedlegg A.

## Prioriterte anbefalinger

1. Kvantifiser effekten av empirisk realistisk plasselastisitet (Eisend 2014: β ≈ 0,17 i snitt, lavere for drikkekategorier) — eller merk tydeligere at S2-gevinsten ligger flere størrelsesordener over empirisk benchmark.
2. Legg inn en enkel ABC-/heuristikk-baseline, og kalibrer mot publiserte SSAP-case-studier (typisk 5–15 % profittforbedring, jf. Hübner et al. 2020) for å plassere +49,8 % i et faglig perspektiv.
3. Drøft A4-reduksjonen og A2-spiken eksplisitt som risikopunkter der modellresultatet bør møtes med faglig skjønn.
4. Prioriter B1–B7 etter forventet effekt på hovedfunnet, og gjør JBP-implikasjonen mer konkret med 2–3 tall leverandøren faktisk tar med i forhandlingsrommet.
5. Stram generaliseringspåstanden: metoden er overførbar, men gevinstnivået krever kategori- og butikkspesifikk validering.
6. Fyll ut [TBD]-feltene på forsiden og avklar båndlegging/Coop-status formelt før innlevering.
7. Styrk reproduserbarheten ved å oppgi repo-URL og commit-hash i Vedlegg A.
