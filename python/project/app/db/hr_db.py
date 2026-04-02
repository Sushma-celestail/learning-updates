from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine_hr = create_engine(settings.HR_DB_URL)
SessionLocalHR = sessionmaker(bind=engine_hr)
BaseHR = declarative_base() 