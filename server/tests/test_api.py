"""
test_api.py — basic API tests for CitySense (Day 5)

Runs against the live local PostgreSQL (citysense DB must be seeded —
see generate_data.py). No mocking; matches the project's manual-verification
style while adding a repeatable safety net.

Run from server/:
    python -m pytest tests/ -v

Requires: PostgreSQL running on localhost:5432, database `citysense` seeded.
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from database import SessionLocal
from main import app
from models import Reading, Sensor

client = TestClient(app)


@pytest.fixture()
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def temp_sensor():
    """Create a disposable sensor via the API; delete it (and readings) after."""
    sensor_id = f"TEST_{uuid.uuid4().hex[:8]}"
    response = client.post(
        "/sensors",
        json={
            "sensor_id": sensor_id,
            "name": "Test Sensor",
            "location": "Test Location",
            "zone": "test",
            "latitude": 17.3850,
            "longitude": 78.4867,
        },
    )
    assert response.status_code == 200, response.text
    created_ids = {"sensor_pk": response.json()["id"], "sensor_id": sensor_id}
    yield created_ids

    session = SessionLocal()
    try:
        row = session.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
        if row:
            session.query(Reading).filter(Reading.sensor_id == row.id).delete()
            session.delete(row)
            session.commit()
    finally:
        session.close()


# ==================== HEALTH / ROOT ====================

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["sensors"] > 0
    assert body["readings"] > 0


def test_root_info():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"


# ==================== SENSORS ====================

def test_list_sensors():
    response = client.get("/sensors")
    assert response.status_code == 200
    sensors = response.json()
    assert len(sensors) >= 10
    required = {"sensor_id", "name", "location", "zone", "latitude", "longitude"}
    assert required.issubset(sensors[0].keys())


def test_get_single_sensor():
    response = client.get("/sensors/SENSOR_001")
    assert response.status_code == 200
    assert response.json()["sensor_id"] == "SENSOR_001"


def test_get_unknown_sensor_returns_404():
    response = client.get("/sensors/DOES_NOT_EXIST")
    assert response.status_code == 404


def test_create_sensor_and_duplicate_rejected(temp_sensor):
    duplicate = client.post(
        "/sensors",
        json={
            "sensor_id": temp_sensor["sensor_id"],
            "name": "Dup",
            "location": "Dup",
            "zone": "test",
            "latitude": 17.3850,
            "longitude": 78.4867,
        },
    )
    assert duplicate.status_code == 400


# ==================== READINGS ====================

def test_submit_reading_roundtrip(temp_sensor):
    payload = {
        "sensor_id": temp_sensor["sensor_id"],
        "temperature": 28.5,
        "humidity": 61.0,
        "pm25": 42.3,
        "pm10": 80.0,
    }
    created = client.post("/readings", json=payload)
    assert created.status_code == 200
    body = created.json()
    assert body["pm25"] == pytest.approx(42.3)

    listed = client.get(f"/readings?sensor_id={temp_sensor['sensor_id']}&hours=1")
    assert listed.status_code == 200
    assert listed.json()["count"] >= 1


def test_submit_reading_unknown_sensor_returns_404():
    response = client.post(
        "/readings",
        json={"sensor_id": "NO_SUCH_SENSOR", "temperature": 20.0, "humidity": 50.0, "pm25": 10.0},
    )
    assert response.status_code == 404


def test_submit_reading_validation_error(temp_sensor):
    response = client.post(
        "/readings",
        json={
            "sensor_id": temp_sensor["sensor_id"],
            "temperature": 25.0,
            "humidity": 50.0,
            "pm25": -5.0,
        },
    )
    assert response.status_code == 422


def test_get_readings_limit_respected():
    response = client.get("/readings?sensor_id=SENSOR_001&hours=168&limit=5")
    assert response.status_code == 200
    assert response.json()["count"] <= 5


# ==================== AGGREGATIONS ====================

def test_aggregation_by_location():
    response = client.get("/aggregations/by-location?hours=24")
    assert response.status_code == 200
    locations = response.json()["locations"]
    assert len(locations) > 0
    assert "avg_pm25" in locations[0]


def test_hourly_trend_and_unknown_sensor():
    response = client.get("/aggregations/hourly-trend?sensor_id=SENSOR_001&hours=24")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) > 0
    assert {"hour", "avg_temperature", "avg_humidity", "avg_pm25"} == set(data[0].keys())

    missing = client.get("/aggregations/hourly-trend?sensor_id=NOPE&hours=24")
    assert missing.status_code == 404


def test_top_polluted_limit():
    response = client.get("/aggregations/top-polluted?hours=168&limit=3")
    assert response.status_code == 200
    assert len(response.json()["top_polluted"]) <= 3


# ==================== AI ENDPOINTS ====================

def test_predict_known_sensor():
    response = client.post("/api/predict", json={"sensor_id": "SENSOR_001"})
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["predicted_pm25"], (int, float))
    assert body["aqi_category"] in {"Good", "Moderate", "Poor", "Very Poor", "Severe"}
    assert "mae_pm25" in body["model_info"]


def test_predict_unknown_sensor_returns_404():
    response = client.post("/api/predict", json={"sensor_id": "NO_SUCH_SENSOR"})
    assert response.status_code == 404


def test_model_info():
    response = client.get("/api/model/info")
    assert response.status_code == 200
    meta = response.json()
    assert meta["model_type"] == "RandomForestRegressor"
    assert meta["training_rows"] > 0
