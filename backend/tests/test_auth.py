def test_register_and_login(client):
    email = "user1@example.com"
    password = "password123"

    r = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert r.status_code == 200
    body = r.json()
    assert body["email"] == email
    assert "id" in body

    dup = client.post("/api/v1/auth/register", json={"email": email, "password": password})
    assert dup.status_code == 400

    bad = client.post("/api/v1/auth/login", json={"email": email, "password": "wrongpass"})
    assert bad.status_code == 401

    ok = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert ok.status_code == 200
    tokens = ok.json()
    assert tokens["access_token"]
    assert tokens["refresh_token"]
    assert tokens["token_type"] == "bearer"


def test_me_change_password_and_email(client):
    email = "profile@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    me = client.get("/api/v1/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    pwd = client.post(
        "/api/v1/auth/change-password",
        headers=headers,
        json={"current_password": password, "new_password": "newpass99"},
    )
    assert pwd.status_code == 200

    # Old password fails
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": password}).status_code
        == 401
    )
    # New password works
    assert (
        client.post("/api/v1/auth/login", json={"email": email, "password": "newpass99"}).status_code
        == 200
    )

    login2 = client.post("/api/v1/auth/login", json={"email": email, "password": "newpass99"})
    headers2 = {"Authorization": f"Bearer {login2.json()['access_token']}"}
    upd = client.patch("/api/v1/auth/me", headers=headers2, json={"email": "renamed@example.com"})
    assert upd.status_code == 200
    assert upd.json()["email"] == "renamed@example.com"


def test_refresh_and_logout_revocation(client):
    email = "refresh@example.com"
    password = "password123"
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    login = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    refresh = login.json()["refresh_token"]

    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert rotated.status_code == 200
    new_refresh = rotated.json()["refresh_token"]

    # Old refresh should be revoked after rotation
    reused = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh})
    assert reused.status_code == 401

    logout = client.post("/api/v1/auth/logout", json={"refresh_token": new_refresh})
    assert logout.status_code == 200

    after_logout = client.post("/api/v1/auth/refresh", json={"refresh_token": new_refresh})
    assert after_logout.status_code == 401
