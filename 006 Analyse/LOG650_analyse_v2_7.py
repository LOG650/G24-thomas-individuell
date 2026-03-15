"""
LOG650 – Helse Bergen Lageranalyse
===================================
Komplett analysescript: ABC, XYZ, EOQ, K-means, Regelmotor, Besparelse
Forfatter : Thomas Ekrem Jensen
Versjon   : 2.7

ENDRINGER FRA v2.6 → v2.7:
    Besparelsesmodell: Bᵢ = fᵢ_obs × S × r  →  B_HVFS = Σ ΔTCᵢ × g
    Grunnlag: alle OVERFØR_HVFS  →  OVERFØR_HVFS ∩ FOR_MANGE_ORDRER
    g-sats: worst=50%, base=75%, best=100%
    BESPARELSE-ark: ny EOQ-tabell + r-kolonne for transparens
    Summary-print: ny formel + begge tall (ny + gammel)
    LGORT i plot-titler og Excel: 3000 → 3001
    K-means bugfiks: numpy float64-krasj → bool()-cast i PROFIL-lambda

OPPSETT – kjør én gang i terminalen:
    pip install -r requirements.txt

    Eller manuelt:
    pip install pandas==2.2.2 openpyxl==3.1.2 xlsxwriter==3.2.0 \
                scikit-learn==1.4.2 matplotlib==3.8.4 numpy==1.26.4
    (seaborn er ikke i bruk og trengs ikke installeres)

MAPPESTRUKTUR:
    LOG650/
    ├── data/
    │   └── MASTERFILE_V1.xlsx   ← legg masterfilen her
    ├── plots/                    ← lages automatisk av scriptet
    ├── requirements.txt
    └── LOG650_analyse.py         ← dette scriptet

KJØRING:
    python LOG650_analyse.py

OUTPUT:
    LOG650_Resultater.xlsx        ← 7 ark med alle analyseresultater
    plots/01_ABC_Pareto.png
    plots/02_ABC_XYZ_Matrise.png
    plots/03_EOQ_Avvik.png
    plots/04_Kmeans_Klynger.png
    plots/05_HVFS_Besparelse.png

PARAMETERE (juster om nødvendig):
    S_ORDRE_KOSTNAD  = 750 kr     (bestillingskostnad)
    H_HOLDE_PROSENT  = 20%        (lagerhold som andel av enhetspris)
    UTTREKK_MÅNEDER  = 24         (EKPO dekker 2024+2025)
    LEAD_TIME_DEFAULT= 14 dager   (fallback – reservert ROP-modul)
    ABC_A            = 80%        (kumulativ grense A-klasse)
    ABC_B            = 95%        (kumulativ grense B-klasse)
    XYZ_X            = CV < 0.50  (stabilt forbruk)
    XYZ_Y            = CV < 1.00  (variabelt forbruk)
    XYZ_Z            = CV ≥ 1.00  (uregelmessig forbruk)

KJENTE BESLUTNINGER (dokumentert i LOG650_Masterfil_Datafunn.md):
    D-01  Kun aktive artikler: D_ANNUAL > 0 ELLER TOTAL_STOCK > 0 – 709 av 1006
          (mer robust enn kun TOTAL_STOCK > 0: fanger artikler med forbruk men nullbeholdning)
    D-02  UNIT_PRICE = STPRS ÷ PEINH (PEINH kan være 10 eller 100)
    D-03  ABC_VALUE = D_ANNUAL × UNIT_PRICE der TOTAL_NETWR mangler
    D-04  XYZ beregnes fra CV – ZZXYZ brukes kun til validering
    D-05  LEAD_TIME_DAYS fallback = 14 dager (6% dekning fra EINA/EINE)
    D-06  MSEG_STATUS blank → AKTIV
    D-07  ABC_VALUE_SOURCE: TOTAL_NETWR > 0 kreves for EKPO
    D-08  ACTUAL_FREQ = ORDER_COUNT × (12 ÷ UTTREKK_MÅNEDER)
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import matplotlib.ticker as mticker
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.model_selection import train_test_split
import warnings, os
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────
# KONFIGURASJON
# ─────────────────────────────────────────────
INPUT_FILE   = 'MASTERFILE V1.xlsx'
OUTPUT_XLSX  = 'LOG650_Resultater.xlsx'
OUTPUT_PLOTS = 'plots'
os.makedirs(OUTPUT_PLOTS, exist_ok=True)

# EOQ parametere
S_ORDRE_KOSTNAD   = 750    # kr per bestilling
H_HOLDE_PROSENT   = 0.20   # 20% av enhetspris per år
UTTREKK_MÅNEDER   = 24     # EKPO dekker 2024+2025 = 24 måneder
# LEAD_TIME_DEFAULT brukes til ROP (reorder point) – ikke EOQ-formelen.
# ROP = D_daglig × LEAD_TIME. Reservert for fremtidig ROP-modul.
LEAD_TIME_DEFAULT = 14     # dager – fallback der EINA/EINE mangler

# ABC grenser
ABC_A = 0.80
ABC_B = 0.95

# XYZ grenser (CV)
XYZ_X = 0.50
XYZ_Y = 1.00

# Besparelse
# Besparelse – transaksjonsreduksjonsfaktor r (scenarioanalyse)
# r representerer andelen av lokale transaksjoner som elimineres ved overføring til HVFS.
# Scenarioverdiene er valgt som konservativt intervall rundt et midtpunkt:
#   worst  r=0.06 – minimal effekt: noe koordinering, men mye gjenværende lokal håndtering
#   base   r=0.12 – moderat effekt: basert på erfaringstall fra tilsvarende sentraliseringsprosjekter
#   best   r=0.20 – høy effekt: nær full eliminering av lokale bestillingstransaksjoner
# RAPPORT-NOTE § 5.6: begrunn satsene eksplisitt, f.eks. med referanse til
# Axsäter (2015) eller intern Helse Bergen/HVFS-estimering. Presiser at r er et
# scenario-parameter, ikke et empirisk estimert tall fra dette datasettet.
# g = realiseringsgrad av EOQ-besparelse for artikler med FOR_MANGE_ORDRER
# Grunnlag: B_HVFS = Σ ΔTCᵢ × g  (kun OVERFØR_HVFS ∩ FOR_MANGE_ORDRER)
# ΔTCᵢ = TC_ACTUAL − TC_OPTIMAL  (beregnet i modul 3, lagret som TC_AVVIK_KR)
# g=1.00: full realisering | g=0.75: base case | g=0.50: konservativt
G_REALISERING = {'worst': 0.50, 'base': 0.75, 'best': 1.00}
# r beholdes for transparens i Excel-arket (ekvivalent r = B_HVFS / (Σfᵢ × S))
TRANSAKSJONSBESPARELSE_R = {'best': 0.20, 'base': 0.12, 'worst': 0.06}  # kun til sammenligning

STYLE = {
    'bg':     '#ffffff',
    'card':   '#ffffff',
    'A':      '#1565C0',
    'B':      '#FB8C00',
    'C':      '#E53935',
    'X':      '#2E7D32',
    'Y':      '#7B1FA2',
    'Z':      '#D81B60',
    'text':   '#212121',
    'grid':   '#E0E0E0',
}

print("=" * 60)
print("LOG650 – Helse Bergen Lageranalyse v2.7")
print("=" * 60)

# ─────────────────────────────────────────────
# LES INN DATA
# ─────────────────────────────────────────────
print("\n[1/7] Leser inn MASTERFILE...")

import openpyxl
wb = openpyxl.load_workbook(INPUT_FILE, data_only=True)
ws = wb['MASTERFILE']
data = list(ws.iter_rows(values_only=True))

for i, row in enumerate(data[:15]):
    if sum(1 for c in row if c is not None) > 5:
        header_idx = i
        headers = [str(c) if c is not None else f'COL{j}' for j, c in enumerate(row)]
        break

rows = [row for row in data[header_idx+1:] if any(c is not None for c in row)]
df = pd.DataFrame(rows, columns=headers)
df['MATNR'] = df['MATNR'].astype(str)

# D-05: Definer aktivitet fra D_ANNUAL og TOTAL_STOCK
df['IS_ACTIVE'] = (
    (pd.to_numeric(df['D_ANNUAL'],    errors='coerce').fillna(0) > 0) |
    (pd.to_numeric(df['TOTAL_STOCK'], errors='coerce').fillna(0) > 0)
)

# D-06: Fyll blanke MSEG_STATUS med 'AKTIV' (normal drift)
df['MSEG_STATUS'] = df['MSEG_STATUS'].fillna('AKTIV')

n_total = len(df)
# --- FILTER: behold kun aktive artikler (D-01) ---
df = df[df['IS_ACTIVE']].reset_index(drop=True)

print(f"   → {n_total} artikler lastet inn, {len(df)} aktive (IS_ACTIVE=True)")

# ─────────────────────────────────────────────
# MODUL 1 – ABC-ANALYSE
# ─────────────────────────────────────────────
print("\n[2/7] Modul 1: ABC-analyse...")

# Bruk TOTAL_NETWR, fyll med D_ANNUAL * UNIT_PRICE der mangler
df['ABC_VALUE'] = df['TOTAL_NETWR'].copy()
mask_beregnet = df['ABC_VALUE'].isna() & df['D_ANNUAL'].notna() & df['UNIT_PRICE'].notna()
df.loc[mask_beregnet, 'ABC_VALUE'] = df.loc[mask_beregnet, 'D_ANNUAL'] * df.loc[mask_beregnet, 'UNIT_PRICE']

# D-03: TOTAL_NETWR > 0 er betingelsen – ikke bare notna()
df['ABC_VALUE_SOURCE'] = df.apply(
    lambda row: 'EKPO' if pd.notna(row['TOTAL_NETWR']) and row['TOTAL_NETWR'] > 0
                else 'BEREGNET', axis=1
)

# Sorter og beregn kumulativ andel
df_abc = df[df['ABC_VALUE'].notna()].copy()
df_abc = df_abc.sort_values('ABC_VALUE', ascending=False).reset_index(drop=True)
total_value = df_abc['ABC_VALUE'].sum()
df_abc['ABC_CUM_VALUE']  = df_abc['ABC_VALUE'].cumsum()
df_abc['ABC_CUM_PCT']    = df_abc['ABC_CUM_VALUE'] / total_value
df_abc['ABC_RANK']       = range(1, len(df_abc)+1)
df_abc['ABC_RANK_PCT']   = df_abc['ABC_RANK'] / len(df_abc)

df_abc['ABC_CLASS'] = 'C'
df_abc.loc[df_abc['ABC_CUM_PCT'] <= ABC_A, 'ABC_CLASS'] = 'A'
df_abc.loc[(df_abc['ABC_CUM_PCT'] > ABC_A) & (df_abc['ABC_CUM_PCT'] <= ABC_B), 'ABC_CLASS'] = 'B'

# ABC_VALUE og ABC_VALUE_SOURCE er allerede i df – merge kun nye kolonner
df = df.merge(df_abc[['MATNR','ABC_CUM_PCT','ABC_CLASS']], on='MATNR', how='left')

abc_summary = df_abc.groupby('ABC_CLASS').agg(
    ANTALL=('MATNR','count'),
    TOTAL_VERDI=('ABC_VALUE','sum')
).reindex(['A','B','C'])
abc_summary['VERDI_PCT'] = abc_summary['TOTAL_VERDI'] / total_value * 100
abc_summary['ANTALL_PCT'] = abc_summary['ANTALL'] / len(df_abc) * 100

print(f"   → ABC ferdig: {len(df_abc)} artikler")
for cls in ['A','B','C']:
    r = abc_summary.loc[cls]
    print(f"      {cls}: {int(r.ANTALL)} art ({r.ANTALL_PCT:.0f}%) – kr {r.TOTAL_VERDI:,.0f} ({r.VERDI_PCT:.0f}%)")

# ─────────────────────────────────────────────
# MODUL 2 – XYZ-KLASSIFISERING
# ─────────────────────────────────────────────
print("\n[3/7] Modul 2: XYZ-klassifisering...")

df_xyz = df[df['CV'].notna()].copy()

df_xyz['XYZ_CLASS'] = 'Z'
df_xyz.loc[df_xyz['CV'] <= XYZ_X, 'XYZ_CLASS'] = 'X'
df_xyz.loc[(df_xyz['CV'] > XYZ_X) & (df_xyz['CV'] <= XYZ_Y), 'XYZ_CLASS'] = 'Y'

df = df.merge(df_xyz[['MATNR','XYZ_CLASS']], on='MATNR', how='left')

# Validering mot SAP ZZXYZ
df_val = df[df['ZZXYZ'].notna() & df['XYZ_CLASS'].notna()].copy()
match = (df_val['ZZXYZ'] == df_val['XYZ_CLASS']).sum()
val_pct = match / len(df_val) * 100 if len(df_val) > 0 else 0

xyz_summary = df_xyz.groupby('XYZ_CLASS').agg(
    ANTALL=('MATNR','count'),
    CV_SNITT=('CV','mean')
).reindex(['X','Y','Z'])

print(f"   → XYZ ferdig: {len(df_xyz)} artikler")
for cls in ['X','Y','Z']:
    r = xyz_summary.loc[cls]
    print(f"      {cls}: {int(r.ANTALL)} art – snitt CV={r.CV_SNITT:.2f}")
print(f"   → SAP-validering: {val_pct:.0f}% samsvar ({match}/{len(df_val)} artikler med ZZXYZ)")

# ─────────────────────────────────────────────
# MODUL 3 – EOQ-AVVIKSANALYSE
# ─────────────────────────────────────────────
print("\n[4/7] Modul 3: EOQ-avviksanalyse...")

df_eoq = df[df['D_ANNUAL'].notna() & df['UNIT_PRICE'].notna() & df['ORDER_COUNT'].notna()].copy()
df_eoq = df_eoq[df_eoq['D_ANNUAL'] > 0].copy()

df_eoq['H_COST']       = df_eoq['UNIT_PRICE'] * H_HOLDE_PROSENT
df_eoq['EOQ']          = np.sqrt(2 * df_eoq['D_ANNUAL'] * S_ORDRE_KOSTNAD / df_eoq['H_COST'])
df_eoq['EOQ_FREQ']     = df_eoq['D_ANNUAL'] / df_eoq['EOQ']
# Annualiser ORDER_COUNT fra uttrekksperioden til per-år-frekvens
df_eoq['ACTUAL_FREQ']  = df_eoq['ORDER_COUNT'] * (12 / UTTREKK_MÅNEDER)
df_eoq['FREQ_AVVIK_PCT'] = ((df_eoq['ACTUAL_FREQ'] - df_eoq['EOQ_FREQ']) / df_eoq['EOQ_FREQ'] * 100).round(1)

# Terskelparameter τ_f = 1,5 (rapport ligning 5.9a–c).
# Ekvivalens: fᵢ_obs > 1,5·f*ᵢ  ⟺  FREQ_AVVIK_PCT > 50
#             fᵢ_obs < 0,5·f*ᵢ  ⟺  FREQ_AVVIK_PCT < −50
# Begrunnelse: FREQ_AVVIK_PCT = (fobs − f*) / f* × 100,
# så FREQ_AVVIK_PCT > 50 er identisk med fobs > 1,5·f*.
df_eoq['EOQ_STATUS'] = 'OK'
df_eoq.loc[df_eoq['FREQ_AVVIK_PCT'] >  50, 'EOQ_STATUS'] = 'FOR_MANGE_ORDRER'
df_eoq.loc[df_eoq['FREQ_AVVIK_PCT'] < -50, 'EOQ_STATUS'] = 'FOR_FÅ_ORDRER'

# Faktisk vs optimal totalkostnad
df_eoq['TC_OPTIMAL']  = np.sqrt(2 * df_eoq['D_ANNUAL'] * S_ORDRE_KOSTNAD * df_eoq['H_COST'])
df_eoq['TC_ACTUAL']   = (df_eoq['ACTUAL_FREQ'] * S_ORDRE_KOSTNAD +
                          (df_eoq['D_ANNUAL'] / (2 * df_eoq['ACTUAL_FREQ'].clip(lower=0.1))) * df_eoq['H_COST'])
df_eoq['TC_AVVIK_KR'] = (df_eoq['TC_ACTUAL'] - df_eoq['TC_OPTIMAL']).round(0)

df = df.merge(df_eoq[['MATNR','EOQ','EOQ_FREQ','FREQ_AVVIK_PCT','EOQ_STATUS','TC_AVVIK_KR']], on='MATNR', how='left')

eoq_dist = df_eoq['EOQ_STATUS'].value_counts()
total_avvik_kr = df_eoq['TC_AVVIK_KR'].sum()
print(f"   → EOQ ferdig: {len(df_eoq)} artikler")
print(f"      For mange ordrer: {eoq_dist.get('FOR_MANGE_ORDRER',0)}")
print(f"      OK: {eoq_dist.get('OK',0)}")
print(f"      For få ordrer: {eoq_dist.get('FOR_FÅ_ORDRER',0)}")
print(f"      Estimert totalt avvik: kr {total_avvik_kr:,.0f}/år")

# ─────────────────────────────────────────────
# MODUL 4 – K-MEANS KLYNGEANALYSE
# ─────────────────────────────────────────────
print("\n[5/7] Modul 4: K-means klyngeanalyse...")

# Featurevektor etter rapport § 5.4 (ligning 5.11):
#   xᵢ = [z(ln(CVᵢ)), z(ln(vᵢ+1)), z(ln(|ΔTCᵢ|+1))]
# Krever at CV, ABC_VALUE og TC_AVVIK_KR er tilgjengelige.
# ABC_VALUE er satt i modul 1; TC_AVVIK_KR er satt i modul 3.
km_cols_needed = ['CV', 'ABC_VALUE', 'TC_AVVIK_KR']
df_km = df[df[km_cols_needed].notna().all(axis=1)].copy()
df_km = df_km[df_km['CV'].notna() & (df_km['ABC_VALUE'] > 0)].copy()

# Log-transformasjon for å redusere skjevhet
df_km['LN_CV']    = np.log(df_km['CV'].clip(lower=1e-6))       # ln(CV) – CV er alltid > 0
df_km['LN_V']     = np.log1p(df_km['ABC_VALUE'].clip(lower=0))  # ln(vᵢ+1)
# |ΔTCᵢ| – absolutt kostnadsavvik (bevisst designvalg):
# Klyngene grupperer artikler etter STØRRELSEN på kostnadsavviket, ikke retningen.
# Begrunnelse: både over- og underfrekvente artikler med stort ΔTC er analytisk
# interessante – de representerer potensiell ineffektivitet i begge retninger.
# Signert avvik ville splitte disse i to separate klynger uten metodisk gevinst.
df_km['LN_DTCABS']= np.log1p(df_km['TC_AVVIK_KR'].abs())        # ln(|ΔTCᵢ|+1)

features = ['LN_CV', 'LN_V', 'LN_DTCABS']
X = df_km[features].values

# ── TRAIN/TEST SPLIT (80/20) – gjøres FØR all modelltrening ──────────────
# Begrunnelse: sikrer at testdata er genuint usett under trening.
# Silhouette score på testdata gir et ærlig mål på generaliserbarhet.
idx_all = np.arange(len(df_km))
idx_train, idx_test = train_test_split(idx_all, test_size=0.20, random_state=42)

X_train = X[idx_train]
X_test  = X[idx_test]

print(f"   → Train/test-split: {len(idx_train)} tren ({len(idx_train)/len(X)*100:.0f}%) / "
      f"{len(idx_test)} test ({len(idx_test)/len(X)*100:.0f}%)")

# StandardScaler fittes KUN på treningsdata – forhindrer datalekkasje
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)   # fit + transform treningsdata
X_test_scaled  = scaler.transform(X_test)         # kun transform testdata

# Eksporter splits for sporbarhet
df_km_reset = df_km.reset_index(drop=True)
df_km_reset.iloc[idx_train].to_csv('LOG650_kmeans_train.csv', index=False)
df_km_reset.iloc[idx_test].to_csv('LOG650_kmeans_test.csv', index=False)

# Elbow + silhouette for K=2..7 – basert på treningsdata
inertia, sil_scores = [], []
K_range = range(2, 8)
for k in K_range:
    km_tmp = KMeans(n_clusters=k, random_state=42, n_init=50)
    labels_tmp = km_tmp.fit_predict(X_train_scaled)
    inertia.append(km_tmp.inertia_)
    sil_scores.append(silhouette_score(X_train_scaled, labels_tmp))

best_k = K_range[np.argmax(sil_scores)]
print(f"   → Beste K = {best_k} (silhouette tren = {max(sil_scores):.3f})")

# Tren endelig modell KUN på treningsdata
km_final = KMeans(n_clusters=best_k, random_state=42, n_init=50)
km_final.fit(X_train_scaled)

# Prediker klynger for tren og test separat
train_labels = km_final.predict(X_train_scaled)
test_labels  = km_final.predict(X_test_scaled)

sil_train = silhouette_score(X_train_scaled, train_labels)
sil_test  = silhouette_score(X_test_scaled,  test_labels)
print(f"   → Silhouette tren:  {sil_train:.3f}")
print(f"   → Silhouette test:  {sil_test:.3f}  (generaliserbarhet)")
if abs(sil_train - sil_test) > 0.05:
    print(f"   ⚠  Avvik tren/test > 0.05 – vurder om K er for høyt")

# Sett klyngelabel tilbake på df_km (1-basert for lesbarhet)
df_km = df_km_reset.copy()
df_km.loc[idx_train, 'CLUSTER'] = train_labels + 1
df_km.loc[idx_test,  'CLUSTER'] = test_labels  + 1
df_km['DATASETT'] = 'tren'
df_km.loc[idx_test, 'DATASETT'] = 'test'

# X_scaled for plotting (kombinert, kun brukt til visualisering etter trening)
X_scaled = np.vstack([X_train_scaled, X_test_scaled])
idx_combined = np.concatenate([idx_train, idx_test])
labels_combined = np.concatenate([train_labels, test_labels])

# Profiler klyngene – sentroidverdier i original skala for tolkning
cluster_profile = df_km.groupby('CLUSTER').agg(
    ANTALL=('MATNR','count'),
    ANTALL_TREN=('DATASETT', lambda x: (x=='tren').sum()),
    ANTALL_TEST=('DATASETT', lambda x: (x=='test').sum()),
    CV_SNITT=('CV','mean'),
    ABC_VERDI_SNITT=('ABC_VALUE','mean'),
    TC_AVVIK_SNITT=('TC_AVVIK_KR','mean'),
).round(2)
cluster_profile['SIL_TREN'] = round(sil_train, 3)
cluster_profile['SIL_TEST'] = round(sil_test, 3)

# Identifiser K_OVERFØR: klynge(r) med lavest normalisert CV og høyest normalisert verdi
# Bruker rangering: rang CV (stigende) + rang verdi (synkende) → lavest sum = K_OVERFØR
cluster_profile['RANG_CV']    = cluster_profile['CV_SNITT'].rank(ascending=True)
cluster_profile['RANG_VERDI'] = cluster_profile['ABC_VERDI_SNITT'].rank(ascending=False)
cluster_profile['RANG_SUM']   = cluster_profile['RANG_CV'] + cluster_profile['RANG_VERDI']
cluster_profile['K_OVERFØR']  = cluster_profile['RANG_SUM'] == cluster_profile['RANG_SUM'].min()

# Lag profil-streng for output
cluster_profile['PROFIL'] = cluster_profile.apply(
    lambda r: (
        f"K_OVERFØR_KANDIDAT | CV={r.CV_SNITT:.2f} Verdi={int(r.ABC_VERDI_SNITT)}kr ΔTC={int(r.TC_AVVIK_SNITT)}kr"
        if bool(r['K_OVERFØR']) else
        f"CV={r.CV_SNITT:.2f} Verdi={int(r.ABC_VERDI_SNITT)}kr ΔTC={int(r.TC_AVVIK_SNITT)}kr"
    ), axis=1
)

# Sett K_OVERFØR-flagg tilbake til df_km for bruk i regelmotor
k_overfør_ids = set(cluster_profile[cluster_profile['K_OVERFØR']].index.tolist())
df_km['K_OVERFØR'] = df_km['CLUSTER'].isin(k_overfør_ids)

df = df.merge(df_km[['MATNR','CLUSTER','K_OVERFØR']], on='MATNR', how='left')
df['K_OVERFØR'] = df['K_OVERFØR'].fillna(False)

print(f"   → Klynger (featurevektor: z(ln(CV)), z(ln(v+1)), z(ln(|ΔTC|+1))):")
for c, r in cluster_profile.iterrows():
    tag = ' ← K_OVERFØR' if r['K_OVERFØR'] else ''
    print(f"      Klynge {c} ({int(r.ANTALL)} art): CV={r.CV_SNITT:.2f}, verdi={int(r.ABC_VERDI_SNITT)}kr, ΔTC={int(r.TC_AVVIK_SNITT)}kr{tag}")

# ─────────────────────────────────────────────
# MODUL 5 – REGELMOTOR OG HVFS-ANBEFALING
# ─────────────────────────────────────────────
print("\n[6/7] Modul 5: Regelmotor...")

def hvfs_anbefaling(row):
    """
    Regelmotor etter Tabell 5.2 i rapporten.
    Dimensjoner: ABC_CLASS, XYZ_CLASS, EOQ_STATUS, K_OVERFØR.
    Regler evalueres sekvensielt; Z-override sjekkes alltid først.
    """
    abc     = row.get('ABC_CLASS')
    xyz     = row.get('XYZ_CLASS')
    eoq     = row.get('EOQ_STATUS')       # 'FOR_MANGE_ORDRER' | 'OK' | 'FOR_FÅ_ORDRER' | NaN
    k_over  = bool(row.get('K_OVERFØR'))  # True = klynge med HVFS-egnet profil

    if pd.isna(abc) or pd.isna(xyz):
        return 'MANGLER_DATA'

    # --- Regel 1: Z-override (alltid behold) ---
    if xyz == 'Z':
        return 'BEHOLD_LOKALT'

    # --- Regel 2: C + Y → behold (lav verdi, variabelt) ---
    if abc == 'C' and xyz == 'Y':
        return 'BEHOLD_LOKALT'

    # --- Regel 3: A/B + X + for mange ordrer → klart overfør ---
    if abc in ('A', 'B') and xyz == 'X' and eoq == 'FOR_MANGE_ORDRER':
        return 'OVERFØR_HVFS'

    # --- Regel 4: A/B + X + OK/for få + K_OVERFØR → overfør ---
    if abc in ('A', 'B') and xyz == 'X' and k_over:
        return 'OVERFØR_HVFS'

    # --- Regel 5: A/B + Y + K_OVERFØR → overfør ---
    if abc in ('A', 'B') and xyz == 'Y' and k_over:
        return 'OVERFØR_HVFS'

    # --- Regel 6: A/B + X + OK/for få, ikke K_OVERFØR → nærmere vurdering ---
    if abc in ('A', 'B') and xyz == 'X':
        return 'VURDER_NÆRMERE'

    # --- Regel 7: A/B + Y + ikke K_OVERFØR → nærmere vurdering ---
    if abc in ('A', 'B') and xyz == 'Y':
        return 'VURDER_NÆRMERE'

    # --- Regel 8: C + X → nærmere vurdering (stabilt, men lav verdi) ---
    if abc == 'C' and xyz == 'X':
        return 'VURDER_NÆRMERE'

    return 'VURDER_NÆRMERE'

def hvfs_begrunnelse(row):
    abc  = row.get('ABC_CLASS', '')
    xyz  = row.get('XYZ_CLASS', '')
    eoq  = row.get('EOQ_STATUS', '')
    kov  = bool(row.get('K_OVERFØR'))
    rec  = row.get('HVFS_ANBEFALING', '')
    eoq_txt = f', EOQ={eoq}' if pd.notna(eoq) and eoq else ''
    kov_txt = ', K_OVERFØR' if kov else ''
    if rec == 'OVERFØR_HVFS':
        return f'{abc}/{xyz}{eoq_txt}{kov_txt} – sentrallagerkandidat'
    elif rec == 'BEHOLD_LOKALT':
        return f'{abc}/{xyz} – Z-artikkel eller lav verdi/variabelt forbruk'
    elif rec == 'VURDER_NÆRMERE':
        return f'{abc}/{xyz}{eoq_txt}{kov_txt} – krever individuell vurdering'
    return 'Utilstrekkelig data'

df['HVFS_ANBEFALING'] = df.apply(hvfs_anbefaling, axis=1)
df['HVFS_BEGRUNNELSE'] = df.apply(hvfs_begrunnelse, axis=1)

rec_summary = df['HVFS_ANBEFALING'].value_counts()
print(f"   → Regelmotor ferdig:")
for rec, cnt in rec_summary.items():
    print(f"      {rec}: {cnt} artikler")

# ─────────────────────────────────────────────
# MODUL 7 – BESPARELSESBEREGNING
# ─────────────────────────────────────────────
print("\n[7/7] Modul 7: Besparelsesberegning...")

# Ny besparelsesmodell (v2.7):
#   B_HVFS = Σ ΔTCᵢ × g
#
# ΔTCᵢ  = TC_ACTUAL − TC_OPTIMAL  (allerede beregnet i modul 3 som TC_AVVIK_KR)
# g     = realiseringsgrad: worst=50%, base=75%, best=100%
# Grunnlag: kun artikler med HVFS_ANBEFALING='OVERFØR_HVFS' OG EOQ_STATUS='FOR_MANGE_ORDRER'
#           → de som faktisk har overfrekvens det er mulig å realisere besparelse på
#
# Gammel modell (Bᵢ = fᵢ_obs × S × r) beholdes som referansekolonne i Excel
# for transparens og sammenlignbarhet med v2.5/v2.6.

df_hvfs = df[
    (df['HVFS_ANBEFALING'] == 'OVERFØR_HVFS') &
    (df['EOQ_STATUS']      == 'FOR_MANGE_ORDRER')
].copy()

# Koble inn ACTUAL_FREQ fra EOQ-modulen (TC_AVVIK_KR er allerede i df fra modul 3 merge)
df_hvfs = df_hvfs.merge(
    df_eoq[['MATNR', 'ACTUAL_FREQ']].drop_duplicates('MATNR'),
    on='MATNR', how='left'
)

# TC_AVVIK_KR skal være positiv for FOR_MANGE_ORDRER (TC_actual > TC_optimal)
# Sett negativ/null til 0 defensivt (bør ikke forekomme i dette filteret)
df_hvfs['TC_AVVIK_KR'] = df_hvfs['TC_AVVIK_KR'].clip(lower=0)

n_grunnlag = len(df_hvfs)
n_overfør_total = (df['HVFS_ANBEFALING'] == 'OVERFØR_HVFS').sum()
n_uten_besparelse = n_overfør_total - n_grunnlag  # OVERFØR men ikke FOR_MANGE

tc_avvik_sum = df_hvfs['TC_AVVIK_KR'].sum()

df_hvfs['B_WORST'] = df_hvfs['TC_AVVIK_KR'] * G_REALISERING['worst']
df_hvfs['B_BASE']  = df_hvfs['TC_AVVIK_KR'] * G_REALISERING['base']
df_hvfs['B_BEST']  = df_hvfs['TC_AVVIK_KR'] * G_REALISERING['best']

savings = {
    'worst': df_hvfs['B_WORST'].sum(),
    'base':  df_hvfs['B_BASE'].sum(),
    'best':  df_hvfs['B_BEST'].sum(),
}

# Gammel formel (Bᵢ = fᵢ_obs × S × r) beholdes som referanse
df_hvfs['B_OLD_BASE'] = (
    df_hvfs['ACTUAL_FREQ'].fillna(0) * S_ORDRE_KOSTNAD * TRANSAKSJONSBESPARELSE_R['base']
)
savings_old_base = df_hvfs['B_OLD_BASE'].sum()

total_hvfs_freq = df_hvfs['ACTUAL_FREQ'].fillna(0).sum()

print(f"   → Grunnlag: {n_grunnlag} artikler (OVERFØR_HVFS ∩ FOR_MANGE_ORDRER)")
print(f"   → Ekskludert {n_uten_besparelse} OVERFØR-artikler uten FOR_MANGE (OK/FOR_FÅ)")
print(f"   → Σ ΔTCᵢ (realiserbar EOQ-overfrekvenskostnad): kr {tc_avvik_sum:,.0f}/år")
print(f"   → Formel: B_HVFS = Σ ΔTCᵢ × g")
for s, v in savings.items():
    g_pct = G_REALISERING[s] * 100
    print(f"      {s.capitalize()} (g={g_pct:.0f}%): kr {v:,.0f}/år")
print(f"   → Ref. gammel formel (Bᵢ=fᵢ_obs×S×r, r=12%): kr {savings_old_base:,.0f}/år")

# ─────────────────────────────────────────────
# MODUL 8 – SENSITIVITETSANALYSE
# ─────────────────────────────────────────────
# Rapport § 5.3 / § 5.6 lover variasjon av tre parametere:
#   S  (bestillingskostnad):    500 / 750 / 1 000 kr
#   h  (holdekostnadssats):     0,15 / 0,20 / 0,25
#   τ_f (EOQ-terskel):          1,25 / 1,50 / 2,00
#
# For hvert (S, h)-par beregnes EOQ og TC på nytt.
# τ_f påvirker bare EOQ_STATUS-fordelingen, ikke TC direkte.
# Besparelsessatsen r holdes fast på base case (0,12) her –
# r-sensitiviteten dekkes allerede av worst/base/best i modul 7.

print("\n[8/8] Modul 8: Sensitivitetsanalyse...")

S_VALS   = [500, 750, 1000]
H_VALS   = [0.15, 0.20, 0.25]
TAU_VALS = [1.25, 1.50, 2.00]
R_BASE   = 0.12

sens_rows = []

for S_val in S_VALS:
    for h_val in H_VALS:
        for tau_val in TAU_VALS:

            # EOQ og TC med disse parameterverdiene
            H_cost  = df_eoq['UNIT_PRICE'] * h_val
            eoq_s   = np.sqrt(2 * df_eoq['D_ANNUAL'] * S_val / H_cost)
            f_star  = df_eoq['D_ANNUAL'] / eoq_s
            tc_opt  = np.sqrt(2 * df_eoq['D_ANNUAL'] * S_val * H_cost)
            tc_act  = (df_eoq['ACTUAL_FREQ'] * S_val
                       + (df_eoq['D_ANNUAL'] / (2 * df_eoq['ACTUAL_FREQ'].clip(lower=0.1))) * H_cost)
            tc_avvik = (tc_act - tc_opt)

            # EOQ_STATUS med τ_f – rekn frekvensavvik på nytt for denne (S, h)-kombinen
            freq_avvik_pct = ((df_eoq['ACTUAL_FREQ'] - f_star) / f_star * 100)
            tau_pct = (tau_val - 1) * 100   # τ_f=1.5 → 50 %
            status = pd.Series('OK', index=df_eoq.index)
            status[freq_avvik_pct >  tau_pct] = 'FOR_MANGE_ORDRER'
            status[freq_avvik_pct < -tau_pct] = 'FOR_FÅ_ORDRER'

            n_mange = (status == 'FOR_MANGE_ORDRER').sum()
            n_ok    = (status == 'OK').sum()
            n_faa   = (status == 'FOR_FÅ_ORDRER').sum()

            # HVFS-kandidater med denne parameterkombinen:
            # Rekn ΔTC for OVERFØR-artiklar med FOR_MANGE_ORDRER under denne (S, h)
            # Regelmotor-anbefalinga endrast ikkje av S/h/τ, men TC-avviket gjer det
            overfør_mask = df_eoq['MATNR'].isin(df_hvfs['MATNR'])
            tc_avvik_sens = (tc_act - tc_opt).clip(lower=0)
            b_total   = (tc_avvik_sens[overfør_mask & (status == 'FOR_MANGE_ORDRER')]
                         * G_REALISERING['base']).sum()

            sens_rows.append({
                'S (kr/ordre)':          S_val,
                'h (holdekostnadssats)': h_val,
                'τ_f (terskel)':         tau_val,
                'For mange ordrer (n)':  n_mange,
                'OK (n)':                n_ok,
                'For få ordrer (n)':     n_faa,
                'ΔTC total (kr/år)':     round(tc_avvik.sum()),
                'B_HVFS base g=75% (kr/år)': round(b_total),
            })

df_sens = pd.DataFrame(sens_rows)

# Oppsummering: vis variasjon langs hver akse
print(f"   → {len(df_sens)} scenariokombiner (3×3×3)")
print(f"   → B_HVFS (g=75%): "
      f"min kr {df_sens['B_HVFS base g=75% (kr/år)'].min():,.0f} – "
      f"maks kr {df_sens['B_HVFS base g=75% (kr/år)'].max():,.0f}")
print(f"   → ΔTC total: "
      f"min kr {df_sens['ΔTC total (kr/år)'].min():,.0f} – "
      f"maks kr {df_sens['ΔTC total (kr/år)'].max():,.0f}")

# ─────────────────────────────────────────────
# VISUALISERINGER
# ─────────────────────────────────────────────
print("\n[*] Lager visualiseringer...")

plt.rcParams.update({
    'figure.facecolor': '#ffffff',
    'axes.facecolor': '#ffffff',
    'axes.edgecolor': '#cccccc',
    'axes.labelcolor': STYLE['text'],
    'text.color': STYLE['text'],
    'xtick.color': STYLE['text'],
    'ytick.color': STYLE['text'],
    'grid.color': STYLE['grid'],
    'grid.linewidth': 0.5,
    'font.family': 'serif',
    'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
    'axes.spines.top': False,
    'axes.spines.right': False,
})

# ── VIS 1: Pareto ABC ──
fig, ax1 = plt.subplots(figsize=(12, 6))

colors_bar = [STYLE['A'] if c=='A' else STYLE['B'] if c=='B' else STYLE['C']
              for c in df_abc['ABC_CLASS']]
ax1.bar(range(len(df_abc)), df_abc['ABC_VALUE'], color=colors_bar, alpha=0.75, width=1.0)
ax1.set_xlabel('Artikler (rangert etter verdi)', fontsize=11)
ax1.set_ylabel('Innkjøpsverdi (NOK)', fontsize=11)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x/1e6:.1f}M'))

ax2 = ax1.twinx()
ax2.plot(range(len(df_abc)), df_abc['ABC_CUM_PCT']*100, color='#333333', linewidth=2)
ax2.set_ylabel('Kumulativ andel (%)', fontsize=11)
ax2.set_ylim(0, 105)

ax1.axvline(x=(df_abc['ABC_CLASS']=='A').sum()-1, color=STYLE['A'], linestyle='--', alpha=0.7, linewidth=1.5, label='A/B grense (80%)')
ax1.axvline(x=(df_abc['ABC_CLASS'].isin(['A','B'])).sum()-1, color=STYLE['B'], linestyle='--', alpha=0.7, linewidth=1.5, label='B/C grense (95%)')

patches = [mpatches.Patch(color=STYLE[c], label=f'{c}: {int(abc_summary.loc[c,"ANTALL"])} art ({abc_summary.loc[c,"ANTALL_PCT"]:.0f}%) – {abc_summary.loc[c,"VERDI_PCT"]:.0f}% av verdi') for c in ['A','B','C']]
ax1.legend(handles=patches, loc='upper right', fontsize=9, framealpha=0.9)
ax1.set_title('ABC-analyse – Pareto-diagram\nHelse Bergen WERKS 3300 LGORT 3001 (2024–2025)', fontsize=13, pad=15)
ax1.grid(axis='y', alpha=0.2)
plt.tight_layout()
plt.savefig(f'{OUTPUT_PLOTS}/01_ABC_Pareto.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ 01_ABC_Pareto.png")

# ── VIS 2: ABC/XYZ Matrise ──
fig, ax = plt.subplots(figsize=(9, 7))
df_matrix = df[df['ABC_CLASS'].notna() & df['XYZ_CLASS'].notna()].copy()
matrix = df_matrix.groupby(['ABC_CLASS','XYZ_CLASS']).size().unstack(fill_value=0).reindex(index=['A','B','C'], columns=['X','Y','Z'], fill_value=0)

cell_colors = {
    ('A','X'): '#81C784', ('A','Y'): '#81C784', ('A','Z'): '#FFB74D',
    ('B','X'): '#81C784', ('B','Y'): '#FFB74D', ('B','Z'): '#E57373',
    ('C','X'): '#FFB74D', ('C','Y'): '#E57373', ('C','Z'): '#E57373',
}

for i, abc in enumerate(['A','B','C']):
    for j, xyz in enumerate(['X','Y','Z']):
        val = matrix.loc[abc, xyz]
        color = cell_colors.get((abc,xyz), '#f5f5f5')
        ax.add_patch(plt.Rectangle((j, 2-i), 1, 1, facecolor=color, edgecolor='#ffffff', linewidth=2))
        total_in_class = matrix.loc[abc].sum()
        pct = val/len(df_matrix)*100 if len(df_matrix)>0 else 0
        ax.text(j+0.5, 2-i+0.5, f'{val}\n({pct:.0f}%)', ha='center', va='center',
                fontsize=13, fontweight='bold', color='#212121')

ax.set_xlim(0,3); ax.set_ylim(0,3)
ax.set_xticks([0.5,1.5,2.5]); ax.set_xticklabels(['X\n(CV<0.5)\nStabilt','Y\n(CV 0.5–1.0)\nVariabelt','Z\n(CV>1.0)\nUregelmessig'], fontsize=10)
ax.set_yticks([0.5,1.5,2.5]); ax.set_yticklabels(['C\nLav verdi','B\nMidlere','A\nHøy verdi'], fontsize=10)
ax.set_title('ABC/XYZ Klassifiseringsmatrise\nHelse Bergen WERKS 3300 LGORT 3001', fontsize=13, pad=15)

legend_info = [
    mpatches.Patch(color='#81C784', label='Klare HVFS-kandidater (AX/AY/BX)'),
    mpatches.Patch(color='#FFB74D', label='Vurder nærmere'),
    mpatches.Patch(color='#E57373', label='Behold lokalt (CZ/CY/BZ)'),
]
ax.legend(handles=legend_info, loc='lower right', fontsize=9, framealpha=0.9)
plt.tight_layout()
plt.savefig(f'{OUTPUT_PLOTS}/02_ABC_XYZ_Matrise.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ 02_ABC_XYZ_Matrise.png")

# ── VIS 3: EOQ-avvik fordeling ──
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

df_eoq_plot = df_eoq[df_eoq['FREQ_AVVIK_PCT'].between(-300, 300)].copy()

ax = axes[0]
colors_eoq = [STYLE['C'] if v > 50 else STYLE['A'] if v < -50 else STYLE['B']
              for v in df_eoq_plot['FREQ_AVVIK_PCT']]
ax.scatter(range(len(df_eoq_plot)), df_eoq_plot['FREQ_AVVIK_PCT'].values,
           c=colors_eoq, alpha=0.5, s=15)
ax.axhline(50, color=STYLE['C'], linestyle='--', alpha=0.7, label='50% grense')
ax.axhline(-50, color=STYLE['A'], linestyle='--', alpha=0.7)
ax.axhline(0, color='#999999', linestyle='-', alpha=0.4)
ax.set_title('EOQ-avvik per artikkel (%)', fontsize=11)
ax.set_ylabel('Avvik fra optimal frekvens (%)')
ax.set_xlabel('Artikler')
ax.grid(alpha=0.2)

ax2 = axes[1]
status_counts = df_eoq['EOQ_STATUS'].value_counts()
colors_bar2 = [STYLE['C'] if 'MANGE' in s else STYLE['A'] if 'FÅ' in s else STYLE['B']
               for s in status_counts.index]
bars = ax2.bar(status_counts.index, status_counts.values, color=colors_bar2, alpha=0.8)
ax2.set_title('EOQ-statusfordeling', fontsize=11)
ax2.set_ylabel('Antall artikler')
for bar, val in zip(bars, status_counts.values):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+2, str(val),
             ha='center', fontsize=10, fontweight='bold')
ax2.grid(axis='y', alpha=0.2)

fig.suptitle('EOQ-avviksanalyse – Helse Bergen 2024–2025', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_PLOTS}/03_EOQ_Avvik.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ 03_EOQ_Avvik.png")

# ── VIS 4: K-means klyngeplot – faktisk feature-rom med tren/test-markering ──
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

cluster_colors = ['#1565C0','#FB8C00','#43A047','#E53935','#7B1FA2','#D81B60']

# Rekonstruer z-score-verdier i kombinert rekkefølge for plotting
z_ln_cv  = X_scaled[np.argsort(idx_combined), 0]
z_ln_v   = X_scaled[np.argsort(idx_combined), 1]
z_ln_dtc = X_scaled[np.argsort(idx_combined), 2]
clusters_plot = labels_combined[np.argsort(idx_combined)] + 1  # 1-basert

is_test = df_km['DATASETT'].values == 'test'

ax = axes[0]
for c in sorted(df_km['CLUSTER'].unique()):
    ci = int(c)
    mask_all  = clusters_plot == ci
    mask_tren = mask_all & ~is_test
    mask_test = mask_all &  is_test
    k_tag = ' ★' if cluster_profile.loc[c, 'K_OVERFØR'] else ''
    # Treningsdata – fylt sirkel
    ax.scatter(z_ln_cv[mask_tren], z_ln_v[mask_tren],
               c=cluster_colors[ci-1], alpha=0.6, s=20,
               label=f'K{ci}{k_tag} tren ({mask_tren.sum()})')
    # Testdata – åpen diamant (genuine generaliseringssjekk)
    ax.scatter(z_ln_cv[mask_test], z_ln_v[mask_test],
               facecolors='none', edgecolors=cluster_colors[ci-1],
               marker='D', alpha=0.85, s=24,
               label=f'K{ci}{k_tag} test ({mask_test.sum()})')
ax.set_xlabel('z(ln(CV))  ←stabil | variabel→')
ax.set_ylabel('z(ln(v+1))  ←lav verdi | høy verdi→')
ax.set_title(f'K-means (K={best_k}): Forbruksstabilitet vs Verdi\n'
             f'Sil tren={sil_train:.3f} | Sil test={sil_test:.3f}', fontsize=10)
ax.legend(fontsize=7, framealpha=0.9, ncol=2)
ax.grid(alpha=0.2)
ax.axvline(0, color='#cccccc', linestyle='--', alpha=0.5, linewidth=0.8)
ax.axhline(0, color='#cccccc', linestyle='--', alpha=0.5, linewidth=0.8)

ax2 = axes[1]
for c in sorted(df_km['CLUSTER'].unique()):
    ci = int(c)
    mask_all  = clusters_plot == ci
    mask_tren = mask_all & ~is_test
    mask_test = mask_all &  is_test
    k_tag = ' ★' if cluster_profile.loc[c, 'K_OVERFØR'] else ''
    ax2.scatter(z_ln_cv[mask_tren], z_ln_dtc[mask_tren],
                c=cluster_colors[ci-1], alpha=0.6, s=20,
                label=f'K{ci}{k_tag} tren')
    ax2.scatter(z_ln_cv[mask_test], z_ln_dtc[mask_test],
                facecolors='none', edgecolors=cluster_colors[ci-1],
                marker='D', alpha=0.85, s=24,
                label=f'K{ci}{k_tag} test')
ax2.set_xlabel('z(ln(CV))  ←stabil | variabel→')
ax2.set_ylabel('z(ln(|ΔTC|+1))  ←lavt avvik | høyt avvik→')
ax2.set_title(f'K-means (K={best_k}): Forbruksstabilitet vs Kostnadsavvik', fontsize=10)
ax2.grid(alpha=0.2)
ax2.axvline(0, color='#cccccc', linestyle='--', alpha=0.5, linewidth=0.8)
ax2.axhline(0, color='#cccccc', linestyle='--', alpha=0.5, linewidth=0.8)

fig.suptitle(
    f'K-means Klyngeanalyse – Helse Bergen  |  ★ = K_OVERFØR  |  ● tren  ◆ test\n'
    f'Featurevektor: z(ln(CV)), z(ln(v+1)), z(ln(|ΔTC|+1)) | '
    f'Sil tren={sil_train:.3f} | Sil test={sil_test:.3f}',
    fontsize=11, y=1.04
)
plt.tight_layout()
plt.savefig(f'{OUTPUT_PLOTS}/04_Kmeans_Klynger.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ 04_Kmeans_Klynger.png")

# ── VIS 5: HVFS-anbefaling ──
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

ax = axes[0]
rec_counts = df['HVFS_ANBEFALING'].value_counts()
colors_rec = {'OVERFØR_HVFS': '#43A047', 'BEHOLD_LOKALT': '#E53935', 'VURDER_NÆRMERE': '#FB8C00', 'MANGLER_DATA': '#9E9E9E'}
pie_colors = [colors_rec.get(r, '#9E9E9E') for r in rec_counts.index]
wedges, texts, autotexts = ax.pie(rec_counts.values, labels=None, colors=pie_colors,
                                   autopct='%1.0f%%', startangle=90,
                                   textprops={'color': '#212121', 'fontsize': 11})
ax.legend(rec_counts.index, loc='lower center', bbox_to_anchor=(0.5, -0.15),
          fontsize=8, framealpha=0.9)
ax.set_title('HVFS-anbefaling fordeling', fontsize=11)

ax2 = axes[1]
scenarios = ['Worst case\n(g=50%)', 'Base case\n(g=75%)', 'Best case\n(g=100%)']
values = [savings['worst']/1e3, savings['base']/1e3, savings['best']/1e3]
bars = ax2.bar(scenarios, values, color=['#E57373', '#FFB74D', '#81C784'], alpha=0.85, width=0.5)
ax2.set_ylabel('Estimert besparelse (TNOK/år)')
ax2.set_title(f'EOQ-besparelse: B = Σ ΔTCᵢ × g  (S={S_ORDRE_KOSTNAD} kr)', fontsize=11)
for bar, val in zip(bars, values):
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.5,
             f'kr {val:.0f}T', ha='center', fontsize=10, fontweight='bold')
ax2.grid(axis='y', alpha=0.2)

fig.suptitle('Regelmotor & Besparelsesanalyse – Helse Bergen', fontsize=13, y=1.02)
plt.tight_layout()
plt.savefig(f'{OUTPUT_PLOTS}/05_HVFS_Besparelse.png', dpi=300, bbox_inches='tight')
plt.close()
print("   ✅ 05_HVFS_Besparelse.png")

# ─────────────────────────────────────────────
# EXCEL OUTPUT
# ─────────────────────────────────────────────
print("\n[*] Skriver Excel-resultater...")

# Merge cluster profile into df for output
cluster_profile_out = cluster_profile[['PROFIL']].copy()
cluster_profile_out.index.name = 'CLUSTER'
df = df.merge(
    cluster_profile_out.rename(columns={'PROFIL':'CLUSTER_PROFIL'}),
    left_on='CLUSTER', right_index=True, how='left'
)

with pd.ExcelWriter(OUTPUT_XLSX, engine='xlsxwriter') as writer:
    wb_out = writer.book

    # Formats
    hdr_fmt  = wb_out.add_format({'bold': True, 'bg_color': '#2C2C2C', 'font_color': 'white', 'border': 1})
    a_fmt    = wb_out.add_format({'bg_color': '#14532d', 'font_color': 'white'})
    b_fmt    = wb_out.add_format({'bg_color': '#78350f', 'font_color': 'white'})
    c_fmt    = wb_out.add_format({'bg_color': '#7f1d1d', 'font_color': 'white'})
    num_fmt  = wb_out.add_format({'num_format': '#,##0.00'})
    int_fmt  = wb_out.add_format({'num_format': '#,##0'})
    pct_fmt  = wb_out.add_format({'num_format': '0.0%'})
    title_fmt = wb_out.add_format({'bold': True, 'font_size': 14, 'bg_color': '#1E3A5F', 'font_color': 'white'})
    grønn_fmt = wb_out.add_format({'bg_color': '#dcfce7', 'font_color': '#14532d'})
    gul_fmt   = wb_out.add_format({'bg_color': '#fef9c3', 'font_color': '#78350f'})
    rød_fmt   = wb_out.add_format({'bg_color': '#fee2e2', 'font_color': '#7f1d1d'})

    # ── Ark 1: MASTERFILE komplett ──
    output_cols = ['MATNR','MAKTX','MTART','WGBEZ','MEINS',
                   'ABC_CLASS','ABC_VALUE','ABC_VALUE_SOURCE','ABC_CUM_PCT',
                   'XYZ_CLASS','CV','ZZXYZ',
                   'CLUSTER','CLUSTER_PROFIL',
                   'EOQ','FREQ_AVVIK_PCT','EOQ_STATUS',
                   'HVFS_ANBEFALING','HVFS_BEGRUNNELSE',
                   'UNIT_PRICE','D_ANNUAL','TOTAL_NETWR','ORDER_COUNT','LEAD_TIME_DAYS']
    out_cols = [c for c in output_cols if c in df.columns]
    df_out = df[out_cols].copy()
    df_out.to_excel(writer, sheet_name='RESULTATER', index=False, startrow=1)
    ws_out = writer.sheets['RESULTATER']
    ws_out.write(0, 0, 'LOG650 – Analyseresultater – Helse Bergen WERKS 3300 LGORT 3001', title_fmt)
    ws_out.set_column('A:A', 12); ws_out.set_column('B:B', 35); ws_out.set_column('C:D', 15)
    ws_out.set_column('E:Z', 14)
    for col, name in enumerate(out_cols):
        ws_out.write(1, col, name, hdr_fmt)
    ws_out.autofilter(1, 0, len(df_out)+1, len(out_cols)-1)
    ws_out.freeze_panes(2, 0)
    print("   ✅ Ark: RESULTATER")

    # ── Ark 2: ABC-oppsummering ──
    abc_summary.reset_index().to_excel(writer, sheet_name='ABC_OPPSUMMERING', index=False, startrow=3)
    ws_abc = writer.sheets['ABC_OPPSUMMERING']
    ws_abc.write(0, 0, 'ABC-analyse – Oppsummering', title_fmt)
    ws_abc.write(1, 0, f'Totalt {len(df_abc)} artikler – totalverdi kr {total_value:,.0f}')
    ws_abc.set_column('A:E', 18)
    print("   ✅ Ark: ABC_OPPSUMMERING")

    # ── Ark 3: XYZ-oppsummering ──
    xyz_out = xyz_summary.copy()
    xyz_out['SAP_SAMSVAR_PCT'] = f'{val_pct:.1f}%'
    xyz_out.reset_index().to_excel(writer, sheet_name='XYZ_OPPSUMMERING', index=False, startrow=3)
    ws_xyz = writer.sheets['XYZ_OPPSUMMERING']
    ws_xyz.write(0, 0, 'XYZ-klassifisering – Oppsummering', title_fmt)
    ws_xyz.write(1, 0, f'SAP-validering: {val_pct:.1f}% samsvar ({match}/{len(df_val)} artikler)')
    ws_xyz.set_column('A:E', 20)
    print("   ✅ Ark: XYZ_OPPSUMMERING")

    # ── Ark 4: EOQ-oppsummering ──
    eoq_sum = pd.DataFrame({
        'Status': list(eoq_dist.index),
        'Antall artikler': list(eoq_dist.values),
        'Andel (%)': [f'{v/len(df_eoq)*100:.1f}%' for v in eoq_dist.values]
    })
    eoq_sum.to_excel(writer, sheet_name='EOQ_OPPSUMMERING', index=False, startrow=4)
    ws_eoq = writer.sheets['EOQ_OPPSUMMERING']
    ws_eoq.write(0, 0, 'EOQ-avviksanalyse – Oppsummering', title_fmt)
    ws_eoq.write(1, 0, f'Analysert: {len(df_eoq)} artikler | S = kr {S_ORDRE_KOSTNAD} | H = {H_HOLDE_PROSENT*100:.0f}%')
    ws_eoq.write(2, 0, f'Estimert totalt kostnadsavvik: kr {total_avvik_kr:,.0f}/år')
    ws_eoq.set_column('A:C', 22)
    print("   ✅ Ark: EOQ_OPPSUMMERING")

    # ── Ark 5: K-means klyngeprofiler ──
    cluster_profile.reset_index().to_excel(writer, sheet_name='KMEANS_PROFILER', index=False, startrow=3)
    ws_km = writer.sheets['KMEANS_PROFILER']
    ws_km.write(0, 0, f'K-means Klyngeanalyse – K={best_k} | Sil tren={sil_train:.3f} | Sil test={sil_test:.3f}', title_fmt)
    ws_km.write(1, 0, f'80/20 train/test-split (random_state=42) | Featurevektor: z(ln(CV)), z(ln(v+1)), z(ln(|ΔTC|+1)) – n_init=50, seed=42')
    ws_km.set_column('A:G', 20)
    print("   ✅ Ark: KMEANS_PROFILER")

    # ── Ark 6: HVFS-kandidater (OVERFØR ∩ FOR_MANGE, med Bᵢ per artikkel) ──
    hvfs_out_cols = [c for c in ['MATNR','MAKTX','ABC_CLASS','XYZ_CLASS','EOQ_STATUS','K_OVERFØR',
                                  'TC_AVVIK_KR','B_WORST','B_BASE','B_BEST','B_OLD_BASE',
                                  'ACTUAL_FREQ','ABC_VALUE','D_ANNUAL','UNIT_PRICE','CLUSTER_PROFIL']
                     if c in df_hvfs.columns]
    hvfs_out = df_hvfs[hvfs_out_cols].copy().sort_values('B_BASE', ascending=False)
    hvfs_out.to_excel(writer, sheet_name='HVFS_KANDIDATER', index=False, startrow=3)
    ws_hvfs = writer.sheets['HVFS_KANDIDATER']
    ws_hvfs.write(0, 0, f'HVFS-kandidater – {n_grunnlag} artikler (OVERFØR_HVFS ∩ FOR_MANGE_ORDRER)', title_fmt)
    ws_hvfs.write(1, 0,
        f'Ny modell: B_HVFS = Σ ΔTCᵢ × g  |  Base case (g=75%): kr {savings["base"]:,.0f}/år  '
        f'|  Ref. gammel formel (r=12%): kr {savings_old_base:,.0f}/år')
    ws_hvfs.set_column('A:A', 12); ws_hvfs.set_column('B:B', 35); ws_hvfs.set_column('C:P', 16)
    print("   ✅ Ark: HVFS_KANDIDATER")

    # ── Ark 7: Besparelse – EOQ-basert modell ──
    bes_data = pd.DataFrame({
        'Scenario':                   ['Worst case (g=50%)', 'Base case (g=75%)', 'Best case (g=100%)'],
        'Grunnlag (art.)':            [n_grunnlag] * 3,
        'Modell':                     ['B_HVFS = Σ ΔTCᵢ × g'] * 3,
        'Σ ΔTCᵢ (kr/år)':            [round(tc_avvik_sum)] * 3,
        'g (realiseringsgrad)':       [0.50, 0.75, 1.00],
        'B_HVFS (kr/år)':             [savings['worst'], savings['base'], savings['best']],
        'B_HVFS (TNOK/år)':           [round(savings['worst']/1e3,1),
                                       round(savings['base']/1e3,1),
                                       round(savings['best']/1e3,1)],
        'Ref: Bᵢ=fᵢ×S×r (r=12%) kr': [round(savings_old_base)] * 3,
        'Merknad':                    [
            'Konservativt – 50% av ΔTC realiseres',
            'Basis – 75% av ΔTC realiseres',
            'Optimistisk – full realisering av ΔTC',
        ],
    })
    bes_data.to_excel(writer, sheet_name='BESPARELSE', index=False, startrow=3)
    ws_bes = writer.sheets['BESPARELSE']
    ws_bes.write(0, 0, 'Besparelsesberegning – EOQ-basert modell (v2.7)', title_fmt)
    ws_bes.write(1, 0,
        f'Grunnlag: {n_grunnlag} art. (OVERFØR_HVFS ∩ FOR_MANGE_ORDRER)  |  '
        f'Ekskludert: {n_uten_besparelse} OVERFØR-art. uten overfrekvens  |  '
        f'Σ ΔTC = kr {tc_avvik_sum:,.0f}/år')
    ws_bes.set_column('A:I', 28)
    print("   ✅ Ark: BESPARELSE")

    # ── Ark 8: Sensitivitetsanalyse ──
    df_sens.to_excel(writer, sheet_name='SENSITIVITET', index=False, startrow=3)
    ws_sens = writer.sheets['SENSITIVITET']
    ws_sens.write(0, 0, 'Sensitivitetsanalyse – 27 scenariokombiner (S × h × τ_f)', title_fmt)
    ws_sens.write(1, 0,
        f'S ∈ {{500, 750, 1000}} kr  |  h ∈ {{0,15, 0,20, 0,25}}  |  τ_f ∈ {{1,25, 1,50, 2,00}}'
        f'  |  g = 75% (base case)')
    ws_sens.set_column('A:H', 26)
    # Betinget formattering: fargeskala på B_HVFS-kolonnen (kolonne H, index 7)
    ws_sens.conditional_format(4, 7, 3 + len(df_sens), 7, {
        'type': '3_color_scale',
        'min_color': '#fee2e2',
        'mid_color': '#fef9c3',
        'max_color': '#dcfce7',
    })
    print("   ✅ Ark: SENSITIVITET")

print(f"\n{'='*60}")
print("ANALYSE FULLFØRT – v2.7")
print(f"{'='*60}")
print(f"Excel:  {OUTPUT_XLSX}")
print(f"Plots:  {OUTPUT_PLOTS}/")
print(f"\nOppsummering:")
print(f"  Totalt analysert:    {len(df)} artikler (aktive)")
print(f"  ABC A:               {int(abc_summary.loc['A','ANTALL'])} art – {abc_summary.loc['A','VERDI_PCT']:.0f}% av verdi")
print(f"  XYZ X (stabilt):     {int(xyz_summary.loc['X','ANTALL'])} art")
print(f"  K-means K:           {best_k} | Sil tren={sil_train:.3f} | Sil test={sil_test:.3f}")
print(f"  HVFS anbefalt:       {rec_summary.get('OVERFØR_HVFS',0)} art (alle OVERFØR)")
print(f"  Besparelsesgrunnlag: {n_grunnlag} art (OVERFØR ∩ FOR_MANGE_ORDRER)")
print(f"  Ny formel (g-modell):")
print(f"    B_HVFS = Σ ΔTCᵢ × g  |  Σ ΔTC = kr {tc_avvik_sum:,.0f}/år")
for s, v in savings.items():
    g_pct = G_REALISERING[s] * 100
    print(f"    {s.capitalize()} (g={g_pct:.0f}%): kr {v:,.0f}/år")
print(f"  Ref. gammel formel (r=12%): kr {savings_old_base:,.0f}/år")
print(f"  Sensitivitet:        {len(df_sens)} scenariokombiner")
