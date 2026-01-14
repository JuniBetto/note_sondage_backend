from typing import Optional
from uuid import UUID


class PermissionEntity:
    def __init__(self, id: UUID, code: str, description: Optional[str] = None):
        self.id = id
        self.code = code
        self.description = description

    def to_dict(self):
        return {
            "id": str(self.id),
            "code": self.code,
            "description": self.description
        }