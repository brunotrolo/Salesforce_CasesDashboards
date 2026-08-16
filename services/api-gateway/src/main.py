"""API Gateway - Main FastAPI application for Salesforce Reports System."""

import os
import logging
from contextlib import asynccontextmanager
from typing import Optional, List
from datetime import datetime

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from report_service.src.report_manager import ReportManager
from report_service.src.models.report import Report, ReportStatus
from auth_service.src.auth_manager import AuthManager
from logging_service.src.logger import StructuredLogger
from mcp_client.src.salesforce_connector import SalesforceConnector

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

    logger.info("Initializing services", extra={"service": "api-gateway"})

    _auth_manager = AuthManager()

    try:
        _salesforce_connector = SalesforceConnector(
            client_id=os.getenv("SF_CLIENT_ID"),
            client_secret=os.getenv("SF_CLIENT_SECRET"),
            refresh_token=os.getenv("SF_REFRESH_TOKEN"),
        )
        await _salesforce_connector.authenticate()
        logger.info("Salesforce authenticated successfully", extra={"service": "api-gateway"})
    except Exception as e:
        logger.error("Failed to authenticate with Salesforce", extra={"error": str(e)})
        _salesforce_connector = None

    # Initialize report manager with Salesforce connector
    _report_manager = ReportManager(salesforce_connector=_salesforce_connector)
    logger.info("ReportManager initialized", extra={"has_salesforce": _salesforce_connector is not None})

    yield

    # Shutdown
    if _salesforce_connector:
        await _salesforce_connector.close()
    logger.info("Services shutdown complete", extra={"service": "api-gateway"})


# Initialize FastAPI
app = FastAPI(
    title="Salesforce Reports API",
    description="API Gateway for Salesforce Reports System",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
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
# Health Check
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "api-gateway",
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
        logger.info(
            "Listing reports",
            extra={
                "action": "list_reports",
                "status": status,
                "limit": limit,
                "offset": offset,
            },
        )

        report_status = None
        if status:
            report_status = ReportStatus[status.upper()]

        result = await report_manager.list_reports(
            status=report_status,
            limit=limit,
            offset=offset,
        )

        return result
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid report status")
    except Exception as e:
        logger.error("Error listing reports", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports")
async def create_report(
    request: ReportCreateRequest,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Create a new report."""
    try:
        logger.info("Creating report", extra={"action": "create_report", "name": request.name})

        report = Report(
            id=f"r:{datetime.utcnow().timestamp()}",
            name=request.name,
            description=request.description,
            object_type=request.object_type,
            report_type=request.report_type,
            fields=request.fields,
            filters=request.filters or [],
        )

        result = await report_manager.create_report(
            report=report,
            user_id="system",
        )

        return result
    except Exception as e:
        logger.error("Error creating report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/reports/{report_id}")
async def get_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Get a specific report by ID."""
    try:
        logger.info("Getting report", extra={"action": "get_report", "report_id": report_id})

        report = await report_manager.get_report(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")

        return report.model_dump()
    except Exception as e:
        logger.error("Error getting report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.put("/api/reports/{report_id}")
async def update_report(
    report_id: str,
    request: ReportUpdateRequest,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Update a report."""
    try:
        logger.info("Updating report", extra={"action": "update_report", "report_id": report_id})

        updates = request.model_dump(exclude_none=True)
        result = await report_manager.update_report(
            report_id=report_id,
            updates=updates,
            user_id="system",
        )

        return result
    except Exception as e:
        logger.error("Error updating report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/api/reports/{report_id}")
async def delete_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Delete a report (soft delete - archives it)."""
    try:
        logger.info("Deleting report", extra={"action": "delete_report", "report_id": report_id})

        result = await report_manager.delete_report(report_id)
        return result
    except Exception as e:
        logger.error("Error deleting report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/execute", response_model=ReportExecuteResponse)
async def execute_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
    salesforce_connector: SalesforceConnector = Depends(get_salesforce_connector),
):
    """Execute a report and return results."""
    try:
        logger.info("Executing report", extra={"action": "execute_report", "report_id": report_id})

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
        logger.error("Error executing report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/activate")
async def activate_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Activate a report."""
    try:
        logger.info("Activating report", extra={"action": "activate_report", "report_id": report_id})

        result = await report_manager.activate_report(report_id, user_id="system")
        return result
    except Exception as e:
        logger.error("Error activating report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/schedule")
async def schedule_report(
    report_id: str,
    cron: str = Query(...),
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Schedule a report for regular execution."""
    try:
        logger.info(
            "Scheduling report",
            extra={"action": "schedule_report", "report_id": report_id, "cron": cron},
        )

        result = await report_manager.schedule_report(report_id, cron, user_id="system")
        return result
    except Exception as e:
        logger.error("Error scheduling report", extra={"error": str(e)})
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/reports/{report_id}/pause")
async def pause_report(
    report_id: str,
    report_manager: ReportManager = Depends(get_report_manager),
):
    """Pause a scheduled report."""
    try:
        logger.info("Pausing report", extra={"action": "pause_report", "report_id": report_id})

        result = await report_manager.pause_report(report_id, user_id="system")
        return result
    except Exception as e:
        logger.error("Error pausing report", extra={"error": str(e)})
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
