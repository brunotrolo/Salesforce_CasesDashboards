# Phase 3: Logging Service

**Status:** ⏳ Planejado  
**Milestone:** Infraestrutura centralizada de logging e análise  
**Duration:** 1-2 semanas  
**Depends on:** Phase 2 ✅

---

## Overview

Phase 3 implementa o sistema centralizado de logging para a arquitetura de microserviços, utilizando o ELK Stack (Elasticsearch, Logstash, Kibana).

### Objetivos Principais

1. **Centralização de Logs**
   - Coleta de logs de todos os serviços
   - Indexação no Elasticsearch
   - Retenção configurável de dados

2. **Análise e Visualização**
   - Dashboards em Kibana
   - Busca e filtragem avançadas
   - Análise de trends e padrões

3. **Alertas e Monitoramento**
   - Regras de alerta baseadas em eventos
   - Notificações de anomalias
   - Tracking de performance

4. **Observabilidade**
   - Distributed tracing (trace_id, correlation_id)
   - Performance metrics
   - Error tracking com stack traces

---

## Arquitetura

### Componentes

```
┌──────────────────────────────────────────┐
│          Aplicações (Serviços)           │
│  MCP Client | Auth | Report | Data      │
└──────────────────┬───────────────────────┘
                   │
                   ▼ (Structured Logs)
        ┌──────────────────────┐
        │  Fluent Bit / Logstash│
        │  (Log Shipper)       │
        └──────────────┬───────┘
                       │
                       ▼
        ┌──────────────────────────┐
        │   Elasticsearch (9200)   │
        │   (Log Storage & Index)  │
        └──────────────┬───────────┘
                       │
        ┌──────────────┴───────────┐
        ▼                         ▼
   ┌─────────┐             ┌──────────┐
   │ Kibana  │             │ Alerting │
   │ (5601)  │             │ Engine   │
   └─────────┘             └──────────┘
```

### Fluxo de Logs

```
Serviço
  │
  ├─ Log Estruturado (JSON)
  │  {
  │    "timestamp": "2026-08-16T10:30:45.123Z",
  │    "service": "report-service",
  │    "level": "INFO",
  │    "trace_id": "abc123def456",
  │    "message": "Report executed",
  │    "context": {...}
  │  }
  │
  ▼
Fluent Bit / Logstash
  │
  ├─ Enriquecimento de dados
  ├─ Transformação de formato
  ├─ Bufferização (em caso de falha)
  │
  ▼
Elasticsearch
  │
  ├─ Indexação (daily, weekly)
  ├─ Retenção por TTL
  ├─ Backup automático
  │
  ▼
Kibana / Analytics
  │
  ├─ Busca por trace_id
  ├─ Dashboards customizados
  ├─ Alertas configuráveis
  │
  ▼
Usuários & Sistemas
```

---

## Componentes

### 1. Elasticsearch

**Porta:** 9200 (REST API) + 9300 (node communication)  
**Repositório:** `infra/elasticsearch/`

#### Responsabilidades

- Armazenamento centralizado de logs
- Indexação e busca fulltext
- Agregações e análises
- Retenção com políticas de ciclo de vida (ILM)

#### Configuração

```yaml
elasticsearch:
  image: docker.elastic.co/elasticsearch/elasticsearch:8.10.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false
    - xpack.ml.enabled=true
  volumes:
    - elasticsearch-data:/usr/share/elasticsearch/data
  ports:
    - "9200:9200"
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:9200/_cluster/health"]
    interval: 30s
```

#### Índices

```
logs-{serviço}-{data}
  ├─ logs-mcp-client-2026.08.16
  ├─ logs-auth-service-2026.08.16
  ├─ logs-report-service-2026.08.16
  └─ logs-{serviço}-2026.08.17
```

#### Template de Mapping

```json
{
  "index_patterns": ["logs-*"],
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "index.lifecycle.name": "logs-policy",
    "index.lifecycle.rollover_alias": "logs-alias"
  },
  "mappings": {
    "properties": {
      "timestamp": { "type": "date" },
      "service": { "type": "keyword" },
      "level": { "type": "keyword" },
      "trace_id": { "type": "keyword" },
      "correlation_id": { "type": "keyword" },
      "message": { "type": "text" },
      "context": { "type": "object" },
      "error": { "type": "keyword" },
      "stack_trace": { "type": "text" }
    }
  }
}
```

### 2. Kibana

**Porta:** 5601  
**Repositório:** `infra/kibana/`

#### Responsabilidades

- Interface de visualização
- Criação de dashboards
- Alertas e notificações
- Análise exploratória

#### Dashboards Pré-configurados

1. **Overview Dashboard**
   - Contagem de logs por serviço
   - Taxa de erro por período
   - Logs mais recentes

2. **Service Dashboard** (por serviço)
   - Requisições por minuto
   - Latência (p50, p95, p99)
   - Taxa de erro
   - Top errors

3. **Performance Dashboard**
   - Slowest operations
   - Database query times
   - Cache hit rates
   - API response times

4. **Security Dashboard**
   - Failed login attempts
   - Unauthorized access attempts
   - Permission denials
   - OAuth failures

#### Alertas Pré-configurados

```
1. High Error Rate
   Condição: errors > 50 in 5 minutes
   Ação: Email + Slack

2. Service Down
   Condição: no logs from service in 2 minutes
   Ação: SMS + Page on-call

3. Slow Queries
   Condição: query_time > 5000ms
   Ação: Log + Slack

4. Database Connection Failures
   Condição: connection_failed > 10 in 5 minutes
   Ação: Page on-call + Page DBA
```

### 3. Fluent Bit / Logstash

**Repositório:** `infra/logstash/`

#### Responsabilidades

- Coleta de logs dos serviços
- Parsing e transformação
- Enriquecimento com metadados
- Buffer e retry em caso de falha

#### Pipeline de Processamento

```
Input (Docker logging driver)
  │
  ├─ Parse JSON
  │
  ├─ Enrich
  │  ├─ Add hostname
  │  ├─ Add pod name
  │  ├─ Add environment
  │
  ├─ Filter
  │  ├─ Remover dados sensíveis
  │  ├─ Normalizar níveis de log
  │
  ▼
Output (Elasticsearch)
  ├─ Batch processing
  ├─ Retry com backoff
  ├─ Buffer em disk
```

#### Configuração do Serviço

Cada serviço deve enviar logs para stdout em JSON:

```python
# src/logger.py
class StructuredLogger:
    def info(self, message, **context):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "service": "service-name",
            "level": "INFO",
            "trace_id": get_trace_id(),
            "correlation_id": get_correlation_id(),
            "message": message,
            "context": context
        }
        print(json.dumps(log_entry))
```

---

## Implementação

### Passo 1: Setup Elasticsearch + Kibana

```bash
# Fazer pull das imagens
docker pull docker.elastic.co/elasticsearch/elasticsearch:8.10.0
docker pull docker.elastic.co/kibana/kibana:8.10.0

# Iniciar com docker-compose
docker-compose up -d elasticsearch kibana

# Aguardar inicialização (30-60 segundos)
# Verificar health
curl http://localhost:9200/_cluster/health
```

### Passo 2: Criar Índices e Templates

```bash
# Criar template de mapping
curl -X PUT http://localhost:9200/_index_template/logs-template \
  -H 'Content-Type: application/json' \
  -d @infra/elasticsearch/mappings/logs-template.json

# Criar ILM policy para retenção
curl -X PUT http://localhost:9200/_ilm/policy/logs-policy \
  -H 'Content-Type: application/json' \
  -d @infra/elasticsearch/policies/logs-ilm.json
```

### Passo 3: Configurar Fluent Bit

```yaml
# infra/fluent-bit/fluent-bit.conf
[INPUT]
    Name docker
    Tag docker.*

[FILTER]
    Name parser
    Match docker.*
    Key_Name log
    Parser json

[OUTPUT]
    Name es
    Match docker.*
    Host elasticsearch
    Port 9200
    Logstash_Format On
    Logstash_Prefix logs
    Retry_Limit 5
```

### Passo 4: Configurar Kibana Alertas

```bash
# Via UI ou API
POST /api/alerting/rules
{
  "name": "High Error Rate",
  "consumer": "logs",
  "rule_type_id": "logs.alert",
  "schedule": { "interval": "5m" },
  "actions": [
    {
      "id": "slack",
      "group": "threshold met",
      "params": {
        "channel": "#alerts"
      }
    }
  ],
  "params": {
    "index": "logs-*",
    "timeWindow": "5m",
    "threshold": 50,
    "condition": "query.hits.total.value > threshold"
  }
}
```

---

## Endpoints da Logging Service

### API de Logs

```
GET /logs/search
Query parameters:
  - service: nome do serviço
  - level: ERROR, WARN, INFO, DEBUG
  - trace_id: ID de trace para correlação
  - from: timestamp inicial
  - to: timestamp final
  - limit: max 10000

Exemplo:
GET /logs/search?service=auth-service&level=ERROR&limit=100

Response:
{
  "total": 234,
  "logs": [
    {
      "timestamp": "2026-08-16T10:30:45.123Z",
      "service": "auth-service",
      "level": "ERROR",
      "trace_id": "abc123",
      "message": "Database connection failed",
      "context": {
        "error": "Connection timeout",
        "duration_ms": 5000
      }
    },
    ...
  ]
}
```

```
GET /logs/{trace_id}
Retorna todos os logs relacionados a um trace

Response:
{
  "trace_id": "abc123",
  "logs": [
    // Logs ordenados cronologicamente
  ]
}
```

### API de Análise

```
GET /analytics/errors/top
Retorna os erros mais frequentes

Response:
{
  "errors": [
    {
      "message": "Connection timeout",
      "count": 342,
      "services": ["auth-service", "report-service"],
      "last_occurrence": "2026-08-16T10:30:45.123Z"
    },
    ...
  ]
}
```

```
GET /analytics/performance/{service}
Retorna métricas de performance

Response:
{
  "service": "report-service",
  "metrics": {
    "p50_latency_ms": 125,
    "p95_latency_ms": 450,
    "p99_latency_ms": 2100,
    "error_rate_percent": 0.5,
    "requests_per_minute": 1250
  }
}
```

---

## Plano de Implementação

### Semana 1: Infraestrutura ELK

**Tarefas:**
1. Setup Elasticsearch em Docker
   - Configurar volume de persistência
   - Habilitar segurança (se necessário)
   - Health checks

2. Setup Kibana
   - Conexão com Elasticsearch
   - Configuração inicial
   - Criação de índices

3. Setup Fluent Bit
   - Parser JSON
   - Enrichment pipeline
   - Buffer e retry logic

**Deliverable:**
- ✅ ELK Stack rodando
- ✅ Logs chegando em Elasticsearch
- ✅ Kibana acessível e funcional

### Semana 2: Dashboards e Alertas

**Tarefas:**
1. Criar Dashboards Kibana
   - Overview
   - Por serviço
   - Performance
   - Security

2. Implementar Alertas
   - High error rate
   - Service down
   - Performance degradation
   - Security events

3. Integração com Slack/Email
   - Notificações de alertas
   - Testes end-to-end

**Deliverable:**
- ✅ Dashboards operacionais
- ✅ Alertas testados
- ✅ Notificações funcionando

---

## Segurança

### Proteção de Dados

- ✅ Elasticsearch com autenticação (X-Pack)
- ✅ Kibana com RBAC
- ✅ Remover dados sensíveis (senhas, tokens)
- ✅ Criptografia em trânsito (TLS)
- ✅ Criptografia em repouso

### Retenção de Dados

```
- Production: 30 dias
- Staging: 14 dias
- Development: 7 dias
- Compliance logs: 365 dias
```

### Auditoria

- ✅ Logs de acesso ao Kibana
- ✅ Modificações em índices
- ✅ Mudanças em alertas
- ✅ Exportações de dados

---

## Monitoramento da Logging Service

### Métricas

```python
# Prometheus metrics
elasticsearch_cluster_health_status
elasticsearch_indices_size_bytes
elasticsearch_document_count
kibana_uptime_seconds
fluent_bit_output_errors_total
```

### Health Checks

```
GET /health/logging
Response:
{
  "elasticsearch": "healthy",
  "kibana": "healthy",
  "fluent_bit": "healthy",
  "retention_policy": "compliant"
}
```

---

## Sucesso Criteria

- ✅ Todos os serviços enviando logs
- ✅ Logs indexados corretamente
- ✅ Dashboards operacionais
- ✅ Alertas funcionando
- ✅ Performance < 200ms para queries
- ✅ Documentação completa
- ✅ Runbook para troubleshooting

---

## Próxima Fase

**Phase 4:** Report Service
- Orquestração de relatórios
- Caching com Redis
- Execução e armazenamento

---

## Recursos

- Elasticsearch: https://www.elastic.co/
- Kibana: https://www.elastic.co/kibana/
- Fluent Bit: https://docs.fluentbit.io/
- ELK Stack Docker: https://www.docker.elastic.co/

---

**Phase 3 Status:** ⏳ Pronto para começar
**Next:** Iniciar implementação da Logging Service
