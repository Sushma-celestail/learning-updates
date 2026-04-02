"""
main.py
-------
Application entry point.

DAY 3 CHANGES:
  - Import Base and engine from database.py
  - Create all tables on startup (Base.metadata.create_all)
  - Everything else identical to Day 2
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from config import settings
from database import engine, Base
from routers import user_router, task_router
from middleware.logging_middleware import RequestLoggingMiddleware
from exceptions.custom_exceptions import (
    UserNotFoundError,
    TaskNotFoundError,
    DuplicateUserError,
    InvalidCredentialsError,
    StorageError,
)


# ── Logging Setup ─────────────────────────────────────────────────────────────

def setup_logging() -> None:
    os.makedirs(os.path.dirname(settings.log_file), exist_ok=True)
    log_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "handlers": {
            "console_handler": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "stream": "ext://sys.stdout",
            },
            "file_handler": {
                "class": "logging.FileHandler",
                "formatter": "standard",
                "filename": settings.log_file,
                "mode": "a",
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": settings.log_level,
            "handlers": ["console_handler", "file_handler"],
        },
    }
    logging.config.dictConfig(log_config)


setup_logging()
logger = logging.getLogger(__name__)


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    DAY 3: Create all database tables on startup.
    Base.metadata.create_all() looks at all models that inherit from Base
    (UserModel, TaskModel) and creates their tables if they don't exist.
    This is the fallback — Alembic migrations are the proper way.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Connecting to database...")

    # Create tables if they don't exist (safe to run multiple times)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready")

    yield
    logger.info(f"{settings.app_name} shutting down")


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Task Management API — Day 3 with SQLAlchemy + Supabase",
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(user_router.router)
app.include_router(task_router.router)


# ── Exception Handlers ────────────────────────────────────────────────────────

def error_response(error_name: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": error_name, "message": message, "status_code": status_code},
    )


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    logger.error(f"TaskNotFoundError: {exc.message}")
    return error_response("TaskNotFoundError", exc.message, status.HTTP_404_NOT_FOUND)


@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(request: Request, exc: UserNotFoundError):
    logger.error(f"UserNotFoundError: {exc.message}")
    return error_response("UserNotFoundError", exc.message, status.HTTP_404_NOT_FOUND)


@app.exception_handler(DuplicateUserError)
async def duplicate_user_handler(request: Request, exc: DuplicateUserError):
    logger.warning(f"DuplicateUserError: {exc.message}")
    return error_response("DuplicateUserError", exc.message, status.HTTP_409_CONFLICT)


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    logger.warning(f"InvalidCredentialsError: {exc.message}")
    return error_response("InvalidCredentialsError", exc.message, status.HTTP_401_UNAUTHORIZED)


@app.exception_handler(StorageError)
async def storage_error_handler(request: Request, exc: StorageError):
    logger.error(f"StorageError: {exc.message}")
    return error_response("StorageError", exc.message, status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    messages = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"])
        messages.append(f"{field}: {error['msg']}")
    message = "; ".join(messages)
    logger.warning(f"ValidationError: {message}")
    return error_response("ValidationError", message, status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return error_response("InternalServerError", "An unexpected error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)


# ── Root + Health ─────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def root():
    return {"app": settings.app_name, "version": settings.app_version, "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


# ── Run ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
