from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Project:
    id: int
    project_code: str
    name: str
    status: str
    visibility: str
    manager_user_id: int
    department_id: int
    starts_on: date
    due_on: date
