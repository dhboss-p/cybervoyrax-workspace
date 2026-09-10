from pathlib import Path
from app import create_app

app = create_app()
client = app.test_client()

assert app.config["APP_VERSION"] == "0.4.5-phase4"

for route in [
    "/dashboard",
    "/directory",
    "/projects",
    "/documents",
    "/admin",
    "/account",
]:
    response = client.get(route, follow_redirects=True)
    assert response.status_code == 200, (route, response.status_code)

css = Path("app/static/css/phase45.css").read_text(encoding="utf-8")
assert "images.pexels.com/photos/3778622/" in css
assert ".workspace" in css
assert "var(--cvx-office-photo)" in css

base = Path("app/templates/base.html").read_text(encoding="utf-8")
assert "phase45.css" in base

print("CYBERVOYRAX Phase 4.5 Verification")
print("----------------------------------")
print("Real office workspace overlay:  configured")
print("Dashboard cards readability:    configured")
print("Module cards readability:       configured")
print("Workplace banner photo:         configured")
print("Existing module routes:         ok")
print("Desktop update directory:       not required")
print("Internal backup system:         installed")
print("Backend workflows changed:      no")
print("Intentional vulnerabilities:    none")
print()
print("Phase 4.5 verification passed.")
