import uuid
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from .logger import StructuredLogger, LogCategory
from .context import RequestContext


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for automatic request/response logging.
    Injects trace_id and correlation_id into all requests.
    """

    TRACE_ID_HEADER = "X-Trace-ID"
    CORRELATION_ID_HEADER = "X-Correlation-ID"

    def __init__(self, app, logger: StructuredLogger):
        super().__init__(app)
        self.logger = logger

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request/response with logging and tracing."""
        trace_id = request.headers.get(
            self.TRACE_ID_HEADER.lower(),
            str(uuid.uuid4())
        )
        correlation_id = request.headers.get(
            self.CORRELATION_ID_HEADER.lower(),
            trace_id
        )

        request.state.trace_id = trace_id
        request.state.correlation_id = correlation_id

        RequestContext.set_trace_id(trace_id)
        RequestContext.set_correlation_id(correlation_id)

        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start_time) * 1000)

            self.logger.info(
                f"{request.method} {request.url.path}",
                category=LogCategory.API_REQUEST,
                trace_id=trace_id,
                correlation_id=correlation_id,
                context={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "query_params": dict(request.query_params),
                },
                duration_ms=duration_ms,
            )

            response.headers[self.TRACE_ID_HEADER] = trace_id
            response.headers[self.CORRELATION_ID_HEADER] = correlation_id

            RequestContext.clear()

            return response

        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            RequestContext.clear()
            self.logger.error(
                f"Request failed: {request.method} {request.url.path}",
                error=e,
                trace_id=trace_id,
                correlation_id=correlation_id,
                context={
                    "method": request.method,
                    "path": request.url.path,
                    "query_params": dict(request.query_params),
                },
            )
            raise

