from datetime import datetime, timedelta, timezone
from flask import Blueprint, jsonify, current_app
from app.auth_context import login_required, load_current_user
from app.services.security import issue_workspace_jwt

account_bp = Blueprint("account", __name__, url_prefix="/api/account")


@account_bp.get("")
@login_required
def account_overview():
    user = load_current_user()
    return jsonify({
        "id": user.id,
        "employee_code": user.employee_code,
        "email": user.email,
        "name": user.full_name,
        "job_title": user.job_title,
        "department": user.department,
        "role": user.role,
        "status": user.account_status,
    })


@account_bp.get("/token")
@login_required
def account_api_token():
    user = load_current_user()
    expires = datetime.now(timezone.utc) + timedelta(minutes=current_app.config["JWT_TTL_MINUTES"])
    token = issue_workspace_jwt(user.id, user.role, current_app.config["SECRET_KEY"], expires)
    return jsonify({"token": token, "token_type": "Bearer", "expires_in": current_app.config["JWT_TTL_MINUTES"] * 60})
