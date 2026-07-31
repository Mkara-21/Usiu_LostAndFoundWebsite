"""Security console rendering and action-visibility tests."""


def test_security_dashboard_shows_pending_checkin_action(
    client, login_as, add_item
):
    item_id = add_item("Pending Security")
    login_as("security", "123456789", "Security Officer")
    page = client.get("/security").data
    assert f'action="/security/items/{item_id}/checkin"'.encode() in page
    assert b"Confirm secure check-in" in page


def test_security_dashboard_shows_claim_decisions_only_when_pending(
    client, login_as, add_item, add_claim
):
    item_id = add_item("Checked-In")
    pending_id = add_claim(item_id, "Pending")
    add_claim(item_id, "Denied")
    login_as("security", "123456789", "Security Officer")
    page = client.get("/security").data
    assert f'action="/security/claims/{pending_id}/decision"'.encode() in page
    assert b"Approve" in page
    assert b"Deny" in page
    assert b"Decision recorded" in page


def test_security_dashboard_renders_metrics_and_filters(client, login_as):
    login_as("security", "123456789", "Security Officer")
    page = client.get("/security").data
    assert b"Awaiting check-in" in page
    assert b"In secure storage" in page
    assert b"Claims to review" in page
    assert b"Returned items" in page
    assert b"filterTableRows" in page
