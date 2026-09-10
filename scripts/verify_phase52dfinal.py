from pathlib import Path

root=Path(__file__).resolve().parents[1]
checks={
    "final stylesheet": "phase52d-final.css" in (root/"app/templates/base.html").read_text(),
    "hero copy block": "class=\"hero-copy\"" in (root/"app/templates/dashboard.html").read_text(),
    "footer": "workspace-footer" in (root/"app/templates/_workspace.html").read_text(),
    "footer routes": all(x in (root/"app/routes/ui.py").read_text() for x in ['@ui_bp.get("/privacy")','@ui_bp.get("/terms")','@ui_bp.get("/security")','@ui_bp.get("/help")','@ui_bp.get("/status")']),
    "text nav": '<i>{{icon("projects")}}</i>' not in (root/"app/templates/_workspace.html").read_text(),
    "project avatars": "p.members[:4]" in (root/"app/templates/projects/index.html").read_text(),
    "people project links": "data-project-href" in (root/"app/templates/directory/index.html").read_text(),
    "recent work ending": "You’re all caught up" in (root/"app/templates/dashboard.html").read_text(),
    "info pages": (root/"app/templates/info.html").exists() and (root/"app/templates/status.html").exists(),
}
print("CYBERVOYRAX Phase 5.2D Final Verification")
for name,ok in checks.items(): print(f"{name:24}: {'ok' if ok else 'FAIL'}")
if not all(checks.values()): raise SystemExit(1)
print("Phase 5.2D final verification passed.")
