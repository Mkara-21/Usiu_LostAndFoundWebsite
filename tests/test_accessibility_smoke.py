"""Small accessibility contract checks for rendered pages."""

import re


def test_authentication_inputs_have_labels(client):
    page = client.get("/auth").get_data(as_text=True)
    input_ids = re.findall(r"<(?:input|select)[^>]+id=\"([^\"]+)\"", page)
    for input_id in input_ids:
        assert f'for="{input_id}"' in page


def test_student_image_has_descriptive_alt_text(client, login_as, add_item, app):
    item_id = add_item(description="Black smartphone")
    connection = __import__("usiulostnfound_database").get_connection(
        app.config["DATABASE_PATH"]
    )
    try:
        connection.execute(
            "UPDATE items SET image_path = 'uploads/example.jpg' WHERE id = ?",
            (item_id,),
        )
        connection.commit()
    finally:
        connection.close()

    login_as()
    page = client.get("/student").get_data(as_text=True)
    assert 'alt="Photograph of Black smartphone"' in page


def test_interactive_icon_controls_have_accessible_names(
    client, login_as
):
    login_as()
    page = client.get("/student").get_data(as_text=True)
    assert 'aria-label="Close finder form"' in page
    assert 'aria-label="Close ownership form"' in page
