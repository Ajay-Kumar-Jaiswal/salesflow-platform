def test_registration_success(client):
    payload = {
        "name": "Sarah Connor",
        "email": "sarah@cyberdyne.com",
        "password": "Password123!",
        "role": "SALES_REP"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sarah Connor"
    assert data["email"] == "sarah@cyberdyne.com"
    assert data["role"] == "SALES_REP"
    assert "hashed_password" not in data


def test_registration_duplicate_email(client, sales_rep_user):
    payload = {
        "name": "Alex Duplicate",
        "email": sales_rep_user.email,
        "password": "Password123!",
        "role": "SALES_REP"
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


def test_registration_validation_error(client):
    payload = {
        "name": "",
        "email": "not-an-email",
        "password": "123"  # too short
    }
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client, sales_rep_user):
    payload = {
        "email": "alex@salesflow.com",
        "password": "RepPass123!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "alex@salesflow.com"


def test_login_invalid_password(client, sales_rep_user):
    payload = {
        "email": "alex@salesflow.com",
        "password": "WrongPassword!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["detail"]


def test_login_nonexistent_user(client):
    payload = {
        "email": "nobody@nowhere.com",
        "password": "SomePassword!"
    }
    response = client.post("/api/auth/login", json=payload)
    assert response.status_code == 401


def test_get_me_authorized(client, sales_rep_user, rep_headers):
    response = client.get("/api/auth/me", headers=rep_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == sales_rep_user.id
    assert data["email"] == sales_rep_user.email


def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_admin_rbac_on_users(client, admin_headers, rep_headers, sales_rep_user):
    # Sales rep cannot delete users
    rep_del = client.delete(f"/api/users/{sales_rep_user.id}", headers=rep_headers)
    assert rep_del.status_code == 403

    # Admin can list users
    admin_list = client.get("/api/users", headers=admin_headers)
    assert admin_list.status_code == 200
    assert len(admin_list.json()) >= 1
