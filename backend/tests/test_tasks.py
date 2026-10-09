from app.models import Role
from tests.conftest import login, make_user


def _task(title="Публичная задача команды", **extra):
    payload = {
        "title": title,
        "description": "Описание для поиска по тексту каталога",
        "status": "todo",
        "priority": "high",
        "is_public": True,
    }
    payload.update(extra)
    return payload


def test_crud_visibility_and_roles(client):
    make_user("user@example.com", Role.USER, name="Пользователь")
    make_user("manager@example.com", Role.MANAGER, name="Менеджер")
    make_user("admin@example.com", Role.ADMIN, name="Админ")
    user_headers, _ = login(client, "user@example.com")
    manager_headers, _ = login(client, "manager@example.com")
    admin_headers, _ = login(client, "admin@example.com")

    created = client.post("/api/tasks", json=_task(), headers=user_headers)
    assert created.status_code == 201, created.text
    task_id = created.json()["id"]
    assert client.get(f"/api/tasks/{task_id}").status_code == 200

    private = client.post("/api/tasks", json=_task("Скрытая задача", is_public=False), headers=user_headers)
    private_id = private.json()["id"]
    hidden = client.get(f"/api/tasks/{private_id}")
    assert hidden.status_code == 403

    forbidden = client.patch(f"/api/tasks/{task_id}", json={"title": "Чужое"}, headers=manager_headers)
    assert forbidden.status_code == 200
    user_forbidden = client.patch(
        f"/api/tasks/{private_id}",
        json={"title": "Не моя"},
        headers=login(client, "manager@example.com")[0],
    )
    assert user_forbidden.status_code == 200

    outsider_headers, _ = login(client, "admin@example.com")
    del outsider_headers
    other = client.post(
        "/api/auth/register",
        json={"name": "Другой", "email": "other@example.com", "password": "User12345"},
    )
    assert other.status_code == 201
    other_headers, _ = login(client, "other@example.com")
    assert client.patch(f"/api/tasks/{private_id}", json={"title": "Попытка"}, headers=other_headers).status_code == 403
    assert client.delete(f"/api/tasks/{task_id}", headers=user_headers).status_code == 403
    assert client.delete(f"/api/tasks/{private_id}", headers=manager_headers).status_code == 403
    assert client.delete(f"/api/tasks/{task_id}", headers=manager_headers).status_code == 403

    own_for_manager = client.post("/api/tasks", json=_task("Задача менеджера", is_public=False), headers=manager_headers)
    assert client.delete(f"/api/tasks/{own_for_manager.json()['id']}", headers=manager_headers).status_code == 200
    assert client.delete(f"/api/tasks/{private_id}", headers=admin_headers).status_code == 200
    assert client.get(f"/api/tasks/{private_id}").status_code == 404


def test_manager_can_edit_any_user_cannot_delete_own_only_update(client):
    make_user("owner@example.com", Role.USER)
    make_user("lead@example.com", Role.MANAGER)
    owner, _ = login(client, "owner@example.com")
    lead, _ = login(client, "lead@example.com")
    task_id = client.post("/api/tasks", json=_task("Общая", is_public=True), headers=owner).json()["id"]
    renamed = client.patch(f"/api/tasks/{task_id}", json={"title": "Новое имя"}, headers=owner)
    assert renamed.status_code == 200
    assert renamed.json()["title"] == "Новое имя"
    moderated = client.patch(f"/api/tasks/{task_id}", json={"is_public": False}, headers=lead)
    assert moderated.status_code == 200
    assert moderated.json()["is_public"] is False


def test_filters_sort_and_pagination(client):
    make_user("owner@example.com", Role.USER)
    headers, _ = login(client, "owner@example.com")
    for index, priority in enumerate(["low", "medium", "high"]):
        response = client.post(
            "/api/tasks",
            json=_task(f"Карточка {index}", priority=priority, description="фильтр каталога"),
            headers=headers,
        )
        assert response.status_code == 201
    client.post("/api/tasks", json=_task("Секрет", is_public=False, description="скрыто"), headers=headers)

    public = client.get("/api/tasks", params={"search": "карточка", "page_size": 2, "sort": "title", "order": "asc"})
    assert public.status_code == 200
    body = public.json()
    assert body["total"] == 3
    assert body["pages"] == 2
    assert len(body["items"]) == 2
    assert body["items"][0]["title"] == "Карточка 0"

    high = client.get("/api/tasks", params={"priority": "high"})
    assert high.json()["total"] == 1
    assert client.get("/api/tasks", params={"sort": "drop"}).status_code == 422

    mine = client.get("/api/tasks", params={"mine": True}, headers=headers)
    assert mine.json()["total"] == 4
    guest_mine = client.get("/api/tasks", params={"mine": True})
    assert guest_mine.status_code == 401


def test_archived_public_task_is_gone(client):
    make_user("owner@example.com", Role.USER)
    make_user("lead@example.com", Role.MANAGER)
    owner, _ = login(client, "owner@example.com")
    lead, _ = login(client, "lead@example.com")
    task_id = client.post("/api/tasks", json=_task(), headers=owner).json()["id"]
    archived = client.patch(f"/api/tasks/{task_id}", json={"status": "archived"}, headers=lead)
    assert archived.status_code == 200
    assert client.get(f"/api/tasks/{task_id}").status_code == 410
    assert client.get(f"/api/tasks/{task_id}", headers=owner).status_code == 200


def test_validation_and_missing(client):
    make_user("owner@example.com", Role.USER)
    headers, _ = login(client, "owner@example.com")
    assert client.post("/api/tasks", json={"title": "ab"}, headers=headers).status_code == 422
    assert client.get("/api/tasks/9999", headers=headers).status_code == 404
    assert client.patch("/api/tasks/9999", json={"title": "Нет"}, headers=headers).status_code == 404


def test_admin_changes_roles_user_cannot(client):
    make_user("admin@example.com", Role.ADMIN)
    make_user("user@example.com", Role.USER)
    admin, _ = login(client, "admin@example.com")
    user, _ = login(client, "user@example.com")
    denied = client.patch("/api/users/1/role", json={"role": "manager"}, headers=user)
    assert denied.status_code == 403
    users = client.get("/api/users", headers=admin).json()
    target = next(item for item in users if item["email"] == "user@example.com")
    changed = client.patch(f"/api/users/{target['id']}/role", json={"role": "manager"}, headers=admin)
    assert changed.status_code == 200
    assert changed.json()["role"] == "manager"
    self_change = client.patch(f"/api/users/{users[0]['id']}/role", json={"role": "user"}, headers=admin)
    assert self_change.status_code == 403
