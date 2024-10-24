from tests.conftest import USER_EMAIL, USER_PASSWORD, USERNAME


def test_create_user(client):
    data = {
        "username": USERNAME,
        "email": USER_EMAIL,
        "password": USER_PASSWORD,
        # "full_name": "Sanjeeb Subedi",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 201


def test_create_user_with_existing_email(client, unverified_user):
    data = {
        "username": "sanjeebsubedi2",
        "email": unverified_user.email,
        "password": USER_PASSWORD,
    }
    response = client.post("/users", json=data)
    assert response.status_code == 400


def test_create_user_with_invalid_email(client):
    data = {
        "username": "sanjeebsubedi2",
        "email": "sanjeeb.com",
        "password": USER_PASSWORD,
    }
    response = client.post("/users", json=data)
    assert response.status_code == 422


def test_create_user_with_empty_password(client):
    data = {"username": "Sanjeeb Subedi", "email": USER_EMAIL, "password": ""}
    response = client.post("/users", json=data)
    assert response.status_code == 422


def test_create_user_with_too_short_password(client):
    data = {
        "username": "sanjeebsubedi",
        "email": USER_EMAIL,
        "password": "and",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 422


def test_create_user_with_too_short_username(client):
    data = {
        "username": "sa",
        "email": USER_EMAIL,
        "password": "and",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 422


def test_create_user_with_existing_username(client, unverified_user):
    data = {
        "username": unverified_user.username,
        "email": "sanjeebsubedi2@gmail.com",
        "password": "abcd1234",
    }
    response = client.post("/users", json=data)
    assert response.status_code == 400
