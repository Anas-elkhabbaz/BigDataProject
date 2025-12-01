# scripts/clean_forecast_csv.py
import sys
import pandas as pd

def main(path):
    print(f"[INFO] Cleaning forecast CSV: {path}")
    df = pd.read_csv(path)

    # 1. Nettoyer les noms de colonnes
    df.columns = [c.strip() for c in df.columns]

    # 2. Garder seulement les colonnes utiles
    # (tu peux en rajouter si tu veux les exploiter ensuite)
    keep_cols = [
        "date",
        "date_epoch",
        "day_maxtemp_c",
        "day_mintemp_c",
        "day_avgtemp_c",
        "day_totalprecip_mm",
        "day_avghumidity",
        "day_condition_text",
        "day_uv",
    ]
    df = df[keep_cols]

    # 3. Renommer en noms plus simples
    df = df.rename(
        columns={
            "day_maxtemp_c": "tmax_c",
            "day_mintemp_c": "tmin_c",
            "day_avgtemp_c": "tavg_c",
            "day_totalprecip_mm": "precip_mm",
            "day_avghumidity": "humidity",
            "day_condition_text": "condition",
            "day_uv": "uv",
        }
    )

    # 4. Convertir les colonnes numériques
    num_cols = ["date_epoch", "tmax_c", "tmin_c", "tavg_c", "precip_mm", "humidity", "uv"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 5. Trier par date (au cas où) 
    df = df.sort_values("date")

    # 6. Réécrire par-dessus le même fichier
    df.to_csv(path, index=False)
    print("[INFO] Cleaning done, file overwritten.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/clean_forecast_csv.py <path_to_csv>")
        sys.exit(1)
    main(sys.argv[1])
