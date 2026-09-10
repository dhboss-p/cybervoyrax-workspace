from pathlib import Path
from app import create_app
from app.extensions import db

def pdf_bytes(title, body):
    title=title.replace("(","[").replace(")","]")
    body=body.replace("(","[").replace(")","]")
    stream=f"BT\n/F1 18 Tf\n72 720 Td\n({title}) Tj\n/F1 11 Tf\n0 -34 Td\n({body}) Tj\nET"
    objs=[
      "1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
      "2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
      "3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >> endobj",
      f"4 0 obj << /Length {len(stream.encode())} >> stream\n{stream}\nendstream endobj",
      "5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj"
    ]
    out=b"%PDF-1.4\n"; offsets=[]
    for o in objs:
        offsets.append(len(out)); out+=o.encode()+b"\n"
    xref=len(out); out+=f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for off in offsets: out+=f"{off:010d} 00000 n \n".encode()
    out+=f"trailer << /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    return out

app=create_app()
with app.app_context():
    folder=Path(app.config["UPLOAD_FOLDER"]); folder.mkdir(parents=True,exist_ok=True)
    rows=db.fetch_all("""SELECT d.id,d.title,d.stored_filename,d.original_filename,p.name project_name,
                         CONCAT(u.first_name,' ',u.last_name) owner_name
                         FROM documents d JOIN users u ON u.id=d.owner_user_id
                         LEFT JOIN projects p ON p.id=d.project_id ORDER BY d.id""")
    created=updated=0
    for r in rows:
        stored=r["stored_filename"]
        if not stored:
            ext=Path(r["original_filename"]).suffix.lower() or ".txt"
            stored=f"seed-{r['id']:04d}{ext}"
            db.execute("UPDATE documents SET stored_filename=%s WHERE id=%s",(stored,r["id"])); updated+=1
        p=folder/stored
        if not p.exists():
            text=f"CYBERVOYRAX fictional training document. Title: {r['title']}. Project: {r['project_name'] or 'General'}. Owner: {r['owner_name']}."
            p.write_bytes(pdf_bytes(r["title"],text) if Path(r["original_filename"]).suffix.lower()==".pdf" else (r["title"]+"\n\n"+text+"\n").encode())
            created+=1
print(f"Seed document materialization complete: {created} created, {updated} updated.")
