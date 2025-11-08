import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from hopsworks import login
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_features_from_hopsworks():
    """Fetch latest features from Hopsworks Feature Store."""
    print("☁️ Connecting to Hopsworks Feature Store...")
    project = login(api_key_value=os.getenv("HOPSWORKS_API_KEY"),
                    host=os.getenv("HOPSWORKS_HOST"))
    fs = project.get_feature_store()
    fg = fs.get_feature_group(name="karachi_aqi_features", version=1)
    df = fg.read()
    print(f"✅ Loaded {len(df)} rows from Feature Store.")
    return df

def run_eda(df):
    """Perform basic EDA and generate visual trends."""
    os.makedirs("eda/outputs", exist_ok=True)

    print("📊 Running Exploratory Data Analysis...")

    # Convert time column
    time_col = "time" if "time" in df.columns else "timestamp"
    df[time_col] = pd.to_datetime(df[time_col])

    # AQI Trend over time
    plt.figure(figsize=(12, 5))
    sns.lineplot(x=time_col, y="aqi_pm25", data=df)
    plt.title("AQI Trend over Time (PM2.5-based AQI)")
    plt.xlabel("Timestamp")
    plt.ylabel("AQI (PM2.5)")
    plt.savefig("eda/outputs/aqi_trend.png", bbox_inches="tight")
    plt.close()

    # Correlation heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(df.corr(numeric_only=True), annot=True, cmap="coolwarm", fmt=".2f")
    plt.title("Feature Correlation Heatmap")
    plt.savefig("eda/outputs/correlation_heatmap.png", bbox_inches="tight")
    plt.close()

    # Distribution of pollutants
    pollutants = [c for c in df.columns if "pm" in c or "ozone" in c or "nitrogen" in c or "sulphur" in c]
    for col in pollutants:
        plt.figure(figsize=(8, 4))
        sns.histplot(df[col], bins=30, kde=True, color="skyblue")
        plt.title(f"Distribution of {col}")
        plt.xlabel(col)
        plt.savefig(f"eda/outputs/dist_{col}.png", bbox_inches="tight")
        plt.close()

    print("✅ EDA completed. Visuals saved in eda/outputs/")

def main():
    df = load_features_from_hopsworks()
    run_eda(df)

if __name__ == "__main__":
    main()
