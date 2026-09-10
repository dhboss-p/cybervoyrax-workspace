from pathlib import Path
from app import create_app
from app.extensions import db


def split_statements(sql_text):
    statements = []
    current = []

    for line in sql_text.splitlines():
        stripped = line.strip()

        if not stripped or stripped.startswith("--"):
            continue

        current.append(line)

        if stripped.endswith(";"):
            statements.append("\n".join(current))
            current = []

    if current:
        statements.append("\n".join(current))

    return statements


app = create_app()

with app.app_context():
    if not db.wait_until_ready():
        raise SystemExit("Database did not become ready in time.")

    conn = db.connect()

    try:
        cur = conn.cursor(dictionary=True)

        # Phase 1 used a tiny key/value app_meta table. It contains no user data,
        # so replace only that legacy metadata table before creating the Phase 2
        # versioned metadata structure.
        cur.execute("SHOW TABLES LIKE 'app_meta'")
        if cur.fetchone():
            cur.execute("SHOW COLUMNS FROM app_meta")
            columns = {row["Field"] for row in cur.fetchall()}

            if "meta_key" in columns and "schema_version" not in columns:
                cur.execute("DROP TABLE app_meta")
                conn.commit()

        sql_path = Path("database/002_schema.sql")
        sql = sql_path.read_text(encoding="utf-8")

        cur = conn.cursor()
        for stmt in split_statements(sql):
            cur.execute(stmt)

        conn.commit()
    finally:
        conn.close()

print("Phase 2 schema migration complete.")
