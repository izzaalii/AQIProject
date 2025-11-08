import os, joblib
def load_model_for_day(day_index, models_dir="data/models"):
    path = os.path.join(models_dir, f"model_day{day_index}.pkl")
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return joblib.load(path)
