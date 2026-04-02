from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "LoanHub"
    DEBUG: bool = True
    DATABASE_URL: str
    LOG_LEVEL: str = "INFO"
    POOL_SIZE: int = 5
    MAX_OVERFLOW: int = 10
    ADMIN_USERNAME: str
    ADMIN_PASSWORD: str
    ADMIN_EMAIL: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
