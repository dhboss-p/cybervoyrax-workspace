from pathlib import Path
from app import create_app

app=create_app()
assert app.config["APP_VERSION"] == "0.6.2-phase6.2"
assert str(app.config["APP_PHASE"]) == "6.2"

for item in [Path("app/csrf.py"), Path("app/services/security.py"), Path("app/auth_context.py"), Path("app/routes/account.py")]:
    assert item.exists(), f"missing {item}"

# Preserve the corrected global CSRF baseline from 6.1.
csrf=Path("app/csrf.py").read_text()
assert "@app.before_request" in csrf and "hmac.compare_digest" in csrf

security=Path("app/services/security.py").read_text()
assert "issue_workspace_jwt" in security and "resolve_workspace_jwt" in security

endpoints={rule.endpoint for rule in app.url_map.iter_rules()}
for endpoint in ["account.account_api_token", "main.login", "ui.document_upload_page", "ui.document_download"]:
    assert endpoint in endpoints, f"missing endpoint {endpoint}"

print("CYBERVOYRAX Workspace Phase 6.2 structural verification passed.")
print("Phase 6.1 CSRF baseline remains active.")
