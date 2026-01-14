from applications.dto.role.role_response_dto import RoleResponseDTO


class GetAllRolesUseCase:
    def __init__(self, role_repository):
        self.role_repository = role_repository

    def execute(self)->list[RoleResponseDTO]:
        roles = self.role_repository.get_all()
        return [RoleResponseDTO.from_entity(role) for role in roles]