# MCP Salesforce Client

Integração com Salesforce via MCP para operações CRUD de relatórios.

## Estrutura

```
src/
  ├── salesforce_connector.py   # Conexão MCP
  ├── report_operations.py      # CRUD de relatórios
  ├── data_models.py            # Tipos de dados
  └── error_handler.py          # Tratamento de erros
```

## Responsabilidades

- Autenticação OAuth com Salesforce
- CRUD de Report Definition
- Parsing de respostas
- Rate limiting e retry logic
- Logging de todas as operações

## Setup

```bash
pip install -r requirements.txt
pytest tests/
```
