"""Cross-role route authorization tests."""

import pytest


@pytest.mark.parametrize(
    "path",
    [
        "/student",
        "/items",
        "/security",
    ],
)
def test_guests_are_redirected_to_authentication(client, path):
    response = client.get(path)
    assert response.status_code == 302
    assert "/auth" in response.headers["Location"]


def test_student_cannot_open_security_dashboard(client, login_as):
    login_as("student")
    assert client.get("/security").status_code == 403


def test_security_cannot_open_student_dashboard(client, login_as):
    login_as("security", "123456789", "Security Officer")
    assert client.get("/student").status_code == 403


def test_root_routes_authenticated_users_to_correct_workspace(client, login_as):
    login_as("student")
    assert client.get("/").headers["Location"].endswith("/student")

    login_as("security", "123456789", "Security Officer")
    assert client.get("/").headers["Location"].endswith("/security")
