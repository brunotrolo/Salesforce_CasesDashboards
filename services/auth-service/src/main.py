from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
from src.config import settings
from src.jwt_handler import JWTHandler
from src.rbac import RBAC, ResourcePermission
from src.models import (
    LoginRequest, LoginResponse, TokenPayload,
    User, PermissionCheck, PermissionRequest, RoleInfo,
    UserInfo, RefreshTokenRequest, HealthCheck,
    UserRole
)

# Inicializar aplicação
app = FastAPI(
    title="Auth Service",
    description="Serviço de autenticação e autorização",
    version="1.0.0",
)

# Handlers
jwt_handler = JWTHandler()

# ==================== Dependencies ====================

async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> TokenPayload:
    """Extrai e valida o usuário atual do token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Schema inválido")
    except ValueError:
        raise HTTPException(status_code=401, detail="Formato de autorização inválido")
    
    token_data = jwt_handler.validate_access_token(token)
    if not token_data:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    
    return token_data

async def require_permission(
    resource: str,
    action: str,
):
    """Factory para validar permissões."""
    async def _require_permission(
        current_user: TokenPayload = Depends(get_current_user),
    ):
        allowed, reason = ResourcePermission.is_action_allowed(
            [current_user.role],
            resource,
            action
        )
        
        if not allowed:
            raise HTTPException(status_code=403, detail=reason)
        
        return current_user
    
    return _require_permission

# ==================== Auth Endpoints ====================

@app.post("/auth/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Realiza login do usuário.
    
    Nota: Implementação simplificada. Em produção, usar banco de dados.
    """
    # TODO: Verificar credenciais no banco de dados
    # Para demo, aceitar qualquer usuário com "test" como username
    
    if request.username == "test":
        # Criar tokens
        tokens = jwt_handler.create_token_pair(
            user_id=f"u:{request.username}",
            role=UserRole.USER,
            permissions=RBAC.get_role_permissions(UserRole.USER),
        )
        
        return LoginResponse(**tokens)
    
    raise HTTPException(status_code=401, detail="Credenciais inválidas")

@app.post("/auth/logout")
async def logout(current_user: TokenPayload = Depends(get_current_user)):
    """Realiza logout (revoga token no Redis)."""
    # TODO: Adicionar token à blacklist no Redis
    return {"message": "Logout realizado com sucesso"}

@app.post("/auth/refresh", response_model=LoginResponse)
async def refresh_token(request: RefreshTokenRequest):
    """Renova o access token usando refresh token."""
    user_id = jwt_handler.validate_refresh_token(request.refresh_token)
    
    if not user_id:
        raise HTTPException(status_code=401, detail="Refresh token inválido")
    
    # TODO: Buscar role e permissions do banco de dados
    tokens = jwt_handler.create_token_pair(
        user_id=user_id,
        role=UserRole.USER,
        permissions=RBAC.get_role_permissions(UserRole.USER),
    )
    
    return LoginResponse(**tokens)

# ==================== User Info Endpoints ====================

@app.get("/auth/me", response_model=UserInfo)
async def get_current_user_info(current_user: TokenPayload = Depends(get_current_user)):
    """Retorna informações do usuário autenticado."""
    return UserInfo(
        id=current_user.sub,
        username=current_user.sub.split(":")[1],
        email=f"{current_user.sub}@example.com",
        roles=[current_user.role],
        permissions=current_user.permissions,
        created_at=datetime.utcfromtimestamp(current_user.iat).isoformat(),
    )

@app.get("/auth/permissions", response_model=list)
async def get_user_permissions(current_user: TokenPayload = Depends(get_current_user)):
    """Lista as permissões do usuário."""
    return current_user.permissions

@app.get("/auth/roles", response_model=list[RoleInfo])
async def get_available_roles():
    """Lista todos os roles disponíveis."""
    roles = RBAC.get_all_roles()
    return [RoleInfo(**role) for role in roles]

# ==================== Permission Check Endpoints ====================

@app.post("/auth/permissions/{resource}/{action}", response_model=PermissionCheck)
async def check_permission(
    resource: str,
    action: str,
    current_user: TokenPayload = Depends(get_current_user),
):
    """Verifica se usuário tem permissão para uma ação."""
    allowed, reason = ResourcePermission.is_action_allowed(
        [current_user.role],
        resource,
        action
    )
    
    return PermissionCheck(
        resource=resource,
        action=action,
        granted=allowed,
        reason=reason,
    )

@app.post("/auth/validate-token")
async def validate_token(token: str = Header(..., alias="X-Token")):
    """Valida um token JWT."""
    token_data = jwt_handler.validate_access_token(token)
    
    if not token_data:
        raise HTTPException(status_code=401, detail="Token inválido")
    
    exp_time = jwt_handler.get_expiration_time(token)
    
    return {
        "valid": True,
        "user_id": token_data.sub,
        "role": token_data.role.value,
        "expires_at": exp_time.isoformat() if exp_time else None,
    }

# ==================== Health Endpoints ====================

@app.get("/health", response_model=HealthCheck)
async def health_check():
    """Verifica saúde do serviço."""
    return HealthCheck(
        service=settings.SERVICE_NAME,
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        database="unknown",
    )

@app.get("/health/readiness")
async def readiness_check():
    """Verifica se serviço está pronto."""
    # TODO: Verificar conexão com banco de dados
    return {"status": "ready"}

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
