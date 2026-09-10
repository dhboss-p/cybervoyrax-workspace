from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks={
 'phase53 stylesheet': 'phase53.css' in (root/'app/templates/base.html').read_text(),
 'publication permission': 'Learning and publication' in (root/'app/routes/ui.py').read_text(),
 'privacy baseline': 'Administrator visibility' in (root/'app/routes/ui.py').read_text(),
 'security isolation': 'Use an isolated lab' in (root/'app/routes/ui.py').read_text(),
 'status database': '("Database","Operational")' in (root/'app/routes/ui.py').read_text(),
 'status metadata': 'Phase 5 baseline' in (root/'app/templates/status.html').read_text(),
 'safe 403 copy': 'You do not have permission to access this area.' in (root/'app/templates/error.html').read_text(),
 'human admin login': "strftime('%b %d, %Y at %-I:%M %p')" in (root/'app/templates/admin/user_detail.html').read_text(),
 'danger hierarchy': '.button-danger' in (root/'app/static/css/phase53.css').read_text(),
 'tab count typography': '.project-tabs .section-count' in (root/'app/static/css/phase53.css').read_text(),
}
print('CYBERVOYRAX Phase 5.3 Product Baseline Verification')
for k,v in checks.items(): print(f'{k:24} {"ok" if v else "FAIL"}')
if not all(checks.values()): raise SystemExit(1)
print('Phase 5.3 baseline verification passed.')
