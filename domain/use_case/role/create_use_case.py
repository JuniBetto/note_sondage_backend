from uuid import uuid4
from applications.dto.role.role_request_dto import RoleRequestDTO
from applications.dto.role.role_response_dto import RoleResponseDTO
from domain.exceptions.role.role_exception import RoleAlreadyExists
from domain.entities.role.role_entity import RoleEntity


class CreateRoleUseCase:
    def __init__(self, role_repository):
        self.role_repository = role_repository

    def execute(self, dto: RoleRequestDTO) -> RoleResponseDTO:
        if self.role_repository.find_by_name(dto.name):
            raise RoleAlreadyExists(dto.name)
        
        # Create a new role entity
        role = RoleEntity(id=uuid4(), team_id=dto.team_id, name=dto.name, description=dto.description)

        # Save the role using the repository
        created_role = self.role_repository.create(role)

        return RoleResponseDTO.from_entity(created_role)