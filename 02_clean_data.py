import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

def clean_makes():
    df = pd.read_csv("data/processed/vehicle_makes.csv")
    df.dropna(subset=["make_name", "make_id"], inplace=True)
    df.drop_duplicates(subset=["make_id"], inplace=True)
    df["make_name"] = df["make_name"].str.strip().str.title()
    df.to_csv("data/processed/vehicle_makes_clean.csv", index=False)
    print(f"✅ Makes cleaned: {len(df)} rows")
    return df

def clean_models():
    df = pd.read_csv("data/processed/vehicle_models.csv")
    df.dropna(subset=["model_name"], inplace=True)
    df.drop_duplicates(inplace=True)
    df["model_name"] = df["model_name"].str.strip().str.title()
    df["make_name"] = df["make_name"].str.strip().str.title()
    df.to_csv("data/processed/vehicle_models_clean.csv", index=False)
    print(f"✅ Models cleaned: {len(df)} rows")
    return df

def clean_epa():
    df = pd.read_csv("data/processed/epa_fuel_economy.csv")
    useful_cols = ["id","year","make","model","trany","drive","fueltype","fueltype1",
                   "city08","highway08","comb08","co2tailpipegpm","ghgscore","cylinders","displ","vclass"]
    available = [c for c in useful_cols if c in df.columns]
    df = df[available].copy()
    df.dropna(subset=["comb08"] if "comb08" in df.columns else [], inplace=True)
    for col in ["city08","highway08","comb08","co2tailpipegpm","cylinders","displ","ghgscore"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    if "comb08" in df.columns:
        df = df[df["comb08"] > 0]
        df["efficiency_category"] = pd.cut(df["comb08"], bins=[0,20,30,40,100],
                                           labels=["Low","Medium","High","Very High"])
    for col in ["make","model","fueltype","drive","vclass"]:
        if col in df.columns:
            df[col] = df[col].str.strip().str.title()
    df.to_csv("data/processed/epa_fuel_economy_clean.csv", index=False)
    print(f"✅ EPA cleaned: {len(df)} rows")
    return df

if __name__ == "__main__":
    clean_makes()
    clean_models()
    clean_epa()
    print("\n✅ All cleaned files saved!")