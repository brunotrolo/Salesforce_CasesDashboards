"""Testes para RBAC (Role-Based Access Control)"""

import pytest

from src.rbac import RBAC, ResourcePermission
from src.models import UserRole


class TestRBAC:
    """Suite de testes para RBAC"""

    def test_get_role_permissions_admin(self, rbac):
        """Testa permissões do papel admin"""
        permissions = rbac.get_role_permissions(UserRole.ADMIN)

        assert permissions is not None
        assert len(permissions) > 0
        assert "reports:create" in permissions
        assert "users:write" in permissions

    def test_get_role_permissions_manager(self, rbac):
        """Testa permissões do papel manager"""
        permissions = rbac.get_role_permissions(UserRole.MANAGER)

        assert permissions is not None
        assert "reports:create" in permissions
        assert "reports:read" in permissions
        assert "reports:update" in permissions
        assert "users:read" in permissions

    def test_get_role_permissions_user(self, rbac):
        """Testa permissões do papel user"""
        permissions = rbac.get_role_permissions(UserRole.USER)

        assert permissions is not None
        assert "reports:read" in permissions
        assert "reports:execute" in permissions
        assert "reports:create" not in permissions

    def test_get_role_permissions_guest(self, rbac):
        """Testa permissões do papel guest"""
        permissions = rbac.get_role_permissions(UserRole.GUEST)

        assert permissions is not None
        assert "reports:read" in permissions
        assert len(permissions) <= len(rbac.get_role_permissions(UserRole.USER))

    def test_get_all_roles(self, rbac):
        """Testa obtenção de todos os papéis"""
        roles = rbac.get_all_roles()

        assert roles is not None
        assert len(roles) == 4  # ADMIN, MANAGER, USER, GUEST
        role_names = [r["name"] for r in roles]
        assert "admin" in role_names
        assert "manager" in role_names
        assert "user" in role_names
        assert "guest" in role_names

    def test_has_permission_admin(self, rbac):
        """Testa se admin tem permissão"""
        user_roles = [UserRole.ADMIN]

        assert rbac.has_permission(user_roles, "reports", "create")
        assert rbac.has_permission(user_roles, "users", "delete")
        assert not rbac.has_permission(user_roles, "unknown_resource", "read")

    def test_has_permission_manager(self, rbac):
        """Testa se manager tem permissões esperadas"""
        user_roles = [UserRole.MANAGER]

        assert rbac.has_permission(user_roles, "reports", "create")
        assert rbac.has_permission(user_roles, "reports", "read")
        assert rbac.has_permission(user_roles, "users", "read")
        assert not rbac.has_permission(user_roles, "users", "delete")

    def test_has_permission_user(self, rbac):
        """Testa se user tem permissões esperadas"""
        user_roles = [UserRole.USER]

        assert rbac.has_permission(user_roles, "reports", "read")
        assert rbac.has_permission(user_roles, "reports", "execute")
        assert not rbac.has_permission(user_roles, "reports", "create")
        assert not rbac.has_permission(user_roles, "users", "read")

    def test_has_permission_guest(self, rbac):
        """Testa se guest tem apenas leitura"""
        user_roles = [UserRole.GUEST]

        assert rbac.has_permission(user_roles, "reports", "read")
        assert not rbac.has_permission(user_roles, "reports", "create")
        assert not rbac.has_permission(user_roles, "reports", "execute")

    def test_has_permission_multiple_roles(self, rbac):
        """Testa permissão com múltiplos papéis"""
        user_roles = [UserRole.GUEST, UserRole.USER]

        # Deve ter permissão se algum papel tiver
        assert rbac.has_permission(user_roles, "reports", "read")
        assert rbac.has_permission(user_roles, "reports", "execute")

    def test_has_permission_invalid_action(self, rbac):
        """Testa ação inválida para recurso válido"""
        user_roles = [UserRole.ADMIN]

        assert not rbac.has_permission(user_roles, "reports", "fly")

    def test_check_admin_only_true(self, rbac):
        """Testa se é admin"""
        user_roles = [UserRole.ADMIN]

        assert rbac.check_admin_only(user_roles)

    def test_check_admin_only_false(self, rbac):
        """Testa se não é admin"""
        user_roles = [UserRole.MANAGER, UserRole.USER]

        assert not rbac.check_admin_only(user_roles)

    def test_check_manager_or_admin_with_manager(self, rbac):
        """Testa manager ou admin com manager"""
        user_roles = [UserRole.MANAGER]

        assert rbac.check_manager_or_admin(user_roles)

    def test_check_manager_or_admin_with_admin(self, rbac):
        """Testa manager ou admin com admin"""
        user_roles = [UserRole.ADMIN]

        assert rbac.check_manager_or_admin(user_roles)

    def test_check_manager_or_admin_with_user(self, rbac):
        """Testa manager ou admin com user"""
        user_roles = [UserRole.USER]

        assert not rbac.check_manager_or_admin(user_roles)

    def test_get_user_permissions(self, rbac):
        """Testa obtenção de todas as permissões do usuário"""
        user_roles = [UserRole.USER]

        permissions = rbac.get_user_permissions(user_roles)

        assert "reports:read" in permissions
        assert "reports:execute" in permissions

    def test_get_user_permissions_multiple_roles(self, rbac):
        """Testa permissões com múltiplos papéis"""
        user_roles = [UserRole.GUEST, UserRole.MANAGER]

        permissions = rbac.get_user_permissions(user_roles)

        # Deve conter união das permissões
        assert "reports:read" in permissions
        assert "reports:create" in permissions

    def test_resource_permission_is_action_allowed(self, rbac):
        """Testa ResourcePermission.is_action_allowed"""
        resource_perm = ResourcePermission()
        user_roles = [UserRole.MANAGER]

        allowed, reason = resource_perm.is_action_allowed(user_roles, "reports", "create")

        assert allowed
        assert reason is None

    def test_resource_permission_is_action_denied(self, rbac):
        """Testa ResourcePermission.is_action_allowed negado"""
        resource_perm = ResourcePermission()
        user_roles = [UserRole.USER]

        allowed, reason = resource_perm.is_action_allowed(user_roles, "reports", "create")

        assert not allowed
        assert "reports:create" in reason