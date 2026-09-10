from app.models import Project


class ProjectRepository:
    def __init__(self, db):
        self.db = db

    def _to_project(self, row):
        if not row:
            return None

        return Project(
            id=row["id"],
            project_code=row["project_code"],
            name=row["name"],
            status=row["status"],
            visibility=row["visibility"],
            manager_user_id=row["manager_user_id"],
            department_id=row["department_id"],
            starts_on=row["starts_on"],
            due_on=row["due_on"],
        )

    def get_by_id(self, project_id):
        row = self.db.fetch_one(
            """
            SELECT id, project_code, name, status, visibility,
                   manager_user_id, department_id, starts_on, due_on
            FROM projects
            WHERE id = %s
            """,
            (project_id,),
        )
        return self._to_project(row)

    def list_for_user(self, user_id, is_admin=False):
        if is_admin:
            rows = self.db.fetch_all(
                """
                SELECT id, project_code, name, status, visibility,
                       manager_user_id, department_id, starts_on, due_on
                FROM projects
                ORDER BY due_on, name
                """
            )
        else:
            rows = self.db.fetch_all(
                """
                SELECT DISTINCT
                    p.id, p.project_code, p.name, p.status, p.visibility,
                    p.manager_user_id, p.department_id, p.starts_on, p.due_on
                FROM projects p
                LEFT JOIN project_members pm ON pm.project_id = p.id
                WHERE
                    p.visibility = 'COMPANY'
                    OR p.manager_user_id = %s
                    OR pm.user_id = %s
                ORDER BY p.due_on, p.name
                """,
                (user_id, user_id),
            )
        return [self._to_project(row) for row in rows]

    def is_member(self, project_id, user_id):
        row = self.db.fetch_one(
            """
            SELECT 1 AS found
            FROM project_members
            WHERE project_id = %s AND user_id = %s
            LIMIT 1
            """,
            (project_id, user_id),
        )
        return bool(row)
