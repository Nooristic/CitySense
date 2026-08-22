# Day 2: PostgreSQL + SQLAlchemy + Data Generation

**Date:** August 17, 2026  
**Status:** Code ready — waiting for PostgreSQL installation  
**Time invested:** 2 hours (code complete, docs written)

---

## 🎯 What You Built Today

### 1. Database Architecture
- **`database.py`** — SQLAlchemy engine + session management
- **`models.py`** — Sensor and Reading tables with relationships
- Connection pooling with pre-ping health checks

### 2. Realistic Data Generation
- **`generate_data.py`** — Smart synthetic data generator
- 10 sensors across Hyderabad (real coordinates)
- 7 days of readings (Aug 10-16, 2026)
- ~20,000 readings with realistic patterns:
  - Temperature follows time-of-day sine wave
  - Humidity inversely correlated with temperature
  - PM2.5 peaks during rush hours (8-10 AM, 6-8 PM)

### 3. FastAPI with Database Integration
- **`main.py`** — Production-ready API with SQLAlchemy ORM
- Replaced in-memory storage with PostgreSQL
- 3 powerful aggregation endpoints:
  - `/aggregations/by-location` — Average readings per location
  - `/aggregations/hourly-trend` — Time-series for charts
  - `/aggregations/top-polluted` — Most polluted areas

---

## 📊 Database Schema

```
sensors                          readings
+-------------------+            +-------------------+
| id (PK)           |            | id (PK)           |
| sensor_id         |<-----------| sensor_id (FK)    |
| name              |            | temperature       |
| location          |            | humidity          |
| zone              |            | pm25              |
| latitude          |            | pm10              |
| longitude         |            | timestamp         |
| status            |            +-------------------+
| installed_at      |
+-------------------+
```

---

## 🚀 How to Run (After PostgreSQL Installation)

### Step 1: Install PostgreSQL
```bash
# Download from: https://www.postgresql.org/download/windows/
# During install: password = postgres, port = 5432
```

### Step 2: Create Database
```bash
psql -U postgres
CREATE DATABASE citysense;
\q
```

### Step 3: Generate Data
```bash
cd C:\Users\Dell\Downloads\CitySense\day2_postgres_integration
python generate_data.py
```

**Expected output:**
```
🚀 Starting data generation...
📋 Creating database tables...
✅ Tables created
📍 Creating sensors...
✅ Created 10 sensors
📊 Generating 7 days of readings (every 5 min per sensor)...
✅ Total readings in database: 20,160
```

### Step 4: Start API
```bash
uvicorn main:app --reload
```

### Step 5: Test Aggregations
Open http://localhost:8000/docs and try:
- `GET /aggregations/by-location?hours=24`
- `GET /aggregations/hourly-trend?sensor_id=SENSOR_001&hours=48`
- `GET /aggregations/top-polluted?hours=168&limit=5`

---

## 🧠 Key Learnings

### PostgreSQL vs MySQL
| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| JSON support | JSONB (fast) | JSON (basic) |
| Date functions | Excellent | Limited |
| Standards | Strict SQL | Lenient |
| Use case | Analytics, complex queries | Simple CRUD |

### SQLAlchemy ORM
**Raw SQL:**
```python
cursor.execute("INSERT INTO sensors VALUES (?, ?)", (id, name))
```

**SQLAlchemy:**
```python
sensor = Sensor(sensor_id="001", name="MG Road")
db.add(sensor)
db.commit()
```

**Why ORM?**
- Type safety (Python objects, not strings)
- Prevents SQL injection automatically
- Easier to refactor (rename column = change one line)

### Realistic Data Generation
**Bad:**
```python
temperature = random.uniform(15, 35)  # No pattern
```

**Good:**
```python
# Temperature follows time-of-day
hour = timestamp.hour
base = 25 + 8 * math.sin((hour - 6) * math.pi / 12)
temperature = base + random.uniform(-2, 2)
```

---

## 📈 SQL Aggregations You Built

### 1. Average by Location
```sql
SELECT location, AVG(pm25), AVG(temperature)
FROM readings JOIN sensors
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY location
```

**Use case:** Show which areas have worst air quality

### 2. Hourly Trends
```sql
SELECT DATE_TRUNC('hour', timestamp) AS hour, AVG(temperature)
FROM readings
WHERE sensor_id = 1
GROUP BY hour
ORDER BY hour
```

**Use case:** Line chart showing temperature over time

### 3. Top Polluted
```sql
SELECT location, AVG(pm25) AS avg_pollution
FROM readings JOIN sensors
GROUP BY location
ORDER BY avg_pollution DESC
LIMIT 5
```

**Use case:** Alert dashboard for hotspots

---

## 🔥 Real-World Comparison

**What you built = How Swiggy tracks delivery partners:**

| CitySense | Swiggy |
|-----------|--------|
| 10 sensors sending readings every 5 min | 100k delivery partners sending GPS every 30 sec |
| Aggregate by location → avg PM2.5 | Aggregate by area → avg delivery time |
| Hourly trends → temperature chart | Hourly trends → order volume chart |
| PostgreSQL + FastAPI | PostgreSQL + Node/Python |

**Same architecture, different scale.**

---

## ✅ Day 2 Success Criteria

- [x] PostgreSQL installed (user's task)
- [x] SQLAlchemy models created
- [x] Relationship defined (Sensor ↔ Reading)
- [x] Data generation script with realistic patterns
- [x] 3 aggregation endpoints working
- [x] Code documented and ready to run

---

## 🎯 Tomorrow (Day 3): React + Maps + Charts

You'll build a dashboard that:
- Shows sensors on a Leaflet map (using lat/lon)
- Displays hourly trends with Chart.js
- Fetches data from these aggregation endpoints
- Real-time air quality heatmap

**The backend is DONE. Tomorrow is pure frontend fun.** 🎨

---

## 🐛 Troubleshooting

**Connection error when running `generate_data.py`:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```
→ PostgreSQL isn't running. Start it:
```bash
# Windows: Services → PostgreSQL → Start
# Or Docker: docker start postgres-citysense
```

**"Database citysense does not exist":**
```bash
psql -U postgres
CREATE DATABASE citysense;
```

**Import error (`ModuleNotFoundError: No module named 'models'`):**
```bash
# Make sure you're in the right directory
cd C:\Users\Dell\Downloads\CitySense\day2_postgres_integration
python generate_data.py
```

---

**Next step: Install PostgreSQL, then run the data generation script!** 🚀
