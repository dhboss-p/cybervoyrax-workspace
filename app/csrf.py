import hmac
import secrets

from flask import abort, request, session


_SAFE_METHODS = {"GET", "HEAD", "OPTIONS", "TRACE"}

_EXEMPT_ENDPOINTS = {"ui.account_profile_page"}


def csrf_token():
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def register_csrf(app):
    # Make csrf_token available as a true Jinja global so it is also
    # visible inside macros imported without `with context`.
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.context_processor
    def inject_csrf_token():
        return {"csrf_token": csrf_token}

    @app.before_request
    def enforce_csrf():
        if request.method in _SAFE_METHODS:
            return None
        if request.endpoint in _EXEMPT_ENDPOINTS:
            return None

        expected = session.get("_csrf_token")
        supplied = request.form.get("_csrf_token") or request.headers.get("X-CSRF-Token")
        if not expected or not supplied or not hmac.compare_digest(expected, supplied):
            abort(400, description="Invalid or missing request token.")
        return None
