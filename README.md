# 🌍 Pearls AQI Predictor

Default City: Karachi

Purpose: Predict and monitor Air Quality Index (AQI) trends using locally processed data and trained ML models.

# ⚙️ Overview

Pearls AQI Predictor is a machine learning-based application designed to forecast AQI levels for Karachi.
It combines feature engineering, model training, and an interactive web dashboard (via Streamlit) — all running locally on Windows.

The project can also optionally connect with Hopsworks for cloud-based feature storage and model management, but this is not required for local use.

# 🧰 Installation Guide
## Step 1: Open PowerShell

Right-click inside the project folder and select “Open in PowerShell.”

## Step 2: Create Virtual Environment
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```

## Step 3: Install Dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 4: Configure Environment Variables
```
copy .env.example .env
```


Edit the .env file as needed to update configurations.

# 🚀 Usage Instructions
## Generate Features
```
python feature_pipeline\run_feature_pipeline.py
```

## Train Models
```
python training_pipeline\train_models.py
```

## Launch Streamlit Dashboard
```
streamlit run web_app\streamlit_app.py
```


Open the displayed URL (typically http://localhost:8501) in your browser to view the dashboard.

# 🔁 Optional Automation (Task Scheduler)

To automate daily and hourly updates, two PowerShell scripts are provided in the scripts\ folder:
```
Script	Purpose
run_hourly_features.ps1	Runs the feature pipeline every hour
run_daily_training.ps1	Retrains models daily
```

You can add these to Windows Task Scheduler to keep data and predictions automatically refreshed.
Make sure the scripts call Python from your virtual environment path (e.g., .venv\Scripts\python.exe).

# ☁️ Optional: Hopsworks Integration

If you prefer to push features or models to Hopsworks instead of keeping them local, edit your .env file and set:

```
LOCAL_FEATURE_STORE=0
HOPSWORKS_HOST=your_host_url
HOPSWORKS_API_KEY=your_api_key
```


This step is optional and not required for the local version.

# 🧠 Project Structure
```
Pearls_AQI_Predictor/
│
├── feature_pipeline/          # Data preprocessing and feature generation
├── training_pipeline/         # Model training, evaluation, and saving
├── web_app/                   # Streamlit dashboard code
├── scripts/                   # PowerShell automation scripts
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variable template
├── README.md                  # Documentation
└── .venv/                     # Virtual environment (created locally)
```


# 🧩 Tech Stack

| Category             | Tools / Frameworks                 |
| -------------------- | ---------------------------------- |
| Programming Language | Python 3.10+                       |
| Dashboard Framework  | Streamlit                          |
| Machine Learning     | Scikit-learn, XGBoost, CatBoost    |
| Data Handling        | Pandas, NumPy                      |
| Automation           | PowerShell, Windows Task Scheduler |
| Environment          | Python venv                        |
| Feature Store        | Hopsworks                          |

# 📊 Output

Once running, the dashboard displays:

Current AQI predictions

Historical and forecasted trends

Model performance insights

Feature importance visualization

# 📸 Visual Preview

<img width="1919" height="961" alt="image" src="https://github.com/user-attachments/assets/a9c41c31-6160-45ed-8fe2-87fcbbf7465f" />

# 🧰 Maintenance Notes

Always activate the virtual environment before running scripts.

Rerun the feature pipeline whenever new raw data is added.

Retrain models weekly (or daily) for the most accurate results.

# 🧑‍💻 Author

Developed by Izza Ali

as part of an internship project at 10Pearls
