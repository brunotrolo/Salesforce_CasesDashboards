# Geração de Dashboards — Template-Based System

## Visão Geral

Dashboards são gerados automaticamente a partir de dados Salesforce via template HTML com tokens `{{...}}` substituídos por dados reais. Cada geração cria um arquivo novo com timestamp — **nunca sobrescreve versões anteriores**.

**Fluxo:**
```
Salesforce (SOQL) → JSON (dashboard.json) → Template HTML ({{TOKENS}}) → HTML Versionado
```

---

## Processo de Geração

### 1. Fetching de Dados (salesforce-sync.py)

O script `scripts/salesforce-sync.py` executa via GitHub Actions:

```bash
python scripts/salesforce-sync.py
```

**Queries SOQL** (agregadas, não raw records):
- Volume total (COUNT)
- Manual vs automático (GROUP BY CreatedAutomatically__c)
- Distribuição por Status (GROUP BY Status)
- Distribuição por Prioridade (GROUP BY Priority)
- Top 10 categorias (GROUP BY Category__c, ORDER BY total DESC)
- Casos encerrados (para SLA)
- Sem categoria (GROUP BY CreatedAutomatically__c)

**Output:** `docs/data/dashboard.json`

```json
{
  "lastSync": "2026-08-16T18:42:00.000Z",
  "isLive": false,
  "summary": {
    "total_cases": 68222,
    "manual_cases": 44063,
    "automatic_cases": 24159,
    "closed_cases": 41775,
    "no_category": 25505
  },
  "categories": [...],
  "status": [...],
  ...
}
```

### 2. Template Rendering (Python)

Função `render_dashboard_html(data)` substitui tokens:

```python
def render_dashboard_html(data, template_path="templates/dashboard-template.html"):
    # Carregar template
    with open(template_path, "r") as f:
        template = f.read()
    
    # Calcular métricas, formatar dados
    # ...
    
    # Substituir tokens
    html = template.replace("{{TOTAL_CASES}}", formatted_value)
    # ... mais substituições ...
    
    return html
```

**Tokens disponíveis:**

| Token | Fonte | Exemplo |
|-------|-------|---------|
| `{{ORG_NAME}}` | Config | "Banco XYZ" |
| `{{TITULO}}` | Período | "Casos da Semana" |
| `{{PERIODO}}` | Script | "09/08/2026 a 16/08/2026" |
| `{{TIMESTAMP}}` | `datetime.utcnow()` | "2026-08-16 18:42 UTC" |
| `{{TOTAL_CASES}}` | `summary.total_cases` | "68.222" (formatado) |
| `{{MANUAL_CASES}}` | `summary.manual_cases` | "44.063" |
| `{{AUTOMATIC_CASES}}` | `summary.automatic_cases` | "24.159" |
| `{{CLOSED_CASES}}` | `summary.closed_cases` | "41.775" |
| `{{NO_CATEGORY_COUNT}}` | `summary.no_category` | "25.505" |
| `{{STATUS_TABLE_ROWS}}` | Loop sobre `status[]` | `<tr><td>Closed</td><td>33,558</td></tr>...` |
| `{{CATEGORIES_TABLE_ROWS}}` | Loop sobre `categories[]` | Igual |
| `{{QUALITY_ALERT}}` | Cálculo de % | `<div class='alert-box'>...` |
| `{{DAILY_VOLUME_SVG}}` | Geração de SVG | Path/rect elements |
| `{{ORIGIN_DONUT_SVG}}` | Geração de SVG | Circle + stroke-dasharray |
| `{{SLA_HISTOGRAM_SVG}}` | Geração de SVG | Rect elements |
| `{{FILENAME}}` | Script | `briefing_executivo_semana_2026-08-16_184200.html` |

### 3. Salvar com Versão (Timestamp)

```python
def save_json_files(data):
    now = datetime.utcnow()
    
    # Salvar JSON
    with open("docs/data/dashboard.json", "w") as f:
        json.dump(data, f, indent=2)
    
    # Gerar HTML versionado
    html_content = render_dashboard_html(data)
    
    # Filename com timestamp: NUNCA SOBRESCREVE
    html_filename = f"briefing_executivo_semana_{now.strftime('%Y-%m-%d_%H%M%S')}.html"
    dashboards_dir = Path("Dashboards")
    dashboards_dir.mkdir(exist_ok=True)
    
    with open(dashboards_dir / html_filename, "w") as f:
        f.write(html_content)
```

**Resultado:** `Dashboards/briefing_executivo_semana_2026-08-16_184200.html`

---

## SVG Formulas (Geometria de Gráficos)

Todos os gráficos são **SVG desenhados à mão** (sem bibliotecas Chart.js). Use estas fórmulas para renderizar com precisão.

### Barras Empilhadas (Volume Diário)

**Canvas:** 980×260 px  
**Baseline:** `y = 220`  
**Altura máxima:** 165 px

**Fórmula de escala:**
```
scale = 165 / max(total_dia_1, total_dia_2, ..., total_dia_N)
```

**Para cada dia `i`:**

```
manual_height = manual_i × scale
auto_height = auto_i × scale
total_height = manual_height + auto_height

# Manual (teal)
<rect
  x="X_POS"
  y="220 - manual_height - auto_height"
  width="100"
  height="manual_height"
  fill="#0e6e6b"
/>

# Automático (amber)
<rect
  x="X_POS"
  y="220 - auto_height"
  width="100"
  height="auto_height"
  fill="#c98a2d"
/>
```

**Posições X:**
- Dia 1: x=60
- Dia 2: x=205
- Dia 3: x=350
- Dia 4: x=495
- Dia 5: x=640
- Dia 6: x=785
- (Espaçamento: 145px, largura rect: 100px)

**Labels:**
```
# Rótulo do dia (ex: "Seg")
<text x="110" y="238" font-family="Sora" font-size="12" text-anchor="middle">
  Seg
</text>

# Total do dia
<text x="110" y="254" font-family="Newsreader" font-size="13" text-anchor="middle" font-weight="600">
  12,450
</text>
```

---

### Donut (Manual × Automático)

**Canvas:** 320×240 px  
**Center:** (160, 115)  
**Raio:** 85 px  
**Stroke-width:** 30 px (para efeito de donut)  
**Circunferência:** `2 × π × 85 ≈ 534`

**Fórmula:**
```
pct_manual = manual_count / total_count
pct_auto = auto_count / total_count

len_manual = pct_manual × 534
len_auto = pct_auto × 534

# Círculo base invisível (para referência)
<circle cx="160" cy="115" r="85" fill="none" stroke="#e3e0d6" stroke-width="30" />

# Fatia manual (teal) — começa em -90deg (top)
<circle
  cx="160"
  cy="115"
  r="85"
  fill="none"
  stroke="#0e6e6b"
  stroke-width="30"
  stroke-dasharray="<len_manual> 534"
  stroke-dashoffset="0"
  transform="rotate(-90 160 115)"
/>

# Fatia automático (amber) — offset pela fatia anterior
<circle
  cx="160"
  cy="115"
  r="85"
  fill="none"
  stroke="#c98a2d"
  stroke-width="30"
  stroke-dasharray="<len_auto> 534"
  stroke-dashoffset="-<len_manual>"
  transform="rotate(-90 160 115)"
/>

# Label manual (teal)
<text x="130" y="100" font-family="Newsreader" font-size="16" font-weight="600" fill="#0e6e6b">
  64%
</text>
<text x="130" y="120" font-family="Sora" font-size="12" fill="#0e6e6b">
  Manual
</text>

# Label automático (amber)
<text x="170" y="140" font-family="Newsreader" font-size="16" font-weight="600" fill="#c98a2d">
  36%
</text>
<text x="160" y="160" font-family="Sora" font-size="12" fill="#c98a2d">
  Automático
</text>
```

---

### Histograma (SLA)

**Canvas:** 980×240 px  
**Baseline:** `y = 190`  
**Altura máxima:** 170 px

**Faixa padrão:**
- `<1h`, `1–4h`, `4–8h`, `8–24h`, `24h+`

**Fórmula de escala:**
```
scale = 170 / max(pct_faixa_1, pct_faixa_2, ...)
```

**Para cada faixa `j`:**

```
faixa_height = pct_j × scale
color = "#b3482f" if (pct_j >= 2 and faixa == "24h+") else "#0e6e6b"

<rect
  x="X_POS"
  y="190 - faixa_height"
  width="110"
  height="faixa_height"
  fill="<color>"
/>
```

**Posições X:**
- `<1h`: x=60
- `1–4h`: x=235
- `4–8h`: x=410
- `8–24h`: x=585
- `24h+`: x=760
- (Largura: 110px)

**Labels:**
```
# Rótulo da faixa
<text x="115" y="210" font-family="Sora" font-size="12" text-anchor="middle">
  &lt;1h
</text>

# Percentual
<text x="115" y="225" font-family="Newsreader" font-size="13" text-anchor="middle" font-weight="600">
  18%
</text>
```

**Regra de Cor:**
- Se `pct_faixa_24h+ >= 2%`: vermelho `#b3482f` (alerta, muitos atrasos)
- Senão: teal `#0e6e6b` (normal)

---

## Workflow Completo

### Local (Desenvolvimento)

```bash
# 1. Setup OAuth2
export SF_CLIENT_ID=your_id
export SF_CLIENT_SECRET=your_secret
export SF_REFRESH_TOKEN=your_token

# 2. Executar sync
python scripts/salesforce-sync.py

# 3. Resultado
# docs/data/dashboard.json (atualizado)
# Dashboards/briefing_executivo_semana_2026-08-16_184200.html (novo)
```

### GitHub Actions (CI/CD)

`.github/workflows/sync.yml` executa a cada 1 hora:

```yaml
name: Sync Salesforce Data
on:
  schedule:
    - cron: "0 * * * *"  # Hourly

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run sync
        env:
          SF_CLIENT_ID: ${{ secrets.SF_CLIENT_ID }}
          SF_CLIENT_SECRET: ${{ secrets.SF_CLIENT_SECRET }}
          SF_REFRESH_TOKEN: ${{ secrets.SF_REFRESH_TOKEN }}
        run: python scripts/salesforce-sync.py
      - name: Commit & push
        run: |
          git config user.name "Bot"
          git config user.email "bot@example.com"
          git add docs/data/ Dashboards/
          git commit -m "chore: sync Salesforce data" || true
          git push
```

---

## Versionamento e Histórico

### Filenames

```
briefing_executivo_<periodo>_YYYY-MM-DD_HHMMSS.html
```

**Componentes:**
- `briefing_executivo` — Prefixo fixo
- `<periodo>` — `semana`, `mes`, `hoje`, etc. (parametrizável)
- `YYYY-MM-DD` — Data de geração
- `HHMMSS` — Hora de geração (unique)

**Exemplos:**
- `briefing_executivo_semana_2026-08-16_184200.html`
- `briefing_executivo_semana_2026-08-16_203845.html` (próxima geração)

### Pasta de Armazenamento

```
Dashboards/
├── briefing_executivo_semana_2026-08-16_184200.html
├── briefing_executivo_semana_2026-08-16_203845.html
├── briefing_executivo_semana_2026-08-15_123456.html
└── ...
```

**Nunca sobrescreve.** Versões anteriores permanecem acessíveis em:
```
https://github.com/brunotrolo/Salesforce_CasesDashboards/tree/main/Dashboards
```

---

## Qualidade e Validação

### Pré-Commit (Impeccable)

Se instalado:
```bash
pre-commit run --all-files
```

Valida:
- HTML válido
- Nenhuma fonte overused
- Sem em-dashes excessivos

### Post-Generation (Opcional)

```bash
node .claude/skills/impeccable/scripts/detect.mjs --json "Dashboards/briefing_executivo_semana_2026-08-16_184200.html"
```

Corrige:
- Fonte overused
- Em-dashes excessivos
- Padrões de acessibilidade

---

## Troubleshooting

### Template não encontrado

```
❌ Template não encontrado: templates/dashboard-template.html
```

**Fix:** Certifique-se que o arquivo existe:
```bash
ls -la templates/dashboard-template.html
```

Se não: recupere da referência brunotrolo-bank.

### Dados incompletos

```
❌ Erro ao conectar Salesforce: ...
```

Script usa `generate_fallback_data()` automaticamente. Dashboard será gerado com dados de fallback (flag `isLive: false`).

### Campos não agregáveis

```
MALFORMED_QUERY: SELECT CategoryUnified__c, COUNT(Id) ...
```

**Causa:** Campos "unified" (string) não são agrupáveis.  
**Fix:** Use campos legados:
- `CategoryUnified__c` → `Category__c`
- `SubcategoryUnified__c` → `SubCategory__c`
- `SubcategoryDetailUnified__c` → `SubCategoryDetail__c`

---

## Next Steps

- [ ] Implementar SVG rendering para barras empilhadas
- [ ] Implementar SVG rendering para donut
- [ ] Implementar SVG rendering para histograma SLA
- [ ] Adicionar SLA calculation (CreatedDate – ClosedDate)
- [ ] Implementar cálculo de mediana/p90
- [ ] Configurar GitHub Actions para sync automático
- [ ] Testar com dados reais Salesforce

