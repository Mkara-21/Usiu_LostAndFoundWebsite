"""Security state-transition tests."""


def test_security_checks_in_pending_item(
    client, login_as, add_item, database
):
    item_id = add_item("Pending Security")
    login_as("security", "123456789", "Security Officer")
    response = client.post(f"/security/items/{item_id}/checkin")
    assert response.status_code == 302
    assert database.execute(
        "SELECT status FROM items WHERE id = ?", (item_id,)
    ).fetchone()["status"] == "Checked-In"


def test_checkin_rejects_unknown_or_non_pending_item(client, login_as, add_item):
    item_id = add_item("Checked-In")
    login_as("security", "123456789", "Security Officer")
    assert client.post("/security/items/999/checkin").status_code == 404
    assert client.post(f"/security/items/{item_id}/checkin").status_code == 409


def test_approval_updates_claim_and_item(
    client, login_as, add_item, add_claim, database
):
    item_id = add_item("Checked-In")
    claim_id = add_claim(item_id)
    login_as("security", "123456789", "Security Officer")
    response = client.post(
        f"/security/claims/{claim_id}/decision", data={"decision": "approve"}
    )
    assert response.status_code == 302
    assert database.execute(
        "SELECT status FROM claims WHERE id = ?", (claim_id,)
    ).fetchone()["status"] == "Approved"
    assert database.execute(
        "SELECT status FROM items WHERE id = ?", (item_id,)
    ).fetchone()["status"] == "Claimed"


def test_denial_changes_only_claim(
    client, login_as, add_item, add_claim, database
):
    item_id = add_item("Checked-In")
    claim_id = add_claim(item_id)
    login_as("security", "123456789", "Security Officer")
    client.post(
        f"/security/claims/{claim_id}/decision", data={"decision": "deny"}
    )
    assert database.execute(
        "SELECT status FROM claims WHERE id = ?", (claim_id,)
    ).fetchone()["status"] == "Denied"
    assert database.execute(
        "SELECT status FROM items WHERE id = ?", (item_id,)
    ).fetchone()["status"] == "Checked-In"


def test_decision_rejects_unknown_invalid_repeated_and_unchecked_claim(
    client, login_as, add_item, add_claim
):
    pending_item = add_item("Pending Security")
    pending_claim = add_claim(pending_item)
    decided_item = add_item("Checked-In", description="Second phone")
    decided_claim = add_claim(decided_item, "Denied")
    login_as("security", "123456789", "Security Officer")

    assert client.post(
        "/security/claims/999/decision", data={"decision": "deny"}
    ).status_code == 404
    assert client.post(
        f"/security/claims/{pending_claim}/decision", data={"decision": "maybe"}
    ).status_code == 400
    assert client.post(
        f"/security/claims/{pending_claim}/decision", data={"decision": "approve"}
    ).status_code == 409
    assert client.post(
        f"/security/claims/{decided_claim}/decision", data={"decision": "deny"}
    ).status_code == 409


def test_return_confirmation_preserves_claimed_status(
    client, login_as, add_item, add_claim, database
):
    item_id = add_item("Claimed")
    add_claim(item_id, "Approved")
    login_as("security", "123456789", "Security Officer")
    assert client.post(f"/security/items/{item_id}/return").status_code == 302
    assert database.execute(
        "SELECT status FROM items WHERE id = ?", (item_id,)
    ).fetchone()["status"] == "Claimed"
