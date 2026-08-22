"""
ml_model.py — PM2.5 prediction model (scikit-learn)

Trains a RandomForestRegressor on historical readings to predict PM2.5
from time features and current weather conditions.

The trained artifact is stored in model_store/ and regenerated
automatically if missing, so a fresh clone works out of the box.
"""

import threading
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine
from models import Reading, Sensor

MODEL_DIR = Path(__file__).parent / "model_store"
MODEL_PATH = MODEL_DIR / "pm25_model.joblib"

FEATURE_NAMES = [
    "hour",
    "day_of_week",
    "is_weekend",
    "temperature",
    "humidity",
    "latitude",
    "longitude",
]

_lock = threading.Lock()
_cache = {"model": None, "meta": None}


def _load_training_data(db: Session):
    """Join readings with sensor locations and build feature/target arrays."""
    rows = db.execute(
        select(
            Reading.timestamp,
            Reading.temperature,
            Reading.humidity,
            Reading.pm25,
            Sensor.latitude,
            Sensor.longitude,
        )
        .join(Sensor, Reading.sensor_id == Sensor.id)
        .where(Reading.pm25.isnot(None))
    ).all()

    features, targets = [], []
    for timestamp, temperature, humidity, pm25, latitude, longitude in rows:
        features.append(
            [
                timestamp.hour,
                timestamp.weekday(),
                1 if timestamp.weekday() >= 5 else 0,
                temperature,
                humidity,
                latitude,
                longitude,
            ]
        )
        targets.append(pm25)
    return np.array(features), np.array(targets)


def train_model(verbose: bool = True) -> dict:
    """Train from the database and persist the artifact. Returns metadata."""
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, r2_score
    from sklearn.model_selection import train_test_split

    Base.metadata.create_all(bind=engine)
    db = Session(bind=engine)
    try:
        features, targets = _load_training_data(db)
    finally:
        db.close()

    if len(features) < 100:
        raise RuntimeError(
            f"Not enough data to train ({len(features)} rows). Run generate_data.py first."
        )

    x_train, x_test, y_train, y_test = train_test_split(
        features, targets, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(n_estimators=120, random_state=42, n_jobs=-1)
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    meta = {
        "model_type": "RandomForestRegressor",
        "n_estimators": 120,
        "trained_at": datetime.now().isoformat(),
        "training_rows": int(len(features)),
        "test_rows": int(len(x_test)),
        "mae_pm25": round(float(mean_absolute_error(y_test, predictions)), 2),
        "r2": round(float(r2_score(y_test, predictions)), 3),
        "feature_names": FEATURE_NAMES,
    }

    MODEL_DIR.mkdir(exist_ok=True)
    joblib.dump({"model": model, "meta": meta}, MODEL_PATH)

    if verbose:
        print(f"Model trained on {meta['training_rows']} rows")
        print(f"MAE: {meta['mae_pm25']} µg/m³ | R²: {meta['r2']}")
        print(f"Saved to {MODEL_PATH}")
    return meta


def get_model():
    """Load the cached model, training it on first use if needed."""
    with _lock:
        if _cache["model"] is not None:
            return _cache["model"], _cache["meta"]
        if MODEL_PATH.exists():
            artifact = joblib.load(MODEL_PATH)
        else:
            train_model(verbose=False)
            artifact = joblib.load(MODEL_PATH)
        _cache["model"], _cache["meta"] = artifact["model"], artifact["meta"]
        return _cache["model"], _cache["meta"]


def predict_pm25(
    hour: int,
    day_of_week: int,
    temperature: float,
    humidity: float,
    latitude: float,
    longitude: float,
) -> float:
    """Predict PM2.5 for one feature vector."""
    model, _ = get_model()
    vector = np.array([[hour, day_of_week, 1 if day_of_week >= 5 else 0,
                        temperature, humidity, latitude, longitude]])
    return round(float(model.predict(vector)[0]), 1)


def aqi_category(pm25: float) -> str:
    """Simplified CPCB-style PM2.5 buckets."""
    if pm25 <= 50:
        return "Good"
    if pm25 <= 100:
        return "Moderate"
    if pm25 <= 150:
        return "Poor"
    if pm25 <= 200:
        return "Very Poor"
    return "Severe"


if __name__ == "__main__":
    train_model()
