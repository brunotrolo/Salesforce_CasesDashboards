# Guia de Deployment - Salesforce Reports System

## Desenvolvimento Local

### 1. Preparar ambiente

```bash
# Clonar repositório
git clone https://github.com/brunotrolo/Salesforce_CasesDashboards
cd Salesforce_CasesDashboards

# Criar arquivo .env com credenciais
cp .env.example .env
```

### 2. Iniciar stack Docker (Redis, PostgreSQL, Elasticsearch)

```bash
docker-compose up -d

# Verificar status
docker-compose ps

# Outputs esperados:
# salesforce-redis           - redis:7-alpine
# salesforce-postgres        - postgres:15-alpine
# salesforce-elasticsearch   - elasticsearch:8.11.0
# salesforce-kibana          - kibana:8.11.0
```

### 3. Iniciar API Gateway

```bash
cd services/api-gateway

# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
python -m uvicorn src.main:app --reload --port 3000

# Endpoints disponíveis:
# GET  http://localhost:3000/health
# POST http://localhost:3000/auth/login
# GET  http://localhost:3000/api/reports
```

### 4. Iniciar Dashboard Frontend

```bash
cd frontends/dashboard-fe

# Instalar dependências
npm install

# Rodar dev server
npm run dev

# Acesso: http://localhost:5173
# Proxy automático para http://localhost:3000/api
```

### 5. Testar fluxo completo

```bash
# 1. Login para obter token
curl -X POST http://localhost:3000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Response: {"access_token":"eyJ0eXA...","token_type":"bearer"}

# 2. Listar relatórios (sem auth - para dev)
curl http://localhost:3000/api/reports?limit=10

# 3. Abrir dashboard
open http://localhost:5173
```

---

## Deployment em Kubernetes

### Pré-requisitos

- Cluster Kubernetes (1.24+)
- kubectl configurado
- Docker Registry (Docker Hub, ECR, GCR)
- Helm (recomendado)

### 1. Build e push da imagem Docker

```bash
# Build API Gateway
cd services/api-gateway
docker build -t brunotrolo/salesforce-api-gateway:1.0.0 .
docker push brunotrolo/salesforce-api-gateway:1.0.0

# Build Dashboard Frontend
cd frontends/dashboard-fe
docker build -t brunotrolo/salesforce-dashboard-fe:1.0.0 .
docker push brunotrolo/salesforce-dashboard-fe:1.0.0
```

### 2. Criar secrets para Salesforce

```bash
kubectl create secret generic salesforce-credentials \
  --from-literal=client-id=$SF_CLIENT_ID \
  --from-literal=client-secret=$SF_CLIENT_SECRET \
  --from-literal=refresh-token=$SF_REFRESH_TOKEN

kubectl create secret generic api-secrets \
  --from-literal=jwt-secret-key=$(openssl rand -hex 32)
```

### 3. Deploy Redis (usar Helm)

```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo update

helm install redis bitnami/redis \
  --set auth.enabled=false \
  --set master.persistence.size=10Gi \
  --set replica.replicaCount=2
```

### 4. Deploy API Gateway

```bash
kubectl apply -f infra/kubernetes/api-gateway-deployment.yaml

# Verificar status
kubectl get deployments
kubectl get pods -l app=api-gateway
kubectl logs -l app=api-gateway -f

# Port forward para testar
kubectl port-forward svc/api-gateway 3000:80
```

### 5. Deploy Dashboard Frontend

```bash
kubectl apply -f infra/kubernetes/dashboard-deployment.yaml

# Verificar status
kubectl get deployments
kubectl get pods -l app=dashboard-frontend
```

### 6. Deploy Ingress

```bash
# Instalar nginx-ingress controller (se não existir)
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace

# Deploy Ingress
kubectl apply -f infra/kubernetes/ingress.yaml

# Verificar
kubectl get ingress
```

### 7. Configurar TLS (Let's Encrypt)

```bash
# Instalar cert-manager
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager \
  --create-namespace

# Criar ClusterIssuer
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@reports.example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 8. Monitoramento e Logs

```bash
# Ver logs em tempo real
kubectl logs -l app=api-gateway -f

# Acessar Elasticsearch/Kibana
kubectl port-forward svc/elasticsearch 9200:9200
kubectl port-forward svc/kibana 5601:5601

# Kibana: http://localhost:5601

# Métricas Prometheus
kubectl apply -f infra/kubernetes/prometheus-config.yaml
```

---

## Verificação Pós-Deploy

### Checklist

- [ ] API Gateway respondendo em `/health`
- [ ] Dashboard acessível via browser
- [ ] Login funcionando (token gerado)
- [ ] Listagem de relatórios funcionando
- [ ] Cache Redis ativo
- [ ] Logs em Elasticsearch/Kibana
- [ ] Rate limiting funcionando (>100 req/min = 429)
- [ ] TLS certificado válido

### Testes

```bash
# Health check
curl https://api.reports.example.com/health

# Login
curl -X POST https://api.reports.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"password"}'

# Listar relatórios
curl -H "Authorization: Bearer $TOKEN" \
  https://api.reports.example.com/api/reports

# Rate limit test
for i in {1..150}; do curl -s https://api.reports.example.com/health > /dev/null; done
# Última requisição deve retornar 429 Too Many Requests
```

---

## Troubleshooting

### API Gateway não inicia

```bash
kubectl describe pod api-gateway-xxx
kubectl logs api-gateway-xxx
```

**Causa comum:** Credenciais Salesforce inválidas
```bash
# Remover e recriar secret
kubectl delete secret salesforce-credentials
kubectl create secret generic salesforce-credentials \
  --from-literal=client-id=$SF_CLIENT_ID \
  --from-literal=client-secret=$SF_CLIENT_SECRET \
  --from-literal=refresh-token=$SF_REFRESH_TOKEN

# Restart deployment
kubectl rollout restart deployment/salesforce-api-gateway
```

### Redis não conecta

```bash
# Verificar Redis
kubectl get pods -l app.kubernetes.io/name=redis
kubectl logs -l app.kubernetes.io/name=redis

# Testar conexão
kubectl run -it --image=redis:7 redis-test -- redis-cli -h redis-service ping
```

### Ingress não roteando

```bash
kubectl get ingress
kubectl describe ingress salesforce-api-ingress

# Verificar DNS
nslookup api.reports.example.com

# Testar direto no ingress controller
kubectl port-forward -n ingress-nginx svc/ingress-nginx-controller 8080:80
curl -H "Host: api.reports.example.com" http://localhost:8080/health
```

---

## Rollback de Deploy

```bash
# Ver histórico
kubectl rollout history deployment/salesforce-api-gateway

# Voltar para versão anterior
kubectl rollout undo deployment/salesforce-api-gateway

# Voltar para versão específica
kubectl rollout undo deployment/salesforce-api-gateway --to-revision=2
```

---

## Próximos Passos

- [ ] Configurar CI/CD pipeline (GitHub Actions)
- [ ] Implementar backup automático de dados
- [ ] Configurar alertas e notificações
- [ ] Testar failover e disaster recovery
- [ ] Documentar runbooks operacionais
- [ ] Treinar time ops
