from app import create_app
from app.extensions import db

app=create_app()
with app.app_context():
    assert db.ping()
    assert db.fetch_one("SHOW TABLES LIKE 'notifications'")
    assert db.fetch_one("SHOW TABLES LIKE 'workspace_settings'")
    assert db.fetch_one("SELECT id FROM users LIMIT 1")
    assert db.fetch_one("SELECT id FROM roles WHERE name='Administrator' LIMIT 1")

client=app.test_client()
r=client.get("/dashboard")
assert r.status_code in (301,302)

print("CYBERVOYRAX Phase 5 compatibility verification passed.")
print("Credential-specific historical checks retired by the Phase 6.3 account baseline.")
