"""Available-item search and ownership-claim service tests."""

import pytest

import usiulostnfound_database as database_module
from usiulostnfound_app import create_app


@pytest.fixture()
def app(tmp_path, monkeypatch):
    database_path = tmp_path / "claims.db"
    monkeypatch.setattr(database_module, "DATABASE_PATH", database_path)
    return create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "claims-test-secret",
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


@pytest.fixture()
def add_item():
    def _add_item(
        status="Checked-In",
        category="Electronics",
        description="Black smartphone",
    ):
        connection = database_module.get_connection()
        try:
            cursor = connection.execute(
                """
                INSERT INTO items (
                    category, description, identifier, location, date,
                    contact, image_path, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    category,
                    description,
                    "PRIVATE-IMEI-1234",
                    "Library",
                    "2026-07-27",
                    "private@usiu.ac.ke",
                    None,
                    status,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    return _add_item


VALID_CLAIM = {
    "claimed_item": "Black smartphone",
    "proof_identifier": "IMEI ends 1234",
    "owner_contact": "0711111111",
}


def test_item_routes_require_student_role(client, login_as):
    assert client.get("/items").status_code == 302

    login_as("security", "123456789", "Security Officer")
    assert client.get("/items").status_code == 403
    assert client.post("/claims", data=VALID_CLAIM).status_code == 403


def test_available_items_hide_claimed_records_and_private_fields(
    client,
    login_as,
    add_item,
):
    visible_id = add_item("Checked-In", description="Visible phone")
    add_item("Claimed", description="Returned wallet")
    login_as()

    response = client.get("/items")

    assert response.status_code == 200
    assert b"Visible phone" in response.data
    assert b"Returned wallet" not in response.data
    assert str(visible_id).encode() in response.data
    assert b"PRIVATE-IMEI-1234" not in response.data
    assert b"private@usiu.ac.ke" not in response.data


def test_category_filter_returns_only_recognised_matching_items(
    client,
    login_as,
    add_item,
):
    add_item(category="Electronics", description="Phone")
    add_item(category="Books", description="Textbook")
    login_as()

    matching = client.get("/items?category=Books")
    invalid = client.get("/items?category=Books%27%20OR%201=1--")

    assert b"Textbook" in matching.data
    assert b"Phone" not in matching.data
    assert b"Textbook" in invalid.data
    assert b"Phone" in invalid.data


def test_valid_claim_is_created_pending(client, login_as, add_item, database):
    item_id = add_item()
    login_as()

    response = client.post(
        "/claims",
        data={**VALID_CLAIM, "item_id": str(item_id)},
    )

    assert response.status_code == 302
    claim = database.execute("SELECT * FROM claims").fetchone()
    assert claim["item_id"] == item_id
    assert claim["claimed_item"] == "Black smartphone"
    assert claim["status"] == "Pending"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("item_id", ""),
        ("item_id", "not-a-number"),
        ("claimed_item", ""),
        ("proof_identifier", ""),
        ("owner_contact", ""),
    ],
)
def test_incomplete_claim_is_rejected(
    client,
    login_as,
    add_item,
    database,
    field,
    value,
):
    item_id = add_item()
    login_as()
    payload = {**VALID_CLAIM, "item_id": str(item_id), field: value}

    response = client.post("/claims", data=payload)

    assert response.status_code == 302
    assert any(
        "provide private proof and contact" in message
        for message in flashed_messages(client)
    )
    assert database.execute("SELECT COUNT(*) FROM claims").fetchone()[0] == 0


def test_unknown_and_claimed_items_are_rejected(
    client,
    login_as,
    add_item,
    database,
):
    claimed_id = add_item("Claimed")
    login_as()

    unknown = client.post(
        "/claims",
        data={**VALID_CLAIM, "item_id": "999"},
    )
    assert "The selected item no longer exists." in flashed_messages(client)

    returned = client.post(
        "/claims",
        data={**VALID_CLAIM, "item_id": str(claimed_id)},
    )

    assert unknown.status_code == 302
    assert returned.status_code == 302
    assert "That item has already been returned to its owner." in flashed_messages(
        client
    )
    assert database.execute("SELECT COUNT(*) FROM claims").fetchone()[0] == 0


def test_tampered_item_description_is_rejected(
    client,
    login_as,
    add_item,
    database,
):
    item_id = add_item()
    login_as()

    response = client.post(
        "/claims",
        data={
            **VALID_CLAIM,
            "item_id": str(item_id),
            "claimed_item": "A different item",
        },
    )

    assert response.status_code == 302
    assert any(
        "details have changed" in message for message in flashed_messages(client)
    )
    assert database.execute("SELECT COUNT(*) FROM claims").fetchone()[0] == 0


def test_duplicate_active_claim_from_same_contact_is_rejected(
    client,
    login_as,
    add_item,
    database,
):
    item_id = add_item()
    login_as()
    payload = {**VALID_CLAIM, "item_id": str(item_id)}

    first = client.post("/claims", data=payload)
    duplicate = client.post("/claims", data=payload)

    assert first.status_code == 302
    assert duplicate.status_code == 302
    assert any(
        "already have an active claim" in message
        for message in flashed_messages(client)
    )
    assert database.execute("SELECT COUNT(*) FROM claims").fetchone()[0] == 1
