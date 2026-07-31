"""Shared shell and authentication-interface tests."""

from pathlib import Path


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


def test_auth_story_grid_can_shrink_at_mobile_widths():
    stylesheet = Path("static/usiulostnfound.css").read_text(encoding="utf-8")
    assert "repeat(3, minmax(0, 1fr))" in stylesheet
    assert ".auth-layout > * {\n    min-width: 0;" in stylesheet
    assert ".auth-story-content {\n    min-width: 0;" in stylesheet
    assert ".auth-proof {\n        grid-template-columns: 1fr;" in stylesheet
