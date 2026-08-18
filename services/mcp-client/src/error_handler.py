"""
Error handling for Salesforce MCP client.
"""

from typing import Optional, Callable, Any, Awaitable
import asyncio
import functools
import traceback
import logging


class SalesforceError(Exception):
    """Base exception for Salesforce errors."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[dict] = None):
        self.message = message
        self.code = code or "UNKNOWN_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class AuthenticationError(SalesforceError):
    """Erro de autenticação com Salesforce."""
    pass


class TokenExpiredError(AuthenticationError):
    """Token de acesso expirou."""
    pass


class InvalidConfigError(SalesforceError):
    """Configuração inválida."""
    pass


class InvalidQueryError(SalesforceError):
    """Query SOQL inválida ou insegura."""
    pass


class ReportNotFoundError(SalesforceError):
    """Relatório não encontrado."""
    pass


class RateLimitError(SalesforceError):
    """Rate limit atingido."""
    pass


class MCPError(SalesforceError):
    """Erro genérico do MCP."""
    pass


class ErrorHandler:
    """Gerenciador centralizado de erros."""
    
    def __init__(self, logger: logging.Logger = None):
        self.logger = logger or logging.getLogger(__name__)

    def handle_error(self, error: Exception, context: dict = None) -> SalesforceError:
        """Mapear e tratar erros."""
        context = context or {}
        
        # Log do erro
        self.logger.error(
            f"Error: {str(error)}",
            extra={
                "error_type": type(error).__name__,
                "context": context,
                "traceback": traceback.format_exc()
            }
        )

        # Mapear para SalesforceError
        if isinstance(error, SalesforceError):
            return error

        if "401" in str(error) or "unauthorized" in str(error).lower():
            return AuthenticationError("Invalid credentials or token expired")

        if "403" in str(error) or "forbidden" in str(error).lower():
            return AuthenticationError("Access forbidden - check IP whitelist")

        if "404" in str(error) or "not found" in str(error).lower():
            return ReportNotFoundError("Resource not found")

        if "429" in str(error) or "rate limit" in str(error).lower():
            return RateLimitError("Rate limit exceeded - retry after delay")

        return MCPError(str(error))

def retry_async(max_retries: int = 3, backoff_factor: float = 2.0):
    """Decorator para retry automático em funções async (não bloqueia event loop).

    Re-tenta em erros de RateLimitError e TokenExpiredError usando asyncio.sleep.

    Exemplo:
        @retry_async(max_retries=3)
        async def fetch_data(self):
            ...
    """
    logger = logging.getLogger(__name__)

    def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except (RateLimitError, TokenExpiredError) as e:
                    if attempt == max_retries - 1:
                        raise
                    wait_time = backoff_factor ** attempt
                    logger.warning(
                        f"Async retry attempt {attempt + 1}/{max_retries} after {wait_time}s",
                        extra={"error": str(e)}
                    )
                    await asyncio.sleep(wait_time)
        return wrapper
    return decorator
