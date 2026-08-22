# SQLAlchemy ORM Quick Reference

**Context:** After building Day 2, use this for quick lookups

---

## 🏗️ Basic Setup

### 1. Database Connection (`database.py`)
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Connection string format:
# postgresql+psycopg2://user:password@host:port/database
DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/citysense"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass
```

---

## 📋 Defining Models (Tables)

### Basic Model
```python
from sqlalchemy import Column, Integer, String, Float, DateTime
from database import Base

class Sensor(Base):
    __tablename__ = "sensors"  # Table name in database
    
    # Columns
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(String(50), unique=True, nullable=False)
    location = Column(String(100), nullable=False)
    latitude = Column(Float)
    
    def __repr__(self):
        return f"<Sensor {self.sensor_id}>"
```

### Common Column Types
```python
Column(Integer)                    # 1, 2, 3
Column(String(50))                 # "text" (max 50 chars)
Column(Text)                       # Unlimited text
Column(Float)                      # 3.14
Column(Boolean)                    # True/False
Column(DateTime)                   # datetime object
Column(DateTime(timezone=True))    # Timezone-aware
Column(JSON)                       # JSON data
```

### Column Constraints
```python
Column(Integer, primary_key=True)           # Primary key
Column(String(50), unique=True)             # Must be unique
Column(String(100), nullable=False)         # Cannot be NULL
Column(String(20), default="active")        # Default value
Column(Integer, index=True)                 # Add index for speed
Column(DateTime, server_default=func.now()) # DB generates default
```

---

## 🔗 Relationships (One-to-Many)

### Parent Model (One)
```python
class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(String(50))
    
    # Relationship: one sensor → many readings
    readings = relationship("Reading", back_populates="sensor")
```

### Child Model (Many)
```python
class Reading(Base):
    __tablename__ = "readings"
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"))  # Links to sensors.id
    temperature = Column(Float)
    
    # Relationship: many readings → one sensor
    sensor = relationship("Sensor", back_populates="readings")
```

### Using Relationships in Queries
```python
# Get a sensor and access its readings
sensor = db.query(Sensor).filter(Sensor.sensor_id == "SENSOR_001").first()
print(sensor.readings)  # List of all Reading objects for this sensor

# Get a reading and access its sensor
reading = db.query(Reading).first()
print(reading.sensor.location)  # "MG Road"
```

---

## 📊 CRUD Operations

### Creating a Session
```python
from database import SessionLocal

db = SessionLocal()  # Create session
try:
    # Your database operations here
    db.commit()
finally:
    db.close()
```

### 1. CREATE (Insert)
```python
# Single insert
sensor = Sensor(
    sensor_id="SENSOR_011",
    location="Kukatpally",
    latitude=17.4948,
    longitude=78.3975
)
db.add(sensor)
db.commit()
db.refresh(sensor)  # Get the auto-generated ID

# Bulk insert
sensors = [
    Sensor(sensor_id="S001", location="Area 1"),
    Sensor(sensor_id="S002", location="Area 2"),
]
db.add_all(sensors)
db.commit()
```

### 2. READ (Query)
```python
# Get all
sensors = db.query(Sensor).all()

# Get one (returns None if not found)
sensor = db.query(Sensor).filter(Sensor.sensor_id == "SENSOR_001").first()

# Get by primary key
sensor = db.query(Sensor).get(1)  # Get sensor with id=1

# Count
count = db.query(Sensor).count()

# Filter with multiple conditions
results = db.query(Sensor).filter(
    Sensor.zone == "Zone A",
    Sensor.status == "active"
).all()

# Filter with OR
from sqlalchemy import or_
results = db.query(Sensor).filter(
    or_(Sensor.zone == "Zone A", Sensor.zone == "Zone B")
).all()

# Order by
sensors = db.query(Sensor).order_by(Sensor.location).all()
sensors = db.query(Sensor).order_by(desc(Sensor.id)).all()  # Descending

# Limit and offset (pagination)
sensors = db.query(Sensor).limit(10).offset(20).all()

# Like (partial match)
sensors = db.query(Sensor).filter(Sensor.location.like("%Road%")).all()
```

### 3. UPDATE
```python
# Update single object
sensor = db.query(Sensor).filter(Sensor.sensor_id == "SENSOR_001").first()
sensor.status = "maintenance"
db.commit()

# Bulk update
db.query(Sensor).filter(Sensor.zone == "Zone A").update({"status": "active"})
db.commit()
```

### 4. DELETE
```python
# Delete single object
sensor = db.query(Sensor).filter(Sensor.sensor_id == "SENSOR_001").first()
db.delete(sensor)
db.commit()

# Bulk delete
db.query(Sensor).filter(Sensor.status == "offline").delete()
db.commit()
```

---

## 🔍 Aggregations & Joins

### Joins
```python
from sqlalchemy import func

# Inner join (only matching rows)
results = db.query(Sensor, Reading).join(Reading).all()

# Get specific columns from join
results = db.query(
    Sensor.location,
    Reading.temperature
).join(Reading).all()
```

### Aggregations
```python
from sqlalchemy import func

# Count
count = db.query(func.count(Sensor.id)).scalar()

# Average
avg_temp = db.query(func.avg(Reading.temperature)).scalar()

# Min, Max, Sum
min_temp = db.query(func.min(Reading.temperature)).scalar()
max_pm25 = db.query(func.max(Reading.pm25)).scalar()
total = db.query(func.sum(Reading.pm25)).scalar()

# Group by
results = db.query(
    Sensor.location,
    func.avg(Reading.temperature).label("avg_temp"),
    func.count(Reading.id).label("count")
).join(Reading).group_by(Sensor.location).all()

for r in results:
    print(f"{r.location}: {r.avg_temp:.2f}°C ({r.count} readings)")
```

### Time-based Queries (PostgreSQL)
```python
from datetime import datetime, timedelta

# Last 24 hours
cutoff = datetime.now() - timedelta(hours=24)
readings = db.query(Reading).filter(Reading.timestamp >= cutoff).all()

# Date truncation (hourly buckets)
results = db.query(
    func.date_trunc('hour', Reading.timestamp).label('hour'),
    func.avg(Reading.temperature).label('avg_temp')
).group_by('hour').order_by('hour').all()
```

---

## 🎯 Common Patterns in FastAPI

### Dependency Injection (Get DB Session)
```python
from database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# In FastAPI endpoint
@app.get("/sensors")
def get_sensors(db: Session = Depends(get_db)):
    sensors = db.query(Sensor).all()
    return sensors
```

### Pydantic Response Models
```python
from pydantic import BaseModel

class SensorResponse(BaseModel):
    id: int
    sensor_id: str
    location: str
    
    class Config:
        from_attributes = True  # Allow SQLAlchemy model → Pydantic

# In endpoint
@app.get("/sensors/{id}", response_model=SensorResponse)
def get_sensor(id: int, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == id).first()
    if not sensor:
        raise HTTPException(status_code=404)
    return sensor  # Automatically converts to Pydantic model
```

---

## 🔥 Performance Tips

### 1. Eager Loading (Avoid N+1 Queries)
```python
from sqlalchemy.orm import joinedload

# Bad (N+1 queries - slow!)
sensors = db.query(Sensor).all()
for sensor in sensors:
    print(sensor.readings)  # Queries database again for each sensor

# Good (1 query - fast!)
sensors = db.query(Sensor).options(joinedload(Sensor.readings)).all()
for sensor in sensors:
    print(sensor.readings)  # Already loaded
```

### 2. Batch Inserts
```python
# Bad (slow)
for i in range(10000):
    reading = Reading(temperature=25.0)
    db.add(reading)
    db.commit()  # 10,000 commits!

# Good (fast)
readings = []
for i in range(10000):
    readings.append(Reading(temperature=25.0))
    if len(readings) >= 1000:
        db.add_all(readings)
        db.commit()
        readings = []
```

### 3. Indexes
```python
class Reading(Base):
    __tablename__ = "readings"
    
    sensor_id = Column(Integer, ForeignKey("sensors.id"), index=True)
    timestamp = Column(DateTime, index=True)
    
    # Composite index (for queries using both columns)
    __table_args__ = (
        Index('ix_sensor_time', 'sensor_id', 'timestamp'),
    )
```

---

## 🐛 Common Errors & Fixes

### "DetachedInstanceError"
**Problem:** Trying to access a relationship after closing the session

```python
# Bad
sensor = db.query(Sensor).first()
db.close()
print(sensor.readings)  # ERROR!

# Good
sensor = db.query(Sensor).options(joinedload(Sensor.readings)).first()
db.close()
print(sensor.readings)  # Works!
```

### "IntegrityError: duplicate key"
**Problem:** Inserting a value that violates unique constraint

```python
# Check if exists first
existing = db.query(Sensor).filter(Sensor.sensor_id == "SENSOR_001").first()
if existing:
    raise HTTPException(status_code=400, detail="Already exists")
```

### "PendingRollbackError"
**Problem:** Previous operation failed, session needs rollback

```python
try:
    db.add(sensor)
    db.commit()
except Exception as e:
    db.rollback()  # Reset session
    raise
```

---

## 📚 Cheatsheet Summary

| Operation | Code |
|-----------|------|
| Get all | `db.query(Model).all()` |
| Get one | `db.query(Model).filter(Model.col == val).first()` |
| Get by ID | `db.query(Model).get(id)` |
| Insert | `db.add(obj); db.commit()` |
| Update | `obj.field = new_val; db.commit()` |
| Delete | `db.delete(obj); db.commit()` |
| Count | `db.query(func.count(Model.id)).scalar()` |
| Average | `db.query(func.avg(Model.col)).scalar()` |
| Join | `db.query(M1, M2).join(M2).all()` |
| Group by | `.group_by(Model.col)` |
| Order by | `.order_by(Model.col)` |
| Limit | `.limit(10)` |

---

## 🎯 Next Steps

1. **Read the official tutorial:** https://docs.sqlalchemy.org/en/20/tutorial/
2. **Experiment with queries** in your Day 2 project
3. **Add a new table** (practice relationships)

**Your Day 2 code is a perfect reference — study it while reading docs!**
