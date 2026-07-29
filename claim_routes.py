"""Available-item search and ownership-claim services."""

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from route_helpers import role_required
from student_routes import ITEM_CATEGORIES, PUBLIC_ITEM_COLUMNS
from usiulostnfound_database import get_connection


claim_bp = Blueprint("claims", __name__)


def _database_connection():
    """Open the configured database without taking ownership of its implementation."""
    database_path = current_app.config.get("DATABASE_PATH")
    if database_path:
        try:
            return get_connection(database_path)
        except TypeError:
            pass
    return get_connection()


@claim_bp.get("/items")
@role_required("student")
def list_items():
    """Render available items, optionally filtered by a recognised category."""
    requested_category = request.args.get("category", "").strip()
    selected_category = (
        requested_category if requested_category in ITEM_CATEGORIES else ""
    )

    query = f"""
        SELECT {PUBLIC_ITEM_COLUMNS}
        FROM items
        WHERE status != 'Claimed'
    """
    parameters = []
    if selected_category:
        query += " AND category = ?"
        parameters.append(selected_category)
    query += " ORDER BY created_at DESC, id DESC"

    connection = _database_connection()
    try:
        items = connection.execute(query, parameters).fetchall()
    finally:
        connection.close()

    return render_template(
        "partials/item_list.html",
        items=items,
        selected_category=selected_category,
    )


@claim_bp.post("/claims")
@role_required("student")
def submit_claim():
    """Validate an ownership claim and queue it for security review."""
    item_id = request.form.get("item_id", "").strip()
    claimed_item = request.form.get("claimed_item", "").strip()
    proof_identifier = request.form.get("proof_identifier", "").strip()
    contact = request.form.get("owner_contact", "").strip()

    if not item_id.isdigit() or not claimed_item or not proof_identifier or not contact:
        flash(
            "Select an item and provide private proof and contact information.",
            "error",
        )
        return redirect(url_for("student.dashboard", panel="owner"))

    connection = _database_connection()
    try:
        item = connection.execute(
            "SELECT id, description, status FROM items WHERE id = ?",
            (int(item_id),),
        ).fetchone()

        if item is None:
            flash("The selected item no longer exists.", "error")
            return redirect(url_for("student.dashboard", panel="owner"))

        if item["status"] == "Claimed":
            flash("That item has already been returned to its owner.", "error")
            return redirect(url_for("student.dashboard", panel="owner"))

        if claimed_item != item["description"]:
            flash("The selected item details have changed. Please select it again.", "error")
            return redirect(url_for("student.dashboard", panel="owner"))

        existing_claim = connection.execute(
            """
            SELECT 1
            FROM claims
            WHERE item_id = ?
              AND contact = ?
              AND status IN ('Pending', 'Approved')
            """,
            (item["id"], contact),
        ).fetchone()
        if existing_claim:
            flash("You already have an active claim for this item.", "error")
            return redirect(url_for("student.dashboard", panel="owner"))

        connection.execute(
            """
            INSERT INTO claims (
                item_id, claimed_item, proof_identifier, contact, status
            )
            VALUES (?, ?, ?, ?, 'Pending')
            """,
            (item["id"], item["description"], proof_identifier, contact),
        )
        connection.commit()
    finally:
        connection.close()

    flash("Your ownership claim is pending security review.", "success")
    return redirect(url_for("student.dashboard"))
