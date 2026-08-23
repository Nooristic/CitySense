"""
main.py — FastAPI with PostgreSQL integration

Day 2 evolution of the Day 1 API:
- Replaced in-memory storage with PostgreSQL
- Added SQLAlchemy ORM models
- Built aggregation endpoints (AVG, GROUP BY)
- Ready for 75k+ sensor readings
"""

from fastapi import FastAPI, HTTPException, Depends, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from sqlalchemy.exc import OperationalError
from typing import Optional, List
from datetime import datetime, timedelta

from database import get_db
from models import Sensor, Reading
from ai_routes import router as ai_router

app = FastAPI(
    title="CitySense API",
    description="Smart city air quality monitoring platform with PostgreSQL backend",
    version="2.0.0",
)

# Enable CORS for React frontend (Day 3)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai_router)


@app.exception_handler(OperationalError)
async def database_unavailable(request: Request, exc: OperationalError):
    """PostgreSQL down/restarting → clean 503 instead of a raw 500 traceback."""
    return JSONResponse(
        status_code=503,
        content={"detail": "Database unavailable - check PostgreSQL is running."},
    )


# ==================== PYDANTIC MODELS (API schemas) ====================
# These validate incoming/outgoing JSON — they do NOT store data

class SensorCreate(BaseModel):
    """Schema for creating a new sensor"""
    sensor_id: str
    name: str
    location: str
    zone: str
    latitude: float
    longitude: float
    description: Optional[str] = None


class SensorResponse(BaseModel):
    """What the API returns for a sensor"""
    id: int
    sensor_id: str
    name: str
    location: str
    zone: str
    latitude: float
    longitude: float
    status: str
    last_reading: Optional[datetime] = None

    class Config:
        from_attributes = True  # Allows SQLAlchemy models → Pydantic


class ReadingCreate(BaseModel):
    """Schema for submitting a sensor reading"""
    sensor_id: str
    temperature: float = Field(ge=-50, le=60)
    humidity: float = Field(ge=0, le=100)
    pm25: float = Field(ge=0)
    pm10: Optional[float] = Field(None, ge=0)
    timestamp: Optional[datetime] = None


class ReadingResponse(BaseModel):
    """What the API returns for a reading"""
    id: int
    sensor_id: int
    temperature: float
    humidity: float
    pm25: float
    pm10: Optional[float]
    timestamp: datetime

    class Config:
        from_attributes = True


# ==================== BASIC ENDPOINTS ====================

@app.get("/", tags=["Root"])
def read_root():
    """API health check and available endpoints"""
    return {
        "message": "CitySense API v2.0 — PostgreSQL Edition",
        "status": "operational",
        "database": "PostgreSQL + SQLAlchemy",
        "endpoints": {
            "docs": "/docs",
            "sensors": "/sensors",
            "readings": "/readings",
            "aggregations": "/aggregations/by-location",
        },
    }


@app.get("/health", tags=["Root"])
def health_check(db: Session = Depends(get_db)):
    """Health check with database stats"""
    sensor_count = db.query(Sensor).count()
    reading_count = db.query(Reading).count()

    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "database": "connected",
        "sensors": sensor_count,
        "readings": reading_count,
    }


# ==================== SENSOR ENDPOINTS ====================

@app.get("/sensors", response_model=List[SensorResponse], tags=["Sensors"])
def get_all_sensors(
    zone: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get all sensors with optional filters"""
    query = db.query(Sensor)

    if zone:
        query = query.filter(Sensor.zone == zone)
    if status:
        query = query.filter(Sensor.status == status)

    sensors = query.all()
    return sensors


@app.get("/sensors/{sensor_id}", response_model=SensorResponse, tags=["Sensors"])
def get_sensor(sensor_id: str, db: Session = Depends(get_db)):
    """Get a specific sensor by sensor_id"""
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()

    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")

    return sensor


@app.post("/sensors", response_model=SensorResponse, tags=["Sensors"])
def create_sensor(sensor: SensorCreate, db: Session = Depends(get_db)):
    """Create a new sensor (admin endpoint)"""
    # Check if sensor_id already exists
    existing = db.query(Sensor).filter(Sensor.sensor_id == sensor.sensor_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Sensor ID already exists")

    db_sensor = Sensor(**sensor.dict())
    db.add(db_sensor)
    db.commit()
    db.refresh(db_sensor)

    return db_sensor


# ==================== READING ENDPOINTS ====================

@app.post("/readings", response_model=ReadingResponse, tags=["Readings"])
def submit_reading(reading: ReadingCreate, db: Session = Depends(get_db)):
    """Submit a new sensor reading"""
    # Find the sensor
    sensor = db.query(Sensor).filter(Sensor.sensor_id == reading.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor {reading.sensor_id} not found")

    # Add timestamp if not provided
    if reading.timestamp is None:
        reading.timestamp = datetime.now()

    # Create reading
    db_reading = Reading(
        sensor_id=sensor.id,
        temperature=reading.temperature,
        humidity=reading.humidity,
        pm25=reading.pm25,
        pm10=reading.pm10,
        timestamp=reading.timestamp,
    )

    db.add(db_reading)
    db.commit()
    db.refresh(db_reading)

    return db_reading


@app.get("/readings", tags=["Readings"])
def get_readings(
    sensor_id: Optional[str] = None,
    hours: int = Query(24, ge=1, le=168, description="Hours of data to retrieve"),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    """Get recent readings with optional sensor filter"""
    query = db.query(Reading).join(Sensor)

    # Filter by sensor if specified
    if sensor_id:
        query = query.filter(Sensor.sensor_id == sensor_id)

    # Time filter
    cutoff = datetime.now() - timedelta(hours=hours)
    query = query.filter(Reading.timestamp >= cutoff)

    # Order and limit
    query = query.order_by(desc(Reading.timestamp)).limit(limit)

    readings = query.all()

    return {
        "count": len(readings),
        "filters": {"sensor_id": sensor_id, "hours": hours},
        "readings": [
            {
                "id": r.id,
                "sensor_id": r.sensor.sensor_id,
                "location": r.sensor.location,
                "temperature": r.temperature,
                "humidity": r.humidity,
                "pm25": r.pm25,
                "timestamp": r.timestamp,
            }
            for r in readings
        ],
    }


# ==================== AGGREGATION ENDPOINTS ====================

@app.get("/aggregations/by-location", tags=["Aggregations"])
def aggregate_by_location(
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Average readings grouped by location for the last N hours"""
    cutoff = datetime.now() - timedelta(hours=hours)

    results = (
        db.query(
            Sensor.location,
            Sensor.zone,
            func.avg(Reading.temperature).label("avg_temperature"),
            func.avg(Reading.humidity).label("avg_humidity"),
            func.avg(Reading.pm25).label("avg_pm25"),
            func.count(Reading.id).label("reading_count"),
        )
        .join(Reading)
        .filter(Reading.timestamp >= cutoff)
        .group_by(Sensor.location, Sensor.zone)
        .all()
    )

    return {
        "time_range": f"Last {hours} hours",
        "locations": [
            {
                "location": r.location,
                "zone": r.zone,
                "avg_temperature": round(r.avg_temperature, 2),
                "avg_humidity": round(r.avg_humidity, 2),
                "avg_pm25": round(r.avg_pm25, 2),
                "reading_count": r.reading_count,
            }
            for r in results
        ],
    }


@app.get("/aggregations/hourly-trend", tags=["Aggregations"])
def hourly_trend(
    sensor_id: str,
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db),
):
    """Hourly average readings for a specific sensor"""
    sensor = db.query(Sensor).filter(Sensor.sensor_id == sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")

    cutoff = datetime.now() - timedelta(hours=hours)

    # PostgreSQL date_trunc for hourly bucketing
    results = (
        db.query(
            func.date_trunc("hour", Reading.timestamp).label("hour"),
            func.avg(Reading.temperature).label("avg_temperature"),
            func.avg(Reading.humidity).label("avg_humidity"),
            func.avg(Reading.pm25).label("avg_pm25"),
        )
        .filter(Reading.sensor_id == sensor.id)
        .filter(Reading.timestamp >= cutoff)
        .group_by("hour")
        .order_by("hour")
        .all()
    )

    return {
        "sensor_id": sensor_id,
        "location": sensor.location,
        "time_range": f"Last {hours} hours",
        "data": [
            {
                "hour": r.hour.isoformat(),
                "avg_temperature": round(r.avg_temperature, 2),
                "avg_humidity": round(r.avg_humidity, 2),
                "avg_pm25": round(r.avg_pm25, 2),
            }
            for r in results
        ],
    }


@app.get("/aggregations/top-polluted", tags=["Aggregations"])
def top_polluted_locations(
    hours: int = Query(24, ge=1, le=168),
    limit: int = Query(5, ge=1, le=10),
    db: Session = Depends(get_db),
):
    """Top N most polluted locations by PM2.5"""
    cutoff = datetime.now() - timedelta(hours=hours)

    results = (
        db.query(
            Sensor.location,
            Sensor.zone,
            Sensor.latitude,
            Sensor.longitude,
            func.avg(Reading.pm25).label("avg_pm25"),
            func.max(Reading.pm25).label("max_pm25"),
        )
        .join(Reading)
        .filter(Reading.timestamp >= cutoff)
        .group_by(Sensor.location, Sensor.zone, Sensor.latitude, Sensor.longitude)
        .order_by(desc("avg_pm25"))
        .limit(limit)
        .all()
    )

    return {
        "time_range": f"Last {hours} hours",
        "top_polluted": [
            {
                "location": r.location,
                "zone": r.zone,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "avg_pm25": round(r.avg_pm25, 2),
                "max_pm25": round(r.max_pm25, 2),
            }
            for r in results
        ],
    }


# Run with: uvicorn main:app --reload
# Docs at: http://localhost:8000/docs
