from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
css = ROOT / "app/static/css/manrope-local.css"
base = (ROOT / "app/templates/base.html").read_text(encoding="utf-8")
dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
phase = (ROOT / "app/static/css/phase52d.css").read_text(encoding="utf-8")
font_dir = ROOT / "app/static/fonts/manrope"
font_files = list(font_dir.glob("*.woff2"))
font_css = css.read_text(encoding="utf-8") if css.exists() else ""

checks = {
    "Local Manrope stylesheet": css.exists() and "@font-face" in font_css and "Manrope" in font_css,
    "Local Manrope WOFF2 assets": bool(font_files) and all(f.stat().st_size > 1000 for f in font_files),
    "Base template loads local font CSS": "css/manrope-local.css" in base,
    "Product stack selects Manrope": '--font-product:"Manrope"' in phase,
    "Docker build fetches Manrope": "python scripts/fetch_manrope.py" in dockerfile,
}

print("CYBERVOYRAX Phase 5.2D.1 Verification")
failed = False
for label, ok in checks.items():
    print(f"{label + ':':36} {'ok' if ok else 'FAILED'}")
    failed |= not ok
if failed:
    raise SystemExit(1)
print("Phase 5.2D.1 verification passed.")
