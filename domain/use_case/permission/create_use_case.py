from datetime import datetime
from uuid import uuid4
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity
from domain.entities.permission.permission_entity import PermissionEntity
from domain.exceptions.permission.permission_exception import PermissionAlreadyExists
from applications.dto.permission.permission_request_dto import PermissionRequestDTO
from applications.dto.permission.permission_response_dto import PermissionResponseDTO
from domain.repositories.permission.permission_repository import PermissionRepository


class CreatePermissionUseCase:
    def __init__(self, permission_repository: PermissionRepository, notification_service: Notification):
        self.permission_repository = permission_repository
        self.notification_service = notification_service
    async def execute(self, request_dto: PermissionRequestDTO) -> PermissionResponseDTO:
        # Creazione dell'entità Permission
        if self.permission_repository.find_by_code(request_dto.code):
            raise PermissionAlreadyExists(request_dto.code)

        new_permission = PermissionEntity(
            id=uuid4(),  # Genera un nuovo UUID
            code=request_dto.code,
            description=request_dto.description
        )

        # Salvataggio dell'entità tramite il repository
        saved_permission = self.permission_repository.save(new_permission)



        # Notifica dell'evento di creazione
        eventEntity = EventEntity(
            name="Permission Created",
            payload=saved_permission.to_dict(),
            occurred_at=datetime.now()
            )
        await self.notification_service.notify(eventEntity)

        return PermissionResponseDTO.from_entity(saved_permission)
