from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """
    Project configuration using Pydantic Settings.
    Loads variables from .env file.
    """
    APP_NAME: str = "LoanHub"
    DEBUG: bool = True
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    
    # Database pooling
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    
    # Admin credentials
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_EMAIL: str

    # Load from .env file
    model_config = SettingsConfigDict(env_file=str(Path(__file__).parent / ".env"))

# Instantiate settings
settings = Settings()
