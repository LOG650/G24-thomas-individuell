"""
Steg 4: Parameterestimering for ARIMAX
======================================
Tilpasser en ARIMAX-modell via statsmodels.SARIMAX med

  (p, d, q)(P, D, Q)_m = (1, 1, 1)(1, 0, 1)_7

og eksogene variabler X fra Steg 2. Til sammenligning tilpasser vi
også en ren SARIMA-modell med samme (p,d,q,P,D,Q,m) men uten X.

Resultatene lagres som pickle, og estimat-tabell som JSON.
"""

import json
import pickle
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.statespace.sarimax import SARIMAX

from step01_datainnsamling import generate_raw_data
from step02_feature_engineering import EXOG_COLS, build_features

warnings.filterwarnings("ignore")

ORDER = (1, 1, 1)
SEASONAL_ORDER = (1, 0, 1, 7)


def fit_arimax(df_feat: pd.DataFrame) -> dict:
    """Tilpass ARIMAX-modellen med eksogene variabler."""
    y = pd.Series(df_feat["salg"].astype(float).values,
                  index=pd.DatetimeIndex(df_feat["dato"]), name="Salg")
    X = pd.DataFrame(
        df_feat[EXOG_COLS].astype(float).values,
        index=y.index,
        columns=EXOG_COLS,
    )

    model = SARIMAX(
        y,
        exog=X,
        order=ORDER,
        seasonal_order=SEASONAL_ORDER,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    res = model.fit(disp=False, maxiter=200)
    return {"results": res, "y": y, "X": X, "exog_cols": list(EXOG_COLS),
            "dates": df_feat["dato"].values}


def fit_sarima_only(df_feat: pd.DataFrame) -> dict:
    """Tilpass referanse-SARIMA uten eksogene variabler (same ordre)."""
    y = pd.Series(df_feat["salg"].astype(float).values,
                  index=pd.DatetimeIndex(df_feat["dato"]), name="Salg")
    model = SARIMAX(
        y,
        order=ORDER,
        seasonal_order=SEASONAL_ORDER,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    res = model.fit(disp=False, maxiter=200)
    return {"results": res, "y": y, "dates": df_feat["dato"].values}


def extract_estimates(fitted: dict) -> pd.DataFrame:
    """Plukk ut parameter-tabellen fra statsmodels-resultatet."""
    res = fitted["results"]
    params = res.params
    bse = res.bse
    pvals = res.pvalues
    df = pd.DataFrame(
        {
            "parameter": params.index.tolist(),
            "estimat": params.values,
            "std_feil": bse.values,
            "p_verdi": pvals.values,
        }
    )
    return df


def main() -> None:
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    print(f"\n{'=' * 60}")
    print("STEG 4: PARAMETERESTIMERING (ARIMAX)")
    print(f"{'=' * 60}")

    df = generate_raw_data()
    df_feat = build_features(df)

    # --- ARIMAX ---
    print("\nTilpasser ARIMAX(1,1,1)(1,0,1)_7 med 7 eksogene variabler ...")
    arimax = fit_arimax(df_feat)
    res_x = arimax["results"]
    print(res_x.summary())

    est_table = extract_estimates(arimax)
    print("\n--- Parametertabell ARIMAX ---")
    print(est_table.to_string(index=False,
                               formatters={
                                   "estimat": "{:.4f}".format,
                                   "std_feil": "{:.4f}".format,
                                   "p_verdi": "{:.4g}".format,
                               }))

    # --- SARIMA (referanse) ---
    print("\n\nTilpasser referanse-SARIMA (ingen eksogene variabler) ...")
    sarima = fit_sarima_only(df_feat)
    res_s = sarima["results"]

    # Modellsammenligning
    comparison = {
        "ARIMAX": {
            "AIC": round(float(res_x.aic), 2),
            "BIC": round(float(res_x.bic), 2),
            "loglik": round(float(res_x.llf), 2),
            "sigma2": round(float(res_x.params.get("sigma2", np.nan)), 2),
            "antall_parametre": int(len(res_x.params)),
        },
        "SARIMA": {
            "AIC": round(float(res_s.aic), 2),
            "BIC": round(float(res_s.bic), 2),
            "loglik": round(float(res_s.llf), 2),
            "sigma2": round(float(res_s.params.get("sigma2", np.nan)), 2),
            "antall_parametre": int(len(res_s.params)),
        },
    }
    print("\n--- Modellsammenligning ---")
    for name, vals in comparison.items():
        print(f"  {name}: {vals}")

    # Lagre estimat-tabell for LaTeX
    est_path = output_dir / "arimax_estimates.json"
    est_records = []
    for _, row in est_table.iterrows():
        est_records.append(
            {
                "parameter": str(row["parameter"]),
                "estimat": round(float(row["estimat"]), 4),
                "std_feil": round(float(row["std_feil"]), 4),
                "p_verdi": round(float(row["p_verdi"]), 6),
            }
        )
    with open(est_path, "w", encoding="utf-8") as f:
        json.dump(
            {"estimates": est_records, "sammenligning": comparison},
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"\nEstimater lagret: {est_path}")

    # Pickle modellene for Steg 5 / 6
    with open(output_dir / "arimax_model.pkl", "wb") as f:
        pickle.dump(arimax, f)
    with open(output_dir / "sarima_benchmark_model.pkl", "wb") as f:
        pickle.dump(sarima, f)

    print(f"\n{'=' * 60}")
    print("KONKLUSJON")
    print(f"{'=' * 60}")
    kampanje_row = est_table[est_table["parameter"] == "x_kampanje"].iloc[0]
    rabatt_row = est_table[est_table["parameter"] == "x_rabatt"].iloc[0]
    print(
        f"  beta_kampanje = {kampanje_row['estimat']:.2f}  "
        f"(p = {kampanje_row['p_verdi']:.3g})\n"
        f"  beta_rabatt   = {rabatt_row['estimat']:.2f}  "
        f"(p = {rabatt_row['p_verdi']:.3g})\n"
        f"  AIC (ARIMAX): {comparison['ARIMAX']['AIC']} "
        f"<->  AIC (SARIMA): {comparison['SARIMA']['AIC']}\n"
        f"  ARIMAX reduserer AIC med "
        f"{comparison['SARIMA']['AIC'] - comparison['ARIMAX']['AIC']:.0f} -> "
        "eksogene variabler gir klart bedre tilpasning."
    )


if __name__ == "__main__":
    main()
