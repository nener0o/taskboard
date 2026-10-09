from app.models import Role
from tests.conftest import login, make_user


def test_register_and_reject_bad_password(client):
    ok = client.post(
        "/api/auth/register",
        json={"name": "Анна", "email": "anna@example.com", "password": "User12345"},
    )
    assert ok.status_code == 201
    assert ok.json()["role"] == "user"
    assert "password" not in ok.json()

    short = client.post(
        "/api/auth/register",
        json={"name": "Анна", "email": "other@example.com", "password": "123"},
    )
    assert short.status_code == 422

    duplicate = client.post(
        "/api/auth/register",
        json={"name": "Анна", "email": "anna@example.com", "password": "User12345"},
    )
    assert duplicate.status_code == 409


def test_login_failures_and_me(client):
    make_user("ivan@example.com", Role.USER)
    bad = client.post("/api/auth/login", json={"email": "ivan@example.com", "password": "Wrong123"})
    assert bad.status_code == 401
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-token"}).status_code == 401
    headers, _tokens = login(client, "ivan@example.com")
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == "ivan@example.com"
    assert "task:create" in me.json()["permissions"]


def test_refresh_rotation_logout_and_reuse(client):
    make_user("session@example.com", Role.USER)
    _headers, first = login(client, "session@example.com")
    refreshed = client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert refreshed.status_code == 200
    second = refreshed.json()
    assert second["access_token"]
    assert second["refresh_token"] != first["refresh_token"]

    reused = client.post("/api/auth/refresh", json={"refresh_token": first["refresh_token"]})
    assert reused.status_code == 401
    blocked = client.post("/api/auth/refresh", json={"refresh_token": second["refresh_token"]})
    assert blocked.status_code == 401

    _headers, fresh = login(client, "session@example.com")
    logout = client.post("/api/auth/logout", json={"refresh_token": fresh["refresh_token"]})
    assert logout.status_code == 200
    after = client.post("/api/auth/refresh", json={"refresh_token": fresh["refresh_token"]})
    assert after.status_code == 401


def test_protected_route_rejects_missing_token(client):
    response = client.post("/api/tasks", json={"title": "Без входа задача"})
    assert response.status_code == 401
