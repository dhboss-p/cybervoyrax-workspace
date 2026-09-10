from flask import Blueprint, jsonify, current_app
from app.extensions import db

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    database_ok = db.ping()
    meta = None

    if database_ok:
        try:
            meta = db.fetch_one(
                "SELECT schema_version, seed_version FROM app_meta WHERE id = 1"
            )
        except Exception:
            meta = None

    status_code = 200 if database_ok else 503

    return jsonify({
        "app": "CYBERVOYRAX Workspace",
        "version": current_app.config["APP_VERSION"],
        "phase": current_app.config["APP_PHASE"],
        "status": "ok" if database_ok else "degraded",
        "database": "reachable" if database_ok else "unreachable",
        "schema_version": meta["schema_version"] if meta else None,
        "seed_version": meta["seed_version"] if meta else None,
        "backend": "core-ready" if database_ok else "unavailable",
    }), status_code
