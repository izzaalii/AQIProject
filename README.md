# Pearls AQI Predictor (Local Windows version)

Default city: Karachi

## Quick start (Windows)

1. Open PowerShell in this folder.
2. Create virtualenv:
   ```
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```
3. Install requirements:
   ```
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and edit if needed.
5. Generate features:
   ```
   python feature_pipeline\run_feature_pipeline.py
   ```
6. Train models:
   ```
   python training_pipeline\train_models.py
   ```
7. Run Streamlit:
   ```
   streamlit run web_app\streamlit_app.py
   ```

## Automation (Windows Task Scheduler)

Two PowerShell scripts are in `scripts\`:
- `run_hourly_features.ps1` -> run feature pipeline
- `run_daily_training.ps1` -> run training

Create Task Scheduler tasks that call PowerShell with these scripts using the venv python.

## Hopsworks (optional)
Set HOPSWORKS_HOST, HOPSWORKS_API_KEY and set LOCAL_FEATURE_STORE=0 in `.env` to push to Hopsworks.

