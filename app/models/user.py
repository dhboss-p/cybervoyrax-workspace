from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class User:
    id: int
    employee_code: str
    email: str
    first_name: str
    last_name: str
    job_title: str
    role: str
    department: str
    account_status: str
    manager_user_id: Optional[int] = None

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
