#!/usr/bin/env python3
from pathlib import Path
from app import create_app
from app.extensions import db

root=Path('.')
assert '.lab-credentials' in (root/'.gitignore').read_text()
readme=(root/'README.md').read_text()
assert 'assessor@cybervoyrax.test' in readme
assert 'cat .lab-credentials' in readme

app=create_app()
with app.app_context():
    assessor=db.fetch_one("SELECT u.password_hash,r.name role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.email=%s",("assessor@cybervoyrax.test",))
    assert assessor and assessor['role']=='User'
    rows=db.fetch_all("SELECT password_hash FROM users")
    assert rows
    assert all(r['password_hash'].startswith(("$2a$","$2b$","$2y$")) for r in rows)
    assert len({r['password_hash'] for r in rows}) == len(rows)
print("Account baseline verification passed.")
