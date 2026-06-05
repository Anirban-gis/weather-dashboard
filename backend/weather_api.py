# backend/weather_api.py

import os
from pathlib import Path
from datetime import datetime

import pandas as pd
import requests

from backend.config import (
    API_KEY,
    LATITUDE,
    LONGITUDE
)

from backend.database import (
    create_database,
    get_session,
    WeatherRecord
)

# ====================================================
# PROJECT PATHS
# ====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# ====================================================
# OPENWEATHER URL
# ====================================================

URL = "https://api.openweathermap.org/data/2.5/weather"

# ====================================================
# FETCH WEATHER
# ====================================================

def fetch_weather():

    params = {
        "lat": LATITUDE,
        "lon": LONGITUDE,
        "appid": API_KEY,
        "units": "metric"
    }

    print("\nFetching weather data...")
    print("API Key:", API_KEY[:6] + "******")

    response = requests.get(
        URL,
        params=params,
        timeout=30
    )

    print("Status Code:", response.status_code)
    print("Request URL:", response.url)

    response.raise_for_status()

    return response.json()

# ====================================================
# SAVE TO DATABASE
# ====================================================

def save_database(data):

    create_database()

    session = get_session()

    record = WeatherRecord(

        timestamp=datetime.now(),

        city=data["name"],

        country=data["sys"]["country"],

        temperature=data["main"]["temp"],

        feels_like=data["main"]["feels_like"],

        humidity=data["main"]["humidity"],

        pressure=data["main"]["pressure"],

        wind_speed=data["wind"]["speed"],

        cloudiness=data["clouds"]["all"],

        weather=data["weather"][0]["main"],

        description=data["weather"][0]["description"]
    )

    session.add(record)

    session.commit()

    session.close()

    print("Database updated.")

# ====================================================
# SAVE CSV
# ====================================================

def save_csv(data):

    csv_file = DATA_DIR / "latest_weather.csv"

    df = pd.DataFrame([{
        "timestamp": datetime.now(),

        "city": data["name"],

        "country": data["sys"]["country"],

        "temperature": data["main"]["temp"],

        "feels_like": data["main"]["feels_like"],

        "humidity": data["main"]["humidity"],

        "pressure": data["main"]["pressure"],

        "wind_speed": data["wind"]["speed"],

        "cloudiness": data["clouds"]["all"],

        "weather": data["weather"][0]["main"],

        "description": data["weather"][0]["description"]
    }])

    df.to_csv(
        csv_file,
        index=False
    )

    print(f"CSV Saved: {csv_file}")

# ====================================================
# MAIN
# ====================================================

def run():

    print("\nProject Folder:")
    print(BASE_DIR)

    print("\nData Folder:")
    print(DATA_DIR)

    data = fetch_weather()

    print("\nWeather Retrieved:")
    print("City:", data["name"])
    print("Temperature:", data["main"]["temp"])
    print("Humidity:", data["main"]["humidity"])
    print("Condition:", data["weather"][0]["description"])

    save_database(data)

    save_csv(data)

    print("\nCompleted Successfully.")

# ====================================================
# START
# ====================================================

if __name__ == "__main__":

    run()