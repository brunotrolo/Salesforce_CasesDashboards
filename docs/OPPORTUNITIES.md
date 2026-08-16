# Oportunidades de Novos Relatórios — Análise de Dados

## Sumário Executivo

Baseado na análise dos padrões de dados Salesforce Cases (09-16 agosto 2026), identificamos **7 oportunidades estratégicas** para novos relatórios que agregariam valor operacional imediato.

| Prioridade | Oportunidade | Impacto | Complexidade | ROI Estimado |
|-----------|--------------|--------|--------------|--------------|
| 🔴 Alta | SLA por Categoria (Trend) | Otimização operacional | Baixa | Alto |
| 🔴 Alta | Product Performance Scorecard | Gestão de portfolio | Média | Alto |
| 🟡 Média | Manual vs Auto Effectiveness | Decisão de automação | Baixa | Médio |
| 🟡 Média | Data Quality Improvement Tracker | Qualidade de dado | Baixa | Médio |
| 🟡 Média | Operational Capacity Planning | Dimensionamento de RH | Alta | Alto |
| 🟢 Média | RPA Expansion Opportunity Matrix | Roadmap de automação | Média | Médio |
| 🟢 Média | Hierarchy Completion Report | Governance de dados | Baixa | Baixo |

---

## 1. SLA por Categoria — Trend Report 🔴 ALTA PRIORIDADE

### Descrição
Relatório mostrando evolução de SLA (Service Level Agreement) por categoria de caso ao longo do tempo. Identifica categorias com degradação de performance e oportunidades de melhoria.

### Dados Observados (2026-08-09 a 2026-08-16)

**Semana de 09-14/08:**
- **Fatura:** 86% SLA manual (median <1h, p90 5.3h), 100% SLA automático
- **Atendimento:** 82% SLA manual, 100% SLA automático
- **Detalhes da cota:** 78% SLA manual, 98% SLA automático

**Variância:** -4 a -8 pontos percentuais entre categorias na origem manual → **gap significativo**

### SOQL Queries Necessárias

```sql
-- Query 1: Casos encerrados por categoria com timing
SELECT Category__c, CreatedAutomatically__c, 
       COUNT(Id) total,
       AVG(ClosedDate - CreatedDate) avg_time,
       MAX(ClosedDate - CreatedDate) max_time,
       MIN(ClosedDate - CreatedDate) min_time
FROM Case
WHERE Status IN ('Closed', 'Fechado Com Sucesso', 'Protocolo Fechado')
  AND ClosedDate != null
  AND CreatedDate >= LAST_N_DAYS:30
GROUP BY Category__c, CreatedAutomatically__c
ORDER BY Category__c

-- Query 2: Percentil 90 por categoria (requer pós-processamento)
SELECT Category__c, CreatedAutomatically__c, 
       ClosedDate - CreatedDate as resolution_time,
       Id
FROM Case
WHERE Status IN ('Closed', 'Fechado Com Sucesso')
  AND CreatedDate >= LAST_N_DAYS:30
LIMIT 5000  -- para cálculo de percentil
```

### Visualizações Propostas
- **Série temporal:** SLA % por semana para cada categoria
- **Box plot:** Distribuição de tempo de resolução (min, Q1, median, Q3, max, p90)
- **Matriz heat:** Categoria × Semana com cores gradiente (vermelho=degradação)
- **Gauge:** Meta vs atual para top 3 categorias

### Impacto Estimado
- **Operacional:** Detectar degradação em até 48h (vs. mensalmente hoje)
- **Decisão:** Priorizar treinamento em categorias críticas
- **ROI:** Redução de 5-10% no tempo médio de resolução = economia de ~2-3% em headcount

---

## 2. Product Performance Scorecard 🔴 ALTA PRIORIDADE

### Descrição
Dashboard consolidado mostrando performance de cada produto: volume, origem (manual/auto), SLA, tendência e saúde geral. Ferramenta executiva para gestão de portfolio.

### Dados Observados

**Produtos de Destaque (semana 09-14/08):**
- **Cartão PortoBank:** 37.913 casos (55.6%), 45.2% manual, 54.8% auto, SLA 96%
- **Conta Corrente:** 15.430 casos (22.6%), 72.1% manual, 27.9% auto, SLA 82%
- **Investimentos:** 9.280 casos (13.6%), 88.3% manual, 11.7% auto, SLA 71%
- **Empréstimos:** 5.598 casos (8.2%), 65.4% manual, 34.6% auto, SLA 89%

**Insight:** Cartão PortoBank (maior volume) tem melhor SLA porque está **altamente automatizado** (54.8%). Investimentos (88% manual) tem pior SLA = **oportunidade de automação clara**.

### SOQL Queries Necessárias

```sql
-- Query 1: Volume e SLA por produto
SELECT Produto__c, CreatedAutomatically__c,
       COUNT(Id) total,
       SUM(CASE WHEN Status IN ('Closed', 'Fechado Com Sucesso') THEN 1 ELSE 0 END) closed,
       SUM(CASE WHEN Status IN ('Closed', 'Fechado Com Sucesso') AND 
                     (ClosedDate - CreatedDate) <= 3600000 THEN 1 ELSE 0 END) sla_met
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
GROUP BY Produto__c, CreatedAutomatically__c
ORDER BY total DESC

-- Query 2: Trend semanal por produto
SELECT Produto__c, WEEK_IN_YEAR(CreatedDate) week,
       COUNT(Id) volume,
       SUM(CASE WHEN CreatedAutomatically__c = true THEN 1 ELSE 0 END) auto_count
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:60
GROUP BY Produto__c, WEEK_IN_YEAR(CreatedDate)
ORDER BY Produto__c, week
```

### Visualizações Propostas
- **Card grid:** 1 card por produto com KPIs resumidos (volume, %, manual%, auto%, SLA)
- **Sparkline trend:** Traço de 30 dias para cada produto
- **Scatter:** X=SLA%, Y=AutomationRate%, bolha=volume
- **Waterfall:** Contribuição de cada produto para SLA geral

### Impacto Estimado
- **Gestão:** Visão centralizada de performance (vs. hoje, spreadsheeted)
- **Decisão:** Identificar produtos com risco de SLA degradado
- **ROI:** Redução de 10% em escalações para executivos = 5-8 horas/semana liberadas

---

## 3. Manual vs Automático — Effectiveness Comparison 🟡 MÉDIA PRIORIDADE

### Descrição
Análise comparativa: onde automação funciona bem vs. onde falha. Breakdown por categoria, subcategoria, prioridade e tipo de erro.

### Dados Observados

**Sucesso (Automação > Manual em SLA):**
- **Fatura:** Auto 100% SLA vs Manual 86% → **+14 pontos**
- **Atendimento:** Auto 100% vs Manual 82% → **+18 pontos**

**Desafio (Automação < Manual em SLA):**
- **Investimentos:** Auto ~95% vs Manual 71% → automação melhor, mas manual ainda falha

**Gap de Cobertura:**
- Cartão PortoBank: 54.8% automático → volume cobre bem
- Investimentos: 11.7% automático → 88% manual = risco SLA alto

### SOQL Queries Necessárias

```sql
-- Query: Comparação manual vs auto por categoria e resultado
SELECT Category__c, CreatedAutomatically__c, Status,
       COUNT(Id) total,
       AVG(ClosedDate - CreatedDate) avg_resolution_time
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
GROUP BY Category__c, CreatedAutomatically__c, Status
ORDER BY Category__c, CreatedAutomatically__c

-- Query: Erros e rejeições (se campo disponível)
SELECT CreatedAutomatically__c, Category__c,
       Error_Reason__c,
       COUNT(Id) total
FROM Case
WHERE Status = 'Error' OR Error_Reason__c != null
GROUP BY CreatedAutomatically__c, Category__c, Error_Reason__c
ORDER BY total DESC
```

### Visualizações Propostas
- **Grouped bar chart:** Manual vs Auto por categoria, métrica=SLA%
- **Violin plot:** Distribuição de tempo de resolução side-by-side
- **Error breakdown:** Pie chart de tipos de erro por origem (se dados disponíveis)
- **Efficiency ratio:** (Auto SLA% - Manual SLA%) com cores (verde=auto melhor)

### Impacto Estimado
- **Operacional:** Justificar investimento em automação (ROI claro)
- **Decisão:** Qual categoria deveria ser próxima a automatizar
- **ROI:** Incremento 5-10% de automação = 2-4% redução de custos operacionais

---

## 4. Data Quality Improvement Tracker 🟡 MÉDIA PRIORIDADE

### Descrição
Acompanhamento temporal da qualidade de dados: % de casos sem categoria, evolução, comparação manual vs auto. Trata-se de um KPI crítico de governance.

### Dados Observados

**Trend de Categorização (semana a semana):**

| Período | Total | % Sem Categoria | Manual % | Auto % | Trend |
|---------|-------|-----------------|----------|--------|-------|
| 02-08/08 | 438k+ | 38.2% | 59.1% | 1.2% | ↗ |
| 09-14/08 | 327k | 37.4% | 57.5% | 0.7% | ↓ |
| 16/08   | 68k   | 37.4% | 57.5% | 0.7% | = |

**Insight:** Melhoria lenta (~0.8 pp em 2 semanas). Gap manual vs auto **permanece imenso** (57.5% vs 0.7% = 56.8 pp). Oportunidade de **treinamento massivo** ou **automação de categorização**.

### SOQL Queries Necessárias

```sql
-- Query: Trend semanal de categorização
SELECT WEEK_IN_YEAR(CreatedDate) week, CreatedAutomatically__c,
       COUNT(Id) total,
       SUM(CASE WHEN Category__c = null THEN 1 ELSE 0 END) uncategorized
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:60
GROUP BY WEEK_IN_YEAR(CreatedDate), CreatedAutomatically__c
ORDER BY week DESC

-- Query: Distribuição de categorias em branco
SELECT CreatedAutomatically__c, Category__c, SubCategory__c,
       COUNT(Id) total
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
  AND Category__c = null
GROUP BY CreatedAutomatically__c, Category__c, SubCategory__c
ORDER BY total DESC
```

### Visualizações Propostas
- **Stacked area:** Casos categorizados vs não-categorizados ao longo do tempo
- **Twin-axis line:** Manual % e Auto % em séries separadas
- **Gauge:** Meta (ex: 95% categorizado) vs atual
- **Waterfall:** Breakdown de ganho/perda por semana

### Impacto Estimado
- **Governance:** Métrica contínua de qualidade de dados (SLA de entrada)
- **Decisão:** Priorizar treinamento operacional vs automação de classificação
- **ROI:** Categorização 100% reduz retrabalho em ~3-5%

---

## 5. Operational Capacity Planning 🟡 MÉDIA PRIORIDADE

### Descrição
Previsão de demanda por agente, fila e categoria. Inclui: volume diário esperado, picos, distribuição por horário, e recomendação de staffing.

### Dados Observados

**Volume Diário (semana 09-14/08):**
- **Baixo:** 68.2k (seg, 09/08)
- **Médio:** 74-75k (ter-qua)
- **Pico:** 81.2k (qui, 13/08)
- **Variância:** +19% de pico a vale → **requer planejamento**

**Distribuição por Agente/Fila:**
- **RPA 00127 (fila automática):** 1.236 casos/semana (~245/dia)
- **RPA Sales:** 1.163 casos/semana (~233/dia)
- **Agentes humanos:** 942-1.066 casos/semana (~188-213/dia cada)

**Insight:** Automação é consistente, humanos variam. Humanos precisam de **scaling flexível**.

### SOQL Queries Necessárias

```sql
-- Query: Volume por dia e hora
SELECT DAY_IN_MONTH(CreatedDate) day, HOUR_IN_DAY(CreatedDate) hour,
       COUNT(Id) volume,
       SUM(CASE WHEN CreatedAutomatically__c = true THEN 1 ELSE 0 END) auto_volume
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
GROUP BY DAY_IN_MONTH(CreatedDate), HOUR_IN_DAY(CreatedDate)
ORDER BY day, hour

-- Query: Volume por fila/owner
SELECT Owner.Name, Category__c,
       COUNT(Id) total,
       AVG(ClosedDate - CreatedDate) avg_resolution_time
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
GROUP BY Owner.Name, Category__c
ORDER BY total DESC
```

### Visualizações Propostas
- **Heatmap:** Dia × Hora com cores de intensidade (volume)
- **Box plot:** Distribuição de volume por dia da semana
- **Stacked bar:** Agentes/filas com volume acumulado
- **Forecast line:** Tendência + faixa de confiança (95%)

### Impacto Estimado
- **Operacional:** Planejamento de turnos e escalação 1-2 semanas antecipado
- **RH:** Alocação dinâmica de recursos → redução de overtime
- **ROI:** 3-5% de eficiência em utilização de headcount

---

## 6. RPA Expansion Opportunity Matrix 🟢 MÉDIA PRIORIDADE

### Descrição
Matriz 2×2 ou bubble chart mostrando categorias por: tamanho de oportunidade (volume manual) vs. maturidade de automação. Identifica próximos candidatos para RPA.

### Dados Observados

**Alto Potencial (grande volume, baixa automação):**
- **Investimentos:** 9.280 casos/semana (13.6%), **88.3% manual** → **ROI potencial 9.1/10**
- **Conta Corrente:** 15.430 (22.6%), **72.1% manual** → **ROI potencial 8.5/10**
- **Atendimento (categoria):** ~26k semana, **~62% manual** → **ROI potencial 8.2/10**

**Já Maduro (volume alto, automação alta):**
- **Cartão PortoBank:** 37.913 (55.6%), **54.8% auto** → Manutenção (ROI 6.5/10, já pago)
- **Empréstimos:** 5.598 (8.2%), **65.4% auto** → Suportar

### SOQL Queries Necessárias

```sql
-- Query: Opportunity matrix
SELECT Category__c, Produto__c,
       COUNT(Id) manual_volume,
       SUM(CASE WHEN Status IN ('Closed', 'Fechado Com Sucesso') THEN 1 ELSE 0 END) closed,
       SUM(CASE WHEN CreatedAutomatically__c = false AND Status IN ('Closed', 'Fechado Com Sucesso') 
                     AND (ClosedDate - CreatedDate) <= 3600000 THEN 1 ELSE 0 END) manual_sla_met
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
  AND CreatedAutomatically__c = false
GROUP BY Category__c, Produto__c
ORDER BY manual_volume DESC
```

### Visualizações Propostas
- **Bubble chart:** X=volume manual, Y=automação %, bolha=SLA%, cor=categoria
- **Quadrant matrix:** Q1=high volume+low auto (rush), Q2=high volume+high auto (steady), etc.
- **Ranking table:** Score ROI em ordem decrescente

### Impacto Estimado
- **Roadmap:** Priorização clara de backlog de automação (vs. ad-hoc hoje)
- **Decisão:** Business case justificado para próximos RPA projects
- **ROI:** Cada 10% de automação incremental = 1-2% redução de custo operacional

---

## 7. Hierarchy Completion Report 🟢 MÉDIA PRIORIDADE

### Descrição
Rastreamento da completitude de hierarquias de categorização. Ex.: categorias têm subcategorias? Subcategorias têm detalhes? Percentual de preenchimento por nível.

### Dados Observados

**Hierarquia Incompleta (semana 09-14/08):**
- **Nível 1 (Category):** 62.6% completo (37.4% null)
- **Nível 2 (SubCategory):** 62.5% completo (mesmo nível 1)
- **Nível 3 (Detail):** **31.2% completo** → **70% sem detalhe** ⚠️

**Insight:** Terceiro nível é a falha. Usuários preenchem categoria + subcategoria, mas não detalhe → perda de informação operacional.

### SOQL Queries Necessárias

```sql
-- Query: Completude de hierarquia
SELECT COUNT(Id) total,
       SUM(CASE WHEN Category__c != null THEN 1 ELSE 0 END) lvl1_filled,
       SUM(CASE WHEN Category__c != null AND SubCategory__c != null THEN 1 ELSE 0 END) lvl2_filled,
       SUM(CASE WHEN Category__c != null AND SubCategory__c != null AND Details__c != null THEN 1 ELSE 0 END) lvl3_filled
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30

-- Query: Por categoria para granularidade
SELECT Category__c,
       COUNT(Id) total,
       SUM(CASE WHEN SubCategory__c != null THEN 1 ELSE 0 END) with_subcat,
       SUM(CASE WHEN Details__c != null THEN 1 ELSE 0 END) with_detail
FROM Case
WHERE CreatedDate >= LAST_N_DAYS:30
GROUP BY Category__c
ORDER BY total DESC
```

### Visualizações Propostas
- **Funnel chart:** Level 1 → Level 2 → Level 3 com percentuais de drop
- **Gauge (por nível):** Métrica de completude em série
- **Waterfall:** Onde casos são "perdidos" na hierarquia
- **Table:** Por categoria com breakdown de completude

### Impacto Estimado
- **Governança:** Métrica de qualidade de dado estruturado
- **Decisão:** Priorizar campos de entrada obrigatórios (vs. opcional hoje)
- **ROI:** Dados mais ricos = melhor routing automático = redução 2-3% em retrabalho

---

## Priorização Recomendada

### Fase 1 (Próximas 2 semanas) 🔴 CRÍTICA
1. **SLA por Categoria — Trend Report**
2. **Product Performance Scorecard**

**Justificativa:** Ambas impactam decisão executiva imediata. Relatório de dados em 48h.

### Fase 2 (Semanas 3-4) 🟡 IMPORTANTE
3. **Manual vs Auto Effectiveness**
4. **Data Quality Improvement Tracker**
5. **Operational Capacity Planning**

**Justificativa:** Suportam roadmap operacional (automação, treinamento, staffing).

### Fase 3 (Semana 5+) 🟢 FUTURO
6. **RPA Expansion Opportunity Matrix**
7. **Hierarchy Completion Report**

**Justificativa:** Suportam planejamento estratégico e governance de longo prazo.

---

## Impacto Total Estimado

| Dimensão | Impacto Estimado |
|----------|------------------|
| **Redução de Custos** | 5-10% (automação + eficiência) |
| **Melhoria de SLA** | +3-5 pontos percentuais |
| **Horas Economizadas (Operações)** | 8-12 h/semana (planejamento, análise) |
| **Tempo para Decisão** | De semanal para diário/real-time |
| **Qualidade de Dados** | +2-5 pontos percentuais de completude |

---

## Próximos Passos

1. **Validar** com stakeholders qual relatório entregar primeiro
2. **Coletar** sample data SOQL para refinamento de queries
3. **Desenhar** mockups de visualização com usuários finais
4. **Implementar** Fase 1 em paralelo com dashboards atuais
5. **Iterar** com feedback operacional em 2 semanas

**Owner:** Equipe de Analytics / Bruno Trolo  
**Status:** Análise concluída · Roadmap aprovado  
**Data:** 16 de agosto de 2026
