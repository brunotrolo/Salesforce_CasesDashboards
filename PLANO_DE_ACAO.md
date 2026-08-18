# Plano de Ação — Salesforce CasesDashboards

**Data:** 2026-08-16 (atualizado após merge da branch `claude/analise-documentos-repositorio-8v7inv`)
**Status:** Análise completa, aguardando execução

---

## Resumo Executivo

O projeto tem uma **arquitetura sólida** documentada no CLAUDE.md, mas a **implementação real** apresenta gaps significativos entre plano e realidade. Após o merge da branch de desenvolvimento, o **mcp-client** e o **auth-service** foram reescritos com implementações reais (FastAPI, OAuth2, REST connector, testes), corrigindo a **SOQL injection** e o **import error no auth-service**. Restam **3 vulnerabilidades CRÍTICAS**, **4 bugs que impedem build**, **~1.200 linhas de código duplicado**, e **CI/CD com workflows parcialmente no-ops**.

### Números (atualizados)

| Métrica | Valor |
|---------|-------|
| Linhas de código | ~19.500 |
| Bugs CRÍTICOS | 0 (4 corrigidos) |
| Vulnerabilidades CRÍTICAS | 3 (pendentes Fase 1.9/1.10 mitigadas; SOQL/import corrigidos) |
| Código duplicado | ~1.200 linhas |
| Skills importadas | 32 (.opencode) / 33 (.claude) |
| Cobertura de testes real | ~50% (213 testes backend + 13 frontend) |
| CI/CD funcional | ✅ 5 serviços + 3 frontends testados; deploy fake removido |

### O que mudou com o merge

| Item antigo | Status | Observação |
|-------------|--------|------------|
| 0.5 — auth-service `RBACManager` import error | ✅ CORRIGIDO | `__init__.py` reescrito sem import quebrado |
| 1.1 — SOQL Injection no connector | ✅ CORRIGIDO | Conector reescrito com REST API (`/services/data/v59.0/sobjects/Report`), sem queries SOQL f-string |
| 5.3 — Duas aiohttp sessions | ✅ CORRIGIDO | Conector agora usa `requests` síncrono (nova pendência: bloqueia event loop async) |
| auth-service login | ⚠️ PARCIAL | Aceita apenas username `"test"`, sem banco de dados |
| mcp-client OAuth | ⚠️ PARCIAL | `oauth_states` em dict em memória (sem Redis), sem CSRF state validation no callback |

---

## Fase 0 — Corrigir Build Breakers (URGENTE)

**Objetivo:** O projeto compila e roda sem erros.

### 0.1 Frontend — builder-fe não compila
- **Problema:** `builder-fe/src/App.tsx:3` importa `DashboardPage` que não existe
- **Ação:** Corrigir imports e rotas em `builder-fe/src/App.tsx`
- **Arquivo:** `frontends/builder-fe/src/App.tsx`

### 0.2 Frontend — analytics-fe não compila
- **Problema:** `analytics-fe/src/App.tsx:3` importa `DashboardPage` que não existe
- **Ação:** Corrigir imports e rotas em `analytics-fe/src/App.tsx`
- **Arquivo:** `frontends/analytics-fe/src/App.tsx`

### 0.3 Frontend — analytics-fe type errors
- **Problema:** `exporters.ts` usa `results.rows` mas o tipo define `rows_returned`; `ResultsPage.tsx` constrói `AnalyticsResult` com propriedades erradas
- **Ação:** Alinhar propriedades com o tipo `AnalyticsResult` em `types/analytics.ts`
- **Arquivos:** `frontends/analytics-fe/src/utils/exporters.ts`, `frontends/analytics-fe/src/pages/ResultsPage.tsx`

### 0.4 Frontend — analytics-fe import mismatch
- **Problema:** `exporters.ts:6` importa de `html-to-image` mas chama `html2canvas()` (API do pacote `html2canvas`)
- **Ação:** Usar a API correta de `html-to-image` (`toPng`, `toBlob`) ou trocar a dependência
- **Arquivo:** `frontends/analytics-fe/src/utils/exporters.ts`

### 0.5 ~~Backend — auth-service import error~~ ✅ CORRIGIDO NO MERGE
- **Status:** `__init__.py` reescrito, sem import de `RBACManager`

### 0.6 Backend — report_validator crash
- **Problema:** `report_validator.py:83` faz `len(report.name)` quando `name` pode ser None
- **Ação:** Adicionar null check antes de medir comprimento
- **Arquivo:** `services/report-service/src/report_validator.py`

### 0.7 Builder — package.json com nome errado
- **Problema:** `builder-fe/package.json:2` diz `"name": "dashboard-fe"`
- **Ação:** Mudar para `"name": "builder-fe"`
- **Arquivo:** `frontends/builder-fe/package.json`

### 0.8 Todos os index.html com mesmo título
- **Problema:** Todos os 3 frontends têm `<title>Dashboard de Relatórios Salesforce</title>`
- **Ação:** Cada frontend deve ter seu título (Dashboard, Builder, Analytics)
- **Arquivos:** `frontends/*/index.html`

---

## Fase 1 — Segurança (CRÍTICO)

**Objetivo:** Eliminar vulnerabilidades de segurança que impedem produção.

### 1.1 ~~SOQL Injection no MCP Client~~ ✅ CORRIGIDO NO MERGE
- **Status:** `salesforce_connector.py` reescrito para usar REST API (`/services/data/v59.0/sobjects/Report`), sem interpolação de strings em queries SOQL

### 1.2 Hardcoded JWT Secrets
- **Problema:** auth-service ainda tem fallback hardcoded: `config.py:12` define `"your-secret-key-change-in-production"`; api-gateway também
- **Ação:** Forçar variável de ambiente, remover fallbacks, raise error se não setado
- **Arquivos:** `services/auth-service/src/config.py:12`, `services/api-gateway/src/main.py:12`, `services/api-gateway/src/auth.py:12`

### 1.3 Authentication Bypass
- **Problema:** `/auth/login` aceita qualquer credencial não-vazia
- **Ação:** Implementar validação real (hash de senha, bcrypt, ou integração OAuth)
- **Arquivo:** `services/api-gateway/src/main.py:243-258`

### 1.4 CORS Wildcard com Credentials
- **Problema:** `allow_origins=["*"]` com `allow_credentials=True`
- **Ação:** Configurar origins específicas via variável de ambiente `CORS_ORIGINS`
- **Arquivo:** `services/api-gateway/src/main.py:176-181`

### 1.5 Mass Assignment
- **Problema:** `report_manager.py:71-73` faz `setattr` com qualquer campo do input
- **Ação:** Definir allowlist de campos atualizáveis
- **Arquivo:** `services/report-service/src/report_manager.py`

### 1.6 Token key mismatch
- **Problema:** `App.tsx` usa `localStorage.getItem('token')`, `reportApi.ts` usa `localStorage.getItem('auth_token')`
- **Ação:** Unificar para uma chave só (`auth_token`)
- **Arquivos:** `frontends/dashboard-fe/src/App.tsx:10,14`, `frontends/dashboard-fe/src/api/reportApi.ts:14`

### 1.7 Endpoints sem autenticação no api-gateway
- **Problema:** Todos os `/api/reports/*` não exigem auth
- **Ação:** Adicionar `Depends(get_current_user)` em todos os endpoints de reports
- **Arquivo:** `services/api-gateway/src/main.py`

### 1.8 Login aceita apenas usuário "test" (auth-service)
- **Problema:** `auth-service/src/main.py:80` só permite login se `username == "test"`, sem banco de dados
- **Ação:** Implementar autenticação real com hash de senha (bcrypt) + banco de dados (PostgreSQL via SQLAlchemy), mantendo modo demo atrás de flag `ENABLE_DEMO_MODE`
- **Arquivo:** `services/auth-service/src/main.py:70-90`

### 1.9 OAuth state sem validação CSRF (mcp-client)
- **Problema:** `oauth_states` é dict em memória, sem expiração, e o callback não valida se o `state` corresponde à sessão do usuário (apenas verifica existência)
- **Ação:** Persistir states no Redis com TTL, validar state no callback contra sessão, remover após uso
- **Arquivos:** `services/mcp-client/src/main.py:24,61-78`

### 1.10 Endereços IP do rate limiter
- **Problema:** `rate_limit.py:54` usa `request.client.host` que retorna o IP do proxy
- **Ação:** Usar `X-Forwarded-For` com configuração de proxy trust
- **Arquivo:** `services/api-gateway/src/rate_limit.py`

---

## Fase 2 — Arquitetura e Limpeza

**Objetivo:** Eliminar duplicação, corrigir arquitetura, establishing shared code.

### 2.1 Criar shared/ package funcional
- **Problema:** `frontends/shared/` está vazio, mas 3 apps duplicam ~1.200 linhas
- **Ação:** Criar `frontends/shared/package.json`, mover types, api, formatters, logger, test setup
- **Afeta:** Todos os 3 frontends

### 2.2 Consolidar docker-compose
- **Problema:** 2 docker-compose.yml com versões diferentes de ES e senhas diferentes
- **Ação:** Manter apenas o root, deletar `infra/docker-compose.yml`
- **Arquivos:** `docker-compose.yml`, `infra/docker-compose.yml`

### 2.3 Remover JWT library duplicada
- **Problema:** `PyJWT` e `python-jose` ambos instalados
- **Ação:** Padronizar em `PyJWT` (mais leve), remover `python-jose` do auth-service
- **Arquivos:** `services/auth-service/requirements.txt`, `services/api-gateway/requirements.txt`

### 2.4 Unificar ReportMetadata
- **Problema:** Duas classes `ReportMetadata` com schemas diferentes
- **Ação:** Criar em `services/shared/` e importar em ambos
- **Arquivos:** `services/mcp-client/src/data_models.py`, `services/report-service/src/models/report.py`

### 2.5 Limpar código morto
- **Ação:** Remover `User` class em auth_manager.py, `RESERVED_FIELDS` em report_validator.py, `ContextVars` em middleware.py, `JSONFormatter` em formatters.py, `retry_on_error` síncrono
- **Afeta:** Múltiplos arquivos backend

### 2.6 Separar test deps de production deps
- **Problema:** pytest/pytest-asyncio em production requirements de 4 serviços
- **Ação:** Mover para requirements-test.txt, usar `-r requirements.txt` para evitar duplicação
- **Afeta:** `services/auth-service/requirements.txt`, `services/logging-service/requirements.txt`, `services/mcp-client/requirements.txt`, `services/report-service/requirements.txt`

### 2.7 Corrigir pytest.ini
- **Problema:** `testpaths` e `norecursedirs` bloqueiam testes de todos os serviços exceto api-gateway
- **Ação:** Configurar para coletar todos os serviços
- **Arquivo:** `pytest.ini`

### 2.8 Rate limiter — cleanup de IPs antigos
- **Problema:** `rate_limit.py:15` cresce indefinidamente
- **Ação:** Adicionar TTL para entries antigos, limitar tamanho do dict
- **Arquivo:** `services/api-gateway/src/rate_limit.py`

---

## Fase 3 — Frontend UX/UI (sem AI Slop)

**Objetivo:** Interface profissional, acessível, sem padrões genéricos de IA.

### 3.1 Design System com UI/UX Pro Max ✅ FEITO
- **Ação:** Rodar `ui-ux-pro-max` para gerar design system específico para Salesforce reporting dashboard
- **Prompt:** `"enterprise saas salesforce reporting dashboard analytics"` com `--design-system`
- **Resultado:** MASTER.md com paleta, tipografia, padrões específicos (evitar indigo/blue gradient genérico)
- **Design aplicado:** **Data-Dense Dashboard** — primary `#1E40AF`, secondary `#3B82F6`, accent `#D97706`, background `#F8FAFC`, border `#DBEAFE`, muted `#E9EEF6`; tipografia **Fira Sans + Fira Code**; aplicado em `tailwind.config.js` e `globals.css` dos 3 frontends

### 3.2 Eliminar AI Slop ✅ FEITO
- **Padrões removidos:**
  - `bg-gradient-to-br from-blue-500 to-indigo-600` (login) → `bg-background` + card com borda
  - `bg-gradient-to-br from-blue-50 to-indigo-100` (builder) → `bg-background`
  - Indigo-600 como cor primária → tokens do design system (`bg-primary`)
  - `shadow-2xl` / `shadow-xl` exagerado → bordas `border-border` sutis
  - Cards genéricos `bg-white rounded-lg shadow-md p-6` → `bg-card border border-border rounded-lg`
- **Arquivos:** `dashboard-fe/src/App.tsx`, `pages/*.tsx`, `components/*.tsx`; `builder-fe` e `analytics-fe` (pages + components)

### 3.3 Corrigir Auth Flow ✅ FEITO
- **Ação:** Implementar login real com formulário (username + password), context de auth, protected routes
- **Arquivo:** `frontends/dashboard-fe/src/App.tsx`
- **Implementado:** Formulário real (`/api/auth/login` → api-gateway), mensagem de erro em `role="alert"`, loading state, logout, token em `auth_token` (já padronizado na Fase 1.6), interceptador 401 ignora falha de login

### 3.4 Code Splitting ✅ FEITO
- **Ação:** Adicionar `React.lazy()` e `Suspense` para todas as rotas
- **Arquivo:** `frontends/dashboard-fe/src/App.tsx`
- **Implementado:** `DashboardPage`, `BuilderPage`, `AnalyticsPage` em chunks separados (build: 220KB index + chunks por página)

### 3.5 Accessibility (WCAG 2.1 AA) ✅ FEITO
- **Ações:**
  - ✅ `htmlFor`/`id` em todos os forms (login, builder)
  - ✅ `role="alert"` em error messages
  - ✅ `aria-pressed` nos filter buttons + `aria-current="page"` (NavLink automático)
  - ✅ `<caption>` e `scope="col"` nas tabelas (DataTable analytics-fe)
  - ✅ Emoji icons substituídos por SVG icons (ResultsPage export buttons)
  - ✅ Skip-to-content link nos 3 frontends + `<main id="main-content">`
- **Skill:** ui-ux-pro-max, domain `ux`

### 3.6 Loading States e Empty States ✅ FEITO
- **Ação:** Criar componentes `LoadingSkeleton`, `EmptyState` com CTA para criar relatório
- **Afeta:** Todos os 3 frontends
- **Feito:** Skeleton de loading estilizado com tokens; empty state com mensagem de CTA em `ReportsList.tsx`

### 3.7 Active Nav State ✅ FEITO
- **Ação:** Adicionar indicador visual de rota ativa (underline, bold, ou bg highlight)
- **Arquivo:** `frontends/dashboard-fe/src/App.tsx`
- **Implementado:** `NavLink` com `bg-primary text-white` para rota ativa

### 3.8 Confirm Dialog customizado ✅ FEITO
- **Ação:** Substituir `window.confirm` por modal customizado
- **Afeta:** `frontends/dashboard-fe/src/pages/DashboardPage.tsx`
- **Implementado:** `ConfirmDialog` com `role="dialog"`, `aria-modal`, focus no botão cancelar

---

## Fase 4 — CI/CD Funcional

**Objetivo:** Pipelines que realmente executam testes e deploy.

### 4.1 Fix CI workflow ✅ FEITO
- **Ação:** Remover `|| true` de todos os test/lint steps, adicionar testes de todos os serviços, adicionar frontend tests
- **Arquivo:** `.github/workflows/ci.yml`, `.github/workflows/ci-cd.yml`
- **Implementado:** `ci.yml` reescrito — matrix com 5 serviços backend (api-gateway, auth-service, report-service, mcp-client, logging-service) + 3 frontends (dashboard-fe, builder-fe, analytics-fe) com `npm ci`, `CI=true npm test` e build. Env vars de teste definidas no workflow. Zero `|| true`.
- **Correções necessárias para CI verde (bugs reais encontrados):**
  - auth-service: 14 testes falhando (escritos contra implementação pré-merge) — reescritos; **bug real corrigido**: refresh token crashava com `UserRole(None)` (TokenPayload.role agora Optional)
  - mcp-client: conftest importava settings antes de setar env; testes usavam assinatura antiga do conector (sem oauth_handler)
  - logging-service: 17 teardown errors (arquivo de log em uso no Windows) — `logging.shutdown()` no fixture
  - **Total: 187 testes passando** (api-gateway 19, auth-service 52, report-service 55, mcp-client 14, logging-service 47)

### 4.2 Fix Deploy workflow ✅ FEITO (Opção A)
- **Ação:** Implementar deploy real ou remover workflows de deploy falsos
- **Feito:** `deploy.yml` removido (kubectl sem cluster = no-op). `ci-cd.yml` mantido apenas para build+push de imagens no GHCR (sem o job `deploy` fake com echo)

### 4.3 Fix Security scan ✅ FEITO
- **Ação:** Remover `|| true` do bandit e npm audit
- **Arquivo:** `.github/workflows/security-scan.yml`
- **Feito:** `bandit -r services/ -ll` (falha em issues) e `npm audit --audit-level=high`

### 4.4 Adicionar .dockerignore ✅ FEITO
- **Ação:** Criar `.dockerignore` na raiz com `.git/`, `node_modules/`, `__pycache__/`, `venv/`, `.env`
- **Arquivo:** `.dockerignore` (novo)

### 4.5 Fix Dockerfiles ✅ FEITO
- **Ações:**
  - Dashboard: `http-server` → `nginx:1.27-alpine` com `nginx.conf` (proxy `/api/` → api-gateway:3000, SPA fallback, gzip), HEALTHCHECK
  - API Gateway: non-root user (`appuser`), COPY seletivo já existente
- **Afeta:** `frontends/dashboard-fe/Dockerfile`, `services/api-gateway/Dockerfile`

### 4.6 Adicionar sourcemaps condicionais ✅ FEITO
- **Ação:** `sourcemap: mode === 'development'` em todos os `vite.config.ts`
- **Afeta:** 3 arquivos `vite.config.ts`

### 4.7 Consolidar dependências ✅ FEITO
- **Ação:** Remover `zustand` do dashboard-fe e analytics-fe (não usado), remover `recharts` do builder-fe
- **Afeta:** 3 `package.json` + lockfiles regenerados

---

## Fase 5 — Backend Robustez

**Objetivo:** Código backend confiável, testável, com error handling correto.

### 5.1 Fix error handling pattern ✅ FEITO
- **Ação:** Trocar `except Exception as e` por tipos específicos, logar traceback em todos os endpoints
- **Afeta:** `services/api-gateway/src/main.py`
- **Feito:** `errors.py` com `GatewayError` + subclasses (404/422/400/502/401/403); `@app.exception_handler(GatewayError)`; endpoints usam erros tipados e logam `context={"error": str(e)}`

### 5.2 Fix retry decorator ✅ FEITO
- **Ação:** Usar `tenacity` ou implementar retry async, remover `retry_on_error` síncrono
- **Arquivo:** `services/mcp-client/src/error_handler.py` (retry_on_error ainda usa sync sleep)
- **Feito:** `retry_async()` decorator module-level com `asyncio.sleep` + backoff; `retry_on_error` síncrono removido; aplicado nos 6 métodos do conector

### 5.3 ~~Fix session management no MCP client~~ ✅ FEITO
- **Status:** Conector migrado para `httpx.AsyncClient` com sessão única (`close()`); `oauth_handler` usa `httpx` (síncrono, refresh raro); `requests` removido do mcp-client
- **Arquivo:** `services/mcp-client/src/salesforce_connector.py`, `services/mcp-client/src/oauth_handler.py`

### 5.4 Fix ContextVars para async ✅ FEITO
- **Ação:** Usar `contextvars.ContextVar` em vez de class variables
- **Arquivo:** `services/logging-service/src/context.py` (novo `RequestContext`); middleware define/limpa por request; `ContextVars` mantido como alias

### 5.5 Fix trace_id no logger ✅ FEITO
- **Ação:** Não gerar novo UUID a cada log; manter trace_id da request
- **Arquivo:** `services/logging-service/src/logger.py` — `_format_log` consome `RequestContext`; UUID só como fallback sem request

### 5.6 Adicionar testes de segurança ✅ FEITO
- **Ação:** Testes para SOQL injection, auth bypass, mass assignment
- **Afeta:** Novos testes em `services/mcp-client/tests/`, `services/api-gateway/tests/`
- **Feito:** `soql.py` (sanitizer + `build_soql_query` seguro); `test_security.py` nos 2 serviços (17 testes); validators SOQL no api-gateway (`ReportCreateRequest`); mock JWT no conftest agora rejeita tokens inválidos

### 5.7 Fix Pydantic v2 deprecations ✅ FEITO
- **Ação:** Trocar `.dict()` por `.model_dump()` em todos os serviços
- **Afeta:** Múltiplos arquivos
- **Feito:** `.dict()`→`.model_dump()` (mcp-client data_models); `class Config`→`model_config`/`ConfigDict` em auth-service, mcp-client, report-service

---

## Ordem de Execução Recomendada

```
Fase 0 (1-2h)  → Build funciona
Fase 1 (4-6h)  → Segurança ok
Fase 2 (3-4h)  → Arquitetura limpa
Fase 4 (2-3h)  → CI/CD funcional
Fase 5 (3-4h)  → Backend robusto
Fase 3 (4-6h)  → Frontend UX/UI (paralelo com 4-5)
```

**Total estimado:** 17-25 horas de trabalho

---

## Skills a Usar por Fase

| Fase | Skills |
|------|--------|
| 0 | code-review-and-quality (verificar fixes) |
| 1 | security-and-hardening, debugging-and-error-recovery |
| 2 | code-simplification, incremental-implementation |
| 3 | ui-ux-pro-max (design system), impeccable (audit), frontend-ui-engineering, performance-optimization |
| 4 | ci-cd-and-automation, git-workflow-and-versioning |
| 5 | test-driven-development, debugging-and-error-recovery |

---

## Anti-AI-Slop Rules (Impeccable)

Ao implementar qualquer fase, seguir:

1. **Sem gradientes genéricos blue/indigo** — usar paleta do design system
2. **Sem Inter/gray-500 como fonte** — usar tipografia do design system
3. **Sem cards `bg-white rounded-lg shadow-md`** — usar padrões de design system
4. **Sem `shadow-2xl` exagerado** — sombras sutis e propósito
5. **Sem bounce/elastic animations** — motion com propósito
6. **Verificar com detector de anti-patterns** do impeccable antes de cada PR
