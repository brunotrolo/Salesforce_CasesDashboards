from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    USER = "user"
    GUEST = "guest"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=8)

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int

class TokenPayload(BaseModel):
    sub: str  # user_id
    exp: int
    iat: int
    type: TokenType
    role: UserRole
    permissions: List[str] = []

class User(BaseModel):
    id: str
    username: str
    email: str
    roles: List[UserRole]
    permissions: List[str]
    is_active: bool
    created_at: str
    last_login: Optional[str] = None

class PermissionCheck(BaseModel):
    resource: str
    action: str
    granted: bool
    reason: Optional[str] = None

class PermissionRequest(BaseModel):
    resource: str
    action: str

class RoleInfo(BaseModel):
    name: UserRole
    description: str
    permissions: List[str]

class UserInfo(BaseModel):
    id: str
    username: str
    email: str
    roles: List[UserRole]
    permissions: List[str]
    created_at: str
    last_login: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class HealthCheck(BaseModel):
    service: str
    status: str
    timestamp: str
    database: str = "unknown"

# RBAC Models
ROLES_PERMISSIONS = {
    UserRole.ADMIN: [
        "reports:create",
        "reports:read",
        "reports:update",
        "reports:delete",
        "reports:execute",
        "users:read",
        "users:write",
        "users:delete",
        "auth:manage",
    ],
    UserRole.MANAGER: [
        "reports:create",
        "reports:read",
        "reports:update",
        "reports:execute",
        "reports:delete",
        "users:read",
    ],
    UserRole.USER: [
        "reports:read",
        "reports:execute",
    ],
    UserRole.GUEST: [
        "reports:read",
    ],
}

RESOURCE_ACTIONS = {
    "reports": ["create", "read", "update", "delete", "execute"],
    "users": ["read", "write", "delete"],
    "auth": ["manage"],
}
