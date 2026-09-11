from pathlib import Path
from app import create_app

app=create_app()
assert app.config["APP_VERSION"]=="0.6.4-phase6.4"
assert str(app.config["APP_PHASE"])=="6.4"
endpoints={rule.endpoint for rule in app.url_map.iter_rules()}
for endpoint in ["ui.project_comment_edit","ui.project_comment_delete","ui.document_delete"]:
    assert endpoint in endpoints, f"missing endpoint: {endpoint}"
ui=Path("app/routes/ui.py").read_text(errors="ignore")
tpl=Path("app/templates/projects/detail.html").read_text(errors="ignore")
css=Path("app/static/css/phase64.css")
assert "updated_at=%s" in ui
assert "p.unlink()" in ui
assert "data-comment-edit" in tpl
assert "return_to_project" in tpl
assert css.exists()
print("CYBERVOYRAX Workspace Phase 6.4 verification passed.")
print("Comment edit/delete, owned document deletion, and activity UI upgrade are installed.")
print("No database reset required; runtime instance data remains separate from source.")
