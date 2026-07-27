"""Shared isolated fixtures for application tests."""

from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

from usiulostnfound_app import create_app
from usiulostnfound_database import get_connection


@pytest.fixture()
def app(tmp_path):
    application = create_app(
        {
            "TESTING": True,
            "SECRET_KEY": "test-secret",
            "DATABASE_PATH": str(tmp_path / "test.db"),
            "UPLOAD_FOLDER": str(tmp_path / "uploads"),
        }
    )
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def database(app):
    connection = get_connection(app.config["DATABASE_PATH"])
    yield connection
    connection.close()


@pytest.fixture()
def upload_folder(app):
    return Path(app.config["UPLOAD_FOLDER"])


@pytest.fixture()
def add_user(app):
    def _add_user(
        user_id="100200",
        name="Jane Wanjiru",
        email="jane@usiu.ac.ke",
        password="Student@123",
        role="student",
    ):
        connection = get_connection(app.config["DATABASE_PATH"])
        try:
            connection.execute(
                """
                INSERT INTO users (user_id, name, email, password, role)
                VALUES (?, ?, ?, ?, ?)
                """,
                (user_id, name, email, generate_password_hash(password), role),
            )
            connection.commit()
        finally:
            connection.close()

    return _add_user


@pytest.fixture()
def login_as(client):
    def _login(role="student", user_id="100200", name="Jane Wanjiru"):
        with client.session_transaction() as session:
            session.update(role=role, user_id=user_id, user_name=name)

    return _login


@pytest.fixture()
def add_item(app):
    def _add_item(
        status="Checked-In",
        category="Electronics",
        description="Black smartphone",
    ):
        connection = get_connection(app.config["DATABASE_PATH"])
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
                    "IMEI ends 1234",
                    "Library",
                    "2026-07-27",
                    "0700000000",
                    None,
                    status,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    return _add_item


@pytest.fixture()
def add_claim(app):
    def _add_claim(item_id, status="Pending"):
        connection = get_connection(app.config["DATABASE_PATH"])
        try:
            cursor = connection.execute(
                """
                INSERT INTO claims (
                    item_id, claimed_item, proof_identifier, contact, status
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    item_id,
                    "Black smartphone",
                    "IMEI ends 1234",
                    "0711111111",
                    status,
                ),
            )
            connection.commit()
            return cursor.lastrowid
        finally:
            connection.close()

    return _add_claim
