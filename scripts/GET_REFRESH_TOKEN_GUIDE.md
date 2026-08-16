# 🔑 Guia: Obter Refresh Token do Salesforce

Este script automatiza o processo de obtenção de credenciais OAuth2 do Salesforce necessárias para integração com GitHub Actions.

## 📋 O que você precisa

- Uma instância **Salesforce**
- Acesso para criar uma **Connected App** (requer permissões de admin)
- Python 3.7+ instalado
- Bibliotecas: `requests`

## 🚀 Passo 1: Criar Connected App no Salesforce

### 1.1 Acessar Setup do Salesforce

1. Faça login em sua instância Salesforce
2. Clique na engrenagem ⚙️ (Setup) no canto superior direito
3. Na barra de busca, digite: **App Manager**
4. Clique em **App Manager** (primeira opção)

### 1.2 Criar Nova Aplicação

1. Clique no botão **New Connected App** (canto superior direito)
2. Na tela que aparecer, preencha:

   ```
   Basic Information
   ├─ Connected App Name: "Dashboard Salesforce"
   ├─ API Name: "Dashboard_Salesforce" (auto-preenchido)
   └─ Contact Email: seu_email@empresa.com
   ```

3. Desça e marque: **Enable OAuth Settings** ✓

### 1.3 Configurar OAuth

Quando marcar "Enable OAuth Settings", aparecerão campos extras:

```
OAuth Scopes (Selected)
├─ Full access (full)
├─ Perform requests at any time (refresh_token)
├─ OpenID Connect compliant (openid)
├─ Access the identity URL service (id)
└─ Access profile information (profile)

Callback URL:
http://localhost:8000/callback
```

**Importante:** O Callback URL deve ser **exatamente** `http://localhost:8000/callback`

4. Clique em **Save**

### 1.4 Obter Consumer Key e Secret

1. Após salvar, voltará à tela da app
2. Na seção **API (Enable OAuth Settings)**, clique em **Reveal** perto de:
   - **Consumer Key** → Copie este valor
   - **Consumer Secret** → Clique **Show** → Copie este valor

Você terá dois valores como:
```
Consumer Key:    3MVG9vtcvGoeH2bjjoBRXWHirj6fo5s23.....
Consumer Secret: 97FE711D7F40A390190B45DDDE1D3B.....
```

---

## 💻 Passo 2: Executar o Script

### 2.1 Preparar Ambiente

```bash
# Ativar virtual environment (se tiver)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Instalar dependências
pip install requests
```

### 2.2 Editar o Script

Abra `scripts/get_refresh_token.py` e preencha os valores:

```python
# Linha 16-17: PREENCHA COM SEUS VALORES
CONSUMER_KEY = "3MVG9vtcvGoeH2bjjoBRXWHirj6fo5s23....."  # Copie aqui
CONSUMER_SECRET = "97FE711D7F40A390190B45DDDE1D3B....."  # Copie aqui
```

### 2.3 Executar Script

```bash
python scripts/get_refresh_token.py
```

Você verá:
```
======================================================================
SALESFORCE REFRESH TOKEN GENERATOR (com PKCE)
======================================================================

[PKCE] Gerando code_verifier e code_challenge...
[1] Abrindo navegador...
[2] Aguardando autorizacao...
[3] Navegador aberto! Autorize no Salesforce.
```

Um navegador abrirá automaticamente pedindo para você autorizar. **Clique em "Autorizar"** na tela do Salesforce.

### 2.4 Copiar Credenciais

O script mostrará um output assim:

```
======================================================================
CREDENCIAIS PARA GITHUB:
======================================================================

SF_CLIENT_ID:
  3MVG9vtcvGoeH2bjjoBRXWHirj6fo5s23.....

SF_CLIENT_SECRET:
  97FE711D7F40A390190B45DDDE1D3B.....

SF_REFRESH_TOKEN:
  00D90000000KKZZ!AQEAQE3pKJvQ0fP5X_v2ExNzJV...

======================================================================

Copie os 3 valores acima para GitHub Secrets!
```

**Copie cada valor com cuidado** (não copie espaços extras).

---

## 🔐 Passo 3: Adicionar no GitHub Secrets

### 3.1 Ir para Settings do Repositório

1. Vá para seu repositório no GitHub
2. Clique em **Settings** (engrenagem)
3. No menu esquerdo, clique em **Secrets and variables** → **Actions**

### 3.2 Criar 3 Repository Secrets

Para cada credencial do script, clique em **New repository secret**:

#### Secret 1
```
Name:   SF_CLIENT_ID
Secret: 3MVG9vtcvGoeH2bjjoBRXWHirj6fo5s23.....
```
Clique **Add secret**

#### Secret 2
```
Name:   SF_CLIENT_SECRET
Secret: 97FE711D7F40A390190B45DDDE1D3B.....
```
Clique **Add secret**

#### Secret 3
```
Name:   SF_REFRESH_TOKEN
Secret: 00D90000000KKZZ!AQEAQE3pKJvQ0fP5X_v2ExNzJV...
```
Clique **Add secret**

### 3.3 Verificar

Você verá na página:
```
Repository secrets (3)

• SF_CLIENT_ID
• SF_CLIENT_SECRET
• SF_REFRESH_TOKEN
```

---

## ✅ Próximas Etapas

1. **Ativar GitHub Pages:**
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: main
   - Folder: /docs
   - Save

2. **Rodar Workflow Manual:**
   - Vá para **Actions**
   - Selecione **Fetch Salesforce Data**
   - Clique **Run workflow**
   - Aguarde ~30 segundos

3. **Acessar Dashboard:**
   - Vá para: `https://seu-usuario.github.io/Salesforce_CasesDashboards`

---

## 🆘 Troubleshooting

### Erro: "missing required code_challenge"
**Causa:** Versão antiga do script sem PKCE  
**Solução:** Use a versão mais recente deste arquivo

### Erro: "Callback URL mismatch"
**Causa:** A URL configurada na Connected App não bate com `http://localhost:8000/callback`  
**Solução:** Edite a Connected App no Salesforce e confirme o Callback URL

### Erro: "Invalid OAuth response"
**Causa:** Consumer Key/Secret copiados errados ou Connected App não ativada  
**Solução:** 
1. Delete a Connected App
2. Crie uma nova
3. Cópie os valores com cuidado

### Script timeout (5 minutos)
**Causa:** Autorizou mas script não capturou o código  
**Solução:** Não feche o terminal enquanto autoriza no Salesforce

### Porta 8000 já em uso
**Causa:** Outra aplicação usando a mesma porta  
**Solução:** Edite o script e mude `PORT = 8000` para `PORT = 8001`

---

## 📝 Notas de Segurança

⚠️ **Importante:**
- Nunca compartilhe seus credentials
- Nunca commite o script com Consumer Key/Secret preenchidos
- Use GitHub Secrets para armazenar essas informações
- Se expôs os secrets, regenere-os no Salesforce

---

## 🔄 Usando com CI/CD

O workflow `.github/workflows/fetch-salesforce-data.yml` usa esses secrets automaticamente:

```yaml
env:
  SF_CLIENT_ID: ${{ secrets.SF_CLIENT_ID }}
  SF_CLIENT_SECRET: ${{ secrets.SF_CLIENT_SECRET }}
  SF_REFRESH_TOKEN: ${{ secrets.SF_REFRESH_TOKEN }}
```

Não precisa fazer mais nada! A sincronização acontece automaticamente a cada 1 hora.

---

## 📚 Referências

- [Salesforce OAuth2 Docs](https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm)
- [MCP Salesforce Server](https://github.com/modelcontextprotocol/server-salesforce)
- [GitHub Actions Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

---

**Última atualização:** 2026-08-16  
**Versão:** 1.0 - Com suporte a PKCE
