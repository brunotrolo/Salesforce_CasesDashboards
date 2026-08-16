---
name: salesforce-cases-insights
description: Análise gerencial de Casos (Case) do Salesforce via SOQL somente leitura — volume, status, categoria/subcategoria, canal manual vs. automático, qualidade de preenchimento dos dados e SLA de atendimento. Use sempre que o usuário pedir análises, filtros, relatórios ou dashboards sobre casos/tickets/atendimentos do Salesforce, mesmo que não diga explicitamente "dashboard" — por exemplo "quantos casos abrimos hoje", "quais as categorias mais comuns", "como está a qualidade de categorização", "quanto tempo leva para fechar um caso", "casos automáticos vs manuais". Este objeto tem volume muito alto (dezenas de milhares de casos por dia) — a skill traz os guardrails e queries de referência necessários para analisar isso sem estourar limites de SOQL ou de contexto.
---

# Salesforce Cases Insights

Esta skill dá uma visão gerencial dos Casos (`Case`) do Salesforce: quantos, de que tipo, criados por quem/o quê, com que qualidade de dado e em quanto tempo são resolvidos. É somente leitura, usando `mcp__SalesforceRead__soqlQuery` (ou a ferramenta SOQL equivalente disponível na sessão).

## Por que os guardrails abaixo existem

Este org tem um volume de casos extremamente alto — em uma checagem real, **68.173 casos foram criados em um único dia**. Isso tem duas consequências práticas que já foram batidas de frente em testes reais:

1. **SOQL tem limite de 50.000 registros por transação**, e mesmo bem abaixo disso, um `SELECT` de 1.000-2.000 casos já produz uma resposta grande demais para caber no contexto da conversa (o harness salva em arquivo e pede para processar com `jq`/`python`).
2. **Nem todo campo é agrupável.** Os campos "unificados" de categoria (`CategoryUnified__c`, `SubcategoryUnified__c`, `SubcategoryDetailUnified__c`) são do tipo `string`, e o Salesforce rejeita `GROUP BY` neles com erro `MALFORMED_QUERY`. Os campos legados equivalentes (`Category__c`, `SubCategory__c`, `SubCategoryDetail__c`) são `picklist` e agregam normalmente — por isso são a base de qualquer análise agregada nesta skill.

Portanto: **a ferramenta certa quase sempre é SOQL agregado (`GROUP BY`/`COUNT`), não puxar registros crus.** Só puxe registros individuais quando o pedido for explicitamente sobre casos específicos (drill-down), e mesmo assim sempre com filtro de data e `LIMIT` baixo (dezenas a poucas centenas).

## Fluxo de trabalho recomendado

1. **Entenda o período e o recorte pedido** (hoje, semana, mês, um intervalo, um status específico etc.). Traduza para uma cláusula `WHERE CreatedDate = ...` — nunca rode uma agregação sobre o objeto inteiro sem filtro de data.
2. **Escolha as queries de referência** em `references/queries.md` que respondem à pergunta (volume, status, categoria, manual x automático, qualidade de dado, SLA) e adapte o filtro de data/status conforme necessário. Elas já foram validadas nesta sessão e evitam redescobrir o schema toda vez.
3. **Sempre que a análise envolver categoria**, reporte também o indicador de qualidade de dado (ver seção abaixo) — é um achado gerencial relevante por si só, não apenas um detalhe técnico.
4. **Se o resultado de uma query vier grande** (o harness avisa quando o SOQL excede o limite de tokens e salva em arquivo), processe com `jq`/`python` no arquivo salvo — nunca tente reler o conteúdo inteiro em contexto.
5. **Para visualizar** os resultados (gráficos, KPIs, tendência), use a skill `dataviz` para montar o artifact — não desenhe gráficos do zero.

## Campos-chave do objeto Case

| Campo | Tipo | Uso |
|---|---|---|
| `CreatedAutomatically__c` | boolean | Distingue casos abertos por automação/RPA (`true`) de casos abertos manualmente por atendente (`false`). É a dimensão central da visão gerencial: "quanto do volume é operação humana vs. automatizada". |
| `Category__c`, `SubCategory__c`, `SubCategoryDetail__c` | picklist | Campos **legados**, mas são os únicos agrupáveis via `GROUP BY`. Use-os para qualquer agregação por categoria/subcategoria. |
| `CategoryUnified__c`, `SubcategoryUnified__c`, `SubcategoryDetailUnified__c` | string | Campos "unificados" mais recentes, só para exibir o detalhe de **um caso específico** (ex.: ao mostrar um registro individual). Não tentar usar em `GROUP BY` — dá erro. |
| `Status` | picklist | Valores observados neste org: `New`, `InAnalysis`, `Em atendimento`, `Closed`, `Fechado Com Sucesso`, `Protocolo Fechado`, `Rejeitado`, `Erro envio CSU`. Trate `Closed`, `Fechado Com Sucesso` e `Protocolo Fechado` como "encerrado" para fins de SLA. |
| `Priority` | picklist | `Normal` e `Ultra` são os valores observados. |
| `Origin` | picklist | Na prática está quase sempre nulo neste org — não é um campo confiável para segmentar canal de entrada. Não usar como base de análise sem antes checar se está preenchido no recorte pedido. |
| `CreatedDate` / `ClosedDate` | datetime | Base para volume por período e para cálculo de SLA (ver abaixo). |
| `Owner.Name` | lookup | Útil para carga operacional por atendente/fila, mas não é o foco principal desta skill. |

## Indicador de qualidade de dado (categoria)

Um achado relevante e recorrente neste org: uma fração considerável dos casos fica sem `Category__c` preenchida, e esse gap se concentra desproporcionalmente nos casos criados manualmente (bem menos comum nos automáticos). Sempre que apresentar uma distribuição por categoria, complemente com:

```sql
SELECT CreatedAutomatically__c, COUNT(Id) total
FROM Case
WHERE CreatedDate = TODAY AND Category__c = null
GROUP BY CreatedAutomatically__c
```

Compare com o total geral por `CreatedAutomatically__c` no mesmo período para calcular o percentual sem categoria em cada grupo. Isso costuma apontar para um problema de processo/treinamento na categorização manual — vale mencionar isso explicitamente ao gestor, não só reportar o número.

## SLA de atendimento (tempo até fechamento)

Não dá para calcular duração via `GROUP BY` puro em SOQL (não há subtração de datas nativa em agregação). O padrão é:

1. Rodar uma query filtrada por período e por status "encerrado", trazendo `CreatedDate` e `ClosedDate` (e a categoria, se for analisar SLA por categoria):

```sql
SELECT Id, Category__c, CreatedAutomatically__c, CreatedDate, ClosedDate
FROM Case
WHERE CreatedDate = TODAY
  AND Status IN ('Closed', 'Fechado Com Sucesso', 'Protocolo Fechado')
  AND ClosedDate != null
LIMIT 2000
```

2. Calcular a duração (`ClosedDate - CreatedDate`) em pós-processamento (jq ou python no arquivo salvo pelo harness), agregando por categoria e/ou por `CreatedAutomatically__c` (média, mediana, p90).
3. Se o volume do dia for muito alto, restrinja por categoria ou reduza o período antes de rodar — não tente puxar todos os casos encerrados do dia de uma vez sem necessidade.

## Queries de referência

Veja `references/queries.md` para o catálogo completo de queries agregadas prontas (volume por dia, status, prioridade, categoria, cruzamento categoria x automático, qualidade de dado, amostra para SLA), incluindo os totais já observados neste org como referência de sanidade.

## Dashboards e automação

- Para montar um dashboard/artifact com os resultados (KPIs, gráfico de barras por categoria, pizza por status, tendência diária), use a skill `dataviz` — ela já define o padrão visual e de cores a seguir; não reinvente estilos de gráfico aqui.
- Para gerar esse dashboard automaticamente todo dia (ex.: resumo do dia anterior ao início da manhã), configure uma Routine com `create_trigger` (cron diário), com um prompt que reexecute esta skill sobre o período de ontem. Isso só deve ser feito quando o usuário pedir explicitamente uma rotina agendada — não crie uma Routine por conta própria.
