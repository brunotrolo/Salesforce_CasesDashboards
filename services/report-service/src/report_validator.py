from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from .models.report import Report, ReportFilter, ReportAggregation


@dataclass
class ValidationError:
    """Validation error details."""
    field: str
    message: str
    code: str


@dataclass
class ValidationResult:
    """Result of report validation."""
    is_valid: bool
    errors: List[ValidationError]

    def add_error(self, field: str, message: str, code: str = "VALIDATION_ERROR"):
        """Add validation error."""
        self.errors.append(ValidationError(field, message, code))

    def __bool__(self) -> bool:
        return self.is_valid


class ReportValidator:
    """Validates report configurations."""

    # Valid Salesforce objects
    VALID_OBJECTS = {
        "Account", "Case", "Contact", "Lead", "Opportunity",
        "Order", "Product", "Quote", "Task", "Event",
    }

    # Valid filter operators
    VALID_OPERATORS = {
        "eq", "ne", "gt", "lt", "gte", "lte", "in", "contains",
        "startswith", "endswith", "between", "is_null",
    }

    # Valid aggregation functions
    VALID_FUNCTIONS = {
        "sum", "avg", "count", "min", "max", "count_distinct",
    }

    # Reserved field names (cannot be selected directly)
    RESERVED_FIELDS = {"Id", "CreatedDate", "LastModifiedDate"}

    @classmethod
    def validate(cls, report: Report) -> ValidationResult:
        """Validate complete report configuration."""
        result = ValidationResult(is_valid=True, errors=[])

        # Basic validations
        cls._validate_basic(report, result)
        if not result:
            return result

        # Object and field validations
        cls._validate_object(report, result)
        cls._validate_fields(report, result)

        # Filter validations
        cls._validate_filters(report, result)

        # Aggregation validations
        cls._validate_aggregations(report, result)

        # Schedule validations
        cls._validate_schedule(report, result)

        result.is_valid = len(result.errors) == 0
        return result

    @classmethod
    def _validate_basic(cls, report: Report, result: ValidationResult) -> None:
        """Validate basic report properties."""
        if not report.name or len(report.name.strip()) == 0:
            result.add_error("name", "Report name is required", "MISSING_NAME")

        if report.name and len(report.name) > 255:
            result.add_error("name", "Report name must be <= 255 characters", "NAME_TOO_LONG")

        if not report.id or len(report.id.strip()) == 0:
            result.add_error("id", "Report ID is required", "MISSING_ID")

        if len(report.fields) == 0:
            result.add_error("fields", "At least one field is required", "NO_FIELDS")

        if len(report.fields) > 100:
            result.add_error("fields", "Maximum 100 fields allowed", "TOO_MANY_FIELDS")

    @classmethod
    def _validate_object(cls, report: Report, result: ValidationResult) -> None:
        """Validate Salesforce object type."""
        if report.object_type not in cls.VALID_OBJECTS:
            result.add_error(
                "object_type",
                f"Invalid object type. Valid types: {', '.join(sorted(cls.VALID_OBJECTS))}",
                "INVALID_OBJECT_TYPE"
            )

    @classmethod
    def _validate_fields(cls, report: Report, result: ValidationResult) -> None:
        """Validate report fields."""
        if not report.fields:
            return

        for field in report.fields:
            if not field or len(field.strip()) == 0:
                result.add_error("fields", "Field name cannot be empty", "EMPTY_FIELD")
                continue

            if not cls._is_valid_field_name(field):
                result.add_error(
                    "fields",
                    f"Invalid field name: {field}",
                    "INVALID_FIELD_NAME"
                )

    @classmethod
    def _validate_filters(cls, report: Report, result: ValidationResult) -> None:
        """Validate report filters."""
        for idx, filter_obj in enumerate(report.filters):
            if not cls._is_valid_field_name(filter_obj.field):
                result.add_error(
                    f"filters[{idx}].field",
                    f"Invalid filter field: {filter_obj.field}",
                    "INVALID_FILTER_FIELD"
                )

            if filter_obj.operator not in cls.VALID_OPERATORS:
                result.add_error(
                    f"filters[{idx}].operator",
                    f"Invalid operator: {filter_obj.operator}. Valid: {', '.join(sorted(cls.VALID_OPERATORS))}",
                    "INVALID_OPERATOR"
                )

            if filter_obj.value is None and filter_obj.operator != "is_null":
                result.add_error(
                    f"filters[{idx}].value",
                    "Filter value cannot be null",
                    "NULL_FILTER_VALUE"
                )

    @classmethod
    def _validate_aggregations(cls, report: Report, result: ValidationResult) -> None:
        """Validate report aggregations."""
        for idx, agg in enumerate(report.aggregations):
            if not cls._is_valid_field_name(agg.field):
                result.add_error(
                    f"aggregations[{idx}].field",
                    f"Invalid aggregation field: {agg.field}",
                    "INVALID_AGG_FIELD"
                )

            if agg.function not in cls.VALID_FUNCTIONS:
                result.add_error(
                    f"aggregations[{idx}].function",
                    f"Invalid function: {agg.function}. Valid: {', '.join(sorted(cls.VALID_FUNCTIONS))}",
                    "INVALID_FUNCTION"
                )

    @classmethod
    def _validate_schedule(cls, report: Report, result: ValidationResult) -> None:
        """Validate report schedule."""
        if report.schedule.enabled:
            if not report.schedule.cron:
                result.add_error(
                    "schedule.cron",
                    "CRON expression is required when schedule is enabled",
                    "MISSING_CRON"
                )

            if report.schedule.max_rows < 1 or report.schedule.max_rows > 1000000:
                result.add_error(
                    "schedule.max_rows",
                    "max_rows must be between 1 and 1,000,000",
                    "INVALID_MAX_ROWS"
                )

    @classmethod
    def _is_valid_field_name(cls, field: str) -> bool:
        """Check if field name is valid."""
        if not field:
            return False

        # Field names should be alphanumeric with underscores
        # Support dot notation for relationships (e.g., Owner.Name)
        parts = field.split(".")
        for part in parts:
            if not part.isidentifier():
                return False

        return True

    @classmethod
    def suggest_fixes(cls, report: Report) -> List[str]:
        """Suggest fixes for common validation issues."""
        suggestions = []

        if not report.fields:
            suggestions.append("Add at least one field to the report")

        if len(report.filters) > 10:
            suggestions.append("Consider reducing the number of filters for better performance")

        if report.limit > 100000:
            suggestions.append("Large row limits may impact performance; consider reducing")

        if report.schedule.enabled and not report.schedule.cron:
            suggestions.append("Define a CRON expression for scheduled reports")

        return suggestions
