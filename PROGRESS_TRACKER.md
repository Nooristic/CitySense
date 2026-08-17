# SCRC Internship Sprint - 6 Day Action Plan

**Goal:** Build CitySense demo + prepare application for IIIT Hyderabad SCRC Internship  
**Deadline:** August 22, 2026  
**Current Date:** August 15, 2026

---

## 📋 Overall Progress Tracker

### Day 1 (Aug 16) - FastAPI + REST ⭐ HIGHEST PRIORITY
- [ ] Read FastAPI tutorial (First Steps through Pydantic Models)
- [ ] Build Mini Sensor API with 3+ endpoints
- [ ] Test with Swagger UI at `/docs`
- [ ] Optional: Port one Express API to FastAPI
- [ ] Push to GitHub with good commit message
- **Status:** 🟡 Setup complete, ready to start

### Day 2 (Aug 17) - PostgreSQL + Data Generation
- [ ] Install PostgreSQL
- [ ] Learn key Postgres vs MySQL differences
- [ ] Connect FastAPI to Postgres with SQLAlchemy
- [ ] Generate 50k-100k synthetic sensor dataset
- [ ] Build aggregation endpoint (AVG, GROUP BY)

### Day 3 (Aug 18) - React + Maps + Graphs
- [ ] React refresher (components, hooks, fetch)
- [ ] Add Leaflet for map visualization
- [ ] Add Chart.js for time-series + bar charts
- [ ] Wire frontend to FastAPI backend (enable CORS)

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
SCRC_Internship_Sprint/
├── DAY1_GUIDE.md                    # ✅ Created
├── day1_fastapi_basics/             # ✅ Created
│   ├── main.py                      # ✅ Working FastAPI app
│   ├── README.md                    # ✅ Complete docs
│   └── requirements.txt             # ✅ Dependencies listed
├── day2_postgres_integration/       # 🔜 Tomorrow
├── day3_react_frontend/             # 🔜 Day 3
├── day4_ml_llm/                     # 🔜 Day 4
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
