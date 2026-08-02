"""Security verification, claim decisions, and return confirmation."""

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from route_helpers import role_required
from usiulostnfound_database import get_connection


security_bp = Blueprint("security", __name__)


def _database_connection():
    return get_connection(current_app.config["DATABASE_PATH"])


@security_bp.get("/security")
@role_required("security")
def dashboard():
    connection = _database_connection()
    try:
        items = connection.execute(
            "SELECT * FROM items ORDER BY created_at DESC, id DESC"
        ).fetchall()
        claims = connection.execute(
            """
            SELECT claims.*, items.status AS item_status,
                   items.description AS item_description
            FROM claims
            LEFT JOIN items ON items.id = claims.item_id
            ORDER BY claims.created_at DESC, claims.id DESC
            """
        ).fetchall()
        metrics = {
            "pending_items": connection.execute(
                "SELECT COUNT(*) FROM items WHERE status = 'Pending Security'"
            ).fetchone()[0],
            "checked_in": connection.execute(
                "SELECT COUNT(*) FROM items WHERE status = 'Checked-In'"
            ).fetchone()[0],
            "pending_claims": connection.execute(
                "SELECT COUNT(*) FROM claims WHERE status = 'Pending'"
            ).fetchone()[0],
            "returned": connection.execute(
                "SELECT COUNT(*) FROM items WHERE status = 'Claimed'"
            ).fetchone()[0],
        }
    finally:
        connection.close()

    return render_template(
        "security_dashboard.html",
        items=items,
        claims=claims,
        metrics=metrics,
    )


@security_bp.post("/security/items/<int:item_id>/checkin")
@role_required("security")
def check_in_item(item_id):
    connection = _database_connection()
    try:
        item = connection.execute(
            "SELECT status FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if item is None:
            abort(404)
        if item["status"] != "Pending Security":
            abort(409, description="Only pending items can be checked in.")
        connection.execute(
            "UPDATE items SET status = 'Checked-In' WHERE id = ?", (item_id,)
        )
        connection.commit()
    finally:
        connection.close()

    flash("Item checked into secure storage.", "success")
    return redirect(url_for("security.dashboard"))


@security_bp.post("/security/claims/<int:claim_id>/decision")
@role_required("security")
def decide_claim(claim_id):
    decision = request.form.get("decision", "").strip().lower()
    if decision not in {"approve", "deny"}:
        abort(400, description="Decision must be approve or deny.")

    connection = _database_connection()
    try:
        claim = connection.execute(
            """
            SELECT claims.*, items.status AS item_status
            FROM claims
            LEFT JOIN items ON items.id = claims.item_id
            WHERE claims.id = ?
            """,
            (claim_id,),
        ).fetchone()
        if claim is None:
            abort(404)
        if claim["status"] != "Pending":
            abort(409, description="This claim has already been decided.")

        if decision == "approve":
            if claim["item_status"] != "Checked-In":
                abort(409, description="Check the item in before approving its claim.")
            connection.execute(
                "UPDATE claims SET status = 'Approved' WHERE id = ?", (claim_id,)
            )
            connection.execute(
                "UPDATE items SET status = 'Claimed' WHERE id = ?", (claim["item_id"],)
            )
            message = "Claim approved and item released to its verified owner."
        else:
            connection.execute(
                "UPDATE claims SET status = 'Denied' WHERE id = ?", (claim_id,)
            )
            message = "Claim denied. The item remains available for verification."
        connection.commit()
    finally:
        connection.close()

    flash(message, "success" if decision == "approve" else "info")
    return redirect(url_for("security.dashboard"))


@security_bp.post("/security/items/<int:item_id>/return")
@role_required("security")
def confirm_return(item_id):
    connection = _database_connection()
    try:
        item = connection.execute(
            "SELECT status FROM items WHERE id = ?", (item_id,)
        ).fetchone()
        if item is None:
            abort(404)
        approved_claim = connection.execute(
            """
            SELECT 1 FROM claims
            WHERE item_id = ? AND status = 'Approved'
            """,
            (item_id,),
        ).fetchone()
        if item["status"] != "Claimed" or approved_claim is None:
            abort(409, description="Only an approved claimed item can be returned.")
        connection.execute(
            "UPDATE items SET status = 'Claimed' WHERE id = ?", (item_id,)
        )
        connection.commit()
    finally:
        connection.close()

    flash("Return confirmed. The item remains recorded as claimed.", "success")
    return redirect(url_for("security.dashboard"))
