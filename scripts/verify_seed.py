#!/usr/bin/env python3
from app import create_app
from app.extensions import db


EXPECTED = {
    "users": 30,
    "departments": 6,
    "roles": 3,
    "projects": 10,
}


def count(table):
    return db.fetch_one(f"SELECT COUNT(*) AS total FROM {table}")["total"]


app = create_app()

with app.app_context():
    results = {
        table: count(table)
        for table in ["users", "departments", "roles", "projects", "project_members",
                      "project_comments", "documents", "activity_logs"]
    }

    role_rows = db.fetch_all("""
        SELECT r.name, COUNT(*) AS total
        FROM users u
        JOIN roles r ON r.id=u.role_id
        GROUP BY r.name
        ORDER BY r.name
    """)

    meta = db.fetch_one("SELECT schema_version, seed_version FROM app_meta WHERE id=1")

    failed = False
    for table, expected in EXPECTED.items():
        if results[table] != expected:
            failed = True

    print("CYBERVOYRAX Phase 2 Seed Verification")
    print("------------------------------------")
    for key, value in results.items():
        print(f"{key:18} {value}")

    print()
    print("Roles")
    for row in role_rows:
        print(f"{row['name']:18} {row['total']}")

    print()
    print(f"Schema version: {meta['schema_version']}")
    print(f"Seed version:   {meta['seed_version']}")

    if failed:
        raise SystemExit("Seed verification failed.")

    print()
    print("Seed verification passed.")
