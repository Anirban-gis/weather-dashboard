import os

API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Local development fallback
if not API_KEY:
    API_KEY = "c4abeba69d2950ffd52c4b8af7f746f2"

print("API Key Loaded:", API_KEY[:5] + "*****")