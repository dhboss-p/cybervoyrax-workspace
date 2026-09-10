from pathlib import Path

root=Path(__file__).resolve().parents[1]
checks={
    "completion stylesheet": "phase52d-complete.css" in (root/"app/templates/base.html").read_text(),
    "plain count treatment": "background:transparent!important" in (root/"app/static/css/phase52d-complete.css").read_text(),
    "member identity stack": ".member-line>div>strong,.member-line>div>small{display:block}" in (root/"app/static/css/phase52d-complete.css").read_text(),
    "compact unsupported file summary": 'class="file-summary"' in (root/"app/templates/documents/detail.html").read_text(),
    "real preview surface": 'class="document-preview"' in (root/"app/templates/documents/detail.html").read_text(),
    "human file type helper": "def human_file_type" in (root/"app/routes/ui.py").read_text(),
    "human file size helper": "def human_file_size" in (root/"app/routes/ui.py").read_text(),
    "formatted upload timestamp": "uploaded_label" in (root/"app/routes/ui.py").read_text(),
}
print("CYBERVOYRAX Phase 5.2D Completion Verification")
failed=[]
for name,ok in checks.items():
    print(f"{name:34} {'ok' if ok else 'FAILED'}")
    if not ok: failed.append(name)
if failed:
    raise SystemExit("Failed: "+", ".join(failed))
print("Phase 5.2D completion verification passed.")
