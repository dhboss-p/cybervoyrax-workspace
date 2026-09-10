from .errors import NotFoundError


class ProjectService:
    def __init__(self, project_repository):
        self.projects = project_repository

    def get_project(self, project_id):
        project = self.projects.get_by_id(project_id)
        if not project:
            raise NotFoundError("Project not found.")
        return project

    def list_visible_projects(self, user):
        return self.projects.list_for_user(
            user_id=user.id,
            is_admin=(user.role == "Administrator"),
        )
