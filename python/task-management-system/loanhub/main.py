from fastapi import FastAPI, Request, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session
import logging

from .config import settings
from .database import engine, get_db, SessionLocal
from .models import db_models
from .models.enums import UserRole
from .routers import auth_router, loan_router, admin_router, analytics_router
from .middleware.logging_middleware import LoggingMiddleware
from .exceptions.custom_exceptions import LoanHubException
from .services.user_service import pwd_context

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("loanhub")

app = FastAPI(title=settings.APP_NAME)

# Add Middleware
app.add_middleware(LoggingMiddleware)

# Include Routers
app.include_router(auth_router.router)
app.include_router(loan_router.router)
app.include_router(admin_router.router)
app.include_router(analytics_router.router)

@app.on_event("startup")
def startup_event():
    """
    On startup, create tables (if not using alembic) and seed admin.
    (Requirement 11)
    """
    # Create tables (simpler than running alembic in this script)
    db_models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if admin exists
        admin = db.query(db_models.User).filter(db_models.User.username == settings.ADMIN_USERNAME).first()
        if not admin:
            admin_user = db_models.User(
                username=settings.ADMIN_USERNAME,
                email=settings.ADMIN_EMAIL,
                password=pwd_context.hash(settings.ADMIN_PASSWORD),
                phone="0000000000",
                monthly_income=0,
                role=UserRole.ADMIN
            )
            db.add(admin_user)
            db.commit()
            logger.info("Admin user seeded successfully")
        else:
            logger.info("Admin user already exists")
    finally:
        db.close()

@app.exception_handler(LoanHubException)
async def custom_exception_handler(request: Request, exc: LoanHubException):
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail
    )

@app.get("/health", tags=["Utility"])
def health_check(db: Session = Depends(get_db)):
    """
    Raw SQL health check (Requirement 4).
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("loanhub.main:app", host="0.0.0.0", port=8000, reload=True)
