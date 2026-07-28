"""Shared shell and authentication-interface tests."""


def test_authentication_page_contains_complete_forms(client):
    response = client.get("/auth")
    page = response.data

    assert response.status_code == 200
    for field in (
        b'form action="/login"',
        b'form action="/signup"',
        b'name="role_selection"',
        b'name="full_name"',
        b'name="email"',
        b'name="user_id"',
        b'name="password"',
    ):
        assert field in page


def test_shared_shell_loads_named_assets_and_skip_link(client):
    page = client.get("/auth").data
    assert b"usiulostnfound.css" in page
    assert b"usiulostnfound.js" in page
    assert b"Skip to main content" in page
    assert b'id="main-content"' in page


def test_auth_role_controls_expose_id_guidance_hooks(client):
    page = client.get("/auth").data
    assert b'adjustIDPlaceholder(\'login-role\', \'login-id\')' in page
    assert b'adjustIDPlaceholder(\'reg-role\', \'reg-id\')' in page
    assert b"togglePasswordVisibility" in page
