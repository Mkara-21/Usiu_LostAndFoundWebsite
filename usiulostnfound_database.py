"""SQLite connection and schema initialization for the application baseline."""

from pathlib import Path
import sqlite3

from werkzeug.security import generate_password_hash


DATABASE_PATH = Path(__file__).resolve().with_name("lostandfound.db")
ITEM_STATUSES = ("Pending Security", "Checked-In", "Claimed")
CLAIM_STATUSES = ("Pending", "Approved", "Denied")


def get_connection():
    """Return a database connection with named rows and FK enforcement."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    """Create the baseline schema and default security account safely."""
    connection = get_connection()
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                description TEXT,
                identifier TEXT,
                location TEXT,
                date TEXT,
                contact TEXT,
                image_path TEXT,
                status TEXT NOT NULL DEFAULT 'Pending Security',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS claims (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER,
                claimed_item TEXT,
                proof_identifier TEXT,
                contact TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES items(id)
            );
            """
        )
        connection.execute(
            """
            INSERT OR IGNORE INTO users (user_id, name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                "123456789",
                "Admin Officer",
                "security@usiu.ac.ke",
                generate_password_hash("password123"),
                "security",
            ),
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    init_db()
    print(f"Database initialized at {DATABASE_PATH}")
