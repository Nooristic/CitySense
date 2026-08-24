# Realistic Data Generation Guide

**Context:** How to generate synthetic data that looks real (not random garbage)

> **Continuous mode:** these formulas don't just seed history once — `server/simulate_sensors.py` reuses them live every 15 minutes (CPCB CAAQMS-style) and backfills gaps on startup. Same patterns, forever-fresh data.

---

## 🎯 Why Realistic Data Matters

**Bad synthetic data:**
```python
temperature = random.uniform(15, 35)  # Completely random
# Problem: No patterns, unrealistic jumps
```

**Real-world data has patterns:**
- Temperature follows day/night cycles
- Traffic follows rush hours
- Sales spike on weekends
- Weather correlates with season

---

## 📊 Patterns in CitySense Data

### 1. Temperature (Sine Wave Pattern)
```python
import math
import random

def generate_realistic_temperature(hour: int, base_temp: float = 25.0) -> float:
    """Temperature follows a sine wave: coolest at 6 AM, hottest at 2 PM"""
    
    # Sine wave: peaks at hour 14 (2 PM), lowest at hour 6 (6 AM)
    cycle = math.sin((hour - 6) * math.pi / 12)
    
    # Base temp + 8°C swing + small random noise
    temp = base_temp + 8 * cycle + random.uniform(-2, 2)
    
    return round(temp, 2)

# Example output:
# 00:00 → 22°C (night, cool)
# 06:00 → 17°C (coldest)
# 14:00 → 33°C (hottest)
# 20:00 → 25°C (evening)
```

**Why this works:**
- `math.sin()` creates smooth day/night cycle
- `+ random.uniform(-2, 2)` adds realistic noise
- Real temperature doesn't jump randomly

---

### 2. Humidity (Inverse Correlation)
```python
def generate_realistic_humidity(temperature: float) -> float:
    """Humidity inversely correlated with temperature"""
    
    # Hot air → dry, cool air → humid
    base_humidity = 90 - (temperature - 15) * 2
    
    # Add noise
    humidity = base_humidity + random.uniform(-10, 10)
    
    # Clamp between 30-95%
    return round(max(30, min(95, humidity)), 2)

# Example:
# Temp 35°C → ~50% humidity (hot, dry)
# Temp 20°C → ~80% humidity (cool, humid)
```

---

### 3. PM2.5 Pollution (Rush Hour Spikes)
```python
def generate_realistic_pm25(hour: int, is_weekend: bool = False) -> float:
    """PM2.5 pollution peaks during rush hours"""
    
    base_pm25 = 35.0  # Normal level
    
    # Rush hour spikes (weekdays only)
    if not is_weekend:
        if 8 <= hour <= 10:
            base_pm25 += 40  # Morning traffic
        elif 18 <= hour <= 20:
            base_pm25 += 50  # Evening traffic (worse)
    
    # Night is cleaner
    if 0 <= hour <= 5:
        base_pm25 -= 15
    
    # Add randomness
    pm25 = base_pm25 + random.uniform(-15, 15)
    
    return round(max(5, pm25), 2)

# Example:
# 03:00 → 20 µg/m³ (night, clean)
# 09:00 → 75 µg/m³ (rush hour, polluted)
# 15:00 → 35 µg/m³ (afternoon, moderate)
```

---

## 🔧 Using Faker for Realistic Data

### Installation
```bash
pip install faker
```

### Basic Usage
```python
from faker import Faker
fake = Faker()

# Names
print(fake.name())           # "John Smith"
print(fake.first_name())     # "Sarah"

# Locations
print(fake.city())           # "New York"
print(fake.address())        # "123 Main St, Apt 4..."
print(fake.latitude())       # 12.3456
print(fake.longitude())      # 78.9012

# Dates/Times
print(fake.date_between(start_date='-30d', end_date='today'))
print(fake.date_time_between(start_date='-7d', end_date='now'))

# Internet
print(fake.email())          # "john@example.com"
print(fake.url())            # "https://example.com"
print(fake.ipv4())           # "192.168.1.1"

# Text
print(fake.text(max_nb_chars=200))
print(fake.paragraph())
print(fake.sentence())

# Numbers
print(fake.random_int(min=0, max=100))
print(fake.pyfloat(min_value=0, max_value=100))

# UUID
print(fake.uuid4())          # "550e8400-e29b-41d4-a716-446655440000"
```

---

## 🧪 Time-Series Data Generation

### Generating Date Ranges
```python
from datetime import datetime, timedelta

start_date = datetime(2026, 8, 10, 0, 0, 0)
days = 7

for day in range(days):
    for hour in range(24):
        for minute in range(0, 60, 5):  # Every 5 minutes
            timestamp = start_date + timedelta(days=day, hours=hour, minutes=minute)
            print(timestamp)  # 2026-08-10 00:00:00, 00:05:00, ...
```

### Adding Seasonality
```python
def get_base_temp_for_month(month: int) -> float:
    """Different base temperatures per season"""
    seasonal_temps = {
        1: 15,  # January (winter)
        2: 17,
        3: 22,
        4: 27,
        5: 32,  # May (hot)
        6: 35,
        7: 34,
        8: 33,  # August (monsoon)
        9: 30,
        10: 26,
        11: 20,
        12: 16,  # December (winter)
    }
    return seasonal_temps.get(month, 25)

# Usage
timestamp = datetime(2026, 8, 10, 14, 0, 0)
base_temp = get_base_temp_for_month(timestamp.month)  # 33°C for August
temp = generate_realistic_temperature(timestamp.hour, base_temp)
```

---

## 🎲 Probability Distributions

### Normal Distribution (Bell Curve)
```python
import random

# Most values near the mean, fewer at extremes
temperature = random.gauss(mu=25, sigma=5)  # Mean 25°C, std dev 5°C
# Results: mostly 20-30°C, rarely <15°C or >35°C
```

### Weighted Random Choices
```python
statuses = random.choices(
    ['active', 'maintenance', 'offline'],
    weights=[85, 10, 5],  # 85% active, 10% maintenance, 5% offline
    k=1
)[0]
```

### Exponential Distribution (for delays/events)
```python
# Useful for: time between events, failure rates
delay = random.expovariate(lambd=1.0/60)  # Average 60 seconds between events
```

---

## 🏗️ Complete Data Generation Template

```python
from datetime import datetime, timedelta
from faker import Faker
import random
import math

fake = Faker()

def generate_sensors(count: int) -> list:
    """Generate realistic sensor metadata"""
    zones = ["Zone A", "Zone B", "Zone C", "Zone D"]
    sensors = []
    
    for i in range(1, count + 1):
        sensor = {
            "sensor_id": f"SENSOR_{i:03d}",
            "name": f"{fake.city()} Monitor",
            "location": fake.street_name(),
            "zone": random.choice(zones),
            "latitude": fake.latitude(),
            "longitude": fake.longitude(),
            "status": random.choices(
                ['active', 'maintenance', 'offline'],
                weights=[85, 10, 5]
            )[0],
            "installed_at": fake.date_time_between(start_date='-2y', end_date='now')
        }
        sensors.append(sensor)
    
    return sensors


def generate_readings(sensor_id: int, start_date: datetime, days: int) -> list:
    """Generate realistic time-series readings"""
    readings = []
    
    for day in range(days):
        is_weekend = (start_date + timedelta(days=day)).weekday() >= 5
        
        for hour in range(24):
            for minute in range(0, 60, 5):
                timestamp = start_date + timedelta(days=day, hours=hour, minutes=minute)
                
                # Generate correlated values
                temp = generate_realistic_temperature(hour)
                humidity = generate_realistic_humidity(temp)
                pm25 = generate_realistic_pm25(hour, is_weekend)
                
                reading = {
                    "sensor_id": sensor_id,
                    "temperature": temp,
                    "humidity": humidity,
                    "pm25": pm25,
                    "timestamp": timestamp
                }
                readings.append(reading)
    
    return readings


# Generate dataset
sensors = generate_sensors(10)
all_readings = []

for sensor in sensors:
    readings = generate_readings(
        sensor_id=sensor["sensor_id"],
        start_date=datetime(2026, 8, 10),
        days=7
    )
    all_readings.extend(readings)

print(f"Generated {len(sensors)} sensors")
print(f"Generated {len(all_readings)} readings")
```

---

## ✅ Validation Checklist

**Good synthetic data should:**
- ✅ Have realistic ranges (temp 15-35°C, not -100 to 500°C)
- ✅ Show patterns over time (not random noise)
- ✅ Have correlations (temp ↑ → humidity ↓)
- ✅ Include edge cases (5% maintenance, rare outliers)
- ✅ Match real-world distributions

**Bad synthetic data:**
- ❌ Completely random values
- ❌ Unrealistic jumps (20°C → 40°C in 5 minutes)
- ❌ No time-based patterns
- ❌ Values outside physical limits

---

## 🔥 Advanced Techniques

### 1. Autocorrelation (Value Depends on Previous Value)
```python
def generate_with_autocorrelation(previous_value: float, mean: float, volatility: float) -> float:
    """New value is close to previous value"""
    change = random.gauss(0, volatility)
    new_value = previous_value + change
    
    # Pull back toward mean (mean reversion)
    new_value = new_value * 0.9 + mean * 0.1
    
    return new_value

# Usage
temp = 25.0
for _ in range(100):
    temp = generate_with_autocorrelation(temp, mean=25, volatility=0.5)
    print(temp)  # Smooth changes, not jumpy
```

### 2. Adding Anomalies
```python
def add_sensor_anomalies(value: float, anomaly_rate: float = 0.01) -> float:
    """Occasionally inject unrealistic readings (sensor malfunction)"""
    if random.random() < anomaly_rate:
        # 1% chance of anomaly
        return value * random.uniform(2, 5)  # Spike 2-5x
    return value
```

### 3. Missing Data
```python
def maybe_none(value, missing_rate: float = 0.05):
    """Simulate missing readings (5% of the time)"""
    return None if random.random() < missing_rate else value

pm25 = maybe_none(generate_realistic_pm25(hour))
```

---

## 📚 Learn More

- **Faker docs:** https://faker.readthedocs.io/
- **Random distributions:** https://docs.python.org/3/library/random.html
- **Time-series patterns:** https://otexts.com/fpp2/components.html
- **Synthetic data best practices:** https://towardsdatascience.com/synthetic-data-generation-a-must-have-skill-for-new-data-scientists-915896c0c1ae

---

## 🎯 Practice Ideas

1. **E-commerce dataset:** Generate orders with weekend spikes, holiday surges
2. **User activity:** Generate login times following work hours pattern
3. **Stock prices:** Generate with trends + random walk
4. **Weather data:** Generate with seasonal patterns + random fronts

**Your Day 2 `generate_data.py` is a perfect example — study it!**
