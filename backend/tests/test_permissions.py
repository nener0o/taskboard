from app.models import Role
from app.permissions import ROLE_PERMISSIONS, has_permission


def test_user_cannot_delete_or_manage_roles():
    assert not has_permission(Role.USER, "task:delete_own")
    assert not has_permission(Role.USER, "task:delete_any")
    assert not has_permission(Role.USER, "user:manage_roles")
    assert has_permission(Role.USER, "task:update_own")


def test_manager_moderates_but_cannot_delete_foreign_or_change_roles():
    assert has_permission(Role.MANAGER, "task:delete_own")
    assert not has_permission(Role.MANAGER, "task:delete_any")
    assert has_permission(Role.MANAGER, "task:moderate")
    assert not has_permission(Role.MANAGER, "user:manage_roles")


def test_admin_has_every_permission():
    assert ROLE_PERMISSIONS[Role.ADMIN] >= ROLE_PERMISSIONS[Role.MANAGER]
    assert has_permission(Role.ADMIN, "user:manage_roles")
    assert has_permission(Role.ADMIN, "task:delete_any")


def test_matrix_endpoint(client):
    response = client.get("/api/meta/permissions")
    assert response.status_code == 200
    body = response.json()
    assert "task:read_public" in body["guest"]
    assert "user:manage_roles" in body["roles"]["admin"]
    assert "user:manage_roles" not in body["roles"]["user"]
