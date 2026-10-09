import httpx
import pytest

from app.models import Role
from app.services import WeatherService
from tests.conftest import login, make_user


def test_robots_sitemap_and_html_statuses(client):
    make_user("owner@example.com", Role.USER)
    headers, _ = login(client, "owner@example.com")
    task_id = client.post(
        "/api/tasks",
        json={"title": "Индексируемая задача", "description": "Текст для сниппета", "is_public": True},
        headers=headers,
    ).json()["id"]

    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert "Sitemap:" in robots.text
    assert "Disallow: /app" in robots.text

    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    assert f"/tasks/{task_id}" in sitemap.text
    assert "application/xml" in sitemap.headers["content-type"]

    page = client.get(f"/pages/tasks/{task_id}")
    assert page.status_code == 200
    assert "<h1>" in page.text
    assert "application/ld+json" in page.text
    assert 'rel="canonical"' in page.text
    assert client.get("/pages/tasks/9999").status_code == 404

    client.patch(f"/api/tasks/{task_id}", json={"status": "archived"}, headers=headers)
    assert client.get(f"/pages/tasks/{task_id}").status_code == 410


def test_weather_normalizes_retries_and_degrades():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] == 1:
            raise httpx.TimeoutException("timeout")
        return {"temperature_c": 4, "weather_code": 2}

    service = WeatherService(fetcher=flaky, clock=lambda: 50)
    result = service.current()
    assert calls["n"] == 2
    assert result.available is True
    assert result.temperature_c == 4
    assert result.summary == "Переменная облачность"
    assert service.current().temperature_c == 4

    def down():
        raise httpx.ConnectError("down")

    failed = WeatherService(fetcher=down, clock=lambda: 5)
    fallback = failed.current()
    assert fallback.available is False
    with pytest.raises(Exception):
        failed.current()


def test_weather_endpoint_uses_adapter(client, monkeypatch):
    service = WeatherService(fetcher=lambda: {"temperature_c": -2, "weather_code": 71}, clock=lambda: 10)
    monkeypatch.setattr("app.deps._weather", service)
    response = client.get("/api/integrations/weather")
    assert response.status_code == 200
    assert response.json()["summary"] == "Снег"
    assert response.json()["location"] == "Москва"


def test_graphql_one_query_and_auth(client):
    make_user("owner@example.com", Role.USER, name="Ольга")
    headers, _ = login(client, "owner@example.com")
    created = client.post(
        "/api/tasks",
        json={"title": "Задача GraphQL", "description": "поля", "is_public": True, "status": "todo"},
        headers=headers,
    )
    assert created.status_code == 201

    query = """
    query {
      users { id name email tasks { id title userId } }
      tasks { id title }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200, response.text
    payload = response.json()
    assert "errors" not in payload
    assert any(task["title"] == "Задача GraphQL" for task in payload["data"]["tasks"])
    owner = payload["data"]["users"][0]
    assert owner["tasks"][0]["title"] == "Задача GraphQL"

    denied = client.post(
        "/graphql",
        json={"query": 'mutation { createTask(title: "Слишком коротко нет") { id } }'},
    )
    assert denied.json()["errors"]

    allowed = client.post(
        "/graphql",
        json={"query": 'mutation { createTask(title: "Из GraphQL") { id title } }'},
        headers=headers,
    )
    assert "errors" not in allowed.json(), allowed.text
    assert allowed.json()["data"]["createTask"]["title"] == "Из GraphQL"
