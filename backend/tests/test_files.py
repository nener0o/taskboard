from app.models import Role
from tests.conftest import login, make_user


def _create(client, headers) -> int:
    response = client.post(
        "/api/tasks",
        json={"title": "Задача с файлом", "description": "вложение", "is_public": True},
        headers=headers,
    )
    assert response.status_code == 201, response.text
    return response.json()["id"]


def test_upload_download_and_delete(client):
    make_user("owner@example.com", Role.USER)
    make_user("other@example.com", Role.USER)
    owner, _ = login(client, "owner@example.com")
    other, _ = login(client, "other@example.com")
    task_id = _create(client, owner)

    bad = client.post(
        f"/api/tasks/{task_id}/files",
        files={"file": ("run.exe", b"MZ", "application/octet-stream")},
        headers=owner,
    )
    assert bad.status_code == 400

    huge = client.post(
        f"/api/tasks/{task_id}/files",
        files={"file": ("note.txt", b"a" * (5 * 1024 * 1024 + 1), "text/plain")},
        headers=owner,
    )
    assert huge.status_code == 400

    uploaded = client.post(
        f"/api/tasks/{task_id}/files",
        files={"file": ("note.txt", b"hello board", "text/plain")},
        headers=owner,
    )
    assert uploaded.status_code == 201, uploaded.text
    body = uploaded.json()
    assert body["size"] == len(b"hello board")
    listed = client.get(f"/api/tasks/{task_id}/files")
    assert listed.status_code == 200
    assert listed.json()[0]["original_name"] == "note.txt"

    download = client.get(body["download_url"].replace("http://testserver", ""))
    assert download.status_code == 200
    assert download.content == b"hello board"
    assert client.get(f"/api/files/{body['id']}/content", params={"token": "bad.1.bad"}).status_code == 403
    assert client.delete(f"/api/files/{body['id']}", headers=other).status_code == 403
    assert client.delete(f"/api/files/{body['id']}", headers=owner).status_code == 200
    assert client.get(f"/api/tasks/{task_id}/files").json() == []


def test_stranger_cannot_upload_to_foreign_task(client):
    make_user("owner@example.com", Role.USER)
    make_user("other@example.com", Role.USER)
    owner, _ = login(client, "owner@example.com")
    other, _ = login(client, "other@example.com")
    task_id = _create(client, owner)
    response = client.post(
        f"/api/tasks/{task_id}/files",
        files={"file": ("note.txt", b"no", "text/plain")},
        headers=other,
    )
    assert response.status_code == 403
