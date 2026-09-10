from .errors import AuthorizationError


def require_role(user, *allowed_roles):
    if user.role not in allowed_roles:
        raise AuthorizationError("You do not have permission to perform this action.")


def can_view_project(user, project, project_repository):
    if user.role == "Administrator":
        return True

    if project.visibility == "COMPANY":
        return True

    if project.manager_user_id == user.id:
        return True

    return project_repository.is_member(project.id, user.id)


def require_project_access(user, project, project_repository):
    if not can_view_project(user, project, project_repository):
        raise AuthorizationError("You do not have access to this project.")


def can_manage_project(user, project):
    return (
        user.role == "Administrator"
        or project.manager_user_id == user.id
    )


def require_project_lead(user, project):
    if not can_manage_project(user, project):
        raise AuthorizationError("You cannot manage this project.")


def can_view_document(user, document, project_repository):
    if user.role == "Administrator":
        return True

    if document.owner_user_id == user.id:
        return True

    if document.visibility == "COMPANY":
        return True

    if document.visibility == "PRIVATE":
        return False

    if document.project_id is None:
        return False

    project = project_repository.get_by_id(document.project_id)
    if not project:
        return False

    if document.visibility == "PROJECT_LEAD":
        return project.manager_user_id == user.id

    if document.visibility == "PROJECT_MEMBERS":
        return (
            project.manager_user_id == user.id
            or project_repository.is_member(project.id, user.id)
        )

    return False


def require_document_access(user, document, project_repository):
    if not can_view_document(user, document, project_repository):
        raise AuthorizationError("You do not have access to this document.")
