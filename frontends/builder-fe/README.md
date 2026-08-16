# Builder Frontend

Interface de criação e edição de relatórios Salesforce com wizard de 6 passos.

## Visão Geral

O Builder Frontend permite aos usuários:
- Criar novos relatórios com interface intuitiva
- Editar relatórios existentes
- Selecionar campos de objetos Salesforce
- Configurar filtros e agregações
- Agendar execução automática

## Tecnologias

- **React 18** - Framework UI
- **TypeScript 5** - Type safety
- **Zustand** - State management
- **Tailwind CSS 3** - Styling
- **Vite** - Build tool

## Estrutura

```
src/
├── components/        # Componentes do formulário (FormStep, FormField)
├── pages/            # BuilderPage (main wizard)
├── stores/           # Zustand stores (reportFormStore)
├── api/              # API client
├── types/            # Types (report, form)
└── utils/            # Utilitários (logger, formatters)
```

## Passos do Wizard

1. **Informações Básicas** - Nome, descrição, tipo
2. **Objeto e Campos** - Selecionar objeto Salesforce
3. **Filtros** - Adicionar filtros
4. **Agregações** - Configurar agregações
5. **Agendamento** - Execução automática
6. **Revisão** - Salvar

## Setup

```bash
npm install
npm run dev      # Porta 5174
npm run lint
npm run test
npm run build
```

## Status de Implementação

- [x] Estrutura React + TypeScript
- [x] Zustand store
- [x] BuilderPage com navegação
- [ ] Implementar cada passo
- [ ] Validação em tempo real
- [ ] Testes unitários

## Próximas Etapas

Implementar os 6 passos do wizard e adicionar testes.
