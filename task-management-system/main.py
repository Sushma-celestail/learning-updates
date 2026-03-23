"""
main.py
-------
Application entry point. This file:
  1. Creates the FastAPI app instance
  2. Configures structured logging
  3. Registers middleware
  4. Includes routers
  5. Registers global exception handlers
  6. Defines startup/shutdown lifecycle events
"""

import logging
import logging.config
import os
from contextlib import asynccontextmanager

import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

# ── DB Imports (PostgreSQL + MongoDB only) ────────────────────────────────────
from database.mongodb import connect_mongo, close_mongo
from database.postgresql import engine as pg_engine, Base as PgBase

from config import settings
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


# ── Lifespan (startup/shutdown) ───────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup: connect all databases.
    Shutdown: gracefully close all connections.

    Using lifespan instead of deprecated @app.on_event("startup").
    """

    # ── Startup ───────────────────────────────────────────────
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")

    # 1. MongoDB — connect client
    try:
        await connect_mongo()
        logger.info("✅ MongoDB connected")
    except Exception as e:
        logger.error(f"❌ MongoDB connection failed: {e}")
        raise

    # 2. PostgreSQL — create tables if not exists
    try:
        async with pg_engine.begin() as conn:
            await conn.run_sync(PgBase.metadata.create_all)
        logger.info("✅ PostgreSQL connected & tables ready")
    except Exception as e:
        logger.error(f"❌ PostgreSQL connection failed: {e}")
        raise

    logger.info(f"Debug mode: {settings.debug}")

    yield  # ← App runs here

    # ── Shutdown ──────────────────────────────────────────────
    logger.info(f"{settings.app_name} shutting down...")

    await close_mongo()
    logger.info("🔌 MongoDB disconnected")

    await pg_engine.dispose()
    logger.info("🔌 PostgreSQL disconnected")

    logger.info("👋 All DB connections closed. Bye!")


# ── FastAPI App ───────────────────────────────────────────────────────────────

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Production-style Task Management REST API",
    lifespan=lifespan,
)


# ── Middleware ────────────────────────────────────────────────────────────────

app.add_middleware(RequestLoggingMiddleware)


# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(user_router.router)
app.include_router(task_router.router)


# ── Global Exception Handlers ─────────────────────────────────────────────────

def error_response(error_name: str, message: str, status_code: int) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "error": error_name,
            "message": message,
            "status_code": status_code,
        },
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
        field = " → ".join(str(loc) for loc in error["loc"])
        messages.append(f"{field}: {error['msg']}")
    message = "; ".join(messages)
    logger.warning(f"ValidationError: {message}")
    return error_response("ValidationError", message, status.HTTP_422_UNPROCESSABLE_ENTITY)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return error_response(
        "InternalServerError",
        "An unexpected error occurred",
        status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


# ── Health check ──────────────────────────────────────────────────────────────

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "app": settings.app_name, "version": settings.app_version}


# ── Dev runner ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )