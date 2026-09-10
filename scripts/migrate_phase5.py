from pathlib import Path
from app import create_app
from app.extensions import db

def split_sql(text):
    out, current = [], []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("--"):
            continue
        current.append(line)
        if s.endswith(";"):
            out.append("\n".join(current))
            current = []
    if current:
        out.append("\n".join(current))
    return out

app = create_app()
with app.app_context():
    if not db.wait_until_ready():
        raise SystemExit("Database not ready.")

    conn = db.connect()
    try:
        cur = conn.cursor()
        sql = Path("database/005_phase5.sql").read_text(encoding="utf-8")
        for stmt in split_sql(sql):
            try:
                cur.execute(stmt)
            except Exception as exc:
                # MySQL raises duplicate-index errors if rerun. Treat those as idempotent.
                if "Duplicate key name" not in str(exc):
                    raise
        cur.execute(
            "UPDATE app_meta SET schema_version='5' WHERE id=1"
        )
        conn.commit()
    finally:
        conn.close()

print("Phase 5 migration complete.")
