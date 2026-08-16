# Logging Service

Centralized structured logging service providing JSON-based logs with trace_id and correlation_id for production observability.

## Features

- **Structured JSON Logging**: Every log entry is a complete JSON object
- **Trace ID Tracking**: Unique ID per request for full request tracing
- **Correlation ID**: Track cross-service communication flows
- **Log Categories**: Organized logging by operation type (API, MCP, Cache, Security, etc.)
- **Performance Metrics**: Built-in duration tracking and slow query detection
- **ELK Stack Compatible**: Format optimized for Elasticsearch + Kibana
- **Middleware Integration**: FastAPI middleware for automatic request/response logging

## Usage

### Basic Logger

```python
from logging_service import StructuredLogger, LogLevel, LogCategory

logger = StructuredLogger(
    service_name="report-service",
    log_level=LogLevel.DEBUG,
    log_file="logs/app.log"
)

# Simple info log
logger.info("Report created", context={"report_id": "r:123"})

# Log with trace context
logger.info(
    "Processing report",
    trace_id="trace-abc123",
    correlation_id="corr-xyz789",
    context={"user_id": "u:456"},
    duration_ms=245
)
```

### Log Categories

| Category | Level | Use Case |
|----------|-------|----------|
| API_REQUEST | INFO | Request/response logging |
| MCP_OPERATION | DEBUG | Salesforce API calls |
| CACHE_OPERATION | DEBUG | Redis hit/miss tracking |
| SECURITY | WARN | Unauthorized access attempts |
| PERFORMANCE | INFO | Slow queries (>500ms) |
| ERROR | ERROR | Exceptions and failures |
| DATABASE | DEBUG | Database operations |
| SYSTEM | INFO/DEBUG | General system events |

### FastAPI Integration

```python
from fastapi import FastAPI
from logging_service import StructuredLogger, LoggingMiddleware

app = FastAPI()
logger = StructuredLogger("my-service")
app.add_middleware(LoggingMiddleware, logger=logger)

@app.get("/api/reports")
async def get_reports(request: Request):
    # Trace ID and correlation ID automatically available
    trace_id = request.state.trace_id
    correlation_id = request.state.correlation_id
    return {"reports": []}
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=services/logging-service
```

## Production

All logs are JSON-formatted and compatible with ELK Stack (Elasticsearch + Kibana) for centralized monitoring and debugging.
