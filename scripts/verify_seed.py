#!/usr/bin/env python3

from app import create_app
from app.extensions import db


REQUIRED_DEPARTMENTS = {
    "Engineering",
    "Product",
    "Operations",
    "Finance",
    "Human Resources",
    "IT",
}

REQUIRED_ROLES = {
    "User",
    "Administrator",
}

REQUIRED_PROJECT_CODES = {
    f"CVX-P{i:03d}" for i in range(1, 11)
}


def count(table):
    row = db.fetch_one(f"SELECT COUNT(*) AS total FROM {table}")
    return int(row["total"])


def fail(message, failures):
    failures.append(message)
    print(f"[FAIL] {message}")


def ok(message):
    print(f"[ OK ] {message}")


app = create_app()

with app.app_context():
    failures = []

    print("CYBERVOYRAX Seed Verification")
    print("------------------------------------")

    # Database connectivity
    if db.ping():
        ok("Database reachable")
    else:
        fail("Database is not reachable", failures)

    # Required roles
    role_rows = db.fetch_all("SELECT name FROM roles")
    roles = {row["name"] for row in role_rows}

    missing_roles = REQUIRED_ROLES - roles

    if missing_roles:
        fail(
            f"Missing required roles: {', '.join(sorted(missing_roles))}",
            failures,
        )
    else:
        ok("Required roles present")

    # Required departments
    department_rows = db.fetch_all("SELECT name FROM departments")
    departments = {row["name"] for row in department_rows}

    missing_departments = REQUIRED_DEPARTMENTS - departments

    if missing_departments:
        fail(
            f"Missing required departments: "
            f"{', '.join(sorted(missing_departments))}",
            failures,
        )
    else:
        ok("Required departments present")

    # Seed user baseline.
    # Runtime registrations are allowed, so this is a minimum.
    user_count = count("users")

    if user_count >= 30:
        ok(f"User baseline present ({user_count} users)")
    else:
        fail(
            f"Expected at least 30 users, found {user_count}",
            failures,
        )

    # Seed project baseline.
    # Runtime-created projects are allowed.
    project_rows = db.fetch_all("SELECT project_code FROM projects")
    project_codes = {row["project_code"] for row in project_rows}

    missing_projects = REQUIRED_PROJECT_CODES - project_codes

    if missing_projects:
        fail(
            f"Missing seed projects: {', '.join(sorted(missing_projects))}",
            failures,
        )
    else:
        ok("Seed project baseline present")

    # Universal company project
    knowledge_base = db.fetch_one(
        """
        SELECT project_code, visibility
        FROM projects
        WHERE project_code=%s
        """,
        ("CVX-P007",),
    )

    if (
        knowledge_base
        and knowledge_base["visibility"] == "COMPANY"
    ):
        ok("Company-wide Internal Knowledge Base configured")
    else:
        fail(
            "CVX-P007 must exist with COMPANY visibility",
            failures,
        )

    # Application metadata
    meta = db.fetch_one(
        """
        SELECT schema_version, seed_version
        FROM app_meta
        WHERE id=1
        """
    )

    if meta:
        ok(
            f"Application metadata present "
            f"(schema={meta['schema_version']}, "
            f"seed={meta['seed_version']})"
        )
    else:
        fail("Application metadata is missing", failures)

    # Runtime information only — these counts are intentionally
    # not compared against fixed seed values.
    print()
    print("Current runtime data")
    print("------------------------------------")

    for table in (
        "users",
        "projects",
        "project_members",
        "project_comments",
        "documents",
        "activity_logs",
    ):
        print(f"{table:18} {count(table)}")

    print()

    if failures:
        print(f"Seed verification failed ({len(failures)} issue(s)).")
        raise SystemExit(1)

    print("Seed verification passed.")
    print("Additional runtime data is allowed.")
