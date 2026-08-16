# PLANO: DASHBOARD EXECUTIVO DE CASOS SALESFORCE
## Arquitetura v2: 100% GitHub (Actions + Pages)

**Status:** Plano Aprovado - Pronto para Implementação
**Data:** 2026-08-15
**Repositório:** brunotrolo/brunotrolo
**Role:** AI Solution Architect

---

## CONTEXTO E MOTIVO DA MUDANÇA DE ARQUITETURA

A primeira versão deste plano usava Apps Script + Google Sheets. Ao decidir migrar o projeto irmão (monitoramento preditivo) para GitHub Actions + Pages — eliminando a dependência de navegador aberto que o Colab exigia — faz sentido aplicar a mesma arquitetura aqui, por consistência e porque ela é estritamente mais simples para este caso: o dashboard de Casos é **só leitura** (nenhum feedback humano precisa ser gravado), então nem o mecanismo de GitHub Issues do projeto irmão é necessário aqui.

- **GitHub Actions** substitui o Apps Script como coletor — roda em `schedule` (cron a cada 10 min), 100% headless
- **Arquivos JSON versionados no repositório** substituem o Google Sheets
- **GitHub Pages** substitui o Web App do Apps Script como front-end, com os mesmos toggles e auto-refresh já especificados na v1

**Resultado:** arquitetura ainda mais enxuta que a v1 — sem Apps Script, sem Sheets, sem navegador aberto, sem nenhum passo manual.

---

## ARQUITETURA

```
Salesforce (objeto Case)
    ↓ (GitHub Actions, cron a cada 10 min, runner com Python)
    ├─ Autentica via OAuth 2.0 refresh_token grant (credenciais em GitHub Secrets)
    │  └─ Credenciais: SF_CLIENT_ID, SF_CLIENT_SECRET, SF_REFRESH_TOKEN (compartilhadas com projeto irmão)
    ├─ Consulta Case via Salesforce REST API (/services/data/v60.0/query)
    │  └─ SOQL: SELECT Id, CaseNumber, Status, Priority, Origin, RecordType.Name, Owner.Name, CreatedDate, ClosedDate, IsClosed FROM Case WHERE CreatedDate = LAST_N_DAYS:30
    └─ Agrega e gera JSON: snapshot atual + histórico para tendências
         ↓
    Commit automático no branch `data` (mesmo padrão do projeto irmão)
         ↓
GitHub Pages (site estático: HTML/CSS/JS, deploy raro — só quando interface muda)
    ↓ (JS busca os JSONs direto do branch `data` via raw.githubusercontent.com)
    ↓ (auto-refresh client-side a cada 10 min, sem novo deploy)
Dashboard com toggles (Agrupamento / Período / Escopo) + gráficos Google Charts
```

Mesma lógica de separação `master` (código) / `data` (dados) e mesmo motivo já detalhado no `PREDICTIVE_MONITORING_PLAN.md`: o cron só dispara para workflows definidos no branch padrão, e manter os dados num branch separado evita poluir o histórico de código com um commit a cada 10 minutos.

---

## DADOS E MÉTRICAS

**Consulta Salesforce (mesma da v1):**
```sql
SELECT Id, CaseNumber, Status, Priority, Origin, RecordType.Name,
       Owner.Name, CreatedDate, ClosedDate, IsClosed
FROM Case
WHERE CreatedDate = LAST_N_DAYS:30
ORDER BY CreatedDate DESC
```

**Métricas executivas:** total aberto/fechado, distribuição por Status/Prioridade/Dono/Origem, aging (casos abertos há mais de X dias), tendência de criados vs. fechados por dia.

**Toggles (client-side, sem nova chamada ao backend a cada clique):**
- **Agrupamento:** Por Status | Por Prioridade | Por Dono | Por Origem
- **Período:** Hoje | Últimos 7 dias | Últimos 30 dias | Todos os casos abertos
- **Escopo:** Todos | Somente Abertos | Somente Fechados

**Risco de volume:** SOQL sem paginação retorna até 2.000 registros — validar volume real de casos em 30 dias antes de decidir se paginação (`nextRecordsUrl`) é necessária.

---

## ESTRUTURA DE ARQUIVOS

```
case-dashboard/
├── scripts/
│   ├── collect_cases.py       (autentica, consulta Case, agrega, gera JSON)
│   └── requirements.txt       (requests, pandas)
├── site/                       (fonte do GitHub Pages)
│   ├── index.html
│   ├── styles.css
│   └── app.js                  (fetch dos JSONs, toggles, Google Charts, auto-refresh)
└── data/                        (só existe no branch `data`)
    ├── snapshot.json             (estado atual dos casos)
    └── metrics_history.json      (série histórica para os gráficos de tendência)

.github/workflows/
├── case-dashboard-collect.yml   (cron */10 * * * *, coleta + commit no branch data)
└── case-dashboard-tests.yml     (roda pytest a cada push/PR em case-dashboard/**)
```

---

## EXEMPLO DE WORKFLOW

```yaml
name: Coleta de Casos - Dashboard Executivo
on:
  schedule:
    - cron: '*/10 * * * *'
  workflow_dispatch:

jobs:
  collect:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install -r case-dashboard/scripts/requirements.txt
      - run: python case-dashboard/scripts/collect_cases.py --output-dir /tmp/data-output
        env:
          SF_CLIENT_ID: ${{ secrets.SF_CLIENT_ID }}
          SF_CLIENT_SECRET: ${{ secrets.SF_CLIENT_SECRET }}
          SF_REFRESH_TOKEN: ${{ secrets.SF_REFRESH_TOKEN }}
      - name: Publica no branch data
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git fetch origin data
          git checkout data
          mkdir -p case-dashboard/data
          cp -r /tmp/data-output/* case-dashboard/data/
          git add case-dashboard/data/
          git commit -m "Atualiza dados de casos $(date -u +%Y-%m-%dT%H:%M:%SZ)" || echo "Sem mudanças"
          git push origin data
```

**Credenciais:** reaproveita os mesmos GitHub Secrets (`SF_CLIENT_ID`, `SF_CLIENT_SECRET`, `SF_REFRESH_TOKEN`) já configurados para o projeto de monitoramento preditivo — **sem necessidade de nova configuração de autenticação**.

---

## SETUP INICIAL (Pré-requisitos)

**Antes de começar a Fase 1, confirme:**

### 1. Requisitos técnicos obrigatórios
- [ ] **Repositório `brunotrolo/brunotrolo` é público** (necessário para GitHub Actions com minutos ilimitados e GitHub Pages gratuito)
- [ ] **GitHub Pages está habilitado** no repositório (Settings → Pages → Source: Deploy from a branch, branch `master`)
- [ ] **Branch `data` existe** (ou será criado automaticamente pelo workflow na primeira execução)
- [ ] **Python 3.11+** está disponível (confirmado no runner `ubuntu-latest` do GitHub Actions)

### 2. Credenciais OAuth Salesforce

**Reutilize as mesmas credenciais do projeto de monitoramento preditivo** — não é necessário criar um novo Connected App. As credenciais já devem estar em GitHub Secrets:
- `SF_CLIENT_ID` ✓
- `SF_CLIENT_SECRET` ✓
- `SF_REFRESH_TOKEN` ✓

Se ainda não existem (primeira execução), consulte a seção "SETUP INICIAL" em `PREDICTIVE_MONITORING_PLAN.md` para obter as credenciais.

### 3. Validação de conectividade IP (Salesforce)

Mesma verificação que o projeto irmão:
- [ ] **Verificar Trusted IP Range** no Salesforce Setup (Setup → Security → Network Access)
- [ ] **Verificar limite de rate limit** (padrão: 15 req/seg — uma SOQL a cada 10 min está bem abaixo)

### 4. Teste exploratório de volume e estrutura de Case

Use MCP Salesforce (Claude Code) antes de Fase 1:

**Validar volume:**
```sql
SELECT COUNT() FROM Case WHERE CreatedDate = LAST_N_DAYS:30
```

Deve retornar um número. Se **< 2.000**, paginação não é necessária na Fase 1. Se **> 2.000**, será implementada na Fase 3 (Hardening).

**Validar campos:**
```sql
SELECT Id, CaseNumber, Status, Priority, Origin, RecordType.Name, 
       Owner.Name, CreatedDate, ClosedDate, IsClosed 
FROM Case 
WHERE CreatedDate = LAST_N_DAYS:30
LIMIT 5
```

Deve retornar registros com todos os campos populados. Se algum retornar NULL para maioria dos registros, pode haver customização missing (ex: RecordType, Owner, Priority).

---

## FRONT-END (GitHub Pages)

```javascript
// case-dashboard/site/app.js
const DATA_BASE = 'https://raw.githubusercontent.com/brunotrolo/brunotrolo/data/case-dashboard/data';
let currentData = null;

async function fetchSnapshot() {
  const res = await fetch(`${DATA_BASE}/snapshot.json?t=${Date.now()}`);
  return res.json();
}

function renderDashboard(data) {
  currentData = data;
  const groupBy = document.getElementById('groupByToggle').value;
  const period = document.getElementById('periodToggle').value;
  const scope = document.getElementById('scopeToggle').value;
  const filtered = applyToggles(data.cases, groupBy, period, scope);
  drawChart(filtered); // Google Charts
}

async function refresh() {
  renderDashboard(await fetchSnapshot());
}
setInterval(refresh, 10 * 60 * 1000);
refresh();

// Toggles só re-renderizam o dataset já carregado, sem novo fetch
document.querySelectorAll('.toggle').forEach(el =>
  el.addEventListener('change', () => renderDashboard(currentData))
);
```

Ambos os dashboards (monitoramento preditivo e Casos) podem conviver no **mesmo site do GitHub Pages**, em caminhos diferentes (`/monitoring/` e `/cases/`), já que cada um busca seus próprios JSONs de subpastas distintas do branch `data`.

---

## ESQUEMAS DE DADOS (JSON)

### snapshot.json

```json
{
  "timestamp": "2026-08-15T14:10:00Z",
  "total_cases": 247,
  "open_cases": 183,
  "closed_cases": 64,
  "metrics_by_status": {
    "New": 42,
    "In Progress": 89,
    "On Hold": 15,
    "Closed": 64,
    "Escalated": 37
  },
  "metrics_by_priority": {
    "Low": 85,
    "Medium": 98,
    "High": 52,
    "Critical": 12
  },
  "metrics_by_owner": {
    "John Smith": 28,
    "Jane Doe": 35,
    "Support Team Queue": 72,
    "Unassigned": 112
  },
  "metrics_by_origin": {
    "Email": 145,
    "Phone": 62,
    "Web": 40
  },
  "aging_open_cases": {
    "0_to_1_day": 45,
    "1_to_3_days": 62,
    "3_to_7_days": 48,
    "7_to_30_days": 22,
    "over_30_days": 6
  }
}
```

### metrics_history.json

```json
{
  "daily_metrics": [
    {
      "date": "2026-08-15",
      "timestamp": "2026-08-15T14:10:00Z",
      "total_cases": 247,
      "open_cases": 183,
      "closed_cases": 64,
      "created_today": 12,
      "closed_today": 8,
      "avg_age_days": 5.2,
      "critical_count": 12
    },
    {
      "date": "2026-08-14",
      "timestamp": "2026-08-14T14:10:00Z",
      "total_cases": 243,
      "open_cases": 179,
      "closed_cases": 64,
      "created_today": 9,
      "closed_today": 5,
      "avg_age_days": 5.1,
      "critical_count": 11
    }
  ],
  "summary": {
    "period": "last_30_days",
    "total_created": 312,
    "total_closed": 268,
    "trend_open_cases": "stable",
    "backlog_increase_percent": 1.6
  }
}
```

**Granularidade:**
- Um snapshot a cada 10 minutos (quando workflow roda)
- Histórico mantém últimos 30 dias em `metrics_history.json`
- Agregações pré-calculadas: Status, Priority, Owner, Origin, Aging

---

## TROUBLESHOOTING COMUM

| Erro | Solução |
|-----|---------|
| `403 Forbidden` ao chamar Salesforce REST API | Verificar IP Trusted Range (Setup → Security → Network Access) ou validar `refresh_token` manualmente |
| `401 Unauthorized` ("invalid_grant") | Token refresh falhou — `refresh_token` expirou ou foi revogado; renovar via projeto irmão ou gerar novo |
| `414 Request URI Too Long` | SOQL está muito complexa — simplificar a consulta ou usar paginação |
| Workflow nunca executa | Confirmar que o workflow `.yml` está no branch `master` (cron só dispara do branch padrão) |
| GitHub Pages mostra 404 | Verificar Settings → Pages → Source (deve ser "Deploy from a branch") e que `master` tem `case-dashboard/site/index.html` |
| Dashboard mostra dados antigos | Verificar se `latest.json` no branch `data` tem timestamp recente; se estiver congelado, o workflow falhou |

---

## FASES

### Fase 0 — MVP com Dados Mockados (sem Salesforce)

**Objetivo:** Validar arquitetura completa (micro-serviços, testes, logging) **sem depender de Salesforce real**. Dados mockados simulam casos reais.

**Setup e Testes:**
```bash
# 1. Instalar dependências
pip install -r services/aggregation/requirements.txt
pip install pytest pytest-cov

# 2. Rodar testes (tudo com mocks)
pytest services/aggregation/ -v --cov=services/aggregation

# 3. Rodar pipeline completo
python case-dashboard/scripts/orchestrate.py --mode mock --log-file /tmp/cases.log

# 4. Inspecionar logs
tail -50 /tmp/cases.log | jq .

# 5. Verificar JSONs gerados
cat case-dashboard/data/snapshot.json | jq .
```

**Definition of Done:**
- [ ] Testes pytest passando com ≥80% coverage
- [ ] Logs estruturados registram cada operação
- [ ] JSONs (snapshot.json, metrics_history.json) são gerados
- [ ] Front-end renderiza dashboard com dados mockados
- [ ] GitHub Pages serve o dashboard
- [ ] Transição para dados reais requer ≤5 mudanças

**Transição para Fase 1:**
1. Obter credenciais OAuth
2. Adicionar nos GitHub Secrets
3. Trocar `services/aggregation/src/mock_cases.py` por `salesforce_client.py`
4. Rodar testes — tudo funciona igual

### Fase 1 — Produção com Dados Reais (Salesforce)
- `services/aggregation/src/collect_cases.py` funcional com Salesforce real
- Commit automático no branch `data` a cada 10 min
- Página no GitHub Pages exibindo tabela de casos com dados reais
- **Definition of Done:** site publicado, mostrando dados reais de Case, atualizados a cada 10 min

### Fase 2 — Dashboard Completo (toggles + gráficos + auto-refresh)
- Implementa os 3 toggles e os gráficos (Google Charts: barras para distribuição, linha para tendência)
- Auto-refresh a cada 10 min sem reload manual
- **Definition of Done:** toggles funcionam instantaneamente (sem novo fetch), dashboard atualiza sozinho

### Fase 3 — Hardening
- Paginação SOQL se volume de Cases > 2.000
- Indicador de "dados desatualizados" se `timestamp` estiver > 15 min
- CI/CD: testes rodando antes de deploy (pytest + Jest coverage ≥80%)

---

## DECISÕES TÉCNICAS

1. **Mesma arquitetura do projeto irmão** (`PREDICTIVE_MONITORING_PLAN.md`), sem o mecanismo de Issues — este dashboard é só leitura, não precisa de feedback humano gravado.
2. **Reaproveita os mesmos GitHub Secrets** de autenticação Salesforce.
3. **Convive no mesmo site do GitHub Pages** que o projeto de monitoramento preditivo, em subcaminho próprio.
4. **Google Charts** carregado via CDN do próprio Google — sem risco de bloqueio de domínio externo por política corporativa.

---

## CRITÉRIOS DE SUCESSO

- Fase 1 conclui com dados reais de Case visíveis no site
- Fase 2: os 3 toggles funcionam instantaneamente e o dashboard atualiza sozinho a cada 10 min
- Fase 3: pipeline CI roda testes automaticamente
- **Custo total: $0/mês** — GitHub Actions e Pages gratuitos, sem Apps Script, sem Sheets
