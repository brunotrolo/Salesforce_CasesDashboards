"""API Gateway - Main FastAPI application for Salesforce Reports System."""

import os
import sys
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from auth import get_current_user, create_access_token
from rate_limit import RateLimitMiddleware
from cache import cache, get_cache_key

# Initialize stdlib logger for bootstrap messages
bootstrap_logger = logging.getLogger(__name__)

# Handle imports from hyphenated service directories
# Add each service's src directory as the root for that package
services_dir = Path(__file__).parent.parent.parent

# Import using importlib to load packages from src directories
import importlib.util

def _import_package(service_name: str):
    """Import a service package from its src directory."""
    src_path = services_dir / service_name / "src"
    init_path = src_path / "__init__.py"

    spec = importlib.util.spec_from_file_location(service_name, init_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {service_name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[service_name] = module
    spec.loader.exec_module(module)
    return module

# Import service packages (with graceful fallback for missing dependencies)
try:
    report_service = _import_package("report-service")
    ReportManager = report_service.ReportManager
    Report = report_service.Report
    ReportStatus = report_service.ReportStatus
    ReportMetadata = report_service.models.report.ReportMetadata
    ReportFilter = report_service.models.report.ReportFilter
except BaseException as e:
    bootstrap_logger.warning(f"Could not load report-service: {type(e).__name__}: {e}. Using mock classes for testing.")
    class ReportManager:  # noqa: E305
        """Mock ReportManager for testing when service is unavailable."""
        async def create_report(self, *args, **kwargs):
            return None
    class Report:  # noqa: E305
        """Mock Report for testing."""
        pass
    class ReportStatus:  # noqa: E305
        """Mock ReportStatus for testing."""
        DRAFT = "DRAFT"
        ACTIVE = "ACTIVE"

try:
    logging_service = _import_package("logging-service")
    StructuredLogger = logging_service.StructuredLogger
except BaseException as e:
    bootstrap_logger.warning(f"Could not load logging-service: {type(e).__name__}: {e}. Using mock StructuredLogger for testing.")
    class StructuredLogger:  # noqa: E305
        """Mock StructuredLogger for testing when service is unavailable."""
        def __init__(self, name):
            self.name = name
        def info(self, *args, **kwargs):
            pass
        def error(self, *args, **kwargs):
            pass
        def debug(self, *args, **kwargs):
            pass

# Try to import auth service, but use a stub if dependencies are missing
try:
    auth_service = _import_package("auth-service")
    AuthManager = auth_service.AuthManager
except BaseException as e:  # Catch BaseException to handle pyo3 panics
    bootstrap_logger.warning(f"Could not load auth-service: {type(e).__name__}: {e}. Using mock AuthManager for testing.")
    class AuthManager:  # noqa: E305
        """Mock AuthManager for testing when actual auth service is unavailable."""
        async def authenticate(self):
            return None
        async def verify_token(self, token):
            return True

# Try to import MCP client, but use a stub if dependencies are missing
try:
    mcp_client = _import_package("mcp-client")
    SalesforceConnector = mcp_client.SalesforceConnector
except BaseException as e:  # Catch BaseException to handle pyo3 panics
    bootstrap_logger.warning(f"Could not load mcp-client: {type(e).__name__}: {e}. Using mock SalesforceConnector for testing.")
    class SalesforceConnector:  # noqa: E305
        """Mock SalesforceConnector for testing when MCP client is unavailable."""
        async def authenticate(self):
            return None
        async def query_sobject(self, *args, **kwargs):
            return {"records": [], "totalSize": 0}

# Initialize logging
logger = StructuredLogger(__name__)

# Dependency injection
_report_manager: Optional[ReportManager] = None
_auth_manager: Optional[AuthManager] = None
_salesforce_connector: Optional[SalesforceConnector] = None


async def get_report_manager() -> ReportManager:
    """Get report manager instance."""
    return _report_manager


async def get_auth_manager() -> AuthManager:
    """Get auth manager instance."""
    return _auth_manager


async def get_salesforce_connector() -> SalesforceConnector:
    """Get Salesforce connector instance."""
    return _salesforce_connector


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    global _report_manager, _auth_manager, _salesforce_connector

    logger.info("Initializing services")

    _auth_manager = AuthManager()

    try:
        _salesforce_connector = SalesforceConnector(
            client_id=os.getenv("SF_CLIENT_ID"),
            client_secret=os.getenv("SF_CLIENT_SECRET"),
            refresh_token=os.getenv("SF_REFRESH_TOKEN"),
        )
        await _salesforce_connector.authenticate()
        logger.info("Salesforce authenticated successfully")
    except Exception as e:
        logger.error("Failed to authenticate with Salesforce")
        _salesforce_connector = None

    # Initialize report manager with Salesforce connector
    _report_manager = ReportManager(salesforce_connector=_salesforce_connector)
    logger.info("ReportManager initialized")

    yield

    # Shutdown
    if _salesforce_connector:
        await _salesforce_connector.close()
    logger.info("Services shutdown complete")


# Initialize FastAPI
app = FastAPI(
    title="Salesforce Reports API",
    description="API Gateway for Salesforce Reports System",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware (order matters - most specific first)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Request/Response Models
# ============================================================================

class ReportCreateRequest(BaseModel):
    """Request to create a new report."""
    name: str
    description: Optional[str] = None
    object_type: str
    report_type: str
    fields: List[str]
    filters: Optional[List[dict]] = None


class ReportUpdateRequest(BaseModel):
    """Request to update a report."""
    name: Optional[str] = None
    description: Optional[str] = None
    fields: Optional[List[str]] = None
    filters: Optional[List[dict]] = None


class LoginRequest(BaseModel):
    """Request to login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Response with access token."""
    access_token: str
    token_type: str = "bearer"


class ReportListResponse(BaseModel):
    """Response for listing reports."""
    success: bool
    total: int
    limit: int
    offset: int
    items: List[dict]


class ReportExecuteResponse(BaseModel):
    """Response for executing a report."""
    report_id: str
    status: str
    rows_returned: int
    execution_time_ms: int
    executed_at: str
    data: Optional[List[dict]] = None
    error: Optional[str] = None


# ============================================================================
# Authentication
# ============================================================================

@app.post("/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login endpoint - generate access token."""
    # Simple validation - in production, validate against real user store
    if not request.username or not request.password:
        raise HTTPException(
            status_code=400,
            detail="Username and password required"
        )

    # For demo: accept any non-empty credentials
    # In production: validate against LDAP, database, OAuth, etc.
    token = create_access_token(data={"sub": request.username})

    logger.info("User logged in")

    return TokenResponse(access_token=token)


@app.post("/auth/token", response_model=TokenResponse)
async def get_token(request: LoginRequest):
    """Token endpoint - generate access token."""
    return await login(request)


# ============================================================================
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api-gateway",
        "cache": "available" if cache.available else "unavailable",
    }


# ============================================================================
# Reports API
# ============================================================================

@app.get("/api/reports", response_model=ReportListResponse)
async def list_reports(
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    report_manager: ReportManager = Depends(get_report_manager),
):
    """List all reports with optional filtering by status."""
    try:
        # Check cache first
        cache_key = get_cache_key("reports", status or "all", limit, offset)
        cached_result = cache.get(cache_key)
        if cached_result:
            logger.info("Listing reports (from cache)")
            return cached_result

        logger.info("Listing reports")

        report_status = None
        if status:
            report_status = ReportStatus[status.upper()]

        result = await report_manager.list_reports(
            status=report_status,
            limit=limit,
            offset=offset,
        )

        # Cache the result
        cache.set(cache_key, result.model_dump() if hasattr(result, 'model_dump') else result)

        return result
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid report status")
    except Exception as e:
        logger.error("Error listing reports")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports")
async def create_report(
    request: ReportCreateRequest,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Create a new report."""
    try:
        logger.info("Creating report")

        # Convert filter dicts to ReportFilter objects
        report_filters = []
        if request.filters:
            for f in request.filters:
                try:
                    report_filters.append(ReportFilter(**f))
                except Exception:
                    pass

        report = Report(
            id=f"r:{int(datetime.utcnow().timestamp() * 1000)}",
            name=request.name,
            description=request.description,
            object_type=request.object_type,
            report_type=request.report_type,
            fields=request.fields,
            filters=report_filters,
            metadata=ReportMetadata(
                created_by="system",
                created_at=datetime.utcnow(),
            ),
        )

        result = await report_manager.create_report(
            report=report,
            user_id="system",
        )

        return result
    except Exception as e:
        logger.error("Error creating report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/reports/{report_id}")
async def get_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Get a specific report by ID."""
    try:
        logger.info("Getting report")

        report = await report_manager.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return report.model_dump()
    except Exception as e:
        logger.error("Error getting report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/api/reports/{report_id}")
async def update_report(
    report_id: str,
    request: ReportUpdateRequest,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Update a report."""
    try:
        logger.info("Updating report")

        updates = request.model_dump(exclude_none=True)
        result = await report_manager.update_report(
            report_id=report_id,
            updates=updates,
            user_id="system",
        )

        return result
    except Exception as e:
        logger.error("Error updating report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/reports/{report_id}")
async def delete_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Delete a report (soft delete - archives it)."""
    try:
        logger.info("Deleting report")

        result = await report_manager.delete_report(report_id)
        return result
    except Exception as e:
        logger.error("Error deleting report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/execute", response_model=ReportExecuteResponse)
async def execute_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
    salesforce_connector: SalesforceConnector = Depends(get_salesforce_connector),
):
    """Execute a report and return results."""
    try:
        logger.info("Executing report")

        # For now, use simulated execution
        # TODO: Integrate with Salesforce MCP for real data
        result = await report_manager.execute_report(report_id)

        return {
            "report_id": result.report_id,
            "status": result.status,
            "rows_returned": result.rows_returned,
            "execution_time_ms": result.execution_time_ms,
            "executed_at": result.executed_at.isoformat(),
            "data": result.data,
            "error": result.error,
        }
    except Exception as e:
        logger.error("Error executing report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/activate")
async def activate_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Activate a report."""
    try:
        logger.info("Activating report")

        result = await report_manager.activate_report(report_id, user_id="system")
        return result
    except Exception as e:
        logger.error("Error activating report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/schedule")
async def schedule_report(
    report_id: str,
    cron: str = Query(...),
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Schedule a report for regular execution."""
    try:
        logger.info("Scheduling report")

        result = await report_manager.schedule_report(report_id, cron, user_id="system")
        return result
    except Exception as e:
        logger.error("Error scheduling report")
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/pause")
async def pause_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Pause a scheduled report."""
    try:
        logger.info("Pausing report")

        result = await report_manager.pause_report(report_id, user_id="system")
        return result
    except Exception as e:
        logger.error("Error pausing report")
        raise HTTPException(status_code=500, detail="Internal server error")


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("API_PORT", 3000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=os.getenv("ENV", "dev") == "dev",
        log_level="info",
    )
