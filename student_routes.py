"""Student dashboard and finder-reporting services."""

from pathlib import Path
import uuid

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.utils import secure_filename

from route_helpers import is_allowed_image, role_required
from usiulostnfound_database import get_connection


student_bp = Blueprint("student", __name__)

ITEM_CATEGORIES = (
    "Electronics",
    "Documents",
    "Keys",
    "Wallets",
    "Books",
    "Other",
)

PUBLIC_ITEM_COLUMNS = """
    id, category, description, location, date, image_path, status, created_at
"""


def _database_connection():
    """Open the configured application database."""
    database_path = current_app.config.get("DATABASE_PATH")
    if database_path:
        return get_connection(database_path)
    return get_connection()


def _available_items(connection, category=""):
    """Return public fields for items that have not been claimed."""
    query = f"""
        SELECT {PUBLIC_ITEM_COLUMNS}
        FROM items
        WHERE status != 'Claimed'
    """
    parameters = []
    if category in ITEM_CATEGORIES:
        query += " AND category = ?"
        parameters.append(category)
    query += " ORDER BY created_at DESC, id DESC"
    return connection.execute(query, parameters).fetchall()


@student_bp.get("/student")
@role_required("student")
def dashboard():
    """Render the student workspace and its available-item register."""
    requested_category = request.args.get("category", "").strip()
    selected_category = (
        requested_category if requested_category in ITEM_CATEGORIES else ""
    )

    connection = _database_connection()
    try:
        items = _available_items(connection, selected_category)
        item_count = connection.execute(
            "SELECT COUNT(*) FROM items WHERE status != 'Claimed'"
        ).fetchone()[0]
        checked_in_count = connection.execute(
            "SELECT COUNT(*) FROM items WHERE status = 'Checked-In'"
        ).fetchone()[0]
    finally:
        connection.close()

    return render_template(
        "student_dashboard.html",
        items=items,
        categories=ITEM_CATEGORIES,
        selected_category=selected_category,
        item_count=item_count,
        checked_in_count=checked_in_count,
    )


@student_bp.post("/items/report")
@role_required("student")
def report_item():
    """Validate and store a found-item report for security review."""
    values = {
        "category": request.form.get("category", "").strip(),
        "description": request.form.get("description", "").strip(),
        "identifier": request.form.get("identifier", "").strip(),
        "location": request.form.get("location", "").strip(),
        "date": request.form.get("date", "").strip(),
        "contact": request.form.get("finder_contact", "").strip(),
    }

    if values["category"] not in ITEM_CATEGORIES:
        flash("Select a valid item category.", "error")
        return redirect(url_for("student.dashboard", panel="finder"))

    if any(not value for value in values.values()):
        flash("Complete every required field before submitting.", "error")
        return redirect(url_for("student.dashboard", panel="finder"))

    uploaded_file = request.files.get("item_photo")
    image_path = None
    if uploaded_file and uploaded_file.filename:
        if not is_allowed_image(uploaded_file.filename):
            flash("Upload a PNG, JPG, JPEG, WEBP, or GIF image.", "error")
            return redirect(url_for("student.dashboard", panel="finder"))

        safe_name = secure_filename(uploaded_file.filename)
        if not safe_name:
            flash("The uploaded image filename is not valid.", "error")
            return redirect(url_for("student.dashboard", panel="finder"))

        unique_name = f"{uuid.uuid4().hex}_{safe_name}"
        upload_folder = Path(current_app.config["UPLOAD_FOLDER"])
        upload_folder.mkdir(parents=True, exist_ok=True)
        uploaded_file.save(upload_folder / unique_name)
        image_path = f"uploads/{unique_name}"

    connection = _database_connection()
    try:
        connection.execute(
            """
            INSERT INTO items (
                category, description, identifier, location, date,
                contact, image_path, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending Security')
            """,
            (
                values["category"],
                values["description"],
                values["identifier"],
                values["location"],
                values["date"],
                values["contact"],
                image_path,
            ),
        )
        connection.commit()
    finally:
        connection.close()

    flash("Found item reported. Security will verify and check it in.", "success")
    return redirect(url_for("student.dashboard"))
