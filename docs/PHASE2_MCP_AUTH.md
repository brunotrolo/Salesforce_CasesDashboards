# Phase 2: MCP Client + Auth Service

**Status:** ⏳ Planned  
**Milestone:** Salesforce integration and authentication layer  
**Duration:** 2-3 weeks  
**Depends on:** Phase 1 ✅

---

## Overview

Phase 2 implements the critical integration layer between the system and Salesforce via the MCP (Model Context Protocol) Client, plus the authentication and authorization service.

### Key Objectives

1. **Salesforce MCP Integration**
   - OAuth 2.0 authentication with Salesforce
   - CRUD operations on Salesforce data
   - Error handling and retry logic
   - Connection pooling and optimization

2. **Authentication Service**
   - JWT token generation and validation
   - OAuth2 flow implementation
   - Refresh token management
   - Session management

3. **Authorization Service**
   - Role-Based Access Control (RBAC)
   - Permission validation
   - API endpoint protection
   - User context propagation

4. **Service Discovery**
   - Service registration
   - Health checks
   - Load balancing preparation

---

## Architecture

### Service Overview

```
┌─────────────┐
│ Salesforce  │
│   OAuth     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   MCP Client Service (3005)         │
│  - OAuth Handler                    │
│  - Connection Manager               │
│  - Report Operations CRUD           │
│  - Error Handling                   │
└─────────────────────────────────────┘
       │                    │
       ▼                    ▼
┌──────────────────┐  ┌───────────────┐
│ Auth Service     │  │ Data Service  │
│  (3002)          │  │  (3003)       │
│                  │  │               │
│ - JWT Handler    │  │ - Salesforce  │
│ - OAuth Flow     │  │   Data Fetch  │
│ - Token Mgmt     │  │ - Transform   │
│ - RBAC          │  │ - Cache       │
└──────────────────┘  └───────────────┘
       ▲                    ▲
       │                    │
       └────────┬───────────┘
                │
        ┌───────▼────────┐
        │ API Gateway    │
        │    (80)        │
        └────────────────┘
```

---

## Components

### 1. MCP Client Service

**Port:** 3005  
**Repository:** `services/mcp-client/`

#### Responsibilities

- **OAuth Authentication**
  - Initial authentication flow
  - Token refresh mechanism
  - Credential management
  - Connection lifecycle

- **Report Operations**
  - Create reports
  - Read/list reports
  - Update reports
  - Delete reports
  - Execute reports

- **Error Handling**
  - Retry logic with exponential backoff
  - Circuit breaker pattern
  - Graceful degradation
  - Error logging and monitoring

#### Structure

```
services/mcp-client/
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── oauth_handler.py         # OAuth flow
│   ├── salesforce_connector.py  # MCP integration
│   ├── report_operations.py     # CRUD operations
│   ├── models.py                # Pydantic models
│   ├── error_handler.py         # Exception handling
│   ├── config.py                # Configuration
│   └── middleware/
│       ├── __init__.py
│       ├── logging.py           # Request/response logging
│       └── tracing.py           # Distributed tracing
├── tests/
│   ├── test_oauth_handler.py
│   ├── test_salesforce_connector.py
│   ├── test_report_operations.py
│   └── conftest.py
├── Dockerfile
├── requirements.txt
└── .env.example
```

#### Key Endpoints

```
POST   /oauth/authorize          # Start OAuth flow
GET    /oauth/callback           # Handle OAuth callback
POST   /oauth/refresh            # Refresh access token

GET    /reports                  # List reports
POST   /reports                  # Create report
GET    /reports/{id}             # Get report
PUT    /reports/{id}             # Update report
DELETE /reports/{id}             # Delete report

POST   /reports/{id}/execute     # Execute report
GET    /reports/{id}/status      # Get execution status

GET    /health                   # Health check
POST   /health/readiness         # Readiness probe
```

#### Dependencies

```txt
fastapi==0.100.0
uvicorn==0.23.0
pydantic==2.0.0
requests==2.31.0
httpx==0.24.0
python-jose==3.3.0
passlib==1.7.4
cryptography==41.0.0
python-multipart==0.0.6
sqlalchemy==2.0.0
psycopg2-binary==2.9.0
redis==5.0.0
elasticsearch==8.0.0
opentelemetry-api==1.20.0
opentelemetry-sdk==1.20.0
```

### 2. Auth Service

**Port:** 3002  
**Repository:** `services/auth-service/`

#### Responsibilities

- **JWT Management**
  - Token generation
  - Token validation
  - Token refresh
  - Claims extraction

- **OAuth2 Integration**
  - Authorization code flow
  - Client credentials flow
  - Token exchange
  - Scope management

- **RBAC Implementation**
  - Permission checking
  - Role hierarchy
  - Resource-level permissions
  - API endpoint protection

- **Session Management**
  - Session creation
  - Session validation
  - Session revocation
  - Timeout handling

#### Structure

```
services/auth-service/
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app
│   ├── jwt_handler.py           # JWT operations
│   ├── oauth_handler.py         # OAuth2 flow
│   ├── rbac.py                  # Permission system
│   ├── models.py                # Pydantic models
│   ├── config.py                # Configuration
│   ├── database.py              # DB models
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py              # Auth middleware
│       └── rbac.py              # RBAC middleware
├── tests/
│   ├── test_jwt_handler.py
│   ├── test_oauth_handler.py
│   ├── test_rbac.py
│   └── conftest.py
├── Dockerfile
├── requirements.txt
└── .env.example
```

#### Key Endpoints

```
POST   /auth/login                # Login with credentials
POST   /auth/logout               # Logout
POST   /auth/refresh              # Refresh token

POST   /auth/oauth/authorize      # OAuth authorization
POST   /auth/oauth/token          # Token exchange

GET    /auth/me                   # Get current user info
GET    /auth/permissions          # List user permissions
GET    /auth/roles                # List user roles

POST   /auth/permissions/{resource}  # Check permission
POST   /auth/validate-token       # Validate JWT

GET    /health                    # Health check
```

#### Permission Model

```python
# Role-based permissions
ROLES = {
    'admin': ['*'],              # All permissions
    'manager': [
        'reports:create',
        'reports:read',
        'reports:update',
        'reports:execute',
        'users:read',
    ],
    'user': [
        'reports:read',
        'reports:execute',
    ],
    'guest': [
        'reports:read',
    ],
}
```

### 3. Configuration & Secrets

**Location:** `infra/kubernetes/configmaps/`

#### Environment Variables

```bash
# Auth Service
JWT_SECRET_KEY=<strong-secret-key>
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
REFRESH_TOKEN_EXPIRATION_DAYS=30

# Salesforce OAuth
SF_CLIENT_ID=<from-salesforce-setup>
SF_CLIENT_SECRET=<from-salesforce-setup>
SF_REDIRECT_URI=https://api.reports.example.com/oauth/callback
SF_INSTANCE_URL=https://login.salesforce.com

# Service Configuration
MCP_CLIENT_URL=http://mcp-client:3005
AUTH_SERVICE_URL=http://auth-service:3002
DATABASE_URL=postgresql://reports_user:password@postgres:5432/reports_db
REDIS_URL=redis://redis:6379/0

# Logging
LOG_LEVEL=INFO
TRACE_SAMPLE_RATE=0.1
```

---

## Implementation Plan

### Week 1: MCP Client Foundation

**Tasks:**
1. Setup FastAPI project structure
2. Implement OAuth handler
   - Authorization code flow
   - Token refresh
   - Error handling
3. Basic Salesforce connector
   - Connection management
   - Authentication testing
4. Unit tests for OAuth and connector

**Deliverable:** 
- ✅ MCP Client service running
- ✅ OAuth flow tested
- ✅ Salesforce connection verified

### Week 2: Report Operations & Auth Service

**Tasks:**
1. Report CRUD operations in MCP client
   - Create/read/update/delete
   - List with pagination
   - Execute report flow
2. Auth service foundation
   - JWT handler
   - Token generation/validation
3. RBAC system
   - Role definition
   - Permission checking
4. Integration tests

**Deliverable:**
- ✅ Report operations working
- ✅ Auth service operational
- ✅ RBAC system validated

### Week 3: Integration & Production Ready

**Tasks:**
1. Error handling improvements
   - Circuit breaker pattern
   - Retry logic
   - Proper error responses
2. Middleware implementation
   - Request logging
   - Authentication middleware
   - RBAC middleware
3. Monitoring & metrics
   - Health checks
   - Prometheus metrics
   - Distributed tracing
4. Documentation
   - API documentation
   - Integration guide
   - Troubleshooting

**Deliverable:**
- ✅ Production-ready services
- ✅ Full integration tests
- ✅ Monitoring active
- ✅ Documentation complete

---

## Testing Strategy

### Unit Tests

**MCP Client:**
```python
# test_oauth_handler.py
def test_authorization_code_flow()
def test_token_refresh()
def test_invalid_credentials()

# test_salesforce_connector.py
def test_connection_establishment()
def test_connection_failure_recovery()

# test_report_operations.py
def test_create_report()
def test_list_reports()
def test_execute_report()
```

**Auth Service:**
```python
# test_jwt_handler.py
def test_token_generation()
def test_token_validation()
def test_expired_token()

# test_rbac.py
def test_permission_check()
def test_role_hierarchy()
```

### Integration Tests

```python
# test_oauth_flow.py
def test_complete_oauth_flow()

# test_report_execution.py
def test_report_lifecycle()

# test_authentication_flow.py
def test_full_authentication_chain()
```

### Coverage Requirements

- MCP Client: 85% coverage
- Auth Service: 90% coverage (security-critical)
- RBAC: 95% coverage

---

## Security Considerations

### OAuth Security

- ✅ Use authorization code flow (not implicit)
- ✅ PKCE support for mobile clients
- ✅ Secure token storage (httpOnly cookies)
- ✅ Token expiration and rotation
- ✅ HTTPS-only in production

### JWT Security

- ✅ Strong secret key (32+ characters)
- ✅ Signed tokens (HS256 or RS256)
- ✅ Short expiration (24 hours)
- ✅ Refresh token rotation
- ✅ Claims validation

### API Security

- ✅ Rate limiting (auth endpoints)
- ✅ Input validation (Pydantic)
- ✅ CORS configuration
- ✅ Security headers
- ✅ SQL injection prevention (ORM)

---

## Monitoring & Logging

### Metrics

```python
# Prometheus metrics
oauth_request_duration_seconds
oauth_request_errors_total
jwt_token_validation_duration_seconds
rbac_permission_check_duration_seconds
report_operation_duration_seconds
```

### Logs (ELK Stack)

```json
{
  "timestamp": "2026-08-16T10:30:45.123Z",
  "service": "auth-service",
  "level": "INFO",
  "trace_id": "abc123def456",
  "event": "JWT token validated",
  "user_id": "u:12345",
  "duration_ms": 2,
  "context": {
    "token_claims": {"exp": 1692259845, "iat": 1692173445}
  }
}
```

---

## Error Handling

### Common Error Codes

```
401 Unauthorized    - Missing/invalid credentials
403 Forbidden       - Insufficient permissions
404 Not Found       - Resource not found
429 Too Many        - Rate limit exceeded
500 Internal Error  - Server error
503 Unavailable     - Service unavailable
```

### Retry Strategy

```
OAuth Failures: Exponential backoff (2s, 4s, 8s, 16s)
Salesforce API: Retry on 429, 503, 504
Max retries: 3
Timeout: 30 seconds
```

---

## Documentation Artifacts

### API Documentation
- OpenAPI/Swagger schema
- Interactive API explorer
- Example requests/responses

### Integration Guide
- Step-by-step setup
- OAuth configuration
- Permission setup

### Architecture Diagram
- Service interactions
- Data flow
- Authentication flow

---

## Success Criteria

- ✅ OAuth flow working end-to-end
- ✅ MCP client can CRUD reports in Salesforce
- ✅ Auth service issues valid JWT tokens
- ✅ RBAC properly restricts access
- ✅ 85%+ test coverage
- ✅ Monitoring and logging active
- ✅ Production-ready error handling
- ✅ Complete documentation

---

## Next Phase

**Phase 3:** Logging Service
- Centralized logging infrastructure
- Log aggregation and analysis
- Alerting and dashboards

---

## Resources

- FastAPI: https://fastapi.tiangolo.com/
- Pydantic: https://docs.pydantic.dev/
- Python-Jose: https://github.com/mpdavis/python-jose
- Salesforce OAuth: https://developer.salesforce.com/docs/atlas.en-us.oauth_guidance.meta/oauth_guidance/
- JWT: https://jwt.io/

---

**Phase 2 Status:** ⏳ Ready to start
**Next:** Begin MCP Client implementation
