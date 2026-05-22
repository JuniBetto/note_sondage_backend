from pydantic import BaseModel

from applications.dto.user.user_response_dto import UserFromTeamIdResponseDTO


class TeamRequestDTO(BaseModel):
    name: str
    description: str
    color: str


class MemberRequestDTO(BaseModel):
    userId: str
    email: str
    status: str
    role: str
    image_url: str | None = None
    teamMember_id: str | None = None

class UpdateTeamRequestDTO(BaseModel):
    name: str | None = None
    description: str | None = None
    color: str | None = None
    list_member: list[MemberRequestDTO] | None = None