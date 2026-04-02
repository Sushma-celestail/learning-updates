"""
database.py
-----------
SQLAlchemy database setup. This is the ONLY file that knows about the
database connection details.

THREE THINGS THIS FILE PROVIDES:
  1. engine       — The connection to Supabase PostgreSQL
  2. SessionLocal — A factory that creates database sessions
  3. Base         — Parent class for all SQLAlchemy table models
  4. get_db()     — FastAPI dependency that gives each request its own session

WHY CONNECTION POOLING?
  Without pooling, every request opens and closes a new DB connection.
  That's slow (100ms+ overhead per request) and wastes DB resources.
  With pool_size=5, SQLAlchemy keeps 5 connections open and reuses them.

  pool_pre_ping=True: Before using a connection from the pool, test it
  with a quick "SELECT 1". If the connection dropped (e.g. Supabase
  restarted), get a fresh one. Prevents "connection closed" errors.

WHY get_db() AS A DEPENDENCY?
  Each HTTP request gets its own session. The session is:
    - Created when the request arrives (before the endpoint runs)
    - Committed if everything succeeded
    - Rolled back if an exception occurred
    - Closed when the response is sent (after the endpoint finishes)
  This is the "unit of work" pattern — one request = one transaction.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config import settings


# ── Engine ────────────────────────────────────────────────────────────────────

engine = create_engine(
    settings.database_url,
    pool_size=5,           # Keep 5 connections open in the pool
    max_overflow=10,       # Allow up to 10 extra connections under heavy load
    pool_pre_ping=True,    # Test connections before using them
    echo=settings.debug,   # Log SQL queries in debug mode (useful for learning)
)


# ── Session Factory ───────────────────────────────────────────────────────────

SessionLocal = sessionmaker(
    autocommit=False,   # We control commits manually (db.commit())
    autoflush=False,    # We control flushes manually
    bind=engine,
)


# ── Declarative Base ──────────────────────────────────────────────────────────

class Base(DeclarativeBase):
    """
    Parent class for all SQLAlchemy ORM models.
    All table definitions in db_models.py inherit from this.
    Base.metadata.create_all(engine) creates all tables at startup.
    """
    pass


# ── FastAPI Dependency ────────────────────────────────────────────────────────

def get_db():
    """
    FastAPI dependency that provides a database session per request.

    Usage in a router:
        @router.get("/tasks")
        def list_tasks(db: Session = Depends(get_db)):
            ...

    The 'yield' makes this a context manager:
      - Code BEFORE yield runs before the endpoint
      - Code AFTER yield runs after the endpoint (cleanup)
      - finally: ensures the session is ALWAYS closed, even on errors
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
