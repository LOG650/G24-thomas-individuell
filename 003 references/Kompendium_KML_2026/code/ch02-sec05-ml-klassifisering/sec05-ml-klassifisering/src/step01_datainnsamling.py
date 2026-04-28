"""
Steg 1: Datainnsamling for ML-basert lagerklassifisering
========================================================
Genererer et syntetisk SKU-katalog + transaksjonsdata for 2500 SKU-er
observert daglig i 2 aar. For hver SKU har vi rike attributter:

- Salgsvolum (aarlig etterspoersel)
- Etterspoerselsvariabilitet (CV)
- Pris og kapitalkostnad
- Kategori (8 stk)
- Leveringstid (lead time) og variabilitet
- Holdbarhet (shelf-life, dager)
- Substitusjonsgrad (0-1)
- Kampanjefrekvens (kampanjer per aar)

Den \"sanne\" optimale lagerstyringsklassen er en deterministisk ikke-
lineaer funksjon av attributtene + stokastisk stoey. Tre klasser:

  0  kontinuerlig  -- hoey etterspoersel, lav variabilitet, hoey verdi
                      ELLER hoey etterspoersel kombinert med hoey
                      substitusjonsgrad (pluss lang leveringstid hjelper)
  1  periodisk     -- moderat volum og/eller variabilitet
  2  make-to-order -- lav etterspoersel og/eller hoey variabilitet og
                      hoey verdi ELLER kort holdbarhet med sporadisk
                      etterspoersel

Figurer:
  mlklasse_data_explore.png  -- utforskning av volum, CV, klassefordelingen
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# -----------------------------------------------------------------------------
# Konfigurasjon
# -----------------------------------------------------------------------------
N_SKUS = 2500
N_DAYS = 730  # 2 aar
START_DATE = "2023-01-02"  # mandag

CATEGORIES = [
    "daglig",       # hoey volum, stabil (meieri etc)
    "sesong",       # sterk aarstidsvariasjon
    "kampanje",     # kampanjedrevet
    "ferskvare",    # kort holdbarhet, daglig
    "frossen",      # lang holdbarhet, moderat
    "ikke-mat",     # lav etterspoersel, hoey verdi
    "premium",      # hoey pris, liten volum
    "reservedel",   # lav etterspoersel, lang leveringstid
]

# Farger som speiler theme.tex
S1 = "#8CC8E5"; S1D = "#1F6587"
S2 = "#97D4B7"; S2D = "#307453"
S3 = "#F6BA7C"; S3D = "#9C540B"
S4 = "#BD94D7"; S4D = "#5A2C77"
S5 = "#ED9F9E"; S5D = "#961D1C"
INK = "#1F2933"
INKMUTED = "#556270"


def generate_sku_catalog(seed: int = 42) -> pd.DataFrame:
    """Generer katalog med attributter per SKU."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(N_SKUS):
        cat = CATEGORIES[rng.integers(0, len(CATEGORIES))]

        # Baseline-attributter som varierer per kategori
        if cat == "daglig":
            arsvolum = float(rng.lognormal(mean=8.5, sigma=0.55))
            cv_target = float(rng.uniform(0.15, 0.45))
            pris = float(rng.uniform(10, 60))
            leveringstid = float(rng.uniform(2, 6))
            lt_variabilitet = float(rng.uniform(0.1, 0.3))
            holdbarhet = float(rng.uniform(7, 30))
            substitusjonsgrad = float(rng.uniform(0.4, 0.8))
            kampanjer_ar = float(rng.uniform(2, 8))
        elif cat == "sesong":
            arsvolum = float(rng.lognormal(mean=7.5, sigma=0.7))
            cv_target = float(rng.uniform(0.45, 0.95))
            pris = float(rng.uniform(30, 160))
            leveringstid = float(rng.uniform(5, 21))
            lt_variabilitet = float(rng.uniform(0.15, 0.35))
            holdbarhet = float(rng.uniform(60, 365))
            substitusjonsgrad = float(rng.uniform(0.1, 0.5))
            kampanjer_ar = float(rng.uniform(3, 10))
        elif cat == "kampanje":
            arsvolum = float(rng.lognormal(mean=7.8, sigma=0.75))
            cv_target = float(rng.uniform(0.55, 1.2))
            pris = float(rng.uniform(20, 120))
            leveringstid = float(rng.uniform(4, 14))
            lt_variabilitet = float(rng.uniform(0.2, 0.4))
            holdbarhet = float(rng.uniform(30, 180))
            substitusjonsgrad = float(rng.uniform(0.3, 0.7))
            kampanjer_ar = float(rng.uniform(8, 20))
        elif cat == "ferskvare":
            arsvolum = float(rng.lognormal(mean=8.2, sigma=0.5))
            cv_target = float(rng.uniform(0.25, 0.6))
            pris = float(rng.uniform(15, 90))
            leveringstid = float(rng.uniform(1, 3))
            lt_variabilitet = float(rng.uniform(0.1, 0.25))
            holdbarhet = float(rng.uniform(1, 7))
            substitusjonsgrad = float(rng.uniform(0.3, 0.7))
            kampanjer_ar = float(rng.uniform(1, 6))
        elif cat == "frossen":
            arsvolum = float(rng.lognormal(mean=7.8, sigma=0.55))
            cv_target = float(rng.uniform(0.2, 0.6))
            pris = float(rng.uniform(35, 200))
            leveringstid = float(rng.uniform(7, 28))
            lt_variabilitet = float(rng.uniform(0.2, 0.4))
            holdbarhet = float(rng.uniform(90, 540))
            substitusjonsgrad = float(rng.uniform(0.2, 0.6))
            kampanjer_ar = float(rng.uniform(2, 6))
        elif cat == "ikke-mat":
            arsvolum = float(rng.lognormal(mean=5.8, sigma=0.9))
            cv_target = float(rng.uniform(0.6, 1.8))
            pris = float(rng.uniform(50, 450))
            leveringstid = float(rng.uniform(5, 30))
            lt_variabilitet = float(rng.uniform(0.15, 0.5))
            holdbarhet = float(rng.uniform(365, 1825))
            substitusjonsgrad = float(rng.uniform(0.1, 0.5))
            kampanjer_ar = float(rng.uniform(0, 4))
        elif cat == "premium":
            arsvolum = float(rng.lognormal(mean=5.0, sigma=0.8))
            cv_target = float(rng.uniform(0.5, 1.6))
            pris = float(rng.uniform(200, 1800))
            leveringstid = float(rng.uniform(3, 21))
            lt_variabilitet = float(rng.uniform(0.15, 0.45))
            holdbarhet = float(rng.uniform(180, 1460))
            substitusjonsgrad = float(rng.uniform(0.1, 0.4))
            kampanjer_ar = float(rng.uniform(0, 3))
        else:  # reservedel
            arsvolum = float(rng.lognormal(mean=3.8, sigma=1.1))
            cv_target = float(rng.uniform(0.9, 2.6))
            pris = float(rng.uniform(80, 3200))
            leveringstid = float(rng.uniform(10, 70))
            lt_variabilitet = float(rng.uniform(0.2, 0.6))
            holdbarhet = float(rng.uniform(720, 3650))
            substitusjonsgrad = float(rng.uniform(0.0, 0.3))
            kampanjer_ar = float(rng.uniform(0, 2))

        rows.append({
            "sku_id": f"S{i + 1:05d}",
            "kategori": cat,
            "arsvolum": round(arsvolum, 2),
            "cv_target": round(cv_target, 3),
            "pris": round(pris, 2),
            "leveringstid_dager": round(leveringstid, 2),
            "lt_variabilitet": round(lt_variabilitet, 3),
            "holdbarhet_dager": round(holdbarhet, 1),
            "substitusjonsgrad": round(substitusjonsgrad, 3),
            "kampanjer_ar": round(kampanjer_ar, 2),
        })
    return pd.DataFrame(rows)


def generate_transactions(catalog: pd.DataFrame,
                          seed: int = 11) -> pd.DataFrame:
    """For hver SKU, generer daglig salg over N_DAYS.

    Salget blir en Poisson-sekvens med middelverdi (arsvolum/365) og
    multiplikative innslag fra uke-mønster, sesong, kampanjer og
    støy slik at CV paa aggregat-niva (ukentlig) matcher cv_target.
    """
    rng = np.random.default_rng(seed)
    dates = pd.date_range(start=START_DATE, periods=N_DAYS, freq="D")
    dow = dates.dayofweek.to_numpy()
    doy = dates.dayofyear.to_numpy()
    weekly_base = np.array([0.9, 0.95, 1.0, 1.05, 1.15, 1.05, 0.8])

    # Kategorispesifikke sesongprofiler
    season_profiles = {
        "daglig": np.zeros(N_DAYS),
        "sesong": 0.35 * np.sin(2 * np.pi * (doy - 60) / 365.25),
        "kampanje": np.zeros(N_DAYS),
        "ferskvare": 0.08 * np.sin(2 * np.pi * (doy - 150) / 365.25),
        "frossen": -0.12 * np.sin(2 * np.pi * (doy - 60) / 365.25),
        "ikke-mat": np.where(dates.month == 12, 0.55, 0.0),
        "premium": np.where(dates.month == 12, 0.30, 0.0),
        "reservedel": np.zeros(N_DAYS),
    }

    rows_sku, rows_dato, rows_salg = [], [], []
    for _, sku in catalog.iterrows():
        base = sku["arsvolum"] / 365.25
        cv_t = sku["cv_target"]
        kamp_prob = sku["kampanjer_ar"] / 365.25
        season = season_profiles[sku["kategori"]]

        # Ukemoenster bare hvis varen er \"daglig\" aktiv
        if sku["kategori"] in ("reservedel", "premium", "ikke-mat"):
            weekly = np.ones(N_DAYS)
        else:
            weekly = weekly_base[dow]

        # Stoeysigma kalibreres loest til cv_t
        noise_sigma = min(0.9, cv_t * 0.9)
        noise = rng.normal(0, noise_sigma, size=N_DAYS)

        # Kampanjer: boost x3-x6 i korte perioder
        is_camp = rng.random(N_DAYS) < kamp_prob
        camp_mult = np.where(is_camp, rng.uniform(2.5, 5.5, size=N_DAYS), 1.0)

        log_mean = np.log(np.maximum(base, 1e-4)) + season + np.log(weekly) + noise
        mean = np.exp(log_mean) * camp_mult

        # Sporadisk etterspoersel for reservedeler/premium: mange null-dager
        if sku["kategori"] in ("reservedel", "premium"):
            gate = rng.random(N_DAYS) < min(0.9, 2.5 * base)
            mean = np.where(gate, mean * (1 / max(2.5 * base, 0.05)), 0.0)

        sales = rng.poisson(np.maximum(mean, 0.0)).astype(np.int32)
        rows_sku.append(np.full(N_DAYS, sku["sku_id"], dtype=object))
        rows_dato.append(dates.to_numpy())
        rows_salg.append(sales)

    tx = pd.DataFrame({
        "sku_id": np.concatenate(rows_sku),
        "dato": np.concatenate(rows_dato),
        "salg": np.concatenate(rows_salg),
    })
    tx["dato"] = pd.to_datetime(tx["dato"])
    return tx


def latent_optimal_class(catalog: pd.DataFrame,
                         aggr: pd.DataFrame,
                         seed: int = 7) -> pd.Series:
    """Definer 'sann' optimal lagerstyringsklasse via en ikke-lineaer
    funksjon av attributtene. Funksjonen speiler en forenklet utgave av
    kostnadsstrukturen i step06: (Q,R) med sikkerhetslager er gunstig
    for hoeye volumer med lav variabilitet og lav pris, mens
    make-to-order er gunstig for lav volum + hoey pris + lang leveringstid.

    Klasser:
      0 = kontinuerlig, 1 = periodisk, 2 = make-to-order
    """
    rng = np.random.default_rng(seed)
    df = catalog.merge(aggr, on="sku_id", how="left")

    # Attributter
    daglig = df["salg_gj_daglig"].to_numpy()            # enheter/dag
    daglig_std = df["salg_std_daglig"].to_numpy()
    lt = df["leveringstid_dager"].to_numpy()
    pris = df["pris"].to_numpy()
    shelf = df["holdbarhet_dager"].to_numpy()
    subs = df["substitusjonsgrad"].to_numpy()
    camp_rate = df["kampanjer_ar"].to_numpy()
    is_reservedel = df["kategori"].isin(["reservedel"]).to_numpy().astype(float)
    is_premium = df["kategori"].isin(["premium"]).to_numpy().astype(float)
    is_ferskvare = df["kategori"].isin(["ferskvare"]).to_numpy().astype(float)

    # Forenklede kostnadsestimat per politikk (per aar).
    # Parametre speiler step06 saa klassene stemmer overens med faktisk
    # simulerte kostnader. Holding rate = 0.30 x pris.
    h = 0.30 * pris
    aarlig = daglig * 365.0

    # Normaliserte rangeringer
    vol_r = df["arsvolum"].rank(pct=True).to_numpy()
    cv_r = df["cv_observert"].rank(pct=True).to_numpy()
    pris_r = df["pris"].rank(pct=True).to_numpy()
    lt_r = df["leveringstid_dager"].rank(pct=True).to_numpy()
    shelf_low = (shelf < 15).astype(float)
    shelf_mid = ((shelf >= 15) & (shelf < 90)).astype(float)

    # Tre ikke-lineaere scorer. Hver klasse foretrekker et \"omraade\"
    # i feature-rommet, og interaksjonene kompliserer det paa maater
    # ABC-XYZ ikke fanger.
    #
    # kontinuerlig:  hoey volum OG lav CV (stabil hoey trafikk) -- klassisk AX
    #                boostes av kampanjer og hoey substitusjonsgrad
    #                straffes av hoey pris eller lang lead time (monitorering
    #                blir dyr naar EOQ-lot er lite)
    s_cont = (
        1.60 * vol_r * (1 - cv_r)               # klassisk AX
        + 0.40 * (camp_rate > 5).astype(float)
        + 0.30 * (subs > 0.5).astype(float)
        - 0.50 * pris_r * (1 - vol_r)            # hoey pris + lav volum straffes
        - 0.45 * lt_r * (1 - vol_r)
        - 0.55 * is_reservedel
        - 0.55 * is_premium
        + 0.40 * shelf_low * vol_r              # ferskvare med volum
    )

    # periodisk: \"midten\" av volum ELLER moderat CV, og holdbarhet
    #            hoey nok til aa tillate batch-ordrer
    s_periodic = (
        1.10 * (1 - np.abs(vol_r - 0.55) * 1.8)
        + 0.55 * (1 - np.abs(cv_r - 0.5) * 1.6)
        + 0.30 * ((shelf >= 15) & (shelf < 365)).astype(float)
        + 0.20 * df["kategori"].isin(["sesong", "kampanje", "frossen"])
                 .to_numpy().astype(float)
        - 0.25 * (camp_rate > 10).astype(float)
        + 0.20
    )

    # make-to-order: lav volum OG hoey CV ELLER hoey pris og lang lead time
    s_mto = (
        0.95 * (1 - vol_r) * cv_r                # lav volum + hoey CV
        + 0.70 * pris_r * lt_r                    # dyr + treg leverandoer
        + 0.55 * is_reservedel
        + 0.50 * is_premium
        + 0.30 * ((shelf > 365)).astype(float)
        - 0.30 * subs
    )

    # Stoey for aa gjoere det realistisk vanskelig
    s_cont += rng.normal(0, 0.22, size=len(df))
    s_periodic += rng.normal(0, 0.22, size=len(df))
    s_mto += rng.normal(0, 0.22, size=len(df))

    scores = np.stack([s_cont, s_periodic, s_mto], axis=1)
    klasse = np.argmax(scores, axis=1)
    return pd.Series(klasse, index=df.index, name="klasse")


def aggregate_transactions(tx: pd.DataFrame) -> pd.DataFrame:
    """Aggreger transaksjoner per SKU (obs: brukes av step02 og
    til generering av latent klasse her i step01)."""
    g = tx.groupby("sku_id")["salg"]
    agg = pd.DataFrame({
        "salg_total": g.sum(),
        "salg_gj_daglig": g.mean(),
        "salg_std_daglig": g.std(),
        "salg_max": g.max(),
        "antall_nulldager": g.apply(lambda s: (s == 0).sum()),
        "antall_dager": g.count(),
    }).reset_index()
    # Observert CV (per-SKU, daglig)
    agg["cv_observert"] = agg["salg_std_daglig"] / agg["salg_gj_daglig"].replace(0, np.nan)
    agg["cv_observert"] = agg["cv_observert"].fillna(agg["cv_observert"].max())
    # Null-dag-andel
    agg["nulldag_andel"] = agg["antall_nulldager"] / agg["antall_dager"]
    return agg


def plot_data_explore(catalog: pd.DataFrame, aggr: pd.DataFrame,
                      klasse: pd.Series, output_path: Path) -> None:
    """Fire-panels utforskning: fordeling av volum, CV, klassefordeling
    og katalogfordeling per kategori."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    df = catalog.merge(aggr, on="sku_id").assign(klasse=klasse.values)

    class_labels = {0: "kontinuerlig", 1: "periodisk", 2: "make-to-order"}
    class_colors = {0: S1D, 1: S2D, 2: S5D}
    fill_colors = {0: S1, 1: S2, 2: S5}

    # Panel 1: histogram av aarsvolum (log) per klasse
    ax = axes[0, 0]
    for k, lbl in class_labels.items():
        sub = df[df["klasse"] == k]
        ax.hist(np.log10(np.clip(sub["salg_total"], 1, None)),
                bins=40, alpha=0.55, color=fill_colors[k],
                edgecolor=class_colors[k], label=lbl)
    ax.set_xlabel(r"$\log_{10}$(totalsalg 2 aar)", fontsize=11)
    ax.set_ylabel("Antall SKU-er", fontsize=11)
    ax.set_title("Volumfordeling per klasse", fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 2: scatter volum vs CV farget etter klasse
    ax = axes[0, 1]
    for k, lbl in class_labels.items():
        sub = df[df["klasse"] == k]
        ax.scatter(np.log10(np.clip(sub["salg_total"], 1, None)),
                   sub["cv_observert"], s=8, alpha=0.45,
                   color=class_colors[k], label=lbl)
    ax.set_xlabel(r"$\log_{10}$(totalsalg)", fontsize=11)
    ax.set_ylabel("Observert daglig CV", fontsize=11)
    ax.set_title("Volum vs variabilitet",
                 fontsize=12, fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    # Panel 3: klassefordeling som stolpe
    ax = axes[1, 0]
    counts = df["klasse"].value_counts().sort_index()
    ax.bar([class_labels[i] for i in counts.index], counts.values,
           color=[fill_colors[i] for i in counts.index],
           edgecolor=[class_colors[i] for i in counts.index])
    for i, v in enumerate(counts.values):
        ax.text(i, v + 15, f"{v:,}", ha="center", fontsize=10)
    ax.set_ylabel("Antall SKU-er", fontsize=11)
    ax.set_title("Fordeling av optimale klasser",
                 fontsize=12, fontweight="bold")
    ax.grid(True, axis="y", alpha=0.3)

    # Panel 4: klasse per kategori (stablet)
    ax = axes[1, 1]
    cat_klasse = (df.groupby(["kategori", "klasse"]).size()
                  .unstack(fill_value=0))
    cat_klasse = cat_klasse.reindex(columns=[0, 1, 2], fill_value=0)
    cats = cat_klasse.index.tolist()
    bottom = np.zeros(len(cats))
    for k in [0, 1, 2]:
        ax.bar(cats, cat_klasse[k].values, bottom=bottom,
               color=fill_colors[k], edgecolor=class_colors[k],
               label=class_labels[k])
        bottom += cat_klasse[k].values
    ax.set_ylabel("Antall SKU-er", fontsize=11)
    ax.set_title("Klasse per kategori (stablet)",
                 fontsize=12, fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"Figur lagret: {output_path}")


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    data_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(exist_ok=True)
    data_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 1: DATAINNSAMLING -- SKU-katalog + transaksjoner")
    print(f"{'=' * 60}")

    catalog = generate_sku_catalog()
    tx = generate_transactions(catalog)
    aggr = aggregate_transactions(tx)
    klasse = latent_optimal_class(catalog, aggr)

    # Slaa sammen til masterkatalog med klasselabelen
    master = catalog.merge(aggr, on="sku_id").assign(klasse=klasse.values)

    # Deskriptiv statistikk
    stats = {
        "antall_skuer": int(len(catalog)),
        "antall_dager": int(N_DAYS),
        "antall_kategorier": int(catalog["kategori"].nunique()),
        "antall_transaksjonsrader": int(len(tx)),
        "klassefordeling": {
            "kontinuerlig": int((klasse == 0).sum()),
            "periodisk": int((klasse == 1).sum()),
            "make_to_order": int((klasse == 2).sum()),
        },
        "gj_salg_daglig": round(float(tx["salg"].mean()), 3),
        "maks_salg_daglig": int(tx["salg"].max()),
        "andel_nulldager": round(float((tx["salg"] == 0).mean()), 3),
        "gj_pris": round(float(catalog["pris"].mean()), 2),
        "median_leveringstid": round(float(catalog["leveringstid_dager"].median()), 1),
    }

    print(f"\n{'Antall SKU-er:':30s} {stats['antall_skuer']:,}")
    print(f"{'Antall dager:':30s} {stats['antall_dager']:,}")
    print(f"{'Transaksjonsrader (SKUxdag):':30s} {stats['antall_transaksjonsrader']:,}")
    print(f"{'Antall kategorier:':30s} {stats['antall_kategorier']}")
    print(f"\nKlassefordeling:")
    for name, cnt in stats["klassefordeling"].items():
        print(f"  {name:20s}: {cnt:,}  ({100 * cnt / stats['antall_skuer']:.1f} %)")

    # Lagre
    catalog.to_csv(data_dir / "sku_catalog.csv", index=False, encoding="utf-8")
    tx.to_parquet(data_dir / "transactions.parquet", index=False)
    master.to_csv(data_dir / "master.csv", index=False, encoding="utf-8")
    aggr.to_csv(data_dir / "aggregates.csv", index=False, encoding="utf-8")

    with open(output_dir / "descriptive_stats.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"\nStatistikk lagret: {output_dir / 'descriptive_stats.json'}")

    # Figur
    plot_data_explore(catalog, aggr, klasse,
                      output_dir / "mlklasse_data_explore.png")

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    print(f"  Syntetisk SKU-panel med {stats['antall_skuer']:,} varer over "
          f"{stats['antall_dager']} dager.")
    print(f"  Tre optimale klasser fordelt {stats['klassefordeling']} ")
    print(f"  -- definert via ikke-lineaer funksjon av attributtene "
          f"og rik nok til aa teste ML-klassifisering.")


if __name__ == "__main__":
    main()
