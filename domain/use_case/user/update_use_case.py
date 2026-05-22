from datetime import datetime
from applications.dto.user.user_request_dto import UserRequestDTO
from applications.dto.user.user_response_dto import UserResponseDTO
from domain.repositories.services.notification import Notification
from domain.entities.event.event_entity import EventEntity


class UpdateUserUseCase:
    def __init__(self, user_repository, notification_service: Notification):
        self.user_repository = user_repository
        self.notification_service = notification_service

    async def execute(self, user_id: str, dto: UserRequestDTO) -> UserResponseDTO:
        user = await self.user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("User not found")

        if dto.full_name is not None:
            user.full_name = dto.full_name
        if dto.email is not None:
            user.email = dto.email
        if dto.is_active is not None:
            user.is_active = dto.is_active

        updated_user = await self.user_repository.update(user)

        # Notifica dell'evento di aggiornamento
        event_entity = EventEntity(
            name="User Updated",
            payload=updated_user.to_dict(),
            occurred_at=datetime.now()
        )
        await self.notification_service.notify(event_entity)

        return UserResponseDTO.from_entity(updated_user)
