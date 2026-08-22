# PostgreSQL vs MySQL - Quick Reference

**Context:** Why CitySense uses PostgreSQL instead of MySQL

---

## Key Differences

| Feature | PostgreSQL | MySQL |
|---------|-----------|-------|
| **Data Types** | Rich (JSON, Arrays, UUID, custom types) | Basic types only |
| **JSON Support** | JSONB (binary, indexed, fast queries) | JSON (text-based, slower) |
| **Date/Time Functions** | Excellent (DATE_TRUNC, intervals, timezones) | Limited |
| **Full-Text Search** | Built-in (tsvector, tsquery) | Requires external engine |
| **Window Functions** | Full support | Limited (newer versions only) |
| **Standards Compliance** | Strict SQL standard | More lenient |
| **Performance** | Complex queries, analytics | Simple reads, writes |
| **Auto-Increment** | SERIAL, IDENTITY | AUTO_INCREMENT |
| **Case Sensitivity** | Column names lowercased | OS-dependent |
| **Community** | Open-source, BSD license | Oracle-owned, GPL |

---

## Why Postgres for CitySense?

### 1. Time-Series Data Excellence
```sql
-- PostgreSQL has DATE_TRUNC for hourly/daily bucketing
SELECT DATE_TRUNC('hour', timestamp) AS hour, AVG(temperature)
FROM readings
GROUP BY hour;

-- MySQL equivalent is messy
SELECT DATE_FORMAT(timestamp, '%Y-%m-%d %H:00:00') AS hour, AVG(temperature)
FROM readings
GROUP BY hour;
```

### 2. JSON Support for Flexible Metadata
```sql
-- Store sensor config as JSON in Postgres
CREATE TABLE sensors (
    id SERIAL PRIMARY KEY,
    sensor_id VARCHAR(50),
    config JSONB  -- Fast indexed queries on nested JSON!
);

-- Query JSON fields
SELECT * FROM sensors WHERE config->>'calibration_date' > '2026-01-01';
```

### 3. Better Aggregation Performance
- Postgres optimizes GROUP BY + JOIN better
- Window functions (RANK, LAG, LEAD) for analytics
- Parallel query execution

### 4. Geographic Data (Bonus)
```sql
-- PostGIS extension for real maps
-- Find sensors within 5km of a point
SELECT * FROM sensors
WHERE ST_DWithin(
    ST_MakePoint(longitude, latitude)::geography,
    ST_MakePoint(78.4744, 17.3850)::geography,
    5000
);
```

---

## When to Use MySQL Instead

✅ **Use MySQL if:**
- Simple CRUD operations (blogs, e-commerce)
- Need MySQL-specific features (e.g., WordPress requires it)
- Team already knows MySQL
- Read-heavy workload with simple queries

❌ **Avoid MySQL for:**
- Complex analytics (GROUP BY, JOINs, aggregations)
- Time-series data
- JSON-heavy applications
- Geographic data

---

## Real-World Examples

| Company | Database | Why |
|---------|----------|-----|
| **Instagram** | PostgreSQL | User feeds, time-series data |
| **Reddit** | PostgreSQL | Comments, votes, complex queries |
| **Swiggy** | PostgreSQL | Delivery tracking, analytics |
| **Stripe** | PostgreSQL | Financial data, ACID compliance |
| **WordPress** | MySQL | Simple CMS, legacy compatibility |
| **Shopify** | MySQL → Postgres | Migrated for better analytics |

---

## Migration Path

If you know MySQL, here's what changes:

| MySQL | PostgreSQL |
|-------|-----------|
| `AUTO_INCREMENT` | `SERIAL` or `IDENTITY` |
| `LIMIT 10 OFFSET 20` | Same (but use OFFSET sparingly) |
| `DATE_FORMAT()` | `TO_CHAR()` or `DATE_TRUNC()` |
| `CONCAT()` | `||` or `CONCAT()` (both work) |
| `IFNULL()` | `COALESCE()` |
| Backticks \`column\` | Double quotes "column" (rarely needed) |

---

## CitySense Architecture Decision

**We chose PostgreSQL because:**
1. Time-series sensor data (DATE_TRUNC for hourly trends)
2. Future JSON support (store sensor metadata flexibly)
3. Better aggregation queries (AVG, GROUP BY)
4. PostGIS extension (map visualizations)
5. Industry standard for data analytics

**The Swiggy backend uses Postgres for the same reasons.**

---

## Learn More

- PostgreSQL Docs: https://www.postgresql.org/docs/
- MySQL vs Postgres (detailed): https://www.2ndquadrant.com/en/postgresql/postgresql-vs-mysql/
- PostGIS (geographic extension): https://postgis.net/
