from typing import Optional
from applications.dto.role.role_response_dto import RoleResponseDTO


class FindRoleByNameUseCase:
    def __init__(self, role_repository):
        self.role_repository = role_repository

    async def execute(self, name: str, team_id: str) -> Optional[RoleResponseDTO] | None:
        role = await self.role_repository.find_by_name(name, team_id)
        if role:
            return RoleResponseDTO.from_entity(role)
        return None