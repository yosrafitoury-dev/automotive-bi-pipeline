import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB = {
    "host": os.getenv("PG_HOST","localhost"),
    "port": os.getenv("PG_PORT","5432"),
    "dbname": os.getenv("PG_DATABASE","AutomotiveBI"),
    "user": os.getenv("PG_USER","postgres"),
    "password": os.getenv("PG_PASSWORD","admin"),
}

def conn(): return psycopg2.connect(**DB)

def create_tables():
    c = conn(); cur = c.cursor()
    cur.execute("""
        DROP TABLE IF EXISTS epa_fuel_economy CASCADE;
        DROP TABLE IF EXISTS vehicle_models CASCADE;
        DROP TABLE IF EXISTS vehicle_makes CASCADE;
        CREATE TABLE vehicle_makes (make_id INTEGER PRIMARY KEY, make_name TEXT);
        CREATE TABLE vehicle_models (id SERIAL PRIMARY KEY, make_name TEXT, model_name TEXT);
        CREATE TABLE epa_fuel_economy (
            id TEXT PRIMARY KEY, year INTEGER, make TEXT, model TEXT,
            trany TEXT, drive TEXT, fuel_type TEXT,
            city_mpg NUMERIC, highway_mpg NUMERIC, combined_mpg NUMERIC,
            co2_gpm NUMERIC, ghg_score NUMERIC, cylinders NUMERIC,
            displacement NUMERIC, vehicle_class TEXT, efficiency_category TEXT);
    """)
    c.commit(); c.close()
    print("✅ Tables created.")

def load_makes():
    df = pd.read_csv("data/processed/vehicle_makes_clean.csv")
    c = conn(); cur = c.cursor()
    for _, row in df.iterrows():
        try:
            cur.execute("INSERT INTO vehicle_makes VALUES (%s,%s) ON CONFLICT DO NOTHING",
                        (int(row["make_id"]), str(row["make_name"])))
        except: pass
    c.commit(); c.close()
    print(f"✅ Loaded {len(df)} makes.")

def load_models():
    df = pd.read_csv("data/processed/vehicle_models_clean.csv")
    c = conn(); cur = c.cursor()
    for _, row in df.iterrows():
        cur.execute("INSERT INTO vehicle_models (make_name,model_name) VALUES (%s,%s)",
                    (str(row.get("make_name","")), str(row.get("model_name",""))))
    c.commit(); c.close()
    print(f"✅ Loaded {len(df)} models.")

def load_epa():
    df = pd.read_csv("data/processed/epa_fuel_economy_clean.csv")
    c = conn(); cur = c.cursor(); n = 0
    for _, row in df.iterrows():
        try:
            cur.execute("""INSERT INTO epa_fuel_economy VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON CONFLICT DO NOTHING""",
                (str(row.get("id","")), int(row["year"]) if pd.notna(row.get("year")) else None,
                 str(row.get("make","")), str(row.get("model","")),
                 str(row.get("trany","")), str(row.get("drive","")),
                 str(row.get("fueltype", row.get("fueltype1",""))),
                 float(row["city08"]) if pd.notna(row.get("city08")) else None,
                 float(row["highway08"]) if pd.notna(row.get("highway08")) else None,
                 float(row["comb08"]) if pd.notna(row.get("comb08")) else None,
                 float(row["co2tailpipegpm"]) if pd.notna(row.get("co2tailpipegpm")) else None,
                 float(row["ghgscore"]) if pd.notna(row.get("ghgscore")) else None,
                 float(row["cylinders"]) if pd.notna(row.get("cylinders")) else None,
                 float(row["displ"]) if pd.notna(row.get("displ")) else None,
                 str(row.get("vclass","")), str(row.get("efficiency_category","")))); n+=1
        except Exception as e: print(f"  ⚠️ {e}")
    c.commit(); c.close()
    print(f"✅ Loaded {n} EPA records.")

def run_analysis():
    c = conn(); cur = c.cursor()
    print("\n── Top 5 makes by avg MPG ──")
    cur.execute("SELECT make, ROUND(AVG(combined_mpg)::numeric,2) FROM epa_fuel_economy GROUP BY make ORDER BY 2 DESC LIMIT 5;")
    for r in cur.fetchall(): print(f"  {r[0]:<20} {r[1]} MPG")
    cur.execute("CREATE OR REPLACE VIEW top_efficient_vehicles AS SELECT make,model,year,combined_mpg,co2_gpm,vehicle_class FROM epa_fuel_economy WHERE combined_mpg IS NOT NULL ORDER BY combined_mpg DESC LIMIT 50;")
    c.commit(); c.close()
    print("✅ View created: top_efficient_vehicles")

if __name__ == "__main__":
    create_tables(); load_makes(); load_models(); load_epa(); run_analysis()