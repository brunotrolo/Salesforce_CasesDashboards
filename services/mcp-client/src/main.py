from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from datetime import datetime
import secrets
from src.config import settings
from src.logger import log
from src.oauth_handler import OAuthHandler
from src.salesforce_connector import SalesforceConnector
from src.models import (
    Report, ReportCreate, ReportUpdate, ReportListResponse,
    ReportExecutionRequest, ReportExecutionResult,
    OAuthAuthorizeResponse, OAuthCallbackRequest,
    HealthCheck, ErrorResponse
)

# Inicializar aplicação
app = FastAPI(
    title="MCP Client Service",
    description="Serviço cliente para integração com Salesforce via MCP",
    version="1.0.0",
)

# Variáveis globais para gerenciar sessões OAuth
oauth_states = {}
oauth_handler = OAuthHandler()
salesforce_connector = SalesforceConnector(oauth_handler)

# Middleware para logging
@app.middleware("http")
async def log_requests(request, call_next):
    log.info(
        f"{request.method} {request.url.path}",
        method=request.method,
        path=request.url.path
    )
    response = await call_next(request)
    log.info(
        f"Response: {response.status_code}",
        status_code=response.status_code
    )
    return response

# ==================== OAuth Endpoints ====================

@app.post("/oauth/authorize", response_model=OAuthAuthorizeResponse)
async def authorize():
    """Inicia o fluxo de autorização OAuth."""
    try:
        auth_url, state = oauth_handler.get_authorization_url()
        oauth_states[state] = {"created_at": datetime.utcnow().isoformat()}
        
        return OAuthAuthorizeResponse(
            authorization_url=auth_url,
            state=state,
            expires_in=600,
        )
    except Exception as e:
        log.error("Erro ao gerar URL de autorização", error=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/oauth/callback")
async def oauth_callback(request: OAuthCallbackRequest):
    """Processa callback do OAuth."""
    try:
        if request.state not in oauth_states:
            raise HTTPException(status_code=400, detail="Estado inválido")
        
        token = oauth_handler.exchange_code_for_token(request.code)
        del oauth_states[request.state]
        
        return {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
        }
    except Exception as e:
        log.error("Erro no callback OAuth", error=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/oauth/refresh")
async def refresh_token(refresh_token: str = Query(...)):
    """Renova o access token."""
    try:
        token = oauth_handler.refresh_access_token(refresh_token)
        return {
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
        }
    except Exception as e:
        log.error("Erro ao renovar token", error=e)
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Report Endpoints ====================

@app.get("/reports", response_model=ReportListResponse)
async def list_reports(limit: int = Query(10, ge=1, le=100), offset: int = Query(0, ge=0)):
    """Lista todos os relatórios."""
    try:
        reports = salesforce_connector.list_reports(limit=limit, offset=offset)
        
        return ReportListResponse(
            items=[Report(**r) for r in reports],
            total=len(reports),
            offset=offset,
            limit=limit,
        )
    except Exception as e:
        log.error("Erro ao listar relatórios", error=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports", response_model=Report, status_code=201)
async def create_report(report: ReportCreate):
    """Cria um novo relatório."""
    try:
        report_data = {
            "description": report.metadata.description if report.metadata else "",
            "report_type": report.report_type.value,
            "fields": report.fields,
        }
        
        salesforce_id = salesforce_connector.create_report(report.name, report_data)
        
        return Report(
            id=salesforce_id,
            name=report.name,
            report_type=report.report_type,
            object_type=report.object_type,
            fields=report.fields,
            metadata=report.metadata or {},
            status=report.status,
            salesforce_id=salesforce_id,
            created_at=datetime.utcnow().isoformat(),
        )
    except Exception as e:
        log.error("Erro ao criar relatório", error=e)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reports/{report_id}", response_model=Report)
async def get_report(report_id: str):
    """Obtém um relatório específico."""
    try:
        report_data = salesforce_connector.get_report(report_id)
        return Report(**report_data)
    except Exception as e:
        log.error("Erro ao obter relatório", error=e, report_id=report_id)
        raise HTTPException(status_code=404, detail=f"Relatório {report_id} não encontrado")

@app.put("/reports/{report_id}", response_model=Report)
async def update_report(report_id: str, report: ReportUpdate):
    """Atualiza um relatório."""
    try:
        updates = report.dict(exclude_none=True)
        
        if "status" in updates:
            updates["Status"] = updates.pop("status").value
        
        salesforce_connector.update_report(report_id, updates)
        
        updated_data = salesforce_connector.get_report(report_id)
        return Report(**updated_data)
    except Exception as e:
        log.error("Erro ao atualizar relatório", error=e, report_id=report_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/reports/{report_id}")
async def delete_report(report_id: str):
    """Deleta um relatório."""
    try:
        salesforce_connector.delete_report(report_id)
        return {"success": True, "message": f"Relatório {report_id} deletado"}
    except Exception as e:
        log.error("Erro ao deletar relatório", error=e, report_id=report_id)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reports/{report_id}/execute", response_model=ReportExecutionResult)
async def execute_report(report_id: str, request: ReportExecutionRequest):
    """Executa um relatório."""
    try:
        result = salesforce_connector.execute_report(report_id)
        return result
    except Exception as e:
        log.error("Erro ao executar relatório", error=e, report_id=report_id)
        raise HTTPException(status_code=500, detail=str(e))

# ==================== Health Endpoints ====================

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Verifica saúde do serviço."""
    return HealthCheck(
        service=settings.SERVICE_NAME,
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
    )

@app.get("/health/readiness")
async def readiness_check():
    """Verifica se o serviço está pronto para aceitar tráfego."""
    try:
        # Verificar conexão com Salesforce
        if not oauth_handler.current_token and not settings.SF_REFRESH_TOKEN:
            return JSONResponse(
                status_code=503,
                content={"status": "not_ready", "reason": "Sem autenticação Salesforce"}
            )
        
        return {"status": "ready"}
    except Exception as e:
        log.error("Erro na verificação de readiness", error=e)
        return JSONResponse(
            status_code=503,
            content={"status": "not_ready", "error": str(e)}
        )

# ==================== Error Handlers ====================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler para exceções HTTP."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "message": "Erro na requisição",
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handler para exceções gerais."""
    log.error("Exceção não tratada", error=exc)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat(),
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=settings.SERVICE_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
