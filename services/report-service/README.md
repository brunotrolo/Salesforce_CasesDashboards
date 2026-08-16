# Report Service

Orquestração de operações de relatórios, cache e validações.

## Estrutura

```
src/
  ├── report_manager.py         # Lógica principal
  ├── report_validator.py       # Validações
  ├── report_cache.py           # Cache strategy
  ├── models/                   # Modelos de dados
  └── handlers/                 # Handlers (create, update, delete)
```

## Responsabilidades

- Validação de configurações
- Orquestração com MCP Client
- Cache de relatórios
- Histórico de versões
- Notificações de mudanças
