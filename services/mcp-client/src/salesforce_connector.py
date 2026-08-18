import httpx
from typing import Dict, List, Optional, Any
from datetime import datetime
from src.config import settings
from src.logger import log
from src.oauth_handler import OAuthHandler
from src.error_handler import retry_async
from src.models import Report, ReportExecutionResult, ReportStatus, ReportType

class SalesforceConnector:
    """Conector com Salesforce via API REST e MCP (async, sessão única)."""
    
    def __init__(self, oauth_handler: OAuthHandler):
        self.oauth = oauth_handler
        self.instance_url = settings.SF_INSTANCE_URL
        self.api_version = "v59.0"
        self.base_url = f"{self.instance_url}/services/data/{self.api_version}"
        self.timeout = settings.OAUTH_TIMEOUT
        self._client = httpx.AsyncClient(
            timeout=self.timeout,
            follow_redirects=True,
        )
    
    async def close(self):
        """Fecha a sessão HTTP."""
        await self._client.aclose()
    
    async def _get_headers(self) -> Dict[str, str]:
        """Retorna headers com autorização."""
        token = self.oauth.get_valid_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
    
    @retry_async(max_retries=3, backoff_factor=2.0)
    async def create_report(self, report_name: str, report_data: Dict) -> str:
        """
        Cria um novo relatório no Salesforce.
        
        Args:
            report_name: Nome do relatório
            report_data: Dados do relatório
            
        Returns:
            ID do relatório criado
        """
        url = f"{self.base_url}/sobjects/Report"
        
        payload = {
            "Name": report_name,
            "Description": report_data.get("description", ""),
            "ReportType": report_data.get("report_type", "StandardType"),
        }
        
        try:
            response = await self._client.post(
                url,
                headers=await self._get_headers(),
                json=payload,
            )
            
            if response.status_code in [200, 201]:
                result = response.json()
                report_id = result.get("id")
                log.info("Relatório criado", salesforce_id=report_id, name=report_name)
                return report_id
            
            log.error(f"Erro ao criar relatório: {response.status_code}")
            raise Exception(f"Erro ao criar relatório: {response.text}")
        
        except Exception as e:
            log.error("Falha ao criar relatório no Salesforce", error=e)
            raise
    
    @retry_async(max_retries=3, backoff_factor=2.0)
    async def get_report(self, report_id: str) -> Dict:
        """
        Obtém informações de um relatório.
        
        Args:
            report_id: ID do relatório no Salesforce
            
        Returns:
            Dados do relatório
        """
        url = f"{self.base_url}/sobjects/Report/{report_id}"
        
        try:
            response = await self._client.get(
                url,
                headers=await self._get_headers(),
            )
            
            if response.status_code == 200:
                log.debug("Relatório obtido", salesforce_id=report_id)
                return response.json()
            
            elif response.status_code == 404:
                log.warning("Relatório não encontrado", salesforce_id=report_id)
                raise Exception(f"Relatório {report_id} não encontrado")
            
            raise Exception(f"Erro ao obter relatório: {response.text}")
        
        except Exception as e:
            log.error("Falha ao obter relatório", error=e, salesforce_id=report_id)
            raise
    
    @retry_async(max_retries=3, backoff_factor=2.0)
    async def list_reports(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        Lista relatórios no Salesforce.
        
        Args:
            limit: Número máximo de resultados
            offset: Deslocamento para paginação
            
        Returns:
            Lista de relatórios
        """
        url = f"{self.base_url}/sobjects/Report"
        
        params = {
            "limit": limit,
            "offset": offset,
        }
        
        try:
            response = await self._client.get(
                url,
                headers=await self._get_headers(),
                params=params,
            )
            
            if response.status_code == 200:
                data = response.json()
                log.info("Relatórios listados", count=len(data.get("records", [])))
                return data.get("records", [])
            
            raise Exception(f"Erro ao listar relatórios: {response.text}")
        
        except Exception as e:
            log.error("Falha ao listar relatórios", error=e)
            raise
    
    @retry_async(max_retries=3, backoff_factor=2.0)
    async def update_report(self, report_id: str, updates: Dict) -> bool:
        """
        Atualiza um relatório.
        
        Args:
            report_id: ID do relatório
            updates: Dados para atualizar
            
        Returns:
            True se sucesso
        """
        url = f"{self.base_url}/sobjects/Report/{report_id}"
        
        try:
            response = await self._client.patch(
                url,
                headers=await self._get_headers(),
                json=updates,
            )
            
            if response.status_code in [200, 204]:
                log.info("Relatório atualizado", salesforce_id=report_id)
                return True
            
            raise Exception(f"Erro ao atualizar relatório: {response.text}")
        
        except Exception as e:
            log.error("Falha ao atualizar relatório", error=e, salesforce_id=report_id)
            raise
    
    @retry_async(max_retries=3, backoff_factor=2.0)
    async def delete_report(self, report_id: str) -> bool:
        """
        Deleta um relatório.
        
        Args:
            report_id: ID do relatório
            
        Returns:
            True se sucesso
        """
        url = f"{self.base_url}/sobjects/Report/{report_id}"
        
        try:
            response = await self._client.delete(
                url,
                headers=await self._get_headers(),
            )
            
            if response.status_code in [200, 204]:
                log.info("Relatório deletado", salesforce_id=report_id)
                return True
            
            elif response.status_code == 404:
                raise Exception(f"Relatório {report_id} não encontrado")
            
            raise Exception(f"Erro ao deletar relatório: {response.text}")
        
        except Exception as e:
            log.error("Falha ao deletar relatório", error=e, salesforce_id=report_id)
            raise
    
    @retry_async(max_retries=3, backoff_factor=2.0)
    async def execute_report(self, report_id: str) -> ReportExecutionResult:
        """
        Executa um relatório no Salesforce.
        
        Args:
            report_id: ID do relatório
            
        Returns:
            Resultado da execução
        """
        url = f"{self.instance_url}/services/data/{self.api_version}/analytics/reports/{report_id}"
        
        start_time = datetime.utcnow()
        
        try:
            response = await self._client.get(
                url,
                headers=await self._get_headers(),
            )
            
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)
            
            if response.status_code == 200:
                result = response.json()
                
                rows_returned = len(result.get("factMap", {}).get("T!T", {}).get("rows", []))
                
                log.info(
                    "Relatório executado com sucesso",
                    salesforce_id=report_id,
                    rows_returned=rows_returned,
                    execution_time_ms=execution_time
                )
                
                return ReportExecutionResult(
                    report_id=report_id,
                    status="success",
                    rows_returned=rows_returned,
                    execution_time_ms=execution_time,
                    executed_at=datetime.utcnow().isoformat(),
                    data=result.get("factMap"),
                )
            
            raise Exception(f"Erro ao executar relatório: {response.text}")
        
        except Exception as e:
            log.error("Falha ao executar relatório", error=e, salesforce_id=report_id)
            raise