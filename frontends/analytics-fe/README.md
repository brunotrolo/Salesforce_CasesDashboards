# Analytics Frontend

Interface para visualização de resultados e análise de dados de relatórios.

## Visão Geral

O Analytics Frontend permite aos usuários:
- Visualizar resultados em tabelas
- Criar gráficos dos dados
- Analisar performance
- Exportar dados

## Tecnologias

- **React 18** - Framework UI
- **TypeScript 5** - Type safety
- **Recharts** - Gráficos
- **Tailwind CSS 3** - Styling
- **Vite** - Build tool

## Estrutura

```
src/
├── components/        # BarChart, DataTable, etc
├── pages/            # ResultsPage (main)
├── api/              # reportApi
├── types/            # Tipos (analytics, report)
└── utils/            # Utilitários
```

## Componentes Principais

### BarChart
Gráfico de barras usando Recharts.

### DataTable
Tabela de dados com formatação condicional.

### ResultsPage
Página de resultados com resumo e visualizações.

## Instalação

```bash
npm install
```

## Desenvolvimento

```bash
npm run dev      # Porta 5175
npm run lint
npm run test
```

## Build

```bash
npm run build
npm run preview
```

## Status de Implementação

- [x] Estrutura React + TypeScript
- [x] BarChart e DataTable
- [x] ResultsPage com summary
- [ ] LineChart
- [ ] PieChart
- [ ] Exportar como PDF/Excel
- [ ] Gráficos customizáveis

## Próximas Etapas

1. Implementar PieChart e LineChart
2. Adicionar export PDF/Excel
3. Testes unitários
4. Performance optimization
