import os
import sys
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.ensemble import RandomForestRegressor
from hopsworks import login
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure parent folder import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DATA_PATH = "data/features.csv"
MODELS_DIR = "data/models"


def load_features(path=DATA_PATH):
    """Load features CSV (handles both 'time' and 'timestamp' columns)."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found. Run the feature pipeline first.")

    preview = pd.read_csv(path, nrows=1)
    time_col = "time" if "time" in preview.columns else "timestamp"

    df = pd.read_csv(path, parse_dates=[time_col])
    df = df.rename(columns={time_col: "time"})
    df = df.sort_values("time")
    return df


def train_and_evaluate(X_train, X_test, y_train, y_test, day_label):
    """Train Random Forest model and compute metrics."""
    model = RandomForestRegressor(n_estimators=120, random_state=42)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)

    mse = mean_squared_error(y_test, preds)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, preds)
    r2 = r2_score(y_test, preds)

    print(f"📅 {day_label} -> RMSE={rmse:.2f}, MAE={mae:.2f}, R²={r2:.3f}")
    return model, {"rmse": rmse, "mae": mae, "r2": r2}


def upload_models_to_hopsworks(metrics_dict):
    """Upload all trained models to Hopsworks Model Registry with metrics and tags."""
    try:
        print("☁️ Connecting to Hopsworks Model Registry...")
        project = login(
            api_key_value=os.getenv("HOPSWORKS_API_KEY"),
            host=os.getenv("HOPSWORKS_HOST")
        )
        mr = project.get_model_registry()

        uploaded = 0
        for model_name, details in metrics_dict.items():
            model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")
            if not os.path.exists(model_path):
                print(f"⚠️ Model file {model_path} not found, skipping.")
                continue

            metrics = details["metrics"]
            metrics = {k: float(v) for k, v in metrics.items()}  # Ensure JSON-safe

            # ✅ Upload model
            model_obj = mr.python.create_model(
                name=model_name,
                description=f"Random Forest AQI forecast model for {model_name}",
                metrics=metrics
            )
            model_obj.save(model_path)

            # ✅ Add metrics as tags (for compatibility with older Hopsworks)
            try:
                for key, value in metrics.items():
                    model_obj.add_tag(key, value)
            except Exception as e:
                print(f"⚠️ Could not add tags to {model_name}: {e}")

            print(f"✅ Uploaded {model_name}.pkl to Hopsworks Model Registry")
            uploaded += 1

        if uploaded > 0:
            print(f"🎉 Successfully uploaded {uploaded} models to Hopsworks.")
        else:
            print("⚠️ No models found to upload.")

    except Exception as e:
        print(f"❌ Failed to upload models to Hopsworks: {e}")


def main():
    print("🚀 Starting model training pipeline...")

    df = load_features()
    print(f"✅ Loaded {len(df)} rows from {DATA_PATH}")

    ignore_cols = ["time", "target_day1", "target_day2", "target_day3"]
    feature_cols = [c for c in df.columns if c not in ignore_cols and df[c].dtype != "object"]

    os.makedirs(MODELS_DIR, exist_ok=True)
    metrics_dict = {}

    for day in [1, 2, 3]:
        target_col = f"target_day{day}"
        if target_col not in df.columns:
            print(f"⚠️ Skipping {target_col} (column not found).")
            continue

        sub_df = df.dropna(subset=[target_col])
        if sub_df.empty:
            print(f"⚠️ Not enough data for {target_col}. Skipping.")
            continue

        X = sub_df[feature_cols]
        y = sub_df[target_col]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model, metrics = train_and_evaluate(X_train, X_test, y_train, y_test, f"Day {day}")
        model_name = f"model_day{day}"
        model_path = os.path.join(MODELS_DIR, f"{model_name}.pkl")

        joblib.dump(model, model_path)
        print(f"💾 Saved model to {model_path}")

        metrics_dict[model_name] = {"metrics": metrics}

    print("🏁 Training completed successfully!")
    upload_models_to_hopsworks(metrics_dict)


if __name__ == "__main__":
    main()
