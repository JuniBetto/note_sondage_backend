from datetime import datetime
from domain.repositories.services.notification import Notification
from applications.dto.role.role_response_dto import RoleResponseDTO
from domain.entities.event.event_entity import EventEntity
from domain.repositories.role.role_repository import RoleRepository


class DeleteRoleUseCase:
    def __init__(self, role_repository: RoleRepository, notification_service: Notification):
        self.role_repository = role_repository
        self.notification_service = notification_service

    async def execute(self, role_id: str) -> RoleResponseDTO:
        # Fetch the role to be deleted for notification purposes
        role = await self.role_repository._find_by_id(role_id)

        if not role:
            raise ValueError("Role not found")

        # Delete the role
        deleted_role = await self.role_repository.delete(role_id)

        # Notifica dell'evento di cancellazione
        event_entity = EventEntity(
            name="Role Deleted",
            payload=role.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return RoleResponseDTO.from_entity(deleted_role)  