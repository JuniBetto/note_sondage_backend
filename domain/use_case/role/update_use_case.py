from datetime import datetime
from applications.dto.role.role_request_dto import RoleRequestDTO
from applications.dto.role.role_response_dto import RoleResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity


class UpdateRoleUseCase:
    def __init__(self, role_repository, notification_service: Notification):
        self.role_repository = role_repository
        self.notification_service = notification_service

    async def execute(self, old_role_id: str, role_request_dto: RoleRequestDTO) -> RoleResponseDTO:
        role = await self.role_repository._find_by_id(old_role_id)
        if not role:
            raise ValueError("Role not found")

        if role_request_dto.name is not None:
            role.name = role_request_dto.name
        if role_request_dto.description is not None:
            role.description = role_request_dto.description
        if role_request_dto.permissions is not None:
            role.permissions = role_request_dto.permissions


        
        updated_role = await self.role_repository.update(role)

        # Notifica dell'evento di aggiornamento
        eventEntity = EventEntity(
            name="Role Updated",
            payload=updated_role.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(eventEntity)

        return RoleResponseDTO.from_entity(updated_role)