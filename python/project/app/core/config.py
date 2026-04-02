import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    HR_DB_URL = os.getenv("HR_DB_URL")
    SALES_DB_URL = os.getenv("SALES_DB_URL")
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

settings = Settings()