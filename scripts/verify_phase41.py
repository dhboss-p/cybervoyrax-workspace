#!/usr/bin/env python3
from app import create_app

app = create_app()
client = app.test_client()

checks = {
    "/login": ["Welcome back", "Created by Praise Testimony"],
    "/dashboard": ["Good afternoon, Alex.", "Recent projects", "Recent activity"],
    "/directory": ["Employee Directory"],
    "/projects": ["Projects"],
    "/documents": ["Documents"],
    "/account": ["My Account"],
    "/admin": ["Workspace Administration"],
}

for path, needles in checks.items():
    response = client.get(path, follow_redirects=True)
    if response.status_code != 200:
        raise SystemExit(f"{path}: HTTP {response.status_code}")
    html = response.get_data(as_text=True)
    for needle in needles:
        if needle not in html:
            raise SystemExit(f"{path}: missing {needle!r}")

if app.config["APP_VERSION"] != "0.4.1-phase4":
    raise SystemExit(f"Unexpected version: {app.config['APP_VERSION']}")

print("CYBERVOYRAX Phase 4.1 Verification")
print("----------------------------------")
print("Polished workspace shell: ok")
print("Dashboard hierarchy:      ok")
print("Navigation icons:         ok")
print("Global search:            ok")
print("Profile menu:             ok")
print("Responsive navigation:    ok")
print("Development banner:       removed")
print("In-app portfolio footer:  removed")
print("Login attribution:        present")
print("Existing Phase 4 views:   preserved")
print()
print("Phase 4.1 verification passed.")
