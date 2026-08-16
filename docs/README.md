# 📊 Salesforce Dashboard - GitHub Pages

Dashboard **100% estático** e hospedado no **GitHub Pages**, com dados **100% reais** do Salesforce via **MCP**.

## 🎯 Como Funciona

```
GitHub Actions (a cada 1h)
    ↓
Conecta ao Salesforce via MCP
    ↓
Extrai Cases, Reports, Accounts (dados REAIS)
    ↓
Gera JSONs em docs/data/
    ↓
Faz commit automático
    ↓
GitHub Pages atualiza o site
    ↓
Dashboard carrega JSONs via JavaScript
    ↓
Renderiza gráficos e tabelas em tempo real
```

## 🚀 Acessar o Dashboard

**Dashboard Live:** https://brunotrolo.github.io/Salesforce_CasesDashboards

### Funcionalidades

- ✅ **Cases por Status** - Visualização em donut chart
- ✅ **Casos por Prioridade** - Gráfico de barras
- ✅ **Tendência de Cases** - Últimos 15 dias
- ✅ **Top Accounts** - Por receita
- ✅ **Tabelas Interativas** - Com busca e filtros
- ✅ **Auto-Refresh** - A cada 5 minutos
- ✅ **Status de Sincronização** - Indica se dados são LIVE ou fallback
- ✅ **Timestamps** - Mostra quando foi última sync

## 🔧 Configuração

### 1. GitHub Secrets

Para usar dados **reais** do Salesforce, configure os secrets:

1. Vá para **Settings → Secrets and variables → Actions**
2. Adicione:
   - `SF_CLIENT_ID` - OAuth2 Client ID
   - `SF_CLIENT_SECRET` - OAuth2 Client Secret
   - `SF_REFRESH_TOKEN` - Refresh Token

**Como obter:**
```bash
# Usar MCP Salesforce para autenticar
python -c "
from services.mcp_client.src.salesforce_connector import MCPClient
# Seguir fluxo OAuth2
"
```

### 2. Ativar GitHub Pages

1. **Settings → Pages**
2. **Source:** Deploy from a branch
3. **Branch:** main
4. **Folder:** /docs
5. **Save**

Dashboard estará disponível em: `https://seu-usuario.github.io/Salesforce_CasesDashboards`

## 📅 Cronograma de Sincronização

Padrão: **A cada 1 hora** (configurável)

Editar `.github/workflows/fetch-salesforce-data.yml`:

```yaml
schedule:
  - cron: '0 * * * *'  # A cada 1 hora (padrão)
  # - cron: '0 */6 * * *'  # A cada 6 horas
  # - cron: '0 9 * * *'  # Diariamente às 9h
```

## 📁 Estrutura de Arquivos

```
docs/
├── index.html              # Dashboard (página principal)
├── css/
│   └── styles.css          # Estilos (design system completo)
├── js/
│   └── app.js              # App.js (carrega JSONs, renderiza gráficos)
└── data/
    ├── cases.json          # ⭐ Gerado por GitHub Actions
    ├── reports.json        # ⭐ Gerado por GitHub Actions
    ├── accounts.json       # ⭐ Gerado por GitHub Actions
    └── metadata.json       # ⭐ Gerado por GitHub Actions
```

## 🤖 Script de Sincronização

**Arquivo:** `scripts/salesforce-sync.py`

Executado automaticamente por GitHub Actions. Pode ser testado localmente:

```bash
# Configurar variáveis de ambiente
export SF_CLIENT_ID="seu_client_id"
export SF_CLIENT_SECRET="seu_client_secret"
export SF_REFRESH_TOKEN="seu_refresh_token"

# Executar script
python scripts/salesforce-sync.py
```

**Output:**
```
============================================================
🚀 Sincronização Salesforce → GitHub Pages
============================================================
✅ Salvou cases.json (25 registros)
✅ Salvou reports.json (15 registros)
✅ Salvou accounts.json (20 registros)
✅ Salvou metadata.json
============================================================
✅ SINCRONIZAÇÃO COMPLETA!
   Cases: 25
   Reports: 15
   Accounts: 20
   Status: SUCCESS
   Última atualização: 2026-08-16T10:30:45.123Z
============================================================
```

## 🔄 Workflow GitHub Actions

**Arquivo:** `.github/workflows/fetch-salesforce-data.yml`

Executa:
1. ✅ Setup Python 3.11
2. ✅ Instala dependências
3. ✅ Executa `scripts/salesforce-sync.py`
4. ✅ Faz commit automático em `docs/data/`
5. ✅ Push para main
6. ✅ GitHub Pages atualiza automaticamente

**Rodar manualmente:**
1. Vá para **Actions**
2. Selecione **"Fetch Salesforce Data"**
3. Clique **"Run workflow"**

## 📊 Dados de Fallback

Se Salesforce não estiver disponível, o script usa **dados de fallback** (mock):
- 25 cases de exemplo
- 15 reports de exemplo
- 15 accounts de exemplo

Dashboard continua funcionando com indicador `📦 Dados de Fallback`.

## 🎨 Design & Responsividade

- ✅ **Responsivo** - Funciona em desktop, tablet, mobile
- ✅ **Dark Mode** - Suportado (usa preferência do SO)
- ✅ **Acessibilidade** - WCAG 2.1 AA
- ✅ **Performance** - Sem dependências externas pesadas
- ✅ **Cache Buster** - JSONs sempre recarregam (query string timestamp)

## 🔒 Segurança

- ✅ **Credenciais em Secrets** - Nunca commitadas
- ✅ **Apenas Leitura** - Dashboard não escreve em Salesforce
- ✅ **HTTPS** - GitHub Pages usa HTTPS automático
- ✅ **No Backend** - Sem servidor próprio para atacar

## 🐛 Troubleshooting

### Dashboard mostra "Carregando..." infinitamente

**Causa:** Workflow ainda não foi executado (primeira vez)

**Solução:** Rodar workflow manualmente em Actions

### "Dados de Fallback" em vez de "LIVE"

**Causa:** Secrets não configurados corretamente

**Solução:** 
1. Verificar secrets em Settings → Secrets
2. Testar credenciais localmente: `python scripts/salesforce-sync.py`
3. Ver logs em Actions → Fetch Salesforce Data

### Gráficos não aparecem

**Causa:** Browsers antigos (IE11)

**Solução:** Usar navegador moderno (Chrome, Firefox, Safari, Edge)

### Dados muito antigos

**Causa:** Workflow desabilitado ou falhando

**Solução:** 
1. Checar Actions → Fetch Salesforce Data
2. Ver logs do último run
3. Verificar configuração de secrets

## 📚 Links Úteis

- [MCP Salesforce Docs](https://github.com/modelcontextprotocol/server-salesforce)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Chart.js Docs](https://www.chartjs.org/docs/latest/)

## 📝 Licença

MIT License - Veja LICENSE para detalhes.

---

**Última atualização:** 2026-08-16  
**Versão:** 1.0.0 - GitHub Pages Edition
