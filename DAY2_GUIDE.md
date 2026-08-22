# Day 2: PostgreSQL + SQLAlchemy + Large Dataset Generation

**Goal:** Replace in-memory storage with PostgreSQL, generate 50k-100k sensor readings, build aggregation endpoints

**Time:** 6-8 hours

---

## 📚 What You'll Learn Today

1. **PostgreSQL Fundamentals**
   - How Postgres differs from MySQL
   - Connection strings and authentication
   - psql CLI basics

2. **SQLAlchemy ORM**
   - Declarative models (like Pydantic but for databases)
   - Sessions and transactions
   - Relationships (one-to-many)

3. **Data Generation at Scale**
   - Realistic time-series data with Faker
   - Batch inserts for performance
   - Timezone-aware timestamps

4. **SQL Aggregations**
   - GROUP BY with time bucketing
   - AVG, MIN, MAX, COUNT
   - Filtering with WHERE

---

## Part 1: Install PostgreSQL (30 minutes)

### Option 1: Official Installer (Recommended)

1. **Download PostgreSQL 16:**
   - Go to: https://www.postgresql.org/download/windows/
   - Click "Download the installer" (EDB installer)
   - Choose PostgreSQL 16.x for Windows x86-64

2. **Run the installer:**
   - ✅ Install PostgreSQL Server
   - ✅ Install pgAdmin 4 (GUI tool)
   - ✅ Install Command Line Tools
   - ❌ Skip Stack Builder (not needed)

3. **During installation:**
   - **Password:** Choose a simple password for development (e.g., `postgres`)
   - **Port:** Keep default `5432`
   - **Locale:** Default (English, United States)

4. **Verify installation:**
   ```bash
   # Add to PATH if not already (installer usually does this)
   # C:\Program Files\PostgreSQL\16\bin
   
   psql --version
   # Should show: psql (PostgreSQL) 16.x
   ```

### Option 2: Docker (If you already use Docker)

```bash
docker run --name postgres-citysense \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=citysense \
  -p 5432:5432 \
  -d postgres:16
```

---

## Part 2: Create Database (5 minutes)

### Method 1: Using psql (Command Line)

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql:
CREATE DATABASE citysense;
\c citysense  -- Connect to the database
\q            -- Quit psql
```

### Method 2: Using pgAdmin 4 (GUI)

1. Open pgAdmin 4
2. Right-click "Databases" → "Create" → "Database"
3. Name: `citysense`
4. Save

---

## Part 3: PostgreSQL vs MySQL - Key Differences

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| **Data Types** | JSON, JSONB, Arrays, UUID | JSON (basic), limited types |
| **Standards Compliance** | Strict SQL standards | More lenient |
| **Performance** | Better for complex queries | Better for simple reads |
| **Full-Text Search** | Built-in (tsvector) | Requires external engine |
| **Window Functions** | Excellent support | Limited (newer versions) |
| **Case Sensitivity** | Column names lowercased | Depends on OS |
| **Auto-Increment** | `SERIAL` or `IDENTITY` | `AUTO_INCREMENT` |

**Why Postgres for CitySense?**
- Time-series data (excellent date/time functions)
- JSON support for flexible sensor metadata
- Better aggregation performance
- Industry standard for analytics

---

## Part 4: Install Python Dependencies (5 minutes)

```bash
cd /c/Users/Dell/Downloads/CitySense

# Install database packages
pip install sqlalchemy psycopg2-binary alembic faker python-dotenv

# Update requirements.txt
pip freeze > day1_fastapi_basics/requirements.txt
```

**What each package does:**
- `sqlalchemy` - ORM (Object-Relational Mapper)
- `psycopg2-binary` - PostgreSQL driver for Python
- `alembic` - Database migration tool
- `faker` - Generate realistic fake data
- `python-dotenv` - Load environment variables from .env

---

## Part 5: Database Models with SQLAlchemy (1 hour)

### Understanding ORM

**Without ORM (raw SQL):**
```python
cursor.execute("INSERT INTO sensors (sensor_id, location) VALUES (%s, %s)", 
               ("SENSOR_001", "MG Road"))
```

**With ORM (SQLAlchemy):**
```python
sensor = Sensor(sensor_id="SENSOR_001", location="MG Road")
db.add(sensor)
db.commit()
```

### SQLAlchemy Models = Database Tables

**Pydantic (Day 1):** Validates incoming JSON data  
**SQLAlchemy (Day 2):** Maps Python classes to database tables

---

## Part 6: Generate Realistic Dataset (1.5 hours)

### What Makes Data "Realistic"?

**Bad synthetic data:**
```python
# Random values with no patterns
temperature = random.uniform(-50, 60)
```

**Good synthetic data:**
```python
# Temperature follows time of day
hour = timestamp.hour
base_temp = 20 + 10 * math.sin((hour - 6) * math.pi / 12)  # Peaks at 2 PM
temperature = base_temp + random.uniform(-3, 3)  # Add noise
```

### Dataset Requirements

- **50,000 - 100,000 readings** (aim for 75k)
- **7 days of data** (Aug 10-16, 2026)
- **10 sensors** across different locations
- **Readings every 5 minutes** per sensor
- **Realistic patterns:**
  - Temperature: 15-35°C, peaks around 2 PM
  - Humidity: 40-90%, inverse correlation with temperature
  - PM2.5: 10-150 µg/m³, worse in morning/evening (traffic)

---

## Part 7: Aggregation Endpoints (1.5 hours)

### SQL Aggregations You'll Build

1. **Average by location:**
   ```sql
   SELECT location, AVG(temperature), AVG(humidity), AVG(pm25)
   FROM readings JOIN sensors ON readings.sensor_id = sensors.id
   GROUP BY location
   ```

2. **Hourly trends:**
   ```sql
   SELECT DATE_TRUNC('hour', timestamp) AS hour, 
          AVG(temperature) AS avg_temp
   FROM readings
   WHERE timestamp >= NOW() - INTERVAL '24 hours'
   GROUP BY hour
   ORDER BY hour
   ```

3. **Top polluted locations:**
   ```sql
   SELECT location, AVG(pm25) AS avg_pollution
   FROM readings JOIN sensors
   GROUP BY location
   ORDER BY avg_pollution DESC
   LIMIT 5
   ```

---

## 🎯 Success Criteria for Day 2

By end of today, you should have:

- ✅ PostgreSQL installed and running
- ✅ `citysense` database created
- ✅ SQLAlchemy models for Sensor and Reading tables
- ✅ 75,000+ realistic sensor readings in database
- ✅ At least 3 aggregation endpoints working
- ✅ Code pushed to GitHub with good commits

---

## 📊 How Your Data Will Look

**Sensors table (10 rows):**
```
| id | sensor_id   | location        | zone   | latitude  | longitude |
|----|-------------|-----------------|--------|-----------|-----------|
| 1  | SENSOR_001  | MG Road         | Zone A | 12.9716   | 77.5946   |
| 2  | SENSOR_002  | Gachibowli      | Zone B | 17.4435   | 78.3772   |
```

**Readings table (75,000 rows):**
```
| id | sensor_id | temperature | humidity | pm25  | timestamp           |
|----|-----------|-------------|----------|-------|---------------------|
| 1  | 1         | 24.5        | 65.2     | 42.1  | 2026-08-10 00:00:00 |
| 2  | 1         | 23.8        | 67.5     | 38.5  | 2026-08-10 00:05:00 |
```

---

## 🔥 Real-World Context: Why This Matters

**Swiggy's backend does exactly this:**
- Delivery partners send GPS + status every 30 seconds
- Data stored in PostgreSQL (or similar)
- Aggregated for "Average delivery time by area"
- Time-series data for "Peak order hours"

**You're building the same architecture at smaller scale.**

---

## Next Steps

Once you've installed PostgreSQL, I'll help you:
1. Create the SQLAlchemy models
2. Write the data generation script
3. Build aggregation endpoints
4. Test everything with real queries

**Install PostgreSQL now using the steps above, then tell me when you're ready!** 🚀
