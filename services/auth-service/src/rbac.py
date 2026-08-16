from typing import List, Optional
from src.models import UserRole, ROLES_PERMISSIONS, RESOURCE_ACTIONS

class RBAC:
    """Sistema de controle de acesso baseado em roles (RBAC)."""
    
    @staticmethod
    def get_role_permissions(role: UserRole) -> List[str]:
        """
        Retorna as permissões de um role.
        
        Args:
            role: UserRole
            
        Returns:
            Lista de permissões
        """
        return ROLES_PERMISSIONS.get(role, [])
    
    @staticmethod
    def get_all_roles() -> List[dict]:
        """
        Retorna informações de todos os roles.
        
        Returns:
            Lista de dicts com informações dos roles
        """
        roles_info = []
        role_descriptions = {
            UserRole.ADMIN: "Administrador - Acesso total",
            UserRole.MANAGER: "Gerente - Acesso a gerenciamento",
            UserRole.USER: "Usuário - Acesso básico",
            UserRole.GUEST: "Convidado - Acesso limitado",
        }
        
        for role in UserRole:
            roles_info.append({
                "name": role.value,
                "description": role_descriptions.get(role, ""),
                "permissions": RBAC.get_role_permissions(role),
            })
        
        return roles_info
    
    @staticmethod
    def has_permission(
        user_roles: List[UserRole],
        resource: str,
        action: str,
    ) -> bool:
        """
        Verifica se o usuário tem permissão para uma ação em um recurso.
        
        Args:
            user_roles: Lista de roles do usuário
            resource: Nome do recurso (ex: 'reports')
            action: Nome da ação (ex: 'create')
            
        Returns:
            True se tem permissão
        """
        # Validar recurso
        if resource not in RESOURCE_ACTIONS:
            return False
        
        # Validar ação
        if action not in RESOURCE_ACTIONS[resource]:
            return False
        
        # Verificar se algum role tem permissão
        required_permission = f"{resource}:{action}"
        
        for role in user_roles:
            permissions = RBAC.get_role_permissions(role)
            if required_permission in permissions:
                return True
        
        return False
    
    @staticmethod
    def check_admin_only(user_roles: List[UserRole]) -> bool:
        """Verifica se é admin."""
        return UserRole.ADMIN in user_roles
    
    @staticmethod
    def check_manager_or_admin(user_roles: List[UserRole]) -> bool:
        """Verifica se é manager ou admin."""
        return UserRole.MANAGER in user_roles or UserRole.ADMIN in user_roles
    
    @staticmethod
    def get_user_permissions(user_roles: List[UserRole]) -> List[str]:
        """
        Retorna todas as permissões de um usuário com vários roles.
        
        Args:
            user_roles: Lista de roles do usuário
            
        Returns:
            Set de permissões
        """
        permissions = set()
        
        for role in user_roles:
            role_perms = RBAC.get_role_permissions(role)
            permissions.update(role_perms)
        
        return list(permissions)

class ResourcePermission:
    """Gerencia permissões por recurso."""
    
    @staticmethod
    def is_action_allowed(
        user_roles: List[UserRole],
        resource: str,
        action: str,
    ) -> tuple[bool, Optional[str]]:
        """
        Verifica se uma ação é permitida e retorna razão se negada.
        
        Args:
            user_roles: Roles do usuário
            resource: Recurso
            action: Ação
            
        Returns:
            (allowed, reason) tuple
        """
        if not RBAC.has_permission(user_roles, resource, action):
            required_perm = f"{resource}:{action}"
            return False, f"Permissão necessária: {required_perm}"
        
        return True, None
