"""Security workflow blueprint baseline."""

from flask import Blueprint, render_template

from route_helpers import role_required

security_bp = Blueprint("security", __name__)


@security_bp.get("/security")
@role_required("security")
def dashboard():
    return render_template("security_dashboard.html")
