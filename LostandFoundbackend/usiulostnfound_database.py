"""SQLite persistence for the USIU-A Lost & Found application."""

from pathlib import Path
import sqlite3

from werkzeug.security import generate_password_hash


DATABASE_PATH = Path(__file__).resolve().with_name("lostandfound.db")
# Backwards-compatible alias used by the demonstration-data script.
DB_PATH = DATABASE_PATH

ITEM_STATUSES = ("Pending Security", "Checked-In", "Claimed")
CLAIM_STATUSES = ("Pending", "Approved", "Denied")


def get_connection(database_path=None):
    """Open a configured SQLite connection with safe defaults."""
    path = Path(database_path or DATABASE_PATH)
    connection = sqlite3.connect(path, timeout=10)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db(database_path=None):
    """Create the schema and required security account idempotently."""
    connection = get_connection(database_path)
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN ('student', 'security'))
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                identifier TEXT NOT NULL,
                location TEXT NOT NULL,
                date TEXT NOT NULL,
                contact TEXT NOT NULL,
                image_path TEXT,
                status TEXT NOT NULL DEFAULT 'Pending Security'
                    CHECK (status IN ('Pending Security', 'Checked-In', 'Claimed')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                claimed_item TEXT NOT NULL,
                proof_identifier TEXT NOT NULL,
                contact TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending'
                    CHECK (status IN ('Pending', 'Approved', 'Denied')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id)
            );

            CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
            CREATE INDEX IF NOT EXISTS idx_items_category ON items(category);
            CREATE INDEX IF NOT EXISTS idx_claims_item_id ON claims(item_id);
            CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(status);
            """
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO users (user_id, name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "123456789",
                "USIU Security Desk",
                "security@usiu.ac.ke",
                generate_password_hash("Security@123"),
                "security",
            ),
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DATABASE_PATH}")
