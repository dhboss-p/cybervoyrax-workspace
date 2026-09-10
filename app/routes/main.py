from datetime import datetime
from flask import (
    Blueprint, current_app, make_response, redirect, render_template,
    request, url_for
)

from app.auth_context import login_required, load_current_user
from app.extensions import db
from app.services.container import build_services
from app.services.errors import AuthenticationError

main_bp = Blueprint("main", __name__)

@main_bp.get("/")
def index():
    return redirect(url_for("main.dashboard") if load_current_user() else url_for("main.login"))

@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if load_current_user():
        return redirect(url_for("main.dashboard"))

    error = None
    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        remember = request.form.get("remember_me") == "on"
        try:
            token, expires = build_services()["auth"].authenticate(
                email, password, remember, request.cookies.get(current_app.config["AUTH_COOKIE_NAME"])
            )
            destination = request.form.get("next") or request.args.get("next") or url_for("main.dashboard")
            response = make_response(redirect(destination))
            response.set_cookie(
                current_app.config["AUTH_COOKIE_NAME"],
                token,
                expires=expires if remember else None,
                httponly=True,
                samesite="Lax",
                secure=False,
            )
            return response
        except AuthenticationError as exc:
            error = exc.message

    return render_template("login.html", error=error)

@main_bp.post("/logout")
def logout():
    token = request.cookies.get(current_app.config["AUTH_COOKIE_NAME"])
    build_services()["auth"].logout(token)
    response = make_response(redirect(url_for("main.login")))
    response.delete_cookie(current_app.config["AUTH_COOKIE_NAME"])
    return response

@main_bp.get("/dashboard")
@login_required
def dashboard():
    user = load_current_user()
    services = build_services()
    visible_projects = services["projects"].list_visible_projects(user)

    project_rows = []
    for p in visible_projects[:6]:
        department = db.fetch_one("SELECT name FROM departments WHERE id=%s", (p.department_id,))
        lead = db.fetch_one("SELECT id, first_name, last_name FROM users WHERE id=%s", (p.manager_user_id,))
        members = db.fetch_all("""
            SELECT u.id,u.first_name,u.last_name
            FROM project_members pm
            JOIN users u ON u.id=pm.user_id
            WHERE pm.project_id=%s
            ORDER BY CASE WHEN u.id=%s THEN 0 ELSE 1 END,u.first_name,u.last_name
            LIMIT 5
        """, (p.id, p.manager_user_id))
        doc_count = db.fetch_one("SELECT COUNT(*) total FROM documents WHERE project_id=%s", (p.id,))["total"]
        raw = db.fetch_one("SELECT description FROM projects WHERE id=%s", (p.id,))
        project_rows.append({
            "id": p.id, "name": p.name, "status": p.status,
            "department": department["name"] if department else "Workspace",
            "lead": f"{lead['first_name']} {lead['last_name']}" if lead else "Workspace",
            "lead_id": p.manager_user_id, "members": members, "document_count": doc_count,
            "description": (raw or {}).get("description") or "Workspace project",
            "starts_on": p.starts_on, "due_on": p.due_on,
        })

    recent_activity = db.fetch_all("""
        SELECT a.summary,a.event_type,a.entity_type,a.entity_id,a.created_at,
               u.id actor_id,u.first_name,u.last_name,
               CONCAT(u.first_name,' ',u.last_name) actor_name
        FROM activity_logs a
        LEFT JOIN users u ON u.id=a.actor_user_id
        ORDER BY a.created_at DESC LIMIT 8
    """)

    recent_work = db.fetch_all("""
        SELECT a.summary,a.event_type,a.entity_type,a.entity_id,a.created_at,
               CONCAT(u.first_name,' ',u.last_name) actor_name,
               CASE WHEN a.entity_type='project' THEN p.name
                    WHEN a.entity_type='document' THEN dp.name ELSE NULL END context_name
        FROM activity_logs a
        LEFT JOIN users u ON u.id=a.actor_user_id
        LEFT JOIN projects p ON a.entity_type='project' AND p.id=a.entity_id
        LEFT JOIN documents d ON a.entity_type='document' AND d.id=a.entity_id
        LEFT JOIN projects dp ON dp.id=d.project_id
        ORDER BY a.created_at DESC LIMIT 10
    """)

    upcoming = sorted(
        [r for r in project_rows if r["status"] in ("ACTIVE", "PLANNING") and r["due_on"]],
        key=lambda r: r["due_on"]
    )[:4]

    return render_template(
        "dashboard.html", projects=project_rows, project_count=len(visible_projects),
        recent_activity=recent_activity, recent_work=recent_work, upcoming=upcoming,
        current_user=user, now=datetime.now(),
    )

@main_bp.get("/search")
@login_required
def search():
    user = load_current_user()
    q = request.args.get("q", "").strip()
    people, projects, documents = [], [], []
    if q:
        like = f"%{q}%"
        people_sql = f"""
            SELECT u.id,u.first_name,u.last_name,u.job_title,d.name AS department
            FROM users u JOIN departments d ON d.id=u.department_id
            WHERE CONCAT(u.first_name,' ',u.last_name) LIKE '%{q}%'
               OR u.job_title LIKE '%{q}%' OR d.name LIKE '%{q}%'
            ORDER BY u.first_name,u.last_name LIMIT 10
        """
        people = db.fetch_all(people_sql)

        all_projects = build_services()["projects"].list_visible_projects(user)
        projects = [p for p in all_projects if q.lower() in p.name.lower()][:10]

        candidate_docs = db.fetch_all("""
            SELECT id,title,original_filename,owner_user_id,project_id,visibility,mime_type,file_size_bytes,document_code
            FROM documents
            WHERE title LIKE %s OR original_filename LIKE %s
            ORDER BY uploaded_at DESC LIMIT 30
        """, (like, like))
        from app.models import Document
        from app.services.authorization import can_view_document
        repo = build_services()["project_repository"]
        for row in candidate_docs:
            doc = Document(
                id=row["id"], document_code=row["document_code"], title=row["title"],
                owner_user_id=row["owner_user_id"], project_id=row["project_id"],
                visibility=row["visibility"], original_filename=row["original_filename"],
                mime_type=row["mime_type"], file_size_bytes=row["file_size_bytes"]
            )
            if can_view_document(user, doc, repo):
                documents.append(row)
            if len(documents) >= 10:
                break

    return render_template("search.html", q=q, people=people, projects=projects, documents=documents, current_user=user)

@main_bp.get("/activity")
@login_required
def activity():
    user = load_current_user()
    rows = db.fetch_all("""
        SELECT a.summary,a.event_type,a.created_at,
               CONCAT(u.first_name,' ',u.last_name) AS actor_name
        FROM activity_logs a
        LEFT JOIN users u ON u.id=a.actor_user_id
        ORDER BY a.created_at DESC LIMIT 40
    """)
    return render_template("activity.html", activity=rows, current_user=user)

@main_bp.route("/notifications", methods=["GET", "POST"])
@login_required
def notifications():
    user = load_current_user()
    if request.method == "POST":
        db.execute("UPDATE notifications SET is_read=TRUE WHERE user_id=%s", (user.id,))
        return redirect(url_for("main.notifications"))

    rows = db.fetch_all("""
        SELECT id,title,body,link_url,is_read,created_at
        FROM notifications
        WHERE user_id=%s
        ORDER BY created_at DESC LIMIT 30
    """, (user.id,))
    return render_template("notifications.html", notifications=rows, current_user=user)
