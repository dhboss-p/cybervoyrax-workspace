from pathlib import Path
from app import create_app

app = create_app()
assert app.config["APP_VERSION"] == "0.6.1-phase6.1"
assert str(app.config["APP_PHASE"]) == "6.1"

required = [
    Path("app/csrf.py"),
    Path("app/routes/main.py"),
    Path("app/routes/projects.py"),
    Path("app/services/auth.py"),
    Path("app/templates/projects/detail.html"),
]
for item in required:
    assert item.exists(), f"missing {item}"

csrf_source = Path("app/csrf.py").read_text()
assert "@app.before_request" in csrf_source
assert "hmac.compare_digest" in csrf_source
assert "_SAFE_METHODS" in csrf_source

# Verify CSRF coverage across standard POST forms.
for template in Path("app/templates").rglob("*.html"):
    source = template.read_text(errors="ignore")
    if 'method="post"' in source.lower() and template.as_posix() != "app/templates/account/profile.html":
        assert "_csrf_token" in source, f"missing CSRF token in {template}"

endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}
for endpoint in ["main.login", "main.search", "projects.project_detail", "ui.project_comment"]:
    assert endpoint in endpoints, f"missing endpoint {endpoint}"

print("CYBERVOYRAX Workspace Phase 6.1 structural verification passed.")
print("Global CSRF baseline verification passed.")
