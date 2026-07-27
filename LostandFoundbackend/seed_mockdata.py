"""Populate the local database with demonstration accounts, items, and claims."""

from datetime import date, timedelta

from werkzeug.security import generate_password_hash

from usiulostnfound_database import DATABASE_PATH, get_connection, init_db


STUDENTS = (
    ("100200", "Jane Wanjiru", "jwanjiru@usiu.ac.ke", "Student@123"),
    ("205311", "Alex Otieno", "aotieno@usiu.ac.ke", "Student@123"),
)


def _demo_items():
    today = date.today()
    return (
        ("Electronics", "Alpine green smartphone", "IMEI ends 4471", "SAC cafeteria", str(today - timedelta(days=1)), "0712334556", None, "Checked-In"),
        ("Electronics", "Black 65W laptop charger", "White inventory sticker", "Library second floor", str(today - timedelta(days=2)), "library@usiu.ac.ke", None, "Pending Security"),
        ("Documents", "Blue student identification card", "Surname begins with K", "Chandaria lobby", str(today), "0700111222", None, "Checked-In"),
        ("Keys", "Car key with two silver keys", "Grey token on ring", "Parking lot B", str(today - timedelta(days=3)), "security@usiu.ac.ke", None, "Pending Security"),
        ("Wallets", "Tan leather wallet", "Hand-stitched edge", "Student centre", str(today - timedelta(days=1)), "0722444666", None, "Checked-In"),
        ("Books", "International business textbook", "Name written on page 12", "Library circulation desk", str(today - timedelta(days=4)), "0755221334", None, "Checked-In"),
        ("Other", "Black insulated water bottle", "Small dent underneath", "Sports complex", str(today - timedelta(days=2)), "0711002003", None, "Checked-In"),
        ("Other", "Metal-frame eyeglasses", "Red hard case", "Auditorium row F", str(today - timedelta(days=5)), "0799887665", None, "Claimed"),
    )


def seed(database_path=None):
    """Reset demonstration items/claims and safely top up demo users."""
    target = database_path or DATABASE_PATH
    init_db(target)
    connection = get_connection(target)
    try:
        connection.execute("DELETE FROM claims")
        connection.execute("DELETE FROM items")
        for user_id, name, email, password in STUDENTS:
            connection.execute(
                """
                INSERT OR IGNORE INTO users (user_id, name, email, password, role)
                VALUES (?, ?, ?, ?, 'student')
                """,
                (user_id, name, email, generate_password_hash(password)),
            )

        item_ids = {}
        for item in _demo_items():
            cursor = connection.execute(
                """
                INSERT INTO items (
                    category, description, identifier, location, date,
                    contact, image_path, status
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                item,
            )
            item_ids[item[1]] = cursor.lastrowid

        connection.execute(
            """
            INSERT INTO claims (
                item_id, claimed_item, proof_identifier, contact, status
            )
            VALUES (?, ?, ?, ?, 'Pending')
            """,
            (
                item_ids["Alpine green smartphone"],
                "Alpine green smartphone",
                "The IMEI ends in 4471 and the lock screen is a mountain.",
                "0712334556",
            ),
        )
        connection.execute(
            """
            INSERT INTO claims (
                item_id, claimed_item, proof_identifier, contact, status
            )
            VALUES (?, ?, ?, ?, 'Approved')
            """,
            (
                item_ids["Metal-frame eyeglasses"],
                "Metal-frame eyeglasses",
                "They are kept in my red hard case.",
                "0799887665",
            ),
        )
        connection.commit()
    finally:
        connection.close()


if __name__ == "__main__":
    seed()
    print(f"Demonstration data written to {DATABASE_PATH}")
