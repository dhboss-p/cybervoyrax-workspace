from app.models import Document


class DocumentRepository:
    def __init__(self, db):
        self.db = db

    def _to_document(self, row):
        if not row:
            return None

        return Document(
            id=row["id"],
            document_code=row["document_code"],
            title=row["title"],
            owner_user_id=row["owner_user_id"],
            project_id=row["project_id"],
            visibility=row["visibility"],
            original_filename=row["original_filename"],
            mime_type=row["mime_type"],
            file_size_bytes=row["file_size_bytes"],
        )

    def get_by_id(self, document_id):
        row = self.db.fetch_one(
            """
            SELECT id, document_code, title, owner_user_id, project_id,
                   visibility, original_filename, mime_type, file_size_bytes
            FROM documents
            WHERE id = %s
            """,
            (document_id,),
        )
        return self._to_document(row)

    def list_owned_by(self, user_id):
        rows = self.db.fetch_all(
            """
            SELECT id, document_code, title, owner_user_id, project_id,
                   visibility, original_filename, mime_type, file_size_bytes
            FROM documents
            WHERE owner_user_id = %s
            ORDER BY uploaded_at DESC
            """,
            (user_id,),
        )
        return [self._to_document(row) for row in rows]
