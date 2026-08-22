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
- [ ] Install PostgreSQL (user task - in progress)
- [x] Learn key Postgres vs MySQL differences
- [x] Connect FastAPI to Postgres with SQLAlchemy
- [x] Generate 50k-100k synthetic sensor dataset (script ready)
- [x] Build aggregation endpoint (AVG, GROUP BY)
- **Status:** 🟡 Code complete - waiting for PostgreSQL install

### Day 3 (Aug 18) - React + Maps + Graphs
- [x] React refresher (components, hooks, fetch)
- [x] Add Leaflet for map visualization
- [x] Add Chart.js for time-series + bar charts
- [x] Wire frontend to FastAPI backend (enable CORS)
- **Status:** ✅ COMPLETE - Dashboard built & verified against live API (Aug 22)

### Day 4 (Aug 19) - ML + LLM Endpoints
- [ ] Train scikit-learn model (predict PM2.5)
- [ ] Expose as `/api/predict` endpoint
- [ ] Add Gemini LLM endpoint `/api/ask`
- [ ] Test both AI endpoints

### Day 5 (Aug 20) - Polish + Documentation
- [ ] Clean repo structure
- [ ] Add .gitignore, requirements.txt, .env handling
- [ ] Write comprehensive README with architecture diagram
- [ ] Add error handling and basic tests
- [ ] Good Git commits throughout

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
├── DAY1_GUIDE.md                    # ✅ Created
├── DAY2_GUIDE.md                    # ✅ Created
├── POSTGRES_VS_MYSQL.md             # ✅ Created
├── day1_fastapi_basics/             # ✅ COMPLETE
│   ├── main.py                      # ✅ Working FastAPI app
│   ├── README.md                    # ✅ Complete docs
│   └── requirements.txt             # ✅ Dependencies listed
├── day2_postgres_integration/       # ✅ CODE COMPLETE
│   ├── main.py                      # ✅ FastAPI + SQLAlchemy
│   ├── database.py                  # ✅ DB connection
│   ├── models.py                    # ✅ ORM models
│   ├── generate_data.py             # ✅ Data generator
│   ├── requirements.txt             # ✅ Dependencies
│   ├── .env                         # ✅ Config
│   └── README.md                    # ✅ Documentation
├── day3_react_frontend/               # ✅ COMPLETE (Vite + React, Leaflet map, Chart.js)
│   ├── src/App.jsx                    # ✅ Dashboard layout + data fetching
│   ├── src/components/                # ✅ SensorMap, HourlyTrend, TopPolluted
│   └── README.md                      # ✅ Run instructions
├── day4_ml_llm/                       # 🔜 Day 4
└── CitySense_Final/                 # 🔜 Day 5 (consolidated)
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
