"""
database.py — SQLAlchemy engine + session configuration

The single place where the app connects to PostgreSQL.
Everything else imports from here so there's ONE connection string.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# .env holds the connection string (never hardcode secrets in code)
from dotenv import load_dotenv
import os

load_dotenv()

# Postgres connection string format:
#   postgresql+psycopg2://USER:PASSWORD@HOST:PORT/DATABASE_NAME
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/citysense",
)

# `pool_pre_ping=True` checks the connection before each request —
# prevents "server closed connection" errors after Postgres restarts.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# A "session" is a workspace for all operations on the database.
# You read, write, and query within a session, then commit.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# This is the BASE CLASS that all our models inherit from.
# In SQLAlchemy 2.0 you define your own DeclarativeBase.
class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency: gives each request its own session.

    The `yield` pattern means the session is created on request start
    and closed (committed or rolled back) when the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()