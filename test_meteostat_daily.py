import os
import requests

API_URL = "https://weatherapi-com.p.rapidapi.com/forecast.json"

headers = {
    "X-RapidAPI-Key": os.getenv("METEOSTAT_KEY"),
    "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
}

# combine lat,lon
location = f"{os.getenv('LAT')},{os.getenv('LON')}"

params = {
    "q": location,
    "days": "3",        # Get 3-day forecast (including tomorrow)
    "aqi": "no",
    "alerts": "no"
}

print("Testing Forecast API with:", location)

resp = requests.get(API_URL, headers=headers, params=params)

print("Status:", resp.status_code)
print("Full Body:\n", resp.text)
