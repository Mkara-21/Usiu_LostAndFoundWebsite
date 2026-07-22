                                                                                                                                                                                           .                                                                                                                                                                                                                                                              Code:                                                                                                                                                                                                                                                import os
import sqlite3

from werkzeug.security import generate_password_hash

# Single source of truth for the database file location
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lostandfound.db')

# Item lifecycle: a finder's report starts unverified, security checks it into
# the vault, and an approved claim marks it as returned to its owner.
ITEM_STATUSES = ('Pending Security', 'Checked-In', 'Claimed')

# Claim lifecycle
CLAIM_STATUSES = ('Pending', 'Approved', 'Denied')


def get_connection():
    """Open a connection with row access by column name and FK enforcement."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Users Table — columns match the signup/login forms
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  TEXT UNIQUE NOT NULL,
            name     TEXT NOT NULL,
            email    TEXT NOT NULL,
            password TEXT NOT NULL,
            role     TEXT NOT NULL
        )
    ''')

    # 2. Items Table — columns match the "Found an Item" finder form,
    #    plus a status column that drives the recovery lifecycle.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT,
            description TEXT,
            identifier  TEXT,
            location    TEXT,
            date        TEXT,
            contact     TEXT,
            image_path  TEXT,
            status      TEXT NOT NULL DEFAULT 'Pending Security',
            created_at  TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 3. Claims Table — each claim is linked to the item it is for.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id          INTEGER,
            claimed_item     TEXT,
            proof_identifier TEXT,
            contact          TEXT,
            status           TEXT NOT NULL DEFAULT 'Pending',
            created_at       TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(item_id) REFERENCES items(id)
        )
    ''')

    # Seed the master security account used for testing (only once).
    # The password is stored hashed, never in plain text.
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", ("123456789",))
    if cursor.fetchone() is None:
        cursor.execute(
            "INSERT INTO users (user_id, name, email, password, role) VALUES (?, ?, ?, ?, ?)",
            (
                "123456789",
                "Admin Officer",
                "security@usiu.ac.ke",
                generate_password_hash("password123"),
                "security",
            ),
        )

    conn.commit()
    conn.close()
    print("Database and tables initialized successfully!")


if __name__ == '__main__':
    init_db()