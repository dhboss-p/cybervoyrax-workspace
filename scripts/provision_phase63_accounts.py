#!/usr/bin/env python3
"""Finalize the Phase 6.3 account baseline without resetting application data."""
import os

from app import create_app
from app.extensions import db
from app.services.security import hash_password

ASSESSMENT_EMAIL = "assessor@cybervoyrax.test"


def main():
    password = os.getenv("ASSESSMENT_PASSWORD")
    if not password or len(password) < 16:
        raise SystemExit("ASSESSMENT_PASSWORD must be supplied and be at least 16 characters")

    app = create_app()
    with app.app_context():
        role = db.fetch_one("SELECT id FROM roles WHERE name='User' LIMIT 1")
        dept = db.fetch_one("SELECT id FROM departments WHERE code='IT' LIMIT 1")
        if not role or not dept:
            raise SystemExit("Required User role or IT department is missing")

        assessor = db.fetch_one("SELECT id FROM users WHERE LOWER(email)=LOWER(%s)", (ASSESSMENT_EMAIL,))
        if assessor:
            print("Assessment account already exists. Existing password preserved.")
        else:
            db.execute(
                """INSERT INTO users(
                       employee_code,email,password_hash,first_name,last_name,job_title,
                       office_location,bio,role_id,department_id,account_status,last_login_at
                   ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE',NULL)""",
                (
                    "CVX-ASSESS", ASSESSMENT_EMAIL, hash_password(password),
                    "Security", "Assessor", "Application Security Assessor", "Remote",
                    "Authorized low-privilege assessment account.", role["id"], dept["id"],
                ),
            )
            print("Assessment account created with installation-local credentials.")

    print("Phase 6.3 account baseline provisioned.")
    print(f"Assessment account: {ASSESSMENT_EMAIL}")
    print("Existing user passwords were not changed.")


if __name__ == "__main__":
    main()
