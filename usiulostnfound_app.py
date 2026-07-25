"""Application entry point for the USIU-A Lost & Found website."""

import os
from pathlib import Path

from flask import Flask, redirect, session, url_for

from auth_routes import auth_bp
from claim_routes import claim_bp
from security_routes import security_bp
from student_routes import student_bp
from usiulostnfound_database import init_db


BASE_DIR = Path(__file__).resolve().parent


def create_app(test_config=None):
    """Create and configure a Flask application instance."""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-me"),
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
        UPLOAD_FOLDER=str(BASE_DIR / "static" / "uploads"),
    )

    if test_config:
        app.config.update(test_config)

    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(claim_bp)
    app.register_blueprint(security_bp)

    @app.get("/")
    def home():
        role = session.get("role")
        if role == "student":
            return redirect(url_for("student.dashboard"))
        if role == "security":
            return redirect(url_for("security.dashboard"))
        return redirect(url_for("auth.authentication"))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
