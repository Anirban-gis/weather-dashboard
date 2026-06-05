import os

print("\n===================================")
print("RUNNING APP FILE:")
print(os.path.abspath(__file__))
print("===================================\n")

from flask import Flask, jsonify
from flask_cors import CORS
from sqlalchemy import desc
from pathlib import Path
import pandas as pd
from flask import jsonify

from backend.database import (
    get_session,
    DistrictWeather
)

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*"
        }
    }
)

# =====================================================
# HEALTH CHECK
# =====================================================

@app.route("/")

def home():

    return jsonify({
        "status": "running",
        "service": "District Weather API"
    })

# =====================================================
# DISTRICT LIST
# =====================================================

@app.route("/api/districts")

def districts():

    session = get_session()

    rows = (
        session.query(
            DistrictWeather.district
        )
        .distinct()
        .all()
    )

    result = sorted(
        [x[0] for x in rows]
    )

    session.close()

    return jsonify(result)

# =====================================================
# LATEST RECORDS
# =====================================================

@app.route("/api/latest")

def latest():

    session = get_session()

    rows = (
        session.query(
            DistrictWeather
        )
        .order_by(
            desc(DistrictWeather.timestamp)
        )
        .limit(500)
        .all()
    )

    result = []

    for row in rows:

        result.append({

            "timestamp":
                row.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "state":
                row.state,

            "district":
                row.district,

            "temperature":
                row.temperature,

            "humidity":
                row.humidity,

            "pressure":
                row.pressure,

            "wind_speed":
                row.wind_speed,

            "cloudiness":
                row.cloudiness,

            "weather":
                row.weather,

            "description":
                row.description
        })

    session.close()

    return jsonify(result)

# =====================================================
# DISTRICT HISTORY
# =====================================================

@app.route(
    "/api/history/<district>"
)

def history(district):

    session = get_session()

    rows = (
        session.query(
            DistrictWeather
        )
        .filter(
            DistrictWeather.district == district
        )
        .order_by(
            DistrictWeather.timestamp
        )
        .all()
    )

    result = []

    for row in rows:

        result.append({

            "timestamp":
                row.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "temperature":
                row.temperature,

            "humidity":
                row.humidity,

            "pressure":
                row.pressure,

            "wind_speed":
                row.wind_speed,

            "cloudiness":
                row.cloudiness,

            "weather":
                row.weather,

            "description":
                row.description
        })

    session.close()

    return jsonify(result)

# =====================================================
# LATEST FOR ONE DISTRICT
# =====================================================

@app.route(
    "/api/latest/<district>"
)

def latest_district(district):

    session = get_session()

    row = (
        session.query(
            DistrictWeather
        )
        .filter(
            DistrictWeather.district == district
        )
        .order_by(
            desc(
                DistrictWeather.timestamp
            )
        )
        .first()
    )

    session.close()

    if row is None:

        return jsonify({
            "error":
                "District not found"
        }), 404

    return jsonify({

        "timestamp":
            row.timestamp.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),

        "state":
            row.state,

        "district":
            row.district,

        "temperature":
            row.temperature,

        "humidity":
            row.humidity,

        "pressure":
            row.pressure,

        "wind_speed":
            row.wind_speed,

        "cloudiness":
            row.cloudiness,

        "weather":
            row.weather,

        "description":
            row.description
    })

# =====================================================
# STATE FILTER
# =====================================================

@app.route(
    "/api/state/<state>"
)

def state_weather(state):

    session = get_session()

    rows = (
        session.query(
            DistrictWeather
        )
        .filter(
            DistrictWeather.state == state
        )
        .order_by(
            desc(
                DistrictWeather.timestamp
            )
        )
        .all()
    )

    result = []

    for row in rows:

        result.append({

            "district":
                row.district,

            "temperature":
                row.temperature,

            "humidity":
                row.humidity,

            "weather":
                row.weather,

            "timestamp":
                row.timestamp.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
        })

    session.close()

    return jsonify(result)

# =====================================================
# RUN
# =====================================================
@app.route("/api/locations")
def locations():

    BASE_DIR = Path(__file__).resolve().parent.parent

    csv_file = (
        BASE_DIR /
        "data" /
        "district_master.csv"
    )

    if not csv_file.exists():

        return jsonify({
            "error": f"File not found: {csv_file}"
        }), 404

    df = pd.read_csv(csv_file)

    return jsonify(
        df.to_dict(
            orient="records"
        )
    )

print("\n===== REGISTERED ROUTES =====")

for rule in app.url_map.iter_rules():
    print(rule)

print("=============================\n")
if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
print("\nAvailable Routes:")
for rule in app.url_map.iter_rules():
    print(rule)