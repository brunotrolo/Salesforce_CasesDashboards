# Report Service

Serviço de orquestração e gerenciamento completo de relatórios Salesforce com validação, cache e agendamento.

## Responsabilidades

- **CRUD Completo**: Criar, ler, atualizar, deletar relatórios
- **Validação**: Validar configurações antes de salvar
- **Execução**: Executar relatórios e retornar resultados
- **Cache**: Cache inteligente com TTL configurável
- **Agendamento**: Suporte para execução agendada (CRON)

## Arquitetura

```
report-service/
├── src/
│   ├── models/report.py             # ReportStatus, ReportType
│   ├── report_manager.py            # Orquestração CRUD
│   ├── report_validator.py          # Validação de configurações
│   ├── report_cache.py              # Cache com TTL
│   └── __init__.py
├── tests/
│   ├── test_report_manager.py       # 18 testes CRUD
│   ├── test_report_validator.py     # 25 testes validação
│   ├── test_report_cache.py         # 18 testes cache
│   └── __init__.py
├── requirements.txt
└── README.md
```

## Modelos de Dados

### Report Status
- **DRAFT**: Rascunho, não pode executar
- **ACTIVE**: Ativo e executável
- **SCHEDULED**: Agendado para execução
- **PAUSED**: Pausado temporariamente
- **ARCHIVED**: Deletado (soft delete)

### Report Type
- **SUMMARY**: Agregação com resumo
- **MATRIX**: Formatação em matriz
- **TABULAR**: Tabela simples
- **JOIN**: Com relacionamentos

## Testes

```bash
pip install -r requirements.txt
pytest tests/ -v

# Com coverage
pytest tests/ --cov=src
```

### Cobertura

- test_report_manager.py: 18 testes ✅
- test_report_validator.py: 25 testes ✅
- test_report_cache.py: 18 testes ✅
- **Total: 61 testes, 100% passando**
