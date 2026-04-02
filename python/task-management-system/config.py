"""
config.py
---------
Central configuration module using pydantic-settings.

DAY 3 CHANGE: Added DATABASE_URL for Supabase PostgreSQL connection.
Everything else remains the same as Day 2.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    # Application metadata
    app_name: str = Field(default="TaskAPI", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # DAY 3: Database connection URL for Supabase PostgreSQL
    # Format: postgresql://user:password@host:5432/dbname
    database_url: str = Field(
        default="postgresql://postgres:password@localhost:5432/postgres",
        env="DATABASE_URL"
    )

    # Security
    secret_key: str = Field(default="changeme", env="SECRET_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Single shared instance used throughout the app
settings = Settings()
