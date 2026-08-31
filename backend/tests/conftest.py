import os
import tempfile
from pathlib import Path

# Must set env before app imports Settings
# Strong test secret (>=32 chars, not a forbidden placeholder fragment)
os.environ.setdefault(
    "SECRET_KEY",
    "pytest-only-strong-secret-key-32b-ok-xxxxxxxx",
)
os.environ.setdefault("POSTGRES_SERVER", "localhost")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "aryacrypt_test")
os.environ.setdefault("BACKEND_CORS_ORIGINS", "http://localhost:5173")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.api.deps import get_db
from app.main import app
from app.core.config import settings

# Isolated upload dir for each test session
_UPLOAD = tempfile.mkdtemp(prefix="aryacrypt_test_uploads_")
settings.UPLOAD_DIR = _UPLOAD


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db_session):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture()
def auth_headers(client):
    email = "vault@example.com"
    password = "securepass1"
    reg = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert reg.status_code == 200, reg.text
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, login.json()
