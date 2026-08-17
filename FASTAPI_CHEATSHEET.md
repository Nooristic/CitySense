# FastAPI Quick Reference - SCRC Sprint

Quick lookup for FastAPI patterns you'll use daily.

---

## Installation & Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install
pip install fastapi uvicorn[standard] pydantic
```

---

## Running the Server

```bash
# Development (auto-reload)
uvicorn main:app --reload

# Custom port
uvicorn main:app --reload --port 8080

# Production
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Docs URLs:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Basic App Structure

```python
from fastapi import FastAPI

app = FastAPI(
    title="My API",
    description="API description",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Hello World"}
```

---

## HTTP Methods

```python
@app.get("/items")       # Read
@app.post("/items")      # Create
@app.put("/items/{id}")  # Update (full)
@app.patch("/items/{id}") # Update (partial)
@app.delete("/items/{id}") # Delete
```

---

## Path Parameters

```python
@app.get("/users/{user_id}")
def get_user(user_id: int):  # Type validated automatically
    return {"user_id": user_id}

# Multiple path params
@app.get("/users/{user_id}/posts/{post_id}")
def get_post(user_id: int, post_id: int):
    return {"user_id": user_id, "post_id": post_id}
```

---

## Query Parameters

```python
# Optional with default
@app.get("/items")
def get_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}

# Required query param (no default)
@app.get("/search")
def search(q: str):
    return {"query": q}

# Optional (can be None)
from typing import Optional

@app.get("/items")
def get_items(category: Optional[str] = None):
    return {"category": category}
```

---

## Pydantic Models (Request Body)

```python
from pydantic import BaseModel, Field
from typing import Optional

class Item(BaseModel):
    name: str
    price: float = Field(..., gt=0, description="Price must be positive")
    description: Optional[str] = None
    tax: Optional[float] = None

@app.post("/items")
def create_item(item: Item):
    return {"item": item.dict(), "total": item.price + (item.tax or 0)}
```

---

## Response Models

```python
class ItemResponse(BaseModel):
    name: str
    price: float
    # Won't include other fields even if returned

@app.post("/items", response_model=ItemResponse)
def create_item(item: Item):
    # Even if Item has more fields, only ItemResponse fields are returned
    return item
```

---

## Validation with Field

```python
from pydantic import Field

class Sensor(BaseModel):
    sensor_id: str = Field(..., min_length=5, max_length=20)
    temperature: float = Field(..., ge=-50, le=60)  # -50 <= temp <= 60
    humidity: float = Field(..., ge=0, le=100)
    pm25: Optional[float] = Field(None, ge=0)
```

---

## HTTP Exceptions

```python
from fastapi import HTTPException

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id not in database:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found"
        )
    return database[item_id]
```

---

## Status Codes

```python
from fastapi import status

@app.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(item: Item):
    return item

# Common status codes:
# 200 - OK
# 201 - Created
# 204 - No Content
# 400 - Bad Request
# 404 - Not Found
# 500 - Internal Server Error
```

---

## Tags (for documentation grouping)

```python
@app.get("/users", tags=["users"])
def get_users():
    return []

@app.get("/items", tags=["items"])
def get_items():
    return []
```

---

## CORS (for React frontend)

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Datetime Handling

```python
from datetime import datetime

class Reading(BaseModel):
    timestamp: datetime
    value: float

@app.post("/readings")
def create_reading(reading: Reading):
    # FastAPI automatically parses ISO 8601 datetime strings
    return {"received_at": datetime.now(), "data": reading}
```

---

## List Responses

```python
from typing import List

class Item(BaseModel):
    name: str
    price: float

@app.get("/items", response_model=List[Item])
def get_items():
    return [
        {"name": "Item 1", "price": 10.5},
        {"name": "Item 2", "price": 20.0}
    ]
```

---

## Environment Variables

```python
import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    
    class Config:
        env_file = ".env"

settings = Settings()
```

---

## Common Patterns

### Health Check
```python
@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### Pagination
```python
@app.get("/items")
def get_items(page: int = 1, page_size: int = 10):
    skip = (page - 1) * page_size
    return {
        "page": page,
        "page_size": page_size,
        "items": items[skip:skip + page_size]
    }
```

### Search with Multiple Filters
```python
@app.get("/sensors")
def search_sensors(
    zone: Optional[str] = None,
    status: Optional[str] = None,
    min_temp: Optional[float] = None
):
    results = all_sensors
    if zone:
        results = [s for s in results if s["zone"] == zone]
    if status:
        results = [s for s in results if s["status"] == status]
    if min_temp:
        results = [s for s in results if s["temp"] >= min_temp]
    return {"count": len(results), "data": results}
```

---

## Tomorrow (Day 2): SQLAlchemy Preview

```python
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Sensor(Base):
    __tablename__ = "sensors"
    
    id = Column(Integer, primary_key=True)
    sensor_id = Column(String, unique=True)
    temperature = Column(Float)
    humidity = Column(Float)

# Coming tomorrow!
```

---

**Keep this open while coding!** 📌
