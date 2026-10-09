from app.models import Role
from tests.conftest import login, make_user


def test_business_flow(client, monkeypatch):
    """Сквозной сценарий: вход, роли, CRUD, фильтры, файл и отказ внешнего API."""
    make_user("admin@example.com", Role.ADMIN, name="Админ")
    make_user("manager@example.com", Role.MANAGER, name="Менеджер")
    user_headers, tokens = login(client, "admin@example.com")
    # Админ заводит обычного пользователя через регистрацию, затем повышает менеджера не требуется.
    registered = client.post(
        "/api/auth/register",
        json={"name": "Ира", "email": "ira@example.com", "password": "User12345"},
    )
    assert registered.status_code == 201
    user_headers, tokens = login(client, "ira@example.com")
    manager_headers, _ = login(client, "manager@example.com")

    created = client.post(
        "/api/tasks",
        json={
            "title": "Подготовить отчёт",
            "description": "сводка по задачам спринта",
            "priority": "high",
            "status": "todo",
            "is_public": True,
        },
        headers=user_headers,
    )
    assert created.status_code == 201
    task_id = created.json()["id"]

    listing = client.get("/api/tasks", params={"search": "отчёт", "priority": "high", "sort": "priority", "order": "desc"})
    assert listing.json()["total"] == 1

    updated = client.patch(f"/api/tasks/{task_id}", json={"status": "in_progress"}, headers=user_headers)
    assert updated.json()["status"] == "in_progress"
    assert client.delete(f"/api/tasks/{task_id}", headers=user_headers).status_code == 403
    assert client.patch(f"/api/tasks/{task_id}", json={"priority": "low"}, headers=manager_headers).status_code == 200

    uploaded = client.post(
        f"/api/tasks/{task_id}/files",
        files={"file": ("report.txt", "готово".encode(), "text/plain")},
        headers=user_headers,
    )
    assert uploaded.status_code == 201
    download = client.get(uploaded.json()["download_url"].replace("http://testserver", ""))
    assert download.content == "готово".encode()

    refreshed = client.post("/api/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert refreshed.status_code == 200
    client.post("/api/auth/logout", json={"refresh_token": refreshed.json()["refresh_token"]})
    assert client.post("/api/auth/refresh", json={"refresh_token": refreshed.json()["refresh_token"]}).status_code == 401

    from app.services import WeatherService

    monkeypatch.setattr(
        "app.deps._weather",
        WeatherService(fetcher=lambda: (_ for _ in ()).throw(Exception("network")) if False else None),
    )

    def explode():
        raise __import__("httpx").ConnectError("offline")

    monkeypatch.setattr("app.deps._weather", WeatherService(fetcher=explode, clock=lambda: 3))
    weather = client.get("/api/integrations/weather")
    assert weather.status_code == 200
    assert weather.json()["available"] is False
