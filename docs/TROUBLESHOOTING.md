# Troubleshooting

## Problemas Comuns

| Erro | Solução |
|------|---------|
| 403 Forbidden (Salesforce) | Verificar IP Trusted Range |
| 401 Unauthorized | Token expirado, renovar refresh_token |
| 414 Request URI Too Long | SOQL complexa, simplificar |
| Logs não aparecem | Verificar Elasticsearch |
| Docker não inicia | Verificar portas em uso |

## Debug

```bash
# Verificar logs
tail -f logs/app.log | jq .

# Verificar conexão Salesforce
curl -X GET http://localhost:3000/health

# Verificar Redis
redis-cli ping

# Verificar PostgreSQL
psql -h localhost -U reports_user -d reports_db
```
