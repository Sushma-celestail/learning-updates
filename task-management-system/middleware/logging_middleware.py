"""
middleware/logging_middleware.py
--------------------------------
Starlette middleware that logs every HTTP request and response.

WHAT IS MIDDLEWARE?
Middleware wraps around every request BEFORE it reaches your route handler
and every response AFTER your route handler returns. Think of it like:

  Request → [Middleware start] → Router → Service → Repo
                                                       ↓
  Response ← [Middleware end]  ← Router ← Service ← Repo

SRP: Logging is a cross-cutting concern — it applies to every endpoint.
     Putting it in middleware means NO logging code in routers or services
     (other than domain-specific messages).

HOW IT WORKS:
  1. Record the start time when the request arrives
  2. Call await call_next(request) to let FastAPI handle the request normally
  3. After the response is ready, calculate elapsed milliseconds
  4. Log the result in the required format
"""

import time
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("middleware")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Logs every incoming request with:
    - HTTP method and path
    - Response status code
    - Time taken in milliseconds

    Format matches the project spec:
    2026-03-20 14:30:00 - INFO - task_router - POST /tasks | 201 | 15ms
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()  # high-resolution timer

        # Let FastAPI process the request normally
        response = await call_next(request)

        # Calculate elapsed time in milliseconds
        elapsed_ms = round((time.perf_counter() - start_time) * 1000)

        logger.info(
            f"{request.method} {request.url.path} | "
            f"{response.status_code} | "
            f"{elapsed_ms}ms"
        )

        return response
