"""
ai_routes.py — /api/predict (ML) and /api/ask (LLM) endpoints

/api/predict uses the scikit-learn model in ml_model.py.
/api/ask answers questions about current air quality using Gemini,
falling back to a local Ollama server when GEMINI_API_KEY is not set.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from database import get_db
from ml_model import aqi_category, get_model, predict_pm25
from models import Reading, Sensor

load_dotenv()

router = APIRouter(prefix="/api", tags=["AI"])

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b-instruct")


class PredictRequest(BaseModel):
    sensor_id: str
    timestamp: Optional[datetime] = None
    temperature: Optional[float] = Field(None, ge=-50, le=60)
    humidity: Optional[float] = Field(None, ge=0, le=100)


class PredictResponse(BaseModel):
    sensor_id: str
    location: str
    target_time: str
    predicted_pm25: float
    aqi_category: str
    inputs: dict
    model_info: dict


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)


class AskResponse(BaseModel):
    question: str
    answer: str
    provider: str


def _sensor_conditions(db: Session, sensor: Sensor) -> tuple[float, float]:
    """Latest temperature/humidity observed at a sensor (fallback: city averages)."""
    row = db.execute(
        select(Reading.temperature, Reading.humidity)
        .where(Reading.sensor_id == sensor.id)
        .order_by(Reading.timestamp.desc())
        .limit(1)
    ).first()
    if row:
        return float(row[0]), float(row[1])
    averages = db.execute(
        select(func.avg(Reading.temperature), func.avg(Reading.humidity))
    ).first()
    # SQL AVG over an empty table returns NULL — fall back to sane defaults
    return round(float(averages[0] or 25.0), 1), round(float(averages[1] or 60.0), 1)


@router.post("/predict", response_model=PredictResponse)
def predict(request: PredictRequest, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.sensor_id == request.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor {request.sensor_id} not found")

    when = request.timestamp or datetime.now()
    temperature, humidity = _sensor_conditions(db, sensor)
    if request.temperature is not None:
        temperature = request.temperature
    if request.humidity is not None:
        humidity = request.humidity

    predicted = predict_pm25(
        hour=when.hour,
        day_of_week=when.weekday(),
        temperature=temperature,
        humidity=humidity,
        latitude=sensor.latitude,
        longitude=sensor.longitude,
    )

    _, meta = get_model()
    return PredictResponse(
        sensor_id=sensor.sensor_id,
        location=sensor.location,
        target_time=when.isoformat(),
        predicted_pm25=predicted,
        aqi_category=aqi_category(predicted),
        inputs={
            "temperature": temperature,
            "humidity": humidity,
            "hour": when.hour,
            "day_of_week": when.strftime("%A"),
            "latitude": sensor.latitude,
            "longitude": sensor.longitude,
        },
        model_info={"type": meta["model_type"], "mae_pm25": meta["mae_pm25"],
                    "trained_on": f"{meta['training_rows']} readings"},
    )


@router.get("/model/info")
def model_info():
    _, meta = get_model()
    return meta


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest, db: Session = Depends(get_db)):
    context = _air_quality_context(db)

    prompt = (
        "You are CitySense, an air quality assistant for Hyderabad.\n"
        "Answer the user's question in 2-4 short sentences using ONLY this live data.\n"
        "If the data cannot answer the question, say so briefly.\n\n"
        f"Live data:\n{context}\n\n"
        f"Question: {request.question}"
    )

    answer, provider, error = _call_llm(prompt)
    if answer is None:
        raise HTTPException(
            status_code=503,
            detail=f"No LLM available ({error}). Set GEMINI_API_KEY in server/.env or start Ollama locally.",
        )
    return AskResponse(question=request.question, answer=answer.strip(), provider=provider)


def _air_quality_context(db: Session) -> str:
    """Snapshot of current conditions to ground the LLM answer.

    Widens to a 7-day window when the last 24 h contain no readings,
    so aging/static datasets don't crash the endpoint (SQL AVG over
    zero rows returns NULL, and float(None) raises TypeError).
    """
    now = datetime.now()

    def window_snapshot(hours):
        cutoff = now - timedelta(hours=hours)
        avg_pm25 = db.execute(
            select(func.avg(Reading.pm25)).where(Reading.timestamp >= cutoff)
        ).scalar()
        top_rows = db.execute(
            select(Sensor.location, func.avg(Reading.pm25).label("avg_pm25"))
            .join(Reading)
            .where(Reading.timestamp >= cutoff)
            .group_by(Sensor.location)
            .order_by(func.avg(Reading.pm25).desc())
            .limit(3)
        ).all()
        return avg_pm25, top_rows

    city_avg, top_rows = window_snapshot(24)
    window_label = "last 24h"
    if city_avg is None or not top_rows:
        city_avg, top_rows = window_snapshot(7 * 24)
        window_label = "last 7 days"

    sensor_count = db.query(func.count(Sensor.id)).scalar() or 0
    reading_count = db.query(func.count(Reading.id)).scalar() or 0

    # "Right now" lens: averages for the most recent hourly slot, so answers
    # line up with what the dashboard's latest chart point shows.
    latest_slot = db.query(func.max(Reading.timestamp)).scalar()
    latest_line = None
    if latest_slot is not None:
        hour_start = latest_slot.replace(minute=0, second=0, microsecond=0)
        recent = db.execute(
            select(Sensor.location, func.avg(Reading.pm25))
            .join(Reading)
            .where(Reading.timestamp >= hour_start)
            .group_by(Sensor.location)
            .order_by(func.avg(Reading.pm25).desc())
        ).all()
        if recent:
            latest_line = (
                f"Most recent hourly averages ({hour_start:%H:%M} slot): "
                + ", ".join(f"{loc} ({round(float(a), 1)})" for loc, a in recent)
            )

    if city_avg is None:
        pollution_line = "No readings available in the last 7 days."
        hotspot_line = "Location ranking unavailable (no recent data)."
    else:
        hotspots = ", ".join(
            f"{row.location} ({round(float(row.avg_pm25), 1)})" for row in top_rows
        )
        pollution_line = f"City average PM2.5 ({window_label}): {round(float(city_avg), 1)} µg/m³"
        hotspot_line = f"Highest-pollution locations ({window_label} avg): {hotspots or 'none'}"

    lines = [
        pollution_line,
        hotspot_line,
        f"Sensor network: {sensor_count} sensors, {reading_count} readings stored",
        f"Current time: {now.strftime('%Y-%m-%d %H:%M')}",
    ]
    if latest_line:
        lines.insert(2, latest_line)
    return "\n".join(lines)


def _call_llm(prompt: str) -> tuple[Optional[str], str, str]:
    """Try Gemini first, then local Ollama. Returns (answer, provider, error_detail)."""
    errors = []

    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)
            response = client.models.generate_content(model=GEMINI_MODEL, contents=prompt)
            return response.text, "gemini", ""
        except Exception as exc:
            errors.append(f"gemini: {exc}")

    try:
        with httpx.Client(timeout=httpx.Timeout(10.0, read=300.0)) as client:
            response = client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False,
                      "keep_alive": "30m", "options": {"num_predict": 150}},
            )
            response.raise_for_status()
            return response.json()["response"], "ollama", ""
    except Exception as exc:
        errors.append(f"ollama: {exc}")

    return None, "none", "; ".join(errors)


@router.get("/health")
def ai_health():
    """Which LLM provider would be used right now."""
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    ollama_up = False
    try:
        with httpx.Client(timeout=2) as client:
            ollama_up = client.get(f"{OLLAMA_BASE_URL}/").status_code == 200
    except Exception:
        pass
    provider = "gemini" if has_key else ("ollama" if ollama_up else "none")
    return {"gemini_configured": has_key, "ollama_running": ollama_up, "active_provider": provider}
