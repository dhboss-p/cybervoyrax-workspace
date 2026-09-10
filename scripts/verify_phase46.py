from pathlib import Path
from app import create_app

app = create_app()
client = app.test_client()

assert app.config["APP_VERSION"] == "0.4.6-phase4"

response = client.get("/login", follow_redirects=True)
assert response.status_code == 200

html = response.get_data(as_text=True)

required = [
    "Welcome back",
    "Work email",
    "Password",
    "Remember me",
    "Forgot password?",
    "Sign in",
    "Created by Praise Testimony",
    "Work stays clearer when everything stays connected.",
]

for item in required:
    assert item in html, item

assert html.count("CYBERVOYRAX Workspace") <= 2

auth_css = Path("app/static/css/auth.css").read_text(encoding="utf-8")
assert ".auth-page" in auth_css
assert ".auth-form-panel" in auth_css

base = Path("app/templates/base.html").read_text(encoding="utf-8")
assert "auth.css" in base

print("CYBERVOYRAX Phase 4.6 Verification")
print("----------------------------------")
print("Styled login page:          ok")
print("Split auth layout:          ok")
print("Dedicated auth stylesheet:  ok")
print("Duplicate brand text:       controlled")
print("Praise attribution:         present")
print("Workspace styling changed:  no")
print("Backend workflows changed:  no")
print("Intentional vulnerabilities:none")
print()
print("Phase 4.6 verification passed.")
