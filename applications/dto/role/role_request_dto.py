from uuid import UUID
from pydantic import BaseModel


class RoleRequestDTO(BaseModel):
        team_id: UUID
        name : str
        description : str