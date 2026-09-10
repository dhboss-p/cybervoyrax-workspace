from pathlib import Path

root=Path(__file__).resolve().parents[1]
checks={
    "Phase 5.2C stylesheet": "phase52c.css" in (root/'app/templates/base.html').read_text(),
    "Top navigation shell": "workspace-header" in (root/'app/templates/_workspace.html').read_text(),
    "Project-first home": "My Projects" in (root/'app/templates/dashboard.html').read_text() and "summary-card" not in (root/'app/templates/dashboard.html').read_text(),
    "Iconless recent work": "Recent Work" in (root/'app/templates/dashboard.html').read_text() and "file-icon" not in (root/'app/templates/dashboard.html').read_text(),
    "Project workspace tabs": all(x in (root/'app/templates/projects/detail.html').read_text() for x in ["Overview","Documents","Members","Activity"]),
    "Projects list and board": all(x in (root/'app/templates/projects/index.html').read_text() for x in ["data-project-list","data-project-board"]),
    "People object list": "person-row" in (root/'app/templates/directory/index.html').read_text(),
    "Document object list": "document-row" in (root/'app/templates/documents/index.html').read_text(),
    "Inbox product surface": "Inbox" in (root/'app/templates/notifications.html').read_text(),
    "Account settings layout": "settings-layout" in (root/'app/templates/account/index.html').read_text(),
    "Admin same product language": "admin-workspace-line" in (root/'app/templates/admin/index.html').read_text() and "admin-stat-grid" not in (root/'app/templates/admin/index.html').read_text(),
    "Fast interaction motion": "transition:" in (root/'app/static/css/phase52c.css').read_text() and "animation-delay" not in (root/'app/static/css/phase52c.css').read_text(),
    "No remote workspace imagery": "images.pexels.com" not in ''.join(p.read_text(errors='ignore') for p in (root/'app').rglob('*') if p.is_file() and p.suffix in {'.css','.html','.js'}),
}
print("CYBERVOYRAX Phase 5.2C Verification")
failed=[]
for name,ok in checks.items():
    print(f"{name + ':':34} {'ok' if ok else 'FAILED'}")
    if not ok: failed.append(name)
if failed:
    raise SystemExit("Phase 5.2C verification failed: "+", ".join(failed))
print("Phase 5.2C verification passed.")
