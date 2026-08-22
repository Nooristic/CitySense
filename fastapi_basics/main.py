"""
Day 1: Mini Sensor API - FastAPI Basics
A simple REST API to practice FastAPI fundamentals
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

# Initialize FastAPI app
app = FastAPI(
    title="Mini Sensor API",
    description="A practice API for learning FastAPI ",
    version="1.0.0"
)

# Pydantic Models (Data Validation)
class SensorReading(BaseModel):
    """Model for incoming sensor readings"""
    sensor_id: str = Field(..., example="SENSOR_001")
    temperature: float = Field(..., ge=-50, le=60, example=25.5, description="Temperature in Celsius")
    humidity: float = Field(..., ge=0, le=100, example=65.0, description="Humidity percentage")
    pm25: Optional[float] = Field(None, ge=0, example=35.2, description="PM2.5 air quality reading")
    timestamp: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "sensor_id": "SENSOR_001",
                "temperature": 28.5,
                "humidity": 70.0,
                "pm25": 42.3,
                "timestamp": "2026-08-16T12:00:00"
            }
        }

class SensorInfo(BaseModel):
    """Model for sensor information"""
    sensor_id: str
    location: str
    zone: str
    status: str
    last_reading: Optional[datetime] = None

class ReadingResponse(BaseModel):
    """Model for reading submission response"""
    message: str
    data: SensorReading
    processed: bool
    received_at: datetime


# Mock database (in-memory storage for now)
mock_sensors = {
    "SENSOR_001": {"location": "MG Road", "zone": "Zone A", "status": "active"},
    "SENSOR_002": {"location": "Gachibowli", "zone": "Zone B", "status": "active"},
    "SENSOR_003": {"location": "Banjara Hills", "zone": "Zone A", "status": "maintenance"},
}

readings_storage: List[SensorReading] = []


# Endpoints

@app.get("/", tags=["Root"])
def read_root():
    """Welcome endpoint - basic health check"""
    return {
        "message": "Welcome to Mini Sensor API",
        "version": "1.0.0",
        "endpoints": {
            "docs": "/docs",
            "sensors": "/sensors/{sensor_id}",
            "all_sensors": "/sensors",
            "post_reading": "/sensors/reading",
            "readings": "/readings"
        },
        "status": "operational"
    }


@app.get("/sensors/{sensor_id}", response_model=SensorInfo, tags=["Sensors"])
def get_sensor(sensor_id: str):
    """
    Get information about a specific sensor by ID

    - **sensor_id**: Unique identifier for the sensor (e.g., SENSOR_001)
    """
    if sensor_id not in mock_sensors:
        raise HTTPException(status_code=404, detail=f"Sensor {sensor_id} not found")

    sensor_data = mock_sensors[sensor_id]
    return {
        "sensor_id": sensor_id,
        "location": sensor_data["location"],
        "zone": sensor_data["zone"],
        "status": sensor_data["status"],
        "last_reading": None  # Will be populated when we connect to database
    }


@app.get("/sensors", tags=["Sensors"])
def get_all_sensors(zone: Optional[str] = None, status: Optional[str] = None):
    """
    Get all sensors, optionally filtered by zone or status

    - **zone**: Filter by zone (e.g., "Zone A")
    - **status**: Filter by status (e.g., "active", "maintenance")
    """
    results = []

    for sensor_id, data in mock_sensors.items():
        # Apply filters if provided
        if zone and data["zone"] != zone:
            continue
        if status and data["status"] != status:
            continue

        results.append({
            "sensor_id": sensor_id,
            **data
        })

    return {
        "count": len(results),
        "filters": {"zone": zone, "status": status},
        "sensors": results
    }


@app.post("/sensors/reading", response_model=ReadingResponse, tags=["Readings"])
def post_reading(reading: SensorReading):
    """
    Submit a new sensor reading

    Accepts temperature, humidity, and optional PM2.5 readings
    """
    # Add timestamp if not provided
    if reading.timestamp is None:
        reading.timestamp = datetime.now()

    # Store the reading (in-memory for now, will be database later)
    readings_storage.append(reading)

    return {
        "message": "Reading received successfully",
        "data": reading,
        "processed": True,
        "received_at": datetime.now()
    }


@app.get("/readings", tags=["Readings"])
def get_readings(sensor_id: Optional[str] = None, limit: int = 10):
    """
    Get recent sensor readings

    - **sensor_id**: Filter by specific sensor (optional)
    - **limit**: Maximum number of readings to return (default: 10)
    """
    filtered_readings = readings_storage

    if sensor_id:
        filtered_readings = [r for r in readings_storage if r.sensor_id == sensor_id]

    # Return most recent readings first
    recent_readings = list(reversed(filtered_readings[-limit:]))

    return {
        "count": len(recent_readings),
        "total_stored": len(readings_storage),
        "filter": {"sensor_id": sensor_id},
        "readings": [r.dict() for r in recent_readings]
    }


@app.get("/health", tags=["Root"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "sensors_registered": len(mock_sensors),
        "readings_stored": len(readings_storage)
    }


# Run with: uvicorn main:app --reload
# Docs at: http://localhost:8000/docs
