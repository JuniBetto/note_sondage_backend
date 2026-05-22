from datetime import datetime
from pydantic import BaseModel

from applications.dto.user.user_response_dto import UserFromTeamIdResponseDTO


class TeamResponseDTO(BaseModel):
    id: str
    name: str
    description: str
    color: str
    created_at: datetime
    created_by_user_id: str
    is_deleted: bool = False

    @classmethod
    def from_entity(cls, team):
        return cls(
            id=team.id,
            name=team.name,
            description=team.description,
            color=team.color,
            created_at=team.created_at,
            created_by_user_id=team.created_by_user_id,
            is_deleted=team.is_deleted
        )
    
class UpdateTeamResponseDTO(BaseModel):
    id: str
    name: str | None = None
    description: str | None = None
    color: str | None = None
    created_at: datetime
    created_by_user_id: str
    is_deleted: bool = False
    list_member: list[UserFromTeamIdResponseDTO] | None = None

    @classmethod
    def from_entity(cls, team):
        return cls(
            id=team.id,
            name=team.name,
            description=team.description,
            color=team.color,
            created_at=team.created_at,
            created_by_user_id=team.created_by_user_id,
            is_deleted=team.is_deleted,
            list_member=[UserFromTeamIdResponseDTO.from_entity(member) for member in team.list_member] 
        )