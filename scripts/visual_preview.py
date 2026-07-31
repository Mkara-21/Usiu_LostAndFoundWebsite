"""Run an authenticated local-only preview for screenshot verification."""

import argparse
from pathlib import Path
import sys

from flask import session

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from usiulostnfound_app import create_app


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--role", choices=("student", "security"), required=True)
    parser.add_argument("--port", type=int, default=5001)
    arguments = parser.parse_args()

    app = create_app(
        {
            "SECRET_KEY": "visual-preview-only",
            "VISUAL_PREVIEW": True,
        }
    )

    @app.before_request
    def preview_session():
        session["role"] = arguments.role
        session["user_id"] = (
            "100200" if arguments.role == "student" else "123456789"
        )
        session["user_name"] = (
            "Jane Wanjiru"
            if arguments.role == "student"
            else "USIU Security Desk"
        )

    app.run(
        host="127.0.0.1",
        port=arguments.port,
        debug=False,
        use_reloader=False,
    )


if __name__ == "__main__":
    main()
