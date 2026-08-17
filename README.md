# CitySense - Smart City Air Quality Monitoring System

A full-stack IoT sensor data platform for real-time urban air quality monitoring and analysis.

---

## Overview

CitySense is a smart city application that collects, stores, and visualizes air quality data from distributed sensor networks. The platform provides real-time monitoring, historical analytics, and predictive insights for urban environmental management.

**Live Demo:** [Coming soon]

---

## Features

- **REST API Backend** - FastAPI-powered service for sensor data ingestion and retrieval
- **Real-time Data Collection** - Endpoints for IoT sensors to POST readings (temperature, humidity, PM2.5)
- **Sensor Management** - Track and manage multiple sensor deployments across zones
- **Query & Analytics** - Filter and aggregate data by location, time, and environmental metrics
- **Auto-generated API Documentation** - Interactive Swagger UI for easy integration

### Coming Soon
- PostgreSQL database with 50k+ sensor readings
- React dashboard with interactive maps (Leaflet)
- Time-series visualizations (Chart.js)
- ML-powered PM2.5 prediction model
- LLM-based reading interpretation

---

## Tech Stack

**Backend:**
- FastAPI 0.115.0
- Pydantic 2.9.0 (data validation)
- Uvicorn (ASGI server)

**Database:** PostgreSQL (upcoming)  
**Frontend:** React + Leaflet + Chart.js (upcoming)  
**ML/AI:** scikit-learn, Gemini LLM (upcoming)

---

## Architecture

```
┌─────────────────┐      ┌──────────────────┐      ┌─────────────────┐
│  IoT Sensors    │      │   FastAPI        │      │   React         │
│  (Data Source)  │ ───► │   REST API       │ ───► │   Dashboard     │
│                 │ POST │                  │ GET  │                 │
└─────────────────┘      └──────────────────┘      └─────────────────┘
                               │
                               ▼
                         ┌──────────────┐
                         │  PostgreSQL  │
                         │  Database    │
                         └──────────────┘
```

---

## API Endpoints

### Sensors
- `GET /` - API information and health status
- `GET /sensors/{sensor_id}` - Get specific sensor details
- `GET /sensors?zone={zone}&status={status}` - List/filter all sensors
- `GET /health` - System health check

### Readings
- `POST /sensors/reading` - Submit new sensor reading
- `GET /readings?sensor_id={id}&limit={n}` - Retrieve historical readings

**Interactive docs:** `http://localhost:8000/docs`

---

## Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/CitySense.git
cd CitySense/day1_fastapi_basics

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows
# source venv/bin/activate    # Mac/Linux

# Install dependencies
pip install -r requirements.txt
```

### Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Testing

Visit the interactive API documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Example curl commands:

```bash
# Get all sensors
curl http://localhost:8000/sensors

# Get specific sensor
curl http://localhost:8000/sensors/SENSOR_001

# Submit a reading
curl -X POST http://localhost:8000/sensors/reading \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_id": "SENSOR_001",
    "temperature": 28.5,
    "humidity": 70.0,
    "pm25": 42.3
  }'

# Get readings
curl "http://localhost:8000/readings?sensor_id=SENSOR_001&limit=10"
```

---

## Project Structure

```
CitySense/
├── day1_fastapi_basics/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt     # Python dependencies
│   └── README.md           # Module documentation
├── .gitignore
└── README.md               # This file
```

---

## Data Model

### SensorReading
```python
{
  "sensor_id": "string",
  "temperature": float,      # -50 to 60°C
  "humidity": float,         # 0 to 100%
  "pm25": float | null,      # PM2.5 µg/m³
  "timestamp": datetime | null
}
```

### SensorInfo
```python
{
  "sensor_id": "string",
  "location": "string",
  "zone": "string",
  "status": "active" | "maintenance",
  "last_reading": datetime | null
}
```

---

## Development

### Current Status
- ✅ REST API with FastAPI
- ✅ Pydantic data validation
- ✅ In-memory data storage
- ✅ Interactive API documentation
- ✅ Error handling and validation

### Roadmap
- PostgreSQL integration for persistent storage
- Bulk data import (50k+ historical readings)
- React-based monitoring dashboard
- Geographic visualization with Leaflet maps
- Time-series charts and analytics
- ML model for air quality prediction
- LLM-powered insights and recommendations

---

## Contributing

This is a portfolio/demonstration project. Feedback and suggestions are welcome via issues.

---

## License

MIT License - This is a demonstration project for educational purposes.

---

## Contact

**Noor Banu**  
[Your Email] | [LinkedIn] | [GitHub]

---

Built with FastAPI · Python · Modern IoT Architecture
