from typing import Optional
from pydantic import BaseModel


class UserRequestDTO(BaseModel):
    full_name: str
    email: str
    is_active: Optional[bool] = True


class UserFromTeamIdRequestDTO(BaseModel):
    team_id: str