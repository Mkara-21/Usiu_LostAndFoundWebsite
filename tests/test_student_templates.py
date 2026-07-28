"""Student template contracts and empty-state tests."""


def test_student_dashboard_contains_finder_and_claim_contracts(
    client, login_as, add_item
):
    add_item()
    login_as()
    page = client.get("/student").data
    for value in (
        b'action="/items/report"',
        b'name="category"',
        b'name="description"',
        b'name="identifier"',
        b'name="location"',
        b'name="date"',
        b'name="finder_contact"',
        b'name="item_photo"',
        b'action="/claims"',
        b'name="item_id"',
        b'name="proof_identifier"',
        b'name="owner_contact"',
    ):
        assert value in page


def test_student_dashboard_renders_item_and_claim_hook(client, login_as, add_item):
    item_id = add_item(description="Lavender smartphone")
    login_as()
    page = client.get("/student").data
    assert b"Lavender smartphone" in page
    assert f'data-item-id="{item_id}"'.encode() in page
    assert b'onclick="startClaim(this)"' in page


def test_student_dashboard_has_empty_state(client, login_as):
    login_as()
    page = client.get("/student").data
    assert b"No available items yet" in page
