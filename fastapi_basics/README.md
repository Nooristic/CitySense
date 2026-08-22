# Mini Sensor API - Day 1 FastAPI Basics

**SCRC Internship Sprint - Day 1 Project**  
**Date:** August 16, 2026

A practice REST API built with FastAPI to demonstrate core concepts: path parameters, query parameters, request bodies, Pydantic validation, and automatic API documentation.

---

## 🎯 What This Project Demonstrates

- ✅ **FastAPI framework basics**
- ✅ **RESTful API design** (GET, POST endpoints)
- ✅ **Pydantic models** for data validation
- ✅ **Path parameters** (`/sensors/{sensor_id}`)
- ✅ **Query parameters** (`/sensors?zone=Zone A&status=active`)
- ✅ **Request body validation** with type hints
- ✅ **Auto-generated API documentation** (Swagger UI)
- ✅ **Error handling** (404 responses)

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn[standard] pydantic
```

---

## 🚀 Running the API

```bash
# Make sure you're in the day1_fastapi_basics directory
cd day1_fastapi_basics

# Run the development server
uvicorn main:app --reload
```

The API will be available at: **http://localhost:8000**

---

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test all endpoints directly in the browser using Swagger UI!

---

## 🔗 API Endpoints

### Root
- **GET /** - Welcome message and API information

### Sensors
- **GET /sensors/{sensor_id}** - Get specific sensor information
  - Example: `/sensors/SENSOR_001`
  
- **GET /sensors** - Get all sensors (with optional filters)
  - Query params: `zone` (e.g., "Zone A"), `status` (e.g., "active")
  - Example: `/sensors?zone=Zone%20A&status=active`

### Readings
- **POST /sensors/reading** - Submit a new sensor reading
  - Body: JSON with `sensor_id`, `temperature`, `humidity`, optional `pm25`
  
- **GET /readings** - Get recent readings
  - Query params: `sensor_id` (filter by sensor), `limit` (max results)
  - Example: `/readings?sensor_id=SENSOR_001&limit=5`

### Health
- **GET /health** - API health check

---

## 🧪 Testing Examples

### Using curl:

```bash
# Get root information
curl http://localhost:8000/

# Get specific sensor
curl http://localhost:8000/sensors/SENSOR_001

# Get all sensors in Zone A
curl "http://localhost:8000/sensors?zone=Zone%20A"

# Submit a reading
curl -X POST http://localhost:8000/sensors/reading \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "SENSOR_001",
    "temperature": 28.5,
    "humidity": 70.0,
    "pm25": 42.3
  }'

# Get recent readings
curl "http://localhost:8000/readings?limit=5"
```

### Using the Interactive Docs:

1. Go to http://localhost:8000/docs
2. Click on any endpoint
3. Click "Try it out"
4. Fill in parameters
5. Click "Execute"

---

## 📂 Project Structure

```
day1_fastapi_basics/
├── main.py          # Main FastAPI application
├── README.md        # This file
└── requirements.txt # Python dependencies
```

---

## 🎓 Key Concepts Learned

### 1. FastAPI Decorators
```python
@app.get("/path")        # GET request
@app.post("/path")       # POST request
```

### 2. Path Parameters
```python
@app.get("/sensors/{sensor_id}")
def get_sensor(sensor_id: str):
    # sensor_id comes from URL path
```

### 3. Query Parameters
```python
@app.get("/sensors")
def get_all(zone: Optional[str] = None):
    # zone comes from ?zone=value
```

### 4. Request Body with Pydantic
```python
class SensorReading(BaseModel):
    sensor_id: str
    temperature: float

@app.post("/readings")
def create(reading: SensorReading):
    # FastAPI validates the JSON body
```

### 5. Response Models
```python
@app.get("/sensor", response_model=SensorInfo)
def get_sensor():
    # Return type is automatically validated
```

---

## 🔄 Next Steps (Day 2)

Tomorrow we'll:
- Connect this API to **PostgreSQL**
- Replace in-memory storage with real database queries
- Use **SQLAlchemy** for ORM
- Generate 50k+ synthetic sensor readings
- Add aggregation endpoints (`AVG`, `GROUP BY`)

---

## 📝 Notes

- Currently using **in-memory storage** (data resets on restart)
- Mock sensors: `SENSOR_001`, `SENSOR_002`, `SENSOR_003`
- Automatic data validation via Pydantic
- Auto-reload enabled for development

---

## 🤝 Author

**Noor Banu**  
SCRC Internship Application - 6 Day Sprint  
Building towards: CitySense (Full-stack Smart City Demo)

---

## 📄 License

This is a learning project for internship application purposes.
