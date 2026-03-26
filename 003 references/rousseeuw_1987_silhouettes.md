# Silhouettes: A Graphical Aid to the Interpretation and Validation of Cluster Analysis

**Forfatter:** Peter J. Rousseeuw
**År:** 1987
**Kilde/Journal:** Journal of Computational and Applied Mathematics, 20, 53–65

---

## Sammendrag

Artikkelen introduserer silhouette-koeffisienten, et grafisk og numerisk verktøy for evaluering og validering av klyngeanalyse. For hvert datapunkt beregnes en silhouette-verdi $s_i$ basert på forholdet mellom gjennomsnittlig intra-klyngeavstand ($a_i$) og gjennomsnittlig avstand til nærmeste naboklynge ($b_i$). Verdien ligger i intervallet $[-1, 1]$, der verdier nær 1 indikerer god klyngetilhørighet, verdier nær 0 indikerer overlapp, og negative verdier indikerer mulig feilklassifisering. Gjennomsnittlig silhouette-score over alle punkter brukes til å sammenligne ulike verdier av $K$ og velge optimalt antall klynger.

## Nøkkelord

`silhouette-koeffisient` · `klyngevalidering` · `klyngeanalyse` · `K-valg` · `intern evalueringsmetrikk`

## Relevans for oppgaven

Artikkelen er primærkilden for silhouette-score, som brukes i K-means-analysen (avsnitt 5.4/6.4) til å velge optimalt antall klynger (K = 3) og evaluere klyngestrukturens kvalitet på trenings- og testdata.

## Referanse (APA 7)

Rousseeuw, P. J. (1987). Silhouettes: A graphical aid to the interpretation and validation of cluster analysis. *Journal of Computational and Applied Mathematics*, *20*, 53–65. https://doi.org/10.1016/0377-0427(87)90125-7
