"""Smoke tests for the recovered application baseline."""

from route_helpers import is_allowed_image
from usiulostnfound_app import create_app


def test_home_redirects_guests_to_authentication():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})

    response = app.test_client().get("/")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/auth")


def test_authentication_page_loads_static_assets():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})

    response = app.test_client().get("/auth")

    assert response.status_code == 200
    assert b"usiulostnfound.css" in response.data
    assert b"usiulostnfound.js" in response.data


def test_role_protected_dashboards_enforce_access():
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})
    client = app.test_client()

    assert client.get("/student").status_code == 302
    assert client.get("/security").status_code == 302

    with client.session_transaction() as session:
        session["role"] = "student"

    assert client.get("/student").status_code == 200
    assert client.get("/security").status_code == 403


def test_allowed_image_extensions_are_case_insensitive():
    for filename in ("item.png", "item.JPG", "item.jpeg", "item.webp", "item.gif"):
        assert is_allowed_image(filename)

    for filename in ("", "no-extension", "item.exe", "item.png.exe"):
        assert not is_allowed_image(filename)
