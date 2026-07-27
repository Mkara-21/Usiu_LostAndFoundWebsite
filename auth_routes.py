"""Authentication and session routes."""

import re
import sqlite3

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from usiulostnfound_database import get_connection


auth_bp = Blueprint("auth", __name__)

ALLOWED_ROLES = {"student", "security"}
USIU_EMAIL_PATTERN = re.compile(r"^[^@\s]+@usiu\.ac\.ke$", re.IGNORECASE)
PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)


def _database_connection():
    from flask import current_app

    return get_connection(current_app.config["DATABASE_PATH"])


def _dashboard_for(role):
    endpoint = "security.dashboard" if role == "security" else "student.dashboard"
    return redirect(url_for(endpoint))


@auth_bp.get("/auth")
def authentication():
    if session.get("role") in ALLOWED_ROLES:
        return _dashboard_for(session["role"])
    return render_template("auth.html")


@auth_bp.post("/signup")
def signup():
    role = request.form.get("role_selection", "").strip().lower()
    full_name = request.form.get("full_name", "").strip()
    email = request.form.get("email", "").strip().lower()
    user_id = request.form.get("user_id", "").strip()
    password = request.form.get("password", "")

    if role not in ALLOWED_ROLES:
        flash("Select a valid student or security role.", "error")
        return redirect(url_for("auth.authentication"))
    if not full_name:
        flash("Enter your full name.", "error")
        return redirect(url_for("auth.authentication", mode="signup"))
    if not USIU_EMAIL_PATTERN.fullmatch(email):
        flash("Use a valid @usiu.ac.ke email address.", "error")
        return redirect(url_for("auth.authentication", mode="signup"))

    required_digits = 6 if role == "student" else 9
    if not user_id.isdigit() or len(user_id) != required_digits:
        label = "Student ID" if role == "student" else "Security badge ID"
        flash(f"{label} must contain exactly {required_digits} digits.", "error")
        return redirect(url_for("auth.authentication", mode="signup"))

    if not PASSWORD_PATTERN.fullmatch(password):
        flash(
            "Password must be at least 8 characters and include uppercase, "
            "lowercase, a number, and a special character.",
            "error",
        )
        return redirect(url_for("auth.authentication", mode="signup"))

    connection = _database_connection()
    try:
        connection.execute(
            """
            INSERT INTO users (user_id, name, email, password, role)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, full_name, email, generate_password_hash(password), role),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        flash("An account with that ID already exists.", "error")
        return redirect(url_for("auth.authentication", mode="signup"))
    finally:
        connection.close()

    session.clear()
    session.update(role=role, user_id=user_id, user_name=full_name)
    flash(f"Welcome, {full_name}. Your account is ready.", "success")
    return _dashboard_for(role)


@auth_bp.post("/login")
def login():
    role = request.form.get("role_selection", "").strip().lower()
    user_id = request.form.get("user_id", "").strip()
    password = request.form.get("password", "")

    if role not in ALLOWED_ROLES or not user_id or not password:
        flash("Enter your role, identification number, and password.", "error")
        return redirect(url_for("auth.authentication"))

    connection = _database_connection()
    try:
        account = connection.execute(
            "SELECT * FROM users WHERE user_id = ?", (user_id,)
        ).fetchone()
    finally:
        connection.close()

    if (
        account is None
        or account["role"] != role
        or not check_password_hash(account["password"], password)
    ):
        flash("Invalid credentials or account role.", "error")
        return redirect(url_for("auth.authentication"))

    session.clear()
    session.update(role=role, user_id=user_id, user_name=account["name"])
    flash(f"Welcome back, {account['name']}.", "success")
    return _dashboard_for(role)


@auth_bp.get("/logout")
def logout():
    session.clear()
    flash("You have been signed out securely.", "info")
    return redirect(url_for("auth.authentication"))
