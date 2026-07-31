"""Authentication validation and session tests."""

import pytest
from werkzeug.security import check_password_hash


VALID_SIGNUP = {
    "role_selection": "student",
    "full_name": "Amina Noor",
    "email": "amina@usiu.ac.ke",
    "user_id": "321654",
    "password": "Strong@123",
}


def test_valid_signup_hashes_password_and_starts_session(client, database):
    response = client.post("/signup", data=VALID_SIGNUP)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/student")
    account = database.execute(
        "SELECT * FROM users WHERE user_id = '321654'"
    ).fetchone()
    assert account is not None
    assert account["password"] != VALID_SIGNUP["password"]
    assert check_password_hash(account["password"], VALID_SIGNUP["password"])
    with client.session_transaction() as session:
        assert session["role"] == "student"
        assert session["user_name"] == "Amina Noor"


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("email", "amina@gmail.com", b"@usiu.ac.ke"),
        ("user_id", "12345", b"exactly 6 digits"),
        ("user_id", "abcdef", b"exactly 6 digits"),
        ("password", "weakpass", b"uppercase"),
        ("role_selection", "admin", b"valid student or security role"),
    ],
)
def test_signup_rejects_invalid_credentials(client, field, value, message):
    data = {**VALID_SIGNUP, field: value}
    response = client.post("/signup", data=data, follow_redirects=True)

    assert response.status_code == 200
    assert message in response.data


def test_signup_rejects_duplicate_user_id(client):
    client.post("/signup", data=VALID_SIGNUP)
    client.get("/logout")

    response = client.post("/signup", data=VALID_SIGNUP, follow_redirects=True)

    assert b"already exists" in response.data


def test_security_signup_requires_nine_digits(client):
    data = {
        **VALID_SIGNUP,
        "role_selection": "security",
        "user_id": "123456",
    }
    response = client.post("/signup", data=data, follow_redirects=True)
    assert b"exactly 9 digits" in response.data


def test_correct_login_succeeds(client, add_user):
    add_user()
    response = client.post(
        "/login",
        data={
            "role_selection": "student",
            "user_id": "100200",
            "password": "Student@123",
        },
    )
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/student")


@pytest.mark.parametrize(
    ("role", "password"),
    [("security", "Student@123"), ("student", "Wrong@123")],
)
def test_login_rejects_wrong_role_or_password(client, add_user, role, password):
    add_user()
    response = client.post(
        "/login",
        data={"role_selection": role, "user_id": "100200", "password": password},
        follow_redirects=True,
    )
    assert b"Invalid credentials or account role" in response.data


def test_logout_clears_complete_session(client, login_as):
    login_as()
    response = client.get("/logout")
    assert response.status_code == 302
    with client.session_transaction() as session:
        assert "role" not in session
        assert "user_id" not in session
        assert "user_name" not in session
