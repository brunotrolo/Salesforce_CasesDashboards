# Queries SOQL de referência — Case

Todas testadas neste org via `mcp__SalesforceRead__soqlQuery`. Ajuste o filtro de data (`CreatedDate`) e demais condições de `WHERE` conforme o recorte pedido — nunca remova o filtro de data em queries de volume alto.

Valores de referência abaixo foram observados em 2026-08-14 (dia com 68.173 casos criados) — servem para checar se um resultado novo está na faixa esperada, não como verdade fixa.

## 1. Volume total no período

```sql
SELECT COUNT(Id) total FROM Case WHERE CreatedDate = TODAY
```
Referência: 68.173 (2026-08-14).

Para outros períodos, troque `TODAY` por `THIS_WEEK`, `THIS_MONTH`, `YESTERDAY`, ou um intervalo explícito:
```sql
SELECT COUNT(Id) total FROM Case WHERE CreatedDate >= 2026-08-01T00:00:00Z AND CreatedDate < 2026-08-14T00:00:00Z
```

## 2. Volume por criação manual vs. automática

```sql
SELECT CreatedAutomatically__c, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY
GROUP BY CreatedAutomatically__c
```
Referência: `false` (manual) 44.029 / `true` (automático) 24.145 — manual costuma ser a maior fatia.

## 3. Distribuição por Status

```sql
SELECT Status, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY
GROUP BY Status
ORDER BY COUNT(Id) DESC
```
Valores observados: `Closed`, `Em atendimento`, `Fechado Com Sucesso`, `New`, `Protocolo Fechado`, `InAnalysis`, `Rejeitado`, `Erro envio CSU`.

## 4. Distribuição por Prioridade

```sql
SELECT Priority, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY
GROUP BY Priority
ORDER BY COUNT(Id) DESC
```
Valores observados: `Normal`, `Ultra`.

## 5. Top categorias (campo legado, agrupável)

```sql
SELECT Category__c, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY
GROUP BY Category__c
ORDER BY COUNT(Id) DESC
LIMIT 20
```
Atenção: `Category__c = null` normalmente aparece como uma das maiores fatias — é o indicador de qualidade de dado (ver query 7), não descartar ao interpretar o resultado.

Drill-down em subcategoria de uma categoria específica:
```sql
SELECT SubCategory__c, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY AND Category__c = 'Fatura'
GROUP BY SubCategory__c
ORDER BY COUNT(Id) DESC
LIMIT 20
```

**Não fazer** `GROUP BY CategoryUnified__c` (ou as demais `*Unified__c`) — retorna `MALFORMED_QUERY: field 'CategoryUnified__c' can not be grouped in a query call`, confirmado neste org.

## 6. Cruzamento categoria x manual/automático

```sql
SELECT Category__c, CreatedAutomatically__c, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY
GROUP BY Category__c, CreatedAutomatically__c
ORDER BY COUNT(Id) DESC
LIMIT 40
```

## 7. Qualidade de dado — % de casos sem categoria, por origem manual/automática

```sql
SELECT CreatedAutomatically__c, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY AND Category__c = null
GROUP BY CreatedAutomatically__c
```
Referência: 25.312 manuais sem categoria (57% dos manuais) vs. 167 automáticos sem categoria (0,7% dos automáticos) — gap concentrado quase inteiramente na criação manual. Para virar percentual, divida pelo total de cada grupo (query 2).

## 8. Amostra para cálculo de SLA (pós-processamento)

```sql
SELECT Id, Category__c, CreatedAutomatically__c, CreatedDate, ClosedDate
FROM Case
WHERE CreatedDate = TODAY
  AND Status IN ('Closed', 'Fechado Com Sucesso', 'Protocolo Fechado')
  AND ClosedDate != null
LIMIT 2000
```
Calcule `ClosedDate - CreatedDate` fora do SOQL (jq/python) e agregue por `Category__c` e/ou `CreatedAutomatically__c` (média, mediana, p90). Se o volume do período for muito alto, filtre por uma categoria específica antes de rodar, em vez de aumentar o `LIMIT`.

## 9. Owner/fila com maior carga (opcional, apoio operacional)

```sql
SELECT Owner.Name, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY
GROUP BY Owner.Name
ORDER BY COUNT(Id) DESC
LIMIT 20
```

## Notas de schema

- `Produto__c` (picklist) está praticamente vazio neste org (1 registro observado num dia inteiro) — não é uma dimensão útil de análise por enquanto. Se o usuário perguntar especificamente por "produto", verifique antes com `getObjectSchema` se `Product_Service__c`/`Servi_o_Produto__c` (ou outro campo específico daquele org) está mais preenchido, em vez de assumir `Produto__c`.
- `Origin` está quase sempre nulo neste org — checar preenchimento antes de usar como dimensão de canal.
