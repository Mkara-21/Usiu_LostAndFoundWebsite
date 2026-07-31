"""Database schema and demonstration-data tests."""

from seed_mockdata import seed
from usiulostnfound_database import get_connection, init_db


def test_database_creates_required_tables_and_foreign_keys(app):
    connection = get_connection(app.config["DATABASE_PATH"])
    try:
        tables = {
            row["name"]
            for row in connection.execute(
                "SELECT name FROM sqlite_master WHERE type = 'table'"
            )
        }
        assert {"users", "items", "claims"} <= tables
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        connection.close()


def test_init_db_is_idempotent_and_security_account_is_unique(app):
    init_db(app.config["DATABASE_PATH"])
    init_db(app.config["DATABASE_PATH"])
    connection = get_connection(app.config["DATABASE_PATH"])
    try:
        count = connection.execute(
            "SELECT COUNT(*) FROM users WHERE user_id = '123456789'"
        ).fetchone()[0]
        assert count == 1
    finally:
        connection.close()


def test_seed_creates_students_items_claims_and_multiple_statuses(app):
    seed(app.config["DATABASE_PATH"])
    connection = get_connection(app.config["DATABASE_PATH"])
    try:
        assert connection.execute(
            "SELECT COUNT(*) FROM users WHERE role = 'student'"
        ).fetchone()[0] >= 2
        assert connection.execute("SELECT COUNT(*) FROM items").fetchone()[0] >= 6
        assert connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0] >= 2
        assert len(
            connection.execute("SELECT DISTINCT status FROM items").fetchall()
        ) >= 3
        assert len(
            connection.execute("SELECT DISTINCT status FROM claims").fetchall()
        ) >= 2
    finally:
        connection.close()
