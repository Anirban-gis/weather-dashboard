from pathlib import Path
from datetime import datetime
import pandas as pd
import requests
import time

from backend.config import API_KEY
from backend.database import (
    create_database,
    get_session,
    DistrictWeather
)
print("API Key Loaded:",
      API_KEY[:5] + "*****")
# ==================================================
# PATHS
# ==================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DISTRICT_FILE = DATA_DIR / "district_master.csv"

CSV_OUTPUT = DATA_DIR / "district_weather_latest.csv"

URL = "https://api.openweathermap.org/data/2.5/weather"

# ==================================================
# FETCH ALL DISTRICTS
# ==================================================

def fetch_all_districts():

    if not DISTRICT_FILE.exists():
        raise FileNotFoundError(
            f"District file not found: {DISTRICT_FILE}"
        )

    create_database()

    session = get_session()

    districts = pd.read_csv(DISTRICT_FILE)

    results = []

    success = 0
    failed = 0

    print(f"\nReading: {DISTRICT_FILE}")
    print(f"Total Districts: {len(districts)}\n")

    for _, row in districts.iterrows():

        state = str(row["State"]).strip()
        district = str(row["District"]).strip()

        lat = float(row["Latitude"])
        lon = float(row["Longitude"])

        try:

            response = requests.get(
                URL,
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": API_KEY,
                    "units": "metric"
                },
                timeout=30
            )

            response.raise_for_status()

            data = response.json()

            record = DistrictWeather(

                timestamp=datetime.now(),

                state=state,

                district=district,

                temperature=data["main"].get("temp"),

                humidity=data["main"].get("humidity"),

                pressure=data["main"].get("pressure"),

                wind_speed=data["wind"].get("speed", 0),

                cloudiness=data["clouds"].get("all", 0),

                weather=data["weather"][0].get("main"),

                description=data["weather"][0].get("description")
            )

            session.add(record)

            results.append({

                "timestamp":
                    datetime.now(),

                "state":
                    state,

                "district":
                    district,

                "temperature":
                    data["main"].get("temp"),

                "humidity":
                    data["main"].get("humidity"),

                "pressure":
                    data["main"].get("pressure"),

                "wind_speed":
                    data["wind"].get("speed", 0),

                "cloudiness":
                    data["clouds"].get("all", 0),

                "weather":
                    data["weather"][0].get("main"),

                "description":
                    data["weather"][0].get("description")
            })

            success += 1

            print(
                f"✓ {district} | "
                f"{data['main']['temp']}°C"
            )

            time.sleep(1)

        except Exception as e:

            failed += 1

            print(
                f"✗ {district} : {e}"
            )

    # =============================================
    # SAVE SQLITE
    # =============================================

    session.commit()
    session.close()

    # =============================================
    # SAVE CSV
    # =============================================

    if len(results) > 0:

        df = pd.DataFrame(results)

        df.to_csv(
            CSV_OUTPUT,
            index=False
        )

        print(
            f"\nCSV Saved: {CSV_OUTPUT}"
        )

    print(
        f"\nCompleted."
        f"\nSuccess: {success}"
        f"\nFailed: {failed}"
    )

# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":

    fetch_all_districts()