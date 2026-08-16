# Salesforce Reports System - CLAUDE.md

## Projeto

Sistema de relatórios Salesforce baseado em **microserviços** com **micro frontends**, logging estruturado e integração com **MCP Salesforce**.

**Status:** Planejamento → Implementação  
**Branch de Desenvolvimento:** `claude/analise-documentos-repositorio-8v7inv`  
**Repositório Principal:** `brunotrolo/Salesforce_CasesDashboards`  

---

## Visão Geral

Este projeto implementa uma arquitetura modular para criação e atualização de relatórios Salesforce, com ênfase em:

- ✅ **Sustentabilidade** — Código limpo, testável, documentado
- ✅ **Observabilidade** — Logging estruturado em todas as camadas
- ✅ **Escalabilidade** — Microserviços independentes
- ✅ **UX/Design** — Micro frontends com design consistency
- ✅ **Developer Experience** — Skills integradas para assistência

---

## Arquitetura

### Camada de Serviços

```
Salesforce (MCP)
    ↓
MCP Client (autenticação OAuth + CRUD)
    ↓
API Gateway
    ├─ Auth Service (JWT, RBAC)
    ├─ Report Service (orquestração)
    ├─ Data Service (transformação)
    └─ Cache Service (Redis)
    ↓
Logging Service (ELK Stack)
```

### Camada de Frontend

```
Dashboard FE      Builder FE        Analytics FE
(visualização)  → (criação/edição) ↔ (histórico)
    ↓                   ↓                ↓
API Gateway (shared)
```

### Separação por Domínio

- **Backend:** Python (FastAPI/Flask)
- **Frontend:** TypeScript (React/Vue)
- **Dados:** JSON + PostgreSQL (para histórico)
- **Cache:** Redis
- **Logs:** Elasticsearch (ou similar)

---

## Skills Integradas

### 1. Agent Skills
**URL:** https://github.com/addyosmani/agent-skills

- Geração automática de tests
- Análise de cobertura de código
- Refatoração assistida
- Detecção de padrões

**Como usar:**
```bash
claude /agent-skills suggest-tests --service report-service
claude /agent-skills analyze-coverage --target services/
```

### 2. UI/UX Pro Max Skill
**URL:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

- Design system management
- Component library setup
- Accessibility audits (WCAG)
- Responsive validation

**Como usar:**
```bash
claude /ui-ux setup-design-system frontends/
claude /ui-ux audit-accessibility frontends/dashboard-fe
```

### 3. Impeccable
**URL:** https://github.com/pbakaus/impeccable

- Code quality automation
- Linting (ESLint, Pylint)
- Pre-commit hooks
- CI/CD quality gates

**Como usar:**
```bash
claude /impeccable setup-linting services/
claude /impeccable quality-report --branch main
```

---

## Automação de Skills

As três skills estão configuradas para ativação automática via `.claude/skills-config.json`. 

### Fluxo Automático

**Ao começar trabalho em novo serviço:**
- Agent Skills detecta padrão anti-design
- Impeccable configura linting automaticamente
- Sugere estrutura de testes

**Ao fazer commit:**
- Pre-commit hook (Impeccable) valida qualidade
- Auto-formata código se necessário
- Bloqueia commit se quality < threshold

**Ao enviar PR:**
- Quality gates (Impeccable) verificam coverage
- Sugestões de testes via Agent Skills
- Audit de acessibilidade via UI/UX (se frontend)

### Setup Rápido de Skills

```bash
# Clonar e configurar todas as skills
bash scripts/setup-skills.sh

# Resultado:
# ✓ agent-skills clonado
# ✓ ui-ux-pro-max clonado  
# ✓ impeccable clonado
# ✓ Pre-commit hooks instalados
# ✓ Design system setup (optional)
```

Depois de setup, skills estarão disponíveis automaticamente.

### Exemplo de Workflow Automático

```bash
# 1. Checkout nova branch
git checkout -b claude/nova-feature

# 2. Escrever código
# ... seu desenvolvimento ...

# 3. Commit (Impeccable hook roda automaticamente)
git add .
git commit -m "feat(service): add feature"
# Pre-commit: ESLint ✓ | Pylint ✓ | Format ✓

# 4. Agent Skills sugere testes
# (aparece em comentário de PR via CI)

# 5. Push
git push origin claude/nova-feature

# 6. Quality gates automaticamente verificam:
# - Coverage (Agent Skills)
# - Code quality (Impeccable)
# - Accessibility (UI/UX, se frontend)
```

Para detalhes completos, ver: [SKILLS_INTEGRATION.md](./SKILLS_INTEGRATION.md)

---

## Estrutura de Diretórios

```
Salesforce_CasesDashboards/
├── services/
│   ├── mcp-client/              # Integração com Salesforce
│   │   ├── src/
│   │   │   ├── salesforce_connector.py
│   │   │   ├── report_operations.py
│   │   │   ├── data_models.py
│   │   │   └── error_handler.py
│   │   ├── tests/
│   │   │   ├── test_salesforce_connector.py
│   │   │   └── test_report_operations.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── report-service/          # Orquestração de relatórios
│   │   ├── src/
│   │   │   ├── report_manager.py
│   │   │   ├── report_validator.py
│   │   │   ├── report_cache.py
│   │   │   ├── models/
│   │   │   └── handlers/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── auth-service/            # Autenticação e autorização
│   │   ├── src/
│   │   │   ├── auth_manager.py
│   │   │   ├── jwt_handler.py
│   │   │   ├── rbac.py
│   │   │   └── oauth_handler.py
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── logging-service/         # Logging centralizado
│   │   ├── src/
│   │   │   ├── logger.py
│   │   │   ├── formatters.py
│   │   │   ├── handlers/
│   │   │   └── middleware/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   ├── data-service/            # Transformação de dados
│   ├── cache-service/           # Cache com Redis
│   ├── api-gateway/             # Roteamento
│   └── shared/                  # Utilitários compartilhados
│
├── frontends/
│   ├── dashboard-fe/            # Visualização
│   │   ├── src/
│   │   │   ├── components/
│   │   │   ├── pages/
│   │   │   ├── api/
│   │   │   ├── hooks/
│   │   │   └── App.tsx
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tailwind.config.js
│   │   └── Dockerfile
│   │
│   ├── builder-fe/              # Criação/edição
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   │
│   ├── analytics-fe/            # Análise
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   │
│   └── shared/                  # Componentes compartilhados
│       ├── components/
│       ├── hooks/
│       ├── types.ts
│       └── utils/
│
├── infra/
│   ├── docker-compose.yml       # Dev environment
│   ├── kubernetes/              # Production
│   │   ├── deployments/
│   │   ├── services/
│   │   └── configmaps/
│   └── terraform/               # IaC
│
├── docs/
│   ├── ARCHITECTURE.md          # Arquitetura geral
│   ├── SERVICES.md              # Detalhe de cada serviço
│   ├── LOGGING.md               # Sistema de logs
│   ├── DEPLOYMENT.md            # Como fazer deploy
│   ├── API.md                   # Documentação de APIs
│   └── TROUBLESHOOTING.md       # Problemas comuns
│
├── tests/
│   ├── integration/             # Testes de integração
│   ├── e2e/                     # Testes end-to-end
│   └── performance/             # Testes de performance
│
├── .github/workflows/
│   ├── ci.yml                   # CI pipeline
│   ├── deploy.yml               # Deploy automatizado
│   └── security-scan.yml        # Security audits
│
├── README.md                    # Documentação principal
├── CONTRIBUTING.md              # Guia de contribuição
├── Makefile                     # Comandos úteis
├── docker-compose.yml
└── .env.example
```

---

## Sistema de Logging

### Padrão Estruturado

Todos os logs devem seguir este formato JSON:

```json
{
  "timestamp": "2026-08-16T10:30:45.123Z",
  "service": "report-service",
  "level": "INFO",
  "trace_id": "abc123def456",
  "correlation_id": "xyz789",
  "message": "Report created successfully",
  "context": {
    "user_id": "u:12345",
    "report_id": "r:67890",
    "operation": "create",
    "duration_ms": 245
  },
  "error": null,
  "stack_trace": null
}
```

### Categorias de Log

| Categoria | Nível | Exemplos |
|-----------|-------|----------|
| API Requests | INFO | `POST /api/reports` |
| MCP Operations | DEBUG | Salesforce API calls |
| Errors | ERROR | Exceptions, failures |
| Cache | DEBUG | Cache hits/misses |
| Security | WARN | Unauthorized access |
| Performance | INFO | Slow queries (>500ms) |

### Acessar Logs

```bash
# Desenvolvimento (local)
tail -f logs/app.log | jq .

# Produção (ELK Stack)
# Acessar Kibana em http://elasticsearch:5601
# Buscar por trace_id: trace_id: "abc123def456"
```

---

## Integração com MCP Salesforce

### Autenticação

```python
from mcp_client import MCPClient

# Credenciais armazenadas em variáveis de ambiente
mcp = MCPClient(
    client_id=os.getenv("SF_CLIENT_ID"),
    client_secret=os.getenv("SF_CLIENT_SECRET"),
    refresh_token=os.getenv("SF_REFRESH_TOKEN")
)

# Conectar com Salesforce
await mcp.authenticate()
```

### Operações CRUD

```python
# Criar relatório
await mcp.create_or_update_file(
    path="/reports/new_report",
    content=report_config.to_json(),
    metadata={"type": "report", "version": "1.0"}
)

# Buscar relatório
report = await mcp.get_file_contents("/reports/report_id")

# Atualizar relatório
await mcp.create_or_update_file(
    path="/reports/report_id",
    content=updated_config.to_json()
)

# Deletar relatório
await mcp.delete_file("/reports/report_id")

# Listar relatórios
reports = await mcp.search_files("/reports", pattern="*.json")
```

---

## Guia de Desenvolvimento

### 1. Setup Local

```bash
# Clonar repositório
git clone <repo-url>
cd Salesforce_CasesDashboards

# Criar branch de trabalho
git checkout -b claude/analise-documentos-repositorio-8v7inv

# Instalar dependências (Python)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Instalar dependências (Node)
cd frontends/dashboard-fe
npm install

# Setup Docker
docker-compose up -d
```

### 2. Desenvolvimento de um Novo Serviço

```bash
# Usando Agent Skills
claude /agent-skills scaffold-service --name my-service --type python

# Estrutura criada:
services/my-service/
├── src/
│   ├── main.py
│   ├── models.py
│   ├── handlers.py
│   └── __init__.py
├── tests/
│   ├── test_handlers.py
│   └── test_main.py
├── Dockerfile
└── requirements.txt
```

### 3. Desenvolvimento de um Frontend

```bash
# Usando UI/UX Pro Max Skill
claude /ui-ux create-component --type dashboard --service reports

# Estrutura criada:
frontends/dashboard-fe/src/
├── components/
│   ├── ReportCard.tsx
│   ├── ReportCard.module.css
│   └── ReportCard.test.tsx
├── hooks/
│   └── useReports.ts
└── types/
    └── report.ts
```

### 4. Verificar Qualidade de Código

```bash
# Usando Impeccable
claude /impeccable lint --service report-service

# Executar testes
npm test  # Frontend
pytest    # Backend

# Coverage
npm run coverage
pytest --cov=services/

# Pre-commit hooks
pre-commit install
pre-commit run --all-files
```

### 5. Fazer Commit e Push

```bash
# Verificar status
git status

# Adicionar arquivos
git add services/report-service/

# Fazer commit (Impeccable fará linting automático)
git commit -m "feat(report-service): add create operation via MCP"

# Push para branch de desenvolvimento
git push origin claude/analise-documentos-repositorio-8v7inv
```

---

## Testes

### Executar Todos os Testes

```bash
# Backend
pytest services/ -v --cov=services/ --cov-report=html

# Frontend
npm run test --workspaces

# Integração
pytest tests/integration/ -v

# E2E
npm run test:e2e
```

### Cobertura Mínima

- **Backend:** 80% de cobertura
- **Frontend:** 75% de cobertura
- **Crítico:** Serviços de autenticação e logging = 95%

---

## Ambiente de Desenvolvimento

### Variáveis de Ambiente

Copiar `.env.example` para `.env` e preencher:

```bash
# Salesforce MCP
SF_CLIENT_ID=your_client_id
SF_CLIENT_SECRET=your_client_secret
SF_REFRESH_TOKEN=your_refresh_token

# Services
API_PORT=3000
LOGGING_LEVEL=DEBUG
CACHE_REDIS_URL=redis://localhost:6379

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=reports_user
DB_PASSWORD=secure_password
```

### Docker Compose (Dev)

```bash
# Iniciar stack completo
docker-compose up -d

# Serviços disponíveis:
# - Elasticsearch: http://localhost:9200
# - Kibana: http://localhost:5601
# - Redis: localhost:6379
# - PostgreSQL: localhost:5432
# - API: http://localhost:3000
```

---

## Pipelines de CI/CD

### GitHub Actions

**`.github/workflows/ci.yml`** - Executa a cada push/PR:
- Lint (ESLint, Pylint)
- Testes unitários
- Cobertura de código
- Security scan

**`.github/workflows/deploy.yml`** - Deploy automático ao fazer merge em `main`:
- Build Docker images
- Push para registry
- Deploy em Kubernetes
- Smoke tests em produção

---

## Contribuindo

### Padrão de Commits

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat:` Nova feature
- `fix:` Bug fix
- `refactor:` Refatoração sem mudança de comportamento
- `test:` Adição de testes
- `docs:` Mudanças na documentação
- `chore:` Tarefas de build, deps, etc

**Exemplo:**
```
feat(report-service): add caching layer for report queries

Implements Redis-based caching for frequently accessed reports.
Reduces API calls to Salesforce by ~85%.

Closes #123
```

### Code Review Checklist

- [ ] Código segue padrões de estilo (Impeccable)
- [ ] Testes implementados (cobertura ≥80%)
- [ ] Logs estruturados em DEBUG para troubleshooting
- [ ] Documentação atualizada (docstrings, README)
- [ ] Sem quebra de compatibilidade com versão anterior
- [ ] Performance validada (se aplicável)

---

## Links Úteis

- **Artifact do Plano:** [Arquitetura: Relatórios Salesforce](https://claude.ai/code/artifact/cd19a446-6d5f-450b-9749-99370c167ec1)
- **Análise de Documentos:** [Análise do Repositório](https://claude.ai/code/artifact/cd6d7e3b-1f4b-4e50-873a-8b4b53d633d1)
- **MCP Salesforce Docs:** [Documentação](https://github.com/modelcontextprotocol)
- **Agent Skills:** https://github.com/addyosmani/agent-skills
- **UI/UX Pro Max:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Impeccable:** https://github.com/pbakaus/impeccable

---

## FAQ

**P: Como começar o desenvolvimento?**  
R: Execute `make setup` para instalar dependências e configurar o ambiente local.

**P: Qual é o branch para trabalho novo?**  
R: `claude/analise-documentos-repositorio-8v7inv` (já está em uso)

**P: Como acessar logs em produção?**  
R: Todos os logs vão para Elasticsearch. Acesse Kibana e busque por `trace_id` ou `correlation_id`.

**P: Como fazer deploy?**  
R: Faça merge em `main` e o GitHub Actions faz deploy automaticamente via Kubernetes.

**P: Qual é a cobertura de testes esperada?**  
R: Mínimo 80% para backend, 75% para frontend, 95% para serviços críticos.

---

## Status do Projeto

- [x] Planejamento e arquitetura
- [x] Documentação de referência
- [x] Fase 1: Setup de infraestrutura ✅
- [ ] Fase 2: MCP Client + Auth Service
- [ ] Fase 3: Logging Service
- [ ] Fase 4: Report Service
- [ ] Fase 5: Dashboard Frontend
- [ ] Fase 6: Builder Frontend
- [ ] Fase 7: Analytics Frontend
- [ ] Fase 8: Testes e hardening
- [ ] Fase 9: Deploy e monitoramento
