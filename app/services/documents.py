from .errors import NotFoundError


class DocumentService:
    def __init__(self, document_repository):
        self.documents = document_repository

    def get_document(self, document_id):
        document = self.documents.get_by_id(document_id)
        if not document:
            raise NotFoundError("Document not found.")
        return document
