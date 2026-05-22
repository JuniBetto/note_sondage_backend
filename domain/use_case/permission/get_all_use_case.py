from applications.dto.permission.permission_request_dto import PermissionRequestDTO
from applications.dto.permission.permission_response_dto import PermissionResponseDTO


class GetAllPermissionsUseCase:
    def __init__(self, permission_repository):
        self.permission_repository = permission_repository

    async def execute(self) -> list[PermissionResponseDTO]:
        permissions = await self.permission_repository.get_all()
        return [PermissionResponseDTO.from_entity(permission) for permission in permissions]