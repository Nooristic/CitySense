# 🚀 Day 2 - Complete Setup Instructions

**Date:** August 17, 2026  
**Status:** Code is 100% ready — just needs PostgreSQL installed

---

## ✅ What's Already Done

All Day 2 code is written and waiting for you:

```
day2_postgres_integration/
├── database.py          ✅ SQLAlchemy engine + session
├── models.py            ✅ Sensor & Reading ORM models
├── generate_data.py     ✅ Smart data generator (20k rows)
├── main.py              ✅ FastAPI with 3 aggregation endpoints
├── requirements.txt     ✅ All dependencies
├── .env                 ✅ Database config
└── README.md            ✅ Complete documentation
```

**Python packages installed:**
- ✅ sqlalchemy 2.0.52
- ✅ psycopg2-binary 2.9.12
- ✅ alembic 1.19.1
- ✅ faker 40.36.0

---

## 🎯 What You Need to Do (30 minutes)

### Step 1: Install PostgreSQL (15 minutes)

**Download & Install:**
1. Go to: https://www.postgresql.org/download/windows/
2. Click "Download the installer"
3. Get PostgreSQL 16.x (latest stable)

**During installation:**
- ✅ Install PostgreSQL Server
- ✅ Install Command Line Tools
- ✅ Install pgAdmin 4 (optional GUI)
- Password: `postgres` (simple for development)
- Port: `5432` (default)

**Verify installation:**
```bash
psql --version
# Should output: psql (PostgreSQL) 16.x
```

---

### Step 2: Create Database (2 minutes)

**Option A: Command line (faster)**
```bash
psql -U postgres
# Enter password: postgres

CREATE DATABASE citysense;
\l  # List databases — you should see "citysense"
\q  # Quit
```

**Option B: pgAdmin 4 GUI**
1. Open pgAdmin 4
2. Right-click "Databases" → "Create" → "Database"
3. Name: `citysense`
4. Save

---

### Step 3: Generate Data (5 minutes)

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
  ✓ Inserted 5000 readings...
  ✓ Inserted 5000 readings...
  ✓ Inserted 5000 readings...
  ✓ Inserted 5000 readings...
  ✓ Inserted 160 readings
✅ Total readings in database: 20,160

🎉 Data generation complete!
   - Sensors: 10
   - Readings: 20,160
   - Date range: Aug 10-16, 2026
```

---

### Step 4: Start the API (2 minutes)

```bash
uvicorn main:app --reload
```

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

### Step 5: Test Aggregations (5 minutes)

Open http://localhost:8000/docs

**Try these endpoints:**

1. **Average by location** (last 24 hours)
   ```
   GET /aggregations/by-location?hours=24
   ```
   **Returns:** Average temp/humidity/PM2.5 for each location

2. **Hourly trend** (specific sensor)
   ```
   GET /aggregations/hourly-trend?sensor_id=SENSOR_001&hours=48
   ```
   **Returns:** Hourly averages for line chart

3. **Top polluted locations**
   ```
   GET /aggregations/top-polluted?hours=168&limit=5
   ```
   **Returns:** Worst 5 locations by PM2.5

---

## 🧪 Quick Test Queries

Once the API is running, test in your browser or Postman:

**1. Get all sensors:**
```
http://localhost:8000/sensors
```

**2. Get readings for one sensor:**
```
http://localhost:8000/readings?sensor_id=SENSOR_001&hours=24&limit=50
```

**3. Get location averages:**
```
http://localhost:8000/aggregations/by-location?hours=168
```

---

## 🐛 Troubleshooting

### Error: "could not connect to server"
**Problem:** PostgreSQL isn't running

**Fix:**
```bash
# Check if running
psql -U postgres

# If error, start PostgreSQL:
# Windows → Services → PostgreSQL → Start
# Or Docker: docker start postgres-citysense
```

---

### Error: "database citysense does not exist"
**Problem:** Database wasn't created

**Fix:**
```bash
psql -U postgres
CREATE DATABASE citysense;
\q
```

---

### Error: "ModuleNotFoundError: No module named 'models'"
**Problem:** Running from wrong directory

**Fix:**
```bash
cd C:\Users\Dell\Downloads\CitySense\day2_postgres_integration
python generate_data.py
```

---

### Error: "Sensor ID already exists" when running generate_data.py
**Problem:** Data already generated

**Fix:**
```bash
# Connect to database
psql -U postgres -d citysense

# Delete all data
DELETE FROM readings;
DELETE FROM sensors;
\q

# Re-run generator
python generate_data.py
```

---

## 📊 What the Data Looks Like

**Sensors table (10 rows):**
```
 id | sensor_id   | location        | zone   | latitude | longitude
----+-------------+-----------------+--------+----------+-----------
  1 | SENSOR_001  | MG Road         | Zone A | 12.9716  | 77.5946
  2 | SENSOR_002  | Gachibowli      | Zone B | 17.4435  | 78.3772
  3 | SENSOR_003  | Banjara Hills   | Zone A | 17.4239  | 78.4738
```

**Readings table (~20,160 rows):**
```
 id | sensor_id | temperature | humidity | pm25  | timestamp
----+-----------+-------------+----------+-------+---------------------
  1 |         1 |       22.34 |    72.15 | 28.45 | 2026-08-10 00:00:00
  2 |         1 |       21.89 |    73.82 | 26.12 | 2026-08-10 00:05:00
  3 |         1 |       21.56 |    74.56 | 24.88 | 2026-08-10 00:10:00
```

---

## 🎓 What You Learned Today

1. **PostgreSQL installation & setup**
2. **SQLAlchemy ORM** (models, sessions, relationships)
3. **Realistic data generation** (time-series patterns)
4. **SQL aggregations** (AVG, GROUP BY, DATE_TRUNC)
5. **FastAPI + database integration**

---

## 🎯 Day 2 Complete Checklist

- [ ] PostgreSQL installed (`psql --version` works)
- [ ] Database `citysense` created
- [ ] `generate_data.py` ran successfully (20,160 readings)
- [ ] API running (`uvicorn main:app --reload`)
- [ ] Tested at least 2 aggregation endpoints in `/docs`
- [ ] Read `POSTGRES_VS_MYSQL.md` (understand why Postgres)

**Once all checked, push to GitHub and you're done!**

---

## 🚀 Git Commit Commands

```bash
cd C:\Users\Dell\Downloads\CitySense
git add day2_postgres_integration/
git add DAY2_GUIDE.md POSTGRES_VS_MYSQL.md PROGRESS_TRACKER.md
git commit -m "Add PostgreSQL integration with SQLAlchemy ORM

- Database models for sensors and readings
- Realistic data generator (20k+ rows with time-series patterns)
- 3 aggregation endpoints (by-location, hourly-trend, top-polluted)
- Complete documentation and setup guide

Co-Authored-By: Claude <noreply@anthropic.com>"

git push origin main
```

---

## 🎯 Tomorrow: React Dashboard

Day 3 will be pure frontend:
- Leaflet map showing sensors (using lat/lon from database)
- Chart.js line chart (hourly trends from aggregation endpoint)
- Real-time air quality dashboard
- Fetch data from the endpoints you just built

**Backend is DONE. Tomorrow is design + visualization.** 🎨

---

## 💡 Pro Tips

**Want to see the data in the database?**
```bash
psql -U postgres -d citysense

# List all sensors
SELECT sensor_id, location, zone FROM sensors;

# Count readings per sensor
SELECT s.sensor_id, COUNT(r.id) as reading_count
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.sensor_id;

# Exit
\q
```

**Want to test aggregations in SQL directly?**
```sql
-- Average PM2.5 by location (last 24 hours)
SELECT 
    s.location,
    AVG(r.pm25) as avg_pm25,
    COUNT(r.id) as reading_count
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
WHERE r.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY s.location
ORDER BY avg_pm25 DESC;
```

---

**Ready? Install PostgreSQL and run the setup!** 🚀
