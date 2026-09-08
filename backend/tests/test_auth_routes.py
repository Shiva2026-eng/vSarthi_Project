def test_signup_success(client):
    payload = {
        "name": "New User",
        "email": "newuser@example.com",
        "password": "securepassword123",
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 201
    json_data = response.json()
    assert json_data["success"] is True
    assert "registered successfully" in json_data["message"]


def test_signup_duplicate_email(client, test_user):
    payload = {
        "name": "Duplicate User",
        "email": test_user.email,
        "password": "anotherpassword",
    }
    response = client.post("/auth/signup", json=payload)
    assert response.status_code == 403
    assert "already exists" in response.json()["detail"]


def test_login_success(client, test_user):
    # Form data for OAuth2 password flow
    data = {
        "username": test_user.email,
        "password": "testpassword123",
    }
    response = client.post("/auth/login", data=data)
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["message"] == "Successfully logged in"
    # Token must NOT be in the response body
    assert "access_token" not in json_data
    # Verify cookie is set
    assert "access_token" in response.cookies


def test_logout_success(client):
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
    # The set-cookie header should delete or expire access_token cookie
    assert "access_token" not in client.cookies or client.cookies.get("access_token") == ""


def test_auth_via_cookie(client, test_user):
    # Log in to receive the cookie in the test client
    data = {
        "username": test_user.email,
        "password": "testpassword123",
    }
    login_res = client.post("/auth/login", data=data)
    assert login_res.status_code == 200

    # Request /user/my_profile relying entirely on the cookie
    profile_res = client.get("/user/my_profile")
    assert profile_res.status_code == 200
    assert profile_res.json()["details"]["email"] == test_user.email


def test_login_wrong_password(client, test_user):
    data = {
        "username": test_user.email,
        "password": "wrongpassword",
    }
    response = client.post("/auth/login", data=data)
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]


def test_login_non_existent_user(client):
    data = {
        "username": "nonexistent@example.com",
        "password": "somepassword",
    }
    response = client.post("/auth/login", data=data)
    assert response.status_code == 404
    assert "No such user found" in response.json()["detail"]


def test_signup_and_login_case_insensitivity(client):
    # 1. Signup with mixed/upper case email
    payload = {
        "name": "Case Test User",
        "email": "ShivanshLavaniya456@Gmail.COM",
        "password": "password12345",
    }
    signup_res = client.post("/auth/signup", json=payload)
    assert signup_res.status_code == 201

    # 2. Trying to signup with lowercase version must fail with 403 Duplicate
    dup_payload = {
        "name": "Case Test User",
        "email": "shivanshlavaniya456@gmail.com",
        "password": "password12345",
    }
    dup_res = client.post("/auth/signup", json=dup_payload)
    assert dup_res.status_code == 403
    assert "already exists" in dup_res.json()["detail"]

    # 3. Login with all-caps email should succeed
    login_data = {
        "username": "SHIVANSHLAVANIYA456@GMAIL.COM",
        "password": "password12345",
    }
    login_res = client.post("/auth/login", data=login_data)
    assert login_res.status_code == 200
    assert login_res.json()["success"] is True
