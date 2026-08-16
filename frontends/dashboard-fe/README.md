# Dashboard Frontend

Interface visual para gerenciamento e execução de relatórios Salesforce.

## Visão Geral

O Dashboard Frontend é uma aplicação React com TypeScript que permite aos usuários:
- Visualizar lista de relatórios com paginação
- Executar relatórios e ver resultados
- Criar e editar relatórios
- Filtrar por status (Ativo, Rascunho, Agendado, Pausado)
- Deletar relatórios

## Tecnologias

- **React 18** - Framework UI
- **TypeScript 5** - Type safety
- **Tailwind CSS 3** - Styling
- **Vite** - Build tool
- **Axios** - HTTP client
- **React Router 6** - Routing
- **Vitest** - Testing

## Estrutura

```
src/
├── components/        # Componentes reutilizáveis
│   ├── ReportCard.tsx
│   └── ReportsList.tsx
├── pages/            # Páginas/rotas
│   └── DashboardPage.tsx
├── hooks/            # Hooks customizados
│   └── useReports.ts
├── api/              # Serviços de API
│   └── reportApi.ts
├── types/            # Tipos TypeScript
│   └── report.ts
├── styles/           # Estilos globais
│   └── globals.css
├── App.tsx           # Componente principal
└── main.tsx          # Entry point
```

## Instalação

```bash
cd frontends/dashboard-fe
npm install
```

## Desenvolvimento

```bash
# Iniciar dev server (porta 5173)
npm run dev

# Lint
npm run lint

# Testes
npm run test

# Coverage
npm run test:coverage
```

## Build

```bash
npm run build
npm run preview
```

## Componentes Principais

### ReportCard
Exibe um único relatório com opções para executar, editar e deletar.

### ReportsList
Lista de relatórios com filtros e paginação.

## Hooks

### useReports
Gerencia estado e operações de relatórios com métodos para:
- Carregar lista
- Obter um relatório
- Executar relatório
- Deletar relatório
- Gerenciar paginação

## API

Comunicação com backend via `reportApi` para todas operações CRUD.

## Status de Implementação

- [x] Estrutura base React + TypeScript
- [x] Componentes ReportCard e ReportsList
- [x] Hook useReports
- [x] Integração API
- [x] Tipos TypeScript
- [ ] Testes unitários
- [ ] Página de detalhes do relatório
- [ ] Página de resultados com gráficos
- [ ] Dark mode
- [ ] Internacionalização

## Próximas Etapas

1. Implementar testes com Vitest
2. Adicionar página de resultados (charts com Recharts)
3. Melhorar UX com loading states
4. Adicionar dark mode
5. Otimizar performance (memoization)
