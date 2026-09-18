#!/usr/bin/env python3

from app import create_app
from app.extensions import db


def main():
    app = create_app()

    with app.app_context():
        project = db.fetch_one(
            """
            SELECT id, visibility
            FROM projects
            WHERE project_code=%s
            """,
            ("CVX-P007",),
        )

        if not project:
            print("Workspace migration: CVX-P007 not present; nothing to update.")
            return

        if project["visibility"] == "COMPANY":
            print("Workspace migration: CVX-P007 already has COMPANY visibility.")
            return

        db.execute(
            """
            UPDATE projects
            SET visibility=%s
            WHERE project_code=%s
            """,
            ("COMPANY", "CVX-P007"),
        )

        print("Workspace migration: CVX-P007 visibility updated to COMPANY.")


if __name__ == "__main__":
    main()
