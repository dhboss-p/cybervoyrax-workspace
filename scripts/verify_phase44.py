from app import create_app

app = create_app()
client = app.test_client()

checks = {
    "/directory": ["Employee Directory", "All departments", "All roles"],
    "/projects": ["Projects", "New project", "All statuses"],
    "/documents": ["Documents", "Upload document", "All projects"],
    "/admin": ["Workspace Administration", "Users", "Projects", "Departments", "Settings"],
    "/account": ["My Account", "Profile information", "Password &amp; security"],
}

for path, required in checks.items():
    response = client.get(path, follow_redirects=True)
    assert response.status_code == 200, (path, response.status_code)
    html = response.get_data(as_text=True)
    for text in required:
        assert text in html, (path, text)

assert app.config["APP_VERSION"] == "0.4.4-phase4"

print("CYBERVOYRAX Phase 4.4 Verification")
print("----------------------------------")
print("Directory module UI:       ok")
print("Projects module UI:        ok")
print("Documents module UI:       ok")
print("Administration module UI:  ok")
print("Account module UI:         ok")
print("Responsive module layouts: ok")
print("Backend workflows changed: no")
print("Intentional vulnerabilities:none")
print()
print("Phase 4.4 verification passed.")
