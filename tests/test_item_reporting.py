"""Finder-reporting permissions, validation, privacy, and upload tests."""

from io import BytesIO
from pathlib import Path

import pytest

import usiulostnfound_database as database_module
from usiulostnfound_app import create_app


VALID_ITEM = {
    "category": "Electronics",
    "description": "Silver USB-C charger",
    "identifier": "Initials AN under the plug",
    "location": "SAC cafeteria",
    "date": "2026-07-27",
    "finder_contact": "amina@usiu.ac.ke",
}


@pytest.fixture()
def app(tmp_path, monkeypatch):
    database_path = tmp_path / "member_05.db"
    monkeypatch.setattr(database_module, "DATABASE_PATH", database_path)
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "member-05-test-secret",
            "DATABASE_PATH": str(database_path),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def database():
    connection = database_module.get_connection()
    yield connection
    connection.close()


@pytest.fixture()
def login_as(client):
    def _login(role="student", user_id="100200", name="Jane Wanjiru"):
        with client.session_transaction() as session:
            session.update(role=role, user_id=user_id, user_name=name)

    return _login


def flashed_messages(client):
    """Return messages queued by the backend without depending on a template."""
    with client.session_transaction() as session:
        return [message for _category, message in session.get("_flashes", [])]


def test_guest_is_redirected_and_security_role_is_forbidden(client, login_as):
    guest_response = client.post("/items/report", data=VALID_ITEM)
    assert guest_response.status_code == 302
    assert "/auth" in guest_response.headers["Location"]

    login_as("security", "123456789", "Security Officer")
    assert client.post("/items/report", data=VALID_ITEM).status_code == 403


def test_student_can_report_item_with_pending_status(client, login_as, database):
    login_as()
    response = client.post("/items/report", data=VALID_ITEM)

    assert response.status_code == 302
    item = database.execute(
        "SELECT * FROM items WHERE description = ?",
        (VALID_ITEM["description"],),
    ).fetchone()
    assert item is not None
    assert item["status"] == "Pending Security"
    assert item["identifier"] == VALID_ITEM["identifier"]
    assert item["contact"] == VALID_ITEM["finder_contact"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("category", "", b"Select a valid item category"),
        ("category", "Vehicles", b"Select a valid item category"),
        ("description", "", b"Complete every required field"),
        ("identifier", "", b"Complete every required field"),
        ("location", "", b"Complete every required field"),
        ("date", "", b"Complete every required field"),
        ("finder_contact", "", b"Complete every required field"),
    ],
)
def test_report_rejects_invalid_or_missing_fields(
    client,
    login_as,
    database,
    field,
    value,
    message,
):
    login_as()
    response = client.post(
        "/items/report",
        data={**VALID_ITEM, field: value},
    )

    assert response.status_code == 302
    assert any(
        message.decode() in flashed_message
        for flashed_message in flashed_messages(client)
    )
    assert database.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0


def test_report_rejects_non_image_upload(client, login_as, app, database):
    login_as()
    response = client.post(
        "/items/report",
        data={
            **VALID_ITEM,
            "item_photo": (BytesIO(b"not an image"), "notes.txt"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 302
    assert any(
        message.startswith("Upload a PNG") for message in flashed_messages(client)
    )
    assert not list(Path(app.config["UPLOAD_FOLDER"]).glob("*"))
    assert database.execute("SELECT COUNT(*) FROM items").fetchone()[0] == 0


def test_valid_uploads_use_unique_sanitized_relative_paths(
    client,
    login_as,
    app,
    database,
):
    login_as()
    for suffix in ("one", "two"):
        response = client.post(
            "/items/report",
            data={
                **VALID_ITEM,
                "description": f"Charger {suffix}",
                "item_photo": (
                    BytesIO(b"\x89PNG\r\n\x1a\n"),
                    "../../photo.png",
                ),
            },
            content_type="multipart/form-data",
        )
        assert response.status_code == 302

    upload_folder = Path(app.config["UPLOAD_FOLDER"])
    uploaded_files = list(upload_folder.glob("*_photo.png"))
    assert len(uploaded_files) == 2
    assert uploaded_files[0].name != uploaded_files[1].name

    stored_paths = database.execute(
        "SELECT image_path FROM items ORDER BY id"
    ).fetchall()
    assert all(row["image_path"].startswith("uploads/") for row in stored_paths)
    assert all(".." not in row["image_path"] for row in stored_paths)


def test_public_dashboard_does_not_expose_private_report_details(
    client,
    login_as,
    database,
):
    login_as()
    client.post("/items/report", data=VALID_ITEM)

    response = client.get("/student")

    assert VALID_ITEM["description"].encode() in response.data
    assert VALID_ITEM["identifier"].encode() not in response.data
    assert VALID_ITEM["finder_contact"].encode() not in response.data
