# SCRC Internship Sprint - 6 Day Action Plan

**Goal:** Build CitySense demo + prepare application for IIIT Hyderabad SCRC Internship  
**Deadline:** August 22, 2026  
**Current Date:** August 17, 2026 (Day 2)

---

## 📋 Overall Progress Tracker

### Day 1 (Aug 16) - FastAPI + REST ⭐ HIGHEST PRIORITY
- [x] Read FastAPI tutorial (First Steps through Pydantic Models)
- [x] Build Mini Sensor API with 3+ endpoints
- [x] Test with Swagger UI at `/docs`
- [x] Optional: Port one Express API to FastAPI
- [x] Push to GitHub with good commit message
- **Status:** ✅ COMPLETE - Pushed to GitHub

### Day 2 (Aug 17) - PostgreSQL + Data Generation
- [x] Install PostgreSQL
- [x] Learn key Postgres vs MySQL differences
- [x] Connect FastAPI to Postgres with SQLAlchemy
- [x] Generate ~20k synthetic sensor dataset
- [x] Build aggregation endpoint (AVG, GROUP BY)
- **Status:** ✅ COMPLETE - verified live (10 sensors, 20k readings)

### Day 3 (Aug 18) - React + Maps + Graphs
- [x] React refresher (components, hooks, fetch)
- [x] Add Leaflet for map visualization
- [x] Add Chart.js for time-series + bar charts
- [x] Wire frontend to FastAPI backend (enable CORS)
- **Status:** ✅ COMPLETE - Dashboard built & verified against live API (Aug 22)

### Day 4 (Aug 19) - ML + LLM Endpoints
- [x] Train scikit-learn model (predict PM2.5)
- [x] Expose as `/api/predict` endpoint
- [x] Add Gemini LLM endpoint `/api/ask` (with local Ollama fallback)
- [x] Test both AI endpoints
- **Status:** ✅ COMPLETE - verified live Aug 22 (R²=0.828, MAE=7.62 µg/m³)

### Day 5 (Aug 20) - Polish + Documentation
- [x] Clean repo structure (`server/`, `web/`, `fastapi_basics/`)
- [x] Add .gitignore, requirements.txt, .env handling
- [x] Write comprehensive README with architecture diagram
- [x] Add error handling and basic tests
- [x] Good Git commits throughout
- **Status:** ✅ COMPLETE - 18 pytest cases green, error hardening done (Aug 23)

### Day 6 (Aug 21) - Application Submission
- [ ] Update resume with 5 specific changes
- [ ] Write cover letter hitting all keywords
- [ ] Include GitHub link + CitySense pitch
- [ ] Submit application before EOD

---

## 🎯 Critical Success Factors

1. **FastAPI proficiency** - Your #1 gap, must demonstrate
2. **Working demo** - Better incomplete + working than complete + broken
3. **GitHub presence** - Clean commits, good README
4. **LLM experience** - Your unique advantage, highlight it

---

## 📁 Project Structure

```
CitySense/
├── fastapi_basics/                    # ✅ COMPLETE (Day 1)
│   ├── main.py                        # ✅ Working FastAPI app
│   ├── README.md                      # ✅ Complete docs
│   └── requirements.txt               # ✅ Dependencies listed
├── server/                            # ✅ COMPLETE (Day 2 + Day 4, renamed from day2_postgres_integration)
│   ├── main.py                        # ✅ FastAPI + SQLAlchemy + AI router
│   ├── database.py                    # ✅ DB connection
│   ├── models.py                      # ✅ ORM models
│   ├── generate_data.py               # ✅ Data generator
│   ├── ml_model.py                    # ✅ PM2.5 RandomForest (Day 4)
│   ├── train_model.py                 # ✅ CLI trainer
│   ├── ai_routes.py                   # ✅ /api/predict + /api/ask (Gemini → Ollama fallback)
│   ├── requirements.txt               # ✅ Dependencies
│   ├── .env                           # ✅ Config (gitignored)
│   └── README.md                      # ✅ Documentation
├── web/                               # ✅ COMPLETE (Day 3, renamed from react_frontend)
│   ├── src/App.jsx                    # ✅ Dashboard layout + data fetching
│   ├── src/components/                # ✅ SensorMap, HourlyTrend, TopPolluted
│   └── README.md                      # ✅ Run instructions
└── CitySense_Final/                   # 🔜 Day 5 (consolidated)
```

---

## ⏰ Time Budget Per Day

- **Learning:** 3-4 hours (focused, no rabbit holes)
- **Building:** 3-4 hours (working code)
- **Documentation:** 30-60 minutes (README, commits)

**Total per day:** 6-8 hours of focused work

---

## 🚨 If Running Short on Time

**Priority order:**
1. FastAPI + REST (do NOT skip)
2. PostgreSQL + data generation
3. React with map OR chart (pick one)
4. ML OR LLM endpoint (you have LLM already)
5. Clean Git + README

Even a simpler version that WORKS beats a complex unfinished one.

---

## 📝 Daily Reflection Questions

At end of each day, answer:
1. What did I build today that I can demo?
2. What's the #1 blocker for tomorrow?
3. Am I on track for a working demo by Day 5?

---

**Let's build this! 🚀**

---

## 🧪 Post-Sprint Enhancements

- [x] AI panel wired into React dashboard (`/api/ask` chat + `/api/predict` card)
- [x] Error hardening: NULL-safe `/api/ask` context (24h→7d fallback), DB-down → clean 503
- [x] 18-case pytest suite green
- [x] **Continuous sensor simulation** (`server/simulate_sensors.py`) — 15-min CPCB CAAQMS-aligned cadence with gap backfill; ends the stale-dataset era permanently
