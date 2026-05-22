from typing import Optional
from pydantic import BaseModel
from applications.dto.team_member.team_member_request_dto import TeamMemberStatus

class ProfilePictureResponse(BaseModel):
    user_id: int
    picture_url: str
    uploaded_at: str


class TeamMemberResponseDTO(BaseModel):
    id: str
    team_id: str
    user_id: str
    image_url: Optional[str] = None
    status: TeamMemberStatus
    role_id: str
    file_name: Optional[str] = None
    image_bytes: Optional[bytes] = None
    image_file: Optional[bytes] = None
    initialName: Optional[str] = None

    @classmethod
    def from_entity(cls, team_member):
        member = cls(
            id=team_member.id,
            team_id=team_member.team_id,
            user_id=team_member.user_id,
            image_url=team_member.image_url,
            status=team_member.status,
            role_id=team_member.role_id,
            initialName=team_member.initialName ,
            file_name=team_member.file_name if hasattr(team_member, 'file_name') else None,
            image_bytes=team_member.image_bytes if hasattr(team_member, 'image_bytes') else None,
            image_file=team_member.image_file if hasattr(team_member, 'image_file') else None
        )
        return member