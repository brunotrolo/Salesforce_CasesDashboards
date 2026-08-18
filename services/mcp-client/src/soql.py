import re
from typing import List, Optional

from src.error_handler import InvalidQueryError

SOQL_FIELD_PATTERN = re.compile(r"^[A-Za-z0-9_.]+$")
SOQL_RESERVED_KEYWORDS = {
    "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "ORDER", "BY",
    "LIMIT", "OFFSET", "GROUP", "HAVING", "IN", "LIKE", "NULL",
    "UPDATE", "DELETE", "INSERT", "MERGE", "UPSERT", "CREATE",
    "DROP", "ALTER", "TABLE", "TRUNCATE",
}


def sanitize_soql_value(value: str, max_length: int = 255) -> str:
    """Sanitiza um valor literal contra SOQL injection.

    Remove aspas simples e palavras reservadas, limitando o tamanho.
    """
    if value is None:
        return ""
    cleaned = str(value).replace("'", "").replace("\\", "")
    cleaned = re.sub(r"\b(?:%s)\b" % "|".join(SOQL_RESERVED_KEYWORDS), "", cleaned, flags=re.IGNORECASE)
    return cleaned[:max_length]


def validate_soql_field(field: str, allowed_fields: Optional[List[str]] = None) -> str:
    """Valida que um campo SOQL é seguro (apenas letras, números, ponto e underscore).

    Args:
        field: Nome do campo (ex: "Case.Subject")
        allowed_fields: Lista opcional de campos permitidos (whitelist)

    Returns:
        Campo validado

    Raises:
        InvalidQueryError: se o campo contém caracteres inválidos
    """
    if not field or not isinstance(field, str):
        raise InvalidQueryError("SOQL field cannot be empty")

    if not SOQL_FIELD_PATTERN.match(field):
        raise InvalidQueryError(f"Invalid SOQL field: {field}")

    if allowed_fields is not None and field not in allowed_fields:
        raise InvalidQueryError(f"Field not allowed: {field}")

    return field


def build_soql_query(
    fields: List[str],
    object_name: str,
    where_clause: Optional[str] = None,
    allowed_fields: Optional[List[str]] = None,
    limit: int = 200,
) -> str:
    """Constrói uma query SOQL segura, validando campos e cláusulas.

    Args:
        fields: Campos a selecionar
        object_name: Objeto Salesforce (ex: "Case")
        where_clause: Cláusula WHERE opcional (já sanitizada pelo caller)
        allowed_fields: Whitelist opcional de campos
        limit: Limite de resultados

    Returns:
        Query SOQL montada

    Raises:
        InvalidQueryError: se campos inválidos
    """
    if not object_name or not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", object_name):
        raise InvalidQueryError(f"Invalid SOQL object: {object_name}")

    safe_fields = []
    for field in fields:
        safe_fields.append(validate_soql_field(field, allowed_fields))

    query = f"SELECT {', '.join(safe_fields)} FROM {object_name}"

    if where_clause:
        if ";" in where_clause or re.search(r"\b(?:insert|update|delete|drop|alter)\b", where_clause, re.IGNORECASE):
            raise InvalidQueryError("Unsafe WHERE clause")
        query += f" WHERE {where_clause}"

    query += f" LIMIT {int(limit)}"
    return query