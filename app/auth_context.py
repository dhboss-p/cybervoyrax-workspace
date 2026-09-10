from functools import wraps
from flask import current_app, g, redirect, request, url_for

from app.services.container import build_services
from app.services.errors import AuthenticationError, AuthorizationError
from app.services.security import resolve_workspace_jwt

def load_current_user():
    if hasattr(g, "current_user"):
        return g.current_user
    token = request.cookies.get(current_app.config["AUTH_COOKIE_NAME"])
    user = build_services()["auth"].resolve_session(token)
    if not user and request.path.startswith("/api/"):
        authz = request.headers.get("Authorization", "")
        if authz.lower().startswith("bearer "):
            claims = resolve_workspace_jwt(authz.split(None, 1)[1].strip(), current_app.config["SECRET_KEY"])
            if claims and claims.get("sub"):
                try:
                    user = build_services()["user_repository"].get_by_id(int(claims["sub"]))
                except (TypeError, ValueError):
                    user = None
    g.current_user = user
    return user

def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = load_current_user()
        if not user:
            if request.path.startswith("/api/"):
                raise AuthenticationError("Authentication is required.")
            return redirect(url_for("main.login", next=request.full_path))
        return view(*args, **kwargs)
    return wrapped

def roles_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            user = load_current_user()
            if not user:
                return redirect(url_for("main.login"))
            if user.role not in roles:
                raise AuthorizationError("You do not have permission to access this area.")
            return view(*args, **kwargs)
        return wrapped
    return decorator
