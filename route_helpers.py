"""Shared authorization and upload-validation helpers."""

from functools import wraps

from flask import abort, redirect, session, url_for


ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}


def login_required(view):
    """Redirect unauthenticated visitors to the authentication page."""
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("role"):
            return redirect(url_for("auth.authentication"))
        return view(*args, **kwargs)

    return wrapped_view


def role_required(*allowed_roles):
    """Require authentication and membership in one of ``allowed_roles``."""
    def decorator(view):
        @wraps(view)
        def wrapped_view(*args, **kwargs):
            if not session.get("role"):
                return redirect(url_for("auth.authentication"))
            if session["role"] not in allowed_roles:
                abort(403)
            return view(*args, **kwargs)

        return wrapped_view

    return decorator


def is_allowed_image(filename):
    """Return whether ``filename`` has an approved image extension."""
    if not filename or "." not in filename:
        return False
    return filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
