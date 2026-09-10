from flask import Blueprint, jsonify
from app.auth_context import roles_required
from app.services.container import build_services

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/overview")
@roles_required("Administrator")
def admin_overview():
    services = build_services()
    role_counts = services["user_repository"].count_by_role()

    return jsonify({
        "area": "administration",
        "role_counts": role_counts,
    })
