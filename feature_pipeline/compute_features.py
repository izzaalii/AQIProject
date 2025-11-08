import pandas as pd
import numpy as np
from sklearn.impute import SimpleImputer
from feature_pipeline.aqi_utils import pm25_to_aqi


def aggregate_pollutants(meas_df):
    # Handle both "timestamp" (OpenAQ) and "time" (Open-Meteo)
    if 'timestamp' in meas_df.columns:
        meas_df['time'] = pd.to_datetime(meas_df['timestamp'])
    elif 'time' in meas_df.columns:
        meas_df['time'] = pd.to_datetime(meas_df['time'])
    else:
        raise KeyError("No timestamp or time column found in data")

    # Round or floor to hourly frequency
    meas_df['hour'] = meas_df['time'].dt.floor('h')

    # Pivot pollutants so each parameter becomes a column
    if 'parameter' in meas_df.columns and 'value' in meas_df.columns:
        pivot = meas_df.pivot_table(index='hour', columns='parameter', values='value', aggfunc='mean')
        pivot = pivot.reset_index().rename(columns={'hour': 'time'})
    else:
        # If Open-Meteo format already has columns like pm10, pm2_5, etc.
        pivot = meas_df.copy()
        pivot = pivot.groupby('time').mean(numeric_only=True).reset_index()

    # Normalize column names
    pivot.columns = [c.replace('.', '_').lower() for c in pivot.columns]
    return pivot


def build_features(pollutant_df, weather_df=None):
    df = pollutant_df.copy()
    df = df.sort_values('time')
    df['hour'] = df['time'].dt.hour
    df['day'] = df['time'].dt.day
    df['month'] = df['time'].dt.month

    # Handle PM2.5 and AQI calculation
    pm_cols = [c for c in df.columns if 'pm25' in c or 'pm2_5' in c or 'pm2.5' in c]
    if pm_cols:
        df['pm25_val'] = df[pm_cols[0]]
        df['aqi_pm25'] = df['pm25_val'].apply(pm25_to_aqi)
    else:
        df['pm25_val'] = np.nan
        df['aqi_pm25'] = np.nan

    # Derived AQI change rate
    df['aqi_lag1'] = df['aqi_pm25'].shift(1)
    df['aqi_change_rate'] = (df['aqi_pm25'] - df['aqi_lag1']) / (df['aqi_lag1'] + 1e-6)

    # Merge with weather data if available
    if weather_df is not None and not weather_df.empty:
        if 'timestamp' in weather_df.columns:
            weather_df['time'] = pd.to_datetime(weather_df['timestamp'])
        weather_df = weather_df.sort_values('time')
        df = pd.merge_asof(df.sort_values('time'), weather_df, on='time', direction='nearest')

    # Handle missing numeric data
    imputer = SimpleImputer(strategy='mean')
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if numeric_cols:
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

    # Set index for time series
    df = df.set_index('time')

    # Targets for 1-, 2-, and 3-day AQI forecast
    df['target_day1'] = df['aqi_pm25'].shift(-24).rolling(window=24, min_periods=1).mean()
    df['target_day2'] = df['aqi_pm25'].shift(-48).rolling(window=24, min_periods=1).mean()
    df['target_day3'] = df['aqi_pm25'].shift(-72).rolling(window=24, min_periods=1).mean()

    df = df.reset_index()
    return df
