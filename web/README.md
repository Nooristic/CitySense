# Web Dashboard — Map + Charts

**Status:** Complete — verified against live API

---

## What Was Built

A Vite + React 19 dashboard (`src/App.jsx`) wired to the Day 2 FastAPI backend:

- **Sensor network map** (`src/components/SensorMap.jsx`) — react-leaflet `MapContainer` centered on Hyderabad, one `CircleMarker` per sensor colored by zone. Clicking a marker selects that sensor everywhere else in the app.
- **Hourly trends chart** (`src/components/HourlyTrend.jsx`) — Chart.js line chart from `/aggregations/hourly-trend`: PM2.5 on the right axis, temperature/humidity on the left.
- **Most polluted areas** (`src/components/TopPolluted.jsx`) — horizontal bar chart of avg PM2.5 per location from `/aggregations/top-polluted`, bars colored by AQI bucket (`src/lib/aqi.js`).
- **AI assistant panel** (`src/components/AiPanel.jsx`) — "Ask CitySense" chat box calling `POST /api/ask` (grounded on last-24h data; provider badge shows gemini/ollama), plus a PM2.5 prediction card calling `POST /api/predict` for the selected sensor with AQI-colored result.
- Time-range switcher (1d / 3d / 7d) shared by both charts; loading/error/empty states throughout.

CORS is already open on the backend (`server/main.py`, `allow_origins=["*"]`), so no backend change was needed.

## How to Run

```bash
# Terminal 1 — backend first (Postgres must be running, DB seeded)
cd server
uvicorn main:app --reload

# Terminal 2 — frontend
cd web
npm install
npm run dev
```

Open http://localhost:5173

## API Contract Used

| Endpoint | Query params | Used for |
|---|---|---|
| `GET /sensors` | — | markers, sensor dropdown |
| `GET /aggregations/hourly-trend` | `sensor_id`, `hours` (24/72/168) | line chart |
| `GET /aggregations/top-polluted` | `hours`, `limit=5` | bar chart |
| `POST /api/ask` | `{question}` (3–500 chars) | AI chat answers |
| `POST /api/predict` | `{sensor_id}` | PM2.5 forecast card |

The API base URL defaults to `http://localhost:8000`; override with `VITE_API_URL` in `.env`.

## Gotchas

- Aggregation endpoints filter by `NOW() - N hours`. The synthetic dataset originally covered Aug 10–16; on Aug 22 all reading timestamps were shifted **+6 days** (now Aug 16–22) so default windows return data. If charts come back empty later, re-shift timestamps or regenerate data.
- Leaflet's default marker icons break under bundlers (missing asset paths), so the map uses `CircleMarker` instead — no icon assets needed.
- `npm run lint` (oxlint) and `npm run build` both pass; there is no test suite.

---

`/api/ask` needs an LLM provider: Gemini key in `server/.env` **or** local Ollama running (see root README). Without either, the chat shows a 503 error message; prediction works regardless.
