from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    if not db.wait_until_ready():
        raise SystemExit("Database did not become ready in time.")

print("Database is ready.")
