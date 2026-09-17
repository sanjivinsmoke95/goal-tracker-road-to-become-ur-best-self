from tests.conftest import register_and_login


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_creates_user(client):
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "password123", "full_name": "A"})
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "a@b.com"
    assert body["is_active"] is True
    assert "id" in body
    assert "hashed_password" not in body  # never leak the hash


def test_duplicate_email_rejected(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    assert r.status_code == 409


def test_short_password_rejected(client):
    r = client.post("/auth/register", json={"email": "a@b.com", "password": "short"})
    assert r.status_code == 422


def test_login_and_me(client):
    headers = register_and_login(client)
    r = client.get("/auth/me", headers=headers)
    assert r.status_code == 200
    assert r.json()["email"] == "dev@example.com"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "a@b.com", "password": "password123"})
    r = client.post("/auth/login", json={"email": "a@b.com", "password": "wrongpass1"})
    assert r.status_code == 401


def test_me_requires_auth(client):
    assert client.get("/auth/me").status_code in (401, 403)


def test_me_rejects_bad_token(client):
    r = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert r.status_code == 401
