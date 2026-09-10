from types import SimpleNamespace

from app import create_app

app = create_app()
assert "csrf_token" in app.jinja_env.globals, "csrf_token is not registered as a Jinja global"

# Render the same imported workspace macro that previously failed. The fixture
# mirrors the attributes the real template expects from current_user.
with app.test_request_context("/dashboard"):
    user = SimpleNamespace(
        first_name="Test",
        last_name="User",
        full_name="Test User",
        email="test@cybervoyrax.local",
        role="Member",
    )
    tmpl = app.jinja_env.from_string(
        '{% from "_workspace.html" import topnav %}{{ topnav("dashboard", current_user) }}'
    )
    rendered = tmpl.render(current_user=user)
    assert 'name="_csrf_token"' in rendered, "workspace macro did not render CSRF field"
    assert 'value="' in rendered, "workspace macro rendered an empty CSRF field"

print("Phase 6.2 CSRF/Jinja hotfix verification passed.")
