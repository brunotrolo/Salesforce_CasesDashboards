# Salesforce Cases Dashboard

Dashboard executivo de Cases (tickets/atendimentos) do Salesforce com análise gerencial baseada em dados reais consumidos via **MCP SalesforceRead**.

## 📊 O que você verá

- **KPIs de status** — Volume total, manual vs automático, em atendimento, encerrados
- **Composição por status** — New, Em atendimento, Closed, InAnalysis etc.
- **Top categorias** — Quais tipos de casos são mais comuns
- **Análise de qualidade** — Gap de categorização manual vs automática
- **Manual vs Automático** — Percentual de automação por categoria

## 🚀 Começar

### Online
Acesse: https://brunotrolo.github.io/Salesforce_CasesDashboards/

### Localmente
```bash
python3 scripts/generate_dashboard.py
open docs/dashboard.html
```

## ⚙️ Como funciona

### Arquitetura

1. **Script Python** (`scripts/generate_dashboard.py`)
   - Conecta ao Salesforce via MCP SalesforceRead
   - Executa queries SOQL para extrair dados de Cases
   - Processa métricas (volume, SLA, qualidade)
   - Gera HTML standalone autossuficiente

2. **MCP Integration**
   - Usa `mcp__SalesforceRead__soqlQuery` para SOQL
   - Autenticação via OAuth2 (credenciais em GitHub Secrets)
   - Somente leitura — zero risco de mutação de dados

3. **Dashboard HTML**
   - Arquivo único, sem dependências externas
   - CSS embutido (Google Fonts com fallback)
   - Responsivo (desktop, tablet, mobile)
   - Otimizado para impressão e PDF

### Dados consumidos do Salesforce

Cada geração executa estas queries SOQL:

```sql
-- Volume total
SELECT COUNT(Id) total FROM Case WHERE CreatedDate = TODAY

-- Manual vs Automático
SELECT CreatedAutomatically__c, COUNT(Id) total
FROM Case WHERE CreatedDate = TODAY
GROUP BY CreatedAutomatically__c

-- Status
SELECT Status, COUNT(Id) total
FROM Case WHERE CreatedDate = TODAY
GROUP BY Status

-- Categorias
SELECT Category__c, COUNT(Id) total
FROM Case WHERE CreatedDate = TODAY
GROUP BY Category__c
```

## 🔄 Automação

Para gerar o dashboard automaticamente todos os dias às 08:00 AM (Brasília):

1. Configure GitHub Secrets (Settings → Secrets and variables → Actions):
   ```
   SF_CLIENT_ID
   SF_CLIENT_SECRET
   SF_REFRESH_TOKEN
   ```

2. Crie um workflow em `.github/workflows/generate-dashboard.yml`:
   ```yaml
   name: Generate Dashboard
   on:
     schedule:
       - cron: '12 12 * * *'  # 08:00 AM Brasília (UTC-3)
     workflow_dispatch:

   jobs:
     generate:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         
         - name: Set up Python
           uses: actions/setup-python@v4
           with:
             python-version: '3.11'
         
         - name: Install dependencies
           run: pip install -r requirements.txt
         
         - name: Generate dashboard
           env:
             SF_CLIENT_ID: ${{ secrets.SF_CLIENT_ID }}
             SF_CLIENT_SECRET: ${{ secrets.SF_CLIENT_SECRET }}
             SF_REFRESH_TOKEN: ${{ secrets.SF_REFRESH_TOKEN }}
           run: python3 scripts/generate_dashboard.py
         
         - name: Commit and push
           run: |
             git config user.name "GitHub Actions"
             git config user.email "actions@github.com"
             git add docs/dashboard.html
             git commit -m "chore: update dashboard" || true
             git push
   ```

3. O dashboard será atualizado automaticamente todo dia.

## 📋 Entendendo as métricas

### Manual vs Automático
- **Manual**: Casos abertos por atendentes humanos
- **Automático (RPA)**: Casos abertos por processos automatizados
- Análise: Onde há oportunidade de aumentar automação?

### Qualidade de Dado
- **Gap de categorização**: % de casos sem `Category__c` preenchida
- **Concentração**: Onde o problema é maior (manual ou automático)?
- **Ação**: Gap alto em manual → treinamento / automatização de preenchimento

### SLA (Tempo até fechamento)
- Média, mediana, P90 do tempo entre CreatedDate e ClosedDate
- Segmentado por origem (manual vs automático)
- Segmentado por categoria

## 🛠️ Customização

### Modificar template
1. Edite `scripts/generate_dashboard.py` → seção `TEMPLATE_HTML`
2. Mantenha a paleta de cores e tipografia original
3. Nunca remove campos de dados

### Adicionar novas queries
1. Adicione método em `SalesforceDataFetcher`
2. Chame em `DashboardGenerator.generate()`
3. Insira novo token no template

### Design
- **Paleta**: Teal (#0e6e6b), Warm paper (#f4f2ec), Slate ink (#20242b)
- **Fontes**: Newsreader (display), Sora (body)
- **Nunca**: Gradientes, shadows, cards aninhados

## 📚 Referências

- Template oficial: [SalesforceOdin_Dashboard](https://github.com/brunotrolo-bank/SalesforceOdin_Dashboard)
- MCP SalesforceRead: [Anthropic MCP](https://github.com/modelcontextprotocol)
- Documentação Salesforce: [Case object](https://developer.salesforce.com/docs/atlas.en-us.object_reference.meta/object_reference/sforce_api_objects_case.htm)

## 📝 Licença

MIT

---

**Gerado via MCP SalesforceRead** · Dados reais, zero dependências externas
