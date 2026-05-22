from applications.dto.role.role_response_dto import RoleResponseDTO


class GetAllRolesByTeamUseCase:
    def __init__(self, role_repository):
        self.role_repository = role_repository

    async def execute(self, team_id) -> list[RoleResponseDTO]:
        roles = await self.role_repository.get_all_by_team(team_id)
        return [RoleResponseDTO.from_entity(role) for role in roles]