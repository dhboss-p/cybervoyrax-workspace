from app.extensions import db
from app.repositories import (
    UserRepository,
    ProjectRepository,
    DocumentRepository,
    SessionRepository,
)
from app.services.users import UserService
from app.services.projects import ProjectService
from app.services.documents import DocumentService
from app.services.auth import AuthService


def build_services():
    user_repo = UserRepository(db)
    project_repo = ProjectRepository(db)
    document_repo = DocumentRepository(db)
    session_repo = SessionRepository(db)

    return {
        "user_repository": user_repo,
        "project_repository": project_repo,
        "document_repository": document_repo,
        "session_repository": session_repo,
        "users": UserService(user_repo),
        "projects": ProjectService(project_repo),
        "documents": DocumentService(document_repo),
        "auth": AuthService(user_repo, session_repo),
    }
