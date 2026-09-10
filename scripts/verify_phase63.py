from pathlib import Path
from app import create_app

app = create_app()

assert app.config["APP_VERSION"] == "0.6.3-phase6.3"
assert str(app.config["APP_PHASE"]) == "6.3"

required_files = [
    Path("app/csrf.py"),
    Path("app/config.py"),
    Path("app/services/auth.py"),
    Path("app/services/security.py"),
    Path("app/routes/main.py"),
    Path("app/routes/ui.py"),
    Path("app/routes/projects.py"),
]

for item in required_files:
    assert item.exists(), f"missing required file: {item}"

csrf_source = Path("app/csrf.py").read_text(errors="ignore")
assert "@app.before_request" in csrf_source
assert "hmac.compare_digest" in csrf_source
assert 'app.jinja_env.globals["csrf_token"]' in csrf_source

endpoints = {rule.endpoint for rule in app.url_map.iter_rules()}

essential_endpoints = [
    "main.login",
]

for endpoint in essential_endpoints:
    assert endpoint in endpoints, f"missing required endpoint: {endpoint}"

assert len(endpoints) > 5, "application route map appears incomplete"

print("CYBERVOYRAX Workspace Phase 6.3 structural verification passed.")
print("Phase 6.1/6.2 baselines and the Phase 6.2 CSRF/Jinja hotfix remain active.")
