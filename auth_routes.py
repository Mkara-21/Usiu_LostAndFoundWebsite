"""Authentication blueprint baseline.

Signup, login, and logout behavior will be completed by the authentication
contributor after this recovery branch is merged.
"""

from flask import Blueprint, render_template


auth_bp = Blueprint("auth", __name__)


@auth_bp.get("/auth")
def authentication():
    return render_template("auth.html")
