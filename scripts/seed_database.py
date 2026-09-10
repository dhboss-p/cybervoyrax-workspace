#!/usr/bin/env python3
import random
import os
import secrets
from datetime import datetime, timedelta, date
import bcrypt

from app import create_app
from app.extensions import db

SEED = 260908
SEED_VERSION = "phase2-seed-v1"
rng = random.Random(SEED)

DEPARTMENTS = [
    ("Engineering", "ENG", "Builds and maintains internal and customer-facing technology."),
    ("Product", "PRD", "Coordinates product planning, design, research, and delivery."),
    ("Operations", "OPS", "Supports business operations and internal service delivery."),
    ("Finance", "FIN", "Handles financial planning, reporting, and operational finance."),
    ("Human Resources", "HR", "Supports people operations, hiring, and employee services."),
    ("IT", "IT", "Maintains workplace technology and internal systems."),
]

PEOPLE = [
    ("Alex", "Morgan", "Software Engineer", "Engineering"),
    ("Jordan", "Reed", "Software Engineer", "Engineering"),
    ("Nina", "Patel", "QA Engineer", "Engineering"),
    ("Ethan", "Cole", "Platform Engineer", "Engineering"),
    ("Grace", "Mensah", "Frontend Engineer", "Engineering"),
    ("Victor", "Adebayo", "Backend Engineer", "Engineering"),

    ("Sarah", "Chen", "Product Designer", "Product"),
    ("Liam", "Walker", "Product Analyst", "Product"),
    ("Chloe", "Adams", "UX Researcher", "Product"),
    ("Noah", "Bennett", "Product Specialist", "Product"),

    ("Olivia", "Hart", "Operations Analyst", "Operations"),
    ("Daniel", "Carter", "Operations Coordinator", "Operations"),
    ("Sophia", "King", "Vendor Operations Specialist", "Operations"),
    ("Samuel", "Grant", "Service Delivery Analyst", "Operations"),

    ("Michael", "Brooks", "Financial Analyst", "Finance"),
    ("Emma", "Turner", "Accounts Specialist", "Finance"),
    ("Lucas", "Ward", "Finance Operations Analyst", "Finance"),
    ("Aisha", "Bello", "Budget Analyst", "Finance"),

    ("Hannah", "Price", "People Operations Specialist", "Human Resources"),
    ("Mason", "Hill", "Recruiting Coordinator", "Human Resources"),
    ("Zara", "Nwosu", "HR Analyst", "Human Resources"),
    ("Caleb", "Scott", "Learning Coordinator", "Human Resources"),

    ("Rachel", "Kim", "IT Support Engineer", "IT"),
    ("Ben", "Foster", "Systems Support Analyst", "IT"),

    # Managers
    ("Amara", "Okafor", "Engineering Manager", "Engineering"),
    ("David", "Okafor", "Product Manager", "Product"),
    ("Mia", "Roberts", "Operations Manager", "Operations"),
    ("James", "Lewis", "Finance Manager", "Finance"),
    ("Laura", "Evans", "HR Manager", "Human Resources"),
    ("Owen", "Clark", "IT Manager", "IT"),

    # Administrators
    ("Maya", "Williams", "Workspace Administrator", "IT"),
    ("Nathan", "Parker", "Workspace Administrator", "IT"),
]

# Keep total at 32? We need exactly 30. Remove two ordinary users deterministically.
PEOPLE = PEOPLE[:24] + PEOPLE[24:]  # readability; list currently 32
# Remove two ordinary users to reach 30.
for remove_name in [("Caleb", "Scott"), ("Ben", "Foster")]:
    PEOPLE = [p for p in PEOPLE if (p[0], p[1]) != remove_name]

assert len(PEOPLE) == 30

MANAGER_NAMES = {
    ("Amara", "Okafor"),
    ("David", "Okafor"),
    ("Mia", "Roberts"),
    ("James", "Lewis"),
    ("Laura", "Evans"),
    ("Owen", "Clark"),
}
ADMIN_NAMES = {
    ("Maya", "Williams"),
    ("Nathan", "Parker"),
}

PROJECTS = [
    ("CVX-P001", "Cloud Migration", "Modernize internal application hosting and supporting infrastructure.", "ACTIVE", "Engineering"),
    ("CVX-P002", "Client Portal Refresh", "Refresh the internal client-facing portal experience and workflows.", "ACTIVE", "Product"),
    ("CVX-P003", "Finance Automation", "Reduce repetitive reconciliation and reporting work.", "PLANNING", "Finance"),
    ("CVX-P004", "Hiring Operations Review", "Review recruiting workflows and candidate handoff processes.", "ACTIVE", "Human Resources"),
    ("CVX-P005", "Support Workflow Improvement", "Improve request routing and workplace support operations.", "ACTIVE", "IT"),
    ("CVX-P006", "Vendor Renewal Program", "Coordinate key vendor review and renewal milestones.", "PLANNING", "Operations"),
    ("CVX-P007", "Internal Knowledge Base", "Improve searchable internal documentation and ownership.", "ACTIVE", "Operations"),
    ("CVX-P008", "Employee Onboarding Refresh", "Standardize the new-hire onboarding experience.", "ACTIVE", "Human Resources"),
    ("CVX-P009", "Platform Reliability Initiative", "Track reliability improvements for core internal services.", "ACTIVE", "Engineering"),
    ("CVX-P010", "Quarterly Planning Workspace", "Prepare cross-functional materials for quarterly planning.", "PLANNING", "Product"),
]

ASSESSMENT_EMAIL = "assessor@cybervoyrax.test"


def generated_background_password():
    # Seeded background/admin credentials are intentionally undisclosed.
    # They only need a valid bcrypt input because testers do not receive them.
    return secrets.token_urlsafe(32)



def bcrypt_hash(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=10)).decode()


def rows_by_key(rows, key):
    return {row[key]: row for row in rows}


def main():
    app = create_app()

    with app.app_context():
        conn = db.connect()
        conn.autocommit = False
        cur = conn.cursor(dictionary=True)

        try:
            # Re-seed only seed-owned tables. This is safe for Phase 2 development.
            cur.execute("SET FOREIGN_KEY_CHECKS=0")
            for table in [
                "password_reset_tokens",
                "user_sessions",
                "activity_logs",
                "documents",
                "project_comments",
                "project_members",
                "projects",
                "users",
                "departments",
                "roles",
            ]:
                cur.execute(f"TRUNCATE TABLE {table}")
            cur.execute("SET FOREIGN_KEY_CHECKS=1")

            roles = [
                ("User", "Normal day-to-day workspace user."),
                ("Administrator", "Application-wide workspace administrator."),
            ]
            cur.executemany(
                "INSERT INTO roles (name, description) VALUES (%s, %s)",
                roles,
            )

            cur.executemany(
                "INSERT INTO departments (name, code, description) VALUES (%s, %s, %s)",
                DEPARTMENTS,
            )

            cur.execute("SELECT id, name FROM roles")
            role_ids = {r["name"]: r["id"] for r in cur.fetchall()}

            cur.execute("SELECT id, name FROM departments")
            dept_ids = {r["name"]: r["id"] for r in cur.fetchall()}

            # First pass creates users without manager relationships.
            user_id_by_name = {}
            employee_counter = 1001

            for first, last, title, dept in PEOPLE:
                key = (first, last)
                if key in ADMIN_NAMES:
                    role = "Administrator"
                else:
                    role = "User"
                pwd = generated_background_password()

                email = f"{first}.{last}@cybervoyrax.test".lower()
                employee_code = f"CVX-{employee_counter}"
                employee_counter += 1

                office = rng.choice([
                    "Port Harcourt HQ",
                    "Lagos Office",
                    "Remote",
                    "Abuja Office",
                ])

                bio = rng.choice([
                    "Focused on reliable delivery and cross-team collaboration.",
                    "Supports day-to-day execution across the workspace.",
                    "Works with teams to improve internal processes and outcomes.",
                    "Contributes to planning, delivery, and documentation.",
                ])

                cur.execute(
                    """
                    INSERT INTO users (
                        employee_code, email, password_hash, first_name, last_name,
                        job_title, office_location, bio, role_id, department_id,
                        account_status, last_login_at
                    )
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE',%s)
                    """,
                    (
                        employee_code,
                        email,
                        bcrypt_hash(pwd),
                        first,
                        last,
                        title,
                        office,
                        bio,
                        role_ids[role],
                        dept_ids[dept],
                        datetime(2026, 9, 1, 9, 0) + timedelta(hours=rng.randint(0, 120)),
                    ),
                )
                user_id_by_name[key] = cur.lastrowid

            # Dedicated low-privilege assessment account. The plaintext password
            # must be supplied locally and is never embedded in source control.
            assessment_password = os.getenv("ASSESSMENT_PASSWORD") or secrets.token_urlsafe(24)
            cur.execute(
                """
                INSERT INTO users (
                    employee_code, email, password_hash, first_name, last_name,
                    job_title, office_location, bio, role_id, department_id,
                    account_status, last_login_at
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'ACTIVE',NULL)
                """,
                (
                    "CVX-ASSESS", ASSESSMENT_EMAIL, bcrypt_hash(assessment_password),
                    "Security", "Assessor", "Application Security Assessor",
                    "Remote", "Authorized low-privilege assessment account.",
                    role_ids["User"], dept_ids["IT"],
                ),
            )

            dept_manager = {
                "Engineering": user_id_by_name[("Amara", "Okafor")],
                "Product": user_id_by_name[("David", "Okafor")],
                "Operations": user_id_by_name[("Mia", "Roberts")],
                "Finance": user_id_by_name[("James", "Lewis")],
                "Human Resources": user_id_by_name[("Laura", "Evans")],
                "IT": user_id_by_name[("Owen", "Clark")],
            }

            for first, last, title, dept in PEOPLE:
                key = (first, last)
                if key in MANAGER_NAMES or key in ADMIN_NAMES:
                    continue
                cur.execute(
                    "UPDATE users SET manager_user_id=%s WHERE id=%s",
                    (dept_manager[dept], user_id_by_name[key]),
                )

            project_id_by_code = {}
            base_start = date(2026, 8, 3)

            for idx, (code, name, desc, status, dept) in enumerate(PROJECTS):
                manager_id = dept_manager[dept]
                starts_on = base_start + timedelta(days=idx * 3)
                due_on = starts_on + timedelta(days=60 + idx * 5)

                cur.execute(
                    """
                    INSERT INTO projects (
                        project_code, name, description, status, visibility,
                        manager_user_id, department_id, starts_on, due_on
                    )
                    VALUES (%s,%s,%s,%s,'MEMBERS',%s,%s,%s,%s)
                    """,
                    (
                        code, name, desc, status, manager_id,
                        dept_ids[dept], starts_on, due_on
                    ),
                )
                project_id_by_code[code] = cur.lastrowid

            # Build department user pools.
            cur.execute("""
                SELECT u.id, d.name AS department, r.name AS role
                FROM users u
                JOIN departments d ON d.id=u.department_id
                JOIN roles r ON r.id=u.role_id
            """)
            all_users = cur.fetchall()

            by_dept = {}
            for row in all_users:
                by_dept.setdefault(row["department"], []).append(row)

            # Memberships: manager + 3-6 coworkers, with some cross-functional members.
            for code, name, desc, status, dept in PROJECTS:
                pid = project_id_by_code[code]
                manager_id = dept_manager[dept]

                member_ids = {manager_id}
                same_dept = [r["id"] for r in by_dept[dept] if r["id"] != manager_id]
                rng.shuffle(same_dept)
                member_ids.update(same_dept[:min(len(same_dept), rng.randint(3, 5))])

                candidates = [r["id"] for r in all_users if r["id"] not in member_ids and r["role"] != "Administrator"]
                rng.shuffle(candidates)
                member_ids.update(candidates[:rng.randint(1, 2)])

                for uid in sorted(member_ids):
                    cur.execute(
                        """
                        INSERT INTO project_members (project_id, user_id, membership_role)
                        VALUES (%s,%s,%s)
                        """,
                        (pid, uid, "MEMBER" if uid != manager_id else "CONTRIBUTOR"),
                    )

            # Comments
            comment_templates = [
                "I added the latest notes from our review.",
                "The current timeline still looks achievable from my side.",
                "I have a small update to the documentation and will attach it shortly.",
                "Can we confirm ownership of the remaining action items?",
                "The latest review is complete. No blockers from my side.",
                "I updated the project notes after today's discussion.",
                "Please check the latest document before the next meeting.",
                "The dependency we discussed has now been confirmed.",
            ]

            comment_time = datetime(2026, 8, 12, 10, 0)
            for code, *_ in PROJECTS:
                pid = project_id_by_code[code]
                cur.execute("SELECT user_id FROM project_members WHERE project_id=%s", (pid,))
                members = [r["user_id"] for r in cur.fetchall()]
                for n in range(rng.randint(5, 8)):
                    cur.execute(
                        """
                        INSERT INTO project_comments (project_id, author_user_id, body, created_at)
                        VALUES (%s,%s,%s,%s)
                        """,
                        (
                            pid,
                            rng.choice(members),
                            rng.choice(comment_templates),
                            comment_time + timedelta(days=rng.randint(0, 24), hours=rng.randint(0, 8)),
                        ),
                    )

            # Documents metadata only for now; physical upload storage arrives later.
            doc_titles = [
                ("Project Brief", "project-brief.pdf", "application/pdf"),
                ("Meeting Notes", "meeting-notes.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"),
                ("Delivery Checklist", "delivery-checklist.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
                ("Review Summary", "review-summary.pdf", "application/pdf"),
                ("Timeline", "timeline.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
            ]

            doc_counter = 1
            upload_time = datetime(2026, 8, 15, 9, 30)

            for code, *_ in PROJECTS:
                pid = project_id_by_code[code]
                cur.execute("SELECT user_id FROM project_members WHERE project_id=%s", (pid,))
                members = [r["user_id"] for r in cur.fetchall()]

                for _ in range(rng.randint(3, 5)):
                    title, filename, mime = rng.choice(doc_titles)
                    owner = rng.choice(members)
                    document_code = f"DOC-{doc_counter:04d}"
                    stored = f"{document_code.lower()}-{filename}"
                    doc_counter += 1

                    cur.execute(
                        """
                        INSERT INTO documents (
                            document_code, title, stored_filename, original_filename,
                            mime_type, file_size_bytes, description, owner_user_id,
                            project_id, visibility, uploaded_at
                        )
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'PROJECT_MEMBERS',%s)
                        """,
                        (
                            document_code,
                            title,
                            stored,
                            filename,
                            mime,
                            rng.randint(45000, 1800000),
                            "Internal project document for normal workspace collaboration.",
                            owner,
                            pid,
                            upload_time + timedelta(days=rng.randint(0, 20), hours=rng.randint(0, 8)),
                        ),
                    )

            # Activity
            cur.execute("SELECT id FROM users")
            user_ids = [r["id"] for r in cur.fetchall()]
            activities = [
                ("PROFILE_UPDATED", "user", "updated their workspace profile."),
                ("PROJECT_COMMENTED", "project", "commented on a project."),
                ("DOCUMENT_UPLOADED", "document", "uploaded a project document."),
                ("PROJECT_UPDATED", "project", "updated project information."),
                ("PASSWORD_CHANGED", "user", "changed their account password."),
            ]

            for n in range(90):
                actor = rng.choice(user_ids)
                event_type, entity_type, summary = rng.choice(activities)
                cur.execute(
                    """
                    INSERT INTO activity_logs (
                        actor_user_id, event_type, entity_type, entity_id, summary, created_at
                    )
                    VALUES (%s,%s,%s,%s,%s,%s)
                    """,
                    (
                        actor,
                        event_type,
                        entity_type,
                        rng.randint(1, 10) if entity_type == "project" else actor,
                        summary,
                        datetime(2026, 8, 1, 8, 0) + timedelta(
                            days=rng.randint(0, 36),
                            hours=rng.randint(0, 10),
                            minutes=rng.randint(0, 59),
                        ),
                    ),
                )

            cur.execute(
                "UPDATE app_meta SET schema_version='2', seed_version=%s WHERE id=1",
                (SEED_VERSION,),
            )

            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    print("Phase 2 deterministic seed complete.")
    print("Users: 30")
    print("Roles: 28 User, 2 Administrator")
    print("Departments: 6")
    print("Projects: 10")


if __name__ == "__main__":
    main()
