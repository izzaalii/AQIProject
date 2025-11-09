# 🌍 Pearls AQI Predictor

Default City: Karachi

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)  ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)


Purpose: Predict and monitor Air Quality Index (AQI) trends using locally processed data and trained ML models.
---

## 📖 Overview

Pearls AQI Predictor is a fully automated Air Quality Index (AQI) forecasting system built for **Karachi**. It fetches live pollution and weather data, processes it into meaningful features, trains forecasting models, and deploys them into a **Streamlit dashboard**. The entire system is powered by **Hopsworks Feature Store** and **Model Registry** for end-to-end MLOps integration.

---

## ⚙️ System Architecture

### Feature Pipeline (Hourly)
- Fetches live AQI data via **OpenAQ API**
- Retrieves weather data via **Open-Meteo**
- Aggregates and builds ML-ready features
- Pushes data into **Hopsworks Feature Store**

### Training Pipeline (Daily)
- Loads latest features from Feature Store
- Trains models for **1, 2, and 3-day forecasts**
- Evaluates models using **RMSE, MAE, R²**
- Uploads models to **Hopsworks Model Registry**

### Streamlit Dashboard
- Visualizes live AQI predictions
- Provides **SHAP** and **LIME** explainability views
- Includes EDA section with correlations, trends, and model metrics

### Automation (CI/CD)
- Hourly Feature Pipeline via **GitHub Actions**
- Daily Model Training Pipeline automation

---

## 🧠 Models Used

| Model                     | Purpose              | Framework      | Evaluation Metrics      |
|----------------------------|-------------------|---------------|-----------------------|
| RandomForestRegressor      | AQI Forecast (1–3 days) | Scikit-learn | RMSE, MAE, R²          |

> Future improvements may include TensorFlow and PyTorch-based deep learning models.

---

## 📊 Performance Metrics (Hopsworks Synced)

| Forecast Day | RMSE  | MAE  | R²   |
|-------------|-------|------|------|
| Day 1       | ~6.0  | ~4.4 | 0.93 |
| Day 2       | ~4.4  | ~3.3 | 0.96 |
| Day 3       | ~7.3  | ~4.5 | 0.92 |

All metrics are automatically fetched from the **Hopsworks Model Registry** and displayed in the EDA Dashboard.

---

## 💡 Explainability

- **SHAP:** Displays global feature importance (which pollutants and weather features most influence AQI).  
- **LIME:** Provides local interpretability for specific prediction samples.  
- Fully interactive visualizations in **Streamlit**.

---

## ⚠️ AQI Hazard Levels

| AQI Range | Category                        | Color | Health Advisory                        |
|-----------|---------------------------------|-------|---------------------------------------|
| 0–50      | Good                            | 🟢 Green | Air quality is satisfactory            |
| 51–100    | Moderate                        | 🟡 Yellow | Acceptable but minor risk             |
| 101–150   | Unhealthy for Sensitive Groups  | 🟠 Orange | Avoid outdoor exertion                 |
| 151–200   | Unhealthy                       | 🔴 Red | General public may experience effects |
| 201–300   | Very Unhealthy                  | 🟣 Purple | Emergency conditions                  |
| 301–500   | Hazardous                       | ⚫ Maroon | Health warning of emergency conditions |

> The app automatically triggers a **Hazard Alert** in the Streamlit dashboard if predictions exceed AQI 150.

---

## 🧩 Tech Stack

- **Language:** Python 3.10  
- **ML Framework:** Scikit-learn  
- **Visualization:** Streamlit, Matplotlib, Seaborn  
- **Explainability:** SHAP, LIME  
- **MLOps:** Hopsworks Feature Store & Model Registry  
- **Automation:** GitHub Actions  
- **Environment Management:** Python venv  
- **APIs:** OpenAQ, Open-Meteo  

---

## 🧱 Folder Structure
```
AQI_Project/
│
├── feature_pipeline/
│ ├── fetch_raw.py
│ ├── compute_features.py
│ └── run_feature_pipeline.py
│
├── training_pipeline/
│ └── train_models.py
│
├── web_app/
│ └── streamlit_app.py
│
├── model_registry/
│ └── load_model.py
│
├── scripts/
│ ├── run_hourly_features.ps1
│ └── run_daily_training.ps1
│
├── data/
│ ├── features.csv
│ └── models/
│
├── .github/workflows/
│ └── ci_cd.yml
│
├── .env
├── requirements.txt
└── README.md
```
---

## 🧰 Installation Guide
 **Step 1: Open PowerShell**

Right-click inside the project folder and select “Open in PowerShell.”

 **Step 2: Create Virtual Environment**
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

 **Step 3: Install Dependencies**
```
pip install --upgrade pip
pip install -r requirements.txt
```

 **Step 4: Configure Environment Variables**
```
copy .env.example .env
```

Edit the .env file as needed to update configurations.

## 🚀 Usage Instructions
 **Generate Features**
```
python feature_pipeline\run_feature_pipeline.py
```

 **Train Models**
```
python training_pipeline\train_models.py
```

 **Launch Streamlit Dashboard**
```
streamlit run web_app\streamlit_app.py
```

Open the displayed URL (typically http://localhost:8501) in your browser to view the dashboard.

## 🔁 Automation (Task Scheduler)

To automate daily and hourly updates, two PowerShell scripts are provided in the scripts\ folder:
```
Script	Purpose
run_hourly_features.ps1	Runs the feature pipeline every hour
run_daily_training.ps1	Retrains models daily
```

You can add these to Windows Task Scheduler to keep data and predictions automatically refreshed.
Make sure the scripts call Python from your virtual environment path (e.g., .venv\Scripts\python.exe).

## ☁️ Hopsworks Integration

If you prefer to push features or models to Hopsworks instead of keeping them local, edit your .env file and set:

```
LOCAL_FEATURE_STORE=0
HOPSWORKS_HOST=your_host_url
HOPSWORKS_API_KEY=your_api_key
```

## Results & Achievements

Fully automated AQI prediction pipeline

Real-time integration with live APIs

Hopsworks-based data and model versioning

CI/CD automation with GitHub Actions

Interactive dashboards with model explainability

Professional-grade MLOps workflow

## 📸 Visual Preview

<img width="1919" height="961" alt="image" src="https://github.com/user-attachments/assets/a9c41c31-6160-45ed-8fe2-87fcbbf7465f" />

# Author

Izza Ali 

Data Science Trainee at 10Pearls

📍 Karachi, Pakistan

🌐 Project: Pearls AQI Predictor (Hopsworks Integrated)


