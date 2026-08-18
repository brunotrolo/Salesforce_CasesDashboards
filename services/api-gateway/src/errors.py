"""Domain exceptions for the API Gateway."""

from typing import Optional


class GatewayError(Exception):
    """Base class for API Gateway domain errors."""

    status_code: int = 500
    code: str = "INTERNAL_ERROR"

    def __init__(self, message: str, detail: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.detail = detail


class ReportNotFoundError(GatewayError):
    """Raised when a requested report does not exist."""

    status_code = 404
    code = "REPORT_NOT_FOUND"


class ReportValidationError(GatewayError):
    """Raised when report data fails validation."""

    status_code = 422
    code = "REPORT_VALIDATION_ERROR"


class InvalidStatusError(GatewayError):
    """Raised when an invalid report status filter is provided."""

    status_code = 400
    code = "INVALID_STATUS"


class ExternalServiceError(GatewayError):
    """Raised when a downstream service (Salesforce, cache) fails."""

    status_code = 502
    code = "EXTERNAL_SERVICE_ERROR"


class UnauthorizedError(GatewayError):
    """Raised when authentication or authorization fails."""

    status_code = 401
    code = "UNAUTHORIZED"


class ForbiddenError(GatewayError):
    """Raised when the user lacks permission for an operation."""

    status_code = 403
    code = "FORBIDDEN"