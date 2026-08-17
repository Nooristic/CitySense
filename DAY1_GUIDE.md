# Day 1: FastAPI + REST Foundations
**Date:** Aug 16, 2026 (Friday)  
**Goal:** Learn FastAPI basics and build a working REST API  
**Time Budget:** 6-8 hours

---

## Why FastAPI Matters for This Internship
FastAPI is **#1 on the SCRC job posting**. It's your biggest skill gap and highest priority. You need to show you can build with it, not just read about it.

---

## Part 1: FastAPI Crash Course (3-4 hours)

### What is FastAPI?
- Modern Python web framework (like Express.js for Node)
- Automatically generates API documentation (Swagger UI)
- Uses Python type hints for validation
- Built on **Starlette** (web) + **Pydantic** (data validation)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install FastAPI and uvicorn (ASGI server)
pip install fastapi uvicorn[standard] pydantic
```

### Core Concepts You MUST Know

#### 1. **Basic Route (GET request)**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

# Run with: uvicorn main:app --reload
```

#### 2. **Path Parameters** (like `/users/{user_id}`)
```python
@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}
```

#### 3. **Query Parameters** (like `/items?skip=0&limit=10`)
```python
@app.get("/items/")
def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

#### 4. **Request Body with Pydantic** (POST requests)
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    is_available: bool = True

@app.post("/items/")
def create_item(item: Item):
    return {"item_name": item.name, "item_price": item.price}
```

#### 5. **Response Models** (control what's returned)
```python
class ItemResponse(BaseModel):
    name: str
    price: float

@app.post("/items/", response_model=ItemResponse)
def create_item(item: Item):
    # Even if you return extra fields, only name and price are sent
    return item
```

### Official Tutorial Sections to Read
Go to: https://fastapi.tiangolo.com/tutorial/

**Read ONLY these sections** (don't get lost in advanced topics):
1. First Steps
2. Path Parameters
3. Query Parameters
4. Request Body
5. Query Parameters and String Validations (skim)
6. Pydantic Models

**SKIP:** Security, Dependencies (advanced), WebSockets, Background Tasks, Testing (for now)

---

## Part 2: Build Your First FastAPI App (1 hour)

### Task: "Mini Sensor API"
Build a tiny API with 3 endpoints to practice the concepts.

**Requirements:**
- `GET /` - returns welcome message
- `GET /sensors/{sensor_id}` - returns mock sensor data
- `POST /sensors/reading` - accepts a sensor reading (Pydantic model)

**Starter Code:**

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Mini Sensor API")

# Pydantic model for sensor reading
class SensorReading(BaseModel):
    sensor_id: str
    temperature: float
    humidity: float
    pm25: Optional[float] = None  # Optional field

@app.get("/")
def root():
    return {"message": "Welcome to Mini Sensor API", "version": "1.0"}

@app.get("/sensors/{sensor_id}")
def get_sensor(sensor_id: str):
    # Mock data for now
    return {
        "sensor_id": sensor_id,
        "location": "Zone A",
        "status": "active"
    }

@app.post("/sensors/reading")
def post_reading(reading: SensorReading):
    return {
        "message": "Reading received",
        "data": reading.dict(),
        "processed": True
    }

# Run with: uvicorn main:app --reload
# Docs at: http://localhost:8000/docs
```

**Test it:**
1. Run: `uvicorn main:app --reload`
2. Open browser: `http://localhost:8000/docs` (automatic Swagger UI!)
3. Try each endpoint in the interactive docs

---

## Part 3: Port an Existing API to FastAPI (2 hours)

### Task: Convert one of your Express.js APIs to FastAPI

**Pick ONE simple API from your Global Data Hub project.** Ideally:
- Has 2-3 endpoints
- Does some data processing
- Uses JSON requests/responses

**Example: If you have a "Countries API" in Express:**

**Express (Node.js):**
```javascript
app.get('/api/countries', (req, res) => {
    const { region } = req.query;
    // filter logic
    res.json({ countries: filteredCountries });
});
```

**FastAPI (Python):**
```python
@app.get("/api/countries")
def get_countries(region: Optional[str] = None):
    # same filter logic in Python
    return {"countries": filtered_countries}
```

**Why this matters:**
- Shows you can move between stacks quickly
- Proves you understand REST principles, not just one framework
- Gives you a second working FastAPI repo

---

## Part 4: Push to GitHub

### Create Repository
```bash
git init
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore

git add .
git commit -m "Day 1: FastAPI basics - Mini Sensor API

- Three working endpoints (GET root, GET sensor, POST reading)
- Pydantic models for validation
- Auto-generated docs at /docs"

# Push to GitHub
gh repo create day1-fastapi-basics --public --source=. --push
```

---

## Deliverables Checklist

- [ ] Virtual environment created and FastAPI installed
- [ ] Read FastAPI tutorial sections (First Steps through Pydantic Models)
- [ ] Built Mini Sensor API with 3 working endpoints
- [ ] Tested endpoints using Swagger UI at `/docs`
- [ ] (Optional) Ported one Express API to FastAPI
- [ ] Created `README.md` with run instructions
- [ ] Pushed to GitHub with descriptive commit message

---

## Tomorrow (Day 2)
We'll connect this FastAPI app to **PostgreSQL**, generate your "huge dataset" of 50k+ sensor rows, and add aggregation endpoints. FastAPI knowledge from today makes that smooth.

---

## Quick Reference

### Running FastAPI
```bash
# Development (auto-reload on file changes)
uvicorn main:app --reload

# Production
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Common Pydantic Field Types
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Example(BaseModel):
    name: str                    # Required string
    age: int                     # Required integer
    email: Optional[str] = None  # Optional string
    tags: List[str] = []         # List of strings
    created_at: datetime         # Datetime object
```

### Auto-generated Docs
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

---

## Tips
1. **Use the interactive docs** (`/docs`) for testing — it's faster than Postman
2. **Type hints are enforced** — FastAPI validates automatically
3. **Errors are clear** — read the Pydantic validation errors carefully
4. **Keep it simple** — don't add auth, middleware, or complex stuff yet

---

**Let's get started!** Tell me when you're ready to begin Part 1, or if you want me to clarify anything first.
