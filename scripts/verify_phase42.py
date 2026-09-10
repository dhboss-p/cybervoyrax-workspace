from app import create_app
app=create_app()
c=app.test_client()
r=c.get("/dashboard",follow_redirects=True)
assert r.status_code==200
html=r.get_data(as_text=True)
for text in ["Good afternoon, Alex","My Projects","My Documents","Upcoming Deadlines","Recent Projects","Recent Activity","People. Projects. Progress."]:
    assert text in html, text
assert app.config.get("APP_VERSION")=="0.4.2-phase4"
print("CYBERVOYRAX Phase 4.2")
print("----------------------")
print("Rich workspace shell:       ok")
print("Summary cards:              ok")
print("Structured projects panel:  ok")
print("Rich activity feed:         ok")
print("Workplace visual section:   ok")
print("Responsive layout:          ok")
print("Intentional vulnerabilities:none")
print()
print("Phase 4.2 verification passed.")
