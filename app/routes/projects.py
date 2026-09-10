from flask import Blueprint, jsonify

from app.auth_context import login_required, load_current_user
from app.services.authorization import require_project_access
from app.services.container import build_services

projects_bp = Blueprint("projects", __name__, url_prefix="/api/projects")


@projects_bp.get("")
@login_required
def project_list():
    services = build_services()
    user = load_current_user()
    projects = services["projects"].list_visible_projects(user)

    return jsonify([
        {
            "id": p.id,
            "project_code": p.project_code,
            "name": p.name,
            "status": p.status,
            "visibility": p.visibility,
            "manager_user_id": p.manager_user_id,
            "starts_on": p.starts_on.isoformat(),
            "due_on": p.due_on.isoformat(),
        }
        for p in projects
    ])


@projects_bp.get("/<int:project_id>")
@login_required
def project_detail(project_id):
    services = build_services()
    user = load_current_user()
    project = services["projects"].get_project(project_id)

    return jsonify({
        "id": project.id,
        "project_code": project.project_code,
        "name": project.name,
        "status": project.status,
        "visibility": project.visibility,
        "manager_user_id": project.manager_user_id,
        "starts_on": project.starts_on.isoformat(),
        "due_on": project.due_on.isoformat(),
    })
