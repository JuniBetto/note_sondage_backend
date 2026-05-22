from applications.dto.user.user_response_dto import UserFromTeamIdResponseDTO
from domain.entities.user.user_enty import UserEntityUpdated


class TeamEntity:
    def __init__(self, id: str, name: str, description: str, color: str, created_at: str, created_by_user_id: str, is_deleted: bool = False):
        self.id = id
        self.name = name

        self.description = description
        self.color = color
        self.created_at = created_at
        self.created_by_user_id = created_by_user_id
        self.is_deleted = is_deleted

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "created_at": self.created_at,
            "created_by_user_id": self.created_by_user_id,
            "is_deleted": self.is_deleted
        }
    

class TeamEntityUpdated(TeamEntity):
    def __init__(self, id: str, name: str, description: str, color: str, created_at: str, created_by_user_id: str, is_deleted: bool = False, list_member: list = None):
        super().__init__(id, name, description, color, created_at, created_by_user_id, is_deleted)
        self.list_member = list_member or []

    def to_dict(self):
        data = super().to_dict()
        data["list_member"] = [
            member.to_dict() if hasattr(member, 'to_dict') else member 
            for member in self.list_member
        ]
        return data