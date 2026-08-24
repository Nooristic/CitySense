"""
generate_data.py — Realistic IoT dataset generator

Generates 7 days of sensor readings (75,000+ rows) with:
- Temperature that follows time-of-day patterns
- Humidity inversely correlated with temperature
- PM2.5 pollution that peaks during rush hours
- 10 sensors across Hyderabad locations

Run this ONCE after creating the database tables.
"""

import random
import math
from datetime import datetime, timedelta
from faker import Faker
from sqlalchemy.orm import Session

from database import SessionLocal, engine
from models import Base, Sensor, Reading

fake = Faker()


# Hyderabad locations with real coordinates
SENSOR_LOCATIONS = [
    {"sensor_id": "SENSOR_001", "name": "MG Road Monitor", "location": "MG Road", "zone": "Zone A", "lat": 12.9716, "lon": 77.5946},
    {"sensor_id": "SENSOR_002", "name": "Gachibowli Station", "location": "Gachibowli", "zone": "Zone B", "lat": 17.4435, "lon": 78.3772},
    {"sensor_id": "SENSOR_003", "name": "Banjara Hills Hub", "location": "Banjara Hills", "zone": "Zone A", "lat": 17.4239, "lon": 78.4738},
    {"sensor_id": "SENSOR_004", "name": "Kondapur Junction", "location": "Kondapur", "zone": "Zone B", "lat": 17.4690, "lon": 78.3638},
    {"sensor_id": "SENSOR_005", "name": "Jubilee Hills Plaza", "location": "Jubilee Hills", "zone": "Zone A", "lat": 17.4329, "lon": 78.4037},
    {"sensor_id": "SENSOR_006", "name": "HITEC City Center", "location": "HITEC City", "zone": "Zone C", "lat": 17.4474, "lon": 78.3808},
    {"sensor_id": "SENSOR_007", "name": "Kukatpally Ring Road", "location": "Kukatpally", "zone": "Zone C", "lat": 17.4948, "lon": 78.3975},
    {"sensor_id": "SENSOR_008", "name": "Secunderabad Station", "location": "Secunderabad", "zone": "Zone D", "lat": 17.4400, "lon": 78.5018},
    {"sensor_id": "SENSOR_009", "name": "LB Nagar Terminal", "location": "LB Nagar", "zone": "Zone D", "lat": 17.3487, "lon": 78.5527},
    {"sensor_id": "SENSOR_010", "name": "Uppal Metro", "location": "Uppal", "zone": "Zone D", "lat": 17.4060, "lon": 78.5591},
]


def generate_realistic_temperature(hour: int, base_temp: float = 25.0) -> float:
    """Temperature follows a sine wave: coolest at 6 AM, hottest at 2 PM."""
    # Peak at hour 14 (2 PM), trough at hour 6 (6 AM)
    cycle = math.sin((hour - 6) * math.pi / 12)
    temp = base_temp + 8 * cycle + random.uniform(-2, 2)
    return round(temp, 2)


def generate_realistic_humidity(temperature: float) -> float:
    """Humidity is inversely correlated with temperature."""
    # Hotter → drier air, cooler → more humid
    base_humidity = 90 - (temperature - 15) * 2
    humidity = base_humidity + random.uniform(-10, 10)
    return round(max(30, min(95, humidity)), 2)


def generate_realistic_pm25(hour: int, is_weekend: bool = False) -> float:
    """PM2.5 pollution peaks during rush hours (8-10 AM, 6-8 PM)."""
    # Base pollution level
    base_pm25 = 35.0

    # Rush hour spikes (weekdays only)
    if not is_weekend:
        if 8 <= hour <= 10:
            base_pm25 += 40  # Morning traffic
        elif 18 <= hour <= 20:
            base_pm25 += 50  # Evening traffic (worse)

    # Night hours are cleaner
    if 0 <= hour <= 5:
        base_pm25 -= 15

    # Add randomness
    pm25 = base_pm25 + random.uniform(-15, 15)
    return round(max(5, pm25), 2)


def create_sensors(db: Session):
    """Create 10 sensor records."""
    print("Creating sensors...")
    sensors = []

    for loc in SENSOR_LOCATIONS:
        sensor = Sensor(
            sensor_id=loc["sensor_id"],
            name=loc["name"],
            location=loc["location"],
            zone=loc["zone"],
            latitude=loc["lat"],
            longitude=loc["lon"],
            status="active",
            description=f"Air quality monitor at {loc['location']}",
        )
        sensors.append(sensor)

    db.add_all(sensors)
    db.commit()
    print(f"Created {len(sensors)} sensors")
    return sensors


def generate_readings(db: Session, sensors: list, days: int = 7):
    """Generate realistic readings for N days, every 5 minutes per sensor.

    Math:
        10 sensors × 7 days × 24 hours × 12 readings/hour = 20,160 readings
        (We'll get ~20k-21k because of randomness)
    """
    print(f"Generating {days} days of readings (every 5 min per sensor)...")

    # Start 7 days ago (relative, not hardcoded) so freshly seeded data always
    # falls inside the API's NOW()-based aggregation windows.
    start_date = (datetime.now() - timedelta(days=7)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    readings = []
    batch_size = 5000  # Insert in batches for performance

    for sensor in sensors:
        current_time = start_date

        for day in range(days):
            for hour in range(24):
                # 12 readings per hour (every 5 minutes)
                for minute in range(0, 60, 5):
                    timestamp = current_time + timedelta(days=day, hours=hour, minutes=minute)

                    # Is it Saturday or Sunday?
                    is_weekend = timestamp.weekday() >= 5

                    temp = generate_realistic_temperature(hour)
                    humidity = generate_realistic_humidity(temp)
                    pm25 = generate_realistic_pm25(hour, is_weekend)
                    pm10 = pm25 * random.uniform(1.5, 2.0)  # PM10 is usually 1.5-2× PM2.5

                    reading = Reading(
                        sensor_id=sensor.id,
                        temperature=temp,
                        humidity=humidity,
                        pm25=pm25,
                        pm10=round(pm10, 2),
                        timestamp=timestamp,
                    )
                    readings.append(reading)

                    # Batch insert for performance
                    if len(readings) >= batch_size:
                        db.add_all(readings)
                        db.commit()
                        print(f"  Inserted {len(readings)} readings...")
                        readings = []

    # Insert remaining readings
    if readings:
        db.add_all(readings)
        db.commit()
        print(f"  Inserted {len(readings)} readings")

    # Final count
    total = db.query(Reading).count()
    print(f"Total readings in database: {total:,}")


def main():
    """Initialize database and generate data."""
    print("Starting data generation...\n")

    # Create all tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created\n")

    # Get a database session
    db = SessionLocal()

    try:
        # Check if data already exists
        existing_sensors = db.query(Sensor).count()
        if existing_sensors > 0:
            print(f"WARNING: Found {existing_sensors} existing sensors. Skipping data generation.")
            print("   Delete all data first if you want to regenerate.")
            return

        # Generate data
        sensors = create_sensors(db)
        generate_readings(db, sensors, days=7)

        print("\nData generation complete!")
        print(f"   - Sensors: {db.query(Sensor).count()}")
        print(f"   - Readings: {db.query(Reading).count():,}")
        print(f"   - Date range: Aug 10-16, 2026")

    except Exception as e:
        print(f"ERROR: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
