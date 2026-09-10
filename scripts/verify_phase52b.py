from pathlib import Path

root=Path(__file__).resolve().parents[1]

def text(rel): return (root/rel).read_text()

print("CYBERVOYRAX Phase 5.2B Shell Verification")
print("---------------------------------------")
checks={
    "Top navigation shell": all(x in text("app/templates/_workspace.html") for x in ["workspace-header","Home","People","Projects","Documents"]),
    "Legacy sidebar removed": "<aside class=\"sidebar\"" not in text("app/templates/_workspace.html"),
    "Admin moved to profile menu": "Workspace administration" in text("app/templates/_workspace.html"),
    "Workspace search shortcut": "<kbd>/</kbd>" in text("app/templates/_workspace.html"),
    "Motion stylesheet": all(x in text("app/static/css/phase52b.css") for x in ["cvx-page-in","cvx-panel-in","prefers-reduced-motion"]),
    "Motion stylesheet loaded": "phase52b.css" in text("app/templates/base.html"),
    "Profile menu motion wiring": "aria-expanded" in text("app/static/js/app.js"),
    "Mobile navigation wiring": "data-mobile-nav-toggle" in text("app/templates/_workspace.html") and "closeMobile" in text("app/static/js/app.js"),
    "Upload drag feedback": "is-dragover" in text("app/static/js/app.js"),
    "No emoji UI controls": "☰" not in text("app/templates/_workspace.html"),
}
for name,ok in checks.items():
    print(f"{name+':':31} {'ok' if ok else 'FAIL'}")
    assert ok,name
print("Phase 5.2B shell verification passed.")
