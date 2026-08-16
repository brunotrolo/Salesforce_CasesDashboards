# Detalhamento de Serviços

## MCP Client

Responsável pela comunicação com Salesforce via MCP.

### Operações

- Create: `/reports/new_report`
- Read: `/reports/report_id`
- Update: `/reports/report_id`
- Delete: `/reports/report_id`
- List: `/reports`

## Report Service

Orquestração de operações de relatórios.

### Endpoints

- POST /reports - Criar
- GET /reports - Listar
- GET /reports/{id} - Buscar
- PUT /reports/{id} - Atualizar
- DELETE /reports/{id} - Deletar

## Auth Service

Gerenciamento centralizado de autenticação.

### Endpoints

- POST /auth/login - Login
- POST /auth/refresh - Refresh token
- POST /auth/logout - Logout
- GET /auth/verify - Verificar token
