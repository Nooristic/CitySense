# AGENTS.md

## What this repo is

Learning/portfolio project ("CitySense" air-quality API), built as a 6-day sprint (see `PROGRESS_TRACKER.md`). **Each `dayN_*` folder is a standalone FastAPI app** with its own `requirements.txt`, README, and venv — there is no root package, lockfile, test suite, or linter. Root-level `DAY*_GUIDE.md` / `*_CHEATSHEET.md` / `*_GUIDE.md` files are study notes, not build docs; treat the code as the source of truth.

New work goes in a **new `dayN_*` folder** (per `PROGRESS_TRACKER.md`: `day3_react_frontend`, `day4_ml_llm`, then a consolidated `CitySense_Final/`) — not by editing earlier days.

## Running an app

- Run commands **from inside the day folder** (imports are flat, e.g. `from database import ...`): `uvicorn main:app --reload`.
- Deps are installed per folder; pins intentionally differ between days (day1 vs day2 requirements). Don't share one venv across days. Windows activation: `venv\Scripts\Activate.ps1`.
- Verification is manual: hit `http://localhost:8000/docs` (Swagger) or curl. There are no automated tests or lint/typecheck config — don't invent commands for them.

## Day 2 setup order (matters)

1. PostgreSQL must be running on localhost:5432 (local dev creds: `postgres`/`postgres`).
2. Database `citysense` must exist: `psql -U postgres -c "CREATE DATABASE citysense;"`.
3. `python generate_data.py` — creates tables via `Base.metadata.create_all` **and** seeds ~20k readings. Run once before starting the server.
4. Then `uvicorn main:app --reload`.

DB connection comes from `day2_postgres_integration/.env` (`DATABASE_URL`), with the same dev fallback hardcoded in `database.py`. `.env` is gitignored — never commit it, never delete it.

## Gotchas

- Endpoint paths differ between days: day1 accepts readings at `POST /sensors/reading`; day2 at `POST /readings`. Aggregation endpoints (`/aggregations/by-location|hourly-trend|top-polluted`) exist only in day2. The root README documents day1 paths only.
- `day2_postgres_integration/opencode.json` scopes a local Ollama model config to that folder; there is no root OpenCode config.
