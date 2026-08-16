# MCP Client Service

Serviço cliente para integração com Salesforce via Model Context Protocol (MCP). Fornece autenticação OAuth 2.0 e operações CRUD completas para relatórios Salesforce.

## 🚀 Quick Start

### Desenvolvimento Local

```bash
# Instalar dependências
pip install -r requirements.txt

# Configurar variáveis de ambiente
cp .env.example .env
# Editar .env com suas credenciais Salesforce

# Executar serviço
python -m uvicorn src.main:app --reload --port 3005
```

### Docker

```bash
# Build da imagem
docker build -t mcp-client:1.0 .

# Executar container
docker run -p 3005:3005 \
  -e SF_CLIENT_ID=your_id \
  -e SF_CLIENT_SECRET=your_secret \
  mcp-client:1.0
```

## 📚 API Endpoints

### OAuth

**POST /oauth/authorize**
- Inicia fluxo de autorização
- Retorna: URL de autorização e state

**POST /oauth/callback**
- Processa callback OAuth
- Corpo: `{ "code": "...", "state": "..." }`
- Retorna: access_token

**POST /oauth/refresh**
- Renova access token
- Query: `refresh_token=...`
- Retorna: novo access_token

### Relatórios

**GET /reports**
- Lista todos os relatórios
- Query params: `limit=10&offset=0`
- Retorna: Lista de relatórios

**POST /reports**
- Cria novo relatório
- Corpo: `{ "name": "...", "report_type": "SUMMARY", ... }`
- Retorna: Relatório criado

**GET /reports/{report_id}**
- Obtém relatório específico
- Retorna: Detalhes do relatório

**PUT /reports/{report_id}**
- Atualiza relatório
- Corpo: `{ "name": "...", "status": "ACTIVE" }`
- Retorna: Relatório atualizado

**DELETE /reports/{report_id}**
- Deleta relatório
- Retorna: `{ "success": true }`

**POST /reports/{report_id}/execute**
- Executa um relatório
- Retorna: Resultado da execução

### Saúde

**GET /health**
- Verifica saúde do serviço
- Retorna: Status e timestamp

**GET /health/readiness**
- Verifica se pronto para tráfego
- Retorna: Status 200 (pronto) ou 503 (não pronto)

## 🔐 Configuração Salesforce

### OAuth Setup

1. Acessar Salesforce Setup → Apps → App Manager
2. Criar novo Connected App
3. Configurar OAuth:
   - Callback URL: `https://api.reports.example.com/oauth/callback`
   - Selected OAuth Scopes: `api`, `refresh_token`, `web`
4. Copiar Client ID e Client Secret

### Credenciais

```env
SF_CLIENT_ID=your_client_id_from_salesforce
SF_CLIENT_SECRET=your_client_secret_from_salesforce
SF_REDIRECT_URI=https://api.reports.example.com/oauth/callback
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Com coverage
pytest --cov=src --cov-report=html

# Testes específicos
pytest tests/test_oauth_handler.py -v
```

## 📊 Logging

Logs estruturados em JSON com:
- timestamp
- service name
- log level
- trace_id para rastreamento
- contexto customizado

Exemplo:
```json
{
  "timestamp": "2026-08-16T10:30:45.123Z",
  "service": "mcp-client",
  "level": "INFO",
  "trace_id": "abc123def456",
  "message": "Token obtido com sucesso"
}
```

## 🔄 Fluxo OAuth

1. **Autorização**: User inicia OAuth → GET `/oauth/authorize`
2. **Redirecionamento**: Salesforce redireciona com `code`
3. **Callback**: POST `/oauth/callback` com code
4. **Token**: Recebe `access_token` e `refresh_token`
5. **Requisições**: Use `access_token` nas requisições
6. **Renovação**: POST `/oauth/refresh` quando necessário

## 🛠️ Troubleshooting

**Erro: "Credenciais inválidas"**
- Verificar SF_CLIENT_ID e SF_CLIENT_SECRET
- Confirmar que Connected App está ativa

**Erro: "Token expirado"**
- Usar refresh_token para renovar
- Automaticamente renovado antes de expirar

**Erro: "Salesforce API error"**
- Verificar logs estruturados
- Confirmar permissões na org Salesforce

## 📈 Próximos Passos

- [ ] Integração com Auth Service
- [ ] Cache de relatórios
- [ ] Rate limiting
- [ ] Monitoramento com Prometheus
- [ ] CI/CD pipeline

## 📖 Documentação

- OpenAPI/Swagger: http://localhost:3005/docs
- ReDoc: http://localhost:3005/redoc
- [Salesforce OAuth](https://developer.salesforce.com/docs/atlas.en-us.oauth_guidance.meta/oauth_guidance/)
