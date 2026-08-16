# Skills Integration Guide

Este documento descreve como as três skills externas estão integradas no projeto para otimizar o fluxo de desenvolvimento via Claude Code Open.

## Arquitetura de Skills

```
Claude Code
    ↓
Skills Manager (.claude/skills-config.json)
    ├─ Agent Skills (code quality, testing, patterns)
    ├─ UI/UX Pro Max (design system, accessibility, components)
    └─ Impeccable (linting, formatting, CI/CD quality gates)
    ↓
Project Development Workflow
```

## Skills Instaladas

### 1. Agent Skills
**Repositório:** https://github.com/addyosmani/agent-skills

**Propósito:** Automação de qualidade de código, testes e detecção de padrões

**Comandos Disponíveis:**
```bash
# Gerar testes automaticamente para um serviço
claude /agent-skills suggest-tests --service report-service

# Analisar cobertura de testes
claude /agent-skills analyze-coverage --target services/

# Refatorar código mantendo testes
claude /agent-skills refactor --file services/api-gateway/src/main.py

# Detectar padrões anti-design
claude /agent-skills detect-patterns --directory services/
```

**Workflow Automático:**
- Acionado ao criar novo serviço (phase setup)
- Sugerido em code reviews
- Executado em novas features

---

### 2. UI/UX Pro Max Skill
**Repositório:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill

**Propósito:** Design system consistency, accessibility audits, component library management

**Comandos Disponíveis:**
```bash
# Configurar design system para um frontend
claude /ui-ux setup-design-system frontends/dashboard-fe

# Auditar acessibilidade (WCAG compliance)
claude /ui-ux audit-accessibility frontends/dashboard-fe

# Validar responsividade em múltiplos viewports
claude /ui-ux validate-responsive frontends/dashboard-fe

# Criar novo componente seguindo padrões
claude /ui-ux create-component --type dashboard --name ReportMetrics
```

**Workflow Automático:**
- Acionado ao criar novo frontend
- Validado em mudanças UI/UX
- Auditorias de acessibilidade em PRs

---

### 3. Impeccable
**Repositório:** https://github.com/pbakaus/impeccable

**Propósito:** Code quality automation, linting, pre-commit hooks, CI/CD gates

**Comandos Disponíveis:**
```bash
# Configurar linting para um serviço
claude /impeccable setup-linting services/report-service

# Gerar relatório de qualidade
claude /impeccable quality-report --branch main

# Lint apenas o serviço alterado
claude /impeccable lint --service api-gateway

# Formatar código
claude /impeccable format --directory services/
```

**Workflow Automático:**
- Pre-commit hook: lint automático antes de commit
- Pull Request: quality gates bloqueiam merge se qualidade < threshold
- CI/CD: security scans e coverage checks

---

## Modo de Operação

### Desenvolvimento de Nova Feature

```bash
# 1. Claude Code detecta nova feature / serviço
# 2. Agent Skills é acionado automaticamente
git checkout -b claude/nova-feature-nome

# 3. Código é escrito
# ... seu desenvolvimento ...

# 4. Pre-commit hook (Impeccable) valida
git add .
git commit -m "feat: implementar nova feature"

# 5. Impeccable formata e lint automaticamente
# 6. Agent Skills sugere testes
claude /agent-skills suggest-tests --service my-service

# 7. Você escreve os testes ou pede para agent gerar
# 8. Push e PR
git push origin claude/nova-feature-nome
```

### Desenvolvimento de Frontend

```bash
# 1. Criar novo componente
claude /ui-ux create-component --type form --name ReportFilter

# 2. UI/UX Pro Max valida design consistency
# 3. Impeccable lint TypeScript/CSS
# 4. Audit acessibilidade
claude /ui-ux audit-accessibility frontends/dashboard-fe

# 5. Commit
git add .
git commit -m "feat(dashboard): add report filter component"
```

### Code Review / Quality Gate

```bash
# Antes de mergear em main, rodar:
claude /impeccable quality-report --branch claude/minha-branch

# Resultado:
# ✓ ESLint: 100% pass
# ✓ Pylint (backend): 95/100
# ✓ Test Coverage: 82%
# ✓ Security Scan: 0 issues
# ✗ Accessibility: 3 contrast warnings (fixable)

# Corrigir issues
claude /ui-ux audit-accessibility frontends/ --fix

# Re-run quality report
claude /impeccable quality-report --branch claude/minha-branch
# ✓ All gates passed!
```

---

## Configuração de Ambiente

### 1. Instalar Skills Localmente

```bash
# Clonar skills para diretório local
mkdir -p skills
cd skills

git clone https://github.com/addyosmani/agent-skills.git
git clone https://github.com/nextlevelbuilder/ui-ux-pro-max-skill.git
git clone https://github.com/pbakaus/impeccable.git

cd ..
```

### 2. Setup de Pre-commit Hooks (Impeccable)

```bash
# Impeccable configura hooks automaticamente
claude /impeccable setup-linting services/

# Agora, todo commit roda linting automaticamente:
# $ git commit -m "feat: minha feature"
# Running Impeccable pre-commit hooks...
# ✓ ESLint passed
# ✓ Pylint passed
# ✓ Black formatting applied
# ✓ isort import sorting applied
# [claude/minha-feature abc1234] feat: minha feature
```

### 3. Design System Setup (UI/UX)

```bash
# Configurar design tokens, component library, e storybook
claude /ui-ux setup-design-system frontends/

# Resultado:
# ✓ Design tokens criados (colors, spacing, typography)
# ✓ Storybook configurado
# ✓ Component library template
# ✓ Tailwind integration
# ✓ Accessibility baseline checks
```

---

## Integração com Claude Code Open

### Automação Recomendada

No `CLAUDE.md`, adicione esta seção de automation directives:

```yaml
# Automation Directives
automation:
  on_new_service:
    - invoke: /agent-skills
      command: scaffold-service
      params:
        type: python
        include_tests: true
    - invoke: /impeccable
      command: setup-linting
      
  on_new_feature:
    - invoke: /agent-skills
      command: detect-patterns
      params:
        check_anti_patterns: true
    - invoke: /agent-skills
      command: suggest-tests
      
  on_frontend_change:
    - invoke: /ui-ux
      command: audit-accessibility
      params:
        auto_fix: false
    - invoke: /ui-ux
      command: validate-responsive
      
  on_pull_request:
    - invoke: /impeccable
      command: quality-report
      params:
        fail_if_below: 80
    - invoke: /agent-skills
      command: analyze-coverage
```

### Environment Variables

Adicione ao `.env`:

```bash
# Skills Configuration
CLAUDE_SKILLS_PATH=./skills
IMPECCABLE_MIN_QUALITY=80
IMPECCABLE_PYTHON_VERSION=3.11
UI_UX_FRAMEWORK=tailwind
AGENT_SKILLS_PYTHON_VERSION=3.11
```

---

## Uso em Desenvolvimento Diário

### Quando Começar Uma Task

```bash
# 1. Checkout branch de desenvolvimento
git checkout -b claude/task-descrição

# 2. Abrir Claude Code
# Open this repository in Claude Code

# 3. Descrever a task
# "Implementar caching layer no report-service"

# 4. Claude Code invoca automaticamente:
# → Agent Skills detecta novo código
# → Impeccable configura linting
# → Faz sugestões de padrões

# 5. Você escreve o código e testa
# ... development ...

# 6. Commit e Pre-commit hook executa
git add .
git commit -m "feat(report-service): add caching layer"
# Impeccable roda automaticamente antes de finalizar commit

# 7. Push
git push origin claude/task-descrição

# 8. PR é criado, quality gates são verificados
# CI/CD roda impeccable quality-report automaticamente
```

### Workflow Sugerido

**Para Backend (Python):**
1. Escrever código
2. `git add`
3. `git commit` → Impeccable lint automático
4. `claude /agent-skills suggest-tests`
5. Implementar testes sugeridos
6. `git commit -m "test(service): add tests for feature"`
7. `git push`

**Para Frontend (React/TypeScript):**
1. Criar componente com `claude /ui-ux create-component`
2. Escrever código
3. Rodar `claude /ui-ux validate-responsive`
4. Rodar `claude /ui-ux audit-accessibility`
5. Corrigir issues se necessário
6. Commit + Push

---

## Troubleshooting

### Skills Não Estão Sendo Acionadas

```bash
# Verificar se skills estão instaladas
ls skills/

# Verificar configuração
cat .claude/skills-config.json

# Reiniciar Claude Code
# Fechar e abrir novamente
```

### Linting Falha no Pre-commit

```bash
# Ver qual regra falhou
git diff --cached | head -50

# Rodar Impeccable manualmente
claude /impeccable lint --service api-gateway

# Auto-fix issues
claude /impeccable format --directory services/

# Retry commit
git add .
git commit -m "fix: linting issues resolved by impeccable"
```

### Testes Não São Sugeridos

```bash
# Verificar se arquivo segue convenção de naming
# Arquivo deve estar em services/*/src/

# Forçar sugestão
claude /agent-skills suggest-tests --service my-service --force

# Ou sugerir para arquivo específico
claude /agent-skills suggest-tests --file services/my-service/src/handler.py
```

---

## Próximos Passos

- [ ] Clonar skills para `./skills`
- [ ] Configurar Impeccable pre-commit hooks
- [ ] Configurar design system com UI/UX skill
- [ ] Adicionar automation directives ao CLAUDE.md
- [ ] Testar workflow em próxima feature
- [ ] Documentar padrões de componentes descobertos

---

## Referências

- **Agent Skills:** https://github.com/addyosmani/agent-skills
- **UI/UX Pro Max:** https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Impeccable:** https://github.com/pbakaus/impeccable
- **Project CLAUDE.md:** ./CLAUDE.md
