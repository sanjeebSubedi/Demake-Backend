import pytest
from conftest import USER_EMAIL, USER_PASSWORD


def test_successful_login(client, verified_user):
    response = client.post(
        "/auth/login",
        data={
            "username": verified_user.email,
            "password": USER_PASSWORD,
        },
    )
    assert response.status_code == 200


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("wrongemail@gmail.com", USER_PASSWORD, 401),
        (USER_EMAIL, "wrongpassword", 401),
        ("wrongemail@gmail.com", "wrongpassword", 401),
    ],
)
def test_unsuccessful_login(client, verified_user, email, password, status_code):
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )
    assert response.status_code == status_code
