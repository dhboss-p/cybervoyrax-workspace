import mimetypes, uuid, json, socket, sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request as UrlRequest, urlopen
from urllib.error import URLError
from flask import Blueprint,current_app,flash,redirect,render_template,request,send_file,url_for
from werkzeug.utils import secure_filename
from app.auth_context import login_required,load_current_user,roles_required
from app.extensions import db
from app.services.authorization import require_document_access,require_project_access,require_project_lead
from app.services.container import build_services
from app.services.security import hash_password,verify_password

ui_bp=Blueprint("ui",__name__)

def activity(actor,event_type,entity_type,entity_id,summary):
    db.execute("""INSERT INTO activity_logs(actor_user_id,event_type,entity_type,entity_id,summary,created_at)
                  VALUES(%s,%s,%s,%s,%s,%s)""",(actor,event_type,entity_type,entity_id,summary,datetime.now()))
def notify(uid,title,body,link=None):
    db.execute("""INSERT INTO notifications(user_id,title,body,link_url,is_read,created_at)
                  VALUES(%s,%s,%s,%s,FALSE,%s)""",(uid,title,body,link,datetime.now()))
def docrow(did):
    return db.fetch_one("""SELECT d.*,CONCAT(u.first_name,' ',u.last_name) owner_name,p.name project_name
                           FROM documents d JOIN users u ON u.id=d.owner_user_id
                           LEFT JOIN projects p ON p.id=d.project_id WHERE d.id=%s""",(did,))
def docpath(row):
    return Path(current_app.config["UPLOAD_FOLDER"])/row["stored_filename"] if row and row.get("stored_filename") else None

def human_file_type(filename, mime):
    ext=Path(filename or "").suffix.lower()
    labels={
        ".docx":"Microsoft Word document",
        ".xlsx":"Microsoft Excel workbook",
        ".csv":"CSV spreadsheet",
        ".pdf":"PDF document",
        ".txt":"Plain text document",
        ".png":"PNG image",
        ".jpg":"JPEG image",
        ".jpeg":"JPEG image",
        ".webp":"WebP image",
    }
    if ext in labels:
        return labels[ext]
    if mime and mime.startswith("image/"):
        return "Image"
    if mime and mime.startswith("text/"):
        return "Text document"
    return "File"

def human_file_size(size):
    try:
        size=float(size or 0)
    except (TypeError,ValueError):
        return "Unknown size"
    units=["bytes","KB","MB","GB"]
    idx=0
    while size >= 1024 and idx < len(units)-1:
        size/=1024.0; idx+=1
    if idx==0:
        return f"{int(size)} {units[idx]}"
    return f"{size:.1f} {units[idx]}" if size < 10 else f"{size:.0f} {units[idx]}"

@ui_bp.get("/directory")
@login_required
def directory_page():
    q=request.args.get("q","").strip(); dep=request.args.get("department","").strip(); role=request.args.get("role","").strip()
    sql="""SELECT u.id,u.first_name,u.last_name,u.job_title,u.office_location,d.name department,r.name role,
           GROUP_CONCAT(DISTINCT p.name ORDER BY p.name SEPARATOR ' · ') project_names
           FROM users u JOIN departments d ON d.id=u.department_id JOIN roles r ON r.id=u.role_id
           LEFT JOIN project_members pm ON pm.user_id=u.id LEFT JOIN projects p ON p.id=pm.project_id WHERE 1=1"""
    params=[]
    if q:
        like=f"%{q}%"; sql+=" AND (CONCAT(u.first_name,' ',u.last_name) LIKE %s OR u.job_title LIKE %s OR d.name LIKE %s)"; params += [like,like,like]
    if dep: sql+=" AND d.name=%s"; params.append(dep)
    if role: sql+=" AND r.name=%s"; params.append(role)
    sql+=" GROUP BY u.id,u.first_name,u.last_name,u.job_title,u.office_location,d.name,r.name ORDER BY u.first_name,u.last_name"
    users=db.fetch_all(sql,tuple(params))
    for u in users:
        u["connections"]=db.fetch_all("""SELECT p.id,p.name FROM project_members pm JOIN projects p ON p.id=pm.project_id
                                           WHERE pm.user_id=%s ORDER BY p.name LIMIT 4""",(u["id"],))
    return render_template("directory/index.html",users=users,
        departments=db.fetch_all("SELECT name FROM departments ORDER BY name"),
        roles=db.fetch_all("SELECT name FROM roles ORDER BY id"),current_user=load_current_user())

@ui_bp.get("/directory/<int:user_id>")
@login_required
def directory_profile_page(user_id):
    user=db.fetch_one("""SELECT u.id,u.first_name,u.last_name,u.job_title,u.email,u.bio,u.office_location,
                         d.name department,r.name role FROM users u JOIN departments d ON d.id=u.department_id
                         JOIN roles r ON r.id=u.role_id WHERE u.id=%s""",(user_id,))
    if not user: return render_template("error.html",status_code=404,message="Employee not found."),404
    projects=db.fetch_all("""SELECT p.id,p.name,p.status,pm.membership_role,
                             CASE WHEN p.manager_user_id=%s THEN 'Project lead' ELSE pm.membership_role END project_role
                             FROM project_members pm JOIN projects p ON p.id=pm.project_id
                             WHERE pm.user_id=%s ORDER BY p.name LIMIT 8""",(user_id,user_id))
    manager=db.fetch_one("""SELECT m.id,m.first_name,m.last_name,m.job_title FROM users u
                            LEFT JOIN users m ON m.id=u.manager_user_id WHERE u.id=%s""",(user_id,))
    recent=db.fetch_all("""SELECT summary,event_type,created_at FROM activity_logs
                            WHERE actor_user_id=%s ORDER BY created_at DESC LIMIT 8""",(user_id,))
    return render_template("directory/profile.html",user=user,projects=projects,manager=manager,recent_activity=recent,current_user=load_current_user())

@ui_bp.get("/projects")
@login_required
def projects_page():
    user=load_current_user(); services=build_services(); rows=[]
    for p in services["projects"].list_visible_projects(user):
        dep=db.fetch_one("SELECT name FROM departments WHERE id=%s",(p.department_id,))
        mgr=db.fetch_one("SELECT CONCAT(first_name,' ',last_name) name FROM users WHERE id=%s",(p.manager_user_id,))
        raw=db.fetch_one("SELECT description FROM projects WHERE id=%s",(p.id,))
        counts=db.fetch_one("""SELECT
            (SELECT COUNT(*) FROM project_members WHERE project_id=%s) members,
            (SELECT COUNT(*) FROM documents WHERE project_id=%s) documents""",(p.id,p.id))
        members=db.fetch_all("""SELECT u.first_name,u.last_name FROM project_members pm JOIN users u ON u.id=pm.user_id
                              WHERE pm.project_id=%s ORDER BY CASE WHEN u.id=%s THEN 0 ELSE 1 END,u.first_name,u.last_name LIMIT 5""",(p.id,p.manager_user_id))
        rows.append({"id":p.id,"project_code":p.project_code,"name":p.name,"status":p.status,"visibility":p.visibility,
                     "department":dep["name"],"manager_name":mgr["name"],"starts_on":p.starts_on,"due_on":p.due_on,
                     "description":(raw or {}).get("description") or "Workspace project",
                     "members":members,"member_count":counts["members"],"document_count":counts["documents"]})
    return render_template("projects/index.html",projects=rows,current_user=user)

@ui_bp.route("/projects/new",methods=["GET","POST"])
@login_required
def project_new_page():
    user=load_current_user()
    # Any authenticated user may create a project and becomes its project lead.
    if request.method=="POST":
        name=request.form.get("name","").strip(); due=request.form.get("due_on")
        if not name or not due: flash("Project name and due date are required.","error")
        else:
            dep=db.fetch_one("SELECT department_id FROM users WHERE id=%s",(user.id,))["department_id"]
            pid,_=db.execute("""INSERT INTO projects(project_code,name,description,status,visibility,manager_user_id,department_id,starts_on,due_on)
                               VALUES(%s,%s,%s,%s,%s,%s,%s,CURDATE(),%s)""",
                               (f"CVX-P{uuid.uuid4().hex[:5].upper()}",name,request.form.get("description","").strip(),
                                request.form.get("status","PLANNING"),request.form.get("visibility","MEMBERS"),user.id,dep,due))
            db.execute("INSERT IGNORE INTO project_members(project_id,user_id,membership_role) VALUES(%s,%s,'CONTRIBUTOR')",(pid,user.id))
            activity(user.id,"PROJECT_CREATED","project",pid,f"created project {name}.")
            return redirect(url_for("ui.project_detail_page",project_id=pid))
    return render_template("projects/form.html",mode="create",project=None,current_user=user)

@ui_bp.get("/projects/<int:project_id>")
@login_required
def project_detail_page(project_id):
    user=load_current_user(); s=build_services(); pobj=s["projects"].get_project(project_id); require_project_access(user,pobj,s["project_repository"])
    project=db.fetch_one("""SELECT p.*,d.name department,CONCAT(u.first_name,' ',u.last_name) manager_name
                            FROM projects p JOIN departments d ON d.id=p.department_id JOIN users u ON u.id=p.manager_user_id WHERE p.id=%s""",(project_id,))
    members=db.fetch_all("""SELECT u.id,u.first_name,u.last_name,u.job_title,pm.membership_role
                            FROM project_members pm JOIN users u ON u.id=pm.user_id WHERE pm.project_id=%s ORDER BY u.first_name,u.last_name""",(project_id,))
    comments=db.fetch_all("""SELECT pc.id,pc.body,pc.created_at,pc.author_user_id,CONCAT(u.first_name,' ',u.last_name) author_name
                             FROM project_comments pc JOIN users u ON u.id=pc.author_user_id WHERE pc.project_id=%s ORDER BY pc.created_at DESC LIMIT 40""",(project_id,))
    documents=db.fetch_all("SELECT id,title,original_filename,visibility,uploaded_at FROM documents WHERE project_id=%s ORDER BY uploaded_at DESC",(project_id,))
    project_activity=db.fetch_all("""SELECT a.summary,a.event_type,a.created_at,CONCAT(u.first_name,' ',u.last_name) actor_name
                                     FROM activity_logs a LEFT JOIN users u ON u.id=a.actor_user_id
                                     WHERE a.entity_type='project' AND a.entity_id=%s ORDER BY a.created_at DESC LIMIT 30""",(project_id,))
    available=db.fetch_all("SELECT id,CONCAT(first_name,' ',last_name) name FROM users WHERE account_status='ACTIVE' ORDER BY first_name,last_name")
    can_manage=user.role=="Administrator" or pobj.manager_user_id==user.id
    return render_template("projects/detail.html",project=project,members=members,comments=comments,documents=documents,
                           project_activity=project_activity,available_users=available,can_manage=can_manage,current_user=user)

@ui_bp.route("/projects/<int:project_id>/edit",methods=["GET","POST"])
@login_required
def project_edit_page(project_id):
    user=load_current_user(); s=build_services(); pobj=s["projects"].get_project(project_id); require_project_lead(user,pobj)
    if request.method=="POST":
        db.execute("UPDATE projects SET name=%s,description=%s,status=%s,visibility=%s,due_on=%s WHERE id=%s",
                   (request.form.get("name","").strip(),request.form.get("description","").strip(),request.form.get("status","ACTIVE"),
                    request.form.get("visibility","MEMBERS"),request.form.get("due_on"),project_id))
        activity(user.id,"PROJECT_UPDATED","project",project_id,"updated project information.")
        return redirect(url_for("ui.project_detail_page",project_id=project_id))
    return render_template("projects/form.html",mode="edit",project=db.fetch_one("SELECT * FROM projects WHERE id=%s",(project_id,)),current_user=user)

@ui_bp.post("/projects/<int:project_id>/status")
@login_required
def project_status_update(project_id):
    user=load_current_user(); s=build_services(); pobj=s["projects"].get_project(project_id); require_project_lead(user,pobj)
    requested=request.form.get("status","").strip().upper()
    if requested not in {"PLANNING","ACTIVE","COMPLETED","ARCHIVED"}:
        return render_template("error.html",status_code=400,message="Unsupported project status."),400
    # Apply the requested project state.
    db.execute("UPDATE projects SET status=%s WHERE id=%s",(requested,project_id))
    activity(user.id,"PROJECT_STATUS_CHANGED","project",project_id,f"changed project status to {requested}.")
    return redirect(url_for("ui.project_detail_page",project_id=project_id))

@ui_bp.post("/projects/<int:project_id>/comments")
@login_required
def project_comment(project_id):
    user=load_current_user(); s=build_services(); pobj=s["projects"].get_project(project_id); require_project_access(user,pobj,s["project_repository"])
    body=request.form.get("body","").strip()
    if body:
        db.execute("INSERT INTO project_comments(project_id,author_user_id,body,created_at) VALUES(%s,%s,%s,%s)",(project_id,user.id,body,datetime.now()))
        activity(user.id,"PROJECT_COMMENTED","project",project_id,"added a project comment."); flash("Comment posted.","success")
    else: flash("Comment cannot be empty.","error")
    return redirect(url_for("ui.project_detail_page",project_id=project_id))

@ui_bp.post("/projects/<int:project_id>/members")
@login_required
def project_add_member(project_id):
    user=load_current_user(); s=build_services(); pobj=s["projects"].get_project(project_id); require_project_lead(user,pobj)
    uid=int(request.form.get("user_id")); db.execute("INSERT IGNORE INTO project_members(project_id,user_id,membership_role) VALUES(%s,%s,'MEMBER')",(project_id,uid))
    notify(uid,"Added to project",f"You were added to {pobj.name}.",url_for("ui.project_detail_page",project_id=project_id))
    activity(user.id,"PROJECT_MEMBER_ADDED","project",project_id,"added a project member.")
    return redirect(url_for("ui.project_detail_page",project_id=project_id))

@ui_bp.post("/projects/<int:project_id>/members/<int:user_id>/remove")
@login_required
def project_remove_member(project_id,user_id):
    user=load_current_user(); s=build_services(); pobj=s["projects"].get_project(project_id); require_project_lead(user,pobj)
    if user_id!=pobj.manager_user_id:
        db.execute("DELETE FROM project_members WHERE project_id=%s AND user_id=%s",(project_id,user_id))
        activity(user.id,"PROJECT_MEMBER_REMOVED","project",project_id,"removed a project member.")
    return redirect(url_for("ui.project_detail_page",project_id=project_id))

@ui_bp.get("/documents")
@login_required
def documents_page():
    user=load_current_user(); rows=db.fetch_all("""SELECT d.*,CONCAT(u.first_name,' ',u.last_name) owner_name,p.name project_name
      FROM documents d JOIN users u ON u.id=d.owner_user_id LEFT JOIN projects p ON p.id=d.project_id ORDER BY d.uploaded_at DESC""")
    from app.models import Document
    from app.services.authorization import can_view_document
    repo=build_services()["project_repository"]; visible=[]
    for r in rows:
        d=Document(id=r["id"],document_code=r["document_code"],title=r["title"],owner_user_id=r["owner_user_id"],project_id=r["project_id"],
                   visibility=r["visibility"],original_filename=r["original_filename"],mime_type=r["mime_type"],file_size_bytes=r["file_size_bytes"])
        if can_view_document(user,d,repo): visible.append(r)
    return render_template("documents/index.html",documents=visible,current_user=user)

@ui_bp.route("/documents/upload",methods=["GET","POST"])
@login_required
def document_upload_page():
    user=load_current_user(); projects=build_services()["projects"].list_visible_projects(user)
    if request.method=="POST":
        f=request.files.get("file"); title=request.form.get("title","").strip()
        if not f or not f.filename or not title: flash("A file and title are required.","error")
        else:
            original=secure_filename(f.filename); ext=Path(original).suffix.lower()
            if ext not in {".pdf",".txt",".docx",".xlsx",".csv",".png",".jpg",".jpeg",".html",".htm",".svg",".xml"}: flash("That file type is not allowed.","error")
            else:
                stored=f"{uuid.uuid4().hex}{ext}"; folder=Path(current_app.config["UPLOAD_FOLDER"]); folder.mkdir(parents=True,exist_ok=True)
                path=folder/stored; f.save(path)
                did,_=db.execute("""INSERT INTO documents(document_code,title,stored_filename,original_filename,mime_type,file_size_bytes,description,
                   owner_user_id,project_id,visibility,uploaded_at) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                   (f"DOC-{uuid.uuid4().hex[:8].upper()}",title,stored,original,f.mimetype or mimetypes.guess_type(original)[0] or "application/octet-stream",
                    path.stat().st_size,request.form.get("description","").strip(),user.id,request.form.get("project_id") or None,
                    request.form.get("visibility","PROJECT_MEMBERS"),datetime.now()))
                activity(user.id,"DOCUMENT_UPLOADED","document",did,f"uploaded document {title}."); flash("Document uploaded.","success")
                return redirect(url_for("ui.document_detail_page",document_id=did))
    return render_template("documents/upload.html",projects=projects,current_user=user)

@ui_bp.get("/documents/<int:document_id>")
@login_required
def document_detail_page(document_id):
    user=load_current_user(); s=build_services(); dobj=s["documents"].get_document(document_id); require_document_access(user,dobj,s["project_repository"])
    row=docrow(document_id); path=docpath(row)
    mime=row["mime_type"] or mimetypes.guess_type(row["original_filename"])[0] or ""
    preview=bool(path and path.exists() and (mime.startswith("image/") or mime=="application/pdf" or mime.startswith("text/")))
    preview_kind="image" if mime.startswith("image/") else "pdf" if mime=="application/pdf" else "text" if mime.startswith("text/") else None
    file_type_label=human_file_type(row["original_filename"],mime)
    file_size_label=human_file_size(row["file_size_bytes"])
    uploaded_label=row["uploaded_at"].strftime("%b %d, %Y at %I:%M %p").replace(" 0", " ") if row.get("uploaded_at") else "Unknown"
    return render_template("documents/detail.html",document=row,can_delete=user.role=="Administrator" or row["owner_user_id"]==user.id,
                           can_preview=preview,preview_kind=preview_kind,file_type_label=file_type_label,
                           file_size_label=file_size_label,uploaded_label=uploaded_label,current_user=user)

@ui_bp.get("/documents/<int:document_id>/preview")
@login_required
def document_preview(document_id):
    user=load_current_user(); s=build_services(); dobj=s["documents"].get_document(document_id); require_document_access(user,dobj,s["project_repository"])
    row=docrow(document_id); path=docpath(row)
    if not path or not path.exists(): flash("Preview file is not available.","error"); return redirect(url_for("ui.document_detail_page",document_id=document_id))
    return send_file(path,mimetype=row["mime_type"] or mimetypes.guess_type(row["original_filename"])[0] or "application/octet-stream",
                     as_attachment=False,download_name=row["original_filename"])

@ui_bp.get("/documents/<int:document_id>/download")
@login_required
def document_download(document_id):
    user=load_current_user(); s=build_services(); dobj=s["documents"].get_document(document_id); require_document_access(user,dobj,s["project_repository"])
    row=docrow(document_id); path=docpath(row)
    legacy_source=request.args.get("source","").strip()
    if legacy_source:
        path=Path(current_app.config["UPLOAD_FOLDER"])/legacy_source
    if not path or not path.exists(): flash("The local document file is missing.","error"); return redirect(url_for("ui.document_detail_page",document_id=document_id))
    activity(user.id,"DOCUMENT_DOWNLOADED","document",document_id,f"downloaded {row['title']}.")
    return send_file(path,as_attachment=True,download_name=row["original_filename"],mimetype=row["mime_type"] or "application/octet-stream")

@ui_bp.post("/documents/<int:document_id>/delete")
@login_required
def document_delete(document_id):
    user=load_current_user(); row=docrow(document_id)
    if row and (user.role=="Administrator" or row["owner_user_id"]==user.id):
        p=docpath(row)
        if p and p.exists(): p.unlink()
        db.execute("DELETE FROM documents WHERE id=%s",(document_id,)); activity(user.id,"DOCUMENT_DELETED","document",document_id,"deleted a document."); flash("Document deleted.","success")
    return redirect(url_for("ui.documents_page"))

@ui_bp.get("/integrations/preview")
@login_required
def integration_preview():
    user=load_current_user(); target=request.args.get("url","").strip()
    result=None; error=None
    if target:
        try:
            req=UrlRequest(target,headers={"User-Agent":"CYBERVOYRAX-Workspace/0.6.3"})
            with urlopen(req,timeout=4) as response:
                raw=response.read(65536)
                content_type=response.headers.get("Content-Type","application/octet-stream")
                charset=response.headers.get_content_charset() or "utf-8"
                preview=raw.decode(charset,errors="replace")
                result={"url":response.geturl(),"status":getattr(response,"status",200),"content_type":content_type,"preview":preview[:12000]}
        except (URLError,ValueError,OSError) as exc:
            error=str(exc)
    return render_template("integration_preview.html",target=target,result=result,error=error,current_user=user)

@ui_bp.get("/api/workspace/runtime")
def workspace_runtime_metadata():
    return {
        "service":"workspace-web",
        "release":current_app.config["APP_VERSION"],
        "python":sys.version.split()[0],
        "hostname":socket.gethostname(),
        "database_host":current_app.config["MYSQL_HOST"],
        "upload_root":current_app.config["UPLOAD_FOLDER"],
    }

INFO_PAGES={
    "privacy": {"title":"Privacy","intro":"How information is handled inside a CYBERVOYRAX Workspace training instance.","sections":[
        ("Information in the workspace","The workspace stores fictional account profiles, departments, projects, project membership, documents, comments, notifications and activity records used to make the training environment behave like a real business application."),
        ("Administrator visibility","Administrators of a workspace instance can manage accounts and may view workspace information needed to operate the local training environment. Learners should assume activity performed inside their own lab instance can be visible to that instance's administrators."),
        ("Local training data","CYBERVOYRAX Workspace is designed for controlled lab use. Do not enter real passwords, confidential business information, personal records, production credentials or other sensitive data into an intentionally vulnerable instance."),
        ("Files and activity records","Documents uploaded to the workspace are stored by the local application. Actions such as project changes, comments and document activity may create local activity records for the workspace experience."),
        ("Your lab instance","The person or organization running a copy of CYBERVOYRAX Workspace controls that instance, its database, uploaded files and reset process. The training project does not require learners to submit lab content to a central CYBERVOYRAX service."),
    ]},
    "terms": {"title":"Terms of use","intro":"Conditions for using CYBERVOYRAX Workspace as a deliberately vulnerable training application.","sections":[
        ("Authorized use only","Use the application only on systems, networks and lab environments you own or are explicitly authorized to assess. The project does not grant permission to test unrelated third-party systems."),
        ("Training purpose","CYBERVOYRAX Workspace is provided for cybersecurity education, penetration-testing practice, secure-development study and controlled security assessments."),
        ("Learning and publication","You may document your testing, create reports and write-ups, record demonstrations, publish screenshots, and share findings from a CYBERVOYRAX Workspace instance that you own or are authorized to assess."),
        ("Safe deployment","Keep intentionally vulnerable instances isolated from the public internet and from systems that should not be exposed. Do not use the application to store real sensitive or production information."),
        ("No production warranty","The application is a training environment and is not intended to provide production-grade availability, confidentiality or security. Lab operators are responsible for their own deployment, isolation, backups and resets."),
    ]},
    "security": {"title":"Security","intro":"Security guidance for operating and assessing CYBERVOYRAX Workspace.","sections":[
        ("Deliberately vulnerable environment","CYBERVOYRAX Workspace is intentionally designed for controlled cybersecurity education and assessment. Some security weaknesses may be intentionally introduced as part of the training environment."),
        ("Use an isolated lab","Run the workspace locally or in a dedicated training network. Do not expose an intentionally vulnerable instance directly to the public internet or connect it to sensitive production resources."),
        ("Use fictional data","Seeded workspace data is fictional. Keep it that way: do not reuse real credentials or upload confidential, personal or production files to a training instance."),
        ("Responsible assessment","Test only the CYBERVOYRAX Workspace instance you own or have permission to assess. Security techniques learned here do not create authorization to test other systems."),
        ("Documenting findings","Learners are welcome to produce reports, demonstrations and public educational write-ups about findings from their authorized lab instances. Avoid publishing real secrets or data from systems outside the training environment."),
        ("Project issues","Unexpected implementation defects that are separate from the intended training design can be reported through the project's public repository and documentation channels."),
    ]},
    "help": {"title":"Help","intro":"Quick guidance for navigating and operating your local CYBERVOYRAX Workspace.","sections":[
        ("Getting around","Use Home for your current work, People for the company directory, Projects for collaborative work, and Documents for files you are permitted to access."),
        ("Projects and membership","Open a project to review its overview, documents, members and activity. Project leads can manage their own project where the workspace permits it."),
        ("Documents and access","Document visibility depends on the selected workspace access level and project relationship. If a document is unavailable, confirm that you are signed in with the intended fictional account."),
        ("Link previews","The workspace can preview remote reference links through the integrations preview page before they are shared with a project."),
        ("Account and password","Use the profile menu to review your account, update profile information and change your password. Administrators have additional workspace-administration options."),
        ("Running or resetting the lab","Setup, Docker startup, reset and troubleshooting instructions are included with the source repository. Reset the local environment whenever you need a clean fictional workspace."),
        ("Security practice","Treat the application like a normal business product during assessment. Record evidence, scope your testing to your own lab and document findings using the same process you would use in an authorized engagement."),
    ]},
}

@ui_bp.get("/privacy")
@ui_bp.get("/terms")
@ui_bp.get("/security")
@ui_bp.get("/help")
@login_required
def workspace_info_page():
    key=request.path.strip("/")
    return render_template("info.html",page=INFO_PAGES[key],current_user=load_current_user())

@ui_bp.get("/status")
@login_required
def workspace_status_page():
    checks=[("Web application","Operational"),("Authentication","Operational"),("Database","Operational"),("File storage","Operational"),("Notifications","Operational")]
    return render_template("status.html",checks=checks,checked_at=datetime.now(),current_user=load_current_user())

@ui_bp.get("/account")
@login_required
def account_page():
    user=load_current_user()
    row=db.fetch_one("""SELECT u.*,d.name department,r.name role FROM users u JOIN departments d ON d.id=u.department_id
                        JOIN roles r ON r.id=u.role_id WHERE u.id=%s""",(user.id,))
    return render_template("account/index.html",user=row,current_user=user)

@ui_bp.route("/account/profile",methods=["GET","POST"])
@login_required
def account_profile_page():
    user=load_current_user()
    if request.method=="POST":
        # Workspace profile editor accepts a shared set of account fields used by
        # Process profile fields submitted by supported clients.
        # field names for this training release.
        editable={
            "bio": lambda v: v.strip(),
            "office_location": lambda v: v.strip(),
            "job_title": lambda v: v.strip(),
            "department_id": int,
            "role_id": int,
            "account_status": lambda v: v.strip().upper(),
        }
        updates=[]; values=[]
        for field,convert in editable.items():
            if field in request.form and request.form.get(field)!="":
                updates.append(f"{field}=%s"); values.append(convert(request.form.get(field)))
        if updates:
            values.append(user.id)
            db.execute(f"UPDATE users SET {', '.join(updates)} WHERE id=%s",tuple(values))
        activity(user.id,"PROFILE_UPDATED","user",user.id,"updated their workspace profile."); flash("Profile updated.","success")
        return redirect(url_for("ui.account_page"))
    return render_template("account/profile.html",user=db.fetch_one("SELECT * FROM users WHERE id=%s",(user.id,)),current_user=user)

@ui_bp.route("/account/password",methods=["GET","POST"])
@login_required
def account_password_page():
    user=load_current_user(); error=None
    if request.method=="POST":
        cur=request.form.get("current_password",""); new=request.form.get("new_password",""); confirm=request.form.get("confirm_password","")
        row=db.fetch_one("SELECT password_hash FROM users WHERE id=%s",(user.id,))
        if not verify_password(cur,row["password_hash"]): error="Current password is incorrect."
        elif len(new)<8: error="New password must be at least 8 characters."
        elif new!=confirm: error="New passwords do not match."
        else:
            db.execute("UPDATE users SET password_hash=%s,account_status='ACTIVE' WHERE id=%s",(hash_password(new),user.id))
            activity(user.id,"PASSWORD_CHANGED","user",user.id,"changed their account password."); flash("Password changed.","success")
            return redirect(url_for("ui.account_page"))
    return render_template("account/password.html",error=error,current_user=user)

@ui_bp.get("/admin")
@roles_required("Administrator")
def admin_dashboard_page():
    stats={k:db.fetch_one(f"SELECT COUNT(*) total FROM {t}")["total"] for k,t in
      [("users","users"),("projects","projects"),("documents","documents"),("departments","departments")]}
    stats["administrators"]=db.fetch_one("""SELECT COUNT(*) total FROM users u JOIN roles r ON r.id=u.role_id WHERE r.name='Administrator'""")["total"]
    people=db.fetch_all("""SELECT u.id,u.first_name,u.last_name,u.job_title,u.account_status,d.name department,r.name role
                           FROM users u JOIN departments d ON d.id=u.department_id JOIN roles r ON r.id=u.role_id
                           ORDER BY u.updated_at DESC,u.first_name LIMIT 5""")
    departments=db.fetch_all("""SELECT d.id,d.name,COUNT(u.id) employee_count FROM departments d LEFT JOIN users u ON u.department_id=d.id
                                GROUP BY d.id,d.name ORDER BY d.name LIMIT 6""")
    recent=db.fetch_all("""SELECT a.summary,a.event_type,a.created_at,CONCAT(u.first_name,' ',u.last_name) actor_name
                           FROM activity_logs a LEFT JOIN users u ON u.id=a.actor_user_id ORDER BY a.created_at DESC LIMIT 6""")
    return render_template("admin/index.html",stats=stats,people=people,departments=departments,recent_activity=recent,current_user=load_current_user())

@ui_bp.get("/admin/users")
@roles_required("Administrator")
def admin_users_page():
    return render_template("admin/users.html",users=db.fetch_all("""SELECT u.id,u.employee_code,u.first_name,u.last_name,u.email,u.account_status,u.last_login_at,
      d.name department,r.name role FROM users u JOIN departments d ON d.id=u.department_id JOIN roles r ON r.id=u.role_id ORDER BY u.first_name,u.last_name"""),
      current_user=load_current_user())

@ui_bp.route("/admin/users/new",methods=["GET","POST"])
@roles_required("Administrator")
def admin_user_new():
    admin=load_current_user(); deps=db.fetch_all("SELECT id,name FROM departments ORDER BY name"); roles=db.fetch_all("SELECT id,name FROM roles WHERE name='User' ORDER BY id")
    if request.method=="POST":
        uid,_=db.execute("""INSERT INTO users(employee_code,email,password_hash,first_name,last_name,job_title,role_id,department_id,account_status)
                           VALUES(%s,%s,%s,%s,%s,%s,%s,%s,'PASSWORD_RESET_REQUIRED')""",
          (f"CVX-{uuid.uuid4().hex[:6].upper()}",request.form["email"].strip().lower(),hash_password(request.form["temporary_password"]),
           request.form["first_name"].strip(),request.form["last_name"].strip(),request.form["job_title"].strip(),int(request.form["role_id"]),int(request.form["department_id"])))
        return redirect(url_for("ui.admin_user_detail_page",user_id=uid))
    return render_template("admin/user_form.html",mode="create",user=None,departments=deps,roles=roles,current_user=admin)

@ui_bp.route("/admin/users/<int:user_id>",methods=["GET","POST"])
@roles_required("Administrator")
def admin_user_detail_page(user_id):
    admin=load_current_user(); deps=db.fetch_all("SELECT id,name FROM departments ORDER BY name"); roles=db.fetch_all("SELECT id,name FROM roles ORDER BY id")
    if request.method=="POST":
        db.execute("UPDATE users SET department_id=%s,role_id=%s,job_title=%s WHERE id=%s",(int(request.form["department_id"]),int(request.form["role_id"]),request.form["job_title"].strip(),user_id))
        return redirect(url_for("ui.admin_user_detail_page",user_id=user_id))
    user=db.fetch_one("""SELECT u.*,d.name department,r.name role FROM users u JOIN departments d ON d.id=u.department_id JOIN roles r ON r.id=u.role_id WHERE u.id=%s""",(user_id,))
    projects=db.fetch_all("""SELECT p.id,p.name,p.status,CASE WHEN p.manager_user_id=%s THEN 'Project lead' ELSE pm.membership_role END project_role
                           FROM project_members pm JOIN projects p ON p.id=pm.project_id WHERE pm.user_id=%s ORDER BY p.name LIMIT 12""",(user_id,user_id))
    recent=db.fetch_all("""SELECT summary,event_type,created_at FROM activity_logs WHERE actor_user_id=%s ORDER BY created_at DESC LIMIT 8""",(user_id,))
    return render_template("admin/user_detail.html",user=user,departments=deps,roles=roles,projects=projects,recent_activity=recent,current_user=admin)

@ui_bp.post("/admin/users/<int:user_id>/toggle")
@roles_required("Administrator")
def admin_user_toggle(user_id):
    admin=load_current_user()
    if user_id!=admin.id:
        row=db.fetch_one("SELECT account_status FROM users WHERE id=%s",(user_id,)); new="ACTIVE" if row["account_status"]=="DISABLED" else "DISABLED"
        db.execute("UPDATE users SET account_status=%s WHERE id=%s",(new,user_id))
    return redirect(url_for("ui.admin_user_detail_page",user_id=user_id))

@ui_bp.post("/admin/users/<int:user_id>/force-reset")
@roles_required("Administrator")
def admin_force_reset(user_id):
    db.execute("UPDATE users SET account_status='PASSWORD_RESET_REQUIRED' WHERE id=%s",(user_id,))
    return redirect(url_for("ui.admin_user_detail_page",user_id=user_id))

@ui_bp.get("/admin/departments")
@roles_required("Administrator")
def admin_departments_page():
    rows=db.fetch_all("""SELECT d.id,d.name,d.code,d.description,COUNT(u.id) employee_count FROM departments d LEFT JOIN users u ON u.department_id=d.id
      GROUP BY d.id,d.name,d.code,d.description ORDER BY d.name""")
    return render_template("admin/departments.html",departments=rows,current_user=load_current_user())

@ui_bp.get("/admin/activity")
@roles_required("Administrator")
def admin_activity_page():
    rows=db.fetch_all("""SELECT a.summary,a.event_type,a.created_at,CONCAT(u.first_name,' ',u.last_name) actor_name
                         FROM activity_logs a LEFT JOIN users u ON u.id=a.actor_user_id ORDER BY a.created_at DESC LIMIT 60""")
    return render_template("admin/activity.html",activity=rows,current_user=load_current_user())

@ui_bp.get("/admin/settings")
@roles_required("Administrator")
def admin_settings_page():
    return render_template("admin/settings.html",settings=db.fetch_one("SELECT * FROM workspace_settings WHERE id=1"),current_user=load_current_user())

@ui_bp.get("/api/system/ui")
def ui_status():
    return {"app":"CYBERVOYRAX Workspace","phase":5,"version":"0.5.1-phase5","functional_modules":True}
