import os
import requests
import pandas as pd
from datetime import datetime, timedelta

OPENAQ_BASE = os.getenv("OPENAQ_BASE", "https://api.openaq.org/v2")
OPEN_METEO_BASE = os.getenv("OPEN_METEO_BASE", "https://api.open-meteo.com/v1/forecast")

def fetch_openaq(city: str, days: int = 14):
    """Fetch AQI-like data from Open-Meteo Air Quality API for given city."""
    # Use coordinates for Karachi
    coords = {
        "Karachi": (24.8607, 67.0011)
    }
    lat, lon = coords.get(city, (24.8607, 67.0011))

    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    url = (
        f"https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}"
        f"&start_date={start_date.strftime('%Y-%m-%d')}"
        f"&end_date={end_date.strftime('%Y-%m-%d')}"
        f"&hourly=pm10,pm2_5,carbon_monoxide,ozone,nitrogen_dioxide,sulphur_dioxide,us_aqi"
    )

    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df

def fetch_weather(lat, lon, start_date, end_date, hourly_vars=None):
    if hourly_vars is None:
        hourly_vars = ["temperature_2m","relativehumidity_2m","windspeed_10m"]
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "hourly": ",".join(hourly_vars)
    }
    url = f"{OPEN_METEO_BASE}"
    resp = requests.get(url + "/forecast", params=params, timeout=30)
    resp.raise_for_status()
    j = resp.json()
    hours = j.get('hourly', {})
    if not hours:
        return pd.DataFrame()
    df = pd.DataFrame(hours)
    df['timestamp'] = pd.to_datetime(df['time'])
    return df

if __name__ == "__main__":
    df = fetch_openaq('Karachi', days=7)
    print(df.head())
