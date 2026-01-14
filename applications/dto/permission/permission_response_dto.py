from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class PermissionResponseDTO(BaseModel):
    id: UUID
    code: str
    description: Optional[str] = None

    @classmethod
    def from_entity(cls,permission):
        print(f"Mapping PermissionEntity to {permission}")
        return cls(
            id=permission.id,
            code=permission.code,
            description=permission.description
        )