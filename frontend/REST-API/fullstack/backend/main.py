import time
import uuid
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

import models
from database import engine
from routers import auth, todos

# --- Logging Setup ---
logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# --- Rate Limiter (shared instance used in routers) ---
limiter = Limiter(key_func=get_remote_address)

# --- Create DB Tables ---
models.Base.metadata.create_all(bind=engine)

# --- App Init ---
app = FastAPI(title="Todo App with JWT", version="1.0.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID"],
)

# --- Request Logging Middleware ---
@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    duration = round((time.time() - start_time) * 1000, 2)
    logger.info(
        f"method={request.method} path={request.url.path} "
        f"status={response.status_code} duration={duration}ms request_id={request_id}"
    )
    response.headers["X-Request-ID"] = request_id
    return response

# --- Global Exception Handlers ---
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})

# --- Include Routers ---
app.include_router(auth.router)
app.include_router(todos.router)

@app.get("/")
def root():
    return {"message": "Todo App API. Visit /docs for Swagger UI."}
