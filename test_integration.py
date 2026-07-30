"""End-to-end workflow integration test using the Flask client."""

from usiulostnfound_database import get_connection


def test_complete_finder_owner_security_workflow(app, client, add_user):
    add_user(
        user_id="100200",
        name="Finder Student",
        email="finder@usiu.ac.ke",
        password="Student@123",
    )
    add_user(
        user_id="205311",
        name="Owner Student",
        email="owner@usiu.ac.ke",
        password="Student@123",
    )

    # Finder reports an item.
    client.post(
        "/login",
        data={
            "role_selection": "student",
            "user_id": "100200",
            "password": "Student@123",
        },
    )
    client.post(
        "/items/report",
        data={
            "category": "Keys",
            "description": "Keys with a blue tag",
            "identifier": "Tag says B17",
            "location": "Library entrance",
            "date": "2026-07-27",
            "finder_contact": "finder@usiu.ac.ke",
        },
    )
    client.get("/logout")

    connection = get_connection(app.config["DATABASE_PATH"])
    try:
        item_id = connection.execute(
            "SELECT id FROM items WHERE description = 'Keys with a blue tag'"
        ).fetchone()["id"]
    finally:
        connection.close()

    # Security checks the item in.
    client.post(
        "/login",
        data={
            "role_selection": "security",
            "user_id": "123456789",
            "password": "Security@123",
        },
    )
    client.post(f"/security/items/{item_id}/checkin")
    client.get("/logout")

    # A different student submits private ownership evidence.
    client.post(
        "/login",
        data={
            "role_selection": "student",
            "user_id": "205311",
            "password": "Student@123",
        },
    )
    client.post(
        "/claims",
        data={
            "item_id": str(item_id),
            "claimed_item": "Keys with a blue tag",
            "proof_identifier": "The blue tag says B17",
            "owner_contact": "owner@usiu.ac.ke",
        },
    )
    client.get("/logout")

    connection = get_connection(app.config["DATABASE_PATH"])
    try:
        claim_id = connection.execute(
            "SELECT id FROM claims WHERE item_id = ?", (item_id,)
        ).fetchone()["id"]
    finally:
        connection.close()

    # Security approves and records the return.
    client.post(
        "/login",
        data={
            "role_selection": "security",
            "user_id": "123456789",
            "password": "Security@123",
        },
    )
    client.post(
        f"/security/claims/{claim_id}/decision",
        data={"decision": "approve"},
    )
    client.post(f"/security/items/{item_id}/return")

    connection = get_connection(app.config["DATABASE_PATH"])
    try:
        item_status = connection.execute(
            "SELECT status FROM items WHERE id = ?", (item_id,)
        ).fetchone()["status"]
        claim_status = connection.execute(
            "SELECT status FROM claims WHERE id = ?", (claim_id,)
        ).fetchone()["status"]
    finally:
        connection.close()

    assert item_status == "Claimed"
    assert claim_status == "Approved"
