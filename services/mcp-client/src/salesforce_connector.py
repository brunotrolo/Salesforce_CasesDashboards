"""
Salesforce MCP Client - Connector
Handles OAuth2 authentication and API communication.
"""

import os
import json
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import aiohttp
from pydantic import BaseModel
import logging

from .data_models import OAuth2Credentials, SalesforceResponse, ReportConfig
from .error_handler import (
    AuthenticationError, TokenExpiredError, RateLimitError,
    MCPError, ErrorHandler
)


logger = logging.getLogger(__name__)


class SalesforceConnector:
    """
    Salesforce MCP Connector
    Gerencia autenticação OAuth2 e comunicação com Salesforce API.
    """

    def __init__(
        self,
        client_id: str = None,
        client_secret: str = None,
        refresh_token: str = None,
        instance_url: str = "https://login.salesforce.com"
    ):
        """
        Inicializar o conector.
        
        Args:
            client_id: OAuth2 Client ID
            client_secret: OAuth2 Client Secret
            refresh_token: Refresh token para renovação
            instance_url: URL da instância Salesforce
        """
        self.client_id = client_id or os.getenv("SF_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SF_CLIENT_SECRET")
        self.refresh_token = refresh_token or os.getenv("SF_REFRESH_TOKEN")
        self.instance_url = instance_url
        
        self.credentials: Optional[OAuth2Credentials] = None
        self.error_handler = ErrorHandler(logger)
        self.session: Optional[aiohttp.ClientSession] = None

        if not all([self.client_id, self.client_secret, self.refresh_token]):
            raise AuthenticationError("Missing OAuth2 credentials in environment")

        logger.info("SalesforceConnector initialized")

    async def authenticate(self) -> bool:
        """
        Autenticar com Salesforce usando OAuth2 refresh_token.
        
        Returns:
            bool: True se autenticado com sucesso
        """
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.instance_url}/services/oauth2/token"
                data = {
                    "grant_type": "refresh_token",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "refresh_token": self.refresh_token
                }

                async with session.post(url, data=data) as resp:
                    if resp.status != 200:
                        raise AuthenticationError(
                            f"OAuth2 token refresh failed: {resp.status}",
                            code="OAUTH2_FAILED"
                        )

                    response_data = await resp.json()
                    self.credentials = OAuth2Credentials(
                        client_id=self.client_id,
                        client_secret=self.client_secret,
                        refresh_token=self.refresh_token,
                        access_token=response_data.get("access_token"),
                        instance_url=response_data.get("instance_url"),
                        token_expires_at=datetime.now() + timedelta(
                            seconds=response_data.get("expires_in", 3600)
                        )
                    )

                    logger.info(
                        "Salesforce authentication successful",
                        extra={"instance_url": self.credentials.instance_url}
                    )
                    return True

        except Exception as e:
            error = self.error_handler.handle_error(e, {"action": "authenticate"})
            raise error

    async def get_session(self) -> aiohttp.ClientSession:
        """Obter ou criar sessão HTTP."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """Fechar sessão HTTP."""
        if self.session:
            await self.session.close()

    async def _get_headers(self) -> Dict[str, str]:
        """Obter headers com autenticação."""
        if not self.credentials or not self.credentials.access_token:
            await self.authenticate()

        return {
            "Authorization": f"Bearer {self.credentials.access_token}",
            "Content-Type": "application/json"
        }

    async def create_report(self, config: ReportConfig) -> SalesforceResponse:
        """Criar novo relatório."""
        try:
            session = await self.get_session()
            headers = await self._get_headers()

            url = f"{self.credentials.instance_url}/services/data/v60.0/sobjects/Report"
            payload = config.dict()

            async with session.post(url, json=payload, headers=headers) as resp:
                data = await resp.json()

                if resp.status not in [200, 201]:
                    return SalesforceResponse(
                        success=False,
                        error=data.get("message", "Failed to create report")
                    )

                logger.info(
                    "Report created successfully",
                    extra={"report_id": data.get("id")}
                )

                return SalesforceResponse(
                    success=True,
                    id=data.get("id"),
                    data=data
                )

        except Exception as e:
            error = self.error_handler.handle_error(
                e,
                {"action": "create_report", "report_name": config.name}
            )
            return SalesforceResponse(success=False, error=str(error))

    async def get_report(self, report_id: str) -> SalesforceResponse:
        """Buscar relatório por ID."""
        try:
            session = await self.get_session()
            headers = await self._get_headers()

            url = f"{self.credentials.instance_url}/services/data/v60.0/sobjects/Report/{report_id}"

            async with session.get(url, headers=headers) as resp:
                data = await resp.json()

                if resp.status != 200:
                    return SalesforceResponse(
                        success=False,
                        error=data.get("message", "Report not found")
                    )

                return SalesforceResponse(
                    success=True,
                    id=report_id,
                    data=data
                )

        except Exception as e:
            error = self.error_handler.handle_error(
                e,
                {"action": "get_report", "report_id": report_id}
            )
            return SalesforceResponse(success=False, error=str(error))

    async def delete_report(self, report_id: str) -> SalesforceResponse:
        """Deletar relatório."""
        try:
            session = await self.get_session()
            headers = await self._get_headers()

            url = f"{self.credentials.instance_url}/services/data/v60.0/sobjects/Report/{report_id}"

            async with session.delete(url, headers=headers) as resp:
                if resp.status != 204:
                    return SalesforceResponse(
                        success=False,
                        error="Failed to delete report"
                    )

                logger.info(
                    "Report deleted successfully",
                    extra={"report_id": report_id}
                )

                return SalesforceResponse(success=True, id=report_id)

        except Exception as e:
            error = self.error_handler.handle_error(
                e,
                {"action": "delete_report", "report_id": report_id}
            )
            return SalesforceResponse(success=False, error=str(error))
