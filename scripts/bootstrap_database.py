#!/usr/bin/env python3
import subprocess
import sys

from app import create_app
from app.extensions import db


def main():
    app = create_app()

    with app.app_context():
        row = db.fetch_one("SELECT COUNT(*) AS total FROM users")
        user_count = int(row["total"]) if row else 0

    if user_count > 0:
        print(f"Database already initialized ({user_count} users). Skipping seed.")
        return

    print("Fresh database detected. Creating CYBERVOYRAX seed data...")

    subprocess.run(
        [sys.executable, "scripts/seed_database.py"],
        check=True,
    )

    print("Initial database seed complete.")


if __name__ == "__main__":
    main()
