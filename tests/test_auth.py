def test_user_registration(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "new_recruiter@company.com",
            "full_name": "New Recruiter",
            "password": "SecurePassword123!",
            "role": "recruiter"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new_recruiter@company.com"
    assert data["full_name"] == "New Recruiter"
    assert "id" in data

def test_duplicate_user_registration_fails(client, test_user):
    response = client.post(
        "/api/auth/register",
        json={
            "email": test_user.email,
            "full_name": "Duplicate Person",
            "password": "Password123!"
        }
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()

def test_user_login_success(client, test_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "Password123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == test_user.email

def test_user_login_invalid_password(client, test_user):
    response = client.post(
        "/api/auth/login",
        json={
            "email": test_user.email,
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()

def test_protected_route_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_protected_route_with_token(client, auth_headers):
    response = client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test_recruiter@company.com"
