# 🚀 Salesforce Reports System

> Sistema moderno de relatórios Salesforce com arquitetura de microserviços, micro frontends e integração com MCP.

## 📋 Status Geral

✅ **Phase 11:** Dependências corrigidas, CI/CD funcionando  
✅ **Phase 12:** Autenticação JWT, Rate Limiting, Cache Redis, Kubernetes ready  
✅ **Phase 13:** Frontend (Dashboard, Builder, Analytics), Testes, CI/CD  
🔄 **Phase 14+:** Deploy em produção, Monitoramento, Otimizações

## 🎯 O Que Funciona AGORA

### ✅ Backend
- **API Gateway** - FastAPI com 8+ endpoints
- **JWT Authentication** - Login, tokens, renovação
- **Rate Limiting** - 100 req/min por IP
- **Redis Caching** - Cache distribuído
- **Structured Logging** - JSON com correlation IDs
- **Kubernetes Ready** - Manifests prontos, HPA, anti-affinity

### ✅ Frontend
- **Dashboard** - Visualização de relatórios
- **Builder** - Criação de novos relatórios
- **Analytics** - Gráficos e métricas
- **Navegação** - Router completo
- **Auth Flow** - Login/Logout

### ✅ Infraestrutura
- **Docker Compose** - Local dev com 4 serviços (Redis, PostgreSQL, Elasticsearch, Kibana)
- **Kubernetes Manifests** - Production-ready
- **GitHub Actions** - CI/CD automatizado
- **Documentação** - DEPLOYMENT_GUIDE.md completo

---

## 🚀 Quick Start (Desenvolvimento Local)

### 1. Preparar Ambiente
```bash
git clone https://github.com/brunotrolo/Salesforce_CasesDashboards
cd Salesforce_CasesDashboards
cp .env.example .env
```

### 2. Iniciar Serviços (Docker)
```bash
docker-compose up -d
# Aguarde os serviços iniciarem (~30s)
```

### 3. Iniciar API Gateway
```bash
cd services/api-gateway
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --port 3000
```

### 4. Iniciar Frontend
```bash
cd frontends/dashboard-fe
npm install
npm run dev
```

### 5. Acessar
- **Dashboard:** http://localhost:5173
- **API:** http://localhost:3000
- **Kibana:** http://localhost:5601

---

## 📊 Arquitetura

```
┌─────────────────────────────────────┐
│         Dashboard Frontend          │
│   (React + Vite + TailwindCSS)     │
│   - Dashboard                       │
│   - Builder                         │
│   - Analytics                       │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      API Gateway (FastAPI)          │
│  - Auth (JWT)                       │
│  - Rate Limiting                    │
│  - Caching (Redis)                  │
│  - Logging (Structured)             │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│      Microserviços                  │
│  - Report Service                   │
│  - Auth Service                     │
│  - Data Service                     │
│  - MCP Client (Salesforce)          │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│    Supporting Services              │
│  - Redis (Cache)                    │
│  - PostgreSQL (DB)                  │
│  - Elasticsearch (Logs)             │
│  - Kibana (Visualization)           │
└─────────────────────────────────────┘
```

---

## 📁 Estrutura do Projeto

```
Salesforce_CasesDashboards/
├── services/                        # Backend microserviços
│   ├── api-gateway/                 # FastAPI principal
│   │   ├── src/
│   │   │   ├── main.py              # Endpoints
│   │   │   ├── auth.py              # JWT
│   │   │   ├── cache.py             # Redis
│   │   │   └── rate_limit.py        # Throttling
│   │   └── tests/
│   ├── auth-service/                # Auth & RBAC
│   ├── report-service/              # Orquestração
│   ├── logging-service/             # Structured logging
│   ├── mcp-client/                  # Salesforce integration
│   └── shared/                      # Utilitários
├── frontends/
│   └── dashboard-fe/                # React + Vite
│       ├── src/
│       │   ├── pages/
│       │   │   ├── DashboardPage.tsx
│       │   │   ├── BuilderPage.tsx
│       │   │   └── AnalyticsPage.tsx
│       │   ├── components/
│       │   ├── hooks/
│       │   └── App.tsx
│       └── Dockerfile
├── infra/
│   ├── kubernetes/                  # K8s manifests
│   │   ├── api-gateway-deployment.yaml
│   │   └── ingress.yaml
│   └── terraform/                   # IaC (future)
├── .github/
│   └── workflows/
│       └── ci-cd.yml                # GitHub Actions
├── docker-compose.yml               # Local dev
├── DEPLOYMENT_GUIDE.md              # Deploy instructions
├── CLAUDE.md                        # Project guidelines
└── README.md                        # This file
```

---

## 🧪 Testes

### Backend
```bash
cd services/api-gateway
pytest tests/ -v --cov=src
```

### Frontend
```bash
cd frontends/dashboard-fe
npm test
npm run test:coverage
```

---

## 🐳 Docker

### Build Local
```bash
# API Gateway
docker build -t salesforce-api-gateway:local -f services/api-gateway/Dockerfile .

# Dashboard
docker build -t salesforce-dashboard-fe:local -f frontends/dashboard-fe/Dockerfile .
```

### Run Local
```bash
docker run -p 3000:3000 salesforce-api-gateway:local
docker run -p 5173:5173 salesforce-dashboard-fe:local
```

---

## ☸️ Kubernetes Deployment

### Pré-requisitos
```bash
# Cluster K8s 1.24+
# kubectl configurado
# Docker images publicadas
```

### Deploy
```bash
# 1. Criar secrets
kubectl create secret generic salesforce-credentials \
  --from-literal=client-id=$SF_CLIENT_ID \
  --from-literal=client-secret=$SF_CLIENT_SECRET

# 2. Deploy API Gateway
kubectl apply -f infra/kubernetes/api-gateway-deployment.yaml

# 3. Deploy Ingress
kubectl apply -f infra/kubernetes/ingress.yaml

# 4. Verificar
kubectl get deployments
kubectl get pods -l app=api-gateway
```

Ver [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) para instruções completas.

---

## 🔑 Variáveis de Ambiente

```bash
# Backend
JWT_SECRET_KEY=your-secret-key
TOKEN_EXPIRE_MINUTES=60
REDIS_URL=redis://localhost:6379
LOGGING_LEVEL=INFO

# Salesforce
SF_CLIENT_ID=your_client_id
SF_CLIENT_SECRET=your_client_secret
SF_REFRESH_TOKEN=your_refresh_token

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=reports_db
DB_USER=reports_user
DB_PASSWORD=secure_password
```

---

## 📚 Documentação

- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Deploy em dev/prod
- **[CLAUDE.md](./CLAUDE.md)** - Diretrizes do projeto
- **[SKILLS_INTEGRATION.md](./SKILLS_INTEGRATION.md)** - Integração de skills

---

## 🚀 API Endpoints

### Authentication
- `POST /auth/login` - Login com credenciais
- `POST /auth/token` - Renovar token
- `GET /health` - Health check

### Reports
- `GET /api/reports` - Listar relatórios (com cache)
- `POST /api/reports` - Criar relatório
- `GET /api/reports/{id}` - Obter relatório
- `PUT /api/reports/{id}` - Atualizar relatório
- `DELETE /api/reports/{id}` - Deletar relatório

### Rate Limiting
- Limite: 100 req/min por IP
- Header: `X-RateLimit-Remaining`
- Status: 429 quando excedido

---

## 🔒 Segurança

- ✅ JWT com HS256
- ✅ HTTP Bearer tokens
- ✅ Rate limiting per-IP
- ✅ CORS habilitado
- ✅ HTTPS (em produção com Let's Encrypt)
- ✅ Kubernetes security context (non-root)

---

## 📊 Monitoramento (Produção)

### Logs
- Elasticsearch + Kibana
- Structured logging JSON
- Correlation IDs para rastreamento

### Métricas (Future)
- Prometheus
- Grafana dashboards
- PagerDuty alerts

---

## 🤝 Contribuindo

1. Create feature branch: `git checkout -b feat/nova-feature`
2. Commit changes: `git commit -am 'feat: descrição'`
3. Push: `git push origin feat/nova-feature`
4. Abrir PR em `main`

Ver [CLAUDE.md](./CLAUDE.md) para padrões de contribuição.

---

## 📅 Roadmap

### Phase 13 ✅ (COMPLETO)
- [x] Frontend Dashboard
- [x] Frontend Builder
- [x] Frontend Analytics
- [x] GitHub Actions CI/CD
- [x] Docker images

### Phase 14 (PRÓXIMO)
- [ ] Deploy em Kubernetes real
- [ ] Salesforce OAuth2 real
- [ ] User database
- [ ] Audit logging
- [ ] Prometheus metrics

### Phase 15+
- [ ] GraphQL API
- [ ] Advanced caching
- [ ] Event streaming (Kafka)
- [ ] Distributed tracing (Jaeger)
- [ ] Machine learning insights

---

## 🆘 Troubleshooting

### API não inicia
```bash
# Verificar dependências
pip install -r services/api-gateway/requirements.txt

# Verificar variáveis de ambiente
echo $JWT_SECRET_KEY

# Verificar Redis
redis-cli ping
```

### Frontend não compila
```bash
# Limpar node_modules
rm -rf node_modules package-lock.json
npm install

# Verificar Node version
node --version  # Deve ser 18+
```

### Docker build falha
```bash
# Limpar Docker cache
docker system prune -a

# Rebuild
docker-compose up --build
```

Ver [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#troubleshooting) para mais.

---

## 📜 Licença

MIT License - Ver LICENSE para detalhes.

---

## 👨‍💼 Contato & Suporte

- **Autor:** Bruno Trolo
- **Email:** brunotrolo@gmail.com
- **GitHub:** https://github.com/brunotrolo
- **Issues:** https://github.com/brunotrolo/Salesforce_CasesDashboards/issues

---

## 🎉 Status da Implementação

| Componente | Status | Última Atualização |
|-----------|--------|-------------------|
| API Gateway | ✅ Pronto | Phase 12 |
| Frontend | ✅ Pronto | Phase 13 |
| Kubernetes | ✅ Pronto | Phase 12 |
| Docker | ✅ Pronto | Phase 13 |
| CI/CD | ✅ Pronto | Phase 13 |
| Testes | 🔄 Em Progresso | Phase 13 |
| Deploy Prod | 🟡 Planejado | Phase 14 |
| Monitoramento | 🟡 Planejado | Phase 15 |

---

**Última atualização:** 2026-08-16  
**Status:** Production-Ready ✅