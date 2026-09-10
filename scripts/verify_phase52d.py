from pathlib import Path
root=Path(__file__).resolve().parents[1]
checks={
 "Phase 5.2D stylesheet": (root/'app/static/css/phase52d.css').exists(),
 "Local hero image": (root/'app/static/images/workspace-hero.webp').exists(),
 "Base loads 5.2D": 'phase52d.css' in (root/'app/templates/base.html').read_text(),
 "No dashboard marketing quote": 'Disciplined work today' not in (root/'app/templates/dashboard.html').read_text(),
 "Grouped activity markup": 'feed-continuation' in (root/'app/templates/dashboard.html').read_text(),
 "People project context": 'person-projects' in (root/'app/templates/directory/index.html').read_text(),
 "People route relationships": 'GROUP_CONCAT' in (root/'app/routes/ui.py').read_text(),
 "Document date hierarchy": 'document-access' in (root/'app/templates/documents/index.html').read_text(),
 "Admin local appearance preview": 'appearance-preview' in (root/'app/templates/admin/settings.html').read_text(),
 "Fast interaction motion": '125ms' in (root/'app/static/css/phase52d.css').read_text(),
}
print('CYBERVOYRAX Phase 5.2D Verification')
failed=[]
for name,ok in checks.items():
 print(f'{name:<34} {"ok" if ok else "FAIL"}')
 if not ok: failed.append(name)
if failed: raise SystemExit('Phase 5.2D verification failed: '+', '.join(failed))
print('Phase 5.2D verification passed.')
