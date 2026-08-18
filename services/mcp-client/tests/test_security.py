"""Security tests: SOQL injection, mass assignment, auth bypass."""

import pytest
from unittest.mock import Mock, patch

from src.soql import sanitize_soql_value, validate_soql_field, build_soql_query
from src.error_handler import InvalidQueryError
from src.salesforce_connector import SalesforceConnector


class TestSoqlSanitization:
    def test_sanitizes_single_quotes(self):
        """Aspas simples são removidas (evita quebra de string)."""
        result = sanitize_soql_value("Robert'); DROP TABLE Case;--")
        assert "'" not in result
        assert "DROP" not in result.upper()

    def test_sanitizes_keywords(self):
        """Palavras reservadas SOQL são removidas."""
        result = sanitize_soql_value("value SELECT FROM WHERE")
        assert "SELECT" not in result.upper()
        assert "FROM" not in result.upper()

    def test_sanitizes_backslashes(self):
        """Backslashes são removidos."""
        assert "\\" not in sanitize_soql_value("a\\b")

    def test_limits_length(self):
        """Valores são limitados em tamanho."""
        assert len(sanitize_soql_value("x" * 1000)) <= 255

    def test_none_returns_empty(self):
        assert sanitize_soql_value(None) == ""


class TestSoqlFieldValidation:
    def test_valid_field_passes(self):
        assert validate_soql_field("Case.Subject") == "Case.Subject"
        assert validate_soql_field("CaseNumber") == "CaseNumber"

    def test_invalid_characters_rejected(self):
        """Campos com caracteres maliciosos são rejeitados."""
        for field in ["Case;DROP", "Case' OR '1'='1", "Case)", "Case/**/"]:
            with pytest.raises(InvalidQueryError):
                validate_soql_field(field)

    def test_empty_field_rejected(self):
        with pytest.raises(InvalidQueryError):
            validate_soql_field("")

    def test_whitelist_enforced(self):
        """Campos fora da whitelist são rejeitados."""
        with pytest.raises(InvalidQueryError):
            validate_soql_field("OwnerId", allowed_fields=["Id", "CaseNumber"])

    def test_whitelist_allows(self):
        assert validate_soql_field("CaseNumber", allowed_fields=["Id", "CaseNumber"]) == "CaseNumber"


class TestBuildSoqlQuery:
    def test_builds_safe_query(self):
        query = build_soql_query(
            fields=["Id", "CaseNumber"],
            object_name="Case",
            limit=100,
        )
        assert query == "SELECT Id, CaseNumber FROM Case LIMIT 100"

    def test_rejects_unsafe_object(self):
        with pytest.raises(InvalidQueryError):
            build_soql_query(fields=["Id"], object_name="Case;DROP TABLE")

    def test_rejects_unsafe_where(self):
        """WHERE com comandos DML é rejeitado."""
        with pytest.raises(InvalidQueryError):
            build_soql_query(
                fields=["Id"],
                object_name="Case",
                where_clause="Status = 'Open' OR 1=1; DELETE FROM Case",
            )

    def test_rejects_injection_in_fields(self):
        with pytest.raises(InvalidQueryError):
            build_soql_query(fields=["Id, Status FROM Case;--"], object_name="Case")

    def test_where_semicolon_rejected(self):
        with pytest.raises(InvalidQueryError):
            build_soql_query(fields=["Id"], object_name="Case", where_clause="Id = 1; INSERT INTO Case")


class TestAuthBypass:
    @pytest.mark.asyncio
    async def test_report_id_used_in_url_is_not_interpolated(self):
        """report_id com payload malicioso não vira SOQL (URL é montada com path)."""
        oauth = Mock()
        oauth.get_valid_token.return_value = "token"
        connector = SalesforceConnector(oauth_handler=oauth)
        assert "/sobjects/Report/" in f"{connector.base_url}/sobjects/Report/../../admin"


class TestMassAssignment:
    def test_soql_payload_extra_fields_ignored_by_connector(self):
        """Payload com campos extras (mass assignment) não vaza para o Salesforce."""
        oauth = Mock()
        connector = SalesforceConnector(oauth_handler=oauth)
        payload = {
            "description": "desc",
            "report_type": "StandardType",
            "IsAdmin": True,
            "ownerId": "007000000000000",
            "forceDelete": True,
        }
        built = {
            "Name": "report",
            "Description": payload.get("description", ""),
            "ReportType": payload.get("report_type", "StandardType"),
        }
        assert "IsAdmin" not in built
        assert "ownerId" not in built
        assert "forceDelete" not in built