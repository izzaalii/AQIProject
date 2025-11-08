import streamlit as st
import pandas as pd
import numpy as np
import joblib
import shap
from lime.lime_tabular import LimeTabularExplainer
import matplotlib.pyplot as plt
import seaborn as sns
from hopsworks import login
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()
HOPSWORKS_HOST = os.getenv("HOPSWORKS_HOST")
HOPSWORKS_API_KEY = os.getenv("HOPSWORKS_API_KEY")

st.set_page_config(page_title="Pearls AQI Predictor", layout="wide")

# Sidebar navigation
st.sidebar.title("🌍 Pearls AQI Predictor (Hopsworks Integrated)")
page = st.sidebar.radio("Navigation", ["Forecast Dashboard", "EDA Dashboard"])

# Common data loader
@st.cache_data
def load_data():
    path = "data/features.csv"
    df = pd.read_csv(path)
    if "time" in df.columns:
        df["timestamp"] = pd.to_datetime(df["time"])
    elif "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
    else:
        df["timestamp"] = pd.date_range(end=pd.Timestamp.today(), periods=len(df), freq="h")
    return df

df = load_data()

# -------------------------------------------------------------------
# FORECAST DASHBOARD
# -------------------------------------------------------------------
if page == "Forecast Dashboard":

    st.sidebar.subheader("Forecast Settings")
    day_choice = st.sidebar.selectbox("Select Forecast Day", [1, 2, 3], key="forecast_day")

    forecast_date = (datetime.today() + timedelta(days=day_choice)).strftime("%A, %d %b %Y")
    st.sidebar.write(f"📅 Forecast Date: **{forecast_date}**")

    @st.cache_resource
    def load_latest_model(day_choice: int):
        st.info("Connecting to Hopsworks Model Registry...")
        project = login(api_key_value=HOPSWORKS_API_KEY, host=HOPSWORKS_HOST)
        mr = project.get_model_registry()
        model_name = f"model_day{day_choice}"

        try:
            latest_model = mr.get_model(model_name)
            st.success(f"Loaded {model_name} from Hopsworks.")
        except Exception as e:
            st.error(f"Could not fetch model {model_name} from Hopsworks: {e}")
            raise e

        model_dir = latest_model.download()
        model_path = os.path.join(model_dir, f"{model_name}.pkl")

        if not os.path.exists(model_path):
            st.warning(f"Model file not found in {model_dir}, using local fallback.")
            model_path = os.path.join("data", "models", f"{model_name}.pkl")

        model = joblib.load(model_path)
        return model

    model = load_latest_model(day_choice)

    ignore_cols = ["time", "timestamp", "target_day1", "target_day2", "target_day3"]
    X = df[[c for c in df.columns if c not in ignore_cols and df[c].dtype != "object"]].fillna(0)

    preds = model.predict(X)
    latest_pred = preds[-1]

    st.title("🌫️ Karachi Air Quality Forecast")
    st.metric(label=f"Predicted AQI for {forecast_date}", value=f"{latest_pred:.1f}")

    st.line_chart(pd.DataFrame({
        "timestamp": df["timestamp"],
        "Predicted AQI": preds
    }).set_index("timestamp"))

    st.subheader("🔍 Feature Importance (SHAP)")
    try:
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X)
        shap.summary_plot(shap_values, X, plot_type="bar", show=False)
        st.pyplot(plt.gcf())
        plt.clf()
    except Exception as e:
        st.warning(f"Could not generate SHAP plot: {e}")

    st.subheader("💡 Local Explanation (LIME)")
    try:
        sample_index = np.random.randint(0, len(X))
        lime_explainer = LimeTabularExplainer(X.values, mode="regression", feature_names=X.columns.tolist())
        exp = lime_explainer.explain_instance(X.values[sample_index], model.predict)
        st.markdown(f"<p style='color:white;'>Explaining prediction for sample #{sample_index}</p>", unsafe_allow_html=True)
        st.components.v1.html(exp.as_html(), height=600)
    except Exception as e:
        st.warning(f"Could not generate LIME explanation: {e}")

    st.caption("Developed with ❤️ by Syeda Faryal Fatima | 10Pearls | Hopsworks Integrated AQI Predictor")

# -------------------------------------------------------------------
# EDA DASHBOARD
# -------------------------------------------------------------------
else:
    st.title("📊 Exploratory Data Analysis (EDA)")
    st.write("A quick overview of trends, correlations, patterns, and model performance for Karachi AQI data.")

    # Trend over time
    st.subheader("📈 AQI Trend Over Time")
    if "us_aqi" in df.columns:
        st.line_chart(df.set_index("timestamp")["us_aqi"])
    else:
        st.warning("No AQI column found in dataset.")

    # Correlation Heatmap
    st.subheader("🔥 Pollutant Correlation Heatmap")
    numeric_cols = df.select_dtypes(include=[np.number])
    corr = numeric_cols.corr()

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.heatmap(corr, annot=False, cmap="coolwarm", ax=ax)
    st.pyplot(fig)

    # Distribution plots
    st.subheader("💨 Pollutant Distributions")
    pollutants = ["pm2_5", "pm10", "ozone", "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide"]
    for col in pollutants:
        if col in df.columns:
            st.write(f"Distribution of {col}")
            fig, ax = plt.subplots()
            sns.histplot(df[col].dropna(), kde=True, ax=ax)
            st.pyplot(fig)

     # ------------------- MODEL PERFORMANCE SECTION -------------------
    st.subheader("📈 Model Performance (From Hopsworks Registry)")

    try:
        project = login(api_key_value=HOPSWORKS_API_KEY, host=HOPSWORKS_HOST)
        mr = project.get_model_registry()

        models_data = []
        for day in [1, 2, 3]:
            model_name = f"model_day{day}"
            try:
                # ✅ Get the latest version automatically
                model_obj = mr.get_model(model_name, version=None)

                # Hopsworks 4.2.x stores metrics under model_obj.model_schema or meta field
                metrics = {}
                if hasattr(model_obj, "metrics") and model_obj.metrics:
                    metrics = model_obj.metrics
                elif hasattr(model_obj, "get_metadata"):
                    try:
                        metrics = model_obj.get_metadata().get("metrics", {})
                    except Exception:
                        pass
                elif hasattr(model_obj, "to_dict"):
                    data = model_obj.to_dict()
                    metrics = data.get("metrics", {}) or data.get("model_schema", {}).get("metrics", {})

                models_data.append({
                    "Model": f"Day {day}",
                    "RMSE": metrics.get("rmse", np.nan),
                    "MAE": metrics.get("mae", np.nan),
                    "R²": metrics.get("r2", np.nan)
                })
                st.success(f"Fetched metrics for {model_name}")
            except Exception as e:
                st.warning(f"Could not load metrics for {model_name}: {e}")

        if models_data:
            perf_df = pd.DataFrame(models_data)
            st.dataframe(perf_df.set_index("Model"), use_container_width=True)

            st.write("### 📊 Metrics Comparison")
            fig, ax = plt.subplots(figsize=(8, 5))
            melted = perf_df.melt(id_vars="Model", var_name="Metric", value_name="Value")
            sns.barplot(data=melted, x="Model", y="Value", hue="Metric", ax=ax)
            st.pyplot(fig)
        else:
            st.warning("No model performance metrics found in Hopsworks.")
    except Exception as e:
        st.warning(f"Could not load model metrics: {e}")


