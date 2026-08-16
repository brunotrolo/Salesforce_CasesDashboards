"""Tests for RBAC."""

import pytest
from src.rbac import RBAC, Role, Permission


def test_admin_has_all_permissions():
    """Testar que admin tem todas as permissões."""
    permissions = RBAC.get_permissions(["admin"])
    
    assert Permission.CREATE_REPORT in permissions
    assert Permission.DELETE_REPORT in permissions
    assert Permission.MANAGE_USERS in permissions


def test_viewer_has_limited_permissions():
    """Testar que viewer tem permissões limitadas."""
    permissions = RBAC.get_permissions(["viewer"])
    
    assert Permission.READ_REPORT in permissions
    assert Permission.CREATE_REPORT not in permissions
    assert Permission.DELETE_REPORT not in permissions


def test_has_permission():
    """Testar verificação de permissão."""
    assert RBAC.has_permission(["admin"], Permission.DELETE_REPORT)
    assert not RBAC.has_permission(["viewer"], Permission.DELETE_REPORT)


def test_require_permission_raises():
    """Testar que require_permission lança exceção."""
    with pytest.raises(PermissionError):
        RBAC.require_permission(["viewer"], Permission.DELETE_REPORT)
