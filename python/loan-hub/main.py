import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from config import settings
from database import engine, Base, get_db, verify_db_connection
from models.db_models import User
from models.enums import UserRole
from services.user_service import UserService
from models.schemas import UserCreate

from routers import auth_router, loan_router, admin_router, analytics_router
from middleware.logging_middleware import LoggingMiddleware
from exceptions.custom_exceptions import (
    LoanHubException, 
    loanhub_exception_handler, 
    validation_exception_handler
)

# Setup logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info("Application starting up...")
    
    # Requirement 1: Database connection verification with @retry
    verify_db_connection()
    
    # Requirement 11: Admin seeding
    db = next(get_db())
    try:
        user_service = UserService(db)
        try:
            user_service.get_user_by_username(settings.ADMIN_USERNAME)
            logger.info("Admin user already exists")
        except Exception:
            # Seed admin
            admin_data = UserCreate(
                username=settings.ADMIN_USERNAME,
                password=settings.ADMIN_PASSWORD,
                email=settings.ADMIN_EMAIL,
                phone="0000000000",
                monthly_income=1000000
            )
            admin = user_service.register_user(admin_data)
            admin.role = UserRole.ADMIN
            db.commit()
            logger.info("Admin user seeded successfully")
    finally:
        db.close()
        
    yield
    # Shutdown logic
    logger.info("Application shutting down...")

app = FastAPI(
    title=settings.APP_NAME,
    lifespan=lifespan
)

# Requirement 9: Logging Middleware
app.add_middleware(LoggingMiddleware)

# Exception Handlers
app.add_exception_handler(LoanHubException, loanhub_exception_handler)
app.add_exception_handler(Exception, validation_exception_handler)

# Routers
app.include_router(auth_router.router)
app.include_router(loan_router.router)
app.include_router(admin_router.router)
app.include_router(analytics_router.router)

from sqlalchemy import text

@app.get("/health", tags=["utility"])
def health_check():
    """Requirement 4: Raw SQL health check."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
