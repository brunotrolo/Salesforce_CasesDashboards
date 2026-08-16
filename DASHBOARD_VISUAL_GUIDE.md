# Dashboard Visual Guide

**Status:** Estrutura completa implementada | Aguardando integração real com API  
**Tecnologia:** React 18 + TypeScript + Tailwind CSS  
**Localização:** `/frontends/dashboard-fe/`

---

## 📱 ESTRUTURA GERAL

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DASHBOARD SALESFORCE                         │
│                    Gerencie e execute seus relatórios               │
│                                                     [Novo Relatório] │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Filtros: [Todos] [✓Ativos] [Rascunhos] [Agendados]              │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ Report 1     │  │ Report 2     │  │ Report 3     │             │
│  │              │  │              │  │              │             │
│  │ Status: Ativo│  │ Status:      │  │ Status: Ativo│             │
│  │              │  │ Rascunho     │  │              │             │
│  │ Objeto: Case │  │              │  │ Objeto: Case │             │
│  │ Campos: 5    │  │ Objeto:      │  │ Campos: 8    │             │
│  │ Tipo: Matrix │  │ Opportunity  │  │ Tipo: Summary│             │
│  │ Criado: hoje │  │ Campos: 3    │  │ Criado: 2d   │             │
│  │              │  │ Tipo: Tabular│  │              │             │
│  │ Filtros: 2   │  │ Criado: 1sem │  │ Filtros: 1   │             │
│  │              │  │ Filtros: 0   │  │              │             │
│  │ [Executar]   │  │ [Executar]   │  │ [Executar]   │             │
│  │ [Editar]     │  │ [Editar]     │  │ [Editar]     │             │
│  │ [Deletar]    │  │ [Deletar]    │  │ [Deletar]    │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                     │
│  [Carregar mais]                                                   │
│                                                                     │
│  Exibindo 3 de 12 relatórios                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 COMPONENTES E DESIGN

### Header
```
┌─────────────────────────────────────────────────────────────────────┐
│ Relatórios Salesforce              [Novo Relatório]              │
│ Gerencie e execute seus relatórios                                │
└─────────────────────────────────────────────────────────────────────┘
```

**Componente:** `DashboardPage.tsx`
- Título principal: "Relatórios Salesforce"
- Subtítulo: "Gerencie e execute seus relatórios"
- Botão de ação: "Novo Relatório" (navega para `/builder`)
- Estilo: Fundo branco, borda inferior cinza

---

### Filter Bar
```
┌─────────────────────────────────────────────────────────────────────┐
│ Filtrar por status:                                                │
│                                                                     │
│ [Todos]  [✓Ativos]  [Rascunhos]  [Agendados]                     │
│                                                                     │
│ Mostrar apenas relatórios com status selecionado                  │
│ Click remove/reaplica filtro e recarrega lista                    │
└─────────────────────────────────────────────────────────────────────┘
```

**Componente:** `ReportsList.tsx` (linhas 63-88)
- Botões para: `Todos`, `Ativos`, `Rascunhos`, `Agendados`
- Estados visuais:
  - Selecionado: `bg-blue-600 text-white`
  - Não selecionado: `bg-gray-200 text-gray-900`
  - Hover: Darker shade

---

### Report Card (Grid 3 Colunas)
```
┌──────────────────────────────────────────────────────────┐
│ ┌──────────────────────────────────────────────────────┐ │
│ │                                    [Status Badge]    │ │
│ │ Relatório de Casos Abertos                          │ │
│ │ Monitora casos em aberto por prioridade              │ │
│ │                                                      │ │
│ │ Objeto: Case           │ Campos: 5                  │ │
│ │ Tipo: Summary          │ Criado: 2 horas atrás      │ │
│ │                                                      │ │
│ │ Filtros: 2                                           │ │
│ │                                                      │ │
│ │ [Executar] [Editar] [Deletar]                       │ │
│ │                                                      │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

**Componente:** `ReportCard.tsx`

**Estrutura:**
1. **Header com Status**
   - Nome do relatório
   - Descrição (opcional)
   - Badge de status com cor
     - DRAFT: Cinza
     - ACTIVE: Verde
     - SCHEDULED: Azul
     - PAUSED: Amarelo
     - ARCHIVED: Cinza escuro

2. **Metadata Grid (2x2)**
   ```
   Objeto: Case              │ Campos: 5
   Tipo: Summary             │ Criado: 2h atrás
   ```

3. **Filtros Info**
   ```
   Filtros: 2 (se houver filtros)
   ```

4. **Action Buttons**
   - [Executar] - Azul (executa report e navega para resultados)
   - [Editar] - Cinza (navega para builder)
   - [Deletar] - Vermelho (com confirmação)

**Estados:**
- Hover: Sombra aumentada
- Loading: Botões desabilitados
- DRAFT: Botão "Executar" desabilitado

---

## 📊 FLUXOS DE USUÁRIO

### 1. VISUALIZAR RELATÓRIOS
```
Dashboard Page
    ↓ (useEffect)
loadReports()
    ↓
reportApi.listReports(limit=10, offset=0)
    ↓
[Loading State] → Skeleton loaders aparecem
    ↓
[Success] → ReportsList renderiza com dados
    ↓
[Error] → Mensagem vermelha aparece
```

**Arquivos Envolvidos:**
- `DashboardPage.tsx` → Página principal
- `ReportsList.tsx` → Container lista
- `ReportCard.tsx` → Card individual
- `useReports.ts` → Hook com lógica
- `reportApi.ts` → Chamadas API

---

### 2. FILTRAR POR STATUS
```
User clica em "Ativos"
    ↓
setCurrentStatus(ReportStatus.ACTIVE)
    ↓
loadReports(ReportStatus.ACTIVE)
    ↓
reportApi.listReports(..., status='ACTIVE')
    ↓
[Loading] + Lista recarrega
    ↓
Mostra apenas relatórios com status ACTIVE
```

---

### 3. EXECUTAR RELATÓRIO
```
User clica [Executar] em um Card
    ↓
handleExecute(reportId)
    ↓
executeReport(reportId)
    ↓
reportApi.executeReport(reportId)
    ↓
[Loading State] → Botão fica desabilitado
    ↓
[Success] → Navega para /analytics com dados
    ↓
Analytics Page renderiza resultados
```

---

### 4. EDITAR RELATÓRIO
```
User clica [Editar]
    ↓
handleEdit(reportId)
    ↓
navigate('/builder/{reportId}')
    ↓
Builder Frontend abre com dados do relatório
```

---

### 5. DELETAR RELATÓRIO
```
User clica [Deletar]
    ↓
Confirmação: "Tem certeza que deseja deletar?"
    ↓
deleteReport(reportId)
    ↓
reportApi.deleteReport(reportId)
    ↓
[Loading State] + Otimistic update (remove card)
    ↓
[Success] → Card desaparece da lista
    ↓
[Error] → Card volta, erro exibido
```

---

## 🔗 INTEGRAÇÃO COM OUTRAS PÁGINAS

### Para Analytics Page
```typescript
// Quando executa relatório
navigate(`/analytics`, {
  state: {
    result: executionResult,
    report: reportData
  }
})

// Analytics recebe:
result: {
  report_id: string
  status: 'success' | 'failed'
  rows_returned: number
  execution_time_ms: number
  executed_at: ISO DateTime
  data: Record<string, any>[]
}
```

### Para Builder Page
```typescript
// Quando edita relatório
navigate(`/builder/${reportId}`)

// Builder pode:
- Pré-carregar dados do relatório
- Modificar configuração
- Salvar alterações
```

---

## 📦 DADOS MOCKADOS ATUAIS

### Estrutura do Relatório
```typescript
interface Report {
  id: string                    // "r:001"
  name: string                  // "Relatório de Casos Abertos"
  description?: string          // "Monitora casos em aberto"
  object_type: string           // "Case", "Opportunity", "Account"
  report_type: string           // "Summary", "Matrix", "Tabular"
  fields: string[]              // ["Id", "Subject", "Status"]
  filters?: Filter[]            // Filtros aplicados
  aggregations?: Aggregation[]  // Agrupamentos
  limit: number                 // 10000
  status: ReportStatus          // DRAFT | ACTIVE | SCHEDULED | PAUSED | ARCHIVED
  metadata: {
    created_by: string          // "user@company.com"
    created_at: ISO DateTime    // "2026-08-16T10:30:00Z"
    updated_by?: string
    updated_at?: ISO DateTime
  }
  schedule?: {
    enabled: boolean
    cron: string               // "0 9 * * MON-FRI"
  }
}
```

### Exemplo de Dados Mock
```javascript
{
  id: "r:001",
  name: "Casos Abertos por Prioridade",
  description: "Monitora casos abertos agrupados por prioridade",
  object_type: "Case",
  report_type: "Summary",
  fields: ["Id", "Subject", "Priority", "Status", "CreatedDate"],
  filters: [
    {
      field: "Status",
      operator: "equals",
      value: "New"
    }
  ],
  limit: 1000,
  status: "ACTIVE",
  metadata: {
    created_by: "admin@company.com",
    created_at: "2026-08-15T14:30:00Z"
  }
}
```

---

## 🔌 INTEGRAÇÃO COM API (Quando implementada)

### Endpoint: `GET /api/reports`
```bash
# Request
GET /api/reports?limit=10&offset=0&status=ACTIVE

# Response
{
  "success": true,
  "total": 12,
  "items": [
    {
      "id": "r:001",
      "name": "Casos Abertos",
      "object_type": "Case",
      "report_type": "Summary",
      "status": "ACTIVE",
      "created_at": "2026-08-15T14:30:00Z",
      "created_by": "admin@company.com",
      "fields": ["Id", "Subject", "Status"]
    },
    ...
  ]
}
```

### Endpoint: `POST /api/reports/{id}/execute`
```bash
# Request
POST /api/reports/r:001/execute

# Response
{
  "report_id": "r:001",
  "status": "success",
  "rows_returned": 42,
  "execution_time_ms": 245,
  "executed_at": "2026-08-16T10:30:45Z",
  "data": [
    {
      "Id": "500xx000001",
      "Subject": "Case A",
      "Priority": "High",
      "Status": "New"
    },
    ...
  ]
}
```

---

## 🚀 COMO VISUALIZAR AGORA

### Opção 1: Iniciar Dev Server (requer mock API)
```bash
cd frontends/dashboard-fe
npm install
npm run dev

# Abre em http://localhost:5173
# Mas vai dar erro porque não há API em /api/reports
```

### Opção 2: Implementar Mock Interceptor
```typescript
// src/api/reportApi.ts (adicionar antes do apiClient)

import MockAdapter from 'axios-mock-adapter';

const mock = new MockAdapter(apiClient, { delayResponse: 500 });

// Mock dados
const MOCK_REPORTS = [
  {
    id: 'r:001',
    name: 'Casos Abertos',
    object_type: 'Case',
    // ...
  }
];

mock.onGet('/reports').reply(200, {
  success: true,
  total: MOCK_REPORTS.length,
  items: MOCK_REPORTS
});
```

### Opção 3: Usar Backend Mock Server
```bash
# Criar servidor Express mock que retorna dados em /api/reports
# Implementado na Fase 11 (Integração Real)
```

---

## 📋 CHECKLIST DE VISUALIZAÇÃO

### Elementos Visuais ✅
- [x] Header com título e botão "Novo Relatório"
- [x] Filter bar com status buttons
- [x] Report cards em grid 3 colunas
- [x] Status badges com cores corretas
- [x] Metadata grid (Objeto, Campos, Tipo, Criado)
- [x] Action buttons (Executar, Editar, Deletar)
- [x] Loading skeleton loaders
- [x] Error message display
- [x] Empty state message
- [x] "Carregar mais" pagination button

### Funcionalidades ✅
- [x] Carregar relatórios ao montar
- [x] Filtrar por status
- [x] Paginação (offset + limit)
- [x] Executar relatório → Navegar para Analytics
- [x] Editar relatório → Navegar para Builder
- [x] Deletar com confirmação
- [x] Estados de loading
- [x] Tratamento de erros

### Responsividade ✅
- [x] Mobile: 1 coluna
- [x] Tablet: 2 colunas
- [x] Desktop: 3 colunas
- [x] Touch-friendly buttons
- [x] Scroll horizontal em devices pequenos (se necessário)

---

## 🎯 PRÓXIMAS ETAPAS

### Fase 11: Integração Real
```
1. Implementar Backend Mock Server (/api/reports)
2. Conectar MCP Client ao API Gateway
3. Substituir dados mock com dados reais do Salesforce
4. Testar fluxo completo
```

### Fase 12: Melhorias UI/UX
```
1. Adicionar busca por nome do relatório
2. Ordenação (criado, atualizado, nome)
3. Bulk actions (deletar múltiplos)
4. Favoritos/starred reports
5. Analytics e insights (mais usados, últimos executados)
```

### Fase 13: Avançado
```
1. Compartilhamento de relatórios
2. Permissões granulares por relatório
3. Histórico de execuções
4. Agendamento direto do dashboard
5. Notificações (Slack, Email)
```

---

## 📝 NOTAS TÉCNICAS

### Performance
- **Paginação:** Limite padrão 10 relatórios por página
- **Skeleton Loading:** 3 placeholders enquanto carrega
- **Caching:** Hook `useReports` mantém estado em memória
- **Refetch:** Apenas quando status filter muda

### Acessibilidade
- [ ] ARIA labels em botões
- [ ] Keyboard navigation (Tab, Enter)
- [ ] Focus indicators
- [ ] Contraste de cores (WCAG AA)

### Testes
```bash
# Arquivo: src/hooks/useReports.test.ts
# Testes de:
# - loading, error, success states
# - filter por status
# - paginação
# - CRUD operations
```

---

## 🔧 TROUBLESHOOTING

### Dashboard mostra "Nenhum relatório encontrado"
**Causa:** API não está retornando dados  
**Solução:** Verificar se backend está rodando em http://localhost:3000/api

### Botões não respondem
**Causa:** Estado de loading contínuo  
**Solução:** Verificar console para erros na API

### Cards aparecem vazios
**Causa:** Dados não formatados corretamente  
**Solução:** Verificar structure Report vs ResponseData

---

## 📚 ARQUIVOS PRINCIPAIS

```
frontends/dashboard-fe/
├── src/
│   ├── pages/
│   │   └── DashboardPage.tsx        ← Página principal
│   ├── components/
│   │   ├── ReportsList.tsx          ← Container lista
│   │   └── ReportCard.tsx           ← Card individual
│   ├── hooks/
│   │   └── useReports.ts            ← Lógica de dados
│   ├── api/
│   │   └── reportApi.ts             ← Chamadas HTTP
│   ├── types/
│   │   └── report.ts                ← TypeScript types
│   └── styles/
│       └── globals.css              ← Tailwind CSS
```

---

**Última Atualização:** 2026-08-16  
**Status:** Pronto para visualização  
**Próxima Etapa:** Fase 11 - Integração com API Real
