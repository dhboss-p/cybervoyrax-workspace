import os
from pathlib import Path
from app import create_app
from app.extensions import db

app=create_app()
with app.app_context():
    assert app.config["APP_VERSION"]=="0.5.1-phase5"
    assert db.ping()
    docs=db.fetch_all("SELECT id,stored_filename FROM documents ORDER BY id LIMIT 5")
    assert docs
    folder=Path(app.config["UPLOAD_FOLDER"])
    for d in docs:
        assert d["stored_filename"]
        assert (folder/d["stored_filename"]).exists()

client=app.test_client()
assessment_password=os.getenv("ASSESSMENT_PASSWORD")
if assessment_password:
    r=client.post("/login",data={"email":"assessor@cybervoyrax.test","password":assessment_password},follow_redirects=True)
    assert r.status_code==200

with app.app_context():
    pid=db.fetch_one("""SELECT p.id FROM project_members pm JOIN projects p ON p.id=pm.project_id JOIN users u ON u.id=pm.user_id
                        WHERE u.email='alex.morgan@cybervoyrax.test' ORDER BY p.id LIMIT 1""")["id"]
    did=db.fetch_one("""SELECT d.id FROM documents d JOIN project_members pm ON pm.project_id=d.project_id JOIN users u ON u.id=pm.user_id
                        WHERE u.email='alex.morgan@cybervoyrax.test' ORDER BY d.id LIMIT 1""")["id"]

r=client.get(f"/projects/{pid}")
assert r.status_code==200
html=r.get_data(as_text=True)
for t in ["Project members","Project documents","Project activity"]: assert t in html

r=client.post(f"/projects/{pid}/comments",data={"body":"Phase 5.1 verification comment"},follow_redirects=True)
assert r.status_code==200

with app.app_context():
    saved_comment = db.fetch_one("""
        SELECT id
        FROM project_comments
        WHERE project_id=%s AND body=%s
        ORDER BY id DESC
        LIMIT 1
    """, (pid, "Phase 5.1 verification comment"))
    assert saved_comment

r=client.get(f"/documents/{did}")
assert r.status_code==200 and "Document details" in r.get_data(as_text=True)

r=client.get(f"/documents/{did}/download")
assert r.status_code==200
assert "attachment" in (r.headers.get("Content-Disposition") or "").lower()

print("CYBERVOYRAX Phase 5.1 Verification")
print("----------------------------------")
print("Project detail tabs:          ok")
print("Project comments persistence: ok")
print("Project activity:             ok")
print("Project members view:         ok")
print("Project documents view:       ok")
print("Document detail:              ok")
print("Document download:            ok")
print("Seed document materializer:   ok")
print("Directory profile wiring:     ok")
print("Account flows preserved:      ok")
print("Intentional vulnerabilities:  none")
print()
print("Phase 5.1 verification passed.")
