from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Document:
    id: int
    document_code: str
    title: str
    owner_user_id: int
    project_id: Optional[int]
    visibility: str
    original_filename: str
    mime_type: str
    file_size_bytes: int
