from pathlib import Path
print("CYBERVOYRAX Phase 5.2 UI Verification")
print("----------------------------------")
checks={
 "Phase 5.2 stylesheet":"app/static/css/phase52.css",
 "Designed error template":"app/templates/error.html",
 "Project product view":"app/templates/projects/detail.html",
 "Document product view":"app/templates/documents/detail.html",
 "Document upload UX":"app/templates/documents/upload.html",
}
for label,path in checks.items():
    assert Path(path).exists(), path
    print(f"{label+':':29} ok")
base=Path('app/templates/base.html').read_text(); assert 'phase52.css' in base
errors=Path('app/errors.py').read_text()
for code in ('400','401','403','404','405','500'): assert f'errorhandler({code})' in errors
assert 'workspace_start("documents",current_user)' in Path('app/templates/documents/index.html').read_text()
print(f"{'Standard error coverage:':29} ok")
print(f"{'Documents user context:':29} ok")
print("\nPhase 5.2 UI verification passed.")
