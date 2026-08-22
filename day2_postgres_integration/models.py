"""
models.py — SQLAlchemy ORM models (these become real database tables)

Think of this as the "schema" of CitySense:
    sensors  →  where the monitors are physically installed
    readings →  what they measure, every few minutes

Compare with Day 1: Pydantic validated incoming JSON. SQLAlchemy
validates & maps data INTO the database. They work together.

Day 1 (Pydantic):  what the API accepts/sends
Day 2 (SQLAlchemy): what's stored in Postgres
"""

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    Index,
)
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class Sensor(Base):
    """A physical air-quality monitor installed somewhere in the city.

    The latitude/longitude columns are here on purpose:
    Day 3 (React + Leaflet map) will plot these on a map of Hyderabad.
    """

    __tablename__ = "sensors"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(100), nullable=False)            # e.g. "MG Road Monitor"
    location = Column(String(100), nullable=False)        # e.g. "MG Road"
    zone = Column(String(50), nullable=False)             # e.g. "Zone A"
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String(20), default="active")         # active / maintenance / offline
    description = Column(Text, nullable=True)
    installed_at = Column(DateTime(timezone=True), server_default=func.now())

    # One sensor → many readings (one-to-many relationship)
    readings = relationship("Reading", back_populates="sensor")

    def __repr__(self):
        return f"<Sensor {self.sensor_id} @ {self.location}>"


class Reading(Base):
    """A single measurement taken by a sensor at one point in time."""

    __tablename__ = "readings"

    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)

    temperature = Column(Float, nullable=False)   # °C
    humidity = Column(Float, nullable=False)      # %
    pm25 = Column(Float, nullable=False)          # µg/m³ (air quality)
    pm10 = Column(Float, nullable=True)           # µg/m³
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)

    # We'll query "all readings from sensor X after time Y, sorted by time"
    # ALMOST EVERY aggregation endpoint uses this combo — so index it.
    __table_args__ = (
        Index("ix_reading_sensor_time", "sensor_id", "timestamp"),
    )

    sensor = relationship("Sensor", back_populates="readings")

    def __repr__(self):
        return f"<Reading sensor={self.sensor_id} pm25={self.pm25:.1f} t={self.timestamp}>"