from datetime import datetime
from applications.dto.user.user_response_dto import UserResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity


class DeleteUserUseCase:
    def __init__(self, user_repository, notification_service: Notification):
        self.user_repository = user_repository
        self.notification_service = notification_service

    async def execute(self, user_id: str) -> UserResponseDTO:
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        deleted_user = await self.user_repository.delete(user_id)

        # Notifica dell'evento di eliminazione
        event_entity = EventEntity(
            name="User Deleted",
            payload=deleted_user.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return UserResponseDTO.from_entity(deleted_user)