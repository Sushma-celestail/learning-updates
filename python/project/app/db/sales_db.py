from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

engine_sales = create_engine(settings.SALES_DB_URL)
SessionLocalSales = sessionmaker(bind=engine_sales)
BaseSales = declarative_base()