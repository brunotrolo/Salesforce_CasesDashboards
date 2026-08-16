"""
Auth Service
Gerenciamento centralizado de autenticação e autorização.
"""

from .auth_manager import AuthManager
from .jwt_handler import JWTHandler
from .rbac import RBACManager

__version__ = "0.1.0"

__all__ = [
    "AuthManager",
    "JWTHandler",
    "RBACManager",
]
