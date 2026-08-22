# SQL Aggregations Quick Reference

**Context:** How to analyze data with GROUP BY, AVG, COUNT, etc.

---

## 🎯 What Are Aggregations?

**Aggregations = Combining many rows into summary statistics**

```sql
-- Instead of 20,000 individual readings...
SELECT * FROM readings;  -- Too much data!

-- Get summary statistics
SELECT AVG(temperature), MAX(pm25), COUNT(*)
FROM readings;
-- Result: 1 row with 3 numbers
```

---

## 📊 Basic Aggregation Functions

### 1. COUNT (How Many?)
```sql
-- Total readings
SELECT COUNT(*) FROM readings;
-- Result: 20160

-- Non-null values only
SELECT COUNT(pm10) FROM readings;
-- Result: 19500 (some NULL values)

-- Unique values
SELECT COUNT(DISTINCT sensor_id) FROM readings;
-- Result: 10 (10 unique sensors)
```

### 2. SUM (Add Them Up)
```sql
-- Total of all temperatures
SELECT SUM(temperature) FROM readings;

-- Total PM2.5 across all sensors
SELECT SUM(pm25) FROM readings;
```

### 3. AVG (Average)
```sql
-- Average temperature
SELECT AVG(temperature) FROM readings;
-- Result: 25.34

-- Round to 2 decimals
SELECT ROUND(AVG(temperature), 2) FROM readings;
-- Result: 25.34
```

### 4. MIN / MAX (Smallest / Largest)
```sql
-- Coldest temperature recorded
SELECT MIN(temperature) FROM readings;

-- Worst pollution level
SELECT MAX(pm25) FROM readings;

-- Both at once
SELECT 
    MIN(temperature) AS coldest,
    MAX(temperature) AS hottest,
    AVG(temperature) AS average
FROM readings;
```

---

## 🔍 GROUP BY (Breakdown by Category)

**The power of GROUP BY: "Show me the average per location/sensor/zone"**

### Basic GROUP BY
```sql
-- Average temperature PER SENSOR
SELECT 
    sensor_id,
    AVG(temperature) AS avg_temp
FROM readings
GROUP BY sensor_id;

-- Result:
-- sensor_id | avg_temp
-- ----------+---------
--         1 |    25.34
--         2 |    26.12
--         3 |    24.89
```

### GROUP BY with Multiple Columns
```sql
-- Average readings per sensor AND zone
SELECT 
    s.zone,
    s.sensor_id,
    AVG(r.temperature) AS avg_temp,
    COUNT(r.id) AS reading_count
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.zone, s.sensor_id
ORDER BY s.zone, avg_temp DESC;
```

### COUNT per Group
```sql
-- How many readings per sensor?
SELECT 
    sensor_id,
    COUNT(*) AS reading_count
FROM readings
GROUP BY sensor_id;

-- Which sensors have the most data?
SELECT 
    sensor_id,
    COUNT(*) AS reading_count
FROM readings
GROUP BY sensor_id
ORDER BY reading_count DESC
LIMIT 5;
```

---

## 🕐 Time-Based Aggregations

### PostgreSQL DATE_TRUNC (Time Bucketing)
```sql
-- Average temperature per HOUR
SELECT 
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(temperature) AS avg_temp
FROM readings
GROUP BY hour
ORDER BY hour;

-- Result:
-- hour                | avg_temp
-- --------------------+---------
-- 2026-08-10 00:00:00 |    22.34
-- 2026-08-10 01:00:00 |    21.89
-- 2026-08-10 02:00:00 |    21.45
```

### Available DATE_TRUNC Units
```sql
DATE_TRUNC('second', timestamp)   -- Round to second
DATE_TRUNC('minute', timestamp)   -- Round to minute
DATE_TRUNC('hour', timestamp)     -- Round to hour
DATE_TRUNC('day', timestamp)      -- Round to day (midnight)
DATE_TRUNC('week', timestamp)     -- Round to week (Monday)
DATE_TRUNC('month', timestamp)    -- Round to month (1st)
DATE_TRUNC('year', timestamp)     -- Round to year (Jan 1)
```

### Daily Aggregations
```sql
-- Average readings per DAY
SELECT 
    DATE_TRUNC('day', timestamp) AS day,
    AVG(temperature) AS avg_temp,
    AVG(humidity) AS avg_humidity,
    AVG(pm25) AS avg_pm25
FROM readings
GROUP BY day
ORDER BY day;
```

### Hourly Trends (Last 24 Hours)
```sql
-- Temperature trend for last 24 hours
SELECT 
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(temperature) AS avg_temp
FROM readings
WHERE timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY hour
ORDER BY hour;
```

---

## 🔗 Aggregations with JOINs

### JOIN + GROUP BY Pattern
```sql
-- Average readings per LOCATION (not sensor ID)
SELECT 
    s.location,
    s.zone,
    AVG(r.temperature) AS avg_temp,
    AVG(r.humidity) AS avg_humidity,
    AVG(r.pm25) AS avg_pm25,
    COUNT(r.id) AS reading_count
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.location, s.zone;
```

### Finding Top/Bottom N
```sql
-- Top 5 most polluted locations
SELECT 
    s.location,
    AVG(r.pm25) AS avg_pm25
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.location
ORDER BY avg_pm25 DESC
LIMIT 5;

-- 5 cleanest locations
SELECT 
    s.location,
    AVG(r.pm25) AS avg_pm25
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.location
ORDER BY avg_pm25 ASC
LIMIT 5;
```

---

## 🎯 HAVING (Filter After Grouping)

**WHERE filters rows BEFORE grouping, HAVING filters AFTER grouping**

```sql
-- Sensors with average PM2.5 > 50
SELECT 
    sensor_id,
    AVG(pm25) AS avg_pm25
FROM readings
GROUP BY sensor_id
HAVING AVG(pm25) > 50;

-- Sensors with at least 1000 readings
SELECT 
    sensor_id,
    COUNT(*) AS reading_count
FROM readings
GROUP BY sensor_id
HAVING COUNT(*) >= 1000;

-- Locations with high pollution (avg > 50) AND lots of data (count > 500)
SELECT 
    s.location,
    AVG(r.pm25) AS avg_pm25,
    COUNT(r.id) AS reading_count
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.location
HAVING AVG(r.pm25) > 50 AND COUNT(r.id) > 500;
```

---

## 📈 Advanced Patterns

### Multiple Aggregations
```sql
-- Full statistics per location
SELECT 
    s.location,
    COUNT(r.id) AS readings,
    MIN(r.temperature) AS min_temp,
    MAX(r.temperature) AS max_temp,
    AVG(r.temperature) AS avg_temp,
    STDDEV(r.temperature) AS std_temp,  -- Standard deviation
    MIN(r.pm25) AS min_pollution,
    MAX(r.pm25) AS max_pollution,
    AVG(r.pm25) AS avg_pollution
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.location
ORDER BY avg_pollution DESC;
```

### Conditional Aggregations
```sql
-- Count readings by status
SELECT 
    sensor_id,
    COUNT(*) AS total_readings,
    COUNT(*) FILTER (WHERE pm25 > 50) AS high_pollution_count,
    COUNT(*) FILTER (WHERE pm25 <= 50) AS normal_count
FROM readings
GROUP BY sensor_id;

-- Percentage of high pollution readings
SELECT 
    sensor_id,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE pm25 > 50) AS high_pollution,
    ROUND(100.0 * COUNT(*) FILTER (WHERE pm25 > 50) / COUNT(*), 2) AS high_pollution_pct
FROM readings
GROUP BY sensor_id;
```

### Time Ranges
```sql
-- Average per location, last 24 hours vs last 7 days
SELECT 
    s.location,
    AVG(r.pm25) FILTER (WHERE r.timestamp >= NOW() - INTERVAL '24 hours') AS pm25_24h,
    AVG(r.pm25) FILTER (WHERE r.timestamp >= NOW() - INTERVAL '7 days') AS pm25_7d
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
GROUP BY s.location;
```

---

## 🪟 Window Functions (Advanced)

**Window functions = Aggregations WITHOUT collapsing rows**

### ROW_NUMBER (Ranking)
```sql
-- Rank locations by average pollution
SELECT 
    location,
    avg_pm25,
    ROW_NUMBER() OVER (ORDER BY avg_pm25 DESC) AS rank
FROM (
    SELECT 
        s.location,
        AVG(r.pm25) AS avg_pm25
    FROM sensors s
    JOIN readings r ON s.id = r.sensor_id
    GROUP BY s.location
) subquery;
```

### RANK vs DENSE_RANK
```sql
-- RANK: 1, 2, 2, 4 (skips 3 if tie)
-- DENSE_RANK: 1, 2, 2, 3 (no skip)

SELECT 
    location,
    avg_pm25,
    RANK() OVER (ORDER BY avg_pm25 DESC) AS rank,
    DENSE_RANK() OVER (ORDER BY avg_pm25 DESC) AS dense_rank
FROM location_stats;
```

### LAG / LEAD (Previous/Next Value)
```sql
-- Compare each hour to previous hour
SELECT 
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(temperature) AS avg_temp,
    LAG(AVG(temperature)) OVER (ORDER BY DATE_TRUNC('hour', timestamp)) AS prev_hour_temp,
    AVG(temperature) - LAG(AVG(temperature)) OVER (ORDER BY DATE_TRUNC('hour', timestamp)) AS temp_change
FROM readings
GROUP BY hour
ORDER BY hour;
```

### Moving Average
```sql
-- 3-hour moving average
SELECT 
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(temperature) AS current_temp,
    AVG(AVG(temperature)) OVER (
        ORDER BY DATE_TRUNC('hour', timestamp)
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3h
FROM readings
GROUP BY hour
ORDER BY hour;
```

---

## 🔥 SQLAlchemy Equivalents

### Basic Aggregation
```python
from sqlalchemy import func

# SQL: SELECT AVG(temperature) FROM readings
avg_temp = db.query(func.avg(Reading.temperature)).scalar()

# SQL: SELECT COUNT(*) FROM readings
count = db.query(func.count(Reading.id)).scalar()
```

### GROUP BY
```python
# SQL: SELECT sensor_id, AVG(temperature) FROM readings GROUP BY sensor_id
results = db.query(
    Reading.sensor_id,
    func.avg(Reading.temperature).label('avg_temp')
).group_by(Reading.sensor_id).all()

for r in results:
    print(f"Sensor {r.sensor_id}: {r.avg_temp:.2f}°C")
```

### DATE_TRUNC
```python
# Hourly averages
results = db.query(
    func.date_trunc('hour', Reading.timestamp).label('hour'),
    func.avg(Reading.temperature).label('avg_temp')
).group_by('hour').order_by('hour').all()
```

### JOIN + GROUP BY
```python
results = db.query(
    Sensor.location,
    func.avg(Reading.pm25).label('avg_pm25'),
    func.count(Reading.id).label('count')
).join(Reading).group_by(Sensor.location).all()
```

---

## 📊 Common Use Cases

### 1. Dashboard Summary
```sql
-- Overall stats for dashboard
SELECT 
    COUNT(DISTINCT s.id) AS total_sensors,
    COUNT(r.id) AS total_readings,
    AVG(r.temperature) AS avg_temp,
    AVG(r.humidity) AS avg_humidity,
    AVG(r.pm25) AS avg_pm25,
    MAX(r.timestamp) AS last_updated
FROM sensors s
LEFT JOIN readings r ON s.id = r.sensor_id;
```

### 2. Heatmap Data
```sql
-- Pollution by location (for map visualization)
SELECT 
    s.location,
    s.latitude,
    s.longitude,
    AVG(r.pm25) AS avg_pm25
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
WHERE r.timestamp >= NOW() - INTERVAL '24 hours'
GROUP BY s.location, s.latitude, s.longitude;
```

### 3. Time-Series Chart
```sql
-- Hourly temperature for Chart.js
SELECT 
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(temperature) AS avg_temp
FROM readings
WHERE sensor_id = 1 
  AND timestamp >= NOW() - INTERVAL '48 hours'
GROUP BY hour
ORDER BY hour;
```

### 4. Alerts (High Pollution)
```sql
-- Locations with avg PM2.5 > 75 in last hour
SELECT 
    s.location,
    AVG(r.pm25) AS avg_pm25
FROM sensors s
JOIN readings r ON s.id = r.sensor_id
WHERE r.timestamp >= NOW() - INTERVAL '1 hour'
GROUP BY s.location
HAVING AVG(r.pm25) > 75;
```

---

## 🐛 Common Mistakes

### ❌ Selecting non-grouped columns
```sql
-- ERROR: location not in GROUP BY
SELECT sensor_id, location, AVG(temperature)
FROM readings
GROUP BY sensor_id;

-- FIX: Add to GROUP BY
SELECT sensor_id, location, AVG(temperature)
FROM readings
GROUP BY sensor_id, location;
```

### ❌ WHERE on aggregation
```sql
-- ERROR: Can't use WHERE on AVG
SELECT sensor_id, AVG(pm25)
FROM readings
WHERE AVG(pm25) > 50  -- WRONG
GROUP BY sensor_id;

-- FIX: Use HAVING
SELECT sensor_id, AVG(pm25)
FROM readings
GROUP BY sensor_id
HAVING AVG(pm25) > 50;  -- CORRECT
```

---

## 📚 Learn More

- **PostgreSQL Aggregations:** https://www.postgresql.org/docs/current/functions-aggregate.html
- **GROUP BY tutorial:** https://www.postgresqltutorial.com/postgresql-aggregate-functions/postgresql-group-by/
- **Window Functions:** https://www.postgresqltutorial.com/postgresql-window-function/

**Practice with your Day 2 database — try these queries yourself!**
