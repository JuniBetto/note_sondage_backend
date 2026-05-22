from datetime import datetime
from pydantic import BaseModel


class UserResponseDTO(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: datetime
    is_active: bool

    @classmethod
    def from_entity(cls, user):
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active
        )
    

class UserFromTeamIdResponseDTO(BaseModel):
    id: str
    full_name: str
    email: str
    created_at: datetime
    is_active: bool
    status: str | None = None
    teamMember_id: str
    image_url: str | None = None
    
    role: str | None = None

    @classmethod
    def from_entity(cls, user):
        return cls(
            id=user.id,
            full_name=user.full_name,
            email=user.email,
            created_at=user.created_at,
            is_active=user.is_active,
            teamMember_id=user.teamMember_id,
            image_url=user.image_url,
            role=user.role,
            status=user.status
        )
    

