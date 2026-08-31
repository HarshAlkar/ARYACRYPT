"""Upload size, history caps, and IDOR smoke tests."""

import io
import pytest
from app.core.config import settings


def test_history_limit_capped(client, auth_headers):
    headers, _ = auth_headers
    r = client.get("/api/v1/files/history?limit=9999", headers=headers)
    assert r.status_code == 200
    # Endpoint should succeed; server clamps limit internally
    assert isinstance(r.json(), list)


def test_content_length_over_limit_rejected(client, auth_headers, monkeypatch):
    headers, _ = auth_headers
    monkeypatch.setattr(settings, "MAX_UPLOAD_SIZE_BYTES", 64)
    # Import module binding after monkeypatch — files.py reads settings at call time via MAX_UPLOAD_SIZE
    import app.api.v1.endpoints.files as files_mod

    monkeypatch.setattr(files_mod, "MAX_UPLOAD_SIZE", 64)

    data = b"x" * 200
    r = client.post(
        "/api/v1/files/encrypt",
        headers={**headers, "Content-Length": str(len(data))},
        files={"file": ("big.bin", io.BytesIO(data), "application/octet-stream")},
        data={"password": "password1"},
    )
    assert r.status_code == 413


def test_idor_download_other_user(client, auth_headers):
    headers_a, _ = auth_headers
    # Second user
    email_b = "other@example.com"
    client.post("/api/v1/auth/register", json={"email": email_b, "password": "securepass1"})
    login_b = client.post(
        "/api/v1/auth/login", json={"email": email_b, "password": "securepass1"}
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    # Encrypt as A
    r = client.post(
        "/api/v1/files/encrypt",
        headers=headers_a,
        files={"file": ("a.txt", io.BytesIO(b"secret-a"), "text/plain")},
        data={"password": "password1"},
    )
    assert r.status_code == 200, r.text
    file_id = r.json()["id"]

    # B cannot download A's file
    denied = client.get(f"/api/v1/files/{file_id}/download", headers=headers_b)
    assert denied.status_code in (403, 404)
