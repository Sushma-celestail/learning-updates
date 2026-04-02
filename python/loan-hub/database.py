import logging
import time
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings
from decorators.retry import retry

logger = logging.getLogger(__name__)

import os

# Base class for SQLAlchemy models
Base = declarative_base()

# Engine setup with connection pooling
if os.getenv("TEST_MODE") == "true":
    engine = create_engine(
        "sqlite:///./test.db",
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.POOL_SIZE,
        max_overflow=settings.MAX_OVERFLOW,
        pool_pre_ping=True
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from sqlalchemy import text

@retry(max_attempts=3)
def verify_db_connection():
    """Verify database connection on startup with retry logic."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            logger.info("Database connection verified successfully.")
            return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise

def get_db():
    """Dependency for database session management."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
