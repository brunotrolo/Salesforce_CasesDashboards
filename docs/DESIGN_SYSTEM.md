# Design System — Briefing Executivo de Casos

## Visão

**Briefing executivo editorial.** O dashboard lê como a pauta da reunião de segunda-feira: primeiro o número que a gestão precisa saber, depois a história de onde ele veio. Recusa a grade genérica de cards — cada seção é uma cena narrativa com um gráfico como protagonista. Modo: Operate.

**Implementação:** Template HTML standalone (CSS embutido, sem dependências), com tokens `{{...}}` substituídos por dados Salesforce via script Python.

---

## Paleta de Cores

Todas as cores foram refinadas a partir da referência brunotrolo-bank para credibilidade financeira.

| Categoria | Nome | Hex | Uso |
|-----------|------|-----|-----|
| **Papel** | Warm Paper | `#f4f2ec` | Fundo da página (credibilidade + warmth) |
| **Superfície** | White | `#ffffff` | Cards, frames de dados |
| **Tinta** | Main | `#20242b` | Texto principal (não preto puro, azulado) |
| **Tinta Suave** | Secondary | `#4c525c` | Texto secundário, leads |
| **Tinta Fraca** | Tertiary | `#7a8090` | Labels, subtítulos |
| **Linhas** | Light | `#e3e0d6` | Hairline borders |
| **Linhas** | Strong | `#c9c5b8` | Borders mais visíveis |
| **Acento** | Teal | `#0e6e6b` | Casos manuais (confiança) |
| **Acento** | Teal Strong | `#0a524f` | Hover/ativa de teal |
| **Acento** | Teal Light | `#e7f0ee` | Background/notas teal |
| **Criação** | Amber | `#c98a2d` | Casos automáticos (energia) |
| **Criação** | Amber BG | `#f6ecd8` | Background para chips automáticos |
| **Criação** | Amber Text | `#8a5c10` | Texto em fundo amber |
| **Alerta** | Burnt Red | `#b3482f` | Sem categoria, alertas críticos |
| **Alerta** | Burnt Red BG | `#f7ebe6` | Background de alertas |

### Regras de Contraste

- **Tinta sobre Papel:** ≥ 4.5:1 (WCAG AA)
- **Textos sobre fundos coloridos:** Tintados da própria cor (ex.: texto teal sobre fundo teal light)
- **Sem preto puro:** `#20242b` (azulado) passa mais confiança que `#000`

---

## Tipografia

### Fontes

- **Display/Headings/Grandes Números:** `Newsreader` (serifa editorial)
  - Pesos: 400, 600
  - Sem itálico em display
  - Imprime credibilidade executiva

- **Corpo, Dados, Labels:** `Sora` (grotesca geométrica)
  - Pesos: 400, 700
  - Legível em qualquer tamanho

### Escala

| Elemento | Tamanho | Família | Notas |
|----------|---------|---------|-------|
| **H1 (Título da página)** | `clamp(30px, 5vw, 44px)` | Newsreader 400 | Responsivo, máx 44px |
| **H2 (Seção/Cena)** | `clamp(24px, 4vw, 32px)` | Newsreader 400 | Subtítulo de narrativa |
| **Lead (Introdução de cena)** | 15px | Sora 400 | Máx 62 caracteres |
| **Body/Tabelas** | 15–15.5px | Sora 400 | Confortável para reunião |
| **Tabela (dados)** | 13.5px | Sora 400 | Tabulares com `font-variant-numeric: tabular-nums` |
| **Labels (caps)** | 12–13px | Sora 700, uppercase | `letter-spacing: 0.12em` |
| **KPI (valor grande)** | 28px | Newsreader 600 | Impacto visual no status ruler |

---

## Componentes

### 1. Masthead Editorial

**Elementos:**
- Org name (caps pequenas, tracking 0.12em)
- Título serifado (Newsreader 30–44px)
- Data badge "DADOS SOQL SOMENTE LEITURA" (alerta visual)
- Período analisado
- Timestamp de geração

**Design:**
- Sem underline, apenas border-bottom hairline
- Espaçamento: 24px abaixo

### 2. Régua de Status (Status Ruler)

**Estrutura:**
- 5 KPIs em linha horizontal
- Sem cards: apenas separadores hairline vertical/horizontal
- Quebra para 2 colunas em `@media (max-width: 900px)`
- Quebra para 1 coluna em `@media (max-width: 560px)`

**KPI em ordem fixa:**
1. Casos criados (total)
2. Manuais (humano)
3. Automáticos (RPA)
4. Encerrados
5. Sem categoria (sempre com classe `.alert`, fundo vermelho)

**Padding:** 24–26px  
**Border radius:** 14px (frame inteiro)

### 3. Cena (Narrative Scene)

**Estrutura:**
```html
<div class="scene">
  <h2 class="scene-title">Título Serifado</h2>
  <p class="scene-lead">Introdução narrativa (máx 62ch)</p>
  <div class="frame">
    <!-- Gráfico ou tabela -->
  </div>
</div>
```

**Design:**
- Sem eyebrow/kicker acima do título
- Lead em texto soft (#4c525c)
- Frame branco com border hairline + radius 14px
- Spacing: 48px entre cenas

### 4. Quadro (Frame/Surface)

- Background: `#ffffff`
- Border: `1px solid #e3e0d6` (hairline)
- Border radius: 14px
- Padding: `clamp(24px, 4vw, 26px)`
- Sem sombra hard

### 5. Gráficos SVG

**Desenhados à mão (não bibliotecas como Chart.js):**

#### a) Barras Empilhadas (Volume Diário)

- Canvas: 980×260px
- Baseline: `y=220`
- Altura máxima: 165px
- `scale = 165 / max(total_dia)`
- Posições x: 60, 205, 350, 495, 640, 785 (espaçamento 145px, largura 100px)
- Manual (teal): Rect em `y = 220 − h_manual − h_auto`, `height = h_manual`
- Automático (amber): Rect em `y = 220 − h_auto`, `height = h_auto`
- Rótulo do dia: Sora 12px em `y=238`
- Total do dia: Newsreader 13px em `y=254`

#### b) Donut (Manual × Automático)

- Raio: 85px
- Circunferência: `2 × π × 85 ≈ 534`
- `len_fatia = pct × 5.34`
- Fatia manual (teal): `stroke-dasharray="<len> 534"`, `rotate(-90 160 115)`
- Fatia automático (amber): `stroke-dasharray="<len> 534"`, `stroke-dashoffset="-<len_manual>"`
- Center: `(160, 115)`

#### c) Histograma (SLA)

- Canvas: 980×240px
- Baseline: `y=190`
- Altura máxima: 170px
- `scale = 170 / max(pct_faixa)`
- Faixas: `<1h`, `1–4h`, `4–8h`, `8–24h`, `24h+`
- Posições x: 60, 235, 410, 585, 760 (largura 110px)
- `24h+` em **vermelho `#b3482f`** quando ≥2%; senão teal

### 6. Tabelas

**Estilo:**
- Collapse borders
- Header: background `#f4f2ec` (page bg), caps pequenas, uppercase, tracking 0.12em
- Body: Sora 400, 13.5px
- Números: `font-variant-numeric: tabular-nums`
- Borders: hairline `#e3e0d6` entre linhas
- Sem linhas verticais internas (apenas separador de coluna visual)

**Responsivo:**
- ≤720px: font-size reduz, padding reduz
- Tabelas longas: `overflow-x: auto` em container

### 7. Chips (Origem)

**Manual:**
- Background: `#e7f0ee` (teal light)
- Color: `#0a524f` (teal strong)
- Font: Sora 600, 12px
- Padding: 4px 8px
- Border radius: 12px

**Automático:**
- Background: `#f6ecd8` (amber light)
- Color: `#8a5c10` (amber text)
- Mesmo padding/border-radius

### 8. Boxes (Alertas e Notas)

**Alert Box (Sem Categoria):**
- Background: `#f7ebe6` (burnt red light)
- Border: 1px `#b3482f`
- Color text: `#b3482f`
- Padding: 16px
- Border radius: 8px

**Note Box (Insights):**
- Background: `#e7f0ee` (teal light)
- Color text: `#0a524f`
- Padding: 12px 16px
- Sem border

---

## Regras de Design (Anti "Vibe Coding")

### ✅ Permitido

- Cores em **regiões inteiras**, não como acentos dispersos
- SVG desenhados à mão (geometria controlada)
- Separadores hairline (1px)
- Responsive via `clamp()` e media queries em pontos fixos
- Tema de navegador customizado (`::selection`, scrollbar, focus)

### ❌ Proibido

- Gradientes (texto ou fundo)
- Sombras hard/offset
- Cards aninhados
- Kicker/eyebrow acima de título
- Em-dashes no corpo (usar `,`, `·`, `:`, `()`)
- Ícones de Unicode/emoji como sistema de ícones
- Preto puro `#000` (usar `#20242b`)
- Fontes overused (Inter, Roboto, Space Grotesk, Plus Jakarta Sans, Geist)

---

## Responsividade

### Breakpoints

| Breakpoint | Comportamento |
|-----------|--------------|
| **≥900px** | Régua em 5 colunas (full) |
| **≤900px** | Régua em 2 colunas |
| **≤560px** | Régua em 1 coluna |
| **≤860px** | Duplas (2-coluna layouts) viram coluna única |
| **≤720px** | Tabelas com scroll horizontal |

### Padding

Dinâmico: `clamp(16px, 4vw, 48px)`  
Garante margem adequada em mobile sem excesso em desktop.

---

## Impressão

- Background: branco (não `#f4f2ec`)
- Sem sombras
- Seções evitam quebra de página
- Cores preservadas (CMYK para printer profiles)

---

## Contrato de Direção

```html
<!-- Comentário no <body> -->
<!-- DIRECTION CONTRACT · seed 007ba89f -->
```

Presença obrigatória para validação de versão. Não remover.

---

## Checklist de Qualidade

- [ ] Nenhuma cor preto puro (`#000`); usar `#20242b`
- [ ] Tipografia: Newsreader (display), Sora (body)
- [ ] Tabelas com `font-variant-numeric: tabular-nums`
- [ ] Status ruler em 5 KPIs, ordem fixa
- [ ] Sem gradientes, sem sombras hard
- [ ] SVG em geometria calculada (não imagens)
- [ ] Responsive: 900px, 860px, 720px, 560px
- [ ] Print: background white, sem sombras
- [ ] Contraste tinta/papel ≥4.5:1
- [ ] Cores em regiões, não acentos dispersos

---

## Referências

- **Especificação Completa:** [brunotrolo-bank/SalesforceOdin_Dashboard](https://github.com/brunotrolo-bank/salesforceodin_dashboard)
- **Template Oficial:** `templates/dashboard-template.html`
- **Dados:** `docs/data/dashboard.json` (gerado por `scripts/salesforce-sync.py`)
- **Gerador:** `scripts/salesforce-sync.py` → `render_dashboard_html()`

