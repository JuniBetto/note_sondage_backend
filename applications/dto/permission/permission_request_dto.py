from typing import Optional
from pydantic import BaseModel


class PermissionRequestDTO(BaseModel):
    code: str
    description: Optional[str] = None