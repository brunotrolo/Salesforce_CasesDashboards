# Arquitetura do Sistema

## Visão Geral

Sistema de relatórios Salesforce baseado em microserviços com micro frontends.

## Componentes Principais

### Microserviços

1. **MCP Client** - Integração com Salesforce
2. **Report Service** - Orquestração de relatórios
3. **Auth Service** - Autenticação e autorização
4. **Logging Service** - Observabilidade
5. **Data Service** - Transformação de dados
6. **Cache Service** - Cache distribuído
7. **API Gateway** - Roteamento

### Micro Frontends

1. **Dashboard FE** - Visualização
2. **Builder FE** - Criação/edição
3. **Analytics FE** - Histórico e tendências

## Fluxo de Dados

Salesforce → MCP Client → Report Service → API Gateway → Frontends

## Logging

Sistema estruturado com trace_id e correlation_id para rastreamento de fluxo completo.
