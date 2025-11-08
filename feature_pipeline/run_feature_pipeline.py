import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from dotenv import load_dotenv

# Hopsworks
import hopsworks

# Ensure parent folder is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from feature_pipeline.fetch_raw import fetch_openaq, fetch_weather
from feature_pipeline.compute_features import aggregate_pollutants, build_features

# Load environment variables
load_dotenv()

CITY = os.getenv("CITY", "Karachi")
DAYS_HISTORY = int(os.getenv("DAYS_HISTORY", "14"))
LOCAL = os.getenv("LOCAL_FEATURE_STORE", "1") == "1"
HOPSWORKS_HOST = os.getenv("HOPSWORKS_HOST", "").replace("https://https://", "https://").replace("http://https://", "https://")
HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY")
HOPSWORKS_PROJECT = os.getenv("HOPSWORKS_PROJECT", "default")


def save_to_hopsworks(features: pd.DataFrame):
    """Save processed features to Hopsworks Feature Store."""
    try:
        print("☁️ Connecting to Hopsworks...")
        project = hopsworks.login(api_key_value=HOPSWORKS_API_KEY, host=HOPSWORKS_HOST, project=HOPSWORKS_PROJECT)
        fs = project.get_feature_store()

        feature_group = fs.get_or_create_feature_group(
            name="karachi_aqi_features",
            version=1,
            primary_key=["timestamp"],
            description="Karachi hourly AQI and weather features for forecasting",
            online_enabled=False
        )

        # Append new data (no overwrite)
        feature_group.insert(features, write_options={"wait_for_job": False})
        print(f"✅ Successfully uploaded {len(features)} rows to Hopsworks Feature Group 'karachi_aqi_features'.")
    except Exception as e:
        print(f"❌ Failed to upload features to Hopsworks: {e}")
        print("💾 Saving locally instead.")
        os.makedirs("data", exist_ok=True)
        features.to_csv("data/features.csv", index=False)


def main():
    print(f"🌍 Starting feature pipeline for {CITY}")

    # Step 1: Fetch raw AQI data
    try:
        raw = fetch_openaq(CITY, days=DAYS_HISTORY)
        if raw is None or raw.empty:
            print("⚠️ No AQI data fetched from API. Exiting.")
            return
        print("✅ AQI data fetched successfully")
    except Exception as e:
        print(f"❌ Error fetching AQI data: {e}")
        return

    # Step 2: Aggregate pollutant readings
    try:
        poll = aggregate_pollutants(raw)
        print("✅ Pollutant data aggregated")
    except Exception as e:
        print(f"❌ Error aggregating pollutants: {e}")
        return

    # Step 3: Fetch weather data (Karachi coordinates)
    lat, lon = 24.8607, 67.0011
    if "time" in raw.columns:
        start_date = pd.to_datetime(raw["time"].min())
        end_date = pd.to_datetime(raw["time"].max())
    else:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=DAYS_HISTORY)

    try:
        weather = fetch_weather(lat, lon, start_date, end_date)
        print("✅ Weather data fetched successfully")
    except Exception as e:
        print(f"⚠️ Could not fetch weather data: {e}")
        weather = pd.DataFrame()

    # Step 4: Build features
    try:
        features = build_features(poll, weather)
        print("✅ Features built successfully")
    except Exception as e:
        print(f"❌ Error building features: {e}")
        return

    # Step 5: Ensure timestamp column for Hopsworks
    if "time" in features.columns and "timestamp" not in features.columns:
        features["timestamp"] = pd.to_datetime(features["time"])
    elif "timestamp" in features.columns:
        features["timestamp"] = pd.to_datetime(features["timestamp"])
    else:
        features["timestamp"] = pd.date_range(end=pd.Timestamp.utcnow(), periods=len(features), freq="h")

    # Step 6: Save to local or Hopsworks
    if LOCAL:
        os.makedirs("data", exist_ok=True)
        features.to_csv("data/features.csv", index=False)
        print("💾 Saved features to data/features.csv (Local Mode)")
    else:
        save_to_hopsworks(features)

    print("🏁 Feature pipeline completed successfully!")


if __name__ == "__main__":
    main()
