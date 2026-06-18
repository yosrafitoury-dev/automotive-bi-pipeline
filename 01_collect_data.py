import requests
import pandas as pd
import time
import os

NHTSA_BASE = "https://vpic.nhtsa.dot.gov/api/vehicles"
EPA_BASE = "https://www.fueleconomy.gov/ws/rest"

def fetch_all_makes():
    url = f"{NHTSA_BASE}/getallmakes?format=json"
    response = requests.get(url)
    data = response.json()
    df = pd.DataFrame(data.get("Results", []))
    df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    print(f"✅ Fetched {len(df)} vehicle makes from NHTSA.")
    return df

def fetch_models_for_makes(makes_list):
    all_models = []
    for make in makes_list:
        url = f"{NHTSA_BASE}/getmodelsformakeyear/make/{make}/vehicletype/car?format=json"
        try:
            response = requests.get(url, timeout=10)
            results = response.json().get("Results", [])
            for r in results:
                r["make_name"] = make
            all_models.extend(results)
            print(f"  → {make}: {len(results)} models")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Failed for {make}: {e}")
    df = pd.DataFrame(all_models)
    if not df.empty:
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    print(f"✅ Fetched {len(df)} models total.")
    return df

def as_list(menu_items):
    """EPA API sometimes returns a single dict instead of a list when there's only 1 item."""
    if menu_items is None:
        return []
    if isinstance(menu_items, dict):
        return [menu_items]
    return menu_items

def fetch_epa_vehicles():
    all_vehicles = []
    years = range(2015, 2025)
    max_makes_per_year = 15
    max_models_per_make = 6
    max_trims_per_model = 3

    for year in years:
        url = f"{EPA_BASE}/vehicle/menu/make?year={year}"
        try:
            response = requests.get(url, timeout=10, headers={"Accept": "application/json"})
            makes_data = as_list(response.json().get("menuItem"))
            for make_item in makes_data[:max_makes_per_year]:
                make_value = make_item.get("value", "")
                menu_url = f"{EPA_BASE}/vehicle/menu/model?year={year}&make={make_value}"
                menu_resp = requests.get(menu_url, timeout=10, headers={"Accept": "application/json"})
                if menu_resp.status_code != 200:
                    continue
                models_data = as_list(menu_resp.json().get("menuItem"))
                for model_item in models_data[:max_models_per_make]:
                    model_value = model_item.get("value", "")
                    search_url = f"{EPA_BASE}/vehicle/menu/options?year={year}&make={make_value}&model={model_value}"
                    opt_resp = requests.get(search_url, timeout=10, headers={"Accept": "application/json"})
                    if opt_resp.status_code != 200:
                        continue
                    options = as_list(opt_resp.json().get("menuItem"))
                    for opt in options[:max_trims_per_model]:
                        vehicle_id = opt.get("value")
                        if not vehicle_id:
                            continue
                        v_resp = requests.get(f"{EPA_BASE}/vehicle/{vehicle_id}", timeout=10, headers={"Accept": "application/json"})
                        if v_resp.status_code == 200:
                            vehicle_data = v_resp.json()
                            vehicle_data["year"] = year
                            vehicle_data["make"] = make_value
                            vehicle_data["model"] = model_value
                            all_vehicles.append(vehicle_data)
                        time.sleep(0.1)
            print(f"  → Year {year}: {len(all_vehicles)} vehicles collected so far")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ⚠️ Year {year} failed: {e}")

    df = pd.DataFrame(all_vehicles)
    if not df.empty:
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]
    print(f"✅ Fetched {len(df)} EPA vehicle records.")
    return df

if __name__ == "__main__":
    os.makedirs("data/processed", exist_ok=True)
    top_makes = ["Toyota", "Ford", "BMW", "Mercedes-Benz", "Honda", "Volkswagen",
                 "Audi", "Hyundai", "Tesla", "Chevrolet", "Nissan", "Kia"]

    fetch_all_makes().to_csv("data/processed/vehicle_makes.csv", index=False)
    fetch_models_for_makes(top_makes).to_csv("data/processed/vehicle_models.csv", index=False)
    fetch_epa_vehicles().to_csv("data/processed/epa_fuel_economy.csv", index=False)

    print("\n✅ All data saved to data/processed/")