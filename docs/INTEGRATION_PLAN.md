# Plano de Integração: Referência brunotrolo-bank

## Resumo Executivo

Análise da referência superior em brunotrolo-bank/SalesforceOdin_Dashboard identificou **4 pilares de maturidade** que modernizam a implementação atual:

1. **Template-Based Generation** — Template HTML com `{{TOKENS}}` em lugar de string replacement direto
2. **Versionamento com Timestamp** — Cada geração é um arquivo novo, nunca sobrescreve
3. **Design System Formal** — Paleta, tipografia e componentes documentados explicitamente
4. **SVG Formulas** — Cálculos de geometria para gráficos reproduzíveis e precisos

---

## O Que Foi Feito (Implementação Imediata)

### ✅ P0: Template + Design System

| Item | Status | Arquivo |
|------|--------|---------|
| Template HTML com {{TOKENS}} | ✅ Criado | `templates/dashboard-template.html` |
| Design System (paleta + tipografia) | ✅ Documentado | `docs/DESIGN_SYSTEM.md` |
| Python script com render_dashboard_html() | ✅ Atualizado | `scripts/salesforce-sync.py` |
| Versionamento com timestamp | ✅ Implementado | `render_dashboard_html()` + `save_json_files()` |
| SVG Formulas (barras, donut, histograma) | ✅ Documentado | `docs/DASHBOARD_GENERATION.md` |

### Comparação Antes/Depois

#### Antes (String Replacement)
```python
html = open("template.html").read()
html = html.replace("{{TOTAL}}", str(total_cases))
# Difícil de manter, sem versionamento
```

#### Depois (Template-Based)
```python
html = render_dashboard_html(data)  # Função estruturada
# Versionado: briefing_executivo_semana_2026-08-16_184200.html
# Nunca sobrescreve
```

---

## Arquitetura Resultante

```
Salesforce (SOQL)
    ↓
fetch_salesforce_data() [agregado, GROUP BY]
    ↓
generate_fallback_data() [fallback automático]
    ↓
Dashboard JSON (docs/data/dashboard.json)
    ↓
render_dashboard_html(data) ← Template + {{TOKENS}}
    ↓
Dashboards/briefing_executivo_semana_2026-08-16_184200.html
    ↓
GitHub Pages (versões históricas acessíveis)
```

---

## Próximos Passos (P1–P2)

### P1: SVG Rendering (Curto Prazo)

**Objetivo:** Implementar funções para gerar SVG dos dados (atualmente placeholders).

**Funções a criar:**

```python
def render_daily_volume_svg(daily_data) -> str:
    """Gera SVG de barras empilhadas (manual vs automático por dia)"""
    # Implementar usando fórmulas de dashboard-design.md
    return "<svg>...</svg>"

def render_origin_donut_svg(manual, automatic) -> str:
    """Gera SVG donut (manual × automático)"""
    # Implementar usando fórmulas do donut

def render_sla_histogram_svg(sla_buckets) -> str:
    """Gera SVG histograma (faixas de SLA)"""
    # Implementar usando fórmulas de histograma
```

**Tempo estimado:** 1–2 horas por função

### P2: SLA Calculation (Curto Prazo)

**Objetivo:** Calcular média/mediana/p90 de tempo até fechamento.

**Implementação:**

```python
async def fetch_sla_sample(access_token, instance_url, limit=2000):
    """Busca amostra de casos encerrados com CreatedDate e ClosedDate"""
    query = """
        SELECT Id, CreatedDate, ClosedDate, Category__c, CreatedAutomatically__c
        FROM Case
        WHERE CreatedDate = TODAY
          AND Status IN ('Closed', 'Fechado Com Sucesso', 'Protocolo Fechado')
          AND ClosedDate != null
        LIMIT 2000
    """
    # Execute e calcule durações em Python
    # Retorne: mean, median, p90 por origem (manual vs auto)
```

### P3: Automação Semanal (Médio Prazo)

**Objetivo:** Mudar de sync horário para semanal (segunda-feira).

**Mudança em `.github/workflows/sync.yml`:**

```yaml
schedule:
  - cron: "0 8 * * 1"  # Segunda-feira, 8am UTC
```

---

## Arquivos Criados/Modificados

```
Salesforce_CasesDashboards/
│
├── templates/
│   └── dashboard-template.html ★ [NOVO]
│       └── Template HTML com {{TOKENS}}
│
├── docs/
│   ├── DESIGN_SYSTEM.md ★ [NOVO]
│   │   └── Paleta, tipografia, componentes, regras
│   │
│   ├── DASHBOARD_GENERATION.md ★ [NOVO]
│   │   └── SVG formulas, workflow, troubleshooting
│   │
│   ├── INTEGRATION_PLAN.md ★ [NOVO]
│   │   └── Este arquivo
│   │
│   └── index.html [compatível com nova geração]
│
└── scripts/
    └── salesforce-sync.py ★ [ATUALIZADO]
        ├── + render_dashboard_html()
        ├── + Versionamento com timestamp
        └── + Suporte a {{TOKENS}}
```

---

## Paleta de Cores (Integrada)

Migração da paleta anterior para brunotrolo-bank:

| Uso | Antes | Depois |
|-----|-------|--------|
| Fundo | `#f9f9f7` | `#f4f2ec` (warm paper) |
| Texto | `#0b0b0b` | `#20242b` (não preto puro) |
| Manual | `#2a78d6` (azul) | `#0e6e6b` (teal, confiança) |
| Automático | `#eb6834` (laranja) | `#c98a2d` (âmbar, energia) |
| Alerta | `#d03b3b` (vermelho) | `#b3482f` (burnt red) |

**Benefício:** Paleta financeira mais credível + consistência visual com referência.

---

## Tipografia

| Elemento | Antes | Depois |
|----------|-------|--------|
| Display | System sans | Newsreader serif (editorial) |
| Body | System sans | Sora (geométrica) |
| Escala H1 | `22px` fixo | `clamp(30px, 5vw, 44px)` responsivo |
| Labels | Não uppercase | Uppercase + `letter-spacing: 0.12em` |

---

## Benefícios Imediatos

1. **Manutenibilidade:** Template centralizado, fácil update de design
2. **Versionamento:** Histórico completo de dashboards (nunca perde dados)
3. **Documentação:** Design system formal facilita onboarding
4. **Precisão:** SVG formulas garantem reprodutibilidade
5. **Credibilidade:** Paleta financeira + editorial aesthetic

---

## Integração com CLAUDE.md

Conforme [CLAUDE.md](CLAUDE.md), skills são ativadas automaticamente:

- **Impeccable:** Valida HTML, fontes, em-dashes
- **Agent Skills:** Sugere testes para `render_dashboard_html()`
- **UI/UX:** Audit de acessibilidade (WCAG) do HTML

```bash
# Pós-implementação de SVG:
claude /impeccable lint --files templates/
claude /agent-skills suggest-tests --service dashboard-generation
claude /ui-ux audit-accessibility frontends/dashboard-fe
```

---

## Testing

### Unit Tests (Backend)

```python
def test_render_dashboard_html_with_fallback_data():
    data = generate_fallback_data()
    html = render_dashboard_html(data)
    assert "{{" not in html  # Todos tokens substituídos
    assert "68,222" in html  # Número formatado
    assert "briefing_executivo_semana" in html

def test_daily_volume_svg_calculation():
    daily = [{"manual": 1000, "auto": 500}, ...]
    svg = render_daily_volume_svg(daily)
    assert "<svg" in svg
    assert "scale =" in svg or "165 /" in svg  # Verificar fórmula
```

### E2E Tests (CI)

```bash
# Após deploy em GitHub Pages:
curl -s https://...Dashboards/briefing_executivo_semana_*.html | grep "Casos da Semana"
# Status: 200 OK
# Content-Type: text/html
# Pode estar vazio em inicial, isso é ok
```

---

## Roadmap

| Fase | O Que | Tempo | Status |
|------|-------|-------|--------|
| **P0** | Template + Design System | ✅ Concluído | DONE |
| **P1** | SVG Rendering | ~3h | TODO |
| **P2** | SLA Calculation | ~2h | TODO |
| **P3** | GitHub Actions automático | ~1h | TODO |
| **P4** | Dashboard Analytics (quem leu, quando) | ~4h | TODO |
| **P5** | Mobile app (React Native) | ~20h | FUTURE |

---

## Referências

- **Análise Detalhada:** https://github.com/brunotrolo-bank/salesforceodin_dashboard
  - DESIGN.md — Paleta, tipografia, componentes
  - PRODUCT.md — Personas, positioning
  - SKILL.md — Guardrails, workflow
  - references/dashboard-design.md — SVG formulas

- **Documentação Local:**
  - `docs/DESIGN_SYSTEM.md` — Paleta + regras integradas
  - `docs/DASHBOARD_GENERATION.md` — SVG formulas + workflow
  - `templates/dashboard-template.html` — Template oficial

---

## Checklist de Deploy

- [ ] Templates renderiza sem erros com fallback data
- [ ] JSON (dashboard.json) é gerado corretamente
- [ ] Arquivo versionado (timestamp) criado em `Dashboards/`
- [ ] HTML renderizado é válido (não há `{{}}` não substituídos)
- [ ] Design system colors aplicadas corretamente
- [ ] Responsividade testada (900px, 720px, 560px)
- [ ] Print testado (background branco, sem sombras)
- [ ] Impeccable lint passou
- [ ] Deploy em GitHub Pages acessível

---

## Contato

**Perguntas sobre integração?** Consulte:
1. `docs/DESIGN_SYSTEM.md` — design e componentes
2. `docs/DASHBOARD_GENERATION.md` — SVG, workflow, troubleshooting
3. `templates/dashboard-template.html` — estrutura de tokens
4. Referência: https://github.com/brunotrolo-bank/salesforceodin_dashboard

