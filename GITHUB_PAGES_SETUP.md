# 🚀 GitHub Pages Setup - Guia Rápido

## ⚡ 5 Passos para Ativar o Dashboard

### Passo 1: Configurar Secrets (Credenciais Salesforce)

1. Vá para: **GitHub → Settings → Secrets and variables → Actions**
2. Clique: **"New repository secret"**
3. Adicione 3 secrets:

```
Name: SF_CLIENT_ID
Value: [Seu Client ID do OAuth2 Salesforce]

Name: SF_CLIENT_SECRET
Value: [Seu Client Secret do OAuth2 Salesforce]

Name: SF_REFRESH_TOKEN
Value: [Seu Refresh Token]
```

**Como obter as credenciais:**
- Se estiver em desenvolvimento local: usar MCP client para autenticar
- Se tiver Salesforce Admin: setup OAuth2 em Setup → Apps → Connected Apps
- Documentação: [MCP Salesforce Docs](https://github.com/modelcontextprotocol/server-salesforce)

### Passo 2: Ativar GitHub Pages

1. Vá para: **GitHub → Settings → Pages**
2. Selecione:
   - **Source:** "Deploy from a branch"
   - **Branch:** "main"
   - **Folder:** "/docs"
3. Clique: **"Save"**

⏳ Aguarde 1-2 minutos...

### Passo 3: Acessar o Dashboard

Seu dashboard estará disponível em:

```
https://brunotrolo.github.io/Salesforce_CasesDashboards
```

(Substitua `brunotrolo` pelo seu username do GitHub)

### Passo 4: Rodar Sincronização Manualmente (Primeira Vez)

1. Vá para: **GitHub → Actions**
2. Selecione: **"Fetch Salesforce Data"**
3. Clique: **"Run workflow"** → **"Run workflow"**
4. Aguarde: ~30 segundos

Dashboard carregará com dados reais do Salesforce!

### Passo 5: Verificar Logs (Opcional)

Se houver erro, ver logs:

1. **Actions** → **"Fetch Salesforce Data"**
2. Clique no último workflow run
3. Veja detalhes e logs de erro

## 📊 O que Funciona Agora

✅ Dashboard Estático 100% Hospedado no GitHub Pages  
✅ Sincronização Automática a Cada 1 Hora  
✅ Dados Reais do Salesforce via MCP  
✅ Gráficos (Status, Prioridade, Tendência, Top Accounts)  
✅ Tabelas Interativas (Cases, Reports, Accounts)  
✅ Auto-Refresh a Cada 5 Minutos  
✅ Dark Mode Support  
✅ Responsivo (Desktop, Tablet, Mobile)  

## 🎯 Status Esperado

Ao acessar dashboard pela primeira vez:

- ❌ Vazio (sem dados ainda)
- 📦 Mostra "Dados de Fallback"

Após rodar workflow:

- ✅ Carrega com dados REAIS de Cases, Reports, Accounts
- 🔄 Auto-sincroniza a cada 1 hora
- 📊 Gráficos e tabelas em tempo real

## 🆘 Troubleshooting

### Dashboard vazio / Mostra "Carregando..."

**Solução 1:** Rodar workflow manualmente em Actions → Fetch Salesforce Data

**Solução 2:** Verificar secrets em Settings → Secrets
- Confirmando que SF_CLIENT_ID, SF_CLIENT_SECRET, SF_REFRESH_TOKEN estão configurados
- Credenciais estão corretas

### "Dados de Fallback" em vez de dados LIVE

**Causa:** Secrets não configurados ou credenciais inválidas

**Solução:**
```bash
# Testar credenciais localmente:
export SF_CLIENT_ID="seu_id"
export SF_CLIENT_SECRET="seu_secret"
export SF_REFRESH_TOKEN="seu_token"
python scripts/salesforce-sync.py
```

Se der erro, revisar credenciais em Salesforce.

### Workflow deu erro "Module not found"

**Solução:** Certificar que `requirements.txt` tem todas as dependências:
```bash
pip install -r requirements.txt
python scripts/salesforce-sync.py  # testar localmente
```

## 📚 Próximos Passos (Opcional)

- [ ] Customizar cron schedule (alterar frequência de sync)
- [ ] Adicionar mais métricas/gráficos
- [ ] Configurar notifications (Slack, email, etc)
- [ ] Setup de monitoring
- [ ] Documentação para team

## 📞 Suporte

Dúvidas? Veja:
- `docs/README.md` - Documentação completa do dashboard
- `.github/workflows/fetch-salesforce-data.yml` - Workflow actions
- `scripts/salesforce-sync.py` - Script de sincronização
- [GitHub Pages Docs](https://docs.github.com/en/pages)

---

**Dashboard URL:** `https://brunotrolo.github.io/Salesforce_CasesDashboards`  
**Última atualização:** 2026-08-16
