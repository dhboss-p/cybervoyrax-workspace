from flask import Blueprint, jsonify, request
from app.auth_context import login_required
from app.services.container import build_services

directory_bp = Blueprint("directory", __name__, url_prefix="/api/directory")


@directory_bp.get("")
@login_required
def directory_list():
    services = build_services()
    users = services["users"].list_directory(
        limit=request.args.get("limit", 100),
        offset=request.args.get("offset", 0),
    )
    return jsonify([
        {
            "id": u.id,
            "employee_code": u.employee_code,
            "name": u.full_name,
            "job_title": u.job_title,
            "department": u.department,
        }
        for u in users
    ])


@directory_bp.get("/<int:user_id>")
@login_required
def directory_profile(user_id):
    user = build_services()["users"].get_user(user_id)
    return jsonify({
        "id": user.id,
        "employee_code": user.employee_code,
        "name": user.full_name,
        "job_title": user.job_title,
        "department": user.department,
        "email": user.email,
    })
