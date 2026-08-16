# Infrastructure Setup

This directory contains all infrastructure configurations for the Salesforce Reports System.

## Directory Structure

```
infra/
├── docker-compose.yml              # Local development stack
├── README.md                        # This file
├── kubernetes/
│   ├── namespace.yaml               # Kubernetes namespace & RBAC
│   ├── ingress.yaml                 # Ingress configuration
│   ├── deployments/
│   │   ├── redis-deployment.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── elasticsearch-deployment.yaml
│   │   ├── kibana-deployment.yaml
│   │   └── api-gateway-deployment.yaml
│   ├── configmaps/
│   │   ├── app-config.yaml          # Environment variables & secrets
│   │   └── report-service-config.yaml
│   ├── services/
│   │   ├── ingress.yaml
│   │   └── report-service.yaml
│   └── monitoring/
│       ├── prometheus-config.yaml
│       └── alerts.yaml
└── terraform/                       # Infrastructure as Code (future)
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

## Quick Start

### Local Development (Docker Compose)

```bash
# Start services
docker-compose up -d

# Verify all services running
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Kubernetes Production

```bash
# Setup namespace & infrastructure
make k8s-setup

# Deploy all services
make k8s-deploy

# Check status
kubectl get pods -n salesforce-reports

# Stop everything
make k8s-down
```

## Services Overview

### Development (Docker Compose)

| Service | Port | Purpose | Health Check |
|---------|------|---------|--------------|
| Redis | 6379 | Caching layer | redis-cli ping |
| PostgreSQL | 5432 | Main database | pg_isready |
| Elasticsearch | 9200 | Logging & search | HTTP health |
| Kibana | 5601 | Log visualization | HTTP status |

### Production (Kubernetes)

All services deployed to `salesforce-reports` namespace with:
- Resource limits (CPU/Memory)
- Liveness & readiness probes
- Service discovery (DNS)
- Persistent volumes (production)
- Network policies

## Environment Configuration

### Development

Update `.env` file:
```bash
cp ../.env.example ../.env
# Edit with your values
```

### Production

Use Kubernetes Secrets:
```bash
kubectl create secret generic app-secrets \
  --from-literal=SF_CLIENT_ID=xxx \
  --from-literal=SF_CLIENT_SECRET=xxx \
  -n salesforce-reports
```

## Networking

### Docker Compose
- Services communicate via `service-name:port`
- Example: `postgres:5432` from app container

### Kubernetes
- Internal: ClusterIP services (DNS-based)
- External: LoadBalancer/Ingress
- Example: `postgres.salesforce-reports.svc.cluster.local:5432`

## Persistence

### Development (Docker Compose)
- Volumes: `redis-data`, `postgres-data`, `elasticsearch-data`
- Data lost on `docker-compose down`
- Good for local development only

### Production (Kubernetes)
- Use persistent volumes
- Configure storage class for your cloud provider
- Automated backups recommended

## Monitoring & Logging

### Kibana (Log Visualization)
```bash
# Local: http://localhost:5601
# K8s: kubectl port-forward svc/kibana 5601:5601 -n salesforce-reports
```

### Prometheus (Metrics)
- Config: `kubernetes/monitoring/prometheus-config.yaml`
- Future: Add metrics scraping from services

### Alerting
- Config: `kubernetes/monitoring/alerts.yaml`
- Future: Configure alert rules

## Security

### Development
- No TLS
- Simple authentication
- Single-node deployments

### Production
- TLS via cert-manager
- NetworkPolicy restrictions
- Secret management
- RBAC enabled

## Troubleshooting

### Docker Issues
```bash
# View service logs
docker-compose logs <service>

# Restart service
docker-compose restart <service>

# Full restart
docker-compose down && docker-compose up -d
```

### Kubernetes Issues
```bash
# Check pod status
kubectl describe pod <pod-name> -n salesforce-reports

# View logs
kubectl logs <pod-name> -n salesforce-reports

# Debug pod
kubectl exec -it <pod-name> -n salesforce-reports -- /bin/sh
```

## Documentation

- Full details: `../docs/PHASE1_INFRASTRUCTURE.md`
- Architecture: `../docs/ARCHITECTURE.md`
- API docs: `../docs/API.md`

## Next Steps

1. **Phase 2:** MCP Client + Auth Service
2. **Phase 3:** Logging Service
3. **Phase 4:** Report Service
4. **Phase 5:** Frontend development

See `../CLAUDE.md` for complete project roadmap.
