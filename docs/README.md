# 📊 Salesforce Cases Dashboard - GitHub Pages

Dashboard **100% estático** hospedado em **GitHub Pages**, com dados **reais** do Salesforce via **OAuth2 REST API**.

Apresenta análise gerencial de Casos (Case) do Salesforce com ênfase em **volume**, **status**, **categorias**, **qualidade de dados** e **manual vs automático**.

## 🎯 Como Funciona

```
GitHub Actions (a cada 1 hora)
    ↓
Autentica no Salesforce via OAuth2 (refresh token)
    ↓
Executa 8 queries SOQL agregadas (GROUP BY/COUNT)
    ↓
Extrai: volume, status, prioridade, categorias, 
        criação manual/automática, qualidade, SLA
    ↓
Gera dashboard.json em docs/data/
    ↓
Faz commit automático
    ↓
GitHub Pages atualiza o site
    ↓
Dashboard carrega dashboard.json via JavaScript
    ↓
Renderiza KPIs, donuts, bar charts em tempo real
```

## 🚀 Acessar o Dashboard

**Dashboard Live:** https://brunotrolo.github.io/Salesforce_CasesDashboards

### Funcionalidades

- ✅ **KPIs em Cards** - Total de cases, manual %, automático %, fechados %, qualidade
- ✅ **Top Categorias** - Gráfico de barras horizontal (top 10)
- ✅ **Distribuição por Status** - Donut chart interativo com legenda
- ✅ **Manual vs Automático** - Donut chart com percentuais
- ✅ **Distribuição por Prioridade** - Gráfico de barras
- ✅ **Indicador de Qualidade** - Percentual de casos sem categoria (por tipo de criação)
- ✅ **Métricas de SLA** - Mediana, média, tamanho da amostra
- ✅ **Auto-Refresh** - A cada 5 minutos
- ✅ **Status de Sincronização** - 🟢 Dados ao Vivo ou 📦 Dados de Fallback
- ✅ **Timestamp** - Mostra quando foi última sincronização
- ✅ **Dark Mode** - Suporte automático

## 🔧 Configuração

### 1. Ativar GitHub Pages

1. Vá para **Settings → Pages**
2. **Source:** Deploy from a branch
3. **Branch:** main
4. **Folder:** /docs
5. **Save**

Dashboard estará disponível em: `https://seu-usuario.github.io/Salesforce_CasesDashboards`

### 2. Configurar GitHub Secrets (para dados reais)

Para conectar ao Salesforce real, configure os secrets em **Settings → Secrets and variables → Actions**:

- `SF_CLIENT_ID` - OAuth2 Client ID
- `SF_CLIENT_SECRET` - OAuth2 Client Secret
- `SF_REFRESH_TOKEN` - Refresh Token

**Obtendo as credenciais:**
1. No Salesforce, criar uma **Connected App** (Setup → Apps → App Manager)
2. Gerar **Client ID** e **Client Secret**
3. Usar Salesforce OAuth2 flow para obter **Refresh Token**
4. Adicionar em GitHub Secrets

**Teste local:**
```bash
export SF_CLIENT_ID="seu_client_id"
export SF_CLIENT_SECRET="seu_client_secret"
export SF_REFRESH_TOKEN="seu_refresh_token"

python scripts/salesforce-sync.py
```

### 3. (Opcional) Ajustar Cronograma

Editar `.github/workflows/fetch-salesforce-data.yml`:

```yaml
schedule:
  - cron: '0 * * * *'  # ← A cada 1 hora (padrão)
  # - cron: '0 */6 * * *'  # A cada 6 horas
  # - cron: '0 9 * * *'  # Diariamente às 9h
```

## 📁 Estrutura de Arquivos

```
docs/
├── index.html                  # Dashboard (página principal)
├── data/
│   ├── dashboard.json          # ⭐ Gerado por GitHub Actions
│   └── metadata.json           # Compatibilidade (deprecated)
└── README.md                   # Este arquivo
```

## 🤖 Script de Sincronização

**Arquivo:** `scripts/salesforce-sync.py`

Executa 8 queries SOQL agregadas para extrair dados do dia:

### Queries Executadas

1. **Volume Total** - COUNT de todos os cases do dia
2. **Manual vs Automático** - GROUP BY CreatedAutomatically__c
3. **Status** - GROUP BY Status
4. **Prioridade** - GROUP BY Priority
5. **Top 10 Categorias** - GROUP BY Category__c (campos legados, agrupáveis)
6. **Casos Fechados** - Para cálculo de SLA
7. **Qualidade de Dados** - COUNT de casos SEM categoria (por tipo de criação)
8. **SLA Bruto** - Últimos 2000 casos fechados (para pós-processamento)

### Estrutura de Saída

```json
{
  "lastSync": "2026-08-16T18:42:00.000Z",
  "isLive": true,
  "summary": {
    "total_cases": 68222,
    "manual_cases": 44063,
    "automatic_cases": 24159,
    "closed_cases": 41775,
    "no_category": 25505
  },
  "categories": [
    {"label": "Fatura", "value": 7339},
    {"label": "Atendimento", "value": 5623},
    ...
  ],
  "status": [
    {"label": "Closed", "value": 33558},
    ...
  ],
  "priority": [
    {"label": "Normal", "value": 52209},
    ...
  ],
  "creationType": [
    {"label": "Manual", "value": 44063},
    {"label": "Automático", "value": 24159}
  ],
  "quality": [
    {"label": "Manual", "value": 25338},
    {"label": "Automático", "value": 167}
  ],
  "sla": {
    "median_total": 0,
    "mean_manual": 10.6,
    "mean_automatic": 0,
    "sample_size": 2000
  }
}
```

## 🔄 Workflow GitHub Actions

**Arquivo:** `.github/workflows/fetch-salesforce-data.yml`

Executa automaticamente segundo cronograma:
1. ✅ Setup Python 3.11
2. ✅ Instala dependências (requests)
3. ✅ Executa `scripts/salesforce-sync.py`
4. ✅ Faz commit automático em `docs/data/dashboard.json`
5. ✅ Push para main
6. ✅ GitHub Pages atualiza automaticamente

**Rodar manualmente:**
1. Vá para **Actions**
2. Selecione **"Fetch Salesforce Data"**
3. Clique **"Run workflow"**

## 📊 Dados de Fallback

Se Salesforce não estiver disponível ou secrets não configurados, o script automaticamente usa **dados de fallback**:
- Dashboard continua funcionando
- Indicador muda para `📦 Dados de Fallback`
- Timestamp mostra última sincronização bem-sucedida

Isso garante **disponibilidade** mesmo com problemas temporários no Salesforce.

## 🎨 Design System

- **Paleta:** 8 cores principais + good/warning/critical
- **Responsivo** - Desktop, tablet, mobile
- **Dark Mode** - Detecta automaticamente via `prefers-color-scheme`
- **Performance** - Zero dependências externas
- **Acessibilidade** - WCAG 2.1 AA

### Componentes

- **KPI Cards** - Números destacados em cards
- **Bar Charts** - Gráficos de barras horizontais
- **Donut Charts** - Conic-gradient donuts com legendas
- **Quality Insight** - Card destacando gap de categorização manual vs automática

## 🔒 Segurança

- ✅ **Credenciais em GitHub Secrets** - Nunca expostas no código
- ✅ **Apenas Leitura** - Dashboard não escreve em Salesforce
- ✅ **HTTPS** - GitHub Pages usa HTTPS automático
- ✅ **No Backend** - Sem servidor próprio para atacar
- ✅ **OAuth2** - Autenticação segura via refresh token

## 🔑 Conceitos-Chave

### Campos de Categoria

**Legacy (Agrupáveis):**
- `Category__c` (picklist) ✅ Usar para agregações GROUP BY
- `SubCategory__c` (picklist)
- `SubCategoryDetail__c` (picklist)

**Unified (Não agrupáveis):**
- `CategoryUnified__c` (string) ❌ NÃO usar em GROUP BY
- `SubcategoryUnified__c` (string)
- `SubcategoryDetailUnified__c` (string)

**Regra:** Agregações sempre com campos legados. Campos unificados apenas para detalhe de um caso específico.

### Dimensão Central: CreatedAutomatically__c

Todas as análises quebram por:
- **false** = Manual (criado por atendente)
- **true** = Automático (criado por RPA/integração)

Achado crítico: **Gap de qualidade é 57,5% em casos manuais vs 0,7% em automáticos**.

## 🐛 Troubleshooting

### Dashboard mostra "Carregando..." infinitamente

**Causa:** Workflow ainda não executado (primeira vez)

**Solução:** Rodar workflow manualmente em Actions → Fetch Salesforce Data → Run workflow

### Status mostra "Dados de Fallback"

**Causa:** Secrets não configurados ou credenciais inválidas

**Solução:**
1. Verificar secrets em Settings → Secrets and variables
2. Testar localmente: `python scripts/salesforce-sync.py`
3. Ver logs em Actions → Fetch Salesforce Data

### Gráficos não aparecem

**Causa:** Browser antigo ou JavaScript desabilitado

**Solução:** Usar Chrome, Firefox, Safari ou Edge moderno (2020+)

### Erro "MALFORMED_QUERY"

**Causa:** Tentativa de GROUP BY em campos `*Unified__c`

**Solução:** Script já corrigido para usar campos legados. Se problema persistir, checar se Salesforce schema mudou.

### Dados muito antigos

**Causa:** Workflow falhando silenciosamente

**Solução:**
1. Ver Actions → Fetch Salesforce Data
2. Clicar em último run e ver logs detalhados
3. Verificar se secrets expiram

## 📈 Métricas de Referência

Use esses números como sanity check para validar dados reais:

```
Exemplo (Dia: 2026-08-14)
─────────────────────────
Volume total:            68.173 casos
├─ Manual:               44.029 (64,6%)
└─ Automático:           24.145 (35,4%)

Sem categoria:
├─ Manual:               25.312 (57,5%)
└─ Automático:              167 (0,7%)

SLA:
├─ Mediana geral:        ~0 min
├─ Média manual:         ~10,6 min
└─ Cauda longa:          categoria "Fatura"
```

## 📚 Links Úteis

- [Salesforce OAuth2 Docs](https://developer.salesforce.com/docs/atlas.en-us.oauth_tokens_flows.meta/oauth_tokens_flows/)
- [GitHub Pages Docs](https://docs.github.com/en/pages)
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SOQL Query Reference](https://developer.salesforce.com/docs/atlas.en-us.soql_sosl.meta/soql_sosl/)

## 📝 Licença

MIT License

---

**Última atualização:** 2026-08-16  
**Versão:** 2.0.0 - OAuth2 REST API Edition
