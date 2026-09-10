from app.models import User


class UserRepository:
    def __init__(self, db):
        self.db = db

    def _to_user(self, row):
        if not row:
            return None

        return User(
            id=row["id"],
            employee_code=row["employee_code"],
            email=row["email"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            job_title=row["job_title"],
            role=row["role"],
            department=row["department"],
            account_status=row["account_status"],
            manager_user_id=row["manager_user_id"],
        )

    def get_by_id(self, user_id):
        row = self.db.fetch_one(
            """
            SELECT
                u.id,
                u.employee_code,
                u.email,
                u.first_name,
                u.last_name,
                u.job_title,
                u.account_status,
                u.manager_user_id,
                r.name AS role,
                d.name AS department
            FROM users u
            JOIN roles r ON r.id = u.role_id
            JOIN departments d ON d.id = u.department_id
            WHERE u.id = %s
            """,
            (user_id,),
        )
        return self._to_user(row)

    def get_auth_record_by_email(self, email):
        return self.db.fetch_one(
            """
            SELECT
                u.id,
                u.email,
                u.password_hash,
                u.account_status,
                r.name AS role
            FROM users u
            JOIN roles r ON r.id = u.role_id
            WHERE LOWER(u.email) = LOWER(%s)
            """,
            (email,),
        )

    def list_directory(self, limit=100, offset=0):
        rows = self.db.fetch_all(
            """
            SELECT
                u.id,
                u.employee_code,
                u.email,
                u.first_name,
                u.last_name,
                u.job_title,
                u.account_status,
                u.manager_user_id,
                r.name AS role,
                d.name AS department
            FROM users u
            JOIN roles r ON r.id = u.role_id
            JOIN departments d ON d.id = u.department_id
            ORDER BY u.first_name, u.last_name
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        )
        return [self._to_user(row) for row in rows]

    def count_by_role(self):
        return self.db.fetch_all(
            """
            SELECT r.name AS role, COUNT(*) AS total
            FROM users u
            JOIN roles r ON r.id = u.role_id
            GROUP BY r.name
            ORDER BY r.name
            """
        )
