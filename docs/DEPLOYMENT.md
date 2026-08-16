# Guia de Deployment

## Pré-requisitos

- Docker e Docker Compose
- Kubernetes (para produção)
- GitHub Actions (CI/CD)

## Desenvolvimento

```bash
make setup
make docker-up
npm run dev
```

## Produção

```bash
docker build -t salesforce-reports .
kubectl apply -f infra/kubernetes/
```

## Monitoring

- Elasticsearch: http://localhost:9200
- Kibana: http://localhost:5601
- Prometheus: http://localhost:9090
