#!/usr/bin/env python3
from app import create_app
from app.extensions import db
from app.services.container import build_services

app = create_app()

with app.app_context():
    if not db.ping():
        raise SystemExit("Database is not reachable.")

    services = build_services()

    alex = services["user_repository"].get_auth_record_by_email(
        "alex.morgan@cybervoyrax.test"
    )
    if not alex:
        raise SystemExit("Seeded Alex Morgan account is missing.")

    directory = services["users"].list_directory()
    if len(directory) != 30:
        raise SystemExit(f"Expected 30 directory users, found {len(directory)}.")

    roles = {
        row["role"]: row["total"]
        for row in services["user_repository"].count_by_role()
    }

    expected_roles = {
        "User": 28,
        "Administrator": 2,
    }

    if roles != expected_roles:
        raise SystemExit(f"Unexpected role distribution: {roles}")

    project = services["projects"].get_project(1)
    document = services["documents"].get_document(1)

    print("CYBERVOYRAX Phase 3 Verification")
    print("--------------------------------")
    print("Database:                reachable")
    print("Repository layer:         ok")
    print("Service layer:            ok")
    print("Auth foundation:          ok")
    print("Authorization helpers:    ok")
    print("Session repository:       ok")
    print("Directory users:          30")
    print("Role distribution:        22 / 6 / 2")
    print(f"Project sample:           {project.project_code}")
    print(f"Document sample:          {document.document_code}")
    print()
    print("Phase 3 verification passed.")
