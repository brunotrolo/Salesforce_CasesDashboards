# Auth Service

Serviço de autenticação e autorização para o Salesforce Reports System.

## Funcionalidades

- **Gerenciamento de JWT**: Criação, validação e refresh de tokens JWT
- **OAuth 2.0**: Suporte para fluxo de autorização com Salesforce
- **RBAC**: Sistema de Controle de Acesso Baseado em Papéis
- **Gerenciamento de Sessões**: Rastreamento de sessões de usuário
- **Logging Estruturado**: Logs em JSON para análise centralizada

## Arquitetura

```
┌─────────────────┐
│  API Gateway    │
└────────┬────────┘
         │
    ┌────▼─────┐
    │ Auth      │
    │ Service   │
    │ (3002)    │
    └────┬─────┘
         │
    ┌────┴────────────────┐
    │                     │
┌───▼──────┐      ┌──────▼─────┐
│PostgreSQL│      │    Redis    │
└──────────┘      └─────────────┘
```

## Quick Start

### Desenvolvimento Local

```bash
# Clonar repositório e navegue até o serviço
cd services/auth-service

# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas configurações

# Executar serviço
uvicorn src.main:app --host 0.0.0.0 --port 3002 --reload
```

O serviço estará disponível em `http://localhost:3002`

### Com Docker

```bash
# Build da imagem
docker build -t auth-service:latest .

# Executar container
docker run -p 3002:3002 \
  -e JWT_SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://user:password@postgres:5432/auth_db \
  -e REDIS_URL=redis://redis:6379/0 \
  auth-service:latest
```

### Com Docker Compose

```bash
# Do diretório raiz do projeto
docker-compose up auth-service
```

## Endpoints da API

### Autenticação

#### Login
```
POST /auth/login

Body:
{
  "username": "user@example.com",
  "password": "password123"
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Refresh Token
```
POST /auth/refresh

Body:
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
}

Response (200):
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

#### Logout
```
POST /auth/logout

Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (204): No Content
```

### Usuário

#### Obter Informações do Usuário
```
GET /auth/me

Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (200):
{
  "user_id": "u:12345",
  "username": "user@example.com",
  "role": "manager",
  "permissions": ["reports:read", "reports:create"]
}
```

#### Obter Permissões
```
GET /auth/permissions

Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (200):
{
  "permissions": ["reports:read", "reports:create", "reports:execute"]
}
```

#### Obter Papéis
```
GET /auth/roles

Response (200):
{
  "roles": [
    {
      "name": "admin",
      "description": "Administrator with full access",
      "permissions": ["*"]
    },
    ...
  ]
}
```

### Validação

#### Validar Token
```
POST /auth/validate-token

Headers:
X-Token: eyJhbGciOiJIUzI1NiIs...

Response (200):
{
  "valid": true,
  "user_id": "u:12345",
  "role": "manager"
}
```

#### Verificar Permissão
```
POST /auth/permissions/{resource}/{action}

Headers:
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

Response (200):
{
  "allowed": true,
  "message": "Permission granted"
}
```

### Health Check

```
GET /health

Response (200):
{
  "status": "healthy",
  "service": "auth-service",
  "timestamp": "2026-08-16T10:30:45.123Z"
}
```

```
GET /health/readiness

Response (200):
{
  "ready": true,
  "checks": {
    "database": "connected",
    "redis": "connected"
  }
}
```

## Sistema de Papéis e Permissões

### Papéis Disponíveis

| Papel | Descrição | Permissões |
|-------|-----------|-----------|
| **admin** | Administrador com acesso total | `*` (todas) |
| **manager** | Gerenciador de relatórios | `reports:create`, `reports:read`, `reports:update`, `reports:execute`, `users:read` |
| **user** | Usuário comum | `reports:read`, `reports:execute` |
| **guest** | Visitante apenas leitura | `reports:read` |

### Permissões

Formato: `{recurso}:{ação}`

**Recursos:**
- `reports` - Relatórios
- `users` - Usuários
- `admin` - Operações administrativas

**Ações:**
- `create` - Criar
- `read` - Ler/Visualizar
- `update` - Atualizar/Editar
- `delete` - Deletar
- `execute` - Executar

## Configuração

### Variáveis de Ambiente

```bash
# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30

# Service
SERVICE_NAME=auth-service
SERVICE_PORT=3002
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@host:5432/db
DATABASE_POOL_SIZE=10

# Redis
REDIS_URL=redis://localhost:6379/0
SESSION_TTL_SECONDS=86400

# Salesforce
SF_CLIENT_ID=your_client_id
SF_CLIENT_SECRET=your_client_secret

# Security
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
TRACE_SAMPLE_RATE=0.1
```

## Testes

### Executar Todos os Testes

```bash
# Com coverage
pytest tests/ -v --cov=src --cov-report=html

# Apenas testes rápidos
pytest tests/ -v -m "not slow"

# Teste específico
pytest tests/test_jwt_handler.py::TestJWTHandler::test_create_access_token -v
```

### Cobertura Mínima

Esperado: **90%** (serviço crítico)

```bash
# Gerar relatório de coverage
pytest tests/ --cov=src --cov-report=term-missing
```

## Integração com MCP Client

O Auth Service fornece tokens JWT que devem ser usados pelo MCP Client:

```python
# No MCP Client
from src.oauth_handler import OAuthHandler

oauth = OAuthHandler()

# Obter token válido
token = oauth.get_valid_token()

# Usar em headers
headers = {
    "Authorization": f"Bearer {token}"
}

# Chamadas para Auth Service
response = requests.get(
    "http://auth-service:3002/auth/me",
    headers=headers
)
```

## Logs Estruturados

Todos os logs são em formato JSON:

```json
{
  "timestamp": "2026-08-16T10:30:45.123Z",
  "service": "auth-service",
  "level": "INFO",
  "trace_id": "abc123def456",
  "message": "User authenticated successfully",
  "context": {
    "user_id": "u:12345",
    "role": "manager",
    "duration_ms": 125
  }
}
```

## Troubleshooting

### Token Expirado

**Erro:** `401 Unauthorized - Token expired`

**Solução:** Use o endpoint `/auth/refresh` com o refresh token para obter um novo access token.

### Acesso Negado

**Erro:** `403 Forbidden - Permission denied`

**Solução:** Verifique se o usuário tem o papel correto. Contate um administrador.

### Banco de Dados Indisponível

**Erro:** `503 Service Unavailable - Database connection failed`

**Solução:** Verifique se PostgreSQL está rodando e a URL de conexão está correta em `.env`.

### Redis Indisponível

**Erro:** `503 Service Unavailable - Redis connection failed`

**Solução:** Verifique se Redis está rodando em `localhost:6379` ou configure `REDIS_URL` corretamente.

## Performance

- **Login:** ~100-200ms
- **Token Refresh:** ~50-100ms
- **Permissão Check:** ~10-50ms
- **Token Validation:** ~5-20ms

## Segurança

### Best Practices

- ✅ Tokens JWT assinados com HS256
- ✅ Refresh tokens armazenados em Redis
- ✅ Senhas com hash Bcrypt (rounds=12)
- ✅ Proteção contra força bruta (max 5 tentativas, lockout 15 min)
- ✅ HTTPS obrigatório em produção
- ✅ CORS configurável
- ✅ Rate limiting no MCP Client

### Secrets em Produção

Use Kubernetes Secrets:

```bash
kubectl create secret generic auth-service-secrets \
  --from-literal=JWT_SECRET_KEY=your-super-secret-key \
  --from-literal=DATABASE_URL=postgresql://... \
  --from-literal=REDIS_URL=redis://... \
  -n salesforce-reports
```

## Recursos

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [JWT.io](https://jwt.io/)
- [Python-Jose](https://github.com/mpdavis/python-jose)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Redis](https://redis.io/)

## Status

✅ **Produção Pronto**

- Autenticação implementada e testada
- Autorização com RBAC completa
- Logging estruturado
- Tratamento de erros robusto
- Documentação abrangente

## Próximas Fases

- [ ] Phase 3: Logging Service
- [ ] Phase 4: Report Service
- [ ] Phase 5: Dashboard Frontend
- [ ] Phase 6: Builder Frontend
- [ ] Phase 7: Analytics Frontend
