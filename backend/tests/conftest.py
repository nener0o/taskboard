import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SEED_DEMO"] = "false"
os.environ["JWT_SECRET"] = "test-secret-key-for-labs-32bytes-min"
os.environ["BCRYPT_ROUNDS"] = "4"
os.environ["STORAGE_DIR"] = tempfile.mkdtemp(prefix="taskboard-")
os.environ["PUBLIC_BASE_URL"] = "http://testserver"
os.environ["FRONTEND_BASE_URL"] = "http://localhost:5173"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, SessionLocal, engine
from app.main import app
from app.models import Role, User
from app.security import hash_password


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client


def make_user(email: str, role: Role, password: str = "User12345", name: str | None = None) -> None:
    db = SessionLocal()
    db.add(User(name=name or email.split("@")[0], email=email, password_hash=hash_password(password), role=role))
    db.commit()
    db.close()


def login(client: TestClient, email: str, password: str = "User12345") -> tuple[dict, dict]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    body = response.json()
    return {"Authorization": f"Bearer {body['access_token']}"}, body
