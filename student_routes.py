"""Student workflow blueprint baseline."""

from flask import Blueprint, render_template

from route_helpers import role_required

student_bp = Blueprint("student", __name__)


@student_bp.get("/student")
@role_required("student")
def dashboard():
    return render_template("student_dashboard.html")
