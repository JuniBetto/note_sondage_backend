from datetime import datetime
from uuid import UUID
from domain.repositories.services.notification import Notification
from domain.entities.event.event_mapper import EventMapper
from domain.entities.event.event_entity import EventEntity
from domain.exceptions.permission.permission_exception import PermissionNotFound


class DeletePermissionUseCase:
    def __init__(self, permission_repository, notification_service:Notification):
        self.permission_repository = permission_repository
        self.notification_service = notification_service

    async def execute(self, permission_id: UUID):
        # Fetch the existing permission
        permission = self.permission_repository.find_by_id(permission_id)
        if not permission:
            raise PermissionNotFound(permission_id)

        # Delete the permission
        self.permission_repository.delete(permission.id)

        

                # Notifica dell'evento di creazione
        eventEntity = EventEntity(
            name="Permission Deleted",
            payload=permission.to_dict() ,
            occurred_at=datetime.now()
            )
        await self.notification_service.notify(eventEntity)
        

        return permission
    