from flask import Blueprint, jsonify, current_app
from app.services.container import build_services

api_system_bp = Blueprint("api_system", __name__, url_prefix="/api/system")


@api_system_bp.get("/backend")
def backend_status():
    services = build_services()
    role_counts = services["user_repository"].count_by_role()

    return jsonify({
        "app": "CYBERVOYRAX Workspace",
        "version": current_app.config["APP_VERSION"],
        "phase": current_app.config["APP_PHASE"],
        "architecture": {
            "routes": "blueprints",
            "services": True,
            "repositories": True,
            "models": True,
            "authorization_helpers": True,
            "session_service": True,
            "central_error_handling": True,
            "request_logging": True,
        },
        "role_counts": role_counts,
    })
