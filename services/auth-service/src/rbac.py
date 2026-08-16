"""
Role-Based Access Control (RBAC).
"""

from typing import List, Set
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class Role(str, Enum):
    """Roles disponíveis."""
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
    ANALYST = "analyst"


class Permission(str, Enum):
    """Permissões disponíveis."""
    # Report operations
    CREATE_REPORT = "create_report"
    READ_REPORT = "read_report"
    UPDATE_REPORT = "update_report"
    DELETE_REPORT = "delete_report"
    
    # User management
    MANAGE_USERS = "manage_users"
    VIEW_LOGS = "view_logs"
    MANAGE_ROLES = "manage_roles"


# Mapeamento Role -> Permissions
ROLE_PERMISSIONS: dict = {
    Role.ADMIN: {
        Permission.CREATE_REPORT,
        Permission.READ_REPORT,
        Permission.UPDATE_REPORT,
        Permission.DELETE_REPORT,
        Permission.MANAGE_USERS,
        Permission.VIEW_LOGS,
        Permission.MANAGE_ROLES,
    },
    Role.ANALYST: {
        Permission.CREATE_REPORT,
        Permission.READ_REPORT,
        Permission.UPDATE_REPORT,
        Permission.DELETE_REPORT,
        Permission.VIEW_LOGS,
    },
    Role.USER: {
        Permission.CREATE_REPORT,
        Permission.READ_REPORT,
        Permission.UPDATE_REPORT,
    },
    Role.VIEWER: {
        Permission.READ_REPORT,
    },
}


class RBAC:
    """Role-Based Access Control."""

    @staticmethod
    def get_permissions(roles: List[str]) -> Set[str]:
        """
        Obter permissões para um conjunto de roles.
        
        Args:
            roles: Lista de roles
            
        Returns:
            Set de permissões
        """
        permissions = set()
        
        for role_name in roles:
            try:
                role = Role[role_name.upper()]
                permissions.update(ROLE_PERMISSIONS.get(role, set()))
            except KeyError:
                logger.warning(f"Unknown role: {role_name}")

        return permissions

    @staticmethod
    def has_permission(roles: List[str], permission: str) -> bool:
        """
        Verificar se roles têm permissão específica.
        
        Args:
            roles: Lista de roles do usuário
            permission: Permissão a verificar
            
        Returns:
            True se tem permissão
        """
        permissions = RBAC.get_permissions(roles)
        return permission in permissions

    @staticmethod
    def require_permission(roles: List[str], permission: str) -> None:
        """
        Exigir permissão, lançar exceção se não tiver.
        
        Args:
            roles: Lista de roles
            permission: Permissão requerida
            
        Raises:
            PermissionError: Se não tem permissão
        """
        if not RBAC.has_permission(roles, permission):
            logger.warning(
                f"Permission denied",
                extra={"required": permission, "roles": roles}
            )
            raise PermissionError(f"Permission denied: {permission}")
