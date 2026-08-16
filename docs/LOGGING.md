# Sistema de Logging

## Formato Estruturado

```json
{
  "timestamp": "2026-08-16T10:30:45.123Z",
  "service": "report-service",
  "level": "INFO",
  "trace_id": "abc123def456",
  "correlation_id": "xyz789",
  "message": "Report created successfully",
  "context": { "user_id": "u:12345", "report_id": "r:67890" },
  "error": null
}
```

## Categorias

- API Requests (INFO)
- MCP Operations (DEBUG)
- Errors (ERROR)
- Cache (DEBUG)
- Security (WARN)
- Performance (INFO)

## Acessar Logs

- Dev: `tail -f logs/app.log | jq .`
- Prod: Kibana (http://elasticsearch:5601)
