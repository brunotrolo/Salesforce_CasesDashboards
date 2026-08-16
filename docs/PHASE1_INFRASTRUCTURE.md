# Phase 1: Infrastructure Setup

**Status:** ✅ In Progress  
**Milestone:** Infrastructure foundation for microservices  
**Duration:** 1-2 weeks  

---

## Overview

Phase 1 establishes the foundational infrastructure required for the Salesforce Reports System. This includes:

- **Docker Compose** for local development
- **Kubernetes** manifests for production deployment
- **Environment configuration** management
- **Database initialization** (PostgreSQL)
- **Logging stack** (Elasticsearch + Kibana)
- **Caching layer** (Redis)
- **API Gateway** routing

---

## Components

### 1. Docker Compose (Local Development)

**File:** `docker-compose.yml`

#### Services
- **Redis** (cache)
  - Port: 6379
  - Health: Redis CLI ping
  - Volume: `redis-data`

- **PostgreSQL** (main database)
  - Port: 5432
  - Health: `pg_isready` check
  - Database: `reports_db`
  - Volume: `postgres-data`

- **Elasticsearch** (logging/search)
  - Port: 9200
  - Health: Cluster health check
  - Volume: `elasticsearch-data`

- **Kibana** (log visualization)
  - Port: 5601
  - Health: API status check
  - Depends: Elasticsearch

#### Usage

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# View service status
docker-compose ps
```

### 2. Kubernetes Infrastructure

**Location:** `infra/kubernetes/`

#### Namespace & RBAC
- **File:** `namespace.yaml`
- Creates `salesforce-reports` namespace
- Resource quotas: 10 CPU, 20Gi memory
- Network policies for pod-to-pod communication

#### Infrastructure Deployments

**a) Redis**
- **File:** `deployments/redis-deployment.yaml`
- Replicas: 1
- Memory: 512Mi limit
- Persistence: EmptyDir (development)
- Service: ClusterIP (internal)

**b) PostgreSQL**
- **File:** `deployments/postgres-deployment.yaml`
- Replicas: 1
- Memory: 1Gi limit
- Initialization: SQL init scripts
- Service: ClusterIP (internal)
- Secret management: Credentials in Kubernetes Secret

**c) Elasticsearch**
- **File:** `deployments/elasticsearch-deployment.yaml`
- Replicas: 1
- Memory: 2Gi limit
- Health checks: HTTP health endpoint
- Service: ClusterIP (internal)

**d) Kibana**
- **File:** `deployments/kibana-deployment.yaml`
- Replicas: 1
- Memory: 1Gi limit
- Service: LoadBalancer (external access)
- Depends on: Elasticsearch

**e) API Gateway**
- **File:** `deployments/api-gateway-deployment.yaml`
- Replicas: 2 (for HA)
- Memory: 256Mi limit
- Configuration: nginx ConfigMap
- Service: LoadBalancer (external access)
- Routes:
  - `/api/reports` → report-service:3001
  - `/api/auth` → auth-service:3002
  - `/api/data` → data-service:3003
  - `/api/cache` → cache-service:3004

#### Ingress & TLS
- **File:** `ingress.yaml`
- Domains:
  - `api.reports.example.com` → API Gateway (port 80)
  - `reports.example.com` → Dashboard + API (ports 80, 5601)
- TLS: Let's Encrypt certificates (cert-manager)
- Rate limiting: 100 requests/minute

#### ConfigMaps & Secrets
- **File:** `configmaps/app-config.yaml`
- Environment variables
- Database credentials
- Salesforce OAuth tokens
- JWT secrets

### 3. Environment Configuration

**File:** `.env.example` → `.env`

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

# Elasticsearch
ELASTICSEARCH_HOST=localhost:9200
```

---

## Setup Instructions

### Quick Start (Local Development)

```bash
# 1. Run setup script
bash scripts/phase1-setup.sh

# 2. Verify services
docker-compose ps

# 3. Test connectivity
curl http://localhost:9200       # Elasticsearch
curl http://localhost:5601       # Kibana
redis-cli ping                   # Redis
psql -h localhost -U reports_user -d reports_db  # PostgreSQL
```

### Manual Setup

```bash
# 1. Create .env file
cp .env.example .env

# 2. Install dependencies
pip install -r requirements.txt
cd frontends/dashboard-fe && npm install

# 3. Start Docker services
docker-compose up -d

# 4. Verify health
docker-compose ps
```

### Kubernetes Deployment

```bash
# 1. Setup cluster and namespace
make k8s-setup

# 2. Deploy all services
make k8s-deploy

# 3. Verify deployment
kubectl get pods -n salesforce-reports
kubectl get svc -n salesforce-reports

# 4. Access services
# Kibana: kubectl port-forward svc/kibana 5601:5601 -n salesforce-reports
# API: kubectl port-forward svc/api-gateway 80:80 -n salesforce-reports
```

---

## Service Health Checks

### Docker Compose

```bash
# Check all services
docker-compose ps

# View service logs
docker-compose logs redis
docker-compose logs postgres
docker-compose logs elasticsearch
docker-compose logs kibana
```

### Kubernetes

```bash
# Watch deployments
kubectl get deployments -n salesforce-reports --watch

# Check pod status
kubectl get pods -n salesforce-reports

# View logs
kubectl logs -f deployment/redis -n salesforce-reports
kubectl logs -f deployment/postgres -n salesforce-reports
```

---

## Database Initialization

### PostgreSQL Schema

The `postgres-deployment.yaml` includes an init script that creates:

1. **Tables:**
   - `reports` — Report definitions and metadata
   - `report_executions` — Execution history and results

2. **Indexes:**
   - Status, created_by, created_at filtering
   - Soft deletes support (deleted_at)

3. **Extensions:**
   - UUID support (`uuid-ossp`)
   - Query analysis (`pg_stat_statements`)

### Verify Database

```bash
# Connect to database
psql -h localhost -U reports_user -d reports_db

# List tables
\dt

# Verify schema
\d reports
\d report_executions
```

---

## Networking

### Docker Compose Network

- Network: `salesforce-network` (bridge)
- Services communicate via service name (DNS)
- Example: `postgres:5432` from other containers

### Kubernetes Networking

- Namespace: `salesforce-reports`
- Services: ClusterIP (internal) or LoadBalancer (external)
- Ingress: External traffic routing via nginx ingress controller

---

## Security Considerations

### Development Environment
- Credentials in `.env` (git-ignored)
- No TLS for local services
- Single-node deployments
- Health checks enabled

### Production Environment
- Secrets stored in Kubernetes Secrets
- TLS/HTTPS via cert-manager
- NetworkPolicy restrictions
- Resource quotas and limits
- High availability (replicas)

---

## Troubleshooting

### Docker Issues

**Service won't start:**
```bash
# Check logs
docker-compose logs <service-name>

# Verify image exists
docker images | grep <image>

# Restart service
docker-compose restart <service-name>
```

**Port conflicts:**
```bash
# Find process using port
lsof -i :<port>

# Change port in docker-compose.yml
# Or kill conflicting process
```

### Kubernetes Issues

**Pod pending:**
```bash
kubectl describe pod <pod-name> -n salesforce-reports
```

**Service unreachable:**
```bash
# Check endpoints
kubectl get endpoints -n salesforce-reports

# Verify ingress
kubectl describe ingress -n salesforce-reports
```

---

## Next Phase

**Phase 2:** MCP Client + Auth Service
- Salesforce OAuth integration
- JWT authentication
- RBAC implementation
- Service discovery

---

## Useful Commands

```bash
# Setup
make setup              # Full setup (install + docker-up)
make env-setup         # Just create .env

# Docker
make docker-up         # Start services
make docker-down       # Stop services
make docker-logs       # View logs

# Kubernetes
make k8s-setup         # Setup namespace & infrastructure
make k8s-deploy        # Deploy all services
make k8s-down          # Tear down cluster

# Verification
docker-compose ps      # List containers
kubectl get pods -n salesforce-reports  # List pods

# Access Services
# Elasticsearch: http://localhost:9200
# Kibana: http://localhost:5601
# Redis: localhost:6379
# PostgreSQL: localhost:5432
```

---

## Documentation Links

- Docker Compose: https://docs.docker.com/compose/
- Kubernetes: https://kubernetes.io/
- Elasticsearch: https://www.elastic.co/
- PostgreSQL: https://www.postgresql.org/
- Redis: https://redis.io/

---

**Phase 1 Status:** ✅ Complete
**Blockers:** None  
**Ready for Phase 2:** Yes
