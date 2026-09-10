from flask import Blueprint, jsonify

from app.auth_context import login_required, load_current_user
from app.services.authorization import require_document_access
from app.services.container import build_services

documents_bp = Blueprint("documents", __name__, url_prefix="/api/documents")


@documents_bp.get("/<int:document_id>")
@login_required
def document_detail(document_id):
    services = build_services()
    user = load_current_user()
    document = services["documents"].get_document(document_id)

    require_document_access(
        user,
        document,
        services["project_repository"],
    )

    return jsonify({
        "id": document.id,
        "document_code": document.document_code,
        "title": document.title,
        "original_filename": document.original_filename,
        "mime_type": document.mime_type,
        "file_size_bytes": document.file_size_bytes,
        "visibility": document.visibility,
        "project_id": document.project_id,
    })
