# Deploying CitySense

Free-tier deployment: **Render** (FastAPI backend + PostgreSQL) + **Vercel** (React dashboard). Total cost: ₹0. Time: ~45 minutes.

```
GitHub push ──► Render Web Service ──► FastAPI ──► Render Postgres
                     │                     ▲
                     └─ (optional) Cron ──►│ simulate_sensors.py --once
Vercel ◄── npm run build (web/) ── dashboard calls https://<api>.onrender.com
```

---

## Step 0 — Push the repo

```powershell
git push origin main
```

`.env`, `model_store/`, and personal notes never leave your machine (gitignored).

## Step 1 — Database (Render)

1. Sign up at [render.com](https://render.com) with GitHub.
2. **New + → Postgres** → name `citysense`, **Free** plan → Create.
3. Copy the **Internal Database URL** (`postgresql://user:pass@dpg-xxx/citysense`).

> No manual URL editing needed: `server/database.py` auto-converts `postgresql://` → `postgresql+psycopg2://`.

## Step 2 — Backend (Render Web Service)

1. **New + → Web Service** → pick `Nooristic/CitySense`.
2. Settings:

   | Field | Value |
   |---|---|
   | Root Directory | `server` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |
   | Instance Type | Free |

3. **Environment → Add:**
   - `DATABASE_URL` = URL from Step 1 (paste as-is)
   - `GEMINI_API_KEY` = free key from [aistudio.google.com](https://aistudio.google.com) — **required for `/api/ask`** in the cloud (local Ollama isn't reachable there; `/api/predict` works regardless)
4. **Create Web Service** → first deploy takes a few minutes.
5. Verify: open `https://<your-app>.onrender.com/docs` → try `GET /health`.

## Step 3 — Seed the cloud database (no Shell needed on free tier)

Render's Shell requires a paid instance. Two free options:

### Option A — seed from your own machine (recommended)

1. Render → your **Postgres** → **Info** → copy the **External Database URL** (`...?sslmode=require`).
2. Locally:

   ```powershell
   cd server
   $env:DATABASE_URL = "postgresql://<external-url-here>"
   python generate_data.py          # seeds the CLOUD db
   Remove-Item Env:DATABASE_URL     # IMPORTANT: back to local db
   ```

3. Verify: `https://<your-app>.onrender.com/health` → sensors 10, readings ~20k.

Skip `train_model.py` in the cloud — the model **auto-trains on the first `/api/predict` call** (~1 min once on free CPU, then cached).

### Option B — seed on every deploy (zero commands)

Settings → Start Command:

```
python generate_data.py && uvicorn main:app --host 0.0.0.0 --port $PORT
```

Idempotent: seeds on first boot, no-ops on restarts (adds a few seconds per boot).

> **Render free Postgres expires after 30 days.** If the demo URL must outlive that, recreate + re-seed, or upgrade the DB only.

## Step 4 — Frontend (Vercel)

1. Sign up at [vercel.com](https://vercel.com) with GitHub → **Add New → Project** → import the repo.
2. Configure:
   - Framework Preset: **Vite** (auto-detected)
   - Root Directory: `web`
   - Environment variable: `VITE_API_URL` = `https://<your-app>.onrender.com`
3. **Deploy** → open the `*.vercel.app` URL → map, charts, and the AI panel should be live.

## Free-tier quirks (set expectations)

| Quirk | What it means |
|---|---|
| Render sleeps after ~15 min idle | First visit wakes it (~50 s). Charts may be empty on that first load — refresh. |
| Ephemeral disk | `model_store/` rebuilds on wake (auto-train). Source of truth is Postgres, which persists. |
| Simulator isn't running in the cloud | Data ages out over weeks. Fix options below. |
| CORS `allow_origins=["*"]` | Works; pin it to your Vercel URL in `server/main.py` for production hygiene. |

### Keeping cloud data fresh (optional)

Pick one:

- **Render Cron Job** (paid, ~$1/mo): new Cron Job → repo, root `server`, command `python simulate_sensors.py --once`, schedule `*/15 * * * *`, with `DATABASE_URL` set.
- **GitHub Actions (free):** scheduled workflow every 15 min that POSTs one reading per sensor to `/readings` — see `simulate_sensors.py --once` logic for the values/formulas.

## Updating after deploy

`git push` → Render and Vercel auto-redeploy. Still manual: DB schema changes (Shell: rerun `generate_data.py` logic / migrations) and model retrains (Shell: `python train_model.py`).

## Troubleshooting

| Symptom | Fix |
|---|---|
| `The remote server returned an error (503)` on wake | Normal cold start; retry in ~30 s. |
| Charts empty after deploy | Shell: run `python generate_data.py` (Step 3 skipped). |
| `/api/ask` returns 503 "No LLM available" | `GEMINI_API_KEY` env var missing/invalid on Render. |
| `/api/predict` first call times out | Free-tier CPU + auto-training. Pre-run `python train_model.py` in Shell. |
| Frontend loads but no data | `VITE_API_URL` typo, or backend still waking — check the Render dashboard → Events/Logs. |
