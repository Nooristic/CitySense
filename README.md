# CitySense — Smart City Air Quality Monitoring System

A full-stack IoT sensor data platform for real-time urban air quality monitoring, analytics, and AI-powered insights. Built as a 6-day sprint: REST API → PostgreSQL → React dashboard → ML + LLM.

---

## Overview

CitySense collects, stores, and visualizes air quality data from a distributed sensor network across Hyderabad. It provides real-time monitoring, historical analytics (SQL aggregations), an interactive map dashboard, a scikit-learn PM2.5 prediction model, and an LLM assistant grounded on live data.

**Status:** All core features complete and verified against live services.

| Layer | What it does |
|---|---|
| **REST API** | Sensor ingestion, readings, SQL aggregations (FastAPI + SQLAlchemy) |
| **Dashboard** | Leaflet sensor map, Chart.js trends & pollution rankings (Vite + React) |
| **ML** | RandomForest PM2.5 prediction (`R²=0.828`, `MAE=7.62 µg/m³` on 20k rows) |
| **LLM** | `/api/ask` answers air-quality questions using Gemini, with a local **Ollama fallback** so the demo works offline |

---

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │              FastAPI  (server/)              │
   IoT sensors ────►│  /sensors  /readings  /aggregations/*        │
   POST readings    │                                              │
                    │  /api/predict ──► RandomForest (model_store/)│
                    │  /api/ask ──► Gemini ──fallback──► Ollama    │
                    └──────────────┬──────────────┬────────────────┘
                                   │              │
                                   ▼              ▼
                            ┌────────────┐  ┌──────────────────┐
                            │ PostgreSQL │  │ React Dashboard  │
                            │ citysense  │◄─│ (web/, port 5173)│
                            │ ~20k rows  │  │ Leaflet + Chart  │
                            └────────────┘  └──────────────────┘
```

---

## Project Structure

Each folder is a standalone app with its own dependencies (see folder READMEs):

```
CitySense/
├── fastapi_basics/      # Day 1 — minimal REST API (in-memory storage)
├── server/              # Day 2+4 — PostgreSQL backend + AI endpoints
│   ├── main.py          #   CRUD + aggregation endpoints
│   ├── database.py      #   Engine/session (DATABASE_URL from .env)
│   ├── models.py        #   Sensor ↔ Reading ORM models
│   ├── generate_data.py #   Creates tables + seeds ~20k realistic readings
│   ├── ml_model.py      #   RandomForest training/inference
│   ├── train_model.py   #   CLI trainer (python train_model.py)
│   ├── ai_routes.py     #   /api/predict, /api/ask, /api/model/info, /api/health
│   └── model_store/     #   Trained artifact (gitignored; auto-trains if missing)
└── web/                 # Day 3 — Vite + React dashboard
    └── src/components/  #   SensorMap, HourlyTrend, TopPolluted
```

> ⚠️ Endpoint paths differ between folders: Day 1 ingests at `POST /sensors/reading`; `server/` ingests at `POST /readings`. Aggregation endpoints exist only in `server/`.

---

## Quick Start (full stack)

### Prerequisites
- Python 3.10+, Node.js 18+
- PostgreSQL running on `localhost:5432`

### 1. Backend (`server/`)

```bash
cd server

# Create database once
psql -U postgres -c "CREATE DATABASE citysense;"

python -m venv venv && venv\Scripts\Activate.ps1   # Windows
pip install -r requirements.txt

# Seed tables + ~20k readings (run once)
python generate_data.py

# Optional: pre-train the ML model (auto-trains on first request otherwise)
python train_model.py

uvicorn main:app --reload          # → http://localhost:8000/docs
```

Database config lives in `server/.env` (`DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/citysense`). Never commit `.env`.

### LLM configuration (optional)

`/api/ask` tries providers in order:

1. **Gemini** — set `GEMINI_API_KEY` (and optionally `GEMINI_MODEL`, default `gemini-2.5-flash`) in `server/.env`
2. **Ollama** — local fallback (`http://localhost:11434`, default model `qwen2.5:0.5b-instruct`; override via `OLLAMA_BASE_URL` / `OLLAMA_MODEL`)
3. Neither available → `503` with setup hint. Check current provider anytime: `GET /api/health`

### 2. Frontend (`web/`)

```bash
cd web
npm install
npm run dev                        # → http://localhost:5173 (backend must be running)
```

Override the API base URL with `VITE_API_URL` in `web/.env` if needed.

---

## API Reference (`server/`)

### Core (Day 2)
| Method | Path | Description |
|---|---|---|
| `POST` | `/readings` | Ingest a reading (`sensor_id`, temperature, humidity, pm25, pm10?, timestamp?) |
| `GET` | `/readings` | Recent readings, filterable by `sensor_id`, `hours` (1–168), `limit` |
| `GET` | `/sensors` | All sensors, filterable by `zone`, `status` |
| `GET` | `/sensors/{sensor_id}` | One sensor |
| `POST` | `/sensors` | Register a sensor |
| `GET` | `/health` | DB connectivity + row counts |

### Aggregations (Day 2)
| Method | Path | Description |
|---|---|---|
| `GET` | `/aggregations/by-location?hours=24` | AVG temp/humidity/PM2.5 grouped by location |
| `GET` | `/aggregations/hourly-trend?sensor_id=SENSOR_001&hours=24` | Hourly buckets via `date_trunc` |
| `GET` | `/aggregations/top-polluted?hours=168&limit=5` | Most polluted locations |

### AI (Day 4)
| Method | Path | Description |
|---|---|---|
| `POST` | `/api/predict` | Predict PM2.5 for a sensor + optional timestamp/temp/humidity; returns value + AQI category + model stats |
| `GET` | `/api/model/info` | Training metadata (rows, MAE, R², features) |
| `POST` | `/api/ask` | Natural-language Q&A grounded on the last-24h data snapshot |
| `GET` | `/api/health` | Which LLM provider is active right now |

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"sensor_id": "SENSOR_001"}'

curl -X POST http://localhost:8000/api/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Which area has the worst air quality right now?"}'
```

Interactive docs: `http://localhost:8000/docs` (Swagger) · `/redoc`

---

## Data Model

```
sensors                              readings
+------------------+                 +------------------+
| id (PK)          |                 | id (PK)          |
| sensor_id  (uniq)|◄────────────────| sensor_id (FK)   |
| name             |                 | temperature      |
| location         |                 | humidity         |
| zone             |                 | pm25             |
| latitude         |                 | pm10             |
| longitude        |                 | timestamp        |
| status           |                 +------------------+
+------------------+
```

Synthetic dataset (10 Hyderabad locations): temperature follows a time-of-day sine wave, humidity is inversely correlated, PM2.5 peaks during rush hours (8–10 AM, 6–8 PM).

---

## Tech Stack

- **Backend:** FastAPI 0.115 · Pydantic v2 · Uvicorn · SQLAlchemy 2.0 · psycopg2
- **ML:** scikit-learn (RandomForestRegressor) · joblib · NumPy
- **LLM:** google-genai (Gemini) → httpx → local Ollama fallback
- **Frontend:** React 19 · Vite · react-leaflet · Chart.js · oxlint
- **Data:** Faker + custom generators (~20k readings)

---

## Development Notes

- Run commands **from inside each app folder** (imports are flat, e.g. `from database import ...`); don't share one venv across folders.
- Verification is manual via Swagger UI / curl / the dashboard — no automated tests.
- `web/`: use `npm run lint` (oxlint) and `npm run build`.
- If charts come back empty, regenerate data (`python generate_data.py`) — aggregation windows filter by `NOW() - N hours`.
- `server/model_store/` is gitignored; the model retrains automatically from the DB on first use.

---

## Contributing

This is a portfolio/demonstration project. Feedback welcome via issues.

## License

MIT License — demonstration project for educational purposes.

---

Built with FastAPI · PostgreSQL · React · scikit-learn · Gemini
