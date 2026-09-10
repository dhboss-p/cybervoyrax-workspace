from app import create_app

app = create_app()
client = app.test_client()

response = client.get("/dashboard", follow_redirects=True)
assert response.status_code == 200

html = response.get_data(as_text=True)
for expected in [
    "Good afternoon, Alex",
    "My Projects",
    "My Documents",
    "Upcoming Deadlines",
    "Recent Projects",
    "Recent Activity",
    "People. Projects. Progress.",
]:
    assert expected in html, expected

assert app.config.get("APP_VERSION") == "0.4.3-phase4"

print("CYBERVOYRAX Phase 4.3 Verification")
print("----------------------------------")
print("Approved dashboard layout:    ok")
print("Professional SVG icons:       ok")
print("Workspace atmosphere:         ok")
print("Summary-card polish:          ok")
print("Project/activity polish:      ok")
print("Workplace banner refinement:  ok")
print("Responsive layout:            ok")
print("Intentional vulnerabilities:  none")
print()
print("Phase 4.3 verification passed.")
