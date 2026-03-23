"""
config.py
---------
Central configuration module using pydantic-settings.

WHY: Instead of hardcoding values like file paths or app names,
we read them from a .env file. This follows the 12-Factor App principle:
configuration belongs in the environment, not in code.

pydantic-settings automatically reads the .env file and validates
each value against the type annotations (str, bool, int, etc.).
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.

    BaseSettings from pydantic-settings:
    - Reads values from .env automatically
    - Validates types (e.g., DEBUG must be bool)
    - Raises an error at startup if a required variable is missing
    """

    # Application metadata
    app_name: str = Field(default="TaskManagementAPI", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=False, env="DEBUG")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/app.log", env="LOG_FILE")

    # Storage paths
    tasks_file: str = Field(default="data/tasks.json", env="TASKS_FILE")
    users_file: str = Field(default="data/users.json", env="USERS_FILE")

    # Security
    secret_key: str = Field(default="changeme", env="SECRET_KEY")

    class Config:
        # Tell pydantic-settings where to find the .env file
        env_file = ".env"
        env_file_encoding = "utf-8"


# Create a single shared instance used throughout the app
# This is the "singleton" pattern: one settings object, imported everywhere
settings = Settings()
