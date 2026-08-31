"""Security tests for JWT types, secret validation, session revocation."""

import pytest
from app.core.config import validate_secret_key
from app.core import security


def test_placeholder_secret_rejected():
    with pytest.raises(ValueError):
        validate_secret_key("your-super-secret-key-change-in-production")
    with pytest.raises(ValueError):
        validate_secret_key("short")
    with pytest.raises(ValueError):
        validate_secret_key("")
    # Strong secret accepted
    ok = validate_secret_key("a" * 32 + "bcdefghijklm")
    assert len(ok) >= 32


def test_access_vs_refresh_token_types(client):
    email = "tokentype@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    access = login.json()["access_token"]
    refresh = login.json()["refresh_token"]

    # access → protected OK
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 200

    # refresh → protected REJECT
    bad = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {refresh}"})
    assert bad.status_code == 401

    # refresh → refresh OK
    ok = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert ok.status_code == 200

    # access → refresh REJECT
    rej = client.post("/api/v1/auth/refresh", json={"refresh_token": access})
    assert rej.status_code == 401


def test_password_change_revokes_refresh(client):
    email = "revokesess@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    access = login.json()["access_token"]
    refresh = login.json()["refresh_token"]

    ch = client.post(
        "/api/v1/auth/change-password",
        headers={"Authorization": f"Bearer {access}"},
        json={"current_password": password, "new_password": "newpass99"},
    )
    assert ch.status_code == 200

    # old refresh rejected (token_version bump)
    old = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert old.status_code == 401

    # old access rejected
    me = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {access}"})
    assert me.status_code == 401

    # new login works
    login2 = client.post(
        "/api/v1/auth/login", json={"email": email, "password": "newpass99"}
    )
    assert login2.status_code == 200
    me2 = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {login2.json()['access_token']}"},
    )
    assert me2.status_code == 200


def test_cookie_refresh_without_body(client):
    email = "cookie@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert login.status_code == 200
    # Refresh using HttpOnly cookie only
    refreshed = client.post("/api/v1/auth/refresh", json={})
    assert refreshed.status_code == 200
    assert refreshed.json()["access_token"]
    me = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {refreshed.json()['access_token']}"},
    )
    assert me.status_code == 200
