#!/usr/bin/env python3

import secrets

from app import create_app
from app.extensions import db
from app.services.security import hash_password

ASSESSMENT_EMAIL = "assessor@cybervoyrax.test"


def main():
    app = create_app()

    with app.app_context():
        assessor = db.fetch_one(
            "SELECT id FROM users WHERE LOWER(email)=LOWER(%s) LIMIT 1",
            (ASSESSMENT_EMAIL,),
        )

        if not assessor:
            raise SystemExit(
                "Assessment account does not exist. Run the normal provisioning workflow first."
            )

        password = "CVX-" + secrets.token_urlsafe(24)

        db.execute(
            "UPDATE users SET password_hash=%s WHERE id=%s",
            (hash_password(password), assessor["id"]),
        )

        # Existing sessions should no longer remain authenticated.
        db.execute(
            "DELETE FROM user_sessions WHERE user_id=%s",
            (assessor["id"],),
        )

        print(f"ASSESSMENT_EMAIL={ASSESSMENT_EMAIL}")
        print(f"ASSESSMENT_PASSWORD={password}")


if __name__ == "__main__":
    main()
