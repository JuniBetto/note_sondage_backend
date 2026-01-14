from uuid import UUID

from pydantic import BaseModel


class RoleResponseDTO(BaseModel):
    id: UUID
    team_id: UUID
    name: str
    description: str

    @classmethod
    def from_entity(cls, role):
        return cls(
            id=role.id,
            team_id=role.team_id,
            name=role.name,
            description=role.description
        )