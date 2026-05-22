from uuid import UUID


class RoleEntity:
    def __init__(self, id: UUID, team_id: UUID, name: str, description: str, permissions: list[str], is_deleted: bool = False):
        self.id = id
        self.team_id = team_id
        self.name = name
        self.description = description
        self.permissions = permissions
        self.is_deleted = is_deleted

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "team_id": str(self.team_id),
            "name": self.name,
            "description": self.description,
            "permissions": self.permissions,
            "is_deleted": self.is_deleted
        }